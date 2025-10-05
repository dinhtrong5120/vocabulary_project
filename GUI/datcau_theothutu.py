import sys
import random
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton


class FlashcardApp(QWidget):
    def __init__(self, excel_file):
        super().__init__()
        self.setWindowTitle('Flashcard Học Từ Vựng')

        # Thiết lập kích thước tối đa của cửa sổ
        self.setMaximumWidth(700)

        # Đọc dữ liệu từ file Excel
        # self.data = pd.read_excel(excel_file, usecols=[0, 1, 2], engine='openpyxl', sheet_name='Sheet1')
        self.data = pd.read_excel(excel_file)
        self.data.columns = ['A', 'C', 'LESSON']
        # self.data = self.data[self.data['LESSON'] == 15]
        self.data = self.data[self.data['LESSON'].isin([1])]

        # Danh sách từ vựng và nghĩa
        self.words = self.data['A'].tolist()
        self.meanings = self.data['C'].tolist()

        # Chỉ mục từ vựng
        self.current_position = 0
        self.show_meaning = False

        # Thiết lập giao diện
        self.layout = QVBoxLayout()
        self.label = QLabel('', self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 24px;")
        self.label.setWordWrap(True)

        self.button = QPushButton('Hiển thị nghĩa', self)
        self.button.setFixedHeight(50)
        self.button.clicked.connect(self.toggle_card)
        self.next_button = QPushButton('Từ kế tiếp', self)
        self.next_button.setFixedHeight(50)
        self.next_button.clicked.connect(self.next_card)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.next_button)

        self.setLayout(self.layout)
        self.update_card()

    def update_card(self):
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
    excel_file = 'all_duplicate_ets2023_20250801_234855.xlsx'  # Đường dẫn tới file Excel của bạn
    flashcard_app = FlashcardApp(excel_file)
    flashcard_app.show()
    sys.exit(app.exec_())
