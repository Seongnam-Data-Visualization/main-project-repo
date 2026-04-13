import pandas as pd
import matplotlib.pyplot as plt
import os

# =========================
# Configs
# =========================
INPUT_PATH = r"C:\Users\rdh08\Desktop\2026_Data_Visualization\Dataset\경기도 성남시_장애인등록_현황_20250524.csv"
OUTPUT_DIR = "./results/outputs_disability"

os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


# =========================
# Load & Process
# =========================
def load_data(path):
    df = pd.read_csv(path)

    df.columns = df.columns.str.replace(" ", "")

    return df


def aggregate_total(df):
    return df.select_dtypes(include='number').sum()


# =========================
# 전체 성별 stacked
# =========================
def plot_total_gender(df):
    total = df.groupby(["읍면동명"]).sum(numeric_only=True).sum()

    male = total["등록장애인수(남성)"]
    female = total["등록장애인수(여성)"]

    plt.figure()
    plt.bar(["전체"], [male], label="남", color="#4C72B0")
    plt.bar(["전체"], [female], bottom=[male], label="여", color="#DD8452")

    plt.title("전체 장애인 성별 분포")
    plt.ylabel("인원")
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "total_gender.png"))
    plt.close()


# =========================
# 중증도 stacked
# =========================
def plot_severity(df):
    total = df.groupby(["읍면동명"]).sum(numeric_only=True).sum()

    severe = total["심한장애인수(합계)"]
    mild = total["심하지않은장애인수(합계)"]

    plt.figure()
    plt.bar(["전체"], [severe], label="심한", color="#C44E52")
    plt.bar(["전체"], [mild], bottom=[severe], label="심하지않음", color="#55A868")

    plt.title("장애 중증도 분포")
    plt.ylabel("인원")
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "severity.png"))
    plt.close()


# =========================
# 구별 성별 stacked
# =========================
def plot_by_gu_gender(df):
    grouped = df.groupby("구명").sum(numeric_only=True)

    x = range(len(grouped))

    plt.figure()
    plt.bar(x, grouped["등록장애인수(남성)"], label="남", color="#4C72B0")
    plt.bar(x, grouped["등록장애인수(여성)"],
            bottom=grouped["등록장애인수(남성)"],
            label="여",
            color="#DD8452")

    plt.xticks(x, grouped.index)
    plt.title("구별 장애인 성별 분포")
    plt.ylabel("인원")
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "gu_gender.png"))
    plt.close()


# =========================
# 구별 중증도
# =========================
def plot_by_gu_severity(df):
    grouped = df.groupby("구명").sum(numeric_only=True)

    x = range(len(grouped))

    plt.figure()
    plt.bar(x, grouped["심한장애인수(합계)"], label="심한", color="#C44E52")
    plt.bar(x, grouped["심하지않은장애인수(합계)"],
            bottom=grouped["심한장애인수(합계)"],
            label="심하지않음",
            color="#55A868")

    plt.xticks(x, grouped.index)
    plt.title("구별 장애 중증도")
    plt.ylabel("인원")
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "gu_severity.png"))
    plt.close()


# =========================
# 동별 
# =========================
def plot_by_dong(df):
    grouped = df.groupby("읍면동명")["등록장애인수(합계)"].sum().sort_values()

    plt.figure(figsize=(8, 12))
    grouped.plot(kind='barh')

    plt.title("동별 장애인 수")
    plt.xlabel("인원")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "dong_total.png"))
    plt.close()


# =========================
# 장애유형
# =========================
def plot_disability_type(df):
    grouped = df.groupby("장애유형")["등록장애인수(합계)"].sum().sort_values(ascending=False)

    plt.figure()
    grouped.plot(kind='bar')

    plt.title("장애 유형별 분포")
    plt.ylabel("인원")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "type_distribution.png"))
    plt.close()


# =========================
# 중증 비율
# =========================
def plot_severity_ratio_by_gu(df):
    grouped = df.groupby("구명").sum(numeric_only=True)

    ratio = grouped["심한장애인수(합계)"] / grouped["등록장애인수(합계)"]

    plt.figure()
    ratio.plot(kind='bar')

    plt.title("구별 중증 장애 비율")
    plt.ylabel("비율")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "severity_ratio_gu.png"))
    plt.close()


# =========================
# main
# =========================
def main():
    df = load_data(INPUT_PATH)

    plot_total_gender(df)
    plot_severity(df)
    plot_by_gu_gender(df)
    plot_by_gu_severity(df)
    plot_by_dong(df)
    plot_disability_type(df)
    plot_severity_ratio_by_gu(df)

    print("Saved:", OUTPUT_DIR)


if __name__ == "__main__":
    main()