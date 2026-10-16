# Validate a serial device name, which is written into the experiments as text

The name is not escaped on its way into the generated code, so a quote
or a line break in it would end the string it lands in. Mirrors the
Python `clean_serial_port`.

## Usage

``` r
clean_serial_port(value, field = "triggers.serial_port")
```

## Arguments

- value:

  The device name, such as `"COM3"` or `"/dev/ttyUSB0"`.

- field:

  Field name, for error messages.

## Value

The value as a plain string.
