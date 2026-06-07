# OpenSesame templates

lexsync generates a complete, plain-text OpenSesame experiment (`.osexp`) for
each design. The generator (`scripting` module, function `export_opensesame`)
builds the file programmatically so that its tab-sensitive structure is always
valid; it is modelled on a proven-working experiment from González Alonso et
al. (2025).

The two Python snippets here are the trigger code that the generated `.osexp`
embeds inline. They are provided separately so you can paste them into an
existing OpenSesame experiment if you prefer to wire triggers into your own
design:

- `inline_trigger_setup.py` — paste into an `inline_script` **Prepare** tab at
  the start of the experiment. Opens the parallel port (default) or a serial
  port, with a test-mode fallback that prints codes when no device is present,
  and defines `send_trigger(code)`.
- `inline_send_triggers.py` — paste into an `inline_script` **Run** tab placed
  immediately after the target-word sketchpad. Sends the onset marker then the
  condition marker for each trial.

The generated `.osexp` expects a loop table (CSV) beside it, providing the
columns `word`, `target_word_trigger` and `condition_trigger` per trial.

Timing note: OpenSesame sends the marker from the item that follows the word
sketchpad, so it is sequence-ordered. The PsychoPy export instead binds the
onset marker to the exact stimulus flip via `win.callOnFlip`. This asymmetry is
discussed in the accompanying manuscript.
