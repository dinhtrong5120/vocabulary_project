import re
import warnings

warnings.filterwarnings("ignore")
from pathlib import Path
import pandas as pd
from datetime import datetime


def replace_words(text, replacements):
    pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in replacements.keys()) + r')\b')
    return pattern.sub(lambda x: replacements[x.group()], text)


# ------------------------------------------------------------
# CẤU HÌNH – chỉ cần sửa tại đây
# ------------------------------------------------------------
_CHARS_TO_REMOVE = [
    r"\bms\.", r"\bmr\.", r"a\.m\.?", r"p\.m\.?",  # tiêu đề & AM/PM
    r"’ve", r"'ve", r"’s", r"'s", r"’d", r"'d", r"n[’']t",  # rút gọn
    r"’ll", r"'ll", r"’m", r"'m", r"’re", r"'re",
    r"[,:?.!\"'—–\-‐-–—]",  # dấu câu
    r"[()\[\]{}<>_^%*$#/+=&@★►•]",  # ký hiệu
    r"\d+",  # số
    r"test\s?\d+", r"part\s?\d+"  # từ khoá “test 1…”
]
_STOPWORDS_TO_BE = [r"\bis\b", r"\bam\b", r"\bare\b", r"\bwas\b", r"\bwere\b"]

_REPLACE_DICT = {
    "has": "have", "had": "have",
    "did": "do", "does": "do",
    "made": "make",
    "came": "come",
    "began": "begin",
    "broke": "break", "broken": "break", "breaking": "break", "breaks": "break",
    "taken": "take", "took": "take",
    "got": "get",
    "caught": "catch",
    "went": "go", "going": "go",
    "kept": "keep",
    "paid": "pay",
    "saved": "save", "saving": "save",
    "holding": "hold", "held": "hold",
    "true": "",  # xoá hoàn toàn
}


# ------------------------------------------------------------
# HÀM CHÍNH
# ------------------------------------------------------------
def read_text_file(path: str) -> str | None:
    """
    Đọc file văn bản, chuyển về chữ thường, loại bỏ/chuẩn hoá chuỗi rác.
    Trả về chuỗi đã làm sạch hoặc None nếu file không tồn tại.
    """
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read().lower()

        # 1) Xoá các mẫu định sẵn
        junk_pattern = re.compile("|".join(_CHARS_TO_REMOVE), flags=re.IGNORECASE)
        text = junk_pattern.sub(" ", text)

        # 2) Chuẩn hoá “is/am/are/was/were” → “be”
        be_pattern = re.compile("|".join(_STOPWORDS_TO_BE))
        text = be_pattern.sub(" be ", text)

        # 3) Thay thế theo từ điển _REPLACE_DICT
        if _REPLACE_DICT:
            # Tạo pattern kiểu r"\b(word1|word2|...)\b"
            repl_pattern = re.compile(
                r"\b(" + "|".join(map(re.escape, _REPLACE_DICT.keys())) + r")\b"
            )
            text = repl_pattern.sub(lambda m: _REPLACE_DICT[m.group(0)], text)

        # 4) Rút gọn khoảng trắng liên tiếp
        text = re.sub(r"\s{2,}", " ", text).strip()
        return text

    except FileNotFoundError:
        print(f"Không tìm thấy file: {path}")
        return None


def sort_by_appearance(big_string, sub_strings):
    # Lọc các chuỗi con thực sự có trong chuỗi lớn
    filtered = [s for s in sub_strings if s in big_string]
    # Sắp xếp theo vị trí xuất hiện đầu tiên
    sorted_list = sorted(filtered, key=lambda s: big_string.index(s))
    return sorted_list

def process_vocabulary(
        form_path: str,
        text_path: str,
        duplicates_path: str,
        cleaned_path: str,
        ignore_path: str
):
    """
    - form_path:          Excel chứa cột 'Từ vựng' và 'Dịch nghĩa'
    - text_path:          File .txt tham chiếu
    - duplicates_path:    Nơi lưu từ vựng trùng lặp (Excel)
    - cleaned_path:       Nơi lưu danh sách từ vựng đã làm sạch (Excel)
    - ignore_path:        Excel chứa cột 'Từ vựng' cần bỏ qua
    """

    # 1. Đọc & chuẩn hoá bảng từ vựng
    vocab_df = pd.read_excel(form_path).applymap(
        lambda x: x.lower() if isinstance(x, str) else x
    )

    # 2. Đọc nội dung file tham chiếu
    original_text = read_text_file(text_path) or ""
    editable_text = original_text  # will be mutated below

    # 3. Danh sách từ vựng (đã loại NaN & viết thường)
    vocab_terms = (
        vocab_df["Từ vựng"]
        .dropna()  # bỏ NaN
        .astype(str)  # ép kiểu str
        .str.lower()
        .tolist()
    )
    vocab_terms = set(vocab_terms)

    # 4. Tìm & xoá các từ đã xuất hiện trong file .txt
    duplicate_terms = []
    for term in vocab_terms:
        word_boundary = rf"(?<![a-zA-Z]){re.escape(term)}(?![a-zA-Z])"
        if re.search(word_boundary, editable_text):
            duplicate_terms.append(term)
            editable_text = re.sub(word_boundary + r"\s*", "", editable_text)

    # 5. Sắp xếp từ trùng lặp theo thứ tự xuất hiện
    duplicates_df = vocab_df[vocab_df["Từ vựng"].str.lower().isin(duplicate_terms)]
    order = sort_by_appearance(original_text, set(duplicates_df["Từ vựng"]))
    duplicates_ordered_df = (
        duplicates_df.set_index("Từ vựng").loc[order].reset_index()
        if duplicate_terms else pd.DataFrame(columns=vocab_df.columns)
    )

    # 6. Bổ sung từ mới tiềm năng (độ dài 4-15 ký tự, chưa có trong vocab_df)
    candidate_tokens = {
        tok for tok in editable_text.split() if 4 <= len(tok) <= 15
    }
    new_entries = [
        {"Từ vựng": tok}
        for tok in candidate_tokens
        if tok not in vocab_df["Từ vựng"].values
    ]
    if new_entries:
        vocab_df = pd.concat([vocab_df, pd.DataFrame(new_entries)], ignore_index=True)

    # 7. Tải & mở rộng danh sách cần bỏ qua
    ignore_df = pd.read_excel(ignore_path)
    ignore_base = ignore_df["Từ vựng"].dropna().str.lower().tolist()
    ignore_complete = _expand_ignore_list(ignore_base)

    # 8. Loại bỏ các từ không quan tâm
    vocab_df = vocab_df[~vocab_df["Từ vựng"].isin(ignore_complete)]
    duplicates_ordered_df = duplicates_ordered_df[
        ~duplicates_ordered_df["Từ vựng"].isin(ignore_complete)
    ]

    # 9. Xuất kết quả
    duplicates_ordered_df.to_excel(duplicates_path, index=False)
    vocab_df.to_excel(cleaned_path, sheet_name="Sheet1", index=False)
    return duplicates_ordered_df


# ------------------------------------------------------------
# Helper: sinh tất cả biến thể của danh sách từ bỏ qua
# ------------------------------------------------------------
def _expand_ignore_list(base_terms):
    """
    Sinh các biến thể chia đuôi thường gặp của mỗi từ,
    sau đó trả về tập hợp duy nhất.
    """
    suffixes = ["", "s", "es", "ies", "ed", "d", "ly", "ing"]

    stems = set()
    for word in base_terms:
        # loại một số hậu tố phổ biến để lấy gốc
        for suf in ["ing", "ies", "es", "ed", "ly", "s", "d", "y"]:
            if word.endswith(suf):
                stems.add(word[: -len(suf)])
        stems.add(word)  # thêm cả chính nó

    # sinh mọi kết hợp stem + hậu tố
    variations = {stem + suf for stem in stems for suf in suffixes}
    return list(variations)


# ============ CẤU HÌNH TOÀN CỤC ============ #
BASE_2023 = Path(r"C:\Users\User\Downloads\ETS2023\ETS2023_TEST0")
BASE_2023_ROOT = Path(r"C:\Users\User\Downloads\ETS2023")
FORM_FILE = BASE_2023 / "vocabulary_ETS2023_0.xlsx"
IGNORE_FILE = Path("ignore.xlsx")

TEST_IDS = range(1, 10)  # 1‥10  ⇨ ETS2023_TEST1 … TEST10
# Lấy thời gian hiện tại và định dạng thành chuỗi
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_UNIQUE = Path(f"all_duplicate_ets2023_{timestamp}.xlsx")


# =========================================== #


def run_single_test(test_id: int) -> pd.DataFrame:
    """Xử lý một TEST và trả về DataFrame từ trùng lặp đã lọc ignore."""
    test_dir = BASE_2023_ROOT / f"ETS2023_TEST{test_id}"
    txt_file = test_dir / "ETS2023.txt"
    dup_xlsx = test_dir / f"duplicate_words{test_id}.xlsx"
    vocab_out_xlsx = test_dir / f"vocabulary_ETS2023_{test_id}.xlsx"

    print(f"▶ Processing TEST{test_id} …")
    return process_vocabulary(
        form_path=FORM_FILE,
        text_path=txt_file,
        duplicates_path=dup_xlsx,
        cleaned_path=vocab_out_xlsx,
        ignore_path=IGNORE_FILE,
    )


def main() -> None:
    # gom kết quả từ tất cả TEST
    all_rows = [run_single_test(tid) for tid in TEST_IDS]

    if not all_rows:
        print("‼ Không tạo được DataFrame nào.")
        return

    df_master = (
        pd.concat(all_rows, ignore_index=True)
        .drop_duplicates(subset=["Từ vựng", "Dịch nghĩa"])
        .reset_index(drop=True)
    )
    # col3: đánh số block 5 từ một
    df_master["col3"] = df_master.index // 5 + 1
    df_master.to_excel(OUTPUT_UNIQUE, index=False)
    print(f"✔ Xuất hoàn tất: {OUTPUT_UNIQUE}")


if __name__ == "__main__":
    main()
