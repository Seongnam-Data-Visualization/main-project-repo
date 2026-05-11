"""private_data 신규 기업(new) CSV → seongnam_new_corp_by_dong.csv."""

from pathlib import Path

import pandas as pd

PRIVATE_ROOT = Path(__file__).resolve().parent.parent / "raw" / "private_data"
OUT_CSV = Path(__file__).resolve().parent.parent / "processed" / "seongnam_new_corp_by_dong.csv"


def _corp4_dir() -> Path:
    for p in PRIVATE_ROOT.iterdir():
        if p.is_dir() and p.name.startswith("4.") and "new" in p.name.lower():
            return p
    raise FileNotFoundError(f"신규 기업(new) 폴더를 찾을 수 없습니다: {PRIVATE_ROOT}")


def main() -> None:
    corp_dir = _corp4_dir()
    paths = sorted(corp_dir.glob("*.csv"))
    if not paths:
        raise SystemExit(f"CSV가 없습니다: {corp_dir}")

    chunks = [pd.read_csv(p, encoding="utf-8-sig") for p in paths]
    df = pd.concat(chunks, ignore_index=True)

    df = df.loc[df["sigun_nm"].astype(str).str.startswith("성남시", na=False)].copy()

    latest = int(df["stdr_ym"].max())
    df = df.loc[df["stdr_ym"].astype(int) == latest].copy()

    df["ncr_crp_comp_cn"] = pd.to_numeric(df["ncr_crp_comp_cn"], errors="coerce").fillna(0)

    out = (
        df.groupby("admi_nm", as_index=False)["ncr_crp_comp_cn"]
        .sum()
        .sort_values("admi_nm")
        .reset_index(drop=True)
    )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print(f"기준월(stdr_ym): {latest}")
    print(f"저장: {OUT_CSV}")
    print(f"행 수: {len(out)}")
    print("\n샘플 5행:")
    with pd.option_context("display.max_columns", None, "display.width", 100):
        print(out.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
