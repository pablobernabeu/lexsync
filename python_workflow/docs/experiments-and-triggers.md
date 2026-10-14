# Experiments and triggers

Once a set of stimuli exists, something has to present it, on the right machine, at the right time,
and in an EEG study it has to tell the amplifier when the stimulus appeared. lexsync writes that
something. This guide covers the declarative trial model that makes one engine serve six paradigms
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
event's length in milliseconds, the unit all three targets present, so a design asks for the same
interval wherever it runs, although each target delivers it differently (below). The PsychoPy script measures the display's refresh at start-up and
converts it to the nearest whole number of flips. `duration_frames` is still accepted for designs
written before that change and is converted at `presentation.assumed_refresh_hz`. `trigger` is a
whole-number EEG code from 1 to 255, or the token `condition` or `item`, and `onset_locked` asks for
it to be written on the event's onset flip.

A text event's `case`, `upper` or `lower`, sets the letter case its text is shown in. The runners
apply it as they show the text, with `str.upper()` and `str.lower()` in PsychoPy and OpenSesame and
`toUpperCase()` and `toLowerCase()` in jsPsych, so the loop tables and the data files keep each item
as it was written. lexsync never changes the case itself, because R's `toupper()` leaves "ß" as it
is where Python and JavaScript give "SS", and the two engines must write the same files. A mask's
`length_of` names fields of the trials, and its one-character content is repeated as many times as
the longest of their values has characters, counted when the experiments are written:

```yaml
- type: mask
  content: '#'
  length_of: [prime, target]
  duration_ms: 500
```

The count is in characters, not bytes, over every trial of every list, so each target and each list
shows the same mask.

Each target realises those durations in its own way. PsychoPy rounds them to whole flips at the
measured refresh and locks the trigger to the flip. The generated OpenSesame experiment builds every
canvas of a trial before the trial starts and times each event from the onset its display returns.
It ends the event half a frame before its duration is up, so that the next display lands on the
refresh that ends it. On a simulated display at 60, 120 and 144 Hz, the prime and the mask of the
`priming` paradigm then last the flips the PsychoPy script gives them. Its 83 ms stimulus-onset
asynchrony stays 83.3 ms at all three rates. A duration within a millisecond or so of halfway
between two whole numbers of flips can still come out a flip longer or shorter than in PsychoPy.
The experiment used to build each canvas while the trial ran and to sleep each event's full
duration after a blocking 10 ms pulse, so every event overran its stated length. In the browser,
timing varies with the machine and the browser, and primes of 33 to 50 ms are not reliably
realised online. Whatever the target, verify the timing a study depends on with a photodiode, as
[checking the timing](#checking-the-timing) describes.

`resolve_events` returns a design's `events` list if it has one, and otherwise the default sequence
of the paradigm it names, defaulting to `factorial`. Supplying `events` explicitly is how you build
a trial the registry does not have.

## When a response is collected

A response event after a text event collects its key from that stimulus's onset. The stimulus stays
on screen for its duration at most and a blank follows it. The window closes once the stimulus's
duration and the response's `timeout_ms` have both passed, so the default lexical decision collects
for 2,800 ms from the target's onset. A key pressed while the target is still visible counts, the
first key ends the trial, and every target times the reaction from the target's onset.

A design that asks the participant to wait, as a delayed-response EEG design does, keeps a window
that opens once the stimulus has gone:

```yaml
- type: response
  keys: [f, j]
  timeout_ms: 2000
  from: offset
```

A stimulus that should stay on screen for the whole window, as the `masked_priming` target does,
takes the window's length as its duration, and its response a `timeout_ms` of 0.

A response after any other event gets the same window by default, so one that follows a blank keeps
the window it had, timed from the window's own onset. `from: onset` after such an event is refused,
since a window from the onset opens with a text event and none comes right before it. The datasheet
records each response window as `presentation.response_windows`, and its Methods text says when
responses were collected.

## Instructions and the response mapping

Every generated experiment shows instructions and waits for the space bar before its first trial.
The participant reads them at their own pace, and the experimenter can start the run when the
participant is ready. A design gives its own text under `instructions`, which may hold line
breaks:

```yaml
instructions: |
  You will see a string of letters.
  Press F if it is a real English word and J if it is not.
```

The text is carried as data: JSON in the PsychoPy script and the jsPsych page, and an escaped
literal in the OpenSesame script, so nothing in it can become code. A control character other than
the line break is refused. Without the key, lexsync writes English instructions for the tasks it
knows. A lexical decision names the keys for a word and a pseudoword. A categorisation says that
its first key means yes and its second no, and a comprehension question says the same of its keys.
Any other design is told only which keys to press, and its run log asks for instructions that say
what each key means. The run log also notes a design in another language that gives no text of its
own. The targets' own short messages, such as the prompt to press the space bar, are in English.

A lexical decision maps word to its response event's first key and pseudoword to its second. The
paradigm's events therefore map word to the left arrow key, and
`config/design_en_lexdec_blocks.yaml`, whose events use f and j, maps word to f, as its practice
table does. A design may give its own mapping, with keys its response event allows, and may rotate
it across lists:

```yaml
response_mapping: {word: j, pseudoword: f}
rotate_mapping_by_list: true
```

Rotated, list *k* moves each key *k* - 1 places along the response event's keys, which with two keys
swaps them in every even-numbered list, and each version's instructions name its own keys. lexsync
refuses a mapping that names a key the response event does not allow. It also refuses one that
gives no key for a condition whose trials name no answer, and one that names a condition no trial
has.

`export_experiments` gives each trial its correct key in `answer` as it assigns the trigger codes,
so every trial of a lexical decision can be scored. A practice or filler table keeps its own
answers, and the run log notes any that the mapping contradicts, as a rotated mapping does in its
even-numbered lists. The stimuli file does not change. jsPsych records a key by the browser's name
for it, so the jsPsych page names each answer that way, `arrowleft` for `left`, and in every target
a correct response equals its trial's answer. The datasheet records the mapping as
`presentation.response_mapping`, and its Methods text says which key the participants pressed for
which condition.


## Timing that varies from trial to trial

A duration need not be the same on every trial. An event may instead declare a
`duration:` block, in one of two forms:

```yaml
- type: text
  content: '{prime}'
  duration: {from_column: prime_ms}          # read per trial from the items
- type: blank
  duration: {jitter: [400, 800], as: iti_ms} # drawn per trial, in milliseconds
```

The two exist for different reasons. A duration read from a column is a
manipulated variable. Here it is the prime's duration, which with the mask that
follows sets the stimulus-onset asynchrony, the lever that separates automatic
from strategic processing. It belongs in the item table and in the analysis. A
jittered duration is not manipulated at all. It decorrelates the design matrix,
as EEG and fMRI designs routinely require.

Neither draws a random number. A jittered value is a uniform integer keyed on the
seed, the column name, the list, the set and the condition, so both engines
realise the same milliseconds and a rerun reproduces them. Naming the column in
the key is what makes two jittered events draw independently, since without it
they would share a single value.

Either form writes the realised milliseconds into the stimuli table and the loop
table, because timing that varies is a variable the analysis needs, not
presentation detail. `config/design_en_priming_jitter.yaml` is a worked
example carrying both. Its prime lasts `prime_ms` and a 33 ms mask follows, so its
stimulus-onset asynchrony is `prime_ms` plus 33 ms.

Every value read from a column must be a finite number of milliseconds, not negative. A blank or
negative cell is refused, naming the column and the trial's set and condition. Left alone, it would
give an experiment that stops at the blank or shows the stimulus for no time at all. Fractional
milliseconds, such as the 33.333333 that an item table built on 60 Hz frames carries, are rounded
once with the rounder both engines share and written back. The stimuli, the loop tables and all
three targets then present the same whole milliseconds, and the run log counts the values rounded.
A fixed `duration_ms` or `duration_frames` is checked the same way, and the lower bound of a jitter
must not be negative.

## The six paradigms

`PARADIGMS` is a plain dictionary. Each entry gives the fields the paradigm presents, its
counterbalancing recipe and its default event sequence.

| Paradigm | Presents | Counterbalancing | The trial |
| --- | --- | --- | --- |
| `factorial` | `word` | `factorial` | Fixation, the critical word carrying the onset-locked condition marker, response, blank. |
| `lexical_decision` | `target` | `factorial` | The same shape, with a generic target field so a real word and a pseudoword are interchangeable. |
| `priming` | `prime`, `target` | `latin_square_target` | Backward pattern-masked: fixation, a 50 ms prime with its own fixed marker, a 33 ms `#####` mask, then the target with the condition marker (an 83 ms stimulus-onset asynchrony at 60 Hz). There is no forward mask, and prime and target keep the item table's letter case. |
| `masked_priming` | `prime`, `target` | `latin_square_target` | A forward mask of hash marks for 500 ms, as many as the longest prime or target has characters, a lower-case prime for three frames (50 ms at 60 Hz) with its own fixed marker, then the upper-case target with the condition marker, on screen until the response or for 2,000 ms, and a 250 ms blank. |
| `self_paced_reading` | `sentence`, `question` | `latin_square_target` | Fixation, the sentence region by region with the critical region marked, then a yes/no comprehension question. |
| `categorisation` | `target`, `category`, `answer` | `latin_square_target` | Fixation, the category cue, then the word to judge against it with the condition marker, response, blank. |

`masked_priming` is the procedure of [Forster and Davis (1984)](references.md#forster-1984).
Without the forward mask, a prime of 50 ms is usually visible. The change of case keeps a related
prime and its target from sharing their visual form, so that priming does not arise from the
overlap of the two displays. `config/design_en_rastle_repro.yaml` uses it for the
[Rastle, Davis and New (2004)](references.md#rastle-2004) reproduction, a lexical decision whose
nonword targets are fillers with the right arrow key as their answer, while its response mapping
puts both priming conditions on the left. `config/design_en_andrews_repro.yaml` runs the
[Andrews (1989)](references.md#andrews-1989) reproduction as a lexical decision the same way, with
one pseudoword per selected word. Both designs' comments say how the fillers were made and what
still differs from the original studies.

`categorisation` is worth a paragraph, because what separates it from lexical decision is not the
shape of the trial but where the question lives. The category cue is a trial event, shown afresh each
time, since the category varies from trial to trial, and crossing one word with two cues is how a
categorisation study separates a property of the word from the demands of the task. A robin is a bird
quickly and an animal slowly, and only the question changed.

Its `answer` field holds the key that is correct on the trial, so scoring is a string comparison
against the recorded response with nothing to look up in whatever language the analysis is
written in. Because the paradigm requires the field, the PsychoPy and OpenSesame targets can score
each response against it, and the jsPsych data rows carry it beside the response. Its recipe is
`latin_square_target` for the same reason a priming design uses one: each item carries both cues,
and a factorial deal would show a participant the same target twice, turning the second
presentation into a repetition-priming trial. A categorisation also needs 'no' trials, or pressing
the yes key on every trial scores perfectly. `config/design_en_categorisation.yaml` is a worked
example, whose 16 foils, nouns that do not belong to the category they appear under, are fillers
with the answer j.

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
participant into the task and is discarded before analysis. Fillers exist to dilute the manipulation
so the participant cannot guess it, and are likewise not analysed. Both have to reach the generated
experiment, and neither belongs in the stimuli file, the descriptives or the realised control.

The pipeline therefore splits. The stimuli CSV and the reports are written from the main rows, while
the PsychoPy, OpenSesame and jsPsych experiments are generated from every presented trial. A `block`
column marks which is which, and it appears only when a design declares the blocks, so a design
without them keeps exactly the columns it had.

```yaml
practice:
  path: items/practice_en_lexdec.csv
fillers:
  path: items/fillers_en_lexdec.csv
```

Where each block goes is a methodological choice. Practice comes first, as its own run, shuffled
within itself so participants do not all meet the practice items in one order. Fillers are
interleaved with the main trials, because a block of fillers at the end is not a filler at all: it
is a second block the participant can tell apart. They are merged in
before the order is drawn, so one deterministic shuffle mixes them through, which does renumber the
main trials. That is correct, since adding fillers changes the sequence and the stimuli file records
where each item actually appeared. Both blocks appear in every list and neither is counterbalanced,
because they carry no manipulation to rotate and every participant should get the same practice. In
a resampled design, the copy of a list in each replicate is a presentation version of its own, and
it gets both blocks too. The PsychoPy and jsPsych runners pause where the practice trials end and
nowhere else, since a pause around a filler would set it apart.

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

`blocks:` restricts an event to the named blocks, and this is its main use: feedback during practice
confirms the mapping the instructions state, and would contaminate reaction times in the task
itself. The restriction has to be expressed on the event because the event list is global to the
design. Since a feedback event scores a keypress, something before it must have collected one. A
design whose feedback event has no preceding `response` or `question` is refused when the
experiment is generated. Left to run time, that one design error would surface as three different
failures, one per target.
`config/design_en_lexdec_blocks.yaml` puts all of this together.

## Counterbalancing

`counterbalance` picks a recipe from the design's paradigm and applies it. A design's own `events`
list has no say in the recipe, so a priming design that reads its prime's duration from the items
keeps its Latin square. `counterbalance.recipe` names a recipe outright, `factorial` or
`latin_square_target`, for a design that needs the other one. Trial order within each list comes
from a keyed-hash shuffle seeded by `schema.seed`, and a `trial` column numbers the result.

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
it. More lists than item sets are refused, since the surplus lists would be empty.

`latin_square_target` is for the paired and sentence paradigms, where showing the same target twice
in one list would ruin it. Each item contributes exactly one trial to each list, in a condition
rotated by the list number, so no target repeats within a list. With `counterbalance.lists` unset,
the number of lists equals the number of conditions, which is the fully counterbalanced case.

The rotation is complete only when the lists and the item sets are multiples of the number of
conditions. One list confounds item and condition, since every participant sees each item in the
same condition. Two lists for three conditions show each item in only two of them, and nine items in
two conditions leave each list with five trials in one condition and four in the other. The run log
and the datasheet report such a rotation, and the Methods text calls it incomplete.
`counterbalance.incomplete: error` refuses it instead, set in the design or, for every design, in the
schema. The datasheet's `counterbalancing` record gives the recipe that ran, the lists the stimuli
table holds, whether the rotation is complete and the trials each list gives each condition.

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
after, so the improvement is checkable. The objective is all-integer and ties are broken by the
seeded keyed hash, which keeps the two engines on the same assignment and stops list 1 being
favoured for being numbered first.

It is off by default, and stays off. Switching it on changes which items a participant sees, so it
has to be a deliberate design decision. A package upgrade must never make that change for a study
already running. It is refused on a Latin-square design, where every item already appears in every
list and the lists are balanced on the items by construction. `balance_lists` runs the search alone
if you want the assignment without applying it. `config/design_en_balanced_lists.yaml` is the worked
example.

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
condition marker starts at 101 and counts up per condition. The item marker starts at 40 and counts
up in code-point order of the set labels. `export_experiments` calls it for you, so you only need it
directly if you are exporting one target at a time.

The condition codes follow the order given in the `conditions` argument, or the order of first
appearance when there is none. The order of first appearance in a shuffled trial list depends on the
seed, so an analysis that decodes the codes should not rely on it. `export_experiments` therefore
passes the order of the design's `conditions` entries, and the pipeline does the same, adding any
other condition in the order the item source lists it, such as the words before the pseudowords of a
generated lexical decision. The first condition the design lists is always 101, whatever the seed.
A condition missing from the given order takes the next free code, in code-point order of its label.

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

Code-point order is not numeric order once a design has ten sets or more. With sets 1 to 20, set 10
is 41 and set 2 is 51. Decode an item code through the loop table, which pairs each trial's set with
its code, and never from the label.

```python exec="1" source="material-block" result="text" session="experiments"
import pandas as pd

twenty = assign_triggers(pd.DataFrame({"condition": "a", "set": range(1, 21)}))
print(dict(zip(twenty["set"].tolist(), twenty["item_trigger"].tolist(), strict=True)))
```

Item codes stay below 240, since a code is one byte and 254 and 255 mark the session. A design may
send item codes together with condition codes, or with a code of its own from 40 to 239. Its item
codes are then drawn from the codes those leave free, skipping 101 upwards and the design's own
codes. Otherwise, sets 65 and 66 of a 70-set design would take 101 and 102, and an analysis that
cuts its epochs at the condition codes would also catch two items. Such a design is refused when it has more item
sets than free codes, unless the schema sets `triggers.allow_code_overlap: true`, which lets the
item codes wrap and repeat within the free codes. Any other design keeps the codes it always had,
wrapping at 200 values.

A literal code must be a whole number from 1 to 255. Anything else, a misspelt token such as
`conditon` included, is refused when the experiment is generated, with a message naming the event.
A literal of 254 or 255, which the PsychoPy and OpenSesame experiments send when the session starts
and ends, is reported then. One equal to a condition code the design sends is reported too, as is
one within the range of the item codes it sends.

The schema sets the hardware defaults: `triggers.parallel_address` (`0x0378`, a typical LPT1 base
address) and `triggers.trigger_hold_ms` (50, comfortably above the 10 ms minimum recorders need to
see). They describe the machine that runs the experiments, so a design does not set them, and
neither do the device settings below. The older `triggers.reset_after_frames` is still accepted and
converted. `triggers.inter_trigger_ms` held the self-paced reading critical-region code for 10 ms.
That code is now held like every other, so the key is no longer used, and the run log says so when
a schema sets it. `triggers.allow_code_overlap` is false, so a design whose item codes cannot all
be kept apart from its other codes is refused.

Every code is held for `trigger_hold_ms` from the onset it marks. The PsychoPy script converts the
hold to the nearest whole number of flips at the refresh it measures, and never to fewer than the
flips that cover 10 ms. It therefore does not shorten on a fast display. The OpenSesame experiment
holds it in milliseconds, at least 10, and a code is reset by the first wait that reaches the end
of its hold. A hold that ends while the experiment waits for the next refresh lasts until that
display, up to a frame longer. One that ends after the last wait of a trial lasts until the next
trial's first display. A code whose event is shorter than the hold stays on the port through
the events after it and is reset when the hold is up. A one-flip prime therefore gets the same
pulse as an 800 ms target, and a key that ends a stimulus early does not cut its code short. Only
the next onset's code ends a code before its hold is up, with a 0 written just before the new
code. Both laboratory targets send 254 just before the first trial and 255 just after the last,
held the same way.

### The trigger device

`triggers.backend` names the device both laboratory targets write the codes to. `parallel`, the
default, is the port at `triggers.parallel_address`. `serial` writes each code as one byte to the
device `triggers.serial_port` names, at `triggers.baudrate` bits per second, 115200 unless set:

```yaml
triggers:
  backend: serial
  serial_port: COM3      # /dev/ttyUSB0 on Linux, /dev/cu.usbserial-... on macOS
  baudrate: 115200       # the rate the device's manual gives
```

The port has to be named, and a serial backend without one is refused. The OpenSesame setup used
to open the first serial port it found, which could be another device, and it reached that code
only once the script had been edited by hand. A code is held and reset on a serial device as on a
parallel port, with a 0 written when its hold is up. A serial line delays each code by an amount
that varies from code to code, and a parallel port does not. A USB-serial adapter carries each
byte in a USB transfer, scheduled in frames of a millisecond on a full-speed connection, and its
driver adds a delay of its own. Adapters built on FTDI chips also hold data on its way to the
computer until their latency timer runs out, 16 ms by default. That matters for a device that
answers and for a response box on the same adapter. Measure the delay with a photodiode, as
[checking the timing](#checking-the-timing) describes, before a study relies on serial codes for
its timing.

`triggers.mode` decides what happens when the device cannot be opened, as on a laptop with no
parallel port. Under `auto`, the default, both targets print each code in the console, and a
screen before any other tells the experimenter that no codes will be sent. Pressing C goes on
without them, and escape stops the run. Every trial records the mode the run used, `hardware` or
`mock`, as `trigger_mode` in the PsychoPy data file and as `lexsync_trigger_mode` in the OpenSesame
log. Both targets used to print the codes and run on with no notice on screen, and only the
OpenSesame log recorded that no code had reached the amplifier, in its `test_mode` column.
`hardware` refuses to start without the device. The PsychoPy script stops before its window
opens, and the OpenSesame experiment stops in its setup. `mock` prints the codes without trying
the device, after the same notice.

## The three targets

`export_experiments` writes all three from the same rendered event list and returns their paths,
with every file it wrote, the tables the experiments read included, listed under `files`.

```python
# illustrative: writes the experiment files into the working directory
paths = lexsync.export_experiments(
    stimuli, design, schema, outdir="output/experiments"
)
# {'psychopy': '.../demo_english_psychopy.py',
#  'opensesame': '.../demo_english.osexp',
#  'jspsych': '.../demo_english.html',
#  'files': ['.../demo_english_psychopy.py', '.../demo_english.osexp',
#            '.../demo_english.html', '.../demo_english_psychopy.csv',
#            '.../demo_english_opensesame.csv', '.../demo_english_opensesame_text.csv']}
```

Generation imports neither PsychoPy nor pyserial. It writes text. That is what lets the whole
demonstration, and the test suite, reproduce on a machine with no laboratory hardware attached.

Two schema settings shape the display. `presentation.text_height_px`, a whole number from 8 to 400
and 48 by default, is the height of the stimulus text in pixels in all three targets. The
OpenSesame experiment drew its text 32 pixels high, where the other two used 48. In OpenSesame,
the setting is the experiment's `font_size`, which every screen uses, the instructions included.
`presentation.fullscreen`, true by default, runs the PsychoPy script full screen, as PsychoPy's
advice on reducing dropped frames recommends. With false, the script opens a 1280 × 1024 window,
the window it always opened before. OpenSesame takes full screen from the mode it is launched in.

### PsychoPy

The PsychoPy export ([Peirce et al., 2019](references.md#peirce-2019)) is where the methodological
argument for lexsync lives. The script reads its stimulus text as data from the conditions CSV
beside it, and interprets an `EVENTS` list embedded as JSON, so one interpreter serves every
paradigm.

The trigger is written on the exact buffer flip on which the stimulus first appears, and reset on
the flip that ends its hold:

```python
# illustrative: an excerpt of the generated script, needing a PsychoPy window and port
def send_code(win, port, code):
    """Write ``code`` to the port on the next flip, the onset it marks, and hold it
    there for TRIGGER_HOLD_FRAMES flip intervals."""
    if PULSE["flips"] > 1:
        win.callOnFlip(PULSE["port"].setData, 0)
    win.callOnFlip(port.setData, code)
    PULSE.update(port=port, flips=TRIGGER_HOLD_FRAMES + 1)


def count_flip(win):
    """Count a flip against the code on the port, and queue its reset on the flip that
    ends the hold, so that the reset is as flip-locked as the onset."""
    if PULSE["flips"]:
        PULSE["flips"] -= 1
        if PULSE["flips"] == 1:
            win.callOnFlip(PULSE["port"].setData, 0)
```

`win.callOnFlip` queues the port write against the next flip, so the code goes out with the photons
rather than from a later component that merely runs soon afterwards. The common alternative, sending
the trigger from a separate sequence-ordered item, inherits whatever jitter sits between that item
and the flip. Every flip of every event counts the hold down, and the reset is queued the same way,
one flip before the hold expires, so that it lands on the flip that ends it. When the stimulus is
shorter than the hold, that flip comes in a later event. The pause between blocks waits without
flipping, so it first holds out the rest of the hold with `core.wait`, and so do the session
markers. `TRIGGER_HOLD_FRAMES` is computed at start-up from `TRIGGER_HOLD_MS` and the measured
refresh rate. It is the hold rounded to whole flips, and never fewer than the flips that cover
10 ms. That keeps a declared hold meaning the same interval on a 60 Hz and a 144 Hz display.

Keys come from PsychoPy's `keyboard` module. A stimulus that collects its response passes its keys,
and `open_window` queues the reset of the keyboard's clock and the clearing of its queue on the same
onset flip as the trigger. The keyboard is polled after every flip, the first key ends the stimulus,
and its `rt` runs from the onset. A window kept with `from: offset`, each self-paced reading region
and each question open on their own first flip in the same way. Before the first trial, the script
shows the version's instructions and waits for the space bar. Escape there ends the run before a
data file is opened.

Each run writes a data file under `data/` beside the script, named
`<base>_p<participant>_v<version>_<date>-<time>.csv`, without the `_p` part when no participant
number is given. It holds one row per trial, written as the trial ends, so a run stopped with escape
leaves a valid file of the trials it completed. A row gives the participant, the version, the
replicate and the list, then the trial's own fields and trigger codes, then what the trial
recorded. `response`, `rt_ms` and `timed_out` hold the key, its reaction time in milliseconds and
whether the window closed without one. The reaction time runs from the onset of the stimulus the key
answers, or from the opening of a window kept with `from: offset`. `correct` says whether the key
was the trial's `answer`. It is 0 after a timeout and empty when the trial names no answer. In a
design without a response event, the question's key is the one scored. `region_rts_ms` holds each
self-paced reading region's time, joined by `|`, and `question_response` and `question_rt_ms` the
question's key and reaction time. Near its end, the row gives the measured `refresh_hz` and
`trigger_mode`, which is `hardware` when the codes went to the device and `mock` when they were
printed. It ends with `event_flips` and `event_onsets_ms`: the flips each event took and the time
of its first flip from the trial's first, joined by `|` in event order. A stimulus that collects
its response counts the blank after it as well, up to the key or the close of the window. The
realised durations can be checked against the declared ones there.

Stimulus text is never interpolated into the script, only read from the CSV at run time, so nothing
in a stimulus can become code. When the trigger device cannot be opened, on a development laptop,
on macOS or in continuous integration, the script follows `triggers.mode`, as
[the trigger device](#the-trigger-device) describes. By default, a mock port prints the codes and
the script still runs, after a notice that says so. The test suite exercises exactly that: a
mock-PsychoPy harness runs the generated script and asserts that the onset trigger is flip-locked.
It also checks that a key pressed while the target is shown is recorded with its reaction time from
the onset, and that every committed script writes one data row per trial. It runs each trigger
mode with and without a port, and a serial device that receives each code as one byte. With the
display simulated at 60, 144 and 240 Hz, it also checks every code each committed script sends,
the session markers included. Each must last at least 10 ms and lie within half a flip of the
hold, unless the next onset ends it.

### OpenSesame

The `.osexp` is generated block by block rather than from a template, and the result is a normal
OpenSesame experiment ([Mathôt et al., 2012](references.md#mathot-2012)): a trigger-setup inline
script, one inline script per event, a sequence and a loop.

```text
define inline_script lexsync_e1
	set description "Show the stimulus and collect the response from its onset"
	___prepare__
	_lexsync_c_e1 = Canvas()
	_lexsync_c_e1.text(_lexsync_row()[u'word'])
	_lexsync_c_e1_blank = Canvas()
	__end__
	___run__
	_t0 = _lexsync_c_e1.show()
	var.onset_time = _t0
	_lexsync_onset(int(var.get(u'condition_trigger', _eval=False)), _t0)
	_kb = Keyboard(keylist=[u'left', u'right'])
	_kb.flush()
	_key, _t = _lexsync_key(_kb, _t0 + 500 - _LEXSYNC_HALF_FRAME)
	if _key is None:
	    _lexsync_c_e1_blank.show()
	    _key, _t = _lexsync_key(_kb, _t0 + 500 + 2000)
	var.response = _key
	var.response_time = u'' if _key is None else _t - _t0
	var.timed_out = 1 if _key is None else 0
	_want = str(_lexsync_row().get(u'answer', u'')).strip()
	_got = u'' if _key is None else str(_key).strip()
	var.correct = (1 if _got == _want else 0) if _want else u''
```

OpenSesame prepares every item of a sequence before it runs any, so each script builds its canvases
in its prepare phase. Nothing is then built between one display and the next while the trial runs.
Between trials, the logger and the next trial's prepare phase run while the last display stays up,
so a trial's last event lasts a little longer than its duration. Each canvas is named after its
script, because all inline scripts share one workspace, and a shared name would show the canvas
prepared last. `Canvas.show()` blocks until the flip and returns its timestamp, so the trigger goes
out immediately after the onset it marks, and every wait is timed from that onset. The word and its
response window are one script. The keyboard is flushed once the trigger is out and polled until
half a frame before the word's 500 ms are up, so that the blank lands on the refresh that ends
them. It is then polled over the blank until the window closes. The response time is taken from
the word's onset. The script computes `correct` from the trial's `answer` itself. OpenSesame's own
`correct_response` is not used, since its variable syntax differs between 3.3 and 4.x.

The setup script measures the display's frame period once, as the median interval between 20
flips, and logs it as `lexsync_frame_ms`. When the measurement fails, as it does on a backend
without a blocking flip, it takes the period from `presentation.assumed_refresh_hz`. It also
defines the helpers the event scripts call. `_lexsync_onset` sends a code, `_lexsync_wait` sleeps
until a time measured from an onset, and `_lexsync_key` polls the keyboard until one. Each resets a
code on the way once its hold is up, so a code is held for `trigger_hold_ms` whether its event is
longer or shorter. The legacy clock the experiment selects counts whole milliseconds, so the waits
are kept to the millisecond, and so is a hold that ends during one. Two scripts around the loop
send the session markers, `lexsync_session_start` with 254 and `lexsync_session_end` with 255. The
trigger device writes a code and returns. It used to hold each code for a fixed 10 ms before
returning. That lengthened every triggered event, and the schema's hold went unused. A test in the
suite runs the generated scripts with the display simulated at 60, 120 and 144 Hz. It checks that
the priming experiment's prime and mask last the flips the PsychoPy script gives them, and that
every code lasts the hold.

The setup block opens the device `triggers.backend` names, the parallel port or the serial port
`triggers.serial_port`, and follows `triggers.mode` when it cannot. Under `auto`, it falls back to
a printing stub, so the experiment opens and runs on a machine with no trigger hardware. An inline
script after it, `lexsync_trigger_notice`, then says so before any other screen and waits for C.
Under `hardware`, the setup stops the experiment. The setup used to set the backend to parallel on
the line before its serial branch, so a serial device needed the script edited by hand. That
branch then took the first serial port it found. Every trial logs `lexsync_trigger_mode`, and
`test_mode` is still `yes` when the codes are printed. OpenSesame takes full screen or a window
from the mode it is launched in, whatever the generated file's `fullscreen` line says.

The word in that script does not come from OpenSesame's variable store, because OpenSesame
evaluates what a loop table puts there. In both versions, a cell holding `[=...]` runs as Python,
and so does one holding a single `{` in OpenSesame 4.x, where it is read as an f-string, or starting
with `=` in 3.3. Both versions also retype a word such as `nan` or `007`, and 4.x shows `True` as 1.
In 4.x, `infinity` and `nan`, both in the English lexicon, stop the session. An item table passed
between laboratories could otherwise run code on the machine that presents it.

The loop table, `<base>_opensesame.csv`, therefore holds numbers only: `lexsync_row`, the trial's
position in loop order, with `lexsync_trial`, `lexsync_list`, `lexsync_set`, the trigger codes,
`critical_region` and any per-trial duration. The prefix matters because OpenSesame 4 makes every
loop column a global of the inline scripts, where `list` and `set` would shadow Python's built-in
functions of those names. The presented text, `condition`, `block` and `answer` are in a companion
file, `<base>_opensesame_text.csv`, which the setup script reads with Python's `csv` module, and
each script looks up its trial's row by `lexsync_row`. Copy both files with the experiment. A value
in a numeric column that is not a plain number is refused when the experiment is generated. The
feedback script reads the response without evaluation, so a timeout shows `no_response` in both
versions. These rules were checked against the sources of OpenSesame 3.3.14 and 4.1.20.

Two details in the generated file are deliberate. The loop is set to `sequential`, because
OpenSesame's default is random, which would discard the seeded trial order the CSV is sorted by and
put this target out of step with the other two. A response kept after the stimulus with
`from: offset` is a `keyboard_response` preceded by a blank canvas. A `keyboard_response` draws
nothing, so the preceding stimulus would otherwise stay on screen for the whole response window
instead of offsetting at its stated duration. It runs none of lexsync's code either, so the script
that shows the blank first holds out a code still held. After a stimulus shorter than the hold, the
window therefore opens when the hold is up, and `response_time`, which OpenSesame times from the
item's start, runs from there. A script after it records `timed_out` and `correct`.
Before the loop, an inline script, `lexsync_instructions`, shows the instructions and waits for the
space bar, and escape there stops the session. OpenSesame's canvas reads a subset of HTML, so the
script writes the text with `&`, `<` and `>` escaped and each line break as `<br />`.
A structural validator in the test suite checks the generated file's blocks and references. A second
test runs its scripts under an emulation of each version's variable store, on item text that
OpenSesame would otherwise evaluate.

OpenSesame writes nothing to its log file without a logger item, so every trial ends with one,
`lexsync_logger`, which writes every variable. Self-paced reading sets `lexsync_region_rts`, each
region's reading time joined by `|`, and a question sets `question_response` and `question_rt`. Each
trial starts by clearing the response variables, so a block that skips a response event cannot log
the previous trial's key. Before the logger, a script copies the trial's `condition`, `block` and
`answer` from the text table into `lexsync_condition`, `lexsync_block` and `lexsync_answer`. Both
versions' loggers write a variable without evaluating it.

### jsPsych

The browser export is a single HTML file carrying the same rendered events and the trial data
inline. It opens with a welcome screen that shows the instructions and waits for the space bar.
It attaches each item's design fields to every recorded row and ends by saving the collected data
as a CSV download, so a generated experiment gathers usable data with no server behind it. The
jsPsych library and its stylesheet load from a content delivery
network, so the first run needs an internet connection. Each of the three files is loaded with
Subresource Integrity, its SHA-384 and `crossorigin="anonymous"`, so the browser refuses a copy
that differs from the published release. A page that collects participants' responses therefore
runs only the code it was written with. To run offline, point the tags at downloaded copies and
serve the folder over http, or remove each tag's `integrity` and `crossorigin` attributes. A
browser refuses the CORS request that a page opened from a `file://` address would make for a
local copy, so it could not check the hash. A target and its response window are one
jsPsych trial, recorded with `lexsync_event` set to `target`. It accepts the response keys from the
target's onset, shows the target for its duration and runs on for the timeout. The first key ends
it, so its `rt` is timed from the target's onset.

Two things are handled on the way out. Event-model key names are mapped to browser key names, so
`left` becomes `arrowleft` and `space` becomes a literal space, in the events and in each trial's
`answer`, since jsPsych records the key pressed by that name. The design's free-text `language`
label is mapped to a BCP 47 tag for the `lang` attribute, falling back to `und` rather than emitting
`lang="english"`, which no user agent can resolve. A design may state `language_tag` outright.

!!! note "The browser target records triggers, it does not send them"

    A browser cannot drive a parallel port. Onset triggers are written into each trial's recorded
    data, which is enough to reconstruct the design offline but not to synchronise an amplifier.
    Online EEG synchronisation needs WebSerial, LSL or a photodiode. The two laboratory targets are
    where the hardware timing lives.

Every worked design in the repository is published as one of these files, which is what the Demo
link in the header opens.

### Checking the timing

The durations above are what the generated code asks for, and what the test suite's simulated
displays confirm. A real display adds delays no software can see, such as an LCD's input lag. A
study whose effect depends on a duration or an onset should therefore be measured on the machine
that will run it. A photodiode on the screen, recorded by the same amplifier as the trigger port,
measures the display and the triggers on one clock.

1. Tape the photodiode over the place where the critical stimulus appears. White text on a black
   background drives most diodes. A small stimulus, such as a fixation cross, may need a white
   patch drawn with it for the pilot.
2. Run a pilot session on the laboratory machine, at the refresh rate and in the screen mode of
   the study, and record the diode and the trigger channel together. With
   `triggers.mode: hardware`, neither the pilot nor the study can start without the trigger
   device.
3. For each trial, measure the time from the trigger's onset to the diode's rise. It should be
   nearly constant. Its mean is the display's lag, which includes the time the screen takes to
   draw down to the diode and, on an LCD, an input lag that can exceed 10 ms. The analysis can
   subtract it. Its spread is the jitter an ERP average will carry.
4. Measure each critical stimulus from the diode's rise to its fall and compare it with the
   flips its duration asks for at that refresh rate: a 50 ms prime is three flips at 60 Hz and
   seven, 48.6 ms, at 144 Hz.
5. Measure the trigger pulses. Each should last about `trigger_hold_ms`, 50 ms by default, unless
   the next onset ends it sooner, and 254 should come before the first trial and 255 after the
   last.
6. Measure again after any change to the machine, the display, its refresh rate or the
   presentation software.

## Running a counterbalanced experiment

A design with more than one list, or with resampled item sets, has several presentation versions.
A version is one (replicate, list) pair of the presented trials, and the versions are numbered from 1
in that order, so in a design without replicates version *k* is list *k*. Each participant is
presented one version. Presenting them all would show each target of a Latin square in every
condition, which is the repetition the rotation exists to prevent, and every item sample of a
resampled design. Participant *p* runs version `((p - 1) mod V) + 1` of the *V* versions, the rule
`participant_table` allocates by. Participants 1 to 4 of a two-list design therefore run lists 1, 2,
1 and 2. `lexsync.scripting.presentation_versions` lists the versions of a set of trials, and every
generated experiment carries the same list.

```python
# illustrative: the versions of a counterbalanced two-list design
lexsync.scripting.presentation_versions(stimuli)
# [{'version': 1, 'replicate': 1, 'list': 1, 'n_trials': 12},
#  {'version': 2, 'replicate': 1, 'list': 2, 'n_trials': 12}]
```

The PsychoPy script runs the participant's version when launched as
`python <base>_psychopy.py --participant 3`. `--version 2` runs a version outright, and so does
`--list 2` in a design without replicates. Launched with none of these, the script asks for the
participant number and the version in a dialogue, where a blank version takes the participant's by
the rule. A version the script does not have stops the run, with a message, before any window
opens.

The jsPsych page reads the same choice from its address: `page.html?participant=3`,
`?version=2`, or `?list=2` without replicates, each a whole number from 1. A page with more than
one version, opened with none of these, shows a screen saying how to open it and runs nothing. A
static page cannot count its participants, so a study recruited online without participant numbers
hands out one `?version=k` link per version. The welcome screen counts the trials of the version,
every data row carries the participant, the version, the list and the replicate, and the data file
is named `<title>_p<participant>_v<version>.csv`.

The OpenSesame target writes one experiment per version, `<base>_list<k>.osexp`, or
`<base>_rep<r>_list<k>.osexp` when the versions span several replicates. Each has its own loop and
text tables, holding only that version's trials, and the experimenter opens the participant's. At
start-up, each experiment compares the subject number OpenSesame asks for with its own version.
When that participant would normally run another one, it says so and waits for a key. Space goes on
with this file, and escape stops the session. A design with one version keeps `<base>.osexp`. The
check runs once, before the loop, so the experiment needs no run-if condition, a syntax that differs
between OpenSesame 3.3 and 4.x.

The datasheet records the number of versions as `counterbalancing.versions` and the rule as
`counterbalancing.assignment`, and its Methods text says that each participant was presented one
version. Its artefact list and the run log name every file `export_experiments` wrote, the loop and
text tables included, since those hold the trial order and the trigger codes the experiments
present. The loop tables keep each version's trials together, ordered by replicate, list and trial.
They carry `replicate` when the design has one. Item codes are allocated by set, so in a resampled
design an item code identifies an item only within its replicate, which the `replicate` column
tells apart.
