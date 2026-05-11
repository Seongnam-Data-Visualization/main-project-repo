"""private_data 법인 기업(cnt) CSV → seongnam_corp_by_dong.csv."""

from pathlib import Path

import numpy as np
import pandas as pd

PRIVATE_ROOT = Path(__file__).resolve().parent.parent / "raw" / "private_data"
OUT_CSV = Path(__file__).resolve().parent.parent / "processed" / "seongnam_corp_by_dong.csv"

COUNT_COLS = [
    "vpap_comp_cn",
    "kosdaq_comp_cn",
    "konex_comp_cn",
    "oc_comp_cn",
    "co_ctx_comp_cn",
]


def _corp3_dir() -> Path:
    for p in PRIVATE_ROOT.iterdir():
        if p.is_dir() and p.name.startswith("3.") and "cnt" in p.name:
            return p
    raise FileNotFoundError(f"법인 기업(cnt) 폴더를 찾을 수 없습니다: {PRIVATE_ROOT}")


def main() -> None:
    corp_dir = _corp3_dir()
    paths = sorted(corp_dir.glob("*.csv"))
    if not paths:
        raise SystemExit(f"CSV가 없습니다: {corp_dir}")

    print("1) 파일 목록:")
    for p in paths:
        print(f"   {p.name}")

    chunks: list[pd.DataFrame] = []
    for p in paths:
        chunks.append(pd.read_csv(p, encoding="utf-8-sig"))
    df = pd.concat(chunks, ignore_index=True)

    print("\n2) 컬럼 목록:")
    print(list(df.columns))

    if "admi_nm" not in df.columns:
        raise SystemExit("admi_nm 컬럼이 없습니다.")
    print("\n   admi_nm 컬럼: 있음")

    if "sigun_nm" not in df.columns:
        raise SystemExit("sigun_nm 컬럼이 없습니다.")

    exact = (df["sigun_nm"].astype(str) == "성남시").sum()
    print(f"\n   sigun_nm == '성남시' 일치 행: {exact}건 (데이터는 '성남시 분당구' 등 구 단위)")
    # 원본은 '성남시 분당구' 등 — 성남시 3개 구 전체
    mask_sn = df["sigun_nm"].astype(str).str.startswith("성남시", na=False)
    n_before = len(df)
    df = df.loc[mask_sn].copy()
    print(f"\n   sigun_nm 성남시* 필터: {n_before} → {len(df)} 행")

    if "stdr_ym" in df.columns:
        latest = int(df["stdr_ym"].max())
        df = df.loc[df["stdr_ym"].astype(int) == latest].copy()
        print(f"   최신 기준월(stdr_ym)만 사용: {latest} ({len(df)} 행)")

    for c in COUNT_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["row_total"] = df[COUNT_COLS].sum(axis=1)
    df["_it"] = df["induty_pri_nm"].astype(str).str.contains(
        "정보|통신", regex=True, na=False
    )
    df["_it_cnt"] = np.where(df["_it"], df["row_total"], 0)

    out = (
        df.groupby("admi_nm", as_index=False)
        .agg(total_corp=("row_total", "sum"), it_corp=("_it_cnt", "sum"))
    )
    tc = out["total_corp"].to_numpy(dtype=float)
    ic = out["it_corp"].to_numpy(dtype=float)
    out["it_ratio"] = np.where(tc > 0, ic / tc, np.nan)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print(f"\n4) 저장: {OUT_CSV}")
    print(f"\n5) 행 수: {len(out)}")
    print("\n   샘플 5행:")
    with pd.option_context("display.max_columns", None, "display.width", 120):
        print(out.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
