# Validate one response key, which is written into the generated experiments

OpenSesame takes the keys as `set allowed_responses "a;b"` on one line
of a line-oriented format, so a key containing a quote closed the string
and a newline ended the line, and the rest of the value became new
top-level items in the experiment, including an inline_script whose body
runs.

## Usage

``` r
clean_key(value, field = "an event's `keys`")
```

## Arguments

- value:

  A value coerced to a single string.

- field:

  Field name, for error messages.

## Value

The value as a plain string.
