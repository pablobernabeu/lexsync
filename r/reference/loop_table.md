# Per-trial table carrying exactly the fields the events reference

The rows are in presentation order within each version: by replicate
when the table has one, then by list, then by trial. `trial` restarts at
1 in every list and in every replicate, so ordering on it alone
interleaved the versions. The sort is stable, so rows that tie keep
their incoming order and the two engines write the same table. A design
with `counterbalance.orders` carries `order_1` to `order_m` after the
columns that place a trial, each trial's position in each order, which
the experiments sort a version by.

## Usage

``` r
loop_table(stimuli, events = NULL)
```
