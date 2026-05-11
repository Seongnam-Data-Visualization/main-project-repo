from __future__ import annotations

import csv
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "Dataset_v1"
PROCESSED_DIR = ROOT / "data" / "processed"
TABLE_DIR = ROOT / "output" / "tables"
FIGURE_DIR = ROOT / "output" / "figures"
TABLEAU_DIR = ROOT / "output" / "tableau"
PYEONG_M2 = 3.3058

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


TYPE_MAP = {
    "아파트": "아파트",
    "단독": "단독_다가구",
    "단독주택": "단독_다가구",
    "다가구": "단독_다가구",
    "다가구주택": "단독_다가구",
    "단독다가구": "단독_다가구",
    "연립": "연립_다세대",
    "연립주택": "연립_다세대",
    "다세대": "연립_다세대",
    "다세대주택": "연립_다세대",
    "연립다세대": "연립_다세대",
    "오피스텔": "오피스텔",
}


def ensure_dirs() -> None:
    for path in (PROCESSED_DIR, TABLE_DIR, FIGURE_DIR, TABLEAU_DIR):
        path.mkdir(parents=True, exist_ok=True)


def read_csv_auto(path: Path, **kwargs) -> pd.DataFrame:
    for encoding in ("utf-8-sig", "cp949", "euc-kr", "utf-8"):
        try:
            return pd.read_csv(path, encoding=encoding, **kwargs)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path, **kwargs)


def to_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False).str.strip().replace({"": None, "-": None}),
        errors="coerce",
    )


def normalize_region_name(value: object) -> str:
    return re.sub(r"\s+", "", str(value).strip())


def normalize_housing_type(value: object) -> str:
    key = normalize_region_name(value).replace("주택", "주택")
    return TYPE_MAP.get(key, TYPE_MAP.get(key.replace(" ", ""), key or "기타"))


def estimate_legal_dong_from_admin(admin_dong: object) -> str:
    dong = normalize_region_name(admin_dong)
    return re.sub(r"(\D+)\d+동$", r"\1동", dong)


def load_admin_geo_lookup() -> pd.DataFrame:
    geojson_path = DATA_DIR / "seongnam_dong.geojson"
    if not geojson_path.exists():
        raise FileNotFoundError(f"Missing geojson: {geojson_path}")

    with geojson_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    records = []
    for feature in payload.get("features", []):
        props = feature.get("properties", {})
        admin_dong = normalize_region_name(props.get("동", props.get("ADM_NM", "")))
        adm_cd = str(props.get("ADM_CD", "")).strip()
        records.append(
            {
                "ADM_CD": adm_cd,
                "행정동명": admin_dong,
                "법정동추정명": estimate_legal_dong_from_admin(admin_dong),
                "지도기준일자": props.get("BASE_DATE"),
            }
        )

    lookup = pd.DataFrame(records).drop_duplicates(subset=["ADM_CD", "행정동명"])
    lookup.to_csv(PROCESSED_DIR / "admin_dong_geo_lookup.csv", index=False, encoding="utf-8-sig")
    lookup.to_csv(TABLEAU_DIR / "admin_dong_geo_lookup.csv", index=False, encoding="utf-8-sig")
    return lookup


def infer_type_from_filename(path: Path) -> str:
    name = path.name
    if "아파트" in name:
        return "아파트"
    if "단독다가구" in name:
        return "단독_다가구"
    if "연립다세대" in name:
        return "연립_다세대"
    if "오피스텔" in name:
        return "오피스텔"
    return "기타"


def infer_trade_kind(path: Path) -> str:
    return "매매" if "(매매)" in path.name else "전월세"


def split_sigungudong(series: pd.Series) -> pd.DataFrame:
    rows = []
    for value in series.fillna(""):
        parts = str(value).split()
        gu = next((part for part in parts if part.endswith("구")), None)
        dong = parts[-1] if parts else None
        rows.append({"구": gu, "읍면동": dong})
    return pd.DataFrame(rows, index=series.index)


def parse_contract_date(df: pd.DataFrame) -> pd.Series:
    year_month = df["계약년월"].astype(str).str.replace(".0", "", regex=False).str.zfill(6)
    day = df["계약일"].astype(str).str.replace(".0", "", regex=False).str.zfill(2)
    return pd.to_datetime(year_month + day, format="%Y%m%d", errors="coerce")


def find_transaction_header(path: Path) -> tuple[int, str]:
    for encoding in ("cp949", "utf-8-sig", "euc-kr", "utf-8"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                for row_idx, row in enumerate(csv.reader(handle)):
                    if row and row[0] == "NO":
                        return row_idx, encoding
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not find transaction header in {path}")


def read_transaction_csv(path: Path) -> pd.DataFrame:
    header_row, encoding = find_transaction_header(path)
    return pd.read_csv(path, encoding=encoding, skiprows=header_row)


def add_iqr_outlier_flag(df: pd.DataFrame, value_col: str, group_col: str = "건축유형") -> pd.Series:
    flags = pd.Series(False, index=df.index)
    for _, idx in df.groupby(group_col).groups.items():
        values = df.loc[idx, value_col].dropna()
        if len(values) < 8:
            continue
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        flags.loc[idx] = (df.loc[idx, value_col] < lower) | (df.loc[idx, value_col] > upper)
    return flags


def clean_transactions() -> tuple[pd.DataFrame, pd.DataFrame]:
    sales_frames = []
    rent_frames = []

    for path in sorted(DATA_DIR.glob("*실거래가*.csv")):
        raw = read_transaction_csv(path)
        kind = infer_trade_kind(path)
        base_type = infer_type_from_filename(path)
        region = split_sigungudong(raw["시군구"])
        raw = pd.concat([raw, region], axis=1)
        raw["계약일자"] = parse_contract_date(raw)
        raw["소스파일"] = path.name

        if "주택유형" in raw.columns:
            raw["건축유형"] = raw["주택유형"].fillna(base_type).map(normalize_housing_type)
        else:
            raw["건축유형"] = base_type

        if kind == "매매":
            area_col = "전용면적(㎡)" if "전용면적(㎡)" in raw.columns else "연면적(㎡)"
            raw["면적기준"] = area_col
            raw["전용면적_m2"] = to_number(raw[area_col])
            raw["거래금액_만원"] = to_number(raw["거래금액(만원)"])
            raw["평수"] = raw["전용면적_m2"] / PYEONG_M2
            raw["매매가_평당_만원"] = raw["거래금액_만원"] / raw["평수"]
            raw["매매가_m2당_만원"] = raw["거래금액_만원"] / raw["전용면적_m2"]
            cols = [
                "계약일자",
                "시군구",
                "구",
                "읍면동",
                "건축유형",
                "거래금액_만원",
                "전용면적_m2",
                "평수",
                "매매가_평당_만원",
                "매매가_m2당_만원",
                "건축년도",
                "층",
                "면적기준",
                "소스파일",
            ]
            clean = raw[[col for col in cols if col in raw.columns]].copy()
            clean = clean[(clean["거래금액_만원"] > 0) & (clean["전용면적_m2"] > 0)]
            sales_frames.append(clean)
        else:
            area_col = "전용면적(㎡)" if "전용면적(㎡)" in raw.columns else "계약면적(㎡)"
            raw["면적기준"] = area_col
            raw["전용면적_m2"] = to_number(raw[area_col])
            raw["보증금_만원"] = to_number(raw["보증금(만원)"])
            raw["월세_만원"] = to_number(raw["월세금(만원)"])
            raw["평수"] = raw["전용면적_m2"] / PYEONG_M2
            raw["보증금_평당_만원"] = raw["보증금_만원"] / raw["평수"]
            raw["월세_평당_만원"] = raw["월세_만원"] / raw["평수"]
            cols = [
                "계약일자",
                "시군구",
                "구",
                "읍면동",
                "건축유형",
                "전월세구분",
                "보증금_만원",
                "월세_만원",
                "전용면적_m2",
                "평수",
                "보증금_평당_만원",
                "월세_평당_만원",
                "건축년도",
                "층",
                "면적기준",
                "소스파일",
            ]
            clean = raw[[col for col in cols if col in raw.columns]].copy()
            clean = clean[(clean["전용면적_m2"] > 0) & (clean["보증금_만원"] >= 0)]
            rent_frames.append(clean)

    sales = pd.concat(sales_frames, ignore_index=True) if sales_frames else pd.DataFrame()
    rent = pd.concat(rent_frames, ignore_index=True) if rent_frames else pd.DataFrame()

    if not sales.empty:
        sales["가격_이상치_IQR"] = add_iqr_outlier_flag(sales, "매매가_평당_만원")
    if not rent.empty:
        rent["보증금_이상치_IQR"] = add_iqr_outlier_flag(rent, "보증금_평당_만원")
        rent["월세_이상치_IQR"] = add_iqr_outlier_flag(rent[rent["전월세구분"] == "월세"], "월세_평당_만원").reindex(
            rent.index, fill_value=False
        )

    sales.to_csv(PROCESSED_DIR / "sales_clean.csv", index=False, encoding="utf-8-sig")
    rent.to_csv(PROCESSED_DIR / "rent_clean.csv", index=False, encoding="utf-8-sig")
    return sales, rent


def column_index(cell_ref: str) -> int:
    letters = re.match(r"([A-Z]+)", cell_ref).group(1)
    number = 0
    for char in letters:
        number = number * 26 + ord(char) - ord("A") + 1
    return number - 1


def read_xlsx_first_sheet_rows(path: Path) -> list[list[str]]:
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("a:si", ns):
                shared.append("".join(text.text or "" for text in item.findall(".//a:t", ns)))

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relmap = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
        first_sheet = workbook.findall("a:sheets/a:sheet", ns)[0]
        rid = first_sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        sheet_path = "xl/" + relmap[rid].lstrip("/")
        sheet = ET.fromstring(archive.read(sheet_path))

        rows = []
        for row in sheet.findall("a:sheetData/a:row", ns):
            values: list[str] = []
            for cell in row.findall("a:c", ns):
                idx = column_index(cell.attrib["r"])
                while len(values) <= idx:
                    values.append("")
                value = ""
                node = cell.find("a:v", ns)
                if node is not None and node.text is not None:
                    value = node.text
                    if cell.attrib.get("t") == "s":
                        value = shared[int(value)]
                elif cell.attrib.get("t") == "inlineStr":
                    value = "".join(text.text or "" for text in cell.findall(".//a:t", ns))
                values[idx] = value
            rows.append(values)
        return rows


def clean_households() -> pd.DataFrame:
    xlsx_files = sorted(DATA_DIR.glob("*.xlsx"))
    if not xlsx_files:
        raise FileNotFoundError("No household xlsx file found in Dataset_v1")

    rows = read_xlsx_first_sheet_rows(xlsx_files[0])
    records = []
    current_gu = None
    for row in rows:
        if len(row) < 11:
            continue
        name = str(row[0]).strip()
        if not name or name == "합   계":
            continue
        if name.startswith("성남시") and name.endswith("구"):
            current_gu = name.replace("성남시", "").strip()
            continue
        if current_gu is None:
            continue
        total_population = pd.to_numeric(str(row[1]).replace(",", ""), errors="coerce")
        adult_19_plus = pd.to_numeric(str(row[4]).replace(",", ""), errors="coerce")
        senior_65_plus = pd.to_numeric(str(row[7]).replace(",", ""), errors="coerce")
        households = pd.to_numeric(str(row[10]).replace(",", ""), errors="coerce")
        records.append(
            {
                "행정동코드": pd.NA,
                "구": current_gu,
                "행정동명": normalize_region_name(name),
                "기준연월": "2026-03",
                "세대수": households,
                "총인구": total_population,
                "19세이상인구": adult_19_plus,
                "65세이상인구": senior_65_plus,
                "생산가능인구_19_64세": adult_19_plus - senior_65_plus,
            }
        )

    households_df = pd.DataFrame(records)
    geo_lookup = load_admin_geo_lookup()
    households_df = households_df.merge(geo_lookup, on="행정동명", how="left")
    households_df["행정동코드"] = households_df["ADM_CD"]
    households_df["법정동추정명"] = households_df["법정동추정명"].fillna(
        households_df["행정동명"].map(estimate_legal_dong_from_admin)
    )
    households_df = households_df[
        [
            "행정동코드",
            "ADM_CD",
            "구",
            "행정동명",
            "법정동추정명",
            "지도기준일자",
            "기준연월",
            "세대수",
            "총인구",
            "19세이상인구",
            "65세이상인구",
            "생산가능인구_19_64세",
        ]
    ]
    households_df.to_csv(PROCESSED_DIR / "households_clean.csv", index=False, encoding="utf-8-sig")
    households_df.to_csv(TABLEAU_DIR / "admin_dong_households.csv", index=False, encoding="utf-8-sig")
    return households_df


def clean_housing_stock() -> tuple[pd.DataFrame, pd.DataFrame]:
    stock_path = next(DATA_DIR.glob("*주택_통계*.csv"))
    raw = read_csv_auto(stock_path)
    num_cols = [col for col in raw.columns if col not in ("구분", "데이터기준일자")]
    for col in num_cols:
        raw[col] = to_number(raw[col])

    summary = pd.DataFrame(
        {
            "지역코드": pd.NA,
            "구": raw["구분"],
            "지역명": raw["구분"],
            "기준연도": pd.to_datetime(raw["데이터기준일자"]).dt.year,
            "아파트수": raw["아파트"],
            "단독_다가구수": raw["단독일반"] + raw["다가구주택 호수기준"],
            "연립_다세대수": raw["연립주택"] + raw["다세대 주택"],
            "오피스텔수": pd.NA,
            "기타수": raw["영업겸용"] + raw["비거주용 건물내 주택"],
        }
    )
    summary = summary[summary["구"].isin(["수정구", "중원구", "분당구"])].copy()
    summary["총주택수"] = summary[["아파트수", "단독_다가구수", "연립_다세대수", "기타수"]].sum(axis=1)
    for col in ("아파트", "단독_다가구", "연립_다세대", "기타"):
        summary[f"{col}비율"] = summary[f"{col}수"] / summary["총주택수"]
    summary["오피스텔비율"] = pd.NA

    long_rows = []
    for _, row in summary.iterrows():
        for housing_type, count_col in {
            "아파트": "아파트수",
            "단독_다가구": "단독_다가구수",
            "연립_다세대": "연립_다세대수",
            "기타": "기타수",
        }.items():
            long_rows.append(
                {
                    "지역코드": pd.NA,
                    "구": row["구"],
                    "지역명": row["지역명"],
                    "기준연도": row["기준연도"],
                    "주택유형": housing_type,
                    "주택수": row[count_col],
                }
            )
    stock_long = pd.DataFrame(long_rows)

    apt_proxy_path = next(DATA_DIR.glob("*공동주택현황*.csv"))
    apt_proxy = read_csv_auto(apt_proxy_path)
    apt_proxy["세대수"] = to_number(apt_proxy["세대수"])
    apt_proxy = apt_proxy.rename(columns={"동": "법정동명", "데이터기준일자": "기준일자"})

    stock_long.to_csv(PROCESSED_DIR / "housing_stock_clean.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(PROCESSED_DIR / "housing_stock_gu_summary.csv", index=False, encoding="utf-8-sig")
    apt_proxy.to_csv(PROCESSED_DIR / "apartment_complexes_clean.csv", index=False, encoding="utf-8-sig")
    stock_long.to_csv(TABLEAU_DIR / "gu_housing_stock_long.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(TABLEAU_DIR / "gu_housing_stock_wide.csv", index=False, encoding="utf-8-sig")
    apt_proxy.to_csv(TABLEAU_DIR / "apartment_complexes_legal_dong.csv", index=False, encoding="utf-8-sig")
    return summary, apt_proxy


def make_summary_tables(
    households: pd.DataFrame, stock: pd.DataFrame, sales: pd.DataFrame, rent: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    admin_dong_summary = households[
        [
            "ADM_CD",
            "구",
            "행정동명",
            "법정동추정명",
            "지도기준일자",
            "기준연월",
            "세대수",
            "총인구",
            "19세이상인구",
            "65세이상인구",
            "생산가능인구_19_64세",
        ]
    ].copy()
    admin_dong_summary["세대당_총인구"] = admin_dong_summary["총인구"] / admin_dong_summary["세대수"]
    admin_dong_summary["생산가능인구비율_19_64세"] = (
        admin_dong_summary["생산가능인구_19_64세"] / admin_dong_summary["총인구"]
    )
    admin_dong_summary["65세이상인구비율"] = admin_dong_summary["65세이상인구"] / admin_dong_summary["총인구"]

    sales_summary = (
        sales.groupby(["구", "읍면동", "건축유형"], dropna=False)
        .agg(
            매매_거래건수=("매매가_평당_만원", "size"),
            매매가_평당_중앙값=("매매가_평당_만원", "median"),
            매매가_평당_평균=("매매가_평당_만원", "mean"),
            매매가_총액_중앙값=("거래금액_만원", "median"),
            전용면적_중앙값=("전용면적_m2", "median"),
        )
        .reset_index()
        .rename(columns={"읍면동": "법정동명"})
    )
    sales_summary["거래건수_주의"] = sales_summary["매매_거래건수"] < 5
    sales_summary = sales_summary.rename(
        columns={
            "전용면적_중앙값": "매매_전용면적_중앙값",
            "거래건수_주의": "매매_거래건수_주의",
        }
    )

    jeonse = rent[rent["전월세구분"] == "전세"].copy()
    jeonse_summary = (
        jeonse.groupby(["구", "읍면동", "건축유형"], dropna=False)
        .agg(
            전세_거래건수=("보증금_평당_만원", "size"),
            전세보증금_평당_중앙값=("보증금_평당_만원", "median"),
            전세보증금_평당_평균=("보증금_평당_만원", "mean"),
            전세보증금_총액_중앙값=("보증금_만원", "median"),
            전용면적_중앙값=("전용면적_m2", "median"),
        )
        .reset_index()
        .rename(columns={"읍면동": "법정동명"})
    )
    jeonse_summary["거래건수_주의"] = jeonse_summary["전세_거래건수"] < 5
    jeonse_summary = jeonse_summary.rename(
        columns={
            "전용면적_중앙값": "전세_전용면적_중앙값",
            "거래건수_주의": "전세_거래건수_주의",
        }
    )

    monthly = rent[rent["전월세구분"] == "월세"].copy()
    monthly_summary = (
        monthly.groupby(["구", "읍면동", "건축유형"], dropna=False)
        .agg(
            월세_거래건수=("월세_평당_만원", "size"),
            월세보증금_평당_중앙값=("보증금_평당_만원", "median"),
            월세_평당_중앙값=("월세_평당_만원", "median"),
            월세보증금_총액_중앙값=("보증금_만원", "median"),
            월세_총액_중앙값=("월세_만원", "median"),
            전용면적_중앙값=("전용면적_m2", "median"),
        )
        .reset_index()
        .rename(columns={"읍면동": "법정동명"})
    )
    monthly_summary["거래건수_주의"] = monthly_summary["월세_거래건수"] < 5
    monthly_summary = monthly_summary.rename(
        columns={
            "전용면적_중앙값": "월세_전용면적_중앙값",
            "거래건수_주의": "월세_거래건수_주의",
        }
    )

    legal_cost_summary = sales_summary.merge(
        jeonse_summary,
        on=["구", "법정동명", "건축유형"],
        how="outer",
    ).merge(
        monthly_summary,
        on=["구", "법정동명", "건축유형"],
        how="outer",
        suffixes=("", "_월세"),
    )

    admin_dong_cost_proxy = admin_dong_summary.merge(
        legal_cost_summary,
        left_on=["구", "법정동추정명"],
        right_on=["구", "법정동명"],
        how="left",
    )
    admin_dong_cost_proxy["가격매핑방식"] = "행정동명에서 숫자를 제거한 법정동명 추정 매핑"
    admin_dong_cost_proxy.loc[admin_dong_cost_proxy["법정동명"].isna(), "가격매핑방식"] = "매칭 없음"

    gu_demand_summary = (
        admin_dong_summary.groupby("구", as_index=False)
        .agg({"세대수": "sum", "총인구": "sum", "생산가능인구_19_64세": "sum"})
        .rename(columns={"구": "지역명"})
    )
    gu_demand_and_stock_reference = gu_demand_summary.merge(stock.drop(columns=["구"]), on="지역명", how="left")
    gu_demand_and_stock_reference["세대수_대비_주택수"] = (
        gu_demand_and_stock_reference["총주택수"] / gu_demand_and_stock_reference["세대수"]
    )

    admin_dong_summary.to_csv(TABLE_DIR / "admin_dong_demand_summary.csv", index=False, encoding="utf-8-sig")
    sales_summary.to_csv(TABLE_DIR / "sales_summary.csv", index=False, encoding="utf-8-sig")
    jeonse_summary.to_csv(TABLE_DIR / "jeonse_summary.csv", index=False, encoding="utf-8-sig")
    monthly_summary.to_csv(TABLE_DIR / "monthly_rent_summary.csv", index=False, encoding="utf-8-sig")
    legal_cost_summary.to_csv(TABLE_DIR / "legal_dong_housing_cost_summary.csv", index=False, encoding="utf-8-sig")
    gu_demand_and_stock_reference.to_csv(
        TABLE_DIR / "gu_demand_and_stock_reference.csv", index=False, encoding="utf-8-sig"
    )

    admin_dong_summary.to_csv(TABLEAU_DIR / "01_admin_dong_demand.csv", index=False, encoding="utf-8-sig")
    legal_cost_summary.to_csv(TABLEAU_DIR / "02_legal_dong_cost_summary.csv", index=False, encoding="utf-8-sig")
    admin_dong_cost_proxy.to_csv(TABLEAU_DIR / "03_admin_dong_cost_proxy.csv", index=False, encoding="utf-8-sig")
    stock.to_csv(TABLEAU_DIR / "04_gu_housing_stock_reference.csv", index=False, encoding="utf-8-sig")
    gu_demand_and_stock_reference.to_csv(
        TABLEAU_DIR / "05_gu_demand_and_stock_reference.csv", index=False, encoding="utf-8-sig"
    )

    sales.to_csv(TABLEAU_DIR / "transactions_sales_long.csv", index=False, encoding="utf-8-sig")
    rent.to_csv(TABLEAU_DIR / "transactions_rent_long.csv", index=False, encoding="utf-8-sig")

    residential_summary = admin_dong_summary.merge(
        legal_cost_summary.groupby(["구", "법정동명"], as_index=False).agg(
            매매가_평당_중앙값=("매매가_평당_중앙값", "median"),
            전세보증금_평당_중앙값=("전세보증금_평당_중앙값", "median"),
            월세_평당_중앙값=("월세_평당_중앙값", "median"),
        ),
        left_on=["구", "법정동추정명"],
        right_on=["구", "법정동명"],
        how="left",
    )
    residential_summary.to_csv(PROCESSED_DIR / "residential_summary.csv", index=False, encoding="utf-8-sig")

    return admin_dong_summary, sales_summary, jeonse_summary, monthly_summary, legal_cost_summary


def save_bar(series: pd.Series, title: str, ylabel: str, output_name: str, horizontal: bool = False) -> None:
    data = series.dropna().sort_values()
    height = max(4, min(12, len(data) * 0.35))
    plt.figure(figsize=(9, height) if horizontal else (8, 5))
    if horizontal:
        data.plot(kind="barh", color="#4C78A8")
        plt.xlabel(ylabel)
    else:
        data.plot(kind="bar", color="#4C78A8")
        plt.ylabel(ylabel)
        plt.xticks(rotation=0)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / output_name, dpi=160)
    plt.close()


def save_boxplot(df: pd.DataFrame, value_col: str, title: str, ylabel: str, output_name: str) -> None:
    groups = [(name, group[value_col].dropna()) for name, group in df.groupby("건축유형")]
    groups = [(name, values) for name, values in groups if len(values) > 0]
    if not groups:
        return
    plt.figure(figsize=(8, 5))
    plt.boxplot([values for _, values in groups], tick_labels=[name for name, _ in groups], showfliers=False)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / output_name, dpi=160)
    plt.close()


def make_visualizations(
    admin_dong_summary: pd.DataFrame, sales: pd.DataFrame, rent: pd.DataFrame
) -> None:
    admin = admin_dong_summary.set_index("행정동명")
    save_bar(admin["세대수"], "행정동별 세대수", "세대 수", "admin_dong_households.png", horizontal=True)
    save_bar(admin["생산가능인구_19_64세"], "행정동별 생산가능인구", "인구 수", "admin_dong_working_age_population.png", horizontal=True)
    save_bar(
        admin["생산가능인구비율_19_64세"],
        "행정동별 생산가능인구 비율",
        "비율",
        "admin_dong_working_age_ratio.png",
        horizontal=True,
    )

    sales_region = sales.groupby("읍면동")["매매가_평당_만원"].median()
    save_bar(sales_region, "지역별 매매가 평당 중앙값", "만원/평", "sales_price_per_pyeong.png", horizontal=True)

    jeonse = rent[rent["전월세구분"] == "전세"]
    jeonse_region = jeonse.groupby("읍면동")["보증금_평당_만원"].median()
    save_bar(jeonse_region, "지역별 전세보증금 평당 중앙값", "만원/평", "jeonse_price_per_pyeong.png", horizontal=True)

    monthly = rent[rent["전월세구분"] == "월세"]
    monthly_region = monthly.groupby("읍면동")["월세_평당_만원"].median()
    save_bar(monthly_region, "지역별 월세 평당 중앙값", "만원/평", "rent_price_per_pyeong.png", horizontal=True)

    save_boxplot(sales, "매매가_평당_만원", "건축유형별 매매가", "만원/평", "sales_price_by_type_boxplot.png")
    save_boxplot(jeonse, "보증금_평당_만원", "건축유형별 전세보증금", "만원/평", "jeonse_price_by_type_boxplot.png")
    save_boxplot(monthly, "월세_평당_만원", "건축유형별 월세", "만원/평", "rent_price_by_type_boxplot.png")

    plt.figure(figsize=(7, 5))
    plt.scatter(admin_dong_summary["세대수"], admin_dong_summary["생산가능인구_19_64세"], color="#4C78A8")
    plt.title("행정동 세대수 vs 생산가능인구")
    plt.xlabel("세대수")
    plt.ylabel("생산가능인구_19_64세")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "admin_dong_households_vs_working_age.png", dpi=160)
    plt.close()


def write_inventory_and_notes(sales: pd.DataFrame, rent: pd.DataFrame) -> None:
    inventory_rows = []
    for path in sorted(DATA_DIR.iterdir()):
        if not path.is_file():
            continue
        row = {"파일명": path.name, "확장자": path.suffix.lower(), "크기_bytes": path.stat().st_size}
        try:
            if path.suffix.lower() == ".csv" and "실거래가" in path.name:
                df = read_transaction_csv(path)
                row.update(
                    {
                        "데이터역할": f"{infer_type_from_filename(path)} {infer_trade_kind(path)} 실거래",
                        "행수": len(df),
                        "컬럼수": len(df.columns),
                        "컬럼목록": "|".join(df.columns),
                    }
                )
            elif path.suffix.lower() == ".csv":
                df = read_csv_auto(path)
                row.update(
                    {
                        "데이터역할": "기초 통계/보조 데이터",
                        "행수": len(df),
                        "컬럼수": len(df.columns),
                        "컬럼목록": "|".join(df.columns),
                    }
                )
            elif path.suffix.lower() == ".xlsx":
                row.update(
                    {
                        "데이터역할": "세대수/인구 엑셀",
                        "행수": pd.NA,
                        "컬럼수": pd.NA,
                        "컬럼목록": "첫 시트: 행정기관|인구수|19세 이상|65세 이상|세대수",
                    }
                )
        except Exception as exc:
            row.update({"데이터역할": "읽기 확인 필요", "행수": pd.NA, "컬럼수": pd.NA, "컬럼목록": str(exc)})
        inventory_rows.append(row)
    pd.DataFrame(inventory_rows).to_csv(TABLE_DIR / "data_inventory.csv", index=False, encoding="utf-8-sig")

    notes = [
        "# Residential Data Notes",
        "",
        "- 세대수/인구: `2026.3 인구현황(1인세대수 현황 포함).xlsx` 첫 시트에서 행정동별 세대수와 인구를 추출했습니다.",
        "- 지도 조인: `Dataset_v1/seongnam_dong.geojson`의 `ADM_CD`와 `동`을 세대수 테이블에 붙였습니다.",
        "- 생산가능인구_19_64세: 원자료의 `19세 이상`에서 `65세 이상`을 뺀 값으로 계산했습니다.",
        "- 기본 granularity: 생활권 재정의 목적에 맞춰 행정동 수요 테이블과 법정동 실거래가 테이블을 분리했습니다.",
        "- 주택 재고: `경기도 성남시_주택_통계_20250618.csv`가 구 단위 총량만 제공하므로 동 단위 테이블에 억지 배분하지 않고 구 단위 reference로 분리했습니다.",
        "- 공동주택현황: 단지별 세대수는 별도 `apartment_complexes_clean.csv`로 저장했습니다. 전체 주택 재고가 아니므로 총 공급량에는 합산하지 않았습니다.",
        "- 실거래가: 국토교통부 실거래가 CSV의 안내문 이후 `NO` 헤더 행부터 읽었습니다. 금액 단위는 원자료 컬럼명 기준 `만원`입니다.",
        "- 실거래가 지역 단위: 원자료에 법정동코드가 없어 `시군구` 문자열의 마지막 동명을 `읍면동`으로 사용했습니다.",
        "- Tableau용 `03_admin_dong_cost_proxy.csv`는 행정동명에서 숫자를 제거한 법정동 추정명으로 가격을 붙인 참고용 테이블입니다. 엄밀한 분석에는 법정동-행정동 매핑표가 필요합니다.",
        "- 오피스텔 재고: 주택 통계 파일에 오피스텔 재고 컬럼이 없어 수요-공급 표의 오피스텔수/비율은 결측으로 남겼습니다.",
        f"- 매매 실거래 정제 건수: {len(sales):,}건",
        f"- 전월세 실거래 정제 건수: {len(rent):,}건",
        "",
        "## Tableau CSV",
        "",
        "- `output/tableau/01_admin_dong_demand.csv`: ADM_CD가 포함된 행정동 단위 수요/인구 테이블입니다.",
        "- `output/tableau/02_legal_dong_cost_summary.csv`: 법정동 x 건축유형 단위 매매/전세/월세 요약입니다.",
        "- `output/tableau/03_admin_dong_cost_proxy.csv`: 행정동 지도에 가격을 얹기 위한 추정 결합 테이블입니다.",
        "- `output/tableau/04_gu_housing_stock_reference.csv`: 구 단위 주택 재고 wide table입니다.",
        "- `output/tableau/05_gu_demand_and_stock_reference.csv`: 구 단위 수요와 주택 재고를 함께 본 reference table입니다.",
        "- `output/tableau/transactions_sales_long.csv`, `transactions_rent_long.csv`: Tableau에서 직접 필터링할 수 있는 실거래 long table입니다.",
        "",
        "## 추가로 있으면 좋은 데이터",
        "",
        "1. 법정동-행정동 코드 매핑표: 가격 분석과 세대수/주택재고를 같은 공간 단위로 연결하는 데 필요합니다.",
        "2. 행정동 또는 격자 단위 주택 재고: 현재 full stock은 구 단위라 생활권 세부 비교에는 해상도가 낮습니다.",
        "3. 오피스텔 재고 데이터: 오피스텔 실거래가는 있으나 공급 재고와 직접 비교할 수 없습니다.",
        "4. 법정동코드가 포함된 실거래 원자료: 문자열 동명보다 안정적인 join이 가능합니다.",
    ]
    (ROOT / "output" / "residential_data_notes.md").write_text("\n".join(notes), encoding="utf-8")

    tableau_readme = [
        "# Tableau Import Guide",
        "",
        "권장 사용 파일은 이 폴더의 CSV입니다.",
        "",
        "1. 지도 레이어: `Dataset_v1/seongnam_dong.geojson`을 Tableau의 spatial file로 불러옵니다.",
        "2. 행정동 수요: `01_admin_dong_demand.csv`를 `ADM_CD` 기준으로 지도 레이어와 연결합니다.",
        "3. 주거 비용: 법정동 기준 분석은 `02_legal_dong_cost_summary.csv`를 사용합니다.",
        "4. 행정동 지도 위 가격 표현: `03_admin_dong_cost_proxy.csv`를 사용하되, `가격매핑방식` 필터/라벨을 같이 확인합니다.",
        "5. 주택 재고: 구 단위 자료라 `04_gu_housing_stock_reference.csv` 또는 `05_gu_demand_and_stock_reference.csv`로 별도 sheet에서 다룹니다.",
        "",
        "주의: `03_admin_dong_cost_proxy.csv`는 공식 법정동-행정동 매핑이 아니라 행정동명 기반 추정 매핑입니다.",
    ]
    (TABLEAU_DIR / "README.md").write_text("\n".join(tableau_readme), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    households = clean_households()
    stock, _ = clean_housing_stock()
    sales, rent = clean_transactions()
    admin_dong_summary, sales_summary, jeonse_summary, monthly_summary, legal_cost_summary = make_summary_tables(
        households, stock, sales, rent
    )
    make_visualizations(admin_dong_summary, sales, rent)
    write_inventory_and_notes(sales, rent)
    print("Residential pipeline complete")
    print(f"households: {len(households):,}")
    print(f"sales transactions: {len(sales):,}")
    print(f"rent transactions: {len(rent):,}")
    print(f"tables: {TABLE_DIR}")
    print(f"tableau csv: {TABLEAU_DIR}")
    print(f"figures: {FIGURE_DIR}")


if __name__ == "__main__":
    main()
