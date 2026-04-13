import pandas as pd
import matplotlib.pyplot as plt
import os

# =========================
# Configs
# =========================
INPUT_PATH = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_기초생활수급자_현황_20250912.csv"
OUTPUT_DIR = "./results/outputs_beneficiaries"

os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


# =========================
# Load & Process
# =========================
def load_data(path):
    df = pd.read_csv(path)

    # 공백 제거 (중요)
    df.columns = df.columns.str.replace(" ", "")

    return df


# =========================
# 전체 성별
# =========================
def plot_total_gender(df):
    total = df.select_dtypes(include='number').sum()

    male = total["총수급자_남"]
    female = total["총수급자_여"]

    plt.figure()
    plt.bar(["전체"], [male], label="남", color="#4C72B0")
    plt.bar(["전체"], [female], bottom=[male], label="여", color="#DD8452")

    plt.title("전체 수급자 성별 분포")
    plt.ylabel("인원")
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "total_gender.png"))
    plt.close()


# =========================
# 전체 유형
# =========================
def plot_total_type(df):
    total = df.select_dtypes(include='number').sum()

    normal = total["일반수급자_인원계"]
    conditional = total["조건부수급자_인원계"]
    special = total["특례수급자_인원계"]

    plt.figure()
    plt.bar(["전체"], [normal], label="일반", color="#4C72B0")
    plt.bar(["전체"], [conditional], bottom=[normal], label="조건부", color="#55A868")
    plt.bar(["전체"], [special],
            bottom=[normal + conditional],
            label="특례",
            color="#C44E52")

    plt.title("수급자 유형 분포")
    plt.ylabel("인원")
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "total_type.png"))
    plt.close()


# =========================
# 구별 유형
# =========================
def plot_by_gu_type(df):
    grouped = df.groupby("구별").sum(numeric_only=True)

    x = range(len(grouped))

    normal = grouped["일반수급자_인원계"]
    conditional = grouped["조건부수급자_인원계"]
    special = grouped["특례수급자_인원계"]

    plt.figure()
    plt.bar(x, normal, label="일반", color="#4C72B0")
    plt.bar(x, conditional, bottom=normal, label="조건부", color="#55A868")
    plt.bar(x, special, bottom=normal + conditional, label="특례", color="#C44E52")

    plt.xticks(x, grouped.index)
    plt.title("구별 수급자 유형 구조")
    plt.ylabel("인원")
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "gu_type.png"))
    plt.close()


# =========================
# 동별 분포
# =========================
def plot_by_dong(df):
    grouped = df.groupby("동별")["총수급자_인원계"].sum().sort_values()

    plt.figure(figsize=(8, 12))
    grouped.plot(kind='barh')

    plt.title("동별 수급자 분포")
    plt.xlabel("인원")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "dong_total.png"))
    plt.close()


# =========================
# 조건부 비율
# =========================
def plot_conditional_ratio(df):
    grouped = df.groupby("구별").sum(numeric_only=True)

    ratio = grouped["조건부수급자_인원계"] / grouped["총수급자_인원계"]

    plt.figure()
    ratio.plot(kind='bar')

    plt.title("구별 조건부 수급자 비율")
    plt.ylabel("비율")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "conditional_ratio.png"))
    plt.close()


# =========================
# main
# =========================
def main():
    df = load_data(INPUT_PATH)

    plot_total_gender(df)
    plot_total_type(df)
    plot_by_gu_type(df)
    plot_by_dong(df)
    plot_conditional_ratio(df)

    print("Saved:", OUTPUT_DIR)


if __name__ == "__main__":
    main()