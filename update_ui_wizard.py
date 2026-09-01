import re

with open('ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

start_idx = content.find('class SetupOverlay(QWidget):')
end_idx = content.find('class CircleMask(QWidget):')

new_overlay = '''class SetupOverlay(QWidget):
    done = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            SetupOverlay {{
                background: rgba(0, 6, 10, 245);
                border: 1px solid {C.BORDER_B};
                border-radius: 6px;
            }}
        """)

        detected = {"darwin": "mac", "windows": "windows"}.get(
            _OS.lower(), "linux"
        )
        self._sel_os = detected

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 22, 30, 22)
        layout.setSpacing(8)

        def _lbl(txt, font_size=9, bold=False, color=C.PRI,
                 align=Qt.AlignmentFlag.AlignCenter):
            w = QLabel(txt)
            w.setAlignment(align)
            w.setFont(QFont("Courier New", font_size,
                            QFont.Weight.Bold if bold else QFont.Weight.Normal))
            w.setStyleSheet(f"color: {color}; background: transparent;")
            return w

        layout.addWidget(_lbl("Welcome to E.V.O", 15, True))
        layout.addWidget(_lbl("Your Personal AI Assistant", 9, color=C.PRI_DIM))
        layout.addSpacing(6)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C.BORDER};"); layout.addWidget(sep)
        layout.addSpacing(8)

        layout.addWidget(_lbl("To get started, please enter your free Gemini API key below.", 9, color=C.TEXT_DIM))
        
        link_lbl = QLabel('<a href="https://aistudio.google.com" style="color: #00ffcc; text-decoration: none;">Get your free key at aistudio.google.com</a>')
        link_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        link_lbl.setFont(QFont("Courier New", 9))
        link_lbl.setOpenExternalLinks(True)
        link_lbl.setStyleSheet("background: transparent;")
        layout.addWidget(link_lbl)
        
        layout.addSpacing(12)

        self._key_input = QLineEdit()
        self._key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._key_input.setPlaceholderText("Paste your API key here...")
        self._key_input.setFont(QFont("Courier New", 10))
        self._key_input.setFixedHeight(34)
        self._key_input.setStyleSheet(f"""
            QLineEdit {{
                background: #000d12; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 4px; padding: 4px 8px;
            }}
            QLineEdit:focus {{ border: 1px solid {C.PRI}; }}
        """)
        layout.addWidget(self._key_input)
        layout.addSpacing(16)

        btn = QPushButton("Start E.V.O")
        btn.setFixedHeight(36)
        btn.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C.PRI};
                border: 1px solid {C.PRI_DIM}; border-radius: 4px;
            }}
            QPushButton:hover {{
                background: {C.PRI_GHO}; border: 1px solid {C.PRI};
            }}
        """)
        btn.clicked.connect(self._submit)
        layout.addWidget(btn)
        layout.addStretch()

    def _submit(self):
        key = self._key_input.text().strip()
        if not key:
            self._key_input.setStyleSheet(f"""
                QLineEdit {{
                    background: #000d12; color: {C.TEXT};
                    border: 1px solid {C.RED}; border-radius: 4px; padding: 4px 8px;
                }}
            """)
            return
        self.done.emit(key, self._sel_os)

'''

content = content[:start_idx] + new_overlay + content[end_idx:]

with open('ui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("SetupOverlay updated in ui.py")
