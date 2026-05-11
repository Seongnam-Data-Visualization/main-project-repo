"""2024 연간 자료에서 성남 3개 구 동별 종사자 집계 → seongnam_workers_by_dong.csv."""

from pathlib import Path

import numpy as np
import pandas as pd

RAW_CSV = Path(__file__).resolve().parent.parent / "raw" / "2024_연간자료_20260511_84850.csv"
OUT_CSV = Path(__file__).resolve().parent.parent / "processed" / "seongnam_workers_by_dong.csv"

COL_NAMES = [
    "행정구역시군구코드",
    "행정구역읍면동코드",
    "주사업_산업대분류코드",
    "주사업_산업중분류코드",
    "자영업_합계종사자수",
    "상용근로_합계종사자수",
    "합계종사자수",
]

GU_MAP = {21: "수정구", 22: "중원구", 23: "분당구"}
CHUNK = 400_000


def main() -> None:
    chunks: list[pd.DataFrame] = []
    for part in pd.read_csv(
        RAW_CSV,
        encoding="cp949",
        header=None,
        names=COL_NAMES,
        chunksize=CHUNK,
        low_memory=False,
    ):
        sub = part.loc[part["행정구역시군구코드"].isin((21, 22, 23))].copy()
        if not sub.empty:
            chunks.append(sub)
    if not chunks:
        raise SystemExit("필터 후 데이터가 없습니다.")
    df = pd.concat(chunks, ignore_index=True)

    df["gu_name"] = df["행정구역시군구코드"].map(GU_MAP)

    for c in ("자영업_합계종사자수", "상용근로_합계종사자수", "합계종사자수"):
        df[c] = df[c].replace("*", pd.NA)
        df[c] = pd.to_numeric(df[c], errors="coerce").astype(float)

    grp_keys = ["gu_name", "행정구역읍면동코드"]
    summary = (
        df.groupby(grp_keys, as_index=False)
        .agg(
            total_workers=("합계종사자수", "sum"),
            regular_workers=("상용근로_합계종사자수", "sum"),
            self_employed=("자영업_합계종사자수", "sum"),
        )
    )
    tw = summary["total_workers"].to_numpy(dtype=float)
    se = summary["self_employed"].to_numpy(dtype=float)
    summary["self_employed_ratio"] = np.where(tw > 0, se / tw, np.nan)

    pivot = pd.pivot_table(
        df,
        index=grp_keys,
        columns="주사업_산업대분류코드",
        values="합계종사자수",
        aggfunc="sum",
        fill_value=0,
    )
    pivot.columns = [f"industry_{c}" for c in pivot.columns.astype(str)]
    pivot = pivot.reset_index()
    ind_cols = sorted([c for c in pivot.columns if c.startswith("industry_")])

    out = summary.merge(pivot, on=grp_keys, how="left")
    for c in ind_cols:
        out[c] = out[c].fillna(0).astype(float)

    ordered = [
        "gu_name",
        "행정구역읍면동코드",
        "total_workers",
        "regular_workers",
        "self_employed",
        "self_employed_ratio",
    ] + ind_cols
    out = out[ordered]

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print(f"행 수: {len(out)}")
    print("컬럼 목록:")
    print(list(out.columns))
    print("\n샘플 5행:")
    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(out.head(5).to_string())


if __name__ == "__main__":
    main()
