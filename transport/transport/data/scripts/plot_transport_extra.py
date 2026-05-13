from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRIPT_DIR = Path(__file__).resolve().parent
TRANSPORT_DIR = SCRIPT_DIR.parents[1]
PROCESSED_ROOT = TRANSPORT_DIR / "data" / "processed"
FIGURE_DIR = PROCESSED_ROOT / "figures"
MASTER_PATH = PROCESSED_ROOT / "seongnam_transport_master.csv"
YEARLY_PATH = PROCESSED_ROOT / "tables" / "yearly_transport_summary.csv"

GU_COLORS = {"수정구": "#D55E00", "중원구": "#E69F00", "분당구": "#0072B2"}
GU_ORDER = ["수정구", "중원구", "분당구"]


def plot_yearly_mode_share(yearly: pd.DataFrame) -> None:
    years = yearly["source_year"].astype(str).tolist()
    x = np.arange(len(years))
    w = 0.25

    fig, ax = plt.subplots(figsize=(9, 5))
    b1 = ax.bar(x - w, yearly["avg_subway_share"], width=w, label="지하철", color="#0072B2")
    b2 = ax.bar(x,      yearly["avg_bus_share"],    width=w, label="버스",   color="#E69F00")
    b3 = ax.bar(x + w,  yearly["avg_car_share"],    width=w, label="승용차", color="#666666")

    for bars in (b1, b2, b3):
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.003,
                    f"{h:.1%}", ha="center", va="bottom", fontsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels([f"{y}년" for y in years])
    ax.set_ylabel("평균 수단 분담률")
    ax.set_title("연도별 통근 수단 분담 추이 (성남시 전체 평균)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_ylim(0, 0.58)
    ax.legend(loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "yearly_mode_share_trend.png", dpi=200)
    plt.close(fig)
    print("saved: yearly_mode_share_trend.png")


def plot_accessibility_boxplot(master: pd.DataFrame) -> None:
    data = [master.loc[master["gu_name"] == gu, "accessibility_score"].values for gu in GU_ORDER]
    colors = [GU_COLORS[gu] for gu in GU_ORDER]

    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot(data, patch_artist=True, widths=0.5, medianprops={"color": "white", "linewidth": 2})
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)

    ax.set_xticklabels(GU_ORDER)
    ax.set_ylabel("접근성 점수 (accessibility_score)")
    ax.set_title("구별 통근 접근성 점수 분포")
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.text(3.45, 0.05, "평균 기준선", fontsize=8, color="gray", va="bottom")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "accessibility_score_by_gu.png", dpi=200)
    plt.close(fig)
    print("saved: accessibility_score_by_gu.png")


def plot_seoul_commute_vs_access(master: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))

    for gu in GU_ORDER:
        sub = master[master["gu_name"] == gu]
        ax.scatter(sub["seoul_commute_share"], sub["accessibility_score"],
                   label=gu, color=GU_COLORS[gu], alpha=0.85, s=70, zorder=3)

    top5 = master.nlargest(5, "high_demand_low_access")
    for _, row in top5.iterrows():
        ax.annotate(
            row["dong_name"],
            (row["seoul_commute_share"], row["accessibility_score"]),
            fontsize=8.5,
            xytext=(6, 4),
            textcoords="offset points",
            arrowprops={"arrowstyle": "-", "color": "#888888", "lw": 0.8},
        )

    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.axvline(master["seoul_commute_share"].median(), color="gray",
               linestyle=":", linewidth=0.8, alpha=0.6)

    ax.text(master["seoul_commute_share"].median() + 0.002,
            ax.get_ylim()[0] + 0.05, "서울통근 중앙값", fontsize=8, color="gray")

    ax.set_xlabel("서울행 통근 비중")
    ax.set_ylabel("접근성 점수")
    ax.set_title("서울 통근 비중 vs 교통 접근성 (행정동별)\n※ 이름 표시: 수요↑ 접근성↓ 상위 5개 동")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.legend(loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    ax.fill_betweenx(
        [ylim[0], 0],
        master["seoul_commute_share"].median(),
        xlim[1],
        alpha=0.05, color="#D55E00",
    )

    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "seoul_commute_vs_accessibility.png", dpi=200)
    plt.close(fig)
    print("saved: seoul_commute_vs_accessibility.png")


def main() -> None:
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False

    master = pd.read_csv(MASTER_PATH, encoding="utf-8-sig")
    yearly = pd.read_csv(YEARLY_PATH, encoding="utf-8-sig")
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    plot_yearly_mode_share(yearly)
    plot_accessibility_boxplot(master)
    plot_seoul_commute_vs_access(master)

    print(f"\n3개 figure 생성 완료 → {FIGURE_DIR}")


if __name__ == "__main__":
    main()
