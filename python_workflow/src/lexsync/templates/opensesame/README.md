# OpenSesame templates

lexsync generates a complete, plain-text OpenSesame experiment (`.osexp`) for
each design. The generator (`scripting` module, function `export_opensesame`)
builds the file programmatically so that its tab-sensitive structure is always
valid. It is modelled on a proven-working experiment from González Alonso et
al. (2025).

The two Python snippets here follow the trigger code that the generated `.osexp`
builds inline, with the differences noted below. They are provided separately so
you can paste them into an existing OpenSesame experiment if you prefer to wire
triggers into your own design:

- `inline_trigger_setup.py` goes into an `inline_script` **Prepare** tab at the
  start of the experiment. It opens the parallel port (default) or a serial
  port, with a test-mode fallback that prints codes when no device is present,
  and defines `send_trigger(code)` and `var.word_duration_ms`. The generated
  file defines no `var.word_duration_ms`, because each of its events carries
  its own duration.
- `inline_send_triggers.py` goes into an `inline_script` **Run** tab. It draws
  and shows the target word and sends the onset marker immediately after
  `show()` returns.

The generated `.osexp` expects two tables (CSV) beside it, and both must be
copied with it. OpenSesame evaluates the cells of a loop table: a cell holding
`[=...]` runs as Python, and so does one holding `{` in OpenSesame 4.x or
starting with `=` in 3.3. The loop table therefore holds numbers only, among them
the `condition_trigger` and `item_trigger` markers that `assign_triggers` adds.
The stimulus fields that the design's events reference (`word` for the
single-word designs, `prime` and `target` for priming, `sentence` and `question`
for self-paced reading) are in `<base>_opensesame_text.csv`. The generated
scripts read it with Python's `csv` module. The snippet above reads `var.word`
from your own loop table, so keep braces, square brackets and a leading `=` out
of the words there. Read that way, a word such as `nan` or `infinity` also
stops OpenSesame 4.x. The snippet sends `item_trigger` and then, once that
10 ms pulse has ended, `condition_trigger`, whereas the generated file sends one
marker at each onset, the one its event names. Adjust those names if you paste
the snippet into a design whose loop table names its markers differently.

A design with more than one counterbalancing list, or with resampled item sets,
has several presentation versions, and each participant runs one. It gets one
experiment per version, `<base>_list<k>.osexp` (`<base>_rep<r>_list<k>.osexp`
with resampled item sets), each with its own two tables holding only that
version's trials. Open the participant's: participant *p* runs version
((*p* - 1) mod *V*) + 1 of the *V* versions. Each experiment compares the
subject number OpenSesame asks for at start-up with its own version. When that
participant would normally run another, it says so and waits for a key. Space
goes on with this file, and escape stops the session.

A response after a text event is collected by that event's own script, from
the stimulus's onset. The keyboard is flushed as the stimulus appears and polled
through it and then through a blank screen, for the stimulus's duration and the
timeout together. The script sets `response`, `response_time` (from the onset),
`timed_out` and `correct` (the response scored against the trial's `answer`). A
response that a design keeps after the stimulus with `from: offset` is a
`keyboard_response` after a blank screen, and a script after it sets `timed_out`
and `correct`. Self-paced reading sets `lexsync_region_rts`, each region's
reading time joined by `|`, and a question sets `question_response` and
`question_rt`. Each trial starts by clearing these, copies its `condition`,
`block` and `answer` into `lexsync_condition`, `lexsync_block` and
`lexsync_answer`, and ends with a logger item, `lexsync_logger`, which writes
every variable to OpenSesame's log file.

Timing: the word is drawn and shown from inside an `inline_script`, and the
trigger is sent immediately after `canvas.show()` returns. Because `show()`
blocks until the display refresh (with the `psycho`/`xpyriment` backends), the
marker is written immediately after the verified stimulus flip. It is therefore
time-locked to onset, by the method OpenSesame recommends. The durations are
less exact, because the generated experiment builds each canvas at run time and
`send_trigger()` blocks for its 10 ms pulse before the event sleeps for its full
duration. Every event therefore overruns its stated length. At 60 Hz, a 50 ms
prime is predicted to last about 67 ms, and an 83 ms stimulus-onset asynchrony
about 117 ms. Check any onset-critical study with a photodiode.
