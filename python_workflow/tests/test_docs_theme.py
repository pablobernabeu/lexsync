"""The documentation theme's header pill is the one control the brand restyles
wholesale, so Material's own focus styling no longer reaches it. Nothing else in
the suite reads the stylesheet, and a missing focus state is invisible to anyone
who navigates with a pointer.
"""
import re
from pathlib import Path

BRAND_CSS = Path(__file__).resolve().parents[1] / "docs" / "stylesheets" / "brand.css"


def test_demo_pill_answers_keyboard_focus():
    css = BRAND_CSS.read_text(encoding="utf-8")
    blocks = re.findall(
        r'\[data-md-component="demo-link"\]:focus-visible[^{]*\{([^}]*)\}', css
    )
    assert blocks, "the Demo pill has no :focus-visible rule"
    declarations = " ".join(blocks)
    # The inversion alone would be indistinguishable from a hovered pill.
    assert "outline" in declarations
    assert "background" in declarations
