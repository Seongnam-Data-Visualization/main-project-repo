import pandas as pd
import matplotlib.pyplot as plt
import os

# =========================
# Configs
# =========================
INPUT_PATH = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_인구및세대_현황_20260331 (1).csv"
OUTPUT_DIR = "./results/outputs_population"

os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


# =========================
# Load & Preprocess
# =========================
def load_data(path):
    df = pd.read_csv(path)
    return df


# =========================
# 구별 인구
# =========================
def plot_population_by_gu(df):
    grouped = df.groupby("구별")["인구수_계"].sum()

    plt.figure()
    grouped.plot(kind='bar')

    plt.title("구별 인구")
    plt.ylabel("인구수")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "gu_population.png"))
    plt.close()


# =========================
# 동별 인구
# =========================
def plot_population_by_dong(df):
    grouped = df.groupby("동")["인구수_계"].sum().sort_values()

    plt.figure(figsize=(8, 12))
    grouped.plot(kind='barh')

    plt.title("동별 인구")
    plt.xlabel("인구수")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "dong_population.png"))
    plt.close()


# =========================
# 구별 노인 비율
# =========================
def plot_elderly_ratio_by_gu(df):
    grouped = df.groupby("구별").sum(numeric_only=True)

    ratio = grouped["65세 이상_계"] / grouped["인구수_계"]

    plt.figure()
    ratio.plot(kind='bar')

    plt.title("구별 노인 비율")
    plt.ylabel("비율")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "gu_elderly_ratio.png"))
    plt.close()


# =========================
# 동별 노인 비율
# =========================
def plot_elderly_ratio_by_dong(df):
    grouped = df.groupby("동").sum(numeric_only=True)

    ratio = grouped["65세 이상_계"] / grouped["인구수_계"]
    ratio = ratio.sort_values()

    plt.figure(figsize=(8, 12))
    ratio.plot(kind='barh')

    plt.title("동별 노인 비율")
    plt.xlabel("비율")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "dong_elderly_ratio.png"))
    plt.close()


# =========================
# 인구 vs 세대수
# =========================
def plot_population_vs_household(df):
    plt.figure()

    plt.scatter(df["세대수"], df["인구수_계"])

    plt.xlabel("세대수")
    plt.ylabel("인구수")
    plt.title("인구 vs 세대수")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "population_vs_household.png"))
    plt.close()


# =========================
# 평균 세대 규모
# =========================
def plot_household_size(df):
    grouped = df.groupby("구별").sum(numeric_only=True)

    avg = grouped["인구수_계"] / grouped["세대수"]

    plt.figure()
    avg.plot(kind='bar')

    plt.title("구별 평균 세대 규모")
    plt.ylabel("평균 인원")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "household_size.png"))
    plt.close()


# =========================
# 연령 구조
# =========================
def make_age_structure(df):
    grouped = df.groupby("동").sum(numeric_only=True)

    minor = grouped["인구수_계"] - grouped["19세 이상_계"]
    working = grouped["19세 이상_계"] - grouped["65세 이상_계"]
    elderly = grouped["65세 이상_계"]

    result = pd.DataFrame({
        "미성년": minor,
        "생산가능": working,
        "노인": elderly
    })

    return result

def plot_age_structure_by_gu(df):
    grouped = df.groupby("구별").sum(numeric_only=True)

    minor = grouped["인구수_계"] - grouped["19세 이상_계"]
    working = grouped["19세 이상_계"] - grouped["65세 이상_계"]
    elderly = grouped["65세 이상_계"]

    x = range(len(grouped))

    plt.figure()
    plt.bar(x, minor, label="미성년")
    plt.bar(x, working, bottom=minor, label="생산가능")
    plt.bar(x, elderly, bottom=minor + working, label="노인")

    plt.xticks(x, grouped.index)
    plt.title("구별 연령 구조")
    plt.ylabel("인구수")
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "gu_age_structure.png"))
    plt.close()

def plot_age_structure_dong(df):
    grouped = df.groupby("동").sum(numeric_only=True)

    grouped = grouped.sort_values("인구수_계", ascending=False)

    minor = grouped["인구수_계"] - grouped["19세 이상_계"]
    working = grouped["19세 이상_계"] - grouped["65세 이상_계"]
    elderly = grouped["65세 이상_계"]

    x = range(len(grouped))

    plt.figure(figsize=(20, 12))
    plt.bar(x, minor, label="미성년")
    plt.bar(x, working, bottom=minor, label="생산가능")
    plt.bar(x, elderly, bottom=minor + working, label="노인")

    plt.xticks(x, grouped.index, rotation=45, fontsize=7)
    plt.title(f"연령 구조")
    plt.ylabel("인구수")
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "dong_age_structure.png"))
    plt.close()

# =========================
# main
# =========================
def main():
    df = load_data(INPUT_PATH)

    plot_population_by_gu(df)
    plot_population_by_dong(df)
    plot_elderly_ratio_by_gu(df)
    plot_elderly_ratio_by_dong(df)
    plot_population_vs_household(df)
    plot_household_size(df)

    make_age_structure(df)
    plot_age_structure_by_gu(df)
    plot_age_structure_dong(df)

    print("Saved:", OUTPUT_DIR) 


if __name__ == "__main__":
    main()