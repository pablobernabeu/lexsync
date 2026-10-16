# Refuse a value the two engines could not write identically

Nothing lexsync computes reaches these magnitudes (frequencies are Zipf
values under 8, counts and durations under 1e6), but a joined norm
table, a supplied pool or an item table may carry any column the user
likes, and those columns go straight into the stimuli CSV. The guard
lives in both engines so that each refuses the same design; one engine
accepting what the other rejects is a difference of its own.

## Usage

``` r
.check_csv_writable(x)
```

## Arguments

- x:

  A data frame about to be written.

## Value

`x`, invisibly, or an error.
