# lexsync OpenSesame trigger sending -- paste into an inline_script 'Run' tab.
# -------------------------------------------------------------------------
# Requires inline_trigger_setup.py to have run first in the experiment (it
# defines send_trigger). Place this inline_script immediately AFTER the target
# word sketchpad in the sequence, so the onset marker is sent as soon as the
# word has been shown. The loop table supplies var.target_word_trigger and
# var.condition_trigger for each trial.

send_trigger(var.target_word_trigger)   # onset marker for the target word
send_trigger(var.condition_trigger)     # condition marker
