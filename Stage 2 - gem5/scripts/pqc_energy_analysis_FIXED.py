#!/usr/bin/env python3
"""
pqc_energy_analysis.py
======================
PQC Energy Prediction & Analysis — gem5 ARM Cortex-M4 Simulation
-----------------------------------------------------------------
Pipeline:
  1. Load data: parse real gem5 log (GEM5_RESULT/RESULT lines) OR
     fall back to the real measured data from your paper_dataset.
  2. Optionally expand with 100-run noise simulation (script 11).
  3. Feature engineering (structural + algorithm ID).
  4. Three ML experiments:
       A. Run-level 5-fold KFold CV
       B. Cross-algorithm GroupKFold
       C. Feature-set ablation (structural-only vs full)
  5. 8-page PDF report with dark-theme plots.

Usage
-----
  python pqc_energy_analysis.py                        # real built-in data
  python pqc_energy_analysis.py gem5_raw.log           # your gem5 output log
  python pqc_energy_analysis.py --output report.pdf
  python pqc_energy_analysis.py --no-expand            # skip 100-run expansion

gem5 config (your gem5_se_pqc.py / 06_run_gem5_all_ops.sh)
  CPU  : ARM Minor / AtomicSimpleCPU, 64 MHz
  Cache: L1d 32 KiB / L1i 32 KiB / L2 256 KiB
  Mem  : DDR3-1600 512 MB
  Power: 66 mW active (ARM Cortex-M4, 20 mA × 3.3 V)
"""

import sys, re, os, argparse, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
import seaborn as sns
from scipy import stats

from sklearn.model_selection import KFold, GroupKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, mean_absolute_percentage_error

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────
# 1. CONSTANTS  (from your scripts 07/08)
# ──────────────────────────────────────────────────────────────────
CLOCK_HZ    = 64_000_000          # 64 MHz
GEM5_FREQ   = 1_000_000_000_000   # gem5 ticks/sec (1 THz)
ACTIVE_UW   = 66_000              # 66 mW = 20mA × 3.3V

# IoT feasibility thresholds (from script 09)
IOT_THRESH = {'KEYGEN': 10_000, 'ENCAP': 100_000, 'DECAP': 100_000,
              'SIGN':   100_000, 'VERIFY': 100_000}

GEM5_CSV = os.environ.get('GEM5_CSV', '/home/user/gem5_results/paper_dataset_fixed.csv')

def load_gem5_csv(path):
    """Load real gem5 measurements from CSV."""
    import csv
    records = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append((
                row['algorithm'],
                row['operation'],
                int(float(row['instructions'])),
                float(row['time_us']),
                float(row['energy_mj']),
            ))
    print(f"[+] Loaded {len(records)} records from {path}")
    return records

META = {
    'Kyber512':    {'family':'Kyber',  'type':'KEM','sec':1,'lattice_dim':256,'uses_fpu':0,'pk':800,  'sk':1632, 'ct':768},
    'Kyber768':    {'family':'Kyber',  'type':'KEM','sec':3,'lattice_dim':256,'uses_fpu':0,'pk':1184, 'sk':2400, 'ct':1088},
    'Kyber1024':   {'family':'Kyber',  'type':'KEM','sec':5,'lattice_dim':256,'uses_fpu':0,'pk':1568, 'sk':3168, 'ct':1568},
    'ML-KEM-512':  {'family':'ML-KEM', 'type':'KEM','sec':1,'lattice_dim':256,'uses_fpu':0,'pk':800,  'sk':1632, 'ct':768},
    'ML-KEM-768':  {'family':'ML-KEM', 'type':'KEM','sec':3,'lattice_dim':256,'uses_fpu':0,'pk':1184, 'sk':2400, 'ct':1088},
    'ML-KEM-1024': {'family':'ML-KEM', 'type':'KEM','sec':5,'lattice_dim':256,'uses_fpu':0,'pk':1568, 'sk':3168, 'ct':1568},
    'ML-DSA-44':   {'family':'ML-DSA', 'type':'SIG','sec':2,'lattice_dim':256,'uses_fpu':0,'pk':1312, 'sk':2528, 'ct':2420},
    'ML-DSA-65':   {'family':'ML-DSA', 'type':'SIG','sec':3,'lattice_dim':256,'uses_fpu':0,'pk':1952, 'sk':4000, 'ct':3309},
    'ML-DSA-87':   {'family':'ML-DSA', 'type':'SIG','sec':5,'lattice_dim':256,'uses_fpu':0,'pk':2592, 'sk':4864, 'ct':4595},
    'Falcon-512':  {'family':'Falcon', 'type':'SIG','sec':1,'lattice_dim':512,'uses_fpu':1,'pk':897,  'sk':1281, 'ct':666},
    'Falcon-1024': {'family':'Falcon', 'type':'SIG','sec':5,'lattice_dim':1024,'uses_fpu':1,'pk':1793,'sk':2305, 'ct':1280},
}

# ──────────────────────────────────────────────────────────────────
# 3. PARSERS  (supports all three log formats from your scripts)
# ──────────────────────────────────────────────────────────────────
def parse_log(path):
    """
    Parse gem5 output log. Handles:
      - GEM5_RESULT algo=X op=Y ns=N     (v3 format)
      - GEM5_RESULT algo=X op=Y ticks=N  (v4 with ticks)
      - RESULT X Y cycles=N              (v1/v2 format)
    Returns list of (algo, op, instructions, time_us, energy_mj).
    """
    records = []
    pat_ns    = re.compile(r'GEM5_RESULT\s+algo=(\S+)\s+op=(\S+)\s+ns=(\d+)')
    pat_ticks = re.compile(r'GEM5_RESULT\s+algo=(\S+)\s+op=(\S+)\s+ticks=(\d+)')
    pat_cyc   = re.compile(r'RESULT\s+(\S+)\s+(\S+)\s+cycles=(\d+)')

    with open(path) as f:
        for line in f:
            m = pat_ns.search(line)
            if m:
                algo, op, ns = m.group(1), m.group(2), int(m.group(3))
                cycles  = ns * CLOCK_HZ / 1e9
                time_us = ns / 1000
                energy_mj = (time_us * ACTIVE_UW / 1e6) / 1000
                records.append((algo, op, int(cycles), time_us, energy_mj))
                continue
            m = pat_ticks.search(line)
            if m:
                algo, op, ticks = m.group(1), m.group(2), int(m.group(3))
                cycles  = ticks * CLOCK_HZ / GEM5_FREQ
                time_us = cycles / CLOCK_HZ * 1e6
                energy_mj = (time_us * ACTIVE_UW / 1e6) / 1000
                records.append((algo, op, int(cycles), time_us, energy_mj))
                continue
            m = pat_cyc.search(line)
            if m:
                algo, op, cyc = m.group(1), m.group(2), int(m.group(3))
                time_us = cyc / CLOCK_HZ * 1e6
                energy_mj = (time_us * ACTIVE_UW / 1e6) / 1000
                records.append((algo, op, cyc, time_us, energy_mj))
    return records

# ──────────────────────────────────────────────────────────────────
# 4. BUILD DATAFRAME
# ──────────────────────────────────────────────────────────────────
def build_df(records):
    rows = []
    for algo, op, insts, time_us, energy_mj in records:
        m = META.get(algo, {})
        op_norm = op.replace('ENCAP_SIGN','ENCAP').replace('DECAP_VERIFY','DECAP')
        thresh  = IOT_THRESH.get(op_norm, 10_000)
        rows.append({
            'algorithm':       algo,
            'operation':       op_norm,
            'family':          m.get('family', algo.split('-')[0]),
            'algo_type':       m.get('type', 'KEM' if 'KEM' in algo.upper() else 'SIG'),
            'security_level':  m.get('sec', 1),
            'lattice_dim':     m.get('lattice_dim', 256),
            'uses_fpu':        m.get('uses_fpu', 0),
            'pk_bytes':        m.get('pk', 0),
            'sk_bytes':        m.get('sk', 0),
            'ct_or_sig_bytes': m.get('ct', 0),
            'instructions':    insts,
            'time_us':         round(time_us, 2),
            'energy_mj':       round(energy_mj, 6),
            'iot_feasible':    int(time_us < thresh),
        })
    return pd.DataFrame(rows)

def expand_100runs(df, seed=42):
    """Simulate 100 measurement runs with ±3% noise (script 11 logic)."""
    np.random.seed(seed)
    rows = []
    for _, r in df.iterrows():
        for run in range(1, 101):
            noise = np.clip(np.random.normal(1.0, 0.03), 0.95, 1.10)
            row = r.to_dict()
            row['run']       = run
            row['time_us']   = round(r['time_us']   * noise, 2)
            row['energy_mj'] = round(r['energy_mj'] * noise, 6)
            rows.append(row)
    return pd.DataFrame(rows)

def encode_features(df):
    le_op  = LabelEncoder()
    le_alg = LabelEncoder()
    df = df.copy()
    df['op_enc']  = le_op.fit_transform(df['operation'])
    df['alg_enc'] = le_alg.fit_transform(df['algorithm'])
    df['log_energy'] = np.log1p(df['energy_mj'])
    return df, le_op, le_alg

FEAT_STRUCT = ['op_enc','security_level','lattice_dim','uses_fpu',
               'pk_bytes','sk_bytes','ct_or_sig_bytes']
FEAT_FULL   = FEAT_STRUCT + ['alg_enc']

# ──────────────────────────────────────────────────────────────────
# 5. DARK THEME
# ──────────────────────────────────────────────────────────────────
BG, AX, EDGE = "#0D1117", "#161B22", "#30363D"
TXT, SUBTEXT = "#E6EDF3", "#8B949E"
GOLD = "#FFD700"
CMAP_DIV = LinearSegmentedColormap.from_list("rdbl",["#D32F2F",BG,"#1976D2"])
CMAP_HOT  = LinearSegmentedColormap.from_list("hot2",[BG,"#1565C0","#F57F17","#FF3D00"])
FAM_COLORS = {"Kyber":"#2196F3","ML-KEM":"#03A9F4","ML-DSA":"#4CAF50",
              "Falcon":"#FF5722","SPHINCS+":"#9C27B0"}
OP_COLORS  = {"KEYGEN":"#4CAF50","ENCAP":"#2196F3","DECAP":"#03A9F4",
              "SIGN":"#FF9800","VERIFY":"#00BCD4"}
TYPE_COL   = {"KEM":"#2196F3","SIG":"#FF5722"}

def style():
    plt.rcParams.update({
        "figure.facecolor":BG,"axes.facecolor":AX,"axes.edgecolor":EDGE,
        "axes.labelcolor":TXT,"xtick.color":SUBTEXT,"ytick.color":SUBTEXT,
        "text.color":TXT,"grid.color":EDGE,"grid.linewidth":0.5,
        "font.family":"DejaVu Sans","font.size":9,
        "axes.titlesize":11,"axes.titleweight":"bold",
        "legend.facecolor":AX,"legend.edgecolor":EDGE,"legend.labelcolor":TXT,
    })

def watermark(fig):
    fig.text(0.99, 0.01, "gem5 ARM • 64 MHz • Cortex-M4 • liboqs",
             ha="right", va="bottom", fontsize=7, color=SUBTEXT, alpha=0.7)

# ──────────────────────────────────────────────────────────────────
# 6. PLOT PAGES
# ──────────────────────────────────────────────────────────────────

def page_overview(df_base, pdf):
    """Page 1 – raw measured data overview (33 real gem5 points)"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle("PQC Energy Usage — Real gem5 ARM Measurements\n"
                 "ARM Cortex-M4  |  64 MHz  |  66 mW active  |  liboqs", fontsize=13)

    # A – Grouped bar: energy_mj per algo, per op
    ax = axes[0,0]
    algos = df_base['algorithm'].unique().tolist()
    ops   = [o for o in ['KEYGEN','ENCAP','DECAP','SIGN','VERIFY']
             if o in df_base['operation'].values]
    x = np.arange(len(algos)); w = 0.15
    for i, op in enumerate(ops):
        vals = [df_base[(df_base.algorithm==a) & (df_base.operation==op)]['energy_mj'].values
                for a in algos]
        vals = [v[0] if len(v) else 0 for v in vals]
        ax.bar(x + i*w - w*len(ops)/2, vals, w, label=op,
               color=OP_COLORS.get(op,'#888'), alpha=0.87)
    ax.set_xticks(x); ax.set_xticklabels(algos, rotation=40, ha='right', fontsize=7)
    ax.set_ylabel('Energy (mJ)'); ax.set_yscale('log')
    ax.set_title('A — Energy per Algorithm & Operation')
    ax.legend(fontsize=7); ax.grid(axis='y', alpha=0.3)

    # B – Instructions vs Energy scatter, coloured by family
    ax = axes[0,1]
    for fam, grp in df_base.groupby('family'):
        ax.scatter(grp['instructions'], grp['energy_mj'],
                   color=FAM_COLORS.get(fam,'#aaa'), s=70, label=fam,
                   alpha=0.85, edgecolors='white', linewidths=0.3)
    # power-law fit
    lx = np.log10(df_base['instructions'])
    ly = np.log10(df_base['energy_mj'])
    sl, ic, r, *_ = stats.linregress(lx, ly)
    xs = np.linspace(lx.min(), lx.max(), 200)
    ax.plot(10**xs, 10**(sl*xs+ic), '--', color=GOLD, lw=1.5,
            label=f'Power-law fit\nR²={r**2:.3f}')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('Instructions'); ax.set_ylabel('Energy (mJ)')
    ax.set_title('B — Instructions vs Energy (log-log)')
    ax.legend(fontsize=7); ax.grid(alpha=0.3)

    # C – IoT feasibility (time_us thresholds from script 09)
    ax = axes[1,0]
    iot_yes = df_base[df_base.iot_feasible==1]
    iot_no  = df_base[df_base.iot_feasible==0]
    ax.scatter(iot_yes['time_us'], iot_yes['energy_mj'],
               color='#4CAF50', s=80, label='IoT Feasible', zorder=3,
               edgecolors='white', linewidths=0.3)
    ax.scatter(iot_no['time_us'],  iot_no['energy_mj'],
               color='#FF5722', s=80, marker='X', label='IoT Infeasible', zorder=3,
               edgecolors='white', linewidths=0.3)
    for _, r2 in df_base.iterrows():
        ax.annotate(f"{r2['algorithm']}\n{r2['operation']}",
                    (r2['time_us'], r2['energy_mj']),
                    fontsize=4.5, color=SUBTEXT, alpha=0.8,
                    xytext=(3,3), textcoords='offset points')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('Time (µs)'); ax.set_ylabel('Energy (mJ)')
    ax.set_title('C — IoT Feasibility Map\n'
                 '(KEYGEN <10ms, ops <100ms)')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # D – Energy by family box plot
    ax = axes[1,1]
    fams = list(FAM_COLORS.keys())
    data = [df_base[df_base.family==f]['energy_mj'].values for f in fams
            if f in df_base.family.values]
    fams_present = [f for f in fams if f in df_base.family.values]
    bp = ax.boxplot(data, labels=fams_present, patch_artist=True,
                    medianprops={'color':GOLD,'linewidth':2})
    for patch, fam in zip(bp['boxes'], fams_present):
        patch.set_facecolor(FAM_COLORS[fam]); patch.set_alpha(0.75)
    ax.set_ylabel('Energy (mJ)'); ax.set_yscale('log')
    ax.set_title('D — Energy Distribution by Algorithm Family')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout(rect=[0,0,1,0.95])
    watermark(fig)
    pdf.savefig(fig, facecolor=BG); plt.close(fig)


def page_energy_breakdown(df_base, pdf):
    """Page 2 – per-family energy breakdown + KEM vs SIG"""
    fig, axes = plt.subplots(1, 3, figsize=(16, 7))
    fig.suptitle("Energy Breakdown — KEM vs SIG Families", fontsize=13)

    # A – Stacked bar: total energy per family
    ax = axes[0]
    ops = ['KEYGEN','ENCAP','DECAP','SIGN','VERIFY']
    piv = (df_base.pivot_table(index='family', columns='operation',
                               values='energy_mj', aggfunc='sum').fillna(0))
    piv = piv[[c for c in ops if c in piv.columns]]
    bottom = np.zeros(len(piv))
    op_c = [OP_COLORS[o] for o in piv.columns]
    for col, color in zip(piv.columns, op_c):
        ax.bar(piv.index, piv[col], bottom=bottom, color=color,
               label=col, alpha=0.88)
        bottom += piv[col].values
    ax.set_ylabel('Total Energy (mJ)'); ax.set_yscale('log')
    ax.set_title('A — Total Energy by Family & Op')
    ax.legend(fontsize=8); ax.grid(axis='y', alpha=0.3)
    plt.setp(ax.get_xticklabels(), rotation=20, ha='right')

    # B – KEM vs SIG violin
    ax = axes[1]
    data_kem = np.log10(df_base[df_base.algo_type=='KEM']['energy_mj'])
    data_sig = np.log10(df_base[df_base.algo_type=='SIG']['energy_mj'])
    vp = ax.violinplot([data_kem, data_sig], positions=[0,1],
                       showmedians=True, showextrema=True)
    for body, col in zip(vp['bodies'], [TYPE_COL['KEM'], TYPE_COL['SIG']]):
        body.set_facecolor(col); body.set_alpha(0.7)
    vp['cmedians'].set_color(GOLD); vp['cmedians'].set_linewidth(2)
    ax.set_xticks([0,1]); ax.set_xticklabels(['KEM','SIG'])
    ax.set_ylabel('log₁₀(Energy mJ)')
    ax.set_title('B — KEM vs SIG Distribution')
    ax.grid(axis='y', alpha=0.3)

    # C – Energy efficiency: mJ per NIST security level
    ax = axes[2]
    eff = (df_base.groupby('algorithm')
                  .apply(lambda g: g['energy_mj'].sum() / g['security_level'].iloc[0])
                  .sort_values())
    colors_bar = [TYPE_COL.get(
        df_base[df_base.algorithm==a]['algo_type'].iloc[0],'#888')
        for a in eff.index]
    ax.barh(eff.index, eff.values, color=colors_bar, alpha=0.85)
    ax.set_xlabel('Total mJ / NIST Security Level')
    ax.set_title('C — Energy Efficiency\n(lower = better per security bit)')
    ax.legend(handles=[Patch(facecolor=TYPE_COL['KEM'],label='KEM'),
                       Patch(facecolor=TYPE_COL['SIG'],label='SIG')], fontsize=8)
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout(rect=[0,0,1,0.95])
    watermark(fig)
    pdf.savefig(fig, facecolor=BG); plt.close(fig)


def page_heatmaps(df_base, pdf):
    """Page 3 – energy heatmaps KEM | SIG"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle("Energy Heatmaps (mJ) — gem5 ARM Measurements", fontsize=13)

    for ax, atype in zip(axes, ['KEM','SIG']):
        sub = df_base[df_base.algo_type==atype]
        piv = sub.pivot_table(index='algorithm', columns='operation',
                              values='energy_mj', aggfunc='mean')
        sns.heatmap(piv, ax=ax, cmap=CMAP_HOT, annot=True, fmt='.4f',
                    linewidths=0.4, linecolor=EDGE,
                    annot_kws={'size':8.5},
                    cbar_kws={'label':'mJ'})
        ax.set_title(f'{atype} Algorithms', fontsize=11)
        ax.set_xlabel('Operation'); ax.set_ylabel('')
        ax.tick_params(axis='x', rotation=15, labelsize=8)
        ax.tick_params(axis='y', rotation=0,  labelsize=8)

    plt.tight_layout(rect=[0,0,1,0.95])
    watermark(fig)
    pdf.savefig(fig, facecolor=BG); plt.close(fig)


def page_iot_analysis(df_base, pdf):
    """Page 4 – IoT feasibility deep dive"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle("IoT Feasibility Analysis — ARM Cortex-M4 @ 64 MHz", fontsize=13)

    # A – Time heatmap (all ops)
    ax = axes[0,0]
    piv = df_base.pivot_table(index='algorithm', columns='operation',
                              values='time_us', aggfunc='mean').fillna(0)
    cmap_t = LinearSegmentedColormap.from_list("tmap",[BG,"#1B5E20","#F9A825","#B71C1C"])
    sns.heatmap(piv, ax=ax, cmap=cmap_t, annot=True, fmt='.0f',
                linewidths=0.3, linecolor=EDGE, annot_kws={'size':7},
                cbar_kws={'label':'µs'})
    ax.set_title('A — Execution Time (µs)')
    ax.tick_params(axis='y', labelsize=7.5)

    # B – IoT feasible count per algorithm
    ax = axes[0,1]
    iot_count = df_base.groupby('algorithm')['iot_feasible'].sum().sort_values()
    total_ops  = df_base.groupby('algorithm')['iot_feasible'].count()
    pct = (iot_count / total_ops * 100).reindex(iot_count.index)
    colors_b = ['#4CAF50' if p==100 else '#FF9800' if p>0 else '#FF5722'
                for p in pct.values]
    ax.barh(iot_count.index, iot_count.values, color=colors_b, alpha=0.88)
    for i, (v, p) in enumerate(zip(iot_count.values, pct.values)):
        ax.text(v+0.05, i, f'{p:.0f}%', va='center', fontsize=8)
    ax.set_xlabel('IoT-Feasible Operations (out of 3)')
    ax.set_title('B — IoT-Feasible Ops per Algorithm')
    ax.set_xlim(0, 4)
    ax.legend(handles=[Patch(facecolor='#4CAF50',label='All feasible'),
                       Patch(facecolor='#FF9800',label='Partial'),
                       Patch(facecolor='#FF5722',label='None')], fontsize=8)
    ax.grid(axis='x', alpha=0.3)

    # C – Energy cost for IoT-feasible ops only
    ax = axes[1,0]
    feasible = df_base[df_base.iot_feasible==1]
    for fam, grp in feasible.groupby('family'):
        ax.scatter(grp['time_us'], grp['energy_mj'],
                   color=FAM_COLORS.get(fam,'#aaa'), s=90, label=fam,
                   alpha=0.85, edgecolors='white', linewidths=0.3)
    for _, r2 in feasible.iterrows():
        ax.annotate(f"{r2['algorithm']}\n{r2['operation']}",
                    (r2['time_us'], r2['energy_mj']),
                    fontsize=5, color=SUBTEXT, alpha=0.9,
                    xytext=(3,3), textcoords='offset points')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('Time (µs)'); ax.set_ylabel('Energy (mJ)')
    ax.set_title('C — IoT-Feasible Operations Only')
    ax.legend(fontsize=7); ax.grid(alpha=0.3)

    # D – Security level vs feasibility
    ax = axes[1,1]
    for sec in sorted(df_base.security_level.unique()):
        sub = df_base[df_base.security_level==sec]
        n_yes = sub.iot_feasible.sum()
        n_no  = len(sub) - n_yes
        ax.bar(str(sec), n_yes, color='#4CAF50', alpha=0.85, label='Feasible' if sec==1 else '')
        ax.bar(str(sec), n_no,  bottom=n_yes, color='#FF5722', alpha=0.85, label='Infeasible' if sec==1 else '')
    ax.set_xlabel('NIST Security Level')
    ax.set_ylabel('Number of Operations')
    ax.set_title('D — IoT Feasibility by Security Level')
    ax.legend(fontsize=9); ax.grid(axis='y', alpha=0.3)

    plt.tight_layout(rect=[0,0,1,0.95])
    watermark(fig)
    pdf.savefig(fig, facecolor=BG); plt.close(fig)


def page_correlation(df_enc, pdf):
    """Page 5 – correlation + feature importance"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    fig.suptitle("Feature Correlation & Importance for Energy Prediction", fontsize=13)

    # A – Correlation matrix
    ax = axes[0]
    cols = ['instructions','time_us','energy_mj','security_level',
            'lattice_dim','pk_bytes','sk_bytes','ct_or_sig_bytes','uses_fpu']
    corr = df_enc[cols].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, ax=ax, cmap=CMAP_DIV, annot=True, fmt='.2f', mask=mask,
                vmin=-1, vmax=1, linewidths=0.4, linecolor=EDGE,
                annot_kws={'size':8})
    ax.set_title('A — Pearson Correlation Matrix')
    ax.tick_params(labelsize=8)

    # B – Feature importance
    ax = axes[1]
    rf = RandomForestRegressor(n_estimators=300, random_state=42)
    rf.fit(df_enc[FEAT_FULL], df_enc['log_energy'])
    imp = pd.Series(rf.feature_importances_, index=FEAT_FULL).sort_values()
    cols_imp = plt.cm.viridis(np.linspace(0.2, 0.9, len(imp)))
    ax.barh(imp.index, imp.values, color=cols_imp, alpha=0.9)
    for i, (v, n) in enumerate(zip(imp.values, imp.index)):
        ax.text(v+0.003, i, f'{v*100:.1f}%', va='center', fontsize=8)
    ax.set_xlabel('Feature Importance (Mean Decrease Impurity)')
    ax.set_title('B — Random Forest Feature Importance\n(predicting log energy)')
    ax.set_xlim(0, imp.max()*1.25)
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout(rect=[0,0,1,0.95])
    watermark(fig)
    pdf.savefig(fig, facecolor=BG); plt.close(fig)


def page_ml_models(df_enc, pdf, n_splits=5):
    """Page 6 – ML model comparison (Exp A: run-level KFold)"""
    n_rows = len(df_enc)
    dataset_note = (f"Training on 100-run expanded dataset ({n_rows} rows)"
                     if n_rows > 33 else
                     f"Training on base gem5 dataset ({n_rows} rows, no expansion)")
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle(f"ML Energy Prediction — {n_splits}-Fold Cross Validation\n"
                 f"{dataset_note}", fontsize=13)
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    models = {
        'Ridge':          Pipeline([('sc',StandardScaler()),('m',Ridge(alpha=10))]),
        'Random Forest':  RandomForestRegressor(n_estimators=300, random_state=42),
        'Grad. Boosting': GradientBoostingRegressor(n_estimators=300,
                                                    learning_rate=0.05,
                                                    max_depth=4, random_state=42),
    }
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    X, y = df_enc[FEAT_FULL], df_enc['log_energy']
    mc = ['#2196F3','#4CAF50','#FF5722']
    results = {}

    for name, mdl in models.items():
        r2s  = cross_val_score(mdl, X, y, cv=kf, scoring='r2')
        mape = cross_val_score(mdl, X, y, cv=kf,
                               scoring='neg_mean_absolute_percentage_error')
        results[name] = {'r2': r2s, 'mape': -mape*100}

    # A – R² bar
    ax = fig.add_subplot(gs[0,0])
    names = list(results.keys())
    r2m = [results[n]['r2'].mean() for n in names]
    r2s = [results[n]['r2'].std()  for n in names]
    bars = ax.bar(names, r2m, yerr=r2s, color=mc, alpha=0.87, capsize=7,
                  error_kw={'ecolor':GOLD,'linewidth':1.5})
    for b, v in zip(bars, r2m):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.005,
                f'{v:.4f}', ha='center', va='bottom', fontsize=9)
    ax.set_ylim(0,1.08); ax.set_ylabel('R²')
    ax.set_title('A — CV R² (5-fold)')
    ax.tick_params(axis='x', rotation=10); ax.grid(axis='y', alpha=0.4)

    # B – MAPE bar
    ax = fig.add_subplot(gs[0,1])
    mm = [results[n]['mape'].mean() for n in names]
    ms = [results[n]['mape'].std()  for n in names]
    bars = ax.bar(names, mm, yerr=ms, color=mc, alpha=0.87, capsize=7,
                  error_kw={'ecolor':GOLD,'linewidth':1.5})
    for b, v in zip(bars, mm):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.3,
                f'{v:.1f}%', ha='center', va='bottom', fontsize=9)
    ax.set_ylabel('MAPE (%)'); ax.set_title('B — CV MAPE (5-fold)')
    ax.tick_params(axis='x', rotation=10); ax.grid(axis='y', alpha=0.4)

    # C – Fold R² violin
    ax = fig.add_subplot(gs[0,2])
    vp = ax.violinplot([results[n]['r2'] for n in names],
                       positions=range(len(names)), showmedians=True)
    for body, col in zip(vp['bodies'], mc):
        body.set_facecolor(col); body.set_alpha(0.7)
    vp['cmedians'].set_color(GOLD); vp['cmedians'].set_linewidth(2)
    ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=10, fontsize=8)
    ax.set_ylabel('R²'); ax.set_title('C — Fold Score Distribution')
    ax.grid(axis='y', alpha=0.4)

    # D/E/F – Pred vs Actual per model
    for i, (name, mdl) in enumerate(models.items()):
        ax = fig.add_subplot(gs[1,i])
        mdl.fit(X, y)
        yp  = np.expm1(mdl.predict(X))
        yt  = np.expm1(y.values)
        r2  = r2_score(yt, yp)
        mpe = mean_absolute_percentage_error(yt, yp)*100
        ax.scatter(yt, yp, c=mc[i], s=6, alpha=0.4, edgecolors='none')
        lims = [min(yt.min(),yp.min())*0.85, max(yt.max(),yp.max())*1.15]
        ax.plot(lims, lims, '--', color=GOLD, lw=1.5, label='Perfect')
        ax.set_xscale('log'); ax.set_yscale('log')
        ax.set_xlim(lims); ax.set_ylim(lims)
        ax.set_xlabel('Actual (mJ)'); ax.set_ylabel('Predicted (mJ)')
        ax.set_title(f'{chr(68+i)} — {name}\nR²={r2:.4f}  MAPE={mpe:.2f}%')
        ax.legend(fontsize=7); ax.grid(alpha=0.3)

    watermark(fig)
    pdf.savefig(fig, facecolor=BG); plt.close(fig)
    return results


def page_group_kfold(df_enc, pdf):
    """Page 7 – Exp B: Cross-algorithm GroupKFold + ablation (script 12 logic)"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    fig.suptitle("Experiment B — Cross-Algorithm Generalisation (GroupKFold)\n"
                 "Tests whether model predicts unseen algorithms from structure alone",
                 fontsize=12)

    rf   = RandomForestRegressor(n_estimators=300, n_jobs=-1, random_state=42)
    kf   = KFold(n_splits=5, shuffle=True, random_state=42)
    gkf  = GroupKFold(n_splits=min(5, df_enc['algorithm'].nunique()))
    X, y, g = df_enc[FEAT_FULL], df_enc['log_energy'], df_enc['alg_enc']

    configs = [
        ('KFold\nStructural', FEAT_STRUCT, kf,  None),
        ('KFold\nFull',       FEAT_FULL,   kf,  None),
        ('GroupKFold\nStructural', FEAT_STRUCT, gkf, g),
        ('GroupKFold\nFull',       FEAT_FULL,   gkf, g),
    ]
    labels, r2_means, r2_stds = [], [], []
    all_folds = []
    for lbl, feats, cv, groups in configs:
        kw = {'groups': groups} if groups is not None else {}
        sc = cross_val_score(rf, df_enc[feats], y, cv=cv, scoring='r2', **kw)
        labels.append(lbl); r2_means.append(sc.mean()); r2_stds.append(sc.std())
        all_folds.append(sc)

    # A – grouped bars
    ax = axes[0]
    colors_ab = ['#2196F3','#03A9F4','#FF5722','#FF8A65']
    bars = ax.bar(labels, r2_means, yerr=r2_stds, color=colors_ab, alpha=0.85,
                  capsize=7, error_kw={'ecolor':GOLD,'linewidth':1.5})
    for b, v, s in zip(bars, r2_means, r2_stds):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+s+0.01,
                f'{v:.3f}', ha='center', va='bottom', fontsize=9)
    ax.axhline(0, color=SUBTEXT, lw=0.8, linestyle=':')
    ax.set_ylabel('Cross-Validated R²')
    ax.set_title('A — KFold vs GroupKFold\n(Structural vs Full features)')
    ax.set_ylim(min(0, min(r2_means)-0.15), 1.12)
    ax.grid(axis='y', alpha=0.4)

    # B – fold distributions
    ax = axes[1]
    vp = ax.violinplot(all_folds, positions=range(4), showmedians=True)
    for body, col in zip(vp['bodies'], colors_ab):
        body.set_facecolor(col); body.set_alpha(0.7)
    vp['cmedians'].set_color(GOLD); vp['cmedians'].set_linewidth(2)
    ax.set_xticks(range(4)); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel('R² per fold')
    ax.set_title('B — R² Fold Distribution\n(width = variance)')
    ax.axhline(0, color=SUBTEXT, lw=0.8, linestyle=':')
    ax.grid(axis='y', alpha=0.4)

    plt.tight_layout(rect=[0,0,1,0.94])
    watermark(fig)
    pdf.savefig(fig, facecolor=BG); plt.close(fig)


def page_summary(df_base, results, pdf):
    """Page 8 – paper-ready summary tables"""
    fig, axes = plt.subplots(1, 2, figsize=(17, 10))
    fig.suptitle("Summary — gem5 ARM Results & ML Model Performance", fontsize=13)

    # Table A – all measurements
    ax = axes[0]; ax.axis('off')
    tbl_data = []
    for _, r in df_base.sort_values(['algo_type','algorithm','operation']).iterrows():
        iot = '✓' if r['iot_feasible'] else '✗'
        tbl_data.append([r['algorithm'], r['operation'],
                         f"{r['instructions']:,}", f"{r['time_us']:.1f}",
                         f"{r['energy_mj']:.4f}", iot])
    tbl = ax.table(cellText=tbl_data,
                   colLabels=['Algorithm','Op','Instructions','Time (µs)','Energy (mJ)','IoT'],
                   cellLoc='center', loc='center')
    tbl.auto_set_font_size(False); tbl.set_fontsize(7)
    tbl.scale(1, 1.35)
    for (row,col), cell in tbl.get_celld().items():
        if row==0:
            cell.set_facecolor('#1565C0'); cell.set_text_props(color='white',fontweight='bold')
        else:
            txt = tbl_data[row-1][-1] if col==5 else ''
            if col==5:
                cell.set_facecolor('#1B5E20' if txt=='✓' else '#B71C1C')
                cell.set_text_props(color='white', fontweight='bold')
            else:
                cell.set_facecolor('#1A2332' if row%2==0 else AX)
        cell.set_edgecolor(EDGE)
    ax.set_title('A — All gem5 Measurements (33 rows)', pad=20)

    # Table B – model scores
    ax = axes[1]; ax.axis('off')
    ml_rows = []
    best = max(results, key=lambda n: results[n]['r2'].mean())
    for name, res in results.items():
        ml_rows.append([
            name,
            f"{res['r2'].mean():.4f}",
            f"± {res['r2'].std():.4f}",
            f"{res['mape'].mean():.2f}%",
            '★ Best' if name==best else '',
        ])
    tbl2 = ax.table(cellText=ml_rows,
                    colLabels=['Model','CV R² Mean','± Std','CV MAPE','Note'],
                    cellLoc='center', loc='upper center')
    tbl2.auto_set_font_size(False); tbl2.set_fontsize(10)
    tbl2.scale(1, 3)
    for (row,col), cell in tbl2.get_celld().items():
        if row==0:
            cell.set_facecolor('#1565C0'); cell.set_text_props(color='white',fontweight='bold')
        elif ml_rows[row-1][-1]=='★ Best':
            cell.set_facecolor('#1B5E20'); cell.set_text_props(color='white')
        else:
            cell.set_facecolor('#1A2332' if row%2==0 else AX)
        cell.set_edgecolor(EDGE)
    # IoT summary block
    ax.text(0.5, 0.42, 'IoT Feasibility Summary', transform=ax.transAxes,
            ha='center', fontsize=11, fontweight='bold', color=TXT)
    iot_lines = []
    for algo in df_base['algorithm'].unique():
        sub  = df_base[df_base.algorithm==algo]
        n    = sub.iot_feasible.sum()
        tot  = len(sub)
        flag = '✓' if n==tot else ('~' if n>0 else '✗')
        iot_lines.append(f"  {flag}  {algo:<14} {n}/{tot} ops feasible")
    ax.text(0.05, 0.38, '\n'.join(iot_lines), transform=ax.transAxes,
            fontsize=8.5, color=TXT, va='top', family='monospace')
    ax.set_title('B — ML Results & IoT Feasibility', pad=20)

    plt.tight_layout(rect=[0,0,1,0.95])
    watermark(fig)
    pdf.savefig(fig, facecolor=BG); plt.close(fig)

# ──────────────────────────────────────────────────────────────────
# 7. MAIN
# ──────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description='PQC Energy Analysis')
    ap.add_argument('input', nargs='?', default=None,
                    help='gem5 output log (default: built-in real data)')
    ap.add_argument('--output', default='pqc_energy_report.pdf')
    ap.add_argument('--no-expand', action='store_true',
                    help='Skip 100-run dataset expansion (use 33 base rows only)')
    args = ap.parse_args()

    print('=' * 62)
    print('  PQC Energy Prediction & Analysis')
    print('  gem5 ARM  |  64 MHz  |  Cortex-M4  |  66 mW  |  liboqs')
    print('=' * 62)

    if args.input:
        print(f'\n[+] Parsing: {args.input}')
        records = parse_log(args.input)
        if not records:
            print('ERROR: no RESULT / GEM5_RESULT lines found. Check log format.')
            sys.exit(1)
        print(f'    Parsed {len(records)} records.')
    else:
        print(f'\n[+] Loading real gem5 data from {GEM5_CSV}')
        records = load_gem5_csv(GEM5_CSV)

    df_base = build_df(records)
    print(f'\n[+] Base dataset: {len(df_base)} rows, '
          f'{df_base.algorithm.nunique()} algorithms\n')

    print(f"{'Algorithm':<14} {'Op':<8} {'Instructions':>14} {'Time(µs)':>12} "
          f"{'Energy(mJ)':>11} {'IoT':>4}")
    print('-' * 67)
    for _, r in df_base.iterrows():
        print(f"{r['algorithm']:<14} {r['operation']:<8} "
              f"{r['instructions']:>14,} {r['time_us']:>12.1f} "
              f"{r['energy_mj']:>11.6f}  {'✓' if r['iot_feasible'] else '✗'}")

    if args.no_expand:
        df_ml = df_base.copy()
        print(f'\n[+] Using base dataset for ML ({len(df_ml)} rows)')
    else:
        df_ml = expand_100runs(df_base)
        print(f'\n[+] Expanded to 100-run dataset: {len(df_ml)} rows '
              f'(±3% measurement noise)')

    df_enc, le_op, le_alg = encode_features(df_ml)

    style()
    print(f'\n[+] Generating PDF → {args.output}')

    with PdfPages(args.output) as pdf:
        info = pdf.infodict()
        info['Title']   = 'PQC Energy Usage Prediction — gem5 ARM'
        info['Subject'] = 'Post-Quantum Cryptography ARM Simulation + ML Analysis'

        page_overview(df_base, pdf);         print('    ✓ Page 1 — Real gem5 Measurements Overview')
        page_energy_breakdown(df_base, pdf); print('    ✓ Page 2 — Energy Breakdown KEM vs SIG')
        page_heatmaps(df_base, pdf);         print('    ✓ Page 3 — Energy Heatmaps')
        page_iot_analysis(df_base, pdf);     print('    ✓ Page 4 — IoT Feasibility Analysis')
        page_correlation(df_enc, pdf);       print('    ✓ Page 5 — Correlation & Feature Importance')
        results = page_ml_models(df_enc, pdf); print('    ✓ Page 6 — ML Model Comparison (Exp A)')
        page_group_kfold(df_enc, pdf);       print('    ✓ Page 7 — Cross-Algorithm GroupKFold (Exp B)')
        page_summary(df_base, results, pdf); print('    ✓ Page 8 — Summary Tables')

    print(f'\n[✓] Done → {args.output}')
    best = max(results, key=lambda n: results[n]['r2'].mean())
    print(f'\n[★] Best model : {best}')
    print(f'    CV R²      = {results[best]["r2"].mean():.4f} ± {results[best]["r2"].std():.4f}')
    print(f'    CV MAPE    = {results[best]["mape"].mean():.2f}%')
    iot_ok = df_base[df_base.iot_feasible==1]['algorithm'].value_counts()
    print(f'\n[★] Most IoT-compatible: {iot_ok.idxmax()} ({iot_ok.max()}/3 ops feasible)')
    worst = df_base.sort_values('energy_mj', ascending=False).iloc[0]
    print(f'[★] Highest energy op : {worst["algorithm"]} {worst["operation"]} = {worst["energy_mj"]:.4f} mJ')

    # ── Canonical, reproducible result exports ──────────────────────
    # These two files are the single source of truth for the paper's
    # Table X/XI (final_results.csv) and Table XII (feature_importance_final.csv).
    # Every value here is derived from THIS run, THIS dataset, THIS git-free
    # script, with fixed random_state=42 throughout — reproducible on rerun.
    import datetime
    run_id = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir = os.path.dirname(args.output) or '.'

    rows_ml = []
    for name, res in results.items():
        rows_ml.append({
            'exp':            f'A_{5}fold_cv_{name.replace(" ",  "").replace(".", "")}',
            'model':          name,
            'cv_r2_mean':     round(res['r2'].mean(), 4),
            'cv_r2_std':      round(res['r2'].std(), 4),
            'cv_mape_pct':    round(res['mape'].mean(), 2),
            'n_rows':         len(df_enc),
            'n_algorithms':   df_enc['algorithm'].nunique(),
            'expanded':       not args.no_expand,
            'run_id':         run_id,
        })
    pd.DataFrame(rows_ml).to_csv(os.path.join(out_dir, 'final_results.csv'), index=False)
    print(f'\n[+] Canonical ML results  → {os.path.join(out_dir, "final_results.csv")}')

    rf_imp = RandomForestRegressor(n_estimators=300, random_state=42)
    rf_imp.fit(df_enc[FEAT_FULL], df_enc['log_energy'])
    imp_df = (pd.Series(rf_imp.feature_importances_, index=FEAT_FULL)
                .sort_values(ascending=False)
                .rename('importance').reset_index().rename(columns={'index':'feature'}))
    imp_df['run_id'] = run_id
    imp_df.to_csv(os.path.join(out_dir, 'feature_importance_final.csv'), index=False)
    print(f'[+] Canonical feature importance → {os.path.join(out_dir, "feature_importance_final.csv")}')
    print(f'[+] Run ID (cite this in the paper/methods section): {run_id}')

if __name__ == '__main__':
    main()

"""
root@debian:/home/user/scripts# python3 /home/user/scripts/pqc_energy_analysis.py \
    --no-expand \
    --output /home/user/gem5_results/pqc_report.pdf
python3: can't open file '/home/user/scripts/pqc_energy_analysis.py': [Errno 2] No such file or directory
root@debian:/home/user/scripts# python3 /home/user/scripts/pqc_energy_analysis-2.py     --no-expand     --output /home/user/gem5_results/pqc_report.pdf
==============================================================
  PQC Energy Prediction & Analysis
  gem5 ARM  |  64 MHz  |  Cortex-M4  |  66 mW  |  liboqs
==============================================================

[+] Loading real gem5 data from /home/user/gem5_results/paper_dataset_fixed.csv
[+] Loaded 33 records from /home/user/gem5_results/paper_dataset_fixed.csv

[+] Base dataset: 33 rows, 11 algorithms

Algorithm      Op         Instructions     Time(µs)  Energy(mJ)  IoT
-------------------------------------------------------------------
Kyber512       KEYGEN        1,004,680        526.2    0.034732  ✓
Kyber512       ENCAP         1,125,732        596.2    0.039348  ✓
Kyber512       DECAP         1,230,556        657.9    0.043418  ✓
Kyber768       KEYGEN        1,058,582        557.9    0.036821  ✓
Kyber768       ENCAP         1,251,368        669.3    0.044174  ✓
Kyber768       DECAP         1,420,996        768.9    0.050745  ✓
Kyber1024      KEYGEN        1,131,129        601.4    0.039695  ✓
Kyber1024      ENCAP         1,411,418        764.4    0.050448  ✓
Kyber1024      DECAP         1,666,035        914.1    0.060329  ✓
ML-KEM-512     KEYGEN        1,046,730        546.8    0.036089  ✓
ML-KEM-512     ENCAP         1,187,481        624.9    0.041243  ✓
ML-KEM-512     DECAP         1,358,552        719.7    0.047498  ✓
ML-KEM-768     KEYGEN        1,109,614        582.2    0.038425  ✓
ML-KEM-768     ENCAP         1,311,387        694.5    0.045838  ✓
ML-KEM-768     DECAP         1,556,727        830.8    0.054830  ✓
ML-KEM-1024    KEYGEN        1,209,103        637.6    0.042082  ✓
ML-KEM-1024    ENCAP         1,517,961        809.4    0.053420  ✓
ML-KEM-1024    DECAP         1,888,189       1014.7    0.066969  ✓
ML-DSA-44      KEYGEN        1,383,960        734.6    0.048484  ✓
ML-DSA-44      SIGN          2,276,270       1234.3    0.081464  ✓
ML-DSA-44      VERIFY        2,717,016       1479.0    0.097614  ✓
ML-DSA-65      KEYGEN        1,729,955        926.5    0.061150  ✓
ML-DSA-65      SIGN          2,633,678       1429.6    0.094355  ✓
ML-DSA-65      VERIFY        3,385,397       1846.1    0.121844  ✓
ML-DSA-87      KEYGEN        2,311,900       1249.5    0.082468  ✓
ML-DSA-87      SIGN          4,125,784       2257.7    0.149008  ✓
ML-DSA-87      VERIFY        5,437,585       2984.4    0.196968  ✓
Falcon-512     KEYGEN       39,296,848      20017.4    1.321147  ✗
Falcon-512     SIGN         40,755,364      20895.4    1.379095  ✓
Falcon-512     VERIFY       41,104,846      21083.7    1.391526  ✓
Falcon-1024    KEYGEN      124,847,496      63625.1    4.199255  ✗
Falcon-1024    SIGN        127,775,399      65404.3    4.316686  ✓
Falcon-1024    VERIFY      128,457,057      65770.1    4.340830  ✓

[+] Using base dataset for ML (33 rows)

[+] Generating PDF → /home/user/gem5_results/pqc_report.pdf
    ✓ Page 1 — Real gem5 Measurements Overview
    ✓ Page 2 — Energy Breakdown KEM vs SIG
    ✓ Page 3 — Energy Heatmaps
    ✓ Page 4 — IoT Feasibility Analysis
    ✓ Page 5 — Correlation & Feature Importance
    ✓ Page 6 — ML Model Comparison (Exp A)
    ✓ Page 7 — Cross-Algorithm GroupKFold (Exp B)
    ✓ Page 8 — Summary Tables

[✓] Done → /home/user/gem5_results/pqc_report.pdf

[★] Best model : Grad. Boosting
    CV R²      = 0.9858 ± 0.0268
    CV MAPE    = 6.69%

[★] Most IoT-compatible: Kyber512 (3/3 ops feasible)
[★] Highest energy op : Falcon-1024 VERIFY = 4.3408 mJ
root@debian:/home/user/scripts# 


"""