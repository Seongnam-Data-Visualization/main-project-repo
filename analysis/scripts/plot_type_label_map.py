from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_DATA_DIR = PROJECT_ROOT / "analysis" / "data"
OUTPUT_DIR = PROJECT_ROOT / "analysis" / "figures"
GEOJSON_PATH = PROJECT_ROOT / "residential" / "data" / "raw" / "Dataset_v1" / "seongnam_dong.geojson"

TYPE_COLOR = {
    "Type A (자족형)": "#2CA25F",       # best / low risk
    "Type B (직주분리형)": "#FEC44F",    # moderate risk
    "Type C (접근성 불량형)": "#F16913",  # high risk
    "Type D (복합 취약형)": "#B10026",   # very high risk
}

TYPE_ORDER = [
    "Type A (자족형)",
    "Type B (직주분리형)",
    "Type C (접근성 불량형)",
    "Type D (복합 취약형)",
]

TYPE_SHORT = {
    "Type A (자족형)": "A",
    "Type B (직주분리형)": "B",
    "Type C (접근성 불량형)": "C",
    "Type D (복합 취약형)": "D",
}

TYPE_RISK_NOTE = {
    "Type A (자족형)": "A: best / low risk",
    "Type B (직주분리형)": "B: worse / commute mismatch",
    "Type C (접근성 불량형)": "C: high accessibility risk",
    "Type D (복합 취약형)": "D: highest combined risk",
}


def setup_font() -> None:
    available_fonts = {font.name for font in fm.fontManager.ttflist}
    for font_name in ("Malgun Gothic", "NanumGothic", "AppleGothic"):
        if font_name in available_fonts:
            plt.rcParams["font.family"] = font_name
            break
    plt.rcParams["axes.unicode_minus"] = False


def main() -> None:
    setup_font()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    scored = pd.read_csv(ANALYSIS_DATA_DIR / "seongnam_scored.csv", encoding="utf-8-sig")
    scored["ADM_CD"] = scored["ADM_CD"].astype(str)
    scored["type_code"] = scored["type_label"].map(TYPE_SHORT)
    scored["type_color"] = scored["type_label"].map(TYPE_COLOR)

    gdf = gpd.read_file(GEOJSON_PATH)
    gdf["ADM_CD"] = gdf["ADM_CD"].astype(str)
    mapped = gdf.merge(scored, on="ADM_CD", how="left")
    mapped["plot_color"] = mapped["type_label"].map(TYPE_COLOR).fillna("#D0D5DD")
    gu_boundary = mapped.dissolve(by="gu_name", dropna=False)

    fig, ax = plt.subplots(figsize=(10.5, 11.5))
    mapped.plot(color=mapped["plot_color"], edgecolor="white", linewidth=0.75, ax=ax)
    mapped.boundary.plot(ax=ax, color="#FFFFFF", linewidth=0.55)
    gu_boundary.boundary.plot(ax=ax, color="#101828", linewidth=2.2, alpha=0.9)

    for _, row in mapped.iterrows():
        if row.geometry is None or row.geometry.is_empty:
            continue
        point = row.geometry.representative_point()
        dong = row.get("dong_name") or row.get("행정동명") or row.get("ADM_NM") or ""
        type_code = row.get("type_code") or "-"
        ax.text(
            point.x,
            point.y,
            f"{dong}\n{type_code}",
            ha="center",
            va="center",
            fontsize=6.2,
            color="white" if type_code in {"C", "D"} else "#101828",
            weight="bold",
            linespacing=0.92,
        )

    for gu_name, row in gu_boundary.iterrows():
        if row.geometry is None or row.geometry.is_empty or pd.isna(gu_name):
            continue
        point = row.geometry.representative_point()

    handles = [
        Patch(facecolor=TYPE_COLOR[label], edgecolor="none", label=f"{TYPE_SHORT[label]} - {label.split(' ', 2)[2]}")
        for label in TYPE_ORDER
    ]
    ax.legend(
        handles=handles,
        title="Type Label",
        loc="lower left",
        bbox_to_anchor=(0.02, 0.03),
        frameon=True,
        framealpha=0.94,
        facecolor="white",
        edgecolor="#D0D5DD",
        fontsize=10,
        title_fontsize=11,
    )

    counts = scored["type_label"].value_counts().reindex(TYPE_ORDER).fillna(0).astype(int)
    note_lines = [TYPE_RISK_NOTE[label] + f" ({counts[label]}개 동)" for label in TYPE_ORDER]
    ax.text(
        0.02,
        0.97,
        "\n".join(note_lines),
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9.5,
        color="#344054",
        bbox={"boxstyle": "round,pad=0.45", "facecolor": "white", "edgecolor": "#D0D5DD", "alpha": 0.94},
    )

    ax.set_title("성남시 행정동 Type Label 지도", fontsize=22, weight="bold", pad=18, color="#101828")
    ax.text(
        0.5,
        1.005,
        "A가 가장 양호하며, B-C-D로 갈수록 위험도가 커지도록 색상을 부여",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=11,
        color="#667085",
    )
    ax.set_axis_off()
    fig.text(
        0.01,
        0.01,
        "Data: analysis/data/seongnam_scored.csv(type_label), residential/data/raw/Dataset_v1/seongnam_dong.geojson. Thick border: gu boundary",
        fontsize=9,
        color="#667085",
    )

    fig.savefig(OUTPUT_DIR / "seongnam_type_label_map.png", dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"saved {OUTPUT_DIR / 'seongnam_type_label_map.png'}")


if __name__ == "__main__":
    main()
