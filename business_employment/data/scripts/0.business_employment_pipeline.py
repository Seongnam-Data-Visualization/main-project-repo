"""성남 고용·사업체 데이터: 기존 build 스크립트 실행, 차트, Tableau 산출물."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")

SCRIPTS_DIR = Path(__file__).resolve().parent
EMPLOYMENT_ROOT = SCRIPTS_DIR.parent.parent
PROCESSED_ROOT = EMPLOYMENT_ROOT / "data" / "processed"
CLEAN_DIR = PROCESSED_ROOT / "clean"
FIGURE_DIR = PROCESSED_ROOT / "figures"
TABLE_DIR = PROCESSED_ROOT / "tables"
TABLEAU_DIR = PROCESSED_ROOT / "tableau"

MASTER_CSV = PROCESSED_ROOT / "seongnam_master.csv"
EMPLOYMENT_FINAL_CSV = PROCESSED_ROOT / "seongnam_employment_final.csv"
TABLEAU_MASTER_CSV = TABLEAU_DIR / "seongnam_employment_master.csv"

GU_SCATTER_COLORS = {"분당구": "#1f77b4", "수정구": "#ff7f0e", "중원구": "#2ca02c"}

# make_figures()가 끝까지 성공 시 생성되는 PNG 목록 (순서대로)
FIGURE_MANIFEST: tuple[str, ...] = (
    "dong_total_workers.png",
    "dong_self_employed_ratio.png",
    "gu_total_workers_boxplot.png",
    "gu_total_workers_bar.png",
    "dong_regular_worker_ratio.png",
    "gu_industry_stack_bar.png",
    "scatter_biz_vs_workers.png",
    "gu_corp_net_inflow_bar.png",
)

# biz → workers 이후 employment_final(기존 스크립트)이 있어야 master 입력이 생김.
# 그 다음 corp 계열은 master에서만 병합됨.
BUILD_STEPS: tuple[str, ...] = (
    "build_seongnam_biz_by_dong.py",
    "build_seongnam_workers_by_dong.py",
    "build_seongnam_employment_final.py",
    "build_seongnam_corp_by_dong.py",
    "build_seongnam_new_corp_by_dong.py",
    "build_seongnam_corp_move_by_dong.py",
    "build_seongnam_employment_master.py",
)


def ensure_dirs() -> None:
    for path in (CLEAN_DIR, FIGURE_DIR, TABLE_DIR, TABLEAU_DIR):
        path.mkdir(parents=True, exist_ok=True)


def configure_korean_font() -> None:
    names = [f.name for f in fm.fontManager.ttflist]
    for want in ("NanumGothic", "Nanum Gothic", "AppleGothic", "Apple SD Gothic Neo"):
        key = want.replace(" ", "").lower()
        for got in names:
            if key in got.replace(" ", "").lower():
                plt.rcParams["font.family"] = got
                plt.rcParams["axes.unicode_minus"] = False
                return
    plt.rcParams["font.family"] = "AppleGothic"
    plt.rcParams["axes.unicode_minus"] = False


def run_build_scripts() -> None:
    for name in BUILD_STEPS:
        script = SCRIPTS_DIR / name
        if not script.is_file():
            raise FileNotFoundError(f"Missing build script: {script}")
        subprocess.run([sys.executable, str(script)], cwd=str(SCRIPTS_DIR), check=True)


def save_barh(series: pd.Series, title: str, xlabel: str, filename: str) -> None:
    data = series.dropna().sort_values()
    height = max(4, min(14, len(data) * 0.35))
    plt.figure(figsize=(9, height))
    data.plot(kind="barh", color="#4C78A8")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / filename, dpi=160)
    plt.close()


def save_bar(
    series: pd.Series, title: str, ylabel: str, filename: str, horizontal: bool = False
) -> None:
    if horizontal:
        save_barh(series, title, ylabel, filename)
        return
    data = series.dropna().sort_values(ascending=False)
    width = max(6, min(10, 0.5 + len(data) * 0.55))
    plt.figure(figsize=(width, 5))
    data.plot(kind="bar", color="#4C78A8")
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / filename, dpi=160)
    plt.close()


def make_figures() -> None:
    if not MASTER_CSV.is_file():
        raise FileNotFoundError(f"Expected master CSV after build steps: {MASTER_CSV}")
    df = pd.read_csv(MASTER_CSV, encoding="utf-8-sig")
    df = df.sort_values(["gu_name", "dong_name"]).reset_index(drop=True)
    idx = df["dong_name"].astype(str)

    # 1
    save_barh(
        pd.Series(df["total_workers"].values, index=idx),
        "동별 총 종사자 수",
        "종사자 수",
        "dong_total_workers.png",
    )
    # 2
    save_barh(
        pd.Series(df["self_employed_ratio"].values, index=idx),
        "동별 자영업 비율",
        "비율",
        "dong_self_employed_ratio.png",
    )

    gu_order = sorted(df["gu_name"].dropna().unique())
    box_groups: list[tuple[str, np.ndarray]] = []
    for g in gu_order:
        arr = df.loc[df["gu_name"] == g, "total_workers"].dropna().to_numpy(dtype=float)
        if len(arr) > 0:
            box_groups.append((g, arr))
    # 3
    if box_groups:
        labels, groups = zip(*box_groups)
        plt.figure(figsize=(8, 5))
        plt.boxplot(groups, tick_labels=labels, showfliers=False)
        plt.title("구별 동 단위 총 종사자 수 분포")
        plt.ylabel("종사자 수")
        plt.tight_layout()
        plt.savefig(FIGURE_DIR / "gu_total_workers_boxplot.png", dpi=160)
        plt.close()

    # 4
    gu_workers_sum = df.groupby("gu_name", sort=False)["total_workers"].sum()
    gu_workers_sum = gu_workers_sum.reindex(sorted(gu_workers_sum.index))
    save_bar(
        gu_workers_sum,
        "구별 총 종사자 수 합계",
        "종사자 수",
        "gu_total_workers_bar.png",
        horizontal=False,
    )

    # 5
    tw = df["total_workers"].to_numpy(dtype=float)
    rw = df["regular_workers"].to_numpy(dtype=float)
    regular_ratio = np.where(tw > 0, rw / tw, np.nan)
    save_barh(
        pd.Series(regular_ratio, index=idx),
        "동별 상용근로 비율 (안정적 일자리 비중)",
        "비율",
        "dong_regular_worker_ratio.png",
    )

    # 6 — industry_* 는 master에 없고 employment_final에 있음
    if not EMPLOYMENT_FINAL_CSV.is_file():
        raise FileNotFoundError(f"Missing employment final for industry chart: {EMPLOYMENT_FINAL_CSV}")
    fin = pd.read_csv(EMPLOYMENT_FINAL_CSV, encoding="utf-8-sig")
    industry_cols = sorted(c for c in fin.columns if c.startswith("industry_"))
    if len(industry_cols) < 1:
        raise ValueError("No industry_* columns in employment final CSV")
    city_totals = fin[industry_cols].sum(axis=0)
    top5_cols = city_totals.nlargest(5).index.tolist()
    other_cols = [c for c in industry_cols if c not in top5_cols]
    by_gu = fin.groupby("gu_name", sort=False)[industry_cols].sum()
    stack = by_gu[top5_cols].copy()
    if other_cols:
        stack["기타"] = by_gu[other_cols].sum(axis=1)
    else:
        stack["기타"] = 0.0
    row_sums = stack.sum(axis=1).replace(0, np.nan)
    pct = stack.div(row_sums, axis=0).fillna(0.0)
    pct = pct.reindex(sorted(pct.index))
    ncol = len(pct.columns)
    bar_colors = [plt.cm.tab10(i % 10) for i in range(ncol)]
    plt.figure(figsize=(9, 5))
    pct.plot(kind="bar", stacked=True, ax=plt.gca(), color=bar_colors, width=0.65)
    plt.title("구별 업종 분포 비교")
    plt.ylabel("비율")
    plt.xlabel("")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "gu_industry_stack_bar.png", dpi=160, bbox_inches="tight")
    plt.close()

    # 7
    plt.figure(figsize=(9, 6))
    for gu, sub in df.groupby("gu_name"):
        color = GU_SCATTER_COLORS.get(str(gu), "#7f7f7f")
        plt.scatter(
            sub["total_biz"],
            sub["total_workers"],
            c=color,
            s=36,
            edgecolors="white",
            linewidths=0.35,
            label=str(gu),
            zorder=2,
        )
        for _, row in sub.iterrows():
            plt.annotate(
                str(row["dong_name"]),
                (float(row["total_biz"]), float(row["total_workers"])),
                fontsize=7,
                ha="center",
                va="bottom",
                alpha=0.85,
                zorder=3,
            )
    plt.title("동별 사업체 수 vs 종사자 수")
    plt.xlabel("사업체 수 (total_biz)")
    plt.ylabel("종사자 수 (total_workers)")
    plt.legend(title="구", loc="best")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "scatter_biz_vs_workers.png", dpi=160)
    plt.close()

    # 8
    net_by_gu = df.groupby("gu_name", sort=False)["순유입"].sum()
    net_by_gu = net_by_gu.reindex(sorted(net_by_gu.index))
    colors = ["#4C78A8" if v >= 0 else "#E45756" for v in net_by_gu.to_numpy(dtype=float)]
    plt.figure(figsize=(8, 5))
    plt.bar(net_by_gu.index.astype(str), net_by_gu.to_numpy(dtype=float), color=colors)
    plt.title("구별 기업 순유입 현황")
    plt.ylabel("순유입 합계")
    plt.xlabel("")
    plt.axhline(0, color="#333", linewidth=0.8, zorder=1)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "gu_corp_net_inflow_bar.png", dpi=160)
    plt.close()


def copy_tableau_master() -> None:
    if not MASTER_CSV.is_file():
        raise FileNotFoundError(f"Missing master for Tableau copy: {MASTER_CSV}")
    shutil.copy2(MASTER_CSV, TABLEAU_MASTER_CSV)


def main() -> None:
    ensure_dirs()
    configure_korean_font()
    run_build_scripts()
    make_figures()
    copy_tableau_master()
    print("Business employment pipeline complete")
    print(f"master: {MASTER_CSV}")
    print(f"figures: {FIGURE_DIR}")
    print(f"tableau: {TABLEAU_MASTER_CSV}")
    print("\n[생성 차트 PNG]")
    for name in FIGURE_MANIFEST:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
