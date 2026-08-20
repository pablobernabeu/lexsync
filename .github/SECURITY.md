# Security policy

## Reporting a vulnerability

If you find a security problem in lexsync, please report it privately by email
to pcbernabeu@gmail.com rather than opening a public issue. A short description
of the problem and, where possible, a way to reproduce it is enough to get
started. You can expect an acknowledgement within a few days, and we will keep
you informed as the issue is investigated and resolved.

## A note on credentials

lexsync handles no credentials of its own. It reads corpora and design files from
disk and writes stimulus tables and experiment scripts, so there is no key or
token for it to store or leak. The generated PsychoPy script opens a parallel port
for EEG triggers and falls back to a mock port when no driver is present, and it
never opens a network connection.

## A note on design files

A design file is meant to travel: attached to a pre-registration, deposited with a
paper, handed to a collaborator running the other engine. That makes a design you
did not write an input from someone else, and the files lexsync generates from it
are meant to be run, a PsychoPy script on a lab machine or an HTML page in a
browser.

lexsync treats a design accordingly. Presented stimuli are always carried as data
in the loop table the experiment reads at run time, never interpolated into
generated code, and the metadata that does reach a code position (a design's name,
language label and font, the parallel-port address, and the column names on jitter
and feedback events) is validated on the way in. A value that could end a string
literal or open a tag is refused, and the message names the field. Both engines
apply the same rule, and `test_injection.py` and `test-injection.R` pin it.

Even so, read a design before you run it, as you would a script. If you find a
value that reaches a generated file without being checked, that is a security bug
and the address above is the right place for it.
