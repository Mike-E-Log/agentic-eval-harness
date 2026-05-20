# vhs tape — regenerates docs/recorded-run.gif deterministically.
# Install vhs: https://github.com/charmbracelet/vhs  (winget install charmbracelet.vhs)
# Render:      vhs docs/recorded-run.tape   (run from the repo root, with aeh installed)
#
# PYTHONUTF8=1 makes the renderer emit the unicode gate (σ, ·, ⚠) instead of the
# ASCII fallback, so the hero GIF shows the dispersion glyphs.

Output docs/recorded-run.gif

Require aeh

Set Shell "powershell"
Set FontSize 16
Set Width 1100
Set Height 760
Set Padding 24
Set Theme "Dracula"

Type "$env:PYTHONUTF8=1; aeh demo"
Sleep 500ms
Enter
Sleep 4s
