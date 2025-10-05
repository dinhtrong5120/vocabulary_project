import os
import re
import warnings

warnings.filterwarnings("ignore")
import pandas as pd


def replace_words(text, replacements):
    pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in replacements.keys()) + r')\b')
    return pattern.sub(lambda x: replacements[x.group()], text)


def read_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
            # Chuyển đổi tất cả các ký tự thành chữ thường
            data = data.lower()
            # Chuỗi các ký tự cần loại bỏ
            chars_to_remove = [" Ms.", " Mr.", " ms.", " mr.", "A.M.", "’ve", "'ve", "A.M", "P.M.", "P.M", " p.m.",
                               " p.m", " pm.", " am.", ":", "：",
                               " a.m.", " a.m.", '’s', "'s", "'d", "’d", "n't", "n’t", "'ll", "’ll", '’m', "'m", '’re',
                               "'re", "n’t", ",", ".", "?", "----------", "---------", "--------", "-------", "------",
                               "-----", "----", "---", "--", "(", ")", "'", ":", "1", "2", "3", "4", "5", "6", "7", "8",
                               "9", "0", "[", "{", "]", "}", "%", "*", "/", ";", '"', "!", "–", "—", "#", "$", "&", "@",
                               '“', '”', "+", "<", ">", "一", "’", "^", "•", " - ", "- ", " -", "_", "★", "=", "►",
                               "test 10", "test 1", "test 2", "test 3", "test 4", "test 5", "test 6", "test 7","‘‘",
                               "test 8", "test 9", "part 1", "part 2", "part 3", "part 4", "part 5", "part 6", "part 7"]

            # Loại bỏ các ký tự trong chuỗi dữ liệu
            for char in chars_to_remove:
                data = data.replace(char, " ")
            for char in ["questions"]:
                data = data.replace(char, " questions")
            for char in ["  ", "   ", "    ", "  ", "  "]:
                data = data.replace(char, " ")
            for char in [' is ', ' am ', ' are ', ' was ', ' were ']:
                data = data.replace(char, " be ")

            for char in ["true"]:
                data = data.replace(char, "")
            replace_dict = {
                'has': 'have',
                'had': 'have',
                'did': 'do',
                'does': 'do',
                'made': 'make',
                'came': 'come',
                'began': 'begin',
                'broke': 'break',
                'broken': 'break',
                'breaking': 'break',
                'breaks': 'break',
                'taken': 'take',
                'took': 'take',
                'got': 'get',
                'caught': 'catch',
                'catching': 'catching',
                'went': 'go',
                'going': 'go',
                'kept': 'keep',
                'paid': 'pay',
                'saved': 'save',
                'saving': 'save',
                'holding': 'hold',
                'held': 'hold'
            }
            new_data = replace_words(data, replace_dict)
            return new_data
    except FileNotFoundError:
        print("File không tồn tại.")
        return None

def sort_by_appearance(big_string, sub_strings):
    # Lọc các chuỗi con thực sự có trong chuỗi lớn
    filtered = [s for s in sub_strings if s in big_string]
    # Sắp xếp theo vị trí xuất hiện đầu tiên
    sorted_list = sorted(filtered, key=lambda s: big_string.index(s))
    return sorted_list

def process_data(link_form_, link_file_txt_, duplicate_file, output_path, ignore_path):
    # Đọc dữ liệu từ file Excel
    df = pd.read_excel(link_form_)  # Đọc dữ liệu từ file Excel và lưu vào biến df
    df = df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    file_data = read_text_file(link_file_txt_)  # Đọc nội dung từ file txt
    file_data_ref = read_text_file(link_file_txt_)  # Đọc nội dung từ file txt
    # print(file_data)
    # Lấy danh sách từ vựng từ cột "Từ vựng" và loại bỏ các giá trị NaN
    vocab_list = list(set(
        df.dropna(subset=['Từ vựng', 'Dịch nghĩa'])['Từ vựng'].str.lower().tolist()
    ))
    # Tạo danh sách để lưu các từ trùng lặp
    duplicate_words = []

    # Khởi tạo một từ điển để lưu số lần xuất hiện của từ bị lặp trong file_data
    word_counts_in_file = {}

    if file_data:  # Kiểm tra nếu dữ liệu từ file txt có tồn tại
        # Lặp qua từng từ trong danh sách vocab_list
        for word in vocab_list:
            occurrences = re.findall(r'(?<![a-zA-Z])' + re.escape(str(word)) + r'(?![a-zA-Z])', file_data)

            # Đếm số lần từ xuất hiện và lưu vào từ điển
            word_counts_in_file[word] = len(occurrences)

            # Kiểm tra nếu từ này xuất hiện trong file_data
            if occurrences:
                duplicate_words.append(word)
                # Thực hiện việc thay thế từ đó trong file_data
                # print(word)
                file_data = re.sub(r'(?<![a-zA-Z])' + re.escape(word + " ") + r'(?![a-zA-Z])', '', file_data)
        # print(file_data)
        # Chuyển danh sách duplicate_words thành DataFrame
        duplicate_df = df[df['Từ vựng'].str.lower().isin(duplicate_words)]
        # Thêm cột 'count' vào DataFrame duplicate_df với số lần từ bị lặp trong file_data
        duplicate_df['count'] = duplicate_df['Từ vựng'].apply(lambda x: word_counts_in_file.get(x, 0))
        my_list_1 = duplicate_df['Từ vựng'].tolist()
        my_list = set(my_list_1)
        result = sort_by_appearance(file_data_ref, my_list)
        df_sorted = duplicate_df.set_index('Từ vựng').loc[result].reset_index()

        # Lưu DataFrame vào file Excel

        df_sorted_1 = df_sorted.sort_index(ascending=False)
        # df_sorted_1.to_excel(duplicate_file, index=False)
        # print(df_sorted_1)
        split_data = file_data.split()
        unique_strings = list(set(split_data))
        unique_strings_new = []
        unique_strings_new = unique_strings
        chars_to_remove = [",", ".", "?", "(", ")", "'", ":", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "[",
                           "{", "]", "}", "%", "*", "/", ";", '"', "!", "--", "—", "#", "$", "&", "@", '“',
                           '”', "+", "<", "-", "’", '•', "°", "|", "£", "=", "^", "®", "_", "_", "★", "_", "■"]
        # Loại bỏ các chuỗi có độ dài lớn hơn 15
        unique_strings_xxx = []
        for string in unique_strings_new:
            if 15 >= len(string) >= 4:
                unique_strings_xxx.append(string)

        # Tạo DataFrame mới từ list các dictionaries chứa dữ liệu
        new_data = [{'Từ vựng': string} for string in unique_strings_xxx if string not in df['Từ vựng'].values]
        if new_data:
            new_df = pd.DataFrame(new_data)
            # Nối DataFrame mới với DataFrame cũ
            df = pd.concat([df, new_df], ignore_index=True)

    # Lưu DataFrame mới vào file Excel
    df_ignore = pd.read_excel(ignore_path)
    ignore_list = df_ignore.dropna(subset=['Từ vựng'])['Từ vựng'].str.lower().tolist()
    ignore_list_end = ignore_list

    ignore_list_no_s = [item[:-1] if item.endswith('s') else item for item in ignore_list]
    ignore_list_no_d = [item[:-1] if item.endswith('d') else item for item in ignore_list]
    ignore_list_no_y = [item[:-1] if item.endswith('y') else item for item in ignore_list]
    ignore_list_no_es = [item[:-2] if item.endswith('es') else item for item in ignore_list]
    ignore_list_no_ed = [item[:-2] if item.endswith('ed') else item for item in ignore_list]
    ignore_list_no_ly = [item[:-2] if item.endswith('ly') else item for item in ignore_list]
    ignore_list_no_ing = [item[:-3] if item.endswith('ing') else item for item in ignore_list]

    ignore_list = ignore_list + ignore_list_no_s + ignore_list_no_d + ignore_list_no_es + ignore_list_no_ed + ignore_list_no_ly + ignore_list_no_ing

    ignore_list_s = [item + 's' for item in ignore_list]
    ignore_list_es = [item + 'es' for item in ignore_list]
    ignore_list_ies = [item + 'ies' for item in ignore_list]
    ignore_list_ed = [item + 'ed' for item in ignore_list]
    ignore_list_d = [item + 'd' for item in ignore_list]
    ignore_list_ly = [item + 'ly' for item in ignore_list]
    ignore_list_ing = [item + 'ing' for item in ignore_list]

    ignore_list = ignore_list + ignore_list_s + ignore_list_es + ignore_list_ed + ignore_list_d + ignore_list_ly + \
                  ignore_list_ing + ignore_list_end + ignore_list_no_y + ignore_list_ies
    ignore_list = list(set(ignore_list))
    df = df[~df['Từ vựng'].isin(ignore_list)]
    df_sorted_2 = df_sorted_1[~df_sorted_1['Từ vựng'].isin(ignore_list)]
    df_sorted_2.to_excel(duplicate_file, index=False)
    print(df_sorted_2)
    df.to_excel(output_path, sheet_name='Sheet1', index=False)
    return df_sorted_2





if __name__ == '__main__':
    df_1 = pd.DataFrame()
    for i in range(5, 7):
        print(f"ETS2023_TEST{i + 1}")
        if i == 5:
            BASE_PATH = fr"C:\Users\User\Downloads\ETS2023\ETS2023_TEST0"
            link_form = os.path.join(BASE_PATH, f"vocabulary_ETS2023_0.xlsx")
        else:
            BASE_PATH = fr"C:\Users\User\Downloads\ETS2023\ETS2023_TEST{i}"
            link_form = os.path.join(BASE_PATH, f"vocabulary_ETS2023_{i}.xlsx")
        USE_PATH = fr"C:\Users\User\Downloads\ETS2023\ETS2023_TEST{i + 1}"

        # link_form la file ma da tong hop tu moi roi

        link_file_txt = os.path.join(USE_PATH, "ETS2023.txt")
        duplicate_file = os.path.join(USE_PATH, f"duplicate_words{i + 1}.xlsx")
        output_path = os.path.join(USE_PATH, f"vocabulary_ETS2023_{i + 1}.xlsx")
        ignore_path = r"D:\Project_o_nha\New folder\ignore (3).xlsx"

        df_result = process_data(link_form, link_file_txt, duplicate_file, output_path, ignore_path)
        df_1 = pd.concat([df_1, df_result], ignore_index=True)
    df_unique = df_1.drop_duplicates(["Từ vựng", "Dịch nghĩa"], keep='first')
    df_unique.to_excel('df_unique.xlsx', index=False)