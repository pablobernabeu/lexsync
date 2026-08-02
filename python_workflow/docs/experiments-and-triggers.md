# Experiments and triggers

Once a set of stimuli exists, something has to present it, on the right machine, at the right time,
and in an EEG study it has to tell the amplifier when the stimulus appeared. lexsync writes that
something. This guide covers the declarative trial model that makes one engine serve five paradigms
and three presentation targets, how items are rotated across lists and blocked into practice and
fillers, and where the trigger is written in each target and why the placement is the interesting
part.

## A trial is data

The core idea is small. A trial is a list of events, and an event is a dictionary. Nothing about a
paradigm is expressed as code in a backend, which is what allows a new paradigm to be a
configuration change rather than three new renderers.

```python exec="1" source="material-block" result="text" session="experiments"
import lexsync

for event in lexsync.resolve_events({"paradigm": "lexical_decision"}):
    print(event)
```

An event's `type` is one of `fixation`, `text`, `mask`, `blank`, `region_by_region`, `response`,
`question` or `feedback`. Its `content` is either a literal, such as `"+"` or `"#####"`, or a field reference in
braces, such as `"{target}"`, which is filled per trial from the loop table. `duration_ms` is the
event's length in milliseconds, the unit all three targets present, so a design means the same
interval wherever it runs; the PsychoPy script measures the display's refresh at start-up and
converts it to the nearest whole number of flips. `duration_frames` is still accepted for designs
written before that change and is converted at `presentation.assumed_refresh_hz`. `trigger` is an
integer EEG code, or the token `condition` or `item`, and `onset_locked` asks for it to be written
on the event's onset flip.

`resolve_events` returns a design's `events` list if it has one, and otherwise the default sequence
of the paradigm it names, defaulting to `factorial`. Supplying `events` explicitly is how you build
a trial the registry does not have.


## Timing that varies from trial to trial

A duration need not be the same on every trial. An event may instead declare a
`duration:` block, in one of two forms:

```yaml
- type: text
  content: '{prime}'
  duration: {from_column: soa_ms}            # read per trial from the items
- type: blank
  duration: {jitter: [400, 800], as: iti_ms} # drawn per trial, in milliseconds
```

The two exist for different reasons. A duration read from a column is a
manipulated variable: the stimulus-onset asynchrony of a priming study is the
lever that separates automatic from strategic processing, so it belongs in the
item table and in the analysis. A jittered duration is not manipulated at all; it
decorrelates the design matrix, as EEG and fMRI designs routinely require.

Neither draws a random number. A jittered value is a uniform integer keyed on the
seed, the column name, the list, the set and the condition, so both engines
realise the same milliseconds and a rerun reproduces them. Naming the column in
the key is what makes two jittered events draw independently rather than sharing
one value.

Either form writes the realised milliseconds into the stimuli table and the loop
table, which is the point: timing that varies is a variable the analysis needs,
not presentation detail. `config/design_en_priming_jitter.yaml` is a worked
example carrying both.

## The five paradigms

`PARADIGMS` is a plain dictionary. Each entry gives the fields the paradigm presents, its
counterbalancing recipe and its default event sequence.

| Paradigm | Presents | Counterbalancing | The trial |
| --- | --- | --- | --- |
| `factorial` | `word` | `factorial` | Fixation, the critical word carrying the onset-locked condition marker, response, blank. |
| `lexical_decision` | `target` | `factorial` | The same shape, with a generic target field so a real word and a pseudoword are interchangeable. |
| `priming` | `prime`, `target` | `latin_square_target` | Fixation, a 3-frame prime with its own fixed marker, a 2-frame mask, then the target with the condition marker. |
| `self_paced_reading` | `sentence`, `question` | `latin_square_target` | Fixation, the sentence region by region with the critical region marked, then a yes/no comprehension question. |
| `categorisation` | `target`, `category`, `answer` | `latin_square_target` | Fixation, the category cue, then the word to judge against it with the condition marker, response, blank. |

`categorisation` is worth a paragraph, because what separates it from lexical decision is not the
shape of the trial but where the question lives. The category cue is a trial event rather than a line
of instructions shown once, since the category varies from trial to trial, and crossing one word with
two cues is how a categorisation study separates a property of the word from the demands of the task.
A robin is a bird quickly and an animal slowly, and only the question changed.

Its `answer` field holds the key that is correct on the trial, not a label, so scoring is a string
comparison against the recorded response with nothing to look up in whatever language the analysis is
written in. The paradigm requires the field, which means an unscoreable categorisation experiment
cannot be generated. Its recipe is `latin_square_target` for the same reason a priming design uses
one: each item carries both cues, and a factorial deal would show a participant the same target
twice, making the second presentation a repetition-priming trial rather than a categorisation trial.
`config/design_en_categorisation.yaml` is a worked example.

`required_fields` tells you what a design's items must carry: the paradigm's own fields, plus any
extra field its events reference.

```python exec="1" source="material-block" result="text" session="experiments"
print(lexsync.required_fields({"paradigm": "priming"}))
print(lexsync.required_fields({"paradigm": "self_paced_reading"}))
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

A third source is `items.source: pool`, which hands the matcher a candidate list of your own instead
of a whole lexicon. It is described under [supplied item pools](matching-and-designs.md#supplied-item-pools),
since what it changes is the selection rather than the trial.

## Practice, fillers and feedback

Everything above treats one frame as both the materials record and the thing that runs. That holds
only while the two are the same trials, and they usually are not. Practice exists to settle the
participant into the task and is discarded before analysis; fillers exist to dilute the manipulation
so the participant cannot guess it, and are likewise not analysed. Both have to reach the generated
experiment, and neither belongs in the stimuli file, the descriptives or the realised control.

So the pipeline splits. The stimuli CSV and the reports are written from the main rows, while the
PsychoPy, OpenSesame and jsPsych experiments are generated from every presented trial. A `block`
column marks which is which, and it appears only when a design declares the blocks, so a design
without them keeps exactly the columns it had.

```yaml
practice:
  path: items/practice_en_lexdec.csv
fillers:
  path: items/fillers_en_lexdec.csv
```

Where each block goes is a methodological choice rather than a convenience. Practice comes first, as
its own run, shuffled within itself so participants do not all meet the practice items in one order.
Fillers are interleaved with the main trials rather than appended, because a block of fillers at the
end is not a filler at all: it is a second block the participant can tell apart. They are merged in
before the order is drawn, so one deterministic shuffle mixes them through, which does renumber the
main trials. That is correct, since adding fillers changes the sequence and the stimuli file records
where each item actually appeared. Both blocks appear in every list and neither is counterbalanced,
because they carry no manipulation to rotate and every participant should get the same practice.

Each block's item table is read with the same validation as any other, and given a `set` range that
cannot collide with the main items, which a naive read would not manage since practice item 1 and
main item 1 would both be set 1. The counts and the tables' checksums go into the datasheet, because
what the participant saw is part of the materials even when it is not part of the analysis.

A `feedback` event scores the trial and shows the result. It reads the field named by `answer`,
compares it as a string with the key the participant pressed, and displays `correct`, `incorrect` or
`no_response` for `duration_ms`.

```yaml
- type: feedback
  answer: answer
  correct: 'Correct'
  incorrect: 'Incorrect'
  no_response: 'Too slow'
  duration_ms: 600
  blocks: [practice]
```

`blocks:` restricts an event to the named blocks, and this is its main use: feedback teaches the
mapping during practice, and would contaminate reaction times in the task itself. The restriction has
to be expressed on the event because the event list is global to the design. Since a feedback event
scores a keypress, something before it must have collected one; a design whose feedback event has no
preceding `response` or `question` is refused when the experiment is generated rather than failing
three different ways at run time. `config/design_en_lexdec_blocks.yaml` puts all of this together.

## Counterbalancing

`counterbalance` picks a recipe from the design's paradigm and applies it. Trial order within each
list comes from a keyed-hash shuffle seeded by `schema.seed`, and a `trial` column numbers the
result.

The rest of this page follows one small design through to its three exported experiments. It runs
against the bundled lexicon, so the output shown is the output you will get.

```python exec="1" source="material-block" session="experiments"
from importlib.resources import files

import yaml

import lexsync

data = files("lexsync") / "data"
schema = yaml.safe_load((data / "schema.yaml").read_text(encoding="utf-8"))
lexicon = lexsync.load_lexicon(
    str(data / "en_example.csv"), schema, language="english"
)

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

```python exec="1" source="material-block" result="text" session="experiments"
stimuli = lexsync.counterbalance(stimuli, design, schema)
print(
    stimuli[["trial", "list", "set", "condition", "word"]]
    .head(3)
    .to_string(index=False)
)
```

A design with a `replicate` column, from `resample_stimuli`, is counterbalanced replicate by
replicate, and trial order is numbered within each.

### Balanced list assignment

The factorial deal sends set 1 to list 1, set 2 to list 2 and so on. That is reproducible, but it
balances nothing: every *n*th set lands in the same list, so a dimension that happens to vary
smoothly across sets is dealt out unevenly, and where each list goes to a different group of
participants, the unevenness is confounded with the group.

`counterbalance.optimise` searches instead for an assignment whose lists have near-equal totals on
the dimensions you name, by exchanging pairs of item sets between lists. List sizes are preserved,
since a swap trades one set for another.

```yaml
counterbalance:
  lists: 4
  optimise: true
  balance_on: [length, n_density, old20, frequency]
```

`balance_on` defaults to `match_on`, and the example widens it deliberately. Frequency is the
manipulated variable and so is not matched on, but it is manipulated *within* a list, since every
list holds both conditions. Equating the lists on its total therefore costs the manipulation nothing
and removes a difference between the participant groups who receive different lists. Naming only the
matched dimensions leaves frequency dealt arbitrarily, and measurably so: on the shipped design the
optimiser then improves the three named dimensions and makes frequency worse than the arbitrary deal
had it. Balance what you want equated across lists, which is usually everything.

This is a steepest descent to a local optimum, not a global search. What it guarantees is that no
single exchange would improve matters further, and the datasheet records the imbalance before and
after, so the improvement is checkable rather than asserted. The objective is all-integer and ties
are broken by the seeded keyed hash rather than by position, which is what keeps the two engines on
the same assignment and stops list 1 being favoured for being numbered first.

It is off by default, and stays off. Switching it on changes which items a participant sees, so it
has to be a design decision rather than something a package upgrade does to a study already running.
It is refused on a Latin-square design, where every item already appears in every list and the lists
are balanced on the items by construction. `balance_lists` runs the search alone if you want the
assignment without applying it; `config/design_en_balanced_lists.yaml` is the worked example.

`participant_table` allocates participants to the cells of any crossed factors, cycling through the
grid so the allocation stays balanced whatever the participant count.

```python exec="1" source="material-block" result="text" session="experiments"
print(
    lexsync.participant_table(
        {"list": [1, 2], "order": ["forward", "reverse"]}, 4
    )
    .to_string(index=False)
)
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

```python exec="1" source="material-block" result="text" session="experiments"
from lexsync.scripting import assign_triggers

print(
    assign_triggers(stimuli)[
        ["word", "condition", "condition_trigger", "item_trigger"]
    ]
    .head(3)
    .to_string(index=False)
)
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
address), `triggers.trigger_hold_ms` (50, comfortably above the 10 ms minimum recorders need to
see, and converted to whole flips against the measured refresh so it does not shorten on a fast
display), and `triggers.inter_trigger_ms` (10, the spacing of trailing markers). A design can
override them. The older `triggers.reset_after_frames` is still accepted and converted.

## The three targets

`export_experiments` writes all three from the same rendered event list and returns their paths.

```python
# illustrative: writes three experiment files into the working directory
paths = lexsync.export_experiments(
    stimuli, design, schema, outdir="output/experiments"
)
# {'psychopy': '.../demo_english_psychopy.py',
#  'opensesame': '.../demo_english.osexp',
#  'jspsych': '.../demo_english.html'}
```

Generation imports neither PsychoPy nor pyserial. It writes text. That is what lets the whole
demonstration, and the test suite, reproduce on a machine with no laboratory hardware attached.

### PsychoPy

The PsychoPy export ([Peirce et al., 2019](references.md#peirce-2019)) is where the methodological
argument for lexsync lives. The script reads its stimulus text as data from the conditions CSV
beside it, and interprets an `EVENTS` list embedded as JSON, so one interpreter serves every
paradigm.

The trigger is written on the exact buffer flip on which the stimulus first appears:

```python
# illustrative: an excerpt of the generated script, needing a PsychoPy window and port
def show_frames(win, stim, frames, port, trigger):
    """Draw ``stim`` for ``frames`` flips; if a trigger is given, lock it to onset."""
    if trigger is not None:
        win.callOnFlip(port.setData, trigger)
    # callOnFlip runs its callback on the NEXT flip, so queueing the reset on this
    # index clears the code one flip later and holds it for exactly
    # TRIGGER_HOLD_FRAMES flip intervals.
    reset_at = TRIGGER_HOLD_FRAMES - 1
    for f in range(frames):
        if stim is not None:
            stim.draw()
        win.flip()
        if trigger is not None and f == reset_at:
            win.callOnFlip(port.setData, 0)
    if trigger is not None and frames <= reset_at:
        port.setData(0)
```

`win.callOnFlip` queues the port write against the next flip, so the code goes out with the photons
rather than from a later component that merely runs soon afterwards. The common alternative, sending
the trigger from a separate sequence-ordered item, inherits whatever jitter sits between that item
and the flip. The reset is queued the same way, one flip before the hold expires so that it lands
on the flip that ends it, with a direct write as the fallback when the stimulus is shorter than the
hold. `TRIGGER_HOLD_FRAMES` is computed at start-up from `TRIGGER_HOLD_MS` and the measured refresh
rate, floored at one flip and at the recorder minimum, which is what keeps a declared hold meaning
the same interval on a 60 Hz and a 144 Hz display.

Stimulus text is never interpolated into the script, only read from the CSV at run time, so nothing
in a stimulus can become code. When no parallel-port driver is present, on a development laptop, on
macOS, or in continuous integration, a mock port prints the codes and the script still runs. The
test suite exercises exactly that: a mock-PsychoPy harness runs the generated script and asserts
that the onset trigger is flip-locked.

### OpenSesame

The `.osexp` is generated block by block rather than from a template, and the result is a normal
OpenSesame experiment ([Mathôt et al., 2012](references.md#mathot-2012)): a trigger-setup inline
script, one inline script per event, a sequence and a loop.

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
