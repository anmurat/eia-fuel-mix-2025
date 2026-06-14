import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ---- SETTINGS ----
DATA_DIR = "eia_Data/"

files = {
    'CAISO': 'CISO.xlsx',
    'ERCOT': 'ERCO.xlsx',
    'ISONE': 'ISNE.xlsx',
    'MISO':  'MISO.xlsx',
    'NYISO': 'NYIS.xlsx',
    'PJM':   'PJM.xlsx',
    'SPP':   'SWPP.xlsx',
}

FUEL_COLS = {
    'Coal':        'NG: COL',
    'Natural Gas': 'NG: NG',
    'Nuclear':     'NG: NUC',
    'Wind':        'NG: WND',
    'Solar':       'NG: SUN',
    'Hydro':       'NG: WAT',
    'Other':       'NG: OTH',
}

YEAR = 2025

COLORS = {
    'Coal':        '#5a5a6e',
    'Natural Gas': '#e07b39',
    'Nuclear':     '#9b59b6',
    'Wind':        '#27ae8f',
    'Solar':       '#f0c419',
    'Hydro':       '#2980b9',
    'Other':       '#3a3a4a',
}

SHORT = {
    'Coal': 'Coal', 'Natural Gas': 'Gas', 'Nuclear': 'Nuclear',
    'Wind': 'Wind', 'Solar': 'Solar', 'Hydro': 'Hydro', 'Other': 'Other'
}

BG      = '#0d1117'
CARD_BG = '#161b22'
TEXT    = '#ffffff'
MUTED   = '#adbac7'
ACCENT  = '#27ae8f'

# ---- LOAD DATA ----
print("Loading data...")
records = []
for iso, fname in files.items():
    print(f"  {iso}...")
    df = pd.read_excel(DATA_DIR + fname)
    df['UTC time'] = pd.to_datetime(df['UTC time'])
    df = df[df['UTC time'].dt.year == YEAR]
    row = {'ISO': iso}
    for fuel, col in FUEL_COLS.items():
        row[fuel] = pd.to_numeric(df[col], errors='coerce').fillna(0).sum() if col in df.columns else 0
    records.append(row)

agg     = pd.DataFrame(records).set_index('ISO')
agg_pct = agg.div(agg.sum(axis=1), axis=0) * 100
sources = list(FUEL_COLS.keys())
isos    = list(files.keys())

# ---- FIGURE ----
fig = plt.figure(figsize=(12, 13), facecolor=BG)

ax_title  = fig.add_axes([0.0,  0.84, 1.0,  0.14])
ax_chart  = fig.add_axes([0.16, 0.18, 0.80, 0.64])
ax_footer = fig.add_axes([0.0,  0.00, 1.0,  0.16])

for ax in [ax_title, ax_footer]:
    ax.axis('off')
    ax.set_facecolor(BG)

# ---- TITLE ----
ax_title.set_facecolor(BG)
ax_title.text(0.06, 0.85, 'U.S. Power Grid: Fuel Mix by Region',
              fontsize=22, fontweight='bold', color=TEXT,
              va='top', transform=ax_title.transAxes)
ax_title.text(0.06, 0.38, '2025 full-year generation  ·  7 balancing authorities',
              fontsize=11, color=MUTED,
              va='top', transform=ax_title.transAxes)
ax_title.text(0.94, 0.85, '2025',
              fontsize=32, fontweight='bold', color=ACCENT,
              va='top', ha='right', transform=ax_title.transAxes, alpha=0.3)

# ---- CHART ----
ax_chart.set_facecolor(CARD_BG)
ax_chart.set_xlim(0, 100)

row_height = 2.0
ax_chart.set_ylim(-0.5, len(isos) * row_height - 0.5)

for x in [25, 50, 75]:
    ax_chart.axvline(x, color='#21262d', linewidth=0.8, zorder=0)

for i, iso in enumerate(isos):
    y_bar = (len(isos) - 1 - i) * row_height + 0.7
    y_sub = y_bar - 0.85

    pct = agg_pct.loc[iso]
    dominant = pct.idxmax()

    left = 0
    seg_positions = {}

    for src in sources:
        val = pct[src]
        if val > 0.1:
            ax_chart.barh(y_bar, val, left=left,
                          color=COLORS[src], height=0.55,
                          alpha=1.0 if src == dominant else 0.75,
                          zorder=2)
            if val > 8:
                ax_chart.text(left + val/2, y_bar, f'{val:.0f}%',
                              ha='center', va='center',
                              fontsize=8.5, fontweight='bold',
                              color='white', zorder=3)
            seg_positions[src] = left
            left += val

    ax_chart.text(-2, y_bar, iso,
                  ha='right', va='center',
                  fontsize=12, fontweight='bold', color=TEXT)

    active_fuels = [(src, pct[src]) for src in sources if pct[src] >= 1]
    n = len(active_fuels)
    if n > 0:
        if n == 1:
            positions = [0]
        else:
            positions = [j * (100 / (n - 1)) for j in range(n)]
        for j, (src, val) in enumerate(active_fuels):
            x_pos = positions[j]
            if j == 0:
                ha = 'left'
            elif j == n - 1:
                ha = 'right'
            else:
                ha = 'center'
            dot_x = x_pos + (2.5 if j == 0 else (-2.5 if j == n - 1 else 0))
            ax_chart.plot(dot_x, y_sub, 'o',
                          color=COLORS[src], markersize=4, zorder=3)
            ax_chart.text(x_pos, y_sub - 0.08,
                          f'{SHORT[src]} {val:.0f}%',
                          va='top', ha=ha, fontsize=7.5, color='#d0d7de', zorder=3)

# Axis
ax_chart.set_yticks([])
ax_chart.set_xticks([0, 25, 50, 75, 100])
ax_chart.set_xticklabels(['0%', '25%', '50%', '75%', '100%'],
                          fontsize=9, color=MUTED)
ax_chart.tick_params(axis='x', colors=MUTED, length=0)
for spine in ax_chart.spines.values():
    spine.set_edgecolor('#21262d')
    spine.set_linewidth(0.8)

# ---- LEGEND ----
handles = [mpatches.Patch(facecolor=COLORS[s], label=s) for s in sources]
fig.legend(
    handles, sources,
    loc='lower center',
    bbox_to_anchor=(0.5, 0.08),
    ncol=7,
    frameon=False,
    fontsize=10,
    labelcolor=MUTED,
    handlelength=1.4,
    handleheight=1.0,
    handletextpad=0.6,
    columnspacing=1.2,
)

# ---- FOOTER ----
ax_footer.set_facecolor(BG)
ax_footer.axhline(0.80, color='#21262d', linewidth=0.8, xmin=0.04, xmax=0.96)
ax_footer.text(0.06, 0.40,
               'Source: U.S. Energy Information Administration (EIA-930 Hourly Grid Monitor)',
               fontsize=8.5, color=MUTED, va='center',
               transform=ax_footer.transAxes)
ax_footer.text(0.94, 0.40,
               'Data processed with Python  ·  Preliminary 2025 data',
               fontsize=8.5, color=MUTED, va='center', ha='right',
               transform=ax_footer.transAxes)

out = 'iso_fuel_mix_2025.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
print(f"Saved: {out}")