from __future__ import annotations

import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover - optional output
    plt = None


SCRIPT_DIR = Path(__file__).resolve().parent
TRANSPORT_DIR = SCRIPT_DIR.parents[1]
PROJECT_DIR = SCRIPT_DIR.parents[2]

LOCAL_RAW_DIR = TRANSPORT_DIR / "data" / "raw"
FALLBACK_RAW_DIR = PROJECT_DIR / "data" / "raw"
LOCAL_REF_PATH = TRANSPORT_DIR / "data" / "reference" / "capital_job_axes.csv"
FALLBACK_REF_PATH = PROJECT_DIR / "data" / "reference" / "capital_job_axes.csv"
PROCESSED_ROOT = TRANSPORT_DIR / "data" / "processed"
CLEAN_DIR = PROCESSED_ROOT / "clean"
TABLE_DIR = PROCESSED_ROOT / "tables"
TABLEAU_DIR = PROCESSED_ROOT / "tableau"
FIGURE_DIR = PROCESSED_ROOT / "figures"
MASTER_PATH = PROCESSED_ROOT / "seongnam_transport_master.csv"
MASTER_BY_YEAR_PATH = PROCESSED_ROOT / "seongnam_transport_master_by_year.csv"
CLEAN_MASTER_PATH = CLEAN_DIR / "seongnam_transport_master.csv"
CLEAN_MASTER_BY_YEAR_PATH = CLEAN_DIR / "seongnam_transport_master_by_year.csv"
TABLEAU_MASTER_PATH = TABLEAU_DIR / "seongnam_transport_tableau.csv"
TABLEAU_MASTER_BY_YEAR_PATH = TABLEAU_DIR / "seongnam_transport_tableau_by_year.csv"
PRIORITY_TABLE_PATH = TABLE_DIR / "transport_priority_summary.csv"
GU_SUMMARY_TABLE_PATH = TABLE_DIR / "gu_transport_summary.csv"
YEARLY_SUMMARY_TABLE_PATH = TABLE_DIR / "yearly_transport_summary.csv"
TABLEAU_README_PATH = TABLEAU_DIR / "README.md"

WEEKDAYS = {"월", "화", "수", "목", "금"}
MORNING_HOURS = {6, 7, 8, 9}
MODE_MAP = {
    0: "car",
    1: "bus",
    2: "subway",
    3: "walk",
    4: "express_bus",
    5: "rail",
    6: "air",
    7: "other",
}


def find_subdir_case_insensitive(base_dir: Path, folder_name: str) -> Path | None:
    for child in base_dir.iterdir():
        if child.is_dir() and child.name.lower() == folder_name.lower():
            return child
    return None


def resolve_raw_dir() -> Path:
    local_t13 = find_subdir_case_insensitive(LOCAL_RAW_DIR, "T13") if LOCAL_RAW_DIR.exists() else None
    local_t27 = find_subdir_case_insensitive(LOCAL_RAW_DIR, "T27") if LOCAL_RAW_DIR.exists() else None
    if local_t13 and local_t27:
        return LOCAL_RAW_DIR

    fallback_t13 = (
        find_subdir_case_insensitive(FALLBACK_RAW_DIR, "T13") if FALLBACK_RAW_DIR.exists() else None
    )
    fallback_t27 = (
        find_subdir_case_insensitive(FALLBACK_RAW_DIR, "T27") if FALLBACK_RAW_DIR.exists() else None
    )
    if fallback_t13 and fallback_t27:
        return FALLBACK_RAW_DIR

    raise FileNotFoundError(
        "Raw transport data not found. Place T13/T27 files under transport/data/raw or data/raw."
    )


def resolve_reference_path() -> Path:
    if LOCAL_REF_PATH.exists():
        return LOCAL_REF_PATH
    if FALLBACK_REF_PATH.exists():
        return FALLBACK_REF_PATH
    raise FileNotFoundError(
        "capital_job_axes.csv not found. Place it under transport/data/reference or data/reference."
    )


def extract_year(member_name: str) -> str | None:
    match = re.search(r"_(20\d{2})\d{2}_", member_name)
    return match.group(1) if match else None


def normalize_colname(value: str) -> str:
    return str(value).strip().replace('"', "")


def get_available_years(raw_dir: Path) -> list[str]:
    years: set[str] = set()
    for folder in ["T13", "T27"]:
        source_dir = find_subdir_case_insensitive(raw_dir, folder)
        if source_dir is None:
            continue
        for zip_path in sorted(source_dir.glob("*.zip")):
            with zipfile.ZipFile(zip_path) as archive:
                for member_name in archive.namelist():
                    source_year = extract_year(member_name)
                    if source_year is not None:
                        years.add(source_year)
    return sorted(years)


def read_selected_csvs(
    raw_dir: Path, folder: str, year_prefix: str | None, usecols: list[str]
) -> list[pd.DataFrame]:
    frames: list[pd.DataFrame] = []
    source_dir = find_subdir_case_insensitive(raw_dir, folder)
    if source_dir is None:
        return frames

    for zip_path in sorted(source_dir.glob("*.zip")):
        with zipfile.ZipFile(zip_path) as archive:
            for member_name in archive.namelist():
                source_year = extract_year(member_name)
                if source_year is None:
                    continue
                if year_prefix is not None and source_year != year_prefix:
                    continue
                with archive.open(member_name) as file_obj:
                    df = pd.read_csv(
                        file_obj,
                        encoding="utf-8-sig",
                        skipinitialspace=True,
                        usecols=lambda col: normalize_colname(col) in usecols,
                    )
                df.columns = [normalize_colname(col) for col in df.columns]
                missing = [col for col in usecols if col not in df.columns]
                if missing:
                    raise KeyError(f"{zip_path.name} is missing columns: {missing}")
                trimmed = df[usecols].copy()
                trimmed["source_year"] = source_year
                frames.append(trimmed)
    return frames


def zscore(series: pd.Series) -> pd.Series:
    std = series.std(ddof=0)
    if std == 0 or pd.isna(std):
        return pd.Series(0.0, index=series.index)
    return (series - series.mean()) / std


def load_reference_axes() -> pd.DataFrame:
    ref = pd.read_csv(resolve_reference_path(), encoding="utf-8-sig")
    return ref[["axis_name", "d_mega_nm", "d_cty_nm", "d_admi_nm"]].drop_duplicates()


def aggregate_t27(raw_dir: Path, year_prefix: str | None) -> pd.DataFrame:
    usecols = [
        "DOW",
        "O_TIME_CD",
        "O_ADMI_CD",
        "O_CTY_NM",
        "O_ADMI_NM",
        "PURPOSE",
        "TRANS_GB",
        "DURATION",
        "CNT",
    ]
    pieces = read_selected_csvs(raw_dir, "T27", year_prefix, usecols)
    if not pieces:
        label = year_prefix if year_prefix is not None else "all years"
        raise FileNotFoundError(f"No T27 files found for {label}")

    summaries: list[pd.DataFrame] = []
    for df in pieces:
        df["O_TIME_CD"] = df["O_TIME_CD"].astype(int)
        df["PURPOSE"] = df["PURPOSE"].astype(int)
        df["TRANS_GB"] = df["TRANS_GB"].astype(int)
        df["DURATION"] = df["DURATION"].astype(float)
        df["CNT"] = df["CNT"].astype(float)
        df["source_year"] = df["source_year"].astype(str)
        df = df[
            df["DOW"].isin(WEEKDAYS)
            & df["O_TIME_CD"].isin(MORNING_HOURS)
            & (df["PURPOSE"] == 1)
        ].copy()
        if df.empty:
            continue

        split_city = df["O_CTY_NM"].astype(str).str.split()
        df["gu_name"] = split_city.str[-1]
        df["dong_name"] = df["O_ADMI_NM"].astype(str)
        df["mode"] = df["TRANS_GB"].map(MODE_MAP).fillna("other")
        df["weighted_stay_duration"] = df["DURATION"] * df["CNT"]
        df["short_stay_cnt"] = np.where(df["DURATION"] <= 60, df["CNT"], 0.0)

        grouped = (
            df.groupby(["source_year", "O_ADMI_CD", "gu_name", "dong_name", "mode"], as_index=False)
            .agg(
                commute_cnt=("CNT", "sum"),
                weighted_stay_duration=("weighted_stay_duration", "sum"),
                short_stay_cnt=("short_stay_cnt", "sum"),
            )
        )
        summaries.append(grouped)

    combined = pd.concat(summaries, ignore_index=True)
    return (
        combined.groupby(["source_year", "O_ADMI_CD", "gu_name", "dong_name", "mode"], as_index=False)
        .agg(
            commute_cnt=("commute_cnt", "sum"),
            weighted_stay_duration=("weighted_stay_duration", "sum"),
            short_stay_cnt=("short_stay_cnt", "sum"),
        )
    )


def aggregate_t13(raw_dir: Path, year_prefix: str | None, axes: pd.DataFrame) -> pd.DataFrame:
    usecols = [
        "O_ADMI_CD",
        "O_CTY_NM",
        "O_ADMI_NM",
        "D_MEGA_NM",
        "D_CTY_NM",
        "D_ADMI_NM",
        "PURPOSE",
        "CNT",
    ]
    pieces = read_selected_csvs(raw_dir, "T13", year_prefix, usecols)
    if not pieces:
        label = year_prefix if year_prefix is not None else "all years"
        raise FileNotFoundError(f"No T13 files found for {label}")

    summaries: list[pd.DataFrame] = []
    for df in pieces:
        df["PURPOSE"] = df["PURPOSE"].astype(int)
        df["CNT"] = df["CNT"].astype(float)
        df["source_year"] = df["source_year"].astype(str)
        df = df[df["PURPOSE"] == 1].copy()
        if df.empty:
            continue

        split_city = df["O_CTY_NM"].astype(str).str.split()
        df["gu_name"] = split_city.str[-1]
        df["dong_name"] = df["O_ADMI_NM"].astype(str)
        df = df.merge(
            axes,
            left_on=["D_MEGA_NM", "D_CTY_NM", "D_ADMI_NM"],
            right_on=["d_mega_nm", "d_cty_nm", "d_admi_nm"],
            how="left",
        )
        df["axis_commute_cnt"] = np.where(df["axis_name"].notna(), df["CNT"], 0.0)
        df["seoul_commute_cnt"] = np.where(df["D_MEGA_NM"] == "서울특별시", df["CNT"], 0.0)

        grouped = (
            df.groupby(["source_year", "O_ADMI_CD", "gu_name", "dong_name"], as_index=False)
            .agg(
                axis_commute_cnt=("axis_commute_cnt", "sum"),
                seoul_commute_cnt=("seoul_commute_cnt", "sum"),
                total_od_commute=("CNT", "sum"),
            )
        )
        summaries.append(grouped)

    combined = pd.concat(summaries, ignore_index=True)
    final = (
        combined.groupby(["source_year", "O_ADMI_CD", "gu_name", "dong_name"], as_index=False)
        .agg(
            axis_commute_cnt=("axis_commute_cnt", "sum"),
            seoul_commute_cnt=("seoul_commute_cnt", "sum"),
            total_od_commute=("total_od_commute", "sum"),
        )
    )
    final["axis_commute_share"] = final["axis_commute_cnt"] / final["total_od_commute"]
    final["seoul_commute_share"] = final["seoul_commute_cnt"] / final["total_od_commute"]
    return final


def build_transport_master(year_prefix: str | None = None) -> pd.DataFrame:
    raw_dir = resolve_raw_dir()
    axes = load_reference_axes()
    t27_summary = aggregate_t27(raw_dir, year_prefix)

    mode_summary = (
        t27_summary.pivot_table(
            index=["source_year", "O_ADMI_CD", "gu_name", "dong_name"],
            columns="mode",
            values="commute_cnt",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )

    for col in ["bus", "car", "subway", "walk", "express_bus", "rail", "air", "other"]:
        if col not in mode_summary.columns:
            mode_summary[col] = 0.0

    duration_summary = (
        t27_summary.groupby(["source_year", "O_ADMI_CD", "gu_name", "dong_name"], as_index=False)
        .agg(
            weighted_stay_duration=("weighted_stay_duration", "sum"),
            total_commute=("commute_cnt", "sum"),
            short_stay_cnt=("short_stay_cnt", "sum"),
        )
    )
    duration_summary["avg_stay_duration"] = (
        duration_summary["weighted_stay_duration"] / duration_summary["total_commute"]
    )
    duration_summary["short_stay_share"] = (
        duration_summary["short_stay_cnt"] / duration_summary["total_commute"]
    )
    duration_summary = duration_summary[
        [
            "source_year",
            "O_ADMI_CD",
            "gu_name",
            "dong_name",
            "total_commute",
            "avg_stay_duration",
            "short_stay_share",
        ]
    ]

    master = mode_summary.merge(
        duration_summary,
        on=["source_year", "O_ADMI_CD", "gu_name", "dong_name"],
        how="left",
    )

    axis_summary = aggregate_t13(raw_dir, year_prefix, axes)
    master = master.merge(
        axis_summary[
            [
                "source_year",
                "O_ADMI_CD",
                "gu_name",
                "dong_name",
                "axis_commute_share",
                "seoul_commute_share",
                "total_od_commute",
            ]
        ],
        on=["source_year", "O_ADMI_CD", "gu_name", "dong_name"],
        how="left",
    )

    master["subway_share"] = master["subway"] / master["total_commute"]
    master["bus_share"] = master["bus"] / master["total_commute"]
    master["car_share"] = master["car"] / master["total_commute"]
    master["other_share"] = (
        master[["walk", "express_bus", "rail", "air", "other"]].sum(axis=1) / master["total_commute"]
    )
    master[["axis_commute_share", "seoul_commute_share"]] = master[
        ["axis_commute_share", "seoul_commute_share"]
    ].fillna(0.0)

    master["accessibility_score"] = (
        0.45 * zscore(master["subway_share"])
        + 0.25 * zscore(master["axis_commute_share"])
        + 0.20 * zscore(master["seoul_commute_share"])
        - 0.10 * zscore(master["bus_share"])
    )
    master["vulnerability_score"] = -master["accessibility_score"]
    master["high_demand_low_access"] = (
        zscore(master["total_commute"]) + zscore(master["vulnerability_score"])
    )

    master = master.rename(columns={"O_ADMI_CD": "admi_cd"})
    ordered_cols = [
        "source_year",
        "gu_name",
        "dong_name",
        "admi_cd",
        "total_commute",
        "subway_share",
        "bus_share",
        "car_share",
        "other_share",
        "avg_stay_duration",
        "short_stay_share",
        "axis_commute_share",
        "seoul_commute_share",
        "accessibility_score",
        "vulnerability_score",
        "high_demand_low_access",
        "bus",
        "car",
        "subway",
        "walk",
        "express_bus",
        "rail",
        "air",
        "other",
        "total_od_commute",
    ]
    return master[ordered_cols].sort_values(
        ["source_year", "gu_name", "accessibility_score"], ascending=[True, True, False]
    ).reset_index(drop=True)


def add_weighted_metric(
    base: pd.DataFrame, yearly_master: pd.DataFrame, metric_col: str, weight_col: str
) -> pd.DataFrame:
    temp = yearly_master[["gu_name", "dong_name", "admi_cd"]].copy()
    temp["weighted_value"] = yearly_master[metric_col] * yearly_master[weight_col]
    temp["weight"] = yearly_master[weight_col]
    summarized = (
        temp.groupby(["gu_name", "dong_name", "admi_cd"], as_index=False)[["weighted_value", "weight"]]
        .sum()
    )
    base = base.merge(summarized, on=["gu_name", "dong_name", "admi_cd"], how="left")
    base[metric_col] = np.where(base["weight"] > 0, base["weighted_value"] / base["weight"], 0.0)
    return base.drop(columns=["weighted_value", "weight"])


def collapse_all_years(yearly_master: pd.DataFrame) -> pd.DataFrame:
    aggregate_cols = [
        "total_commute",
        "bus",
        "car",
        "subway",
        "walk",
        "express_bus",
        "rail",
        "air",
        "other",
        "total_od_commute",
    ]
    base = (
        yearly_master.groupby(["gu_name", "dong_name", "admi_cd"], as_index=False)[aggregate_cols]
        .sum()
    )

    for metric_col in ["avg_stay_duration", "short_stay_share"]:
        base = add_weighted_metric(base, yearly_master, metric_col, "total_commute")
    for metric_col in ["axis_commute_share", "seoul_commute_share"]:
        base = add_weighted_metric(base, yearly_master, metric_col, "total_od_commute")

    base["subway_share"] = base["subway"] / base["total_commute"]
    base["bus_share"] = base["bus"] / base["total_commute"]
    base["car_share"] = base["car"] / base["total_commute"]
    base["other_share"] = (
        base[["walk", "express_bus", "rail", "air", "other"]].sum(axis=1) / base["total_commute"]
    )
    base["accessibility_score"] = (
        0.45 * zscore(base["subway_share"])
        + 0.25 * zscore(base["axis_commute_share"])
        + 0.20 * zscore(base["seoul_commute_share"])
        - 0.10 * zscore(base["bus_share"])
    )
    base["vulnerability_score"] = -base["accessibility_score"]
    base["high_demand_low_access"] = (
        zscore(base["total_commute"]) + zscore(base["vulnerability_score"])
    )

    ordered_cols = [
        "gu_name",
        "dong_name",
        "admi_cd",
        "total_commute",
        "subway_share",
        "bus_share",
        "car_share",
        "other_share",
        "avg_stay_duration",
        "short_stay_share",
        "axis_commute_share",
        "seoul_commute_share",
        "accessibility_score",
        "vulnerability_score",
        "high_demand_low_access",
        "bus",
        "car",
        "subway",
        "walk",
        "express_bus",
        "rail",
        "air",
        "other",
        "total_od_commute",
    ]
    return base[ordered_cols].sort_values(
        ["gu_name", "accessibility_score"], ascending=[True, False]
    ).reset_index(drop=True)


def ensure_output_dirs() -> None:
    for path in [PROCESSED_ROOT, CLEAN_DIR, TABLE_DIR, TABLEAU_DIR, FIGURE_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def build_priority_table(master: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "gu_name",
        "dong_name",
        "admi_cd",
        "total_commute",
        "subway_share",
        "axis_commute_share",
        "seoul_commute_share",
        "accessibility_score",
        "high_demand_low_access",
    ]
    return master[columns].sort_values(
        ["high_demand_low_access", "total_commute"], ascending=[False, False]
    ).reset_index(drop=True)


def build_gu_summary(master: pd.DataFrame) -> pd.DataFrame:
    summary = (
        master.groupby("gu_name", as_index=False)
        .agg(
            dong_count=("dong_name", "count"),
            total_commute=("total_commute", "sum"),
            avg_accessibility_score=("accessibility_score", "mean"),
            avg_subway_share=("subway_share", "mean"),
            avg_bus_share=("bus_share", "mean"),
            avg_car_share=("car_share", "mean"),
            avg_axis_commute_share=("axis_commute_share", "mean"),
            avg_seoul_commute_share=("seoul_commute_share", "mean"),
        )
        .sort_values("avg_accessibility_score", ascending=False)
        .reset_index(drop=True)
    )
    return summary


def build_yearly_summary(yearly_master: pd.DataFrame) -> pd.DataFrame:
    summary = (
        yearly_master.groupby("source_year", as_index=False)
        .agg(
            total_commute=("total_commute", "sum"),
            avg_accessibility_score=("accessibility_score", "mean"),
            avg_subway_share=("subway_share", "mean"),
            avg_bus_share=("bus_share", "mean"),
            avg_car_share=("car_share", "mean"),
            avg_axis_commute_share=("axis_commute_share", "mean"),
            avg_seoul_commute_share=("seoul_commute_share", "mean"),
        )
        .sort_values("source_year")
        .reset_index(drop=True)
    )
    return summary


def write_tableau_readme() -> None:
    TABLEAU_README_PATH.write_text(
        "# Tableau Files\n\n"
        "- `seongnam_transport_tableau.csv`: 전체 연도 통합 동 단위 마스터\n"
        "- `seongnam_transport_tableau_by_year.csv`: 연도별 동 단위 마스터\n\n"
        "기본 조인 키는 `gu_name`, `dong_name`, `admi_cd`다.\n",
        encoding="utf-8",
    )


def export_figures(master: pd.DataFrame, gu_summary: pd.DataFrame) -> None:
    if plt is None:
        print("matplotlib not installed; skipped transport figures")
        return

    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False

    priority = build_priority_table(master).head(10).sort_values("high_demand_low_access")
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = priority["dong_name"] + " (" + priority["gu_name"] + ")"
    ax.barh(labels, priority["high_demand_low_access"], color="#D55E00")
    ax.set_title("High Demand, Low Access Priority")
    ax.set_xlabel("high_demand_low_access")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "high_demand_low_access_top10.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(gu_summary))
    width = 0.25
    ax.bar(x - width, gu_summary["avg_subway_share"], width=width, label="subway", color="#0072B2")
    ax.bar(x, gu_summary["avg_bus_share"], width=width, label="bus", color="#E69F00")
    ax.bar(x + width, gu_summary["avg_car_share"], width=width, label="car", color="#666666")
    ax.set_xticks(x)
    ax.set_xticklabels(gu_summary["gu_name"])
    ax.set_ylabel("average mode share")
    ax.set_title("Mode Share by Gu")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "mode_share_by_gu.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(master["total_commute"], master["accessibility_score"], color="#009E73", alpha=0.8)
    for _, row in build_priority_table(master).head(5).iterrows():
        ax.annotate(row["dong_name"], (row["total_commute"], row["accessibility_score"]), fontsize=8)
    ax.set_title("Commute Demand vs Accessibility")
    ax.set_xlabel("total_commute")
    ax.set_ylabel("accessibility_score")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "commute_vs_accessibility.png", dpi=200)
    plt.close(fig)


def export_supporting_outputs(master: pd.DataFrame, yearly_master: pd.DataFrame) -> None:
    ensure_output_dirs()

    priority = build_priority_table(master)
    gu_summary = build_gu_summary(master)
    yearly_summary = build_yearly_summary(yearly_master)

    master.to_csv(CLEAN_MASTER_PATH, index=False, encoding="utf-8-sig")
    yearly_master.to_csv(CLEAN_MASTER_BY_YEAR_PATH, index=False, encoding="utf-8-sig")
    master.to_csv(TABLEAU_MASTER_PATH, index=False, encoding="utf-8-sig")
    yearly_master.to_csv(TABLEAU_MASTER_BY_YEAR_PATH, index=False, encoding="utf-8-sig")
    priority.to_csv(PRIORITY_TABLE_PATH, index=False, encoding="utf-8-sig")
    gu_summary.to_csv(GU_SUMMARY_TABLE_PATH, index=False, encoding="utf-8-sig")
    yearly_summary.to_csv(YEARLY_SUMMARY_TABLE_PATH, index=False, encoding="utf-8-sig")
    write_tableau_readme()
    export_figures(master, gu_summary)


def main() -> None:
    ensure_output_dirs()
    raw_dir = resolve_raw_dir()
    years = get_available_years(raw_dir)
    yearly_master = pd.concat(
        [build_transport_master(year_prefix=year) for year in years],
        ignore_index=True,
    )
    all_years_master = collapse_all_years(yearly_master)

    yearly_master.to_csv(MASTER_BY_YEAR_PATH, index=False, encoding="utf-8-sig")
    all_years_master.to_csv(MASTER_PATH, index=False, encoding="utf-8-sig")
    export_supporting_outputs(all_years_master, yearly_master)

    print(f"Saved {len(all_years_master)} rows to {MASTER_PATH}")
    print(f"Saved {len(yearly_master)} rows to {MASTER_BY_YEAR_PATH}")
    print(f"Included years: {years}")
    print(all_years_master.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
