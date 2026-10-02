# `$` on a list matches a name partially when no name matches exactly, so a design
# key that only began another key's name used to stand in for it (`font_size` read
# as `font`). The package reads design and schema lists with `[[`, and this option
# turns any partial match the suite still reaches into a warning, which the CI
# parity job counts as a failure.
options(warnPartialMatchDollar = TRUE)
