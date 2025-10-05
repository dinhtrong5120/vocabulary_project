import re

def replace_text(s):
    # Biểu thức chính quy đã được cập nhật:
    # Thêm `\d+` vào danh sách các điều kiện trong lookahead.
    # Điều này đảm bảo rằng nếu `\n` được theo sau bởi một số, nó cũng sẽ được khớp
    # và thay thế bằng `\n` (tức là được giữ nguyên trong ngữ cảnh chuẩn hóa).
    return re.sub(r'\\n(?=W-Br|M-Cn|Câu hỏi|Questions |W-Am|M-Au|Question |\(A\) |\(B\) |\(C\) |\(c\) |\(D\) |\d+)', '\n', s)

def write_string_to_txt(content, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def print_file_with_literal_newlines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Bước 1: Thay thế ký tự xuống dòng thực sự trong nội dung đọc được
    # bằng chuỗi ký tự `\n` để nó được xử lý bởi regex sau đó.
    # Nếu không làm bước này, regex `\\n` sẽ không khớp với ký tự xuống dòng thực tế.
    # Đây là điểm quan trọng cần lưu ý dựa trên cách bạn dùng `repr` và `replace('\n', '\\n')`.
    content_escaped_for_regex = content.replace('\n', '\\n')
    content_escaped_for_regex = content_escaped_for_regex.replace('TEST 6 ', '')
    content_escaped_for_regex = content_escaped_for_regex.replace(' GO ON TO THE NEXTPAGE', ' ')
    content_escaped_for_regex = content_escaped_for_regex.replace('GO ON TO THE NEXTPAGE', ' ')

    print("--- Chuỗi sau khi chuyển đổi \\n để regex nhận diện ---")
    print(content_escaped_for_regex)

    # Bước 2: Áp dụng hàm replace_text để chuẩn hóa `\\n` thành `\n`
    # tại các vị trí mong muốn (bao gồm trước số).
    result_after_regex = replace_text(content_escaped_for_regex)

    print("\n--- Chuỗi sau khi hàm replace_text xử lý ---")
    print(result_after_regex)

    # Bước 3: Thay thế tất cả các `\\n` còn lại (những cái không khớp với regex)
    # bằng một dấu cách (hoặc chuỗi rỗng nếu bạn muốn loại bỏ chúng hoàn toàn).
    # Việc này ngụ ý rằng các `\\n` không được giữ lại (vì không khớp với regex) thì sẽ bị xóa/thay thế.
    result_final_processed = result_after_regex.replace('\\n', ' ')

    print("\n--- Chuỗi cuối cùng sau khi thay thế các \\n còn lại bằng dấu cách ---")
    print(result_final_processed)

    # Ghi kết quả cuối cùng vào file
    write_string_to_txt(result_final_processed, r"C:\Users\User\Downloads\ETS2023\ETS2023_TEST6\ETS2023_lol_lol.txt")

# Ví dụ dùng
file_path = r"C:\Users\User\Downloads\ETS2023\ETS2023_TEST6\ETS2023 - Copy.txt"
print_file_with_literal_newlines(file_path)