# Experiments and triggers

Once a set of stimuli exists, something has to present it, on the right machine, at the right time,
and in an EEG study it has to tell the amplifier when the stimulus appeared. lexsync writes that
something. This guide covers the declarative trial model that makes one engine serve four paradigms
and three presentation targets, how items are rotated across lists, and where the trigger is written
in each target and why the placement is the interesting part.

## A trial is data

The core idea is small. A trial is a list of events, and an event is a dictionary. Nothing about a
paradigm is expressed as code in a backend, which is what allows a new paradigm to be a
configuration change rather than three new renderers.

```python
import lexsync

for event in lexsync.resolve_events({"paradigm": "lexical_decision"}):
    print(event)
```

```text
{'type': 'fixation', 'content': '+', 'duration_frames': 30}
{'type': 'text', 'content': '{target}', 'duration_frames': 48, 'trigger': 'condition', 'onset_locked': True}
{'type': 'response', 'keys': ['left', 'right'], 'timeout_ms': 2000}
{'type': 'blank', 'duration_frames': 15}
```

An event's `type` is one of `fixation`, `text`, `mask`, `blank`, `region_by_region`, `response` or
`question`. Its `content` is either a literal, such as `"+"` or `"#####"`, or a field reference in
braces, such as `"{target}"`, which is filled per trial from the loop table. `duration_frames`
counts flips at 60 Hz rather than milliseconds, because a frame is the unit the display actually
has. `trigger` is an integer EEG code, or the token `condition` or `item`, and `onset_locked` asks
for it to be written on the event's onset flip.

`resolve_events` returns a design's `events` list if it has one, and otherwise the default sequence
of the paradigm it names, defaulting to `factorial`. Supplying `events` explicitly is how you build
a trial the registry does not have.

## The four paradigms

`PARADIGMS` is a plain dictionary. Each entry gives the fields the paradigm presents, its
counterbalancing recipe and its default event sequence.

| Paradigm | Presents | Counterbalancing | The trial |
| --- | --- | --- | --- |
| `factorial` | `word` | `factorial` | Fixation, the critical word carrying the onset-locked condition marker, response, blank. |
| `lexical_decision` | `target` | `factorial` | The same shape, with a generic target field so a real word and a pseudoword are interchangeable. |
| `priming` | `prime`, `target` | `latin_square_target` | Fixation, a 3-frame prime with its own fixed marker, a 2-frame mask, then the target with the condition marker. |
| `self_paced_reading` | `sentence`, `question` | `latin_square_target` | Fixation, the sentence region by region with the critical region marked, then a yes/no comprehension question. |

`required_fields` tells you what a design's items must carry: the paradigm's own fields, plus any
extra field its events reference.

```python
print(lexsync.required_fields({"paradigm": "priming"}))          # ['prime', 'target']
print(lexsync.required_fields({"paradigm": "self_paced_reading"}))  # ['sentence', 'question']
```

Adding a paradigm means adding an entry to `PARADIGMS` in both engines, with its event sequence, its
fields and its recipe. Both backends then render it with no further code.

## Where the items come from

The corpus paradigms build their own items. Priming and self-paced reading cannot, because a prime,
a target and a sentence with a marked critical region are editorial work, so those designs set
`items.source: table` and point at a CSV.

`load_items` reads it. The table must carry an `item` identifier, a `condition` label and the
paradigm's presented fields, and it is checked on the way in. Field values are validated against
control characters and over-long strings, which is not paranoia about typos: the values are written
into a loop table and an experiment script, and a stray newline in a stimulus would corrupt both.
Commas and quotation marks pass through, because they go into a properly quoted CSV that the
experiment reads at run time rather than into generated code. Items are then mapped to an integer
`set` id in byte order, so that a table-sourced design counterbalances the same way as a
corpus-sourced one, and the same way in both engines.

The self-paced-reading design shows how a sentence carries its own structure: regions are delimited
with `|` in the `sentence` field, and a `critical_region` column names the region that gets the
marker.

## Counterbalancing

`counterbalance` picks a recipe from the design's paradigm and applies it. Trial order within each
list comes from a keyed-hash shuffle seeded by `schema.seed`, and a `trial` column numbers the
result.

The rest of this page follows one small design through to its three exported experiments. It runs
against the bundled lexicon, so the output shown is the output you will get.

```python
from importlib.resources import files

import yaml

import lexsync

data = files("lexsync") / "data"
schema = yaml.safe_load((data / "schema.yaml").read_text(encoding="utf-8"))
lexicon = lexsync.load_lexicon(str(data / "en_example.csv"), schema, language="english")

design = {
    "name": "demo", "language": "english", "n_per_condition": 6,
    "pool_filters": {"length": [3, 8], "frequency": [3.8, 7.0]},
    "conditions": [
        {"name": "high_frequency", "define_by": {"frequency": [5.2, 7.0]}},
        {"name": "low_frequency", "define_by": {"frequency": [3.8, 4.4]}},
    ],
    "match_on": ["length", "n_density", "old20"],
    "counterbalance": {"lists": 1},
    "timing": {"fixation_frames": 30, "word_frames": 30, "isi_frames": 15},
}

pool = lexsync.build_pool(lexicon, design["pool_filters"])
stimuli = lexsync.match_stimuli(pool, design, schema)
```

`factorial` shows every matched item. With more than one list, matched sets are dealt to lists round
robin by set index, so a list gets a balanced slice of the design rather than a contiguous block of
it.

`latin_square_target` is for the paired and sentence paradigms, where showing the same target twice
in one list would ruin it. Each item contributes exactly one trial to each list, in a condition
rotated by the list number, so no target repeats within a list and conditions stay balanced because
items rotate through them. With `counterbalance.lists` unset, the number of lists equals the number
of conditions, which is the fully counterbalanced case.

```python
stimuli = lexsync.counterbalance(stimuli, design, schema)
print(stimuli[["trial", "list", "set", "condition", "word"]].head(3).to_string(index=False))
```

```text
 trial  list  set      condition  word
     1     1    4 high_frequency water
     2     1    1 high_frequency  knew
     3     1    3 high_frequency  fact
```

A design with a `replicate` column, from `resample_stimuli`, is counterbalanced replicate by
replicate, and trial order is numbered within each.

`participant_table` allocates participants to the cells of any crossed factors, cycling through the
grid so the allocation stays balanced whatever the participant count.

```python
print(lexsync.participant_table({"list": [1, 2], "order": ["forward", "reverse"]}, 4)
      .to_string(index=False))
```

```text
 list   order  participant
    1 forward            1
    2 forward            2
    1 reverse            3
    2 reverse            4
```

The grid is crossed with the first factor varying fastest, matching R's `expand.grid`, so both
engines put participant 3 in the same cell.

!!! note "Trial order is part of the parity contract"

    The selection, the pairing, the condition assignment and the trial order are all byte-identical
    across the engines. The shuffle draws no random number, since R's and NumPy's generators could
    never agree on a permutation. Each trial is instead ranked by the SHA-256 digest of its seed,
    replicate, list, set and condition, so the order is a pure function of the design: the same
    bytes from either engine on any platform, a different order for every seed, and no systematic
    position effects.

## Triggers

`assign_triggers` gives each row two EEG codes in the 0–255 range a parallel port can carry. The
condition marker starts at 101 and counts up per condition; the item marker starts at 40 and wraps
after 200 sets. `export_experiments` calls it for you, so you only need it directly if you are
exporting one target at a time.

```python
from lexsync.scripting import assign_triggers

print(assign_triggers(stimuli)[["word", "condition", "condition_trigger", "item_trigger"]]
      .head(3).to_string(index=False))
```

```text
 word      condition  condition_trigger  item_trigger
water high_frequency                101            43
 knew high_frequency                101            40
 fact high_frequency                101            42
```

The codes land in the loop table as `condition_trigger` and `item_trigger`, and the event's
`trigger: condition` token is what binds one to the other:

```text
trial,list,set,condition,word,condition_trigger,item_trigger
1,1,4,high_frequency,water,101,43
2,1,1,high_frequency,knew,101,40
3,1,3,high_frequency,fact,101,42
```

The schema sets the hardware defaults: `triggers.parallel_address` (`0x0378`, a typical LPT1 base
address), `triggers.reset_after_frames` (2, about 33 ms at 60 Hz, comfortably above the 10 ms
minimum recorders need to see), and `triggers.inter_trigger_ms` (10, the spacing of trailing
markers). A design can override them.

## The three targets

`export_experiments` writes all three from the same rendered event list and returns their paths.

```python
paths = lexsync.export_experiments(stimuli, design, schema, outdir="output/experiments")
# {'psychopy': '.../demo_english_psychopy.py',
#  'opensesame': '.../demo_english.osexp',
#  'jspsych': '.../demo_english.html'}
```

Generation imports neither PsychoPy nor pyserial. It writes text. That is what lets the whole
demonstration, and the test suite, reproduce on a machine with no laboratory hardware attached.

### PsychoPy

The PsychoPy export is where the methodological argument for lexsync lives. The script reads its
stimulus text as data from the conditions CSV beside it, and interprets an `EVENTS` list embedded as
JSON, so one interpreter serves every paradigm.

The trigger is written on the exact buffer flip on which the stimulus first appears:

```python
def show_frames(win, stim, frames, port, trigger):
    """Draw ``stim`` for ``frames`` flips; if a trigger is given, lock it to onset."""
    if trigger is not None:
        win.callOnFlip(port.setData, trigger)
    for f in range(frames):
        if stim is not None:
            stim.draw()
        win.flip()
        if trigger is not None and f == RESET_AFTER_FRAMES:
            win.callOnFlip(port.setData, 0)
    if trigger is not None and frames <= RESET_AFTER_FRAMES:
        port.setData(0)
```

`win.callOnFlip` queues the port write against the next flip, so the code goes out with the photons
rather than from a later component that merely runs soon afterwards. The common alternative, sending
the trigger from a separate sequence-ordered item, inherits whatever jitter sits between that item
and the flip. The reset is queued the same way, on the flip `reset_after_frames` later, with a
direct write as the fallback when the stimulus is shorter than the reset window.

Stimulus text is never interpolated into the script, only read from the CSV at run time, so nothing
in a stimulus can become code. When no parallel-port driver is present, on a development laptop, on
macOS, or in continuous integration, a mock port prints the codes and the script still runs. The
test suite exercises exactly that: a mock-PsychoPy harness runs the generated script and asserts
that the onset trigger is flip-locked.

### OpenSesame

The `.osexp` is generated block by block rather than from a template, and the result is a normal
OpenSesame experiment: a trigger-setup inline script, one inline script per event, a sequence and a
loop.

```text
define inline_script lexsync_e1
	set description "Show stimulus and send onset-aligned trigger"
	set _prepare ""
	___run__
	c = Canvas()
	c.text(var.word)
	var.onset_time = c.show()
	send_trigger(var.condition_trigger)
	clock.sleep(500)
```

`Canvas.show()` blocks until the flip and returns its timestamp, so the trigger goes out
immediately after the onset it marks. The setup block opens a parallel or serial device and falls
back to a printing stub when neither is available, so the experiment opens and runs on a machine
with no trigger hardware.

Two details in the generated file are deliberate. The loop is set to `sequential`, because
OpenSesame's default is random, which would discard the seeded trial order the CSV is sorted by and
put this target out of step with the other two. A `response` event is preceded by a blank canvas,
because a `keyboard_response` draws nothing and the preceding stimulus would otherwise stay on
screen for the whole response window instead of offsetting at its stated duration. A structural
validator in the test suite checks the generated file's blocks and references.

### jsPsych

The browser export is a single HTML file carrying the same rendered events and the trial data
inline. It opens with instructions, attaches each item's design fields to every recorded row, and
ends by saving the collected data as a CSV download, so a generated experiment gathers usable data
with no server behind it. The jsPsych library and its stylesheet load from a content delivery
network, so the first run needs an internet connection.

Two things are handled on the way out. Event-model key names are mapped to browser key names, so
`left` becomes `arrowleft` and `space` becomes a literal space. The design's free-text `language`
label is mapped to a BCP 47 tag for the `lang` attribute, falling back to `und` rather than emitting
`lang="english"`, which no user agent can resolve; a design may state `language_tag` outright.

!!! note "The browser target records triggers, it does not send them"

    A browser cannot drive a parallel port. Onset triggers are written into each trial's recorded
    data, which is enough to reconstruct the design offline but not to synchronise an amplifier.
    Online EEG synchronisation needs WebSerial, LSL or a photodiode. The two laboratory targets are
    where the hardware timing lives.

Every worked design in the repository is published as one of these files, which is what the Demo
link in the header opens.
