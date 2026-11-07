# Security policy

## Reporting a vulnerability

If you find a security problem in lexsync, please report it privately by email
to pcbernabeu@gmail.com rather than opening a public issue. A short description
of the problem and, where possible, a way to reproduce it is enough to get
started. You can expect an acknowledgement within a few days, and we will keep
you informed as the issue is investigated and resolved.

## A note on credentials

lexsync handles no credentials of its own. It reads corpora and design files from
disk and writes stimulus tables and experiment scripts. The R and Python packages
open a network connection only for a download you ask for. `fetch_corpus()`, or
`lexsync fetch` on the Python command line, downloads the file a corpus's registry
entry names, from an `https` or `http` address only. It checks the file against
the SHA-256 the registry records, where the registry records one.

The generated PsychoPy and OpenSesame experiments open a parallel or serial port
for EEG triggers. When that port cannot be opened, they print the codes instead,
or stop if the schema's `triggers.mode` is `hardware`. Under `mock`, they print
the codes without trying the port. Neither opens a network connection. The
generated jsPsych page loads the jsPsych library, its keyboard-response plugin
and its stylesheet from unpkg, each verified against its SHA-384 hash by
Subresource Integrity. It saves its data only as a CSV download in the
participant's browser.

## A note on design files

A design file is meant to be shared, for example attached to a pre-registration,
deposited with a paper or handed to a collaborator running the other engine. A
design you did not write is therefore input from someone else, and the files
lexsync generates from it are meant to be run, as a PsychoPy script on a lab
machine or an HTML page in a browser.

lexsync treats a design accordingly. Presented stimuli are carried as data, never
as code. The PsychoPy script reads them from its conditions file. An OpenSesame
experiment, whose loop table holds numbers only, reads them with Python's `csv`
module from the text table beside it. The jsPsych page holds them as JSON with
`<`, `>` and `&` escaped. The design's instructions are carried as data too, as
JSON in the PsychoPy script and the jsPsych page and as an escaped string literal
in the OpenSesame script. A design's name, language label and font, the
parallel-port address and serial device name, and the column names on jitter and
feedback events reach a code position as written. This metadata is validated
before it is written into a generated file. A value that could end a string
literal or open a tag raises an error that names the field. Both engines apply the
same rule, and `test_injection.py` and `test-injection.R` check it.

Even so, read a design before you run it, as you would a script. If you find a
value that reaches a generated file without being checked, report it to the
address above as a security bug.
