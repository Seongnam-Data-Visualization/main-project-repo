from __future__ import annotations

from datetime import date
from pathlib import Path
from textwrap import fill

import matplotlib

matplotlib.use("Agg")

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd
import seaborn as sns


RESIDENTIAL_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_ROOT = RESIDENTIAL_ROOT / "data" / "processed"
TABLEAU_DIR = PROCESSED_ROOT / "tableau"
OUTPUT_DIR = PROCESSED_ROOT / "python_visualizations"

GU_ORDER = ["분당구", "수정구", "중원구"]
TYPE_ORDER = ["아파트", "단독_다가구", "연립_다세대", "오피스텔"]
PALETTE_GU = {
    "분당구": "#2F80ED",
    "수정구": "#27AE60",
    "중원구": "#EB5757",
}


def setup_theme() -> None:
    available_fonts = {font.name for font in fm.fontManager.ttflist}
    for font_name in ("Malgun Gothic", "NanumGothic", "AppleGothic"):
        if font_name in available_fonts:
            plt.rcParams["font.family"] = font_name
            break
    plt.rcParams["axes.unicode_minus"] = False
    sns.set_theme(
        context="notebook",
        style="whitegrid",
        font=plt.rcParams.get("font.family", ["sans-serif"])[0],
        rc={
            "axes.edgecolor": "#D0D5DD",
            "axes.labelcolor": "#344054",
            "axes.titlecolor": "#101828",
            "grid.color": "#EAECF0",
            "legend.frameon": False,
        },
    )


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(TABLEAU_DIR / name, encoding="utf-8-sig")


def save(fig: plt.Figure, filename: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_DIR / filename, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def comma(value: float) -> str:
    if pd.isna(value):
        return "-"
    return f"{value:,.0f}"


def man(value: float) -> str:
    if pd.isna(value):
        return "-"
    return f"{value / 10000:.1f}만"


def pct(value: float) -> str:
    if pd.isna(value):
        return "-"
    return f"{value:.1%}"


def build_metrics(admin: pd.DataFrame, cost: pd.DataFrame, gu_ref: pd.DataFrame, sales: pd.DataFrame, rent: pd.DataFrame) -> dict:
    total_households = admin["세대수"].sum()
    gu_admin = admin.groupby("구", as_index=False)[["세대수", "총인구", "생산가능인구_19_64세"]].sum()
    gu_admin["세대비중"] = gu_admin["세대수"] / total_households

    sales_clean = sales[sales["매매가_평당_만원"].notna() & (~sales["가격_이상치_IQR"].fillna(False))].copy()
    gu_sales = sales_clean.groupby("구", as_index=False)["매매가_평당_만원"].median()
    gu_sales = gu_sales.rename(columns={"매매가_평당_만원": "매매가_평당_중앙값"})

    trade_counts = []
    for label, column in (("매매", "매매_거래건수"), ("전세", "전세_거래건수"), ("월세", "월세_거래건수")):
        frame = cost.groupby("구", as_index=False)[column].sum()
        frame["거래구분"] = label
        frame = frame.rename(columns={column: "거래건수"})
        trade_counts.append(frame)
    trade_counts = pd.concat(trade_counts, ignore_index=True)

    gu = (
        gu_admin.merge(gu_ref, left_on="구", right_on="지역명", how="left", suffixes=("", "_구단위"))
        .merge(gu_sales, on="구", how="left")
    )

    top_households = admin.nlargest(5, "세대수")[["구", "행정동명", "세대수", "생산가능인구_19_64세", "65세이상인구비율"]]
    top_elderly = admin.nlargest(5, "65세이상인구비율")[["구", "행정동명", "세대수", "65세이상인구비율"]]
    top_working_ratio = admin.nlargest(5, "생산가능인구비율_19_64세")[["구", "행정동명", "세대수", "생산가능인구비율_19_64세"]]

    top_sales = (
        cost[cost["매매_거래건수"].fillna(0) >= 10]
        .nlargest(8, "매매가_평당_중앙값")[["구", "법정동명", "건축유형", "매매_거래건수", "매매가_평당_중앙값"]]
        .copy()
    )
    top_jeonse = (
        cost[cost["전세_거래건수"].fillna(0) >= 10]
        .nlargest(8, "전세보증금_평당_중앙값")[["구", "법정동명", "건축유형", "전세_거래건수", "전세보증금_평당_중앙값"]]
        .copy()
    )
    top_monthly = (
        cost[cost["월세_거래건수"].fillna(0) >= 10]
        .nlargest(8, "월세_평당_중앙값")[["구", "법정동명", "건축유형", "월세_거래건수", "월세_평당_중앙값"]]
        .copy()
    )

    rent_counts = rent.groupby(["구", "전월세구분"], as_index=False).size().rename(columns={"size": "거래건수"})
    sales_counts = sales.groupby("구", as_index=False).size().rename(columns={"size": "거래건수"})
    sales_counts["거래구분"] = "매매"
    rent_counts = rent_counts.rename(columns={"전월세구분": "거래구분"})
    transaction_counts_raw = pd.concat([sales_counts, rent_counts], ignore_index=True)

    return {
        "gu": gu,
        "trade_counts": trade_counts,
        "transaction_counts_raw": transaction_counts_raw,
        "top_households": top_households,
        "top_elderly": top_elderly,
        "top_working_ratio": top_working_ratio,
        "top_sales": top_sales,
        "top_jeonse": top_jeonse,
        "top_monthly": top_monthly,
        "city_households": total_households,
        "sales_clean": sales_clean,
    }


def draw_card(ax: plt.Axes, x: float, y: float, w: float, h: float, color: str, title: str, body: str) -> None:
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        linewidth=0,
        facecolor=color,
        alpha=0.11,
        transform=ax.transAxes,
    )
    ax.add_patch(box)
    ax.text(x + 0.03, y + h - 0.055, fill(title, width=24), transform=ax.transAxes, fontsize=13.5, weight="bold", color=color, va="top", linespacing=1.25)
    ax.text(x + 0.03, y + h - 0.145, fill(body, width=37), transform=ax.transAxes, fontsize=10.2, color="#344054", va="top", linespacing=1.42)


def plot_executive_summary(metrics: dict) -> None:
    gu = metrics["gu"].set_index("구")
    top_admin = metrics["top_households"].iloc[0]
    top_sale = metrics["top_sales"].iloc[0]
    top_monthly = metrics["top_monthly"].iloc[0]

    fig, ax = plt.subplots(figsize=(13, 9.2))
    ax.set_axis_off()
    ax.text(0.02, 0.94, "성남시 주거 데이터 핵심 인사이트", fontsize=24, weight="bold", color="#101828", transform=ax.transAxes)
    ax.text(
        0.02,
        0.885,
        "인구/세대, 주택 재고, 실거래 가격과 거래량을 함께 보면 구별 역할이 선명하게 갈립니다.",
        fontsize=12.5,
        color="#667085",
        transform=ax.transAxes,
    )

    bd = gu.loc["분당구"]
    sj = gu.loc["수정구"]
    jw = gu.loc["중원구"]
    draw_card(
        ax,
        0.04,
        0.61,
        0.43,
        0.22,
        PALETTE_GU["분당구"],
        "1. 분당구는 가격과 아파트 재고의 중심",
        f"세대수 {man(bd['세대수'])}, 아파트 비율 {pct(bd['아파트비율'])}, 매매가 중앙값 {comma(bd['매매가_평당_중앙값'])}만원/평으로 세 축 모두에서 가장 강합니다.",
    )
    draw_card(
        ax,
        0.53,
        0.61,
        0.43,
        0.22,
        PALETTE_GU["수정구"],
        "2. 수정구는 단독/다가구 재고와 도심 수요가 겹침",
        f"단독/다가구 비율 {pct(sj['단독_다가구비율'])}로 가장 높고, {top_admin['행정동명']}처럼 세대 규모가 큰 행정동이 가격 수요와 맞물립니다.",
    )
    draw_card(
        ax,
        0.04,
        0.35,
        0.43,
        0.22,
        PALETTE_GU["중원구"],
        "3. 중원구는 상대적 가격 접근성과 연립/다세대 비중",
        f"세대수 대비 주택수 {jw['세대수_대비_주택수']:.2f}, 연립/다세대 비율 {pct(jw['연립_다세대비율'])}로 중저가 주거 선택지 성격이 강합니다.",
    )
    draw_card(
        ax,
        0.53,
        0.35,
        0.43,
        0.22,
        "#9B51E0",
        "4. 가격 상단은 특정 법정동-유형 조합이 주도",
        f"매매 상위 조합은 {top_sale['구']} {top_sale['법정동명']} {top_sale['건축유형']}({comma(top_sale['매매가_평당_중앙값'])}만원/평)입니다.",
    )
    draw_card(
        ax,
        0.04,
        0.09,
        0.43,
        0.22,
        "#F2994A",
        "5. 월세 고가 조합은 오피스텔/소형 주거에서 두드러짐",
        f"월세 상위 조합은 {top_monthly['구']} {top_monthly['법정동명']} {top_monthly['건축유형']}({top_monthly['월세_평당_중앙값']:.1f}만원/평)입니다.",
    )
    draw_card(
        ax,
        0.53,
        0.09,
        0.43,
        0.22,
        "#475467",
        "6. 해석 단위는 반드시 분리해서 봐야 함",
        "인구/세대 지도는 행정동, 가격은 법정동, 주택 재고는 구 단위입니다. 직접 결합보다 축별 비교가 안전합니다.",
    )
    save(fig, "15_insight_executive_summary.png")


def plot_admin_quadrants(admin: pd.DataFrame) -> None:
    data = admin.copy()
    x_mid = data["세대수"].median()
    y_mid = data["생산가능인구비율_19_64세"].median()

    fig, ax = plt.subplots(figsize=(11, 7.5))
    sns.scatterplot(
        data=data,
        x="세대수",
        y="생산가능인구비율_19_64세",
        hue="구",
        hue_order=GU_ORDER,
        size="65세이상인구비율",
        sizes=(80, 380),
        palette=PALETTE_GU,
        edgecolor="white",
        linewidth=0.9,
        alpha=0.9,
        ax=ax,
    )
    ax.axvline(x_mid, color="#98A2B3", linestyle="--", linewidth=1)
    ax.axhline(y_mid, color="#98A2B3", linestyle="--", linewidth=1)
    ax.text(x_mid * 1.02, data["생산가능인구비율_19_64세"].max() * 0.995, "세대수 중앙값", color="#667085", fontsize=9)
    ax.text(data["세대수"].min() * 1.05, y_mid * 1.003, "생산가능인구비율 중앙값", color="#667085", fontsize=9)

    for _, row in pd.concat([data.nlargest(6, "세대수"), data.nlargest(4, "65세이상인구비율")]).drop_duplicates("행정동명").iterrows():
        ax.annotate(row["행정동명"], (row["세대수"], row["생산가능인구비율_19_64세"]), xytext=(6, 5), textcoords="offset points", fontsize=9)

    ax.set_title("행정동 수요 포지셔닝: 규모 x 생산가능인구 비율", fontsize=18, weight="bold", pad=14)
    ax.set_xlabel("세대수")
    ax.set_ylabel("생산가능인구 비율(19-64세)")
    ax.xaxis.set_major_formatter(lambda x, _: f"{x / 10000:.1f}만" if x >= 10000 else f"{x:,.0f}")
    ax.yaxis.set_major_formatter(lambda y, _: f"{y:.0%}")
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), title="")
    ax.text(0.98, 0.96, "대규모·활동인구형", transform=ax.transAxes, ha="right", color="#101828", fontsize=11, weight="bold")
    ax.text(0.02, 0.08, "소규모·고령/저활동형", transform=ax.transAxes, ha="left", color="#101828", fontsize=11, weight="bold")
    sns.despine()
    save(fig, "16_insight_admin_dong_quadrants.png")


def plot_gu_positioning(metrics: dict) -> None:
    gu = metrics["gu"].copy()

    fig, ax = plt.subplots(figsize=(10, 7))
    scatter = ax.scatter(
        gu["세대수_대비_주택수"],
        gu["매매가_평당_중앙값"],
        s=gu["세대수"] / 90,
        c=gu["아파트비율"],
        cmap="Blues",
        edgecolors="white",
        linewidths=1.4,
        alpha=0.92,
    )
    for _, row in gu.iterrows():
        ax.annotate(
            f"{row['구']}\n세대 {man(row['세대수'])}",
            (row["세대수_대비_주택수"], row["매매가_평당_중앙값"]),
            xytext=(12, 8),
            textcoords="offset points",
            fontsize=11,
            weight="bold",
        )
    ax.axvline(1.0, color="#475467", linestyle="--", linewidth=1, alpha=0.8)
    ax.set_title("구별 수요-공급-가격 포지셔닝", fontsize=18, weight="bold", pad=14)
    ax.set_xlabel("세대수 대비 주택수")
    ax.set_ylabel("매매가 중앙값(만원/평)")
    x_margin = (gu["세대수_대비_주택수"].max() - gu["세대수_대비_주택수"].min()) * 0.35
    y_margin = (gu["매매가_평당_중앙값"].max() - gu["매매가_평당_중앙값"].min()) * 0.25
    ax.set_xlim(gu["세대수_대비_주택수"].min() - x_margin, max(1.01, gu["세대수_대비_주택수"].max() + x_margin))
    ax.set_ylim(gu["매매가_평당_중앙값"].min() - y_margin, gu["매매가_평당_중앙값"].max() + y_margin)
    cbar = fig.colorbar(scatter, ax=ax, shrink=0.78)
    cbar.set_label("아파트 비율")
    cbar.ax.yaxis.set_major_formatter(lambda y, _: f"{y:.0%}")
    ax.text(1.002, ax.get_ylim()[0], "주택수=세대수", color="#667085", fontsize=9, va="bottom")
    sns.despine()
    save(fig, "17_insight_gu_demand_supply_price.png")


def plot_top_price_triptych(metrics: dict) -> None:
    specs = [
        ("매매가_평당_중앙값", "매매_거래건수", "top_sales", "매매가 상위 조합", "만원/평", "#2F80ED"),
        ("전세보증금_평당_중앙값", "전세_거래건수", "top_jeonse", "전세보증금 상위 조합", "만원/평", "#27AE60"),
        ("월세_평당_중앙값", "월세_거래건수", "top_monthly", "월세 상위 조합", "만원/평", "#F2994A"),
    ]
    fig, axes = plt.subplots(3, 1, figsize=(12, 13.5))
    for ax, (value_col, count_col, key, title, unit, color) in zip(axes, specs):
        data = metrics[key].copy().sort_values(value_col)
        data["라벨"] = data["구"] + " " + data["법정동명"] + " / " + data["건축유형"] + " / " + data[count_col].fillna(0).astype(int).astype(str) + "건"
        ax.barh(data["라벨"], data[value_col], color=color, alpha=0.86)
        for y, value in enumerate(data[value_col]):
            label = f"{value:.1f}" if value < 100 else f"{value:,.0f}"
            ax.text(value, y, f" {label}", va="center", fontsize=9, color="#344054")
        ax.set_title(title, fontsize=14, weight="bold")
        ax.set_xlabel(unit)
        ax.set_ylabel("")
        ax.grid(axis="x", color="#EAECF0")
        ax.tick_params(axis="y", labelsize=9.5)
    fig.suptitle("법정동-건축유형별 가격 상위 조합", fontsize=19, weight="bold", y=1.02)
    fig.text(0.01, 0.01, "거래건수 10건 이상 조합만 표시", color="#667085", fontsize=10)
    fig.subplots_adjust(hspace=0.48)
    sns.despine()
    save(fig, "18_insight_top_price_combinations.png")


def plot_transaction_mix(metrics: dict) -> None:
    data = metrics["transaction_counts_raw"].copy()
    data["거래구분"] = pd.Categorical(data["거래구분"], categories=["매매", "전세", "월세"], ordered=True)
    pivot = data.pivot_table(index="구", columns="거래구분", values="거래건수", aggfunc="sum", observed=False).reindex(GU_ORDER).fillna(0)
    ratio = pivot.div(pivot.sum(axis=1), axis=0)

    fig, ax = plt.subplots(figsize=(10, 5.8))
    left = pd.Series(0.0, index=ratio.index)
    colors = {"매매": "#2F80ED", "전세": "#27AE60", "월세": "#F2994A"}
    for trade in ["매매", "전세", "월세"]:
        ax.barh(ratio.index, ratio[trade], left=left, color=colors[trade], label=trade, height=0.56)
        for idx, value in ratio[trade].items():
            if value >= 0.09:
                ax.text(left.loc[idx] + value / 2, idx, f"{value:.0%}", ha="center", va="center", color="white", fontsize=10, weight="bold")
        left += ratio[trade]
    totals = pivot.sum(axis=1)
    for idx in ratio.index:
        ax.text(1.01, idx, f"총 {comma(totals.loc[idx])}건", va="center", fontsize=10, color="#344054")
    ax.set_xlim(0, 1.16)
    ax.set_title("구별 실거래 거래구분 믹스", fontsize=18, weight="bold", pad=14)
    ax.set_xlabel("거래 비중")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(lambda x, _: f"{x:.0%}")
    ax.legend(ncols=3, loc="upper center", bbox_to_anchor=(0.5, -0.10))
    sns.despine(left=True, bottom=True)
    save(fig, "19_insight_transaction_mix.png")


def write_insights(metrics: dict) -> None:
    gu = metrics["gu"].set_index("구")
    top_h = metrics["top_households"].iloc[0]
    top_e = metrics["top_elderly"].iloc[0]
    top_w = metrics["top_working_ratio"].iloc[0]
    top_s = metrics["top_sales"].iloc[0]
    top_j = metrics["top_jeonse"].iloc[0]
    top_m = metrics["top_monthly"].iloc[0]

    lines = [
        "# Residential Insights",
        "",
        f"생성일: {date.today().isoformat()}",
        "",
        "이 문서는 `python_visualizations`의 figure와 `processed/tableau` CSV를 함께 보고 도출한 핵심 인사이트입니다.",
        "",
        "## 핵심 결론",
        "",
        f"1. **분당구는 성남시 주거시장의 가격 및 아파트 재고 중심축입니다.** 세대수는 {man(gu.loc['분당구', '세대수'])}({pct(gu.loc['분당구', '세대수'] / metrics['city_households'])})이고, 아파트 비율은 {pct(gu.loc['분당구', '아파트비율'])}, 매매가 중앙값은 {comma(gu.loc['분당구', '매매가_평당_중앙값'])}만원/평입니다.",
        f"2. **수정구는 단독/다가구 중심의 재고 구조와 도심형 수요가 겹칩니다.** 단독/다가구 비율이 {pct(gu.loc['수정구', '단독_다가구비율'])}로 가장 높고, 세대수 대비 주택수는 {gu.loc['수정구', '세대수_대비_주택수']:.2f}입니다.",
        f"3. **중원구는 상대적으로 가격 접근성이 있고 연립/다세대 비중이 큽니다.** 연립/다세대 비율은 {pct(gu.loc['중원구', '연립_다세대비율'])}, 세대수 대비 주택수는 {gu.loc['중원구', '세대수_대비_주택수']:.2f}입니다.",
        f"4. **행정동 수요의 절대 규모는 일부 동에 집중됩니다.** 세대수 1위는 {top_h['구']} {top_h['행정동명']}({comma(top_h['세대수'])}세대)이고, 고령인구 비율 1위는 {top_e['구']} {top_e['행정동명']}({pct(top_e['65세이상인구비율'])})입니다.",
        f"5. **가격 상단은 특정 법정동-건축유형 조합이 끌어올립니다.** 매매 상위는 {top_s['구']} {top_s['법정동명']} {top_s['건축유형']}({comma(top_s['매매가_평당_중앙값'])}만원/평), 전세 상위는 {top_j['구']} {top_j['법정동명']} {top_j['건축유형']}({comma(top_j['전세보증금_평당_중앙값'])}만원/평), 월세 상위는 {top_m['구']} {top_m['법정동명']} {top_m['건축유형']}({top_m['월세_평당_중앙값']:.1f}만원/평)입니다.",
        "",
        "## 추가 생성 Figure",
        "",
        "- `15_insight_executive_summary.png`: 전체 분석을 6개 메시지 카드로 요약한 executive summary입니다.",
        "- `16_insight_admin_dong_quadrants.png`: 행정동별 세대수와 생산가능인구 비율을 사분면으로 나눈 수요 포지셔닝 figure입니다.",
        "- `17_insight_gu_demand_supply_price.png`: 구별 세대수 대비 주택수, 매매가, 아파트 비율을 함께 본 포지셔닝 figure입니다.",
        "- `18_insight_top_price_combinations.png`: 매매/전세/월세의 법정동-건축유형별 가격 상위 조합을 비교한 figure입니다.",
        "- `19_insight_transaction_mix.png`: 구별 매매/전세/월세 거래 비중과 총 거래건수를 보여주는 figure입니다.",
        "",
        "## Figure별 활용 메모",
        "",
        "- 수요 규모를 설명할 때는 `01`, `02`, `03`, `16`을 함께 사용합니다.",
        "- 고령화 또는 활동인구 특성을 설명할 때는 `04`, `05`, `16`을 함께 사용합니다.",
        "- 구별 주택 재고 구조와 공급 여건은 `06`, `07`, `17`로 설명합니다.",
        "- 가격 수준과 고가 조합은 `08`, `09`, `10`, `12`, `18`을 사용합니다.",
        "- 거래량과 시장 두께는 `11`, `13`, `14`, `19`로 보완합니다.",
        "",
        "## 해석상 주의",
        "",
        "- 인구/세대 자료는 행정동 단위, 가격 자료는 법정동 단위, 주택 재고는 구 단위입니다.",
        "- `03_admin_dong_cost_proxy.csv`는 행정동명 기반 추정 매핑이므로 핵심 인사이트에서는 가격-행정동 직접 결합을 피했습니다.",
        "- 실거래 기간은 2025.5.13-2026.5.12이며, 2025년 5월과 2026년 5월은 부분월입니다.",
    ]
    (OUTPUT_DIR / "INSIGHTS.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    setup_theme()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    admin = read_csv("01_admin_dong_demand.csv")
    cost = read_csv("02_legal_dong_cost_summary.csv")
    gu_ref = read_csv("05_gu_demand_and_stock_reference.csv")
    sales = read_csv("transactions_sales_long.csv")
    rent = read_csv("transactions_rent_long.csv")

    metrics = build_metrics(admin, cost, gu_ref, sales, rent)
    plot_executive_summary(metrics)
    plot_admin_quadrants(admin)
    plot_gu_positioning(metrics)
    plot_top_price_triptych(metrics)
    plot_transaction_mix(metrics)
    write_insights(metrics)
    print(f"created insight report and figures in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
