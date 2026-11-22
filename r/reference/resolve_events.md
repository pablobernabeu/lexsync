# The trial events of a design: its own `events`, or else its paradigm's

The trial events of a design: its own `events`, or else its paradigm's

## Usage

``` r
resolve_events(design)
```

## Arguments

- design:

  A parsed design list.

## Value

The list of trial events the design presents.

## Examples

``` r
vapply(resolve_events(list(paradigm = "lexical_decision")),
       function(e) e$type, character(1))
#> [1] "fixation" "text"     "response" "blank"   
```
