# Refuse a value the two engines could not write identically

A double column (an integer column passes) is refused, naming the column
and the value, when a finite value's magnitude is 1e15 or more, where
readr's number layout cannot be reproduced in Python, or when a value
that is not a whole number lies between 2^49 and 1e15 and has two
equally short decimal forms, of which the two writers pick opposite
ones.

## Usage

``` r
.check_csv_writable(x)
```

## Arguments

- x:

  A data frame about to be written.

## Value

`x`, invisibly, or an error.

## Details

Nothing lexsync computes reaches these magnitudes (frequencies are Zipf
values under 8, counts and durations under 1e6), but a joined norm
table, a supplied pool or an item table may carry any column the user
likes, and those columns go straight into the stimuli CSV. Both engines
apply this check, so that each refuses the same design, since one engine
accepting what the other rejects would be a difference of its own.
