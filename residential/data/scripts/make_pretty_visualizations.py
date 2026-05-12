from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

try:
    import geopandas as gpd
except ImportError:  # pragma: no cover - maps are skipped if geopandas is unavailable.
    gpd = None


RESIDENTIAL_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = RESIDENTIAL_ROOT / "data" / "raw" / "Dataset_v1"
PROCESSED_ROOT = RESIDENTIAL_ROOT / "data" / "processed"
TABLEAU_DIR = PROCESSED_ROOT / "tableau"
OUTPUT_DIR = PROCESSED_ROOT / "python_visualizations"

PALETTE_GU = {
    "분당구": "#2F80ED",
    "수정구": "#27AE60",
    "중원구": "#EB5757",
}

PALETTE_TYPE = {
    "아파트": "#2F80ED",
    "단독_다가구": "#F2994A",
    "연립_다세대": "#27AE60",
    "오피스텔": "#9B51E0",
    "기타": "#828282",
}

TYPE_ORDER = ["아파트", "단독_다가구", "연립_다세대", "오피스텔", "기타"]
GU_ORDER = ["분당구", "수정구", "중원구"]


def setup_theme() -> None:
    available_fonts = {font.name for font in fm.fontManager.ttflist}
    for font_name in ("Malgun Gothic", "NanumGothic", "AppleGothic"):
        if font_name in available_fonts:
            plt.rcParams["font.family"] = font_name
            break
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 120
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


def read_tableau_csv(filename: str) -> pd.DataFrame:
    return pd.read_csv(TABLEAU_DIR / filename, encoding="utf-8-sig")


def save_figure(fig: plt.Figure, filename: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_DIR / filename, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def format_number(value: float) -> str:
    if pd.isna(value):
        return ""
    if abs(value) >= 10000:
        return f"{value / 10000:.1f}만"
    return f"{value:,.0f}"


def add_source_note(fig: plt.Figure, note: str) -> None:
    fig.text(0.01, 0.01, note, ha="left", va="bottom", color="#667085", fontsize=9)


def plot_admin_households(admin: pd.DataFrame) -> None:
    data = admin.sort_values("세대수", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 14))
    sns.barplot(
        data=data,
        x="세대수",
        y="행정동명",
        hue="구",
        hue_order=GU_ORDER,
        palette=PALETTE_GU,
        dodge=False,
        ax=ax,
    )
    ax.set_title("행정동별 세대수", fontsize=18, weight="bold", pad=14)
    ax.set_xlabel("세대수")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(lambda x, _: format_number(x))
    for container in ax.containers:
        ax.bar_label(container, labels=[format_number(v.get_width()) for v in container], padding=3, fontsize=8)
    sns.despine(left=True, bottom=True)
    add_source_note(fig, "자료: 2026.3 인구현황, 성남시")
    save_figure(fig, "01_admin_dong_households.png")


def plot_admin_demand_scatter(admin: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.scatterplot(
        data=admin,
        x="세대수",
        y="생산가능인구_19_64세",
        hue="구",
        hue_order=GU_ORDER,
        size="65세이상인구비율",
        sizes=(70, 360),
        palette=PALETTE_GU,
        edgecolor="white",
        linewidth=0.8,
        alpha=0.88,
        ax=ax,
    )
    for _, row in admin.nlargest(7, "세대수").iterrows():
        ax.annotate(row["행정동명"], (row["세대수"], row["생산가능인구_19_64세"]), xytext=(6, 5), textcoords="offset points", fontsize=9)
    ax.set_title("세대수와 생산가능인구의 관계", fontsize=18, weight="bold", pad=14)
    ax.set_xlabel("세대수")
    ax.set_ylabel("생산가능인구(19-64세)")
    ax.xaxis.set_major_formatter(lambda x, _: format_number(x))
    ax.yaxis.set_major_formatter(lambda y, _: format_number(y))
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), title="")
    sns.despine()
    add_source_note(fig, "원 크기: 65세 이상 인구비율")
    save_figure(fig, "02_admin_households_vs_working_age.png")


def plot_admin_maps(admin: pd.DataFrame) -> None:
    if gpd is None:
        return
    geojson_path = RAW_DATA_DIR / "seongnam_dong.geojson"
    if not geojson_path.exists():
        return

    gdf = gpd.read_file(geojson_path)
    gdf["ADM_CD"] = gdf["ADM_CD"].astype(str)
    admin = admin.copy()
    admin["ADM_CD"] = admin["ADM_CD"].astype(str)
    merged = gdf.merge(admin, on="ADM_CD", how="left")

    map_specs = [
        ("세대수", "행정동별 세대수 지도", "03_map_admin_households.png", "Blues", None),
        ("생산가능인구비율_19_64세", "행정동별 생산가능인구 비율", "04_map_working_age_ratio.png", "Greens", "{:.0%}"),
        ("65세이상인구비율", "행정동별 65세 이상 인구 비율", "05_map_elderly_ratio.png", "OrRd", "{:.0%}"),
    ]

    for column, title, filename, cmap, fmt in map_specs:
        fig, ax = plt.subplots(figsize=(8, 9))
        merged.plot(
            column=column,
            cmap=cmap,
            linewidth=0.6,
            edgecolor="white",
            legend=True,
            legend_kwds={"shrink": 0.72, "label": title.replace("지도", "").strip()},
            missing_kwds={"color": "#F2F4F7", "edgecolor": "white"},
            ax=ax,
        )
        for _, row in merged.iterrows():
            if row.geometry is None or row.geometry.is_empty or pd.isna(row.get(column)):
                continue
            point = row.geometry.representative_point()
            label = row.get("행정동명", "")
            ax.text(point.x, point.y, label, ha="center", va="center", fontsize=6.5, color="#344054")
        ax.set_title(title, fontsize=18, weight="bold", pad=14)
        ax.set_axis_off()
        add_source_note(fig, "지도: 직접 추출한 seongnam_dong.geojson, 지표: 2026.3 인구현황")
        save_figure(fig, filename)


def plot_housing_stock(stock_long: pd.DataFrame, gu_ref: pd.DataFrame) -> None:
    stock = stock_long.copy()
    stock = stock[stock["주택수"].notna() & (stock["주택수"] > 0)]
    stock["주택유형"] = pd.Categorical(stock["주택유형"], categories=TYPE_ORDER, ordered=True)
    pivot = (
        stock.pivot_table(index="지역명", columns="주택유형", values="주택수", aggfunc="sum", observed=False)
        .reindex(GU_ORDER)
        .fillna(0)
    )
    ratio = pivot.div(pivot.sum(axis=1), axis=0)

    fig, ax = plt.subplots(figsize=(10, 5.8))
    left = pd.Series(0.0, index=ratio.index)
    for housing_type in TYPE_ORDER:
        if housing_type not in ratio:
            continue
        values = ratio[housing_type]
        ax.barh(
            ratio.index,
            values,
            left=left,
            color=PALETTE_TYPE.get(housing_type, "#98A2B3"),
            label=housing_type,
            height=0.58,
        )
        for idx, value in values.items():
            if value >= 0.07:
                ax.text(left.loc[idx] + value / 2, idx, f"{value:.0%}", ha="center", va="center", color="white", fontsize=10, weight="bold")
        left += values

    ax.set_title("구별 주택 재고 구성", fontsize=18, weight="bold", pad=14)
    ax.set_xlabel("구성비")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(lambda x, _: f"{x:.0%}")
    ax.legend(ncols=5, loc="upper center", bbox_to_anchor=(0.5, -0.08))
    sns.despine(left=True, bottom=True)
    add_source_note(fig, "자료: 경기도 성남시_주택_통계_20250618")
    save_figure(fig, "06_gu_housing_stock_composition.png")

    demand = gu_ref.sort_values("세대수_대비_주택수", ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5.6))
    sns.barplot(
        data=demand,
        x="지역명",
        y="세대수_대비_주택수",
        order=GU_ORDER,
        hue="지역명",
        hue_order=GU_ORDER,
        palette=PALETTE_GU,
        legend=False,
        ax=ax,
    )
    ax.axhline(1, color="#344054", linestyle="--", linewidth=1, alpha=0.7)
    ax.set_title("세대수 대비 주택수", fontsize=18, weight="bold", pad=14)
    ax.set_xlabel("")
    ax.set_ylabel("주택수 / 세대수")
    ax.set_ylim(0, max(1.05, demand["세대수_대비_주택수"].max() * 1.15))
    for container in ax.containers:
        ax.bar_label(container, labels=[f"{v.get_height():.2f}" for v in container], padding=4, fontsize=11, weight="bold")
    sns.despine()
    add_source_note(fig, "1.00에 가까울수록 세대수와 주택수가 비슷함")
    save_figure(fig, "07_gu_housing_supply_per_household.png")


def make_cost_matrix(cost: pd.DataFrame, value_col: str, count_col: str, min_count: int = 10) -> pd.DataFrame:
    data = cost[(cost[value_col].notna()) & (cost[count_col].fillna(0) >= min_count)].copy()
    data["지역"] = data["구"] + " " + data["법정동명"]
    ordered_regions = (
        data.groupby("지역")[value_col]
        .median()
        .sort_values(ascending=False)
        .head(24)
        .index
    )
    matrix = data.pivot_table(index="지역", columns="건축유형", values=value_col, aggfunc="median")
    matrix = matrix.reindex(ordered_regions)
    matrix = matrix[[col for col in TYPE_ORDER if col in matrix.columns]]
    return matrix


def plot_heatmap(matrix: pd.DataFrame, title: str, cbar_label: str, filename: str, cmap: str) -> None:
    if matrix.empty:
        return
    fig_height = max(7, len(matrix) * 0.38)
    fig, ax = plt.subplots(figsize=(9.5, fig_height))
    sns.heatmap(
        matrix,
        cmap=cmap,
        linewidths=0.6,
        linecolor="white",
        annot=True,
        fmt=".0f",
        cbar_kws={"label": cbar_label, "shrink": 0.72},
        ax=ax,
    )
    ax.set_title(title, fontsize=18, weight="bold", pad=14)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="x", rotation=0)
    add_source_note(fig, "거래건수 10건 이상 법정동-유형만 표시")
    save_figure(fig, filename)


def plot_cost_heatmaps(cost: pd.DataFrame) -> None:
    plot_heatmap(
        make_cost_matrix(cost, "매매가_평당_중앙값", "매매_거래건수"),
        "법정동 x 건축유형 매매가 중앙값",
        "만원/평",
        "08_legal_dong_sales_price_heatmap.png",
        "YlGnBu",
    )
    plot_heatmap(
        make_cost_matrix(cost, "전세보증금_평당_중앙값", "전세_거래건수"),
        "법정동 x 건축유형 전세보증금 중앙값",
        "만원/평",
        "09_legal_dong_jeonse_deposit_heatmap.png",
        "PuBuGn",
    )
    plot_heatmap(
        make_cost_matrix(cost, "월세_평당_중앙값", "월세_거래건수"),
        "법정동 x 건축유형 월세 중앙값",
        "만원/평",
        "10_legal_dong_monthly_rent_heatmap.png",
        "YlOrRd",
    )


def plot_transaction_volume(cost: pd.DataFrame) -> None:
    rows = []
    for trade_name, count_col in (("매매", "매매_거래건수"), ("전세", "전세_거래건수"), ("월세", "월세_거래건수")):
        subset = cost[["구", "건축유형", count_col]].copy()
        subset = subset.rename(columns={count_col: "거래건수"})
        subset["거래구분"] = trade_name
        rows.append(subset)
    data = pd.concat(rows, ignore_index=True)
    data = data.groupby(["거래구분", "구", "건축유형"], as_index=False)["거래건수"].sum()
    data["건축유형"] = pd.Categorical(data["건축유형"], categories=TYPE_ORDER, ordered=True)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.6), sharey=True)
    for ax, trade_name in zip(axes, ["매매", "전세", "월세"]):
        subset = data[data["거래구분"] == trade_name]
        sns.barplot(
            data=subset,
            x="건축유형",
            y="거래건수",
            hue="구",
            hue_order=GU_ORDER,
            palette=PALETTE_GU,
            ax=ax,
        )
        ax.set_title(trade_name, fontsize=14, weight="bold")
        ax.set_xlabel("")
        ax.set_ylabel("거래건수" if ax is axes[0] else "")
        ax.tick_params(axis="x", rotation=25)
        ax.yaxis.set_major_formatter(lambda y, _: format_number(y))
        if ax is not axes[-1]:
            ax.get_legend().remove()
    axes[-1].legend(title="", loc="center left", bbox_to_anchor=(1.02, 0.5))
    fig.suptitle("구별/건축유형별 거래량", fontsize=18, weight="bold", y=1.02)
    sns.despine()
    add_source_note(fig, "자료: 국토교통부 실거래가 공개시스템, 2025.5.13-2026.5.12. 2025년 5월과 2026년 5월은 부분월")
    save_figure(fig, "11_transaction_volume_by_gu_and_type.png")


def plot_sales_distribution(sales: pd.DataFrame) -> None:
    data = sales[(sales["매매가_평당_만원"].notna()) & (~sales["가격_이상치_IQR"].fillna(False))].copy()
    data["건축유형"] = pd.Categorical(data["건축유형"], categories=TYPE_ORDER, ordered=True)

    fig, ax = plt.subplots(figsize=(11, 6.5))
    sns.boxplot(
        data=data,
        x="건축유형",
        y="매매가_평당_만원",
        hue="구",
        hue_order=GU_ORDER,
        palette=PALETTE_GU,
        showfliers=False,
        linewidth=1,
        ax=ax,
    )
    ax.set_title("건축유형별 매매가 분포", fontsize=18, weight="bold", pad=14)
    ax.set_xlabel("")
    ax.set_ylabel("만원/평")
    ax.legend(title="", ncols=3, loc="upper center", bbox_to_anchor=(0.5, -0.08))
    sns.despine()
    add_source_note(fig, "IQR 기준 이상치 제외")
    save_figure(fig, "12_sales_price_distribution_by_type.png")


def plot_monthly_rent_scatter(rent: pd.DataFrame) -> None:
    data = rent[
        (rent["전월세구분"] == "월세")
        & rent["보증금_만원"].notna()
        & rent["월세_만원"].notna()
        & (~rent["보증금_이상치_IQR"].fillna(False))
        & (~rent["월세_이상치_IQR"].fillna(False))
    ].copy()
    if len(data) > 7000:
        data = data.sample(7000, random_state=42)

    fig, ax = plt.subplots(figsize=(10, 7))
    sns.scatterplot(
        data=data,
        x="보증금_만원",
        y="월세_만원",
        hue="구",
        hue_order=GU_ORDER,
        style="건축유형",
        palette=PALETTE_GU,
        alpha=0.42,
        s=30,
        linewidth=0,
        ax=ax,
    )
    ax.set_title("월세 거래의 보증금-월세 분포", fontsize=18, weight="bold", pad=14)
    ax.set_xlabel("보증금(만원)")
    ax.set_ylabel("월세(만원)")
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(lambda x, _: format_number(x))
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), title="")
    sns.despine()
    add_source_note(fig, "IQR 기준 이상치 제외, 표본이 큰 경우 7,000건 샘플링")
    save_figure(fig, "13_monthly_rent_deposit_scatter.png")


def plot_monthly_trend(sales: pd.DataFrame, rent: pd.DataFrame) -> None:
    sales_data = sales.copy()
    sales_data["계약월"] = pd.to_datetime(sales_data["계약일자"], errors="coerce").dt.to_period("M").dt.to_timestamp()
    sales_month = (
        sales_data[sales_data["매매가_평당_만원"].notna()]
        .groupby(["계약월", "구"], as_index=False)["매매가_평당_만원"]
        .median()
    )

    rent_data = rent.copy()
    rent_data["계약월"] = pd.to_datetime(rent_data["계약일자"], errors="coerce").dt.to_period("M").dt.to_timestamp()
    rent_month = rent_data.groupby(["계약월", "구", "전월세구분"], as_index=False).size().rename(columns={"size": "거래건수"})

    fig, axes = plt.subplots(2, 1, figsize=(11, 9), sharex=True)
    sns.lineplot(
        data=sales_month,
        x="계약월",
        y="매매가_평당_만원",
        hue="구",
        hue_order=GU_ORDER,
        marker="o",
        palette=PALETTE_GU,
        ax=axes[0],
    )
    axes[0].set_title("월별 매매가 중앙값", fontsize=15, weight="bold")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("만원/평")
    axes[0].legend(title="", ncols=3, loc="upper center", bbox_to_anchor=(0.5, 1.18))

    sns.lineplot(
        data=rent_month,
        x="계약월",
        y="거래건수",
        hue="구",
        hue_order=GU_ORDER,
        style="전월세구분",
        marker="o",
        palette=PALETTE_GU,
        ax=axes[1],
    )
    axes[1].set_title("월별 전월세 거래건수", fontsize=15, weight="bold")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("거래건수")
    axes[1].legend(title="", loc="center left", bbox_to_anchor=(1.02, 0.5))
    fig.suptitle("실거래 월별 추이", fontsize=18, weight="bold", y=1.02)
    sns.despine()
    add_source_note(fig, "자료: 국토교통부 실거래가 공개시스템, 2025.5.13-2026.5.12. 2025년 5월과 2026년 5월은 부분월")
    save_figure(fig, "14_monthly_transaction_trends.png")


def write_readme(created_files: list[str]) -> None:
    lines = [
        "# Python Visualizations",
        "",
        "Tableau 대신 Python에서 바로 확인할 수 있도록 만든 정적 시각화 산출물입니다.",
        "",
        "## 입력 데이터",
        "",
        "- `residential/data/processed/tableau/*.csv`",
        "- `residential/data/raw/Dataset_v1/seongnam_dong.geojson`",
        "",
        "## 산출물",
        "",
    ]
    lines.extend(f"- `{filename}`" for filename in created_files)
    lines.extend(
        [
            "",
            "## 재생성",
            "",
            "```powershell",
            "python .\\residential\\data\\scripts\\make_pretty_visualizations.py",
            "```",
            "",
            "지도 이미지는 `geopandas`가 설치되어 있을 때 생성됩니다.",
        ]
    )
    (OUTPUT_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    setup_theme()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    admin = read_tableau_csv("01_admin_dong_demand.csv")
    cost = read_tableau_csv("02_legal_dong_cost_summary.csv")
    stock_long = read_tableau_csv("gu_housing_stock_long.csv")
    gu_ref = read_tableau_csv("05_gu_demand_and_stock_reference.csv")
    sales = read_tableau_csv("transactions_sales_long.csv")
    rent = read_tableau_csv("transactions_rent_long.csv")

    plot_admin_households(admin)
    plot_admin_demand_scatter(admin)
    plot_admin_maps(admin)
    plot_housing_stock(stock_long, gu_ref)
    plot_cost_heatmaps(cost)
    plot_transaction_volume(cost)
    plot_sales_distribution(sales)
    plot_monthly_rent_scatter(rent)
    plot_monthly_trend(sales, rent)

    created_files = sorted(path.name for path in OUTPUT_DIR.glob("*.png"))
    write_readme(created_files)
    print(f"created {len(created_files)} figures in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
