# Build a complete plain-text OpenSesame experiment from rendered events

The loop table and its companion text table are both looked up through
OpenSesame's file pool, which also searches the experiment's own folder.
Mirrors `build_osexp` in the Python engine.

## Usage

``` r
build_osexp(
  design,
  conditions_file,
  schema,
  rendered,
  font = "mono",
  text_file = NULL,
  version = NULL,
  n_versions = NULL,
  instructions = NULL,
  order = 1L,
  n_orders = 1L
)
```

## Arguments

- design:

  A parsed design configuration.

- conditions_file:

  File name of the loop table.

- schema:

  The parsed global schema: its trigger settings,
  `presentation.text_height_px` and `presentation.assumed_refresh_hz`,
  the rate the frame period falls back to when the start-up measurement
  fails.

- rendered:

  Rendered events, from
  [`render_events()`](https://pablobernabeu.github.io/lexsync/r/reference/render_events.md),
  with each `length_of` mask already written out for the trials, as the
  exporters do. A mask that still carries `length_of` shows its single
  character.

- font:

  The font family OpenSesame draws text in.

- text_file:

  File name of the companion text table. `NULL` (the default) puts
  `_text` before the `.csv` of `conditions_file`.

- version, n_versions:

  The experiment is version `version` of `n_versions`. With more than
  one version, or more than one order, it checks OpenSesame's subject
  number against its own before the loop and warns when the participant
  would normally run another. `NULL` (the default) writes no check.

- instructions:

  The text the experiment shows before the loop, waiting for the space
  bar. `NULL` (the default) takes list 1's, the design's own
  `instructions` or lexsync's for its task.

- order, n_orders:

  The experiment presents trial order `order` of `n_orders`. With more
  than one order, the check compares the participant's order too, and
  the experiment sets `lexsync_order`, which every trial logs.

## Value

The experiment's text, one string. Each trial starts by clearing the
last trial's responses and ends with a logger item. The setup script
opens the trigger device the schema names, measures the frame period and
defines the helpers that time the events and hold their codes. A notice
follows it when no codes will be sent, and the session markers 254 and
255 are sent just before and after the loop. Every text is drawn at
`presentation.text_height_px`. A `response` event collected from the
offset, which becomes a keyboard_response, is refused when it carries
`blocks`, since the block restriction is applied only within lexsync's
inline scripts. Restrict a feedback or stimulus event instead.
