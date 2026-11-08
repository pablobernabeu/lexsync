---
name: Bug report
about: Report something that is not working as expected
title: ''
labels: bug
assignees: ''
---

### Describe the bug

A clear description of what went wrong and what you expected instead.

### Reproducible example

A small, self-contained example helps a great deal. Never paste a secret, such as
an API key or token, into an issue. Replace it with a placeholder.

```
# your example here (R reprex or Python snippet)
```

### Design and run log

If the problem came up in a pipeline run, paste the design YAML, and paste or
attach the run log. The run writes the log to the `reports/` folder of its output
directory, as the file ending `_run_log_R.md` from R or `_run_log_py.md` from
Python. Together, the design YAML and the run log record the inputs and every
step that ran.

### Environment

<details>

```
# R: output of sessionInfo()
# Python: Python version, lexsync version, operating system
```

</details>

### Anything else

Any other context that might help.
