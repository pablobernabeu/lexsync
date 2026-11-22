# Validate a metadata value interpolated into generated code or markup

A design's name, language label and font are not stimuli. They are not
in the loop table the experiment reads at run time. They are substituted
straight into the PsychoPy script, the OpenSesame inline Python and the
jsPsych HTML, so a quote or an angle bracket there would be read as
code, not text. A design file is meant to be shared and re-run by
someone else, so an unvalidated one could carry code as well as
configuration.

## Usage

``` r
clean_meta(value, field = "value", max_len = 200L)
```

## Arguments

- value:

  A value coerced to a single string.

- field:

  Field name, for error messages.

- max_len:

  Maximum permitted length in characters.

## Value

The value as a plain string.

## Details

Such a value is refused, not escaped. Escaping correctly would need
three different escapes for three targets in two engines, six places to
get wrong, and it would change the bytes the two engines write. Refusing
is one rule that leaves every legitimate value (such as `en_lexdec`,
`english`, `Courier New` or `SimHei`) unchanged.
