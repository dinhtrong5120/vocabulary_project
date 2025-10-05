import re


def replace_text(s):
    """Xử lý chuỗi để loại bỏ số trước "Question" và chuẩn hóa các ký tự xuống dòng."""
    # Xóa số trước "Questions" hoặc "Question"
    s = re.sub(r'\d+(?=Questions )', '', s)
    s = re.sub(r'\d+(?=Question )', '', s)

    # Chuẩn hóa ký tự xuống dòng như yêu cầu, thay thế \n khi có điều kiện
    return re.sub(r'\\n(?=W-Br|M-Cn|Câu hỏi|Questions |W-Am|M-Au|Question |\(A\) |\(B\) |\(C\) |\(c\) |\(D\) |\d+)',
                  '\n', s)


def write_string_to_txt(content, file_path):
    """Ghi chuỗi nội dung vào file ở file_path."""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def process_file(content, replacements):
    """Thực hiện tất cả các thao tác thay thế trên nội dung văn bản."""
    for old, new in replacements.items():
        content = content.replace(old, new)
    return content


def print_file_with_literal_newlines(file_path, output_path):
    """Đọc nội dung file, xử lý và ghi lại vào file mới."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Bước 1: Thực hiện các thay thế cần thiết
    replacements = {
        '\n': '\\n',
        'TEST 6 ': '',
        ' GO ON TO THE NEXTPAGE': ' ',
        'GO ON TO THE NEXTPAGE': ' ',
        'GO ON TO THE NEXT PAGE': ' ',
        'GO ON TO THENEXTPAGE': ' '
    }

    # Thực hiện thay thế trên chuỗi
    content_escaped_for_regex = process_file(content, replacements)

    # Bước 2: Áp dụng hàm replace_text để xử lý
    result_after_all_regex = replace_text(content_escaped_for_regex)

    # Bước 3: Thay thế các \n còn lại bằng dấu cách (hoặc có thể thay bằng chuỗi rỗng nếu muốn loại bỏ hoàn toàn)
    result_final_processed = result_after_all_regex.replace('\\n', ' ')

    # Ghi kết quả vào file
    write_string_to_txt(result_final_processed, output_path)


if __name__ == '__main__':
    input_file_path = r"C:\Users\User\Downloads\ETS2025\ETS2025_TEST1\ETS2025.txt"
    output_file_path = r"C:\Users\User\Downloads\ETS2025\ETS2025_TEST1\ETS2025_process.txt"
    print_file_with_literal_newlines(input_file_path, output_file_path)
