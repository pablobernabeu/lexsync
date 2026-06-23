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
  and defines `send_trigger(code)` and `var.word_duration_ms`.
- `inline_send_triggers.py` — paste into an `inline_script` **Run** tab. It
  draws and shows the target word and sends the onset marker immediately after
  `show()` returns.

The generated `.osexp` expects a loop table (CSV) beside it, providing the
columns `word`, `target_word_trigger` and `condition_trigger` per trial.

Timing: the word is drawn and shown from inside an `inline_script`, and the
trigger is sent immediately after `canvas.show()` returns. Because `show()`
blocks until the display refresh (with the `psycho`/`xpyriment` backends), the
marker is written immediately after the verified stimulus flip. It is therefore
time-locked to onset. This is the OpenSesame-recommended method, equivalent in
effect to PsychoPy's `win.callOnFlip`. A photodiode check is still advisable for
any onset-critical study.
