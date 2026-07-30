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
for EEG triggers and falls back to a mock port when no driver is present; it never
opens a network connection.
