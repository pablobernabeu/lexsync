"""The documentation site's header pill, which the brand restyles wholesale.

Material's own focus styling no longer reaches the Demo pill, so without a rule of the
brand's own a reader moving through the header with the keyboard cannot see where the
focus is. Nothing else in the suite reads the stylesheet. The R site's Demo link has
such a rule (R_workflow/pkgdown/extra.scss), and the shared Meridian brand carries the
same one for its App pill.
"""
import re

import pytest
from helper_repo import REPO

BRAND_CSS = (REPO / "python_workflow" / "docs" / "stylesheets" / "brand.css") if REPO else None

pytestmark = pytest.mark.skipif(REPO is None, reason="the documentation sources are not in this tree")


def test_the_demo_pill_answers_keyboard_focus():
    css = BRAND_CSS.read_text(encoding="utf-8")
    blocks = re.findall(r'\[data-md-component="demo-link"\]:focus-visible[^{]*\{([^}]*)\}', css)
    assert blocks, "the Demo pill has no :focus-visible rule"
    declarations = " ".join(blocks)
    # The inversion the pointer gets, and a ring, without which a focused pill would look
    # like a hovered one.
    assert "background" in declarations
    assert "outline" in declarations
