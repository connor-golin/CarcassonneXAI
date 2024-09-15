import sys
import ollama
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QWidget, QFrame)
from PyQt6.QtGui import QTextCursor, QColor, QFont, QPalette
from PyQt6.QtCore import pyqtSignal, QObject, QThread, Qt
from markdown2 import Markdown

class StreamWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, message):
        super().__init__()
        self.message = message

    def run(self):
        try:
            stream = ollama.chat(
                model='llama3.1',
                messages=[{'role': 'user', 'content': self.message}],
                stream=True,
            )

            for chunk in stream:
                content = chunk['message']['content']
                self.progress.emit(content)
            
            self.finished.emit()
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")
            self.finished.emit()

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat with LLAMA")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QTextEdit, QLineEdit {
                background-color: #2D2D2D;
                color: #E0E0E0;
                border: 1px solid #3E3E3E;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0063B1;
            }
        """)

        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Segoe UI", 10))

        self.user_input = QLineEdit(self)
        self.user_input.setPlaceholderText("Type your message here...")
        self.user_input.setFont(QFont("Segoe UI", 10))

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setFont(QFont("Segoe UI", 10))

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(self.send_button)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.user_input.returnPressed.connect(self.send_message)

        self.thread = None
        self.worker = None
        self.last_message = ""
        self.user_messages = []
        self.bot_messages = []

    def send_message(self):
        user_message = self.user_input.text()
        if user_message:
            self.display_message("You: " + user_message, "#3498db")  # Light blue for user
            self.user_input.clear()
            self.get_ai_response(user_message)
            self.user_messages.append(user_message)

    def display_message(self, message, color):
        self.chat_display.setTextColor(QColor(color))
        self.chat_display.append(message)
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)

    def update_chat_display(self, text):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()
        self.last_message += text

    def get_ai_response(self, message):
        self.display_message("LLAMA: ", "#2ecc71")  # Light green for AI
        self.thread = QThread()
        self.worker = StreamWorker(message)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.update_chat_display)
        self.thread.finished.connect(self.on_response_finished)
        self.thread.start()

    def on_response_finished(self):
        markdowner = Markdown()
        self.last_message = markdowner.convert(self.last_message)
        self.bot_messages.append(self.last_message)

        # Update chat display with all messages
        self.chat_display.clear()
        for i in range(len(self.user_messages)):
            self.display_message("You: " + self.user_messages[i], "#3498db")
            self.display_message("LLAMA: " + self.bot_messages[i], "#2ecc71")
        
        # move cursor to end
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)

        # Clear last message
        self.last_message = ""

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())