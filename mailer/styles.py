"""Shared CSS and HTML shell for MacroPulse email templates."""

EMAIL_CSS = """
  body { margin:0; padding:0; background-color:#081018; color:#e8eef2; font-family:Arial,Helvetica,sans-serif; }
  table { border-collapse:collapse; border-spacing:0; }
  img { border:0; display:block; line-height:100%; max-width:100%; outline:none; text-decoration:none; }

  .shell { width:100%; background: radial-gradient(circle at top left, rgba(255,157,47,0.12), transparent 28%),
           linear-gradient(180deg, #0a1a24 0%, #081018 100%); }
  .container { width:100%; max-width:600px; }
  .card { background-color:#101a24; border:1px solid #1e2e3e; border-radius:14px; }
  .section-card { background-color:#101a24; border:1px solid #1e2e3e; border-radius:14px; }

  .eyebrow { display:inline-block; padding:5px 12px; border:1px solid #2a3a4e; border-radius:999px;
             color:#d4a853; font-size:11px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; }
  .section-title { font-size:20px; font-weight:700; color:#e8eef2; margin:0 0 8px; }
  .section-copy { font-size:14px; line-height:1.6; color:#9db0bf; }
  .small-copy { font-size:12px; line-height:1.5; color:#6a8090; }
  .muted { color:#9db0bf; }

  .data-table { width:100%; border-collapse:collapse; font-size:13px; }
  .data-table th { background-color:#0d1f2d; color:#6a8090; font-size:11px; font-weight:600;
                   text-transform:uppercase; letter-spacing:0.06em; padding:8px 10px; text-align:left; }
  .data-table td { padding:9px 10px; border-top:1px solid #1e2e3e; color:#e8eef2; }
  .data-table tr:hover td { background-color:#0d1f2d; }

  .pill-green { display:inline-block; background-color:#122211; color:#4ade80;
                font-weight:700; padding:3px 9px; border-radius:5px; font-size:12px; }
  .pill-red   { display:inline-block; background-color:#2a1111; color:#f87171;
                font-weight:700; padding:3px 9px; border-radius:5px; font-size:12px; }
  .pill-neutral { display:inline-block; background-color:#1a2535; color:#9db0bf;
                  font-weight:700; padding:3px 9px; border-radius:5px; font-size:12px; }

  .callout { background-color:#0d1f2d; border:1px solid #1e2e3e; border-left:3px solid #d4a853;
             border-radius:8px; }

  .event-row-rate     { border-left:3px solid #f7931a; }
  .event-row-inflation { border-left:3px solid #4ade80; }
  .event-row-employment { border-left:3px solid #00b4d8; }
  .event-row-earnings  { border-left:3px solid #d4a853; }

  .footer-link { color:#4a7090; text-decoration:none; font-size:11px; }
"""

WORDMARK_SVG = """
<svg width="140" height="22" viewBox="0 0 140 22" xmlns="http://www.w3.org/2000/svg">
  <text x="0" y="17" font-family="Arial,Helvetica,sans-serif" font-size="18"
        font-weight="700" fill="#e8eef2" letter-spacing="-0.5">MacroPulse</text>
  <rect x="0" y="20" width="50" height="2" rx="1" fill="#d4a853"/>
</svg>
"""


def change_pill(pct: float) -> str:
    """Return a coloured HTML pill for a percentage change."""
    sign  = "+" if pct >= 0 else ""
    cls   = "pill-green" if pct >= 0 else "pill-red"
    return f'<span class="{cls}">{sign}{pct:.1f}%</span>'


def html_shell(content: str, subject: str = "MacroPulse") -> str:
    """Wrap content in the standard email outer shell."""
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{subject}</title>
  <style type="text/css">
{EMAIL_CSS}
  </style>
</head>
<body>
  <table class="shell" role="presentation" width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:20px 12px;">
        <table class="container" role="presentation" cellpadding="0" cellspacing="0">
{content}
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
