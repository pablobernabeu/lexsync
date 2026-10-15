# Run `check` again with the session's character type set to C, where R translates
# text through ASCII: paste() renders a latin1 letter as escape text such as "<e9>",
# enc2utf8() does the same to the bytes of an unmarked string, and a connection that
# re-encodes stops at the first byte ASCII lacks. Every platform R runs on names this
# locale "C", so the switch fails, and the test skips, only on an unusual build. The
# restore is registered before the switch, so a switch that changes the locale
# without reporting "C" cannot leak into later tests.
in_c_ctype <- function(check) {
  old <- Sys.getlocale("LC_CTYPE")
  on.exit(Sys.setlocale("LC_CTYPE", old), add = TRUE)
  skip_if(!isTRUE(suppressWarnings(Sys.setlocale("LC_CTYPE", "C")) == "C"),
          "cannot switch to the C locale on this platform")
  check()
}
