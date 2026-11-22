# The item fields a design needs, from its paradigm and its events

The item fields a design needs, from its paradigm and its events

## Usage

``` r
required_fields(design)
```

## Arguments

- design:

  A parsed design list.

## Value

Character vector of the item fields the design's trials reference.

## Examples

``` r
required_fields(list(paradigm = "categorisation"))
#> [1] "target"   "category" "answer"  
```
