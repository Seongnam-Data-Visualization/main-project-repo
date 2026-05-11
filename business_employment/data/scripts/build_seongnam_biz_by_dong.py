"""성남시 사업체 데이터를 동·구 단위로 집계해 seongnam_biz_by_dong.csv 생성."""

from pathlib import Path

import pandas as pd

_DATA = Path(__file__).resolve().parent.parent
RAW_CSV = _DATA / "raw" / "업종별 사업체 현황_2023년.csv"
OUT_CSV = _DATA / "processed" / "seongnam_biz_by_dong.csv"
CHUNK_SIZE = 100_000


def _extract_gu(행정구역명: str) -> str | float:
    if pd.isna(행정구역명):
        return pd.NA
    for part in str(행정구역명).strip().split():
        if part.endswith("구"):
            return part
    return pd.NA


def main() -> None:
    chunks: list[pd.DataFrame] = []
    for chunk in pd.read_csv(RAW_CSV, encoding="cp949", chunksize=CHUNK_SIZE):
        sub = chunk.loc[chunk["시군명"] == "성남시"].copy()
        if not sub.empty:
            chunks.append(sub)
    if not chunks:
        raise SystemExit("성남시 행이 없습니다. 시군명·파일 경로를 확인하세요.")
    df = pd.concat(chunks, ignore_index=True)

    df["dong_name"] = df["행정구역명"].astype(str).str.strip().str.split().str[-1]
    df["gu_name"] = df["행정구역명"].map(_extract_gu)

    df["_it"] = df["산업대분류명"].astype(str).str.contains(
        "정보|통신|출판", regex=True, na=False
    )

    summary = (
        df.groupby("dong_name", as_index=False)
        .agg(
            gu_name=("gu_name", lambda s: s.mode().iloc[0] if len(s.mode()) else s.iloc[0]),
            total_biz=("dong_name", "count"),
            _it_sum=("_it", "sum"),
        )
    )
    summary["it_ratio"] = summary["_it_sum"] / summary["total_biz"]
    summary = summary.drop(columns=["_it_sum"])

    pivot = pd.crosstab(df["dong_name"], df["산업대분류명"])
    pivot = pivot.reset_index()
    pivot_cols = [c for c in pivot.columns if c != "dong_name"]

    out = summary.merge(pivot, on="dong_name", how="left")
    for c in pivot_cols:
        out[c] = out[c].fillna(0).astype(int)

    ordered = ["gu_name", "dong_name", "total_biz", "it_ratio"] + sorted(pivot_cols)
    out = out[ordered]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(out)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
