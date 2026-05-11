"""private_data 기업 이전 통계(nps_move_cnt) → seongnam_corp_move_by_dong.csv."""

from pathlib import Path

import pandas as pd

PRIVATE_ROOT = Path(__file__).resolve().parent.parent / "raw" / "private_data"
OUT_CSV = Path(__file__).resolve().parent.parent / "processed" / "seongnam_corp_move_by_dong.csv"


def _corp5_dir() -> Path:
    for p in PRIVATE_ROOT.iterdir():
        if p.is_dir() and "nps_move" in p.name.lower():
            return p
    raise FileNotFoundError(f"nps_move_cnt 폴더를 찾을 수 없습니다: {PRIVATE_ROOT}")


def main() -> None:
    corp_dir = _corp5_dir()
    paths = sorted(corp_dir.glob("*.csv"))
    if not paths:
        raise SystemExit(f"CSV가 없습니다: {corp_dir}")

    chunks = [pd.read_csv(p, encoding="utf-8-sig") for p in paths]
    df = pd.concat(chunks, ignore_index=True)
    print(f"1) CSV {len(paths)}개 concat → {len(df)} 행")

    print("\n2) 컬럼 목록:")
    print(list(df.columns))
    print(
        "\n   전출: out_sido_nm, out_sigun_nm, out_admi_nm / "
        "전입: in_sido, in_sigun_nm, in_admi_nm / 건수: comp_cn"
    )

    latest = int(df["stdr_ym"].max())
    df = df.loc[df["stdr_ym"].astype(int) == latest].copy()
    print(f"\n   기준월(stdr_ym) 최신만 사용: {latest} ({len(df)} 행)")

    df["comp_cn"] = pd.to_numeric(df["comp_cn"], errors="coerce").fillna(0)

    out_sn = df["out_sigun_nm"].astype(str).str.startswith("성남시", na=False)
    in_sn = df["in_sigun_nm"].astype(str).str.startswith("성남시", na=False)

    corp_out = (
        df.loc[out_sn & df["out_admi_nm"].notna() & (df["out_admi_nm"].astype(str).str.strip() != "")]
        .groupby("out_admi_nm", as_index=False)["comp_cn"]
        .sum()
        .rename(columns={"out_admi_nm": "admi_nm", "comp_cn": "corp_out"})
    )
    corp_in = (
        df.loc[in_sn & df["in_admi_nm"].notna() & (df["in_admi_nm"].astype(str).str.strip() != "")]
        .groupby("in_admi_nm", as_index=False)["comp_cn"]
        .sum()
        .rename(columns={"in_admi_nm": "admi_nm", "comp_cn": "corp_in"})
    )

    out = corp_out.merge(corp_in, on="admi_nm", how="outer")
    out["corp_out"] = out["corp_out"].fillna(0).astype(int)
    out["corp_in"] = out["corp_in"].fillna(0).astype(int)
    out["순유입"] = out["corp_in"] - out["corp_out"]
    out = out.sort_values("admi_nm").reset_index(drop=True)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print(f"\n5) 저장: {OUT_CSV}")
    print(f"\n6) 행 수: {len(out)}")
    print("\n   샘플 5행:")
    with pd.option_context("display.max_columns", None, "display.width", 120):
        print(out.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
