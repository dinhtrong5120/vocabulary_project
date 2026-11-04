import sys
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton


class FlashcardApp(QWidget):
    def __init__(self, excel_file):
        super().__init__()
        self.setWindowTitle('Flashcard Học Từ Vựng')

        # Thiết lập kích thước tối đa của cửa sổ
        self.setMaximumWidth(700)

        self.data = pd.read_excel(excel_file)
        if {'Từ vựng hoặc cụm từ', 'Dịch nghĩa'}.issubset(self.data.columns):
            columns = ['Từ vựng hoặc cụm từ', 'Dịch nghĩa']
        else:
            columns = ['Nội dung câu hỏi', 'Giải thích']
            columns += [f'Phương án {i}' for i in range(1, 5)]
            if not set(columns).issubset(self.data.columns):
                raise ValueError('File Excel cần có các cột từ vựng/nghĩa hoặc câu hỏi/giải thích và 4 phương án.')

        self.data = self.data.dropna(subset=columns)
        if self.data.empty:
            raise ValueError('File Excel không có dòng dữ liệu đầy đủ để học.')

        # Danh sách từ vựng và nghĩa
        self.words = self.data[columns[0]].astype(str).tolist()
        self.meanings = self.data[columns[1]].astype(str).tolist()
        self.word_types = (
            self.data['Phân loại'].fillna('').astype(str).tolist()
            if 'Phân loại' in self.data.columns else [''] * len(self.data)
        )
        if len(columns) > 2:
            for index, options in enumerate(self.data[columns[2:]].itertuples(index=False, name=None)):
                self.words[index] += '\n\n' + '\n'.join(
                    f'{letter}. {option}' for letter, option in zip('ABCD', options)
                )

        # Chỉ mục từ vựng
        self.current_position = 0
        self.show_meaning = False

        # Thiết lập giao diện
        self.layout = QVBoxLayout()
        self.label = QLabel('', self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 24px;")
        self.label.setWordWrap(True)
        self.type_label = QLabel('', self)
        self.type_label.setAlignment(Qt.AlignCenter)
        self.type_label.setStyleSheet('font-size: 18px; color: #666666;')
        self.type_label.setWordWrap(True)

        self.button = QPushButton('Hiển thị nghĩa', self)
        self.button.setFixedHeight(50)
        self.button.clicked.connect(self.toggle_card)
        self.next_button = QPushButton('Từ kế tiếp', self)
        self.next_button.setFixedHeight(50)
        self.next_button.clicked.connect(self.next_card)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.type_label)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.next_button)

        self.setLayout(self.layout)
        self.update_card()

    def update_card(self):
        word_type = self.word_types[self.current_position]
        self.type_label.setText(f'{word_type}' if word_type else '')
        self.type_label.setVisible(bool(word_type))
        if self.show_meaning:
            self.label.setText(self.meanings[self.current_position])
            self.button.setText('Hiển thị từ')
            self.setFixedWidth(1000)
        else:
            self.label.setText(self.words[self.current_position])
            self.button.setText('Hiển thị nghĩa')
            self.setFixedWidth(1000)

    def toggle_card(self):
        self.show_meaning = not self.show_meaning
        self.update_card()

    def next_card(self):
        self.current_position += 1
        if self.current_position >= len(self.words):
            self.current_position = 0
        self.show_meaning = False
        self.update_card()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown:
            self.next_card()
        elif event.key() == Qt.Key_PageUp:
            self.toggle_card()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    excel_file = '/Users/TrongKieu/Developer/study/English/ETS_2023/TEST1/bang_tu_vung_part5_test1_2023.xlsx'
    flashcard_app = FlashcardApp(excel_file)
    flashcard_app.show()
    sys.exit(app.exec_())
