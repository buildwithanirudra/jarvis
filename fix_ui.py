import re

with open('ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

wrong_class = '''class MainWindow(QMainWindow):
    _log_sig   = pyqtSignal(str)
    _stream_sig = pyqtSignal(str, bool, str)
    _state_sig = pyqtSignal(str)
    _error_sig = pyqtSignal(str, str, str)
    _restart_audio_sig = pyqtSignal()

    def __init__(self, face_path: str):
        super().__init__()
        self.setWindowTitle("E.V.O — Your Personal AI")
        self.setMinimumSize(_MIN_W, _MIN_H)
        self.resize(_DEFAULT_W, _DEFAULT_H)'''

content = content.replace(wrong_class + '\n\n', '')
content = content.replace(wrong_class + '\n', '')
content = content.replace(wrong_class, '')

old_real = '''class MainWindow(QMainWindow):
    _log_sig   = pyqtSignal(str)
    _stream_sig = pyqtSignal(str, bool, str)
    _state_sig = pyqtSignal(str)
    _error_sig = pyqtSignal(str, str, str)
    _restart_audio_sig = pyqtSignal()

    def __init__(self, face_path: str):
        super().__init__()
        self.setWindowTitle("E.V.O")'''

new_real = '''class MainWindow(QMainWindow):
    _log_sig   = pyqtSignal(str)
    _stream_sig = pyqtSignal(str, bool, str)
    _state_sig = pyqtSignal(str)
    _error_sig = pyqtSignal(str, str, str)
    _restart_audio_sig = pyqtSignal()

    def __init__(self, face_path: str):
        super().__init__()
        self.setWindowTitle("E.V.O — Your Personal AI")'''

content = content.replace(old_real, new_real)

with open('ui.py', 'w', encoding='utf-8') as f:
    f.write(content)
