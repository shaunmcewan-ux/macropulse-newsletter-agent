"""
Re-skin the templates produced by _make_templates.py to match macropulse.uk live styling:
- Cool blue-grey background (not black)
- Newsreader-style serif wordmark (no SVG glyph)
- 4-state rail with website state colours (replaces the gradient pulse bar)

Run AFTER _make_templates.py.
"""

import os
import re

HERE = os.path.dirname(__file__)
TPL  = os.path.join(HERE, "templates")


# ── Live website palette ─────────────────────────────────────────────────────
NEW_BG_PAGE   = "#0c141b"
NEW_BG_CARD   = "#111a23"
NEW_BORDER    = "#1c2935"
NEW_TEXT_HI   = "#edf3f7"
NEW_TEXT_MID  = "#b9c4cc"
NEW_TEXT_LO   = "#7c8a95"
NEW_ORANGE    = "#ff9d2f"
NEW_ORANGE_LT = "#ffbd69"
NEW_SILVER    = "#d9dfe5"

# Header gradient rule: replace the rainbow `Sell→Hold→Buy BTC→Alt Season→Top`
# strip with a brand-consistent fade-in-fade-out orange line.
RAINBOW_RULE_RE = re.compile(
    r'<tr><td height="1" bgcolor="#[a-fA-F0-9]+" style="height:1px;line-height:1px;'
    r'font-size:0;background:#[a-fA-F0-9]+;'
    r'background-image:linear-gradient\(90deg,#dc2626 0%,#f97316 24%,#eab308 48%,'
    r'#22c55e 76%,#a855f7 100%\);">&nbsp;</td></tr>'
)
BRAND_RULE = (
    '<tr><td height="1" bgcolor="#1c2935" style="height:1px;line-height:1px;font-size:0;'
    'background:#1c2935;background-image:linear-gradient(90deg,rgba(255,157,47,0) 0%,'
    '#ff9d2f 50%,rgba(255,157,47,0) 100%);">&nbsp;</td></tr>'
)

# Same-named keys, old → new
SWAPS = [
    # Backgrounds
    ("background:#0a0a0a",          f"background:{NEW_BG_PAGE}"),
    ("bgcolor=\"#0a0a0a\"",         f"bgcolor=\"{NEW_BG_PAGE}\""),
    ("background:#141414",          f"background:{NEW_BG_CARD}"),
    ("bgcolor=\"#141414\"",         f"bgcolor=\"{NEW_BG_CARD}\""),
    ("background:#1a1a1a",          f"background:{NEW_BG_CARD}"),  # indicator tiles
    ("bgcolor=\"#1a1a1a\"",         f"bgcolor=\"{NEW_BG_CARD}\""),
    # Card borders
    ("border:1px solid #232323",    f"border:1px solid {NEW_BORDER}"),
    # Body text colour — primary
    ("color:#ffffff",               f"color:{NEW_TEXT_HI}"),
    ("color: #ffffff",              f"color:{NEW_TEXT_HI}"),
    # Secondary text — translate rgba(255,255,255,0.68) etc
    ("color:rgba(255,255,255,0.68)",  f"color:{NEW_TEXT_MID}"),
    ("color: rgba(255,255,255,0.68)", f"color:{NEW_TEXT_MID}"),
    ("color:rgba(255,255,255,0.92)",  f"color:{NEW_TEXT_HI}"),
    # Muted
    ("color:rgba(255,255,255,0.45)",  f"color:{NEW_TEXT_LO}"),
    ("color: rgba(255,255,255,0.45)", f"color:{NEW_TEXT_LO}"),
    # Brand orange
    ("color:#f97316",               f"color:{NEW_ORANGE}"),
    ("background:#f97316",          f"background:{NEW_ORANGE}"),
    ("bgcolor=\"#f97316\"",         f"bgcolor=\"{NEW_ORANGE}\""),
    ("border-left:3px solid #f97316", f"border-left:3px solid {NEW_ORANGE}"),
    # Link colour
    ("a { color: #f97316;",         f"a {{ color: {NEW_ORANGE};"),
    # Outlook fallback chip colours stay the same (already designed for dark)
]


# ── New wordmark (replaces ring SVG + word lockup) ───────────────────────────
def wordmark_html(size_px: int) -> str:
    """Pure-text MacroPulse wordmark matching the website."""
    return (
        '<td valign="middle" align="left">'
        f'<span style="font-family:Georgia,\'Times New Roman\',serif;'
        f'font-size:{size_px}px;font-weight:600;line-height:1;'
        f'letter-spacing:-0.045em;color:{NEW_SILVER};'
        f'-webkit-font-smoothing:antialiased;">MacroPulse</span>'
        '</td>'
    )


# Matches the entire two-cell header lockup (SVG icon td + wordmark td)
HEADER_LOCKUP_RE = re.compile(
    r"<table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\">\s*"
    r"<tr>\s*"
    r"<td valign=\"middle\" style=\"padding-right:12px;line-height:0;\">\s*"
    r"<svg width=\"32\".*?</svg>\s*"
    r"</td>\s*"
    r"<td valign=\"middle\" style=\"font-family:Arial[^\"]+\"[^>]*>\s*"
    r"Macro<span[^>]+>Pulse</span>\s*"
    r"</td>\s*"
    r"</tr>\s*"
    r"</table>",
    re.DOTALL,
)

FOOTER_LOCKUP_RE = re.compile(
    r"<table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" align=\"center\">\s*"
    r"<tr>\s*"
    r"<td valign=\"middle\" style=\"padding-right:10px;line-height:0;\">\s*"
    r"<svg width=\"24\".*?</svg>\s*"
    r"</td>\s*"
    r"<td valign=\"middle\" style=\"font-size:18px[^\"]+\"[^>]*>\s*"
    r"Macro<span[^>]+>Pulse</span>\s*"
    r"</td>\s*"
    r"</tr>\s*"
    r"</table>",
    re.DOTALL,
)


# ── New 4-state pulse rail (replaces the gradient bar SVG + caption row) ────
# The whole pulse-strip CARD content gets a rewrite. We keep the outer card
# wrapper but replace its body content with token-driven markup.
def new_pulse_rail() -> str:
    """
    Inner HTML for the dial card. Layout (top → bottom):
      - eyebrow "The Cycle"
      - phase headline (large serif, e.g. "BTC Accumulation.")
      - D1 Phase Arc dial (centered, full-width SVG)
      - phase summary paragraph

    Tokens: {{DIAL_PHASE}}, {{DIAL_SVG}}, {{DIAL_SUMMARY}}
    """
    return (
        f'<div style="font-family:Georgia,\'Times New Roman\',serif;font-size:11px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:{NEW_TEXT_LO};">The Cycle</div>\n'
        f'              <h2 style="font-family:Georgia,\'Times New Roman\',serif;font-size:32px;line-height:1.1;letter-spacing:-0.03em;color:{NEW_TEXT_HI};margin:14px 0 4px;font-weight:600;">{{{{DIAL_PHASE}}}}<span style="color:{NEW_ORANGE};">.</span></h2>\n'
        f'              <div style="margin:20px auto 0;text-align:center;line-height:0;">{{{{DIAL_SVG}}}}</div>\n'
        f'              <p style="font-family:Georgia,\'Times New Roman\',serif;font-size:18px;line-height:1.55;color:{NEW_TEXT_MID};margin:22px 0 0;font-weight:400;">{{{{DIAL_SUMMARY}}}}</p>'
    )


# Match the whole content block of the pulse-strip card. The block starts with
# the "MacroPulse Dial" eyebrow and ends with the labels caption row.
PULSE_BODY_RE = re.compile(
    r"<div style=\"font-family:Arial,Helvetica,sans-serif;font-size:11px;"
    r"font-weight:600;letter-spacing:0\.28em;text-transform:uppercase;"
    r"color:[^\"]+;\">MacroPulse Dial</div>"
    r".*?"
    r"\{\{PULSE_LABELS_ROW\}\}\s*</table>",
    re.DOTALL,
)


def reskin(s: str) -> str:
    # 0) Header rule: rainbow → brand fade
    s = RAINBOW_RULE_RE.sub(BRAND_RULE, s)

    # 1) Logo lockups → text wordmarks
    s = HEADER_LOCKUP_RE.sub(wordmark_html(28), s, count=1)
    s = FOOTER_LOCKUP_RE.sub(wordmark_html(22), s, count=1)

    # 2) Replace the pulse strip body (gradient SVG + caption row) with the rail
    new_body = new_pulse_rail() + "\n            </td></tr>"
    # The above closes the inner card cell early — but the outer </table></td></tr>
    # is still there. We must instead just replace the BODY content up to but
    # not including the closing </td></tr></table>. Tweak: match through the
    # PULSE_LABELS_ROW caption table's closing </table> and replace with our
    # new content (which itself ends with </p>).
    s = PULSE_BODY_RE.sub(new_pulse_rail(), s, count=1)

    # 3) Colour swaps (apply LAST so the wordmark uses the new silver color too)
    for old, new in SWAPS:
        s = s.replace(old, new)

    return s


def main():
    for name in ("monday", "friday"):
        path = os.path.join(TPL, f"{name}.html")
        with open(path, encoding="utf-8") as f:
            html = f.read()
        out = reskin(html)
        with open(path, "w", encoding="utf-8") as f:
            f.write(out)
        # quick check
        unresolved = set(re.findall(r"\{\{[A-Z_0-9]+\}\}", out))
        print(f"[reskin] {name}.html — {len(out):,} chars; tokens: {sorted(unresolved)}")


if __name__ == "__main__":
    main()
