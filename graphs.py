import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np

plt.rcParams.update({
    "font.family":       "serif",
    "font.serif":        ["Times New Roman", "Times", "DejaVu Serif"],
    "axes.titlesize":    9,
    "axes.labelsize":    8,
    "xtick.labelsize":   7.5,
    "ytick.labelsize":   7.5,
    "legend.fontsize":   7,
    "figure.dpi":        300,
    "savefig.dpi":       300,
    "axes.linewidth":    0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.direction":   "in",
    "ytick.direction":   "in",
    "axes.grid":         True,
    "grid.linestyle":    "--",
    "grid.linewidth":    0.4,
    "grid.alpha":        0.5,
    "legend.framealpha": 0.9,
    "legend.edgecolor":  "#999999",
    "legend.borderpad":  0.4,
})

# ── Fig 16: Disease Detection (Grouped Bar Chart) ─────────────────────────────
diseases = ["Heart Disease", "Diabetes", "Kidney Disease", "Respiratory\nDisease"]
metrics  = ["Accuracy", "Precision", "Recall", "F1-Score"]
data = np.array([
    [96.1, 95.2, 96.8, 96.0],
    [93.8, 93.0, 94.1, 93.5],
    [91.7, 90.8, 92.5, 91.6],
    [92.4, 91.6, 93.1, 92.3],
])
colours16 = ["#1f4e79", "#2e86ab", "#5cb8e4", "#a8d8ea"]

fig16, ax16 = plt.subplots(figsize=(5.0, 3.2))
fig16.patch.set_facecolor("white")
ax16.set_facecolor("white")

x      = np.arange(len(diseases))
bar_w  = 0.18
offsets = np.linspace(-(len(metrics)-1)/2, (len(metrics)-1)/2, len(metrics)) * bar_w

for i, (metric, colour, offset) in enumerate(zip(metrics, colours16, offsets)):
    bars = ax16.bar(x + offset, data[:, i], width=bar_w,
                    color=colour, edgecolor="white", linewidth=0.5,
                    label=metric, zorder=3)
    for bar, val in zip(bars, data[:, i]):
        ax16.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.12,
                  f"{val:.1f}", ha="center", va="bottom",
                  fontsize=5.5, color="#222222", rotation=90)

ax16.set_xticks(x)
ax16.set_xticklabels(diseases, fontsize=7)
ax16.set_ylabel("Performance Score (%)")
ax16.set_xlabel("Disease Category")
ax16.set_title("Fig. 16. Disease Detection Module Performance\nAcross Four Disease Classes",
               fontsize=8, pad=6, loc="left")
ax16.set_ylim(85, 100)
ax16.yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(2))
ax16.legend(loc="lower right", ncol=2, handlelength=1.2, handleheight=0.8)
ax16.spines["top"].set_visible(False)
ax16.spines["right"].set_visible(False)
fig16.tight_layout(pad=0.6)
fig16.savefig("fig16_disease_detection.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig16)
print("✓ fig16_disease_detection.png saved")

# ── Fig 17: NLP Pipeline Metrics (Horizontal Bar Chart) ──────────────────────
nlp_labels = ["NER F1-Score", "Concept Normalization\nAccuracy", "Negation Resolution\nAccuracy"]
nlp_vals   = [91.2, 88.6, 93.4]
colours17  = ["#1a5276", "#2471a3", "#76b4d4"]

fig17, ax17 = plt.subplots(figsize=(4.5, 2.6))
fig17.patch.set_facecolor("white")
ax17.set_facecolor("white")

y_pos  = np.arange(len(nlp_labels))
bars17 = ax17.barh(y_pos, nlp_vals, height=0.45,
                   color=colours17, edgecolor="white", linewidth=0.5, zorder=3)

for bar, val in zip(bars17, nlp_vals):
    ax17.text(val + 0.3, bar.get_y() + bar.get_height()/2,
              f"{val:.1f}%", va="center", ha="left",
              fontsize=7.5, fontweight="bold", color="#1a3a5c")

ax17.set_yticks(y_pos)
ax17.set_yticklabels(nlp_labels, fontsize=7.5)
ax17.set_xlabel("Score (%)")
ax17.set_xlim(80, 100)
ax17.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(2))
ax17.set_title("Fig. 17. Symptom Analysis and NLP\nPipeline Performance Metrics",
               fontsize=8, pad=6, loc="left")
ax17.axvline(x=90, color="#aaaaaa", linewidth=0.6, linestyle=":", zorder=2)
ax17.text(90.2, -0.6, "90%", fontsize=6, color="#888888", va="top")
ax17.spines["top"].set_visible(False)
ax17.spines["right"].set_visible(False)
ax17.invert_yaxis()
fig17.tight_layout(pad=0.6)
fig17.savefig("fig17_nlp_metrics.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig17)
print("✓ fig17_nlp_metrics.png saved")

# ── Fig 18: Response Latency (Bar Chart) ─────────────────────────────────────
modules  = ["Disease\nDetection", "Symptom\nEngine", "AI Doctor",
            "Emergency\nAI", "Hospital\nLocator", "PDF\nReports"]
latency  = [145, 142, 310, 178, 194, 2300]
colours18 = ["#1f4e79", "#2e86ab", "#c0392b", "#e67e22", "#27ae60", "#8e44ad"]

fig18, ax18 = plt.subplots(figsize=(5.2, 3.1))
fig18.patch.set_facecolor("white")
ax18.set_facecolor("white")

x18    = np.arange(len(modules))
bars18 = ax18.bar(x18, latency, width=0.55,
                  color=colours18, edgecolor="white", linewidth=0.6, zorder=3)

for bar, val in zip(bars18, latency):
    label = f"{val} ms" if val < 1000 else f"{val/1000:.1f} s"
    ax18.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 35,
              label, ha="center", va="bottom",
              fontsize=6.5, fontweight="bold", color="#222222")

ax18.set_xticks(x18)
ax18.set_xticklabels(modules, fontsize=7)
ax18.set_ylabel("Average Response Latency (ms)")
ax18.set_xlabel("Aura MediX Module")
ax18.set_ylim(0, 2750)
ax18.yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(2))
ax18.set_title("Fig. 18. Response Latency Comparison Across Aura MediX Modules",
               fontsize=8, pad=6, loc="left")
ax18.axhline(y=500, color="#c0392b", linewidth=0.8, linestyle="--",
             zorder=2, label="500 ms threshold")
ax18.legend(loc="upper left", fontsize=7)
ax18.annotate("Disk I/O\nbound", xy=(5, 2300), xytext=(4.5, 2560),
              fontsize=5.5, color="#8e44ad", ha="center",
              arrowprops=dict(arrowstyle="-|>", color="#8e44ad", lw=0.8))
ax18.spines["top"].set_visible(False)
ax18.spines["right"].set_visible(False)
fig18.tight_layout(pad=0.6)
fig18.savefig("fig18_latency_comparison.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig18)
print("✓ fig18_latency_comparison.png saved")