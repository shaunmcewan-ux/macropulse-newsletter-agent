"""
One-off generator for the "Corporate Bitcoin Treasuries" spotlight chart.
Renders a horizontal bar chart (log scale, BTC held) coloured by this
quarter's accumulation behaviour, matching the email's dark card palette.

Run: python charts/render_btc_treasury.py
Output: drafts/charts/btctreasury.png
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BG_CARD = "#111a23"
INK     = "#edf3f7"
INK_2   = "#b9c4cc"
INK_3   = "#7c8a95"
LINE    = "#1c2935"

GREEN  = "#4ec38a"   # net accumulator this quarter
GRAY   = "#7c8a95"   # broadly flat
RED    = "#ef5a6b"   # net seller this quarter

# (label, BTC held, colour)
HOLDERS = [
    ("Strategy (MSTR)",   845256, GREEN),
    ("Metaplanet (3350)",  40177, GREEN),
    ("Marathon (MARA)",    38689, RED),
    ("Galaxy Digital",     17000, GRAY),
    ("Riot Platforms",     15680, RED),
    ("Coinbase",           14500, GRAY),
    ("Hut 8",              14000, GRAY),
    ("CleanSpark",         13000, GRAY),
    ("Tesla",              11500, GRAY),
]

ROOT = os.path.dirname(os.path.dirname(__file__))
OUT  = os.path.join(ROOT, "drafts", "charts", "btctreasury.png")

width, height, dpi = 560, 280, 100
fig, ax = plt.subplots(figsize=(width / dpi, height / dpi), dpi=dpi)
fig.patch.set_facecolor(BG_CARD)
ax.set_facecolor(BG_CARD)

labels = [h[0] for h in HOLDERS][::-1]
values = [h[1] for h in HOLDERS][::-1]
colors = [h[2] for h in HOLDERS][::-1]

bars = ax.barh(labels, values, color=colors, height=0.6, log=True)

for bar, val in zip(bars, values):
    ax.text(
        bar.get_width() * 1.15, bar.get_y() + bar.get_height() / 2,
        f"{val:,.0f}", va="center", ha="left",
        color=INK, fontsize=8.5, fontweight="600",
    )

ax.set_xlim(8_000, 2_000_000)
ax.set_xscale("log")
ax.tick_params(colors=INK_3, labelsize=8.5)
ax.tick_params(axis="y", colors=INK_2, labelsize=9)
for spine in ax.spines.values():
    spine.set_color(LINE)
    spine.set_linewidth(0.8)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.set_xticks([])
ax.grid(False)

ax.set_title(
    "Corporate BTC treasuries (log scale)",
    color=INK, fontsize=11, fontweight="600", loc="left", pad=10,
)

# legend
legend_handles = [
    plt.Rectangle((0, 0), 1, 1, color=GREEN, label="Accumulating (2026)"),
    plt.Rectangle((0, 0), 1, 1, color=GRAY,  label="Broadly flat"),
    plt.Rectangle((0, 0), 1, 1, color=RED,   label="Trimming (Q1 2026)"),
]
ax.legend(
    handles=legend_handles, loc="lower right", frameon=False,
    fontsize=8, labelcolor=INK_2, ncol=1,
)

fig.tight_layout(pad=1.2)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, format="png", facecolor=BG_CARD, dpi=dpi)
plt.close(fig)
print(f"Saved {OUT}")
