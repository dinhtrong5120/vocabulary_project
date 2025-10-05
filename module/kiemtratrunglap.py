import pandas as pd


def process(file_path_):
    df = pd.read_excel(file_path_, sheet_name="Sheet1")
    # duplicate_words = (
    #     df['Từ vựng']
    #     .dropna()  # Bỏ các giá trị NaN
    #     .str.lower()  # Đưa về chữ thường để so sánh không phân biệt hoa thường
    #     .value_counts()  # Đếm số lần xuất hiện
    #     .loc[lambda x: x > 1]  # Lọc ra các từ xuất hiện >1 lần (tức là bị trùng)
    #     .index
    #     .tolist()
    # )
    df_cleaned = df.loc[
        ~df['Từ vựng'].str.lower().duplicated(keep='first')
    ]
    duplicate_words = (
        df_cleaned['Từ vựng']
        .dropna()  # Bỏ các giá trị NaN
        .str.lower()  # Đưa về chữ thường để so sánh không phân biệt hoa thường
        .value_counts()  # Đếm số lần xuất hiện
        .loc[lambda x: x > 1]  # Lọc ra các từ xuất hiện >1 lần (tức là bị trùng)
        .index
        .tolist()
    )
    df_cleaned.to_excel(r"C:\Users\User\Downloads\ETS2023\ETS2023_TEST0\vocabulary_ETS2023_0_0.xlsx")
    return duplicate_words


if __name__ == '__main__':
    file_path = r"C:\Users\User\Downloads\ETS2023\ETS2023_TEST0\vocabulary_ETS2023_0.xlsx"
    result = process(file_path)
    print(result)
