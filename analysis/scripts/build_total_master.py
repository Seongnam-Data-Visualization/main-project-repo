"""주거·고용·교통 요약을 gu_name + dong_name으로 병합 → seongnam_total_master.csv."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]

RESIDENTIAL_PATH = REPO_ROOT / "residential/data/processed/clean/residential_summary.csv"
EMPLOYMENT_PATH = REPO_ROOT / "business_employment/data/processed/seongnam_employment_master.csv"
TRANSPORT_PATH = REPO_ROOT / "transport/transport/data/processed/seongnam_transport_master.csv"

OUT_DIR = REPO_ROOT / "analysis/data"
OUT_CSV = OUT_DIR / "seongnam_total_master.csv"

RESIDENTIAL_COLS = [
    "gu_name",
    "dong_name",
    "ADM_CD",
    "세대수",
    "총인구",
    "생산가능인구_19_64세",
    "생산가능인구비율_19_64세",
    "65세이상인구비율",
    "매매가_평당_중앙값",
    "전세보증금_평당_중앙값",
    "월세_평당_중앙값",
]

EMPLOYMENT_COLS = [
    "gu_name",
    "dong_name",
    "total_workers",
    "regular_workers",
    "self_employed",
    "self_employed_ratio",
    "total_biz",
    "total_corp",
    "new_corp",
    "corp_in",
    "corp_out",
    "순유입",
]

TRANSPORT_COLS = [
    "gu_name",
    "dong_name",
    "total_commute",
    "subway_share",
    "bus_share",
    "car_share",
    "axis_commute_share",
    "seoul_commute_share",
    "accessibility_score",
    "vulnerability_score",
    "high_demand_low_access",
]

EXPECTED_ROWS = 50


def load_residential() -> pd.DataFrame:
    df = pd.read_csv(RESIDENTIAL_PATH, encoding="utf-8-sig")
    df = df.rename(columns={"구": "gu_name", "행정동명": "dong_name"})
    missing = [c for c in RESIDENTIAL_COLS if c not in df.columns]
    if missing:
        raise KeyError(f"residential_summary.csv missing columns: {missing}")
    return df[RESIDENTIAL_COLS].copy()


def load_employment() -> pd.DataFrame:
    df = pd.read_csv(EMPLOYMENT_PATH, encoding="utf-8-sig")
    missing = [c for c in EMPLOYMENT_COLS if c not in df.columns]
    if missing:
        raise KeyError(f"seongnam_employment_master.csv missing columns: {missing}")
    return df[EMPLOYMENT_COLS].copy()


def load_transport() -> pd.DataFrame:
    df = pd.read_csv(TRANSPORT_PATH, encoding="utf-8-sig")
    missing = [c for c in TRANSPORT_COLS if c not in df.columns]
    if missing:
        raise KeyError(f"seongnam_transport_master.csv missing columns: {missing}")
    return df[TRANSPORT_COLS].copy()


def main() -> None:
    r = load_residential()
    e = load_employment()
    t = load_transport()

    merged = r.merge(e, on=["gu_name", "dong_name"], how="inner")
    merged = merged.merge(t, on=["gu_name", "dong_name"], how="inner")

    n = len(merged)
    if n != EXPECTED_ROWS:
        raise ValueError(f"Expected {EXPECTED_ROWS} rows after inner merge, got {n}")

    na_cols = [c for c in merged.columns if merged[c].isna().any()]
    if na_cols:
        print("결측치가 있는 컬럼:")
        for c in na_cols:
            print(f"  - {c}: {merged[c].isna().sum()}건")
    else:
        print("결측치가 있는 컬럼: 없음")

    print(f"\n병합 후 행 수: {n}")
    print("\n컬럼 목록 (전체):")
    print(list(merged.columns))

    print("\n샘플 3행:")
    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(merged.head(3).to_string(index=False))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n저장 완료: {OUT_CSV}")


if __name__ == "__main__":
    main()
