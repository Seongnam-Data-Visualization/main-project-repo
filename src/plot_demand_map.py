import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# =========================
# Configs
# =========================
PATH_POP = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_인구및세대_현황_20260331 (1).csv"
PATH_SINGLE = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_1인세대_현황_20250430.csv"
PATH_PARENT = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_저소득_한부모가족_현황_20250531.csv"
PATH_DISABLED = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_장애인등록_현황_20250524.csv"
PATH_BENEFIT = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_기초생활수급자_현황_20250912.csv"

PATH_GEO = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\BND_ADM_DONG_PG\BND_ADM_DONG_PG.shp"

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# =========================
# Load
# =========================
def load_data():
    pop = pd.read_csv(PATH_POP)
    single = pd.read_csv(PATH_SINGLE)
    parent = pd.read_csv(PATH_PARENT, encoding="euc-kr")
    disabled = pd.read_csv(PATH_DISABLED)
    benefit = pd.read_csv(PATH_BENEFIT)

    # 컬럼 정리
    parent.columns = parent.columns.str.replace(" ", "")
    disabled.columns = disabled.columns.str.replace(" ", "")
    benefit.columns = benefit.columns.str.replace(" ", "")

    return pop, single, parent, disabled, benefit

def load_geo():
    gdf = gpd.read_file(PATH_GEO)

    # 성남시 필터링
    gdf = gdf[gdf["ADM_CD"].str.startswith(("31021", "31022", "31023"))]

    # col 통일
    gdf = gdf.rename(columns={"ADM_NM": "동"})

    # 공백 제거...
    gdf["동"] = gdf["동"].str.replace(" ", "")

    return gdf

# =========================
# 2. 동 기준 집계
# =========================
def aggregate(pop, single, parent, disabled, benefit):

    pop_g = pop.groupby("동").sum(numeric_only=True)
    single_g = single.groupby("동별").sum(numeric_only=True)
    parent_g = parent.groupby("동별").sum(numeric_only=True)
    disabled_g = disabled.groupby("읍면동명").sum(numeric_only=True)
    benefit_g = benefit.groupby("동별").sum(numeric_only=True)

    # 이름 통일
    single_g.index.name = "동"
    parent_g.index.name = "동"
    disabled_g.index.name = "동"
    benefit_g.index.name = "동"

    # merge
    df = pop_g.join(single_g, how="left") \
              .join(parent_g, how="left") \
              .join(disabled_g, how="left") \
              .join(benefit_g, how="left")
    df.index = df.index.str.replace(" ", "")
    # df = df.fillna(0)

    return df


# =========================
# 3. 비율 계산
# =========================
def make_features(df):

    df["1인가구비율"] = df["1인세대수_계"] / df["인구수_계"]
    df["한부모비율"] = df["한부모가족_세대수"] / df["인구수_계"]
    df["장애인비율"] = df["등록장애인수(합계)"] / df["인구수_계"]
    df["수급자비율"] = df["총수급자_인원계"] / df["인구수_계"]
    df["노인비율"] = df["65세 이상_계"] / df["인구수_계"]

    return df


# =========================
# 4. 정규화 + score
# =========================
def make_score(df):

    cols = ["1인가구비율", "한부모비율", "장애인비율", "수급자비율", "노인비율"]

    for c in cols:
        df[c] = (df[c] - df[c].min()) / (df[c].max() - df[c].min() + 1e-9)

    # 가중치 동일 (추후 조정)
    df["취약도"] = df[cols].mean(axis=1)

    return df


# =========================
# 5. 지도 그리기
# =========================
def plot_map(df):

    fig, ax = plt.subplots(figsize=(12, 10))
    gdf = load_geo()

    merged = gdf.merge(df, left_on="동", right_index=True, how="left")

    # 디버깅용
    print("Unmatched:")
    print(merged[merged["취약도"].isna()]["동"].tolist())

    merged["취약도"] = merged["취약도"].fillna(0)

    # plt.figure(figsize=(10, 10))
    merged.plot(
        ax=ax,
        column="취약도",
        cmap="Reds",
        legend=True,
        edgecolor="black"
    )

    plt.title("성남시 동별 취약도 지도")

    top10 = df["취약도"].sort_values(ascending=False).head(10)  # top 10
    for i, (dong, val) in enumerate(top10.items()):
        geom = merged[merged["동"] == dong].geometry

        if len(geom) == 0:
            continue

        centroid = geom.to_crs(epsg=5179).centroid.to_crs(geom.crs).values[0]

        ax.text(
            centroid.x, centroid.y,
            str(i + 1),
            fontsize=10,
            ha='center',
            va='center',
            color='black',
            fontweight='bold'
        )

    text = "\n".join([f"{i+1}. {name}" for i, name in enumerate(top10.index)])

    plt.gcf().text(
        0.85, 0.5, text,
        fontsize=10,
        va="center",
        bbox=dict(
            boxstyle="round",
            facecolor="white",
            edgecolor="black",
            alpha=0.9
        )
)

    # 구 코드 추출
    merged["구코드"] = merged["ADM_CD"].str[:5]

    gu_boundary = merged.dissolve(by="구코드")

    # boundary overlay
    gu_boundary.boundary.plot(
        ax=ax,
        color="black",
        linewidth=2
    )

    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.savefig("results/demand_map.png")
    plt.show()


# =========================
# main
# =========================
def main():
    pop, single, parent, disabled, benefit = load_data()

    df = aggregate(pop, single, parent, disabled, benefit)
    df = make_features(df)
    df = make_score(df)

    # save geojson
    gdf = load_geo()
    gdf.to_file("seongnam_dong.geojson", driver="GeoJSON")

    plot_map(df)


if __name__ == "__main__":
    main()