"""
One-shot script that converts the Claude Design Monday/Friday templates
into Python-renderable templates with {{TOKEN}} placeholders.

Run once. Outputs:
  mailer/templates/monday.html
  mailer/templates/friday.html
"""

import os
import re

HERE = os.path.dirname(__file__)
ROOT = os.path.dirname(HERE)
SRC  = os.path.join(ROOT, "design-pack", "mp-dashboard", "project", "email")
DST  = os.path.join(HERE, "templates")
os.makedirs(DST, exist_ok=True)


def common_subs(s: str) -> str:
    """Substitutions applied to both Monday and Friday templates."""

    # Title tag
    s = s.replace("Week Ahead, Monday 18 May 2026", "{{ISSUE_DATE}}")
    s = s.replace("Week in Review, Friday 22 May 2026", "{{ISSUE_DATE}}")

    # Preview text (first visible line of body)
    s = re.sub(
        r"(<div style=\"display:none;[^>]+>\s*)[^<]+(\s*</div>)",
        r"\1{{PREVIEW_TEXT}}\2",
        s,
        count=1,
    )

    # Header date + issue number
    s = s.replace("Mon 18 May 2026 &middot; Issue 79", "{{ISSUE_DATE}} &middot; Issue {{ISSUE_NUMBER}}")
    s = s.replace("Fri 22 May 2026 &middot; Issue 80", "{{ISSUE_DATE}} &middot; Issue {{ISSUE_NUMBER}}")

    # Pulse strip — phase / summary / score / confidence
    s = s.replace(
        '<div style="font-size:26px;font-weight:600;letter-spacing:-0.015em;color:#ffffff;line-height:1.15;">Early Expansion</div>',
        '<div style="font-size:26px;font-weight:600;letter-spacing:-0.015em;color:#ffffff;line-height:1.15;">{{DIAL_PHASE}}</div>',
    )
    s = s.replace(
        "Risk on. Liquidity opening. Position size with discipline.",
        "{{DIAL_SUMMARY}}",
    )
    s = s.replace(
        '<div style="font-size:28px;font-weight:700;letter-spacing:-0.02em;color:#22c55e;line-height:1;">+3.0</div>',
        '<div style="font-size:28px;font-weight:700;letter-spacing:-0.02em;color:{{DIAL_SCORE_COLOR}};line-height:1;">{{DIAL_SCORE}}</div>',
    )
    s = s.replace(
        '<div style="font-size:28px;font-weight:700;letter-spacing:-0.02em;color:#22c55e;line-height:1;">+3.4</div>',
        '<div style="font-size:28px;font-weight:700;letter-spacing:-0.02em;color:{{DIAL_SCORE_COLOR}};line-height:1;">{{DIAL_SCORE}}</div>',
    )
    s = s.replace("Conf 68/100", "Conf {{DIAL_CONFIDENCE}}")
    s = s.replace("Conf 71/100", "Conf {{DIAL_CONFIDENCE}}")

    # Pulse pointer position — regex-based to handle Monday (304/306) AND Friday (321/323)
    s = re.sub(
        r'<rect x="\d+" y="4" width="8" height="48" rx="4" fill="#0a0a0a"/>',
        '<rect x="{{PULSE_HALO_X}}" y="4" width="8" height="48" rx="4" fill="#0a0a0a"/>',
        s,
    )
    s = re.sub(
        r'<rect x="\d+" y="6" width="4" height="44" rx="2" fill="#ffffff"/>',
        '<rect x="{{PULSE_BAR_X}}" y="6" width="4" height="44" rx="2" fill="#ffffff"/>',
        s,
    )

    # Pulse caption row — replace the whole row with a token. The 5 cells use varying
    # colors (white for the active one, muted for the others). We render them in Python.
    s = re.sub(
        r"<tr>\s*<td align=\"left\" width=\"20%\"[^>]+>Sell</td>.*?<td align=\"right\" width=\"20%\"[^>]+>Top</td>\s*</tr>",
        "{{PULSE_LABELS_ROW}}",
        s,
        count=1,
        flags=re.DOTALL,
    )

    return s


def monday_subs(s: str) -> str:
    s = common_subs(s)

    # Market snapshot — replace ALL 7 data rows with a single token.
    # The rows start after the header row and run to the closing </table>.
    s = re.sub(
        r"(border-bottom:1px solid rgba\(255,255,255,0\.1\);\">7d</td>\s*</tr>)\s*"
        r"(<tr>.*?Oil \(WTI\).*?</tr>)\s*(</table>)",
        r"\1\n{{SNAPSHOT_ROWS}}\n\3",
        s,
        count=1,
        flags=re.DOTALL,
    )

    # Week ahead calendar — replace all 5 day rows
    s = re.sub(
        r"(<tr>\s*<td valign=\"top\" width=\"72\" style=\"padding:14px 0;border-top:1px solid rgba\(255,255,255,0\.1\);\">\s*<div style=\"font-size:10px[^\"]+\">Mon</div>.*?Fri</div>.*?G7 Summit.*?</tr>)",
        "{{CALENDAR_ROWS}}",
        s,
        count=1,
        flags=re.DOTALL,
    )

    # Chart Spotlight 1
    s = s.replace(
        "BTC reclaims the 200-day &mdash; and the slope finally turns up",
        "{{SPOT1_TITLE}}",
    )
    s = re.sub(
        r"<svg width=\"100%\" height=\"210\"[^>]*aria-label=\"BTC price 30d\".*?</svg>",
        "{{SPOT1_CHART_SVG}}",
        s,
        count=1,
        flags=re.DOTALL,
    )
    s = s.replace(
        "Bitcoin closed the week above its 200&minus;day moving average for the fourth session running, with the moving average itself rolling positive for the first time since February. The 50d/200d spread is widening &mdash; the textbook condition for trend continuation.",
        "{{SPOT1_ANALYSIS}}",
    )

    # Chart Spotlight 2
    s = s.replace(
        "S&amp;P 500 grinds to fresh highs on narrowing breadth",
        "{{SPOT2_TITLE}}",
    )
    s = re.sub(
        r"<svg width=\"100%\" height=\"210\"[^>]*aria-label=\"SPX 30d\".*?</svg>",
        "{{SPOT2_CHART_SVG}}",
        s,
        count=1,
        flags=re.DOTALL,
    )
    s = s.replace(
        "Headline still strong &mdash; but only 38&percnt; of S&amp;P constituents are trading above their own 50&minus;day. When the index leads the average stock by this much, the next CPI print decides whether the laggards catch up or the leaders catch down.",
        "{{SPOT2_ANALYSIS}}",
    )

    # Feature article — eyebrow, headline, body
    s = s.replace(
        '<div style="font-family:Arial,Helvetica,sans-serif;font-size:11px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:#f97316;">This Week</div>',
        '<div style="font-family:Arial,Helvetica,sans-serif;font-size:11px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:#f97316;">{{FEATURE_EYEBROW}}</div>',
    )
    # Replace headline + all 3 paragraphs + pull-quote with a single token block
    s = re.sub(
        r"(<h1 class=\"h1-sm\"[^>]+>)\s*The week the Fed shows its hand\s*(</h1>)"
        r".*?"
        r"(<table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"margin-top:28px;\">)",
        r"\1{{FEATURE_HEADLINE}}\2\n{{FEATURE_BODY}}\n              \3",
        s,
        count=1,
        flags=re.DOTALL,
    )

    # CTA link
    s = s.replace(
        'href="https://www.macropulse.uk/this-week"',
        'href="{{FEATURE_CTA_URL}}"',
    )
    s = s.replace(
        "Read the full breakdown",
        "{{FEATURE_CTA_LABEL}}",
    )

    return s


def friday_subs(s: str) -> str:
    s = common_subs(s)

    # Header issue type
    s = s.replace("Week in Review</div>", "{{ISSUE_TYPE}}</div>", 1)
    # We don't actually template ISSUE_TYPE — it's already "Week in Review" hard in the file
    # but undoing — set it back:
    s = s.replace("{{ISSUE_TYPE}}", "Week in Review", 1)

    # Market snapshot rows — same pattern as Monday
    s = re.sub(
        r"(border-bottom:1px solid rgba\(255,255,255,0\.1\);\">7d</td>\s*</tr>)\s*"
        r"(<tr>.*?Oil \(WTI\).*?</tr>)\s*(</table>)",
        r"\1\n{{SNAPSHOT_ROWS}}\n\3",
        s,
        count=1,
        flags=re.DOTALL,
    )

    # Indicator pulse — 4 tiles, 2 rows. Replace the inner <tr>s with a token.
    s = re.sub(
        r"(<table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"margin-top:20px;font-family:Arial,Helvetica,sans-serif;\">\s*<!-- row 1 -->)"
        r".*?"
        r"(</table>\s*</td></tr>\s*</table>\s*</td></tr>\s*<!-- CHART SPOTLIGHT 1)",
        r"\1\n{{INDICATOR_TILES}}\n              </table>\n            </td></tr>\n          </table>\n        </td></tr>\n\n        \2",
        s,
        count=1,
        flags=re.DOTALL,
    )

    # Chart Spotlight 1
    s = s.replace(
        "BTC dominance breaks support &mdash; the rotation tell",
        "{{SPOT1_TITLE}}",
    )
    s = re.sub(
        r"<svg width=\"100%\" height=\"210\"[^>]*aria-label=\"BTC dominance 30d\".*?</svg>",
        "{{SPOT1_CHART_SVG}}",
        s,
        count=1,
        flags=re.DOTALL,
    )
    s = s.replace(
        "Dominance broke 52.4&percnt; cleanly on Wednesday and failed to reclaim it on Thursday&rsquo;s bounce attempt. Historically, a confirmed loss of this level precedes a 6&ndash;10 week window where ETH and large-cap alts outperform BTC by 12&ndash;18&percnt;. The setup is now live.",
        "{{SPOT1_ANALYSIS}}",
    )

    # Chart Spotlight 2
    s = s.replace(
        "TOTAL3 breaks out of an eight-week range",
        "{{SPOT2_TITLE}}",
    )
    s = re.sub(
        r"<svg width=\"100%\" height=\"210\"[^>]*aria-label=\"TOTAL3 30d\".*?</svg>",
        "{{SPOT2_CHART_SVG}}",
        s,
        count=1,
        flags=re.DOTALL,
    )
    s = s.replace(
        "Alts-ex-ETH market cap broke through &dollar;685B resistance on Tuesday and held the level as support on Friday. Combined with dominance breaking down, the rotation we&rsquo;ve been positioning for is here &mdash; not coming. The discipline now is staying with the names we already own.",
        "{{SPOT2_ANALYSIS}}",
    )

    # Portfolio rows — replace the 3 data rows
    s = re.sub(
        r"(border-bottom:1px solid rgba\(255,255,255,0\.1\);\">Since</td>\s*</tr>)\s*"
        r"(<tr>.*?DOGE.*?</tr>)\s*(</table>)",
        r"\1\n{{PORTFOLIO_ROWS}}\n              \3",
        s,
        count=1,
        flags=re.DOTALL,
    )

    # Allocation guidance card (inverted)
    s = s.replace("Stay weighted to held positions", "{{ALLOCATION_HEADLINE}}")
    s = s.replace(
        "No new entries this week. The book is positioned for the rotation already &mdash; let it work.",
        "{{ALLOCATION_BODY}}",
    )
    s = s.replace(
        '<div style="font-size:28px;font-weight:700;color:#0a0a0a;line-height:1;margin-top:8px;letter-spacing:-0.02em;">+8.4%</div>',
        '<div style="font-size:28px;font-weight:700;color:#0a0a0a;line-height:1;margin-top:8px;letter-spacing:-0.02em;">{{BOOK_PNL}}</div>',
    )

    # Feature article eyebrow & content
    s = s.replace(
        '<div style="font-family:Arial,Helvetica,sans-serif;font-size:11px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:#f97316;">Last Week</div>',
        '<div style="font-family:Arial,Helvetica,sans-serif;font-size:11px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;color:#f97316;">{{FEATURE_EYEBROW}}</div>',
    )
    s = re.sub(
        r"(<h1 class=\"h1-sm\"[^>]+>)\s*[^<]+\s*(</h1>)"
        r".*?"
        r"(<table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"margin-top:28px;\">)",
        r"\1{{FEATURE_HEADLINE}}\2\n{{FEATURE_BODY}}\n              \3",
        s,
        count=1,
        flags=re.DOTALL,
    )

    s = re.sub(r'href="https://www\.macropulse\.uk/last-week"', 'href="{{FEATURE_CTA_URL}}"', s)
    s = re.sub(r'href="https://www\.macropulse\.uk/[a-z\-]+"(?![^<>]*>(Framework|Dial|Newsletter|Glossary))', 'href="{{FEATURE_CTA_URL}}"', s, count=1)
    s = s.replace("Read the full review", "{{FEATURE_CTA_LABEL}}")
    s = s.replace("Read the full breakdown", "{{FEATURE_CTA_LABEL}}")

    return s


def main():
    # Monday
    with open(os.path.join(SRC, "monday-template.html"), encoding="utf-8") as f:
        mon = f.read()
    mon_out = monday_subs(mon)
    with open(os.path.join(DST, "monday.html"), "w", encoding="utf-8") as f:
        f.write(mon_out)
    print(f"[templates] wrote monday.html ({len(mon_out):,} chars)")

    # Friday
    with open(os.path.join(SRC, "friday-template.html"), encoding="utf-8") as f:
        fri = f.read()
    fri_out = friday_subs(fri)
    with open(os.path.join(DST, "friday.html"), "w", encoding="utf-8") as f:
        f.write(fri_out)
    print(f"[templates] wrote friday.html ({len(fri_out):,} chars)")

    # Quick sanity: list found placeholders
    import re as _re
    for name, content in [("monday", mon_out), ("friday", fri_out)]:
        tokens = sorted(set(_re.findall(r"\{\{[A-Z_0-9]+\}\}", content)))
        print(f"  {name} tokens: {tokens}")


if __name__ == "__main__":
    main()
