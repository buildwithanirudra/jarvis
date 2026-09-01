import re, json

with open('ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add _restart_audio_sig to MainWindow
content = content.replace('    _error_sig = pyqtSignal(str, str, str)', '    _error_sig = pyqtSignal(str, str, str)\n    _restart_audio_sig = pyqtSignal()')

# Add restart_audio_sig to JarvisUI properties
jarvisui_prop = '''
    @property
    def _error_sig(self):
        """Proxy to MainWindow._error_sig so main.py can emit it thread-safely."""
        return self._win._error_sig

    @property
    def _restart_audio_sig(self):
        return self._win._restart_audio_sig
'''
content = content.replace('''
    @property
    def _error_sig(self):
        """Proxy to MainWindow._error_sig so main.py can emit it thread-safely."""
        return self._win._error_sig''', jarvisui_prop)

# Replace SettingsDialog
start_idx = content.find('class SettingsDialog(QDialog):')
end_idx = content.find('class MainWindow(QMainWindow):')

new_dialog = '''class SettingsDialog(QDialog):
    test_result_sig = pyqtSignal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("E.V.O - Settings")
        self.setFixedSize(450, 580)
        self.setStyleSheet(f"""
            QDialog {{
                background: {C.BG};
                border: 1px solid {C.BORDER_B};
            }}
        """)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self._parent_win = parent
        self.current_key = self._load_current_key()
        self.is_masked = True

        main_scroll = QScrollArea(self)
        main_scroll.setWidgetResizable(True)
        main_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        main_scroll.setWidget(scroll_content)

        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(main_scroll)

        # Header Label
        hdr_lbl = QLabel("◈  E.V.O SYSTEM CONFIGURATION")
        hdr_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr_lbl.setFont(QFont("Courier New", 11, QFont.Weight.Bold))
        hdr_lbl.setStyleSheet(f"color: {C.PRI}; background: transparent; border: none;")
        layout.addWidget(hdr_lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C.BORDER}; border: none; background: {C.BORDER}; height: 1px;")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        # --- API KEY SECTION ---
        api_lbl = QLabel("API KEY CONFIGURATION")
        api_lbl.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        api_lbl.setStyleSheet(f"color: {C.TEXT}; background: transparent; border: none; margin-top: 10px;")
        layout.addWidget(api_lbl)

        cur_key_layout = QHBoxLayout()
        cur_key_layout.setSpacing(6)
        
        self.key_display = QLineEdit()
        self.key_display.setReadOnly(True)
        self.key_display.setFont(QFont("Courier New", 9))
        self.key_display.setFixedHeight(30)
        self.key_display.setStyleSheet(f"""
            QLineEdit {{
                background: #000d12; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 3px; padding: 4px 8px;
            }}
        """)
        cur_key_layout.addWidget(self.key_display)

        self.reveal_btn = QPushButton("Reveal")
        self.reveal_btn.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        self.reveal_btn.setFixedSize(70, 30)
        self.reveal_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reveal_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C.PANEL}; color: {C.PRI};
                border: 1px solid {C.PRI_DIM}; border-radius: 3px;
            }}
            QPushButton:hover {{
                background: {C.PRI_GHO}; border: 1px solid {C.PRI};
            }}
        """)
        self.reveal_btn.clicked.connect(self._toggle_reveal)
        cur_key_layout.addWidget(self.reveal_btn)
        
        layout.addLayout(cur_key_layout)
        self._update_mask_display()

        self.new_key_input = QLineEdit()
        self.new_key_input.setPlaceholderText("Paste new API key here...")
        self.new_key_input.setFont(QFont("Courier New", 9))
        self.new_key_input.setFixedHeight(30)
        self.new_key_input.setStyleSheet(f"""
            QLineEdit {{
                background: #000d12; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 3px; padding: 4px 8px;
            }}
            QLineEdit:focus {{ border: 1px solid {C.PRI}; }}
        """)
        layout.addWidget(self.new_key_input)

        btn_layout = QHBoxLayout()
        self.test_btn = QPushButton("Test API Key")
        self.test_btn.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        self.test_btn.setFixedHeight(34)
        self.test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.test_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {C.ACC2}; border: 1px solid {C.ACC2}; border-radius: 3px; }} QPushButton:hover {{ background: rgba(255, 204, 0, 30); }}")
        self.test_btn.clicked.connect(self._test_key)
        btn_layout.addWidget(self.test_btn)

        self.save_btn = QPushButton("Save & Reconnect")
        self.save_btn.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        self.save_btn.setFixedHeight(34)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {C.PRI}; border: 1px solid {C.PRI_DIM}; border-radius: 3px; }} QPushButton:hover {{ background: {C.PRI_GHO}; border: 1px solid {C.PRI}; }}")
        self.save_btn.clicked.connect(self._save_and_reconnect)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"color: {C.BORDER}; border: none; background: {C.BORDER}; height: 1px; margin-top: 10px; margin-bottom: 10px;")
        sep2.setFixedHeight(21)
        layout.addWidget(sep2)

        # --- DEVICES SECTION ---
        dev_lbl = QLabel("HARDWARE DEVICES")
        dev_lbl.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        dev_lbl.setStyleSheet(f"color: {C.TEXT}; background: transparent; border: none;")
        layout.addWidget(dev_lbl)

        # Load settings
        self.settings_data = {"mic_device_index": None, "speaker_device_index": None, "camera_index": 0}
        if SETTINGS_FILE.exists():
            try:
                self.settings_data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass

        cb_style = f"""
            QComboBox {{
                background: #000d12; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 3px; padding: 4px 8px;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background: #000d12; color: {C.TEXT}; selection-background-color: {C.PRI_DIM};
            }}
        """

        # Microphone
        layout.addWidget(self._mk_lbl("Microphone (Input):"))
        self.mic_cb = QComboBox()
        self.mic_cb.setStyleSheet(cb_style)
        self.mic_cb.setFixedHeight(30)
        self._mic_ids = [None]
        self.mic_cb.addItem("Default (Windows system default)")
        try:
            import sounddevice as sd
            for i, d in enumerate(sd.query_devices()):
                if d['max_input_channels'] > 0:
                    self._mic_ids.append(i)
                    self.mic_cb.addItem(f"[{i}] {d['name']}")
        except Exception:
            pass
        if self.settings_data.get("mic_device_index") in self._mic_ids:
            self.mic_cb.setCurrentIndex(self._mic_ids.index(self.settings_data["mic_device_index"]))
        layout.addWidget(self.mic_cb)

        # Speaker
        layout.addWidget(self._mk_lbl("Speaker (Output):"))
        self.spk_cb = QComboBox()
        self.spk_cb.setStyleSheet(cb_style)
        self.spk_cb.setFixedHeight(30)
        self._spk_ids = [None]
        self.spk_cb.addItem("Default (Windows system default)")
        try:
            import sounddevice as sd
            for i, d in enumerate(sd.query_devices()):
                if d['max_output_channels'] > 0:
                    self._spk_ids.append(i)
                    self.spk_cb.addItem(f"[{i}] {d['name']}")
        except Exception:
            pass
        if self.settings_data.get("speaker_device_index") in self._spk_ids:
            self.spk_cb.setCurrentIndex(self._spk_ids.index(self.settings_data["speaker_device_index"]))
        layout.addWidget(self.spk_cb)

        # Camera
        layout.addWidget(self._mk_lbl("Camera:"))
        self.cam_cb = QComboBox()
        self.cam_cb.setStyleSheet(cb_style)
        self.cam_cb.setFixedHeight(30)
        self._cam_ids = [0]
        self.cam_cb.addItem("Default (Camera 0)")
        try:
            import cv2
            for i in range(1, 6):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    self._cam_ids.append(i)
                    self.cam_cb.addItem(f"Camera {i}")
                    cap.release()
        except Exception:
            pass
        if self.settings_data.get("camera_index") in self._cam_ids:
            self.cam_cb.setCurrentIndex(self._cam_ids.index(self.settings_data["camera_index"]))
        layout.addWidget(self.cam_cb)

        # Audio Restart Button
        self.audio_btn = QPushButton("Apply & Restart Audio")
        self.audio_btn.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        self.audio_btn.setFixedHeight(34)
        self.audio_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.audio_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {C.WHITE}; border: 1px solid {C.WHITE}; border-radius: 3px; margin-top: 5px; }} QPushButton:hover {{ background: rgba(255, 255, 255, 30); }}")
        self.audio_btn.clicked.connect(self._apply_audio)
        layout.addWidget(self.audio_btn)

        self.status_lbl = QLabel("")
        self.status_lbl.setFont(QFont("Courier New", 8))
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("background: transparent; border: none; margin-top: 5px;")
        layout.addWidget(self.status_lbl)

        layout.addStretch()
        self.test_result_sig.connect(self._on_test_result)

    def _mk_lbl(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent; border: none; margin-top: 5px;")
        return lbl

    def _load_current_key(self) -> str:
        if API_FILE.exists():
            try:
                d = json.loads(API_FILE.read_text(encoding="utf-8"))
                return d.get("gemini_api_key", "")
            except Exception:
                pass
        return ""

    def _toggle_reveal(self):
        self.is_masked = not self.is_masked
        self._update_mask_display()

    def _update_mask_display(self):
        if self.is_masked:
            if len(self.current_key) > 4:
                val = "*" * (len(self.current_key) - 4) + self.current_key[-4:]
            else:
                val = "*" * len(self.current_key)
            self.key_display.setText(val)
            self.reveal_btn.setText("Reveal")
        else:
            self.key_display.setText(self.current_key)
            self.reveal_btn.setText("Hide")

    def _test_key(self):
        new_key = self.new_key_input.text().strip()
        key_to_test = new_key if new_key else self.current_key
        if not key_to_test:
            self.status_lbl.setText("No API key to test.")
            self.status_lbl.setStyleSheet(f"color: {C.RED}; background: transparent; border: none;")
            return

        self.status_lbl.setText("Testing API key...")
        self.status_lbl.setStyleSheet(f"color: {C.ACC2}; background: transparent; border: none;")
        self.test_btn.setEnabled(False)

        def run_test():
            try:
                from google import genai
                test_client = genai.Client(api_key=key_to_test)
                test_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="test"
                )
                self.test_result_sig.emit(True, "API key is valid and working")
            except Exception as e:
                err_msg = str(e)
                if "API_KEY_INVALID" in err_msg or "400" in err_msg or "401" in err_msg or "403" in err_msg:
                    msg = "API key failed: Invalid key."
                elif "Quota exceeded" in err_msg or "429" in err_msg:
                    msg = "API key failed: Rate limit exceeded."
                else:
                    msg = f"API key failed: {err_msg[:60]}"
                self.test_result_sig.emit(False, msg)

        import threading
        threading.Thread(target=run_test, daemon=True).start()

    def _on_test_result(self, success: bool, message: str):
        self.test_btn.setEnabled(True)
        self.status_lbl.setText(message)
        if success:
            self.status_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent; border: none;")
        else:
            self.status_lbl.setStyleSheet(f"color: {C.RED}; background: transparent; border: none;")

    def _save_and_reconnect(self):
        new_key = self.new_key_input.text().strip()
        if new_key:
            try:
                import os
                os.makedirs(CONFIG_DIR, exist_ok=True)
                config_data = {}
                if API_FILE.exists():
                    try:
                        config_data = json.loads(API_FILE.read_text(encoding="utf-8"))
                    except Exception:
                        pass
                config_data["gemini_api_key"] = new_key
                import platform
                if "os_system" not in config_data:
                    detected = {"darwin": "mac", "windows": "windows"}.get(platform.system().lower(), "linux")
                    config_data["os_system"] = detected

                API_FILE.write_text(json.dumps(config_data, indent=4), encoding="utf-8")
                self.current_key = new_key
                self._update_mask_display()
                self.new_key_input.clear()
                self.status_lbl.setText("API key saved. Reconnecting...")
                self.status_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent; border: none;")
            except Exception as e:
                self.status_lbl.setText(f"Failed to save key: {e}")
                self.status_lbl.setStyleSheet(f"color: {C.RED}; background: transparent; border: none;")
                return
        else:
            self.status_lbl.setText("Reconnecting with current key...")
            self.status_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent; border: none;")

        if self._parent_win:
            self._parent_win.reconnect_evo()
            
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1000, self.accept)

    def _apply_audio(self):
        self.settings_data["mic_device_index"] = self._mic_ids[self.mic_cb.currentIndex()]
        self.settings_data["speaker_device_index"] = self._spk_ids[self.spk_cb.currentIndex()]
        self.settings_data["camera_index"] = self._cam_ids[self.cam_cb.currentIndex()]
        try:
            import os
            os.makedirs(CONFIG_DIR, exist_ok=True)
            SETTINGS_FILE.write_text(json.dumps(self.settings_data, indent=4), encoding="utf-8")
            self.status_lbl.setText("Devices saved. Restarting audio...")
            self.status_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent; border: none;")
            if self._parent_win:
                self._parent_win._restart_audio_sig.emit()
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1500, self.accept)
        except Exception as e:
            self.status_lbl.setText(f"Failed to save devices: {e}")
            self.status_lbl.setStyleSheet(f"color: {C.RED}; background: transparent; border: none;")

'''

content = content[:start_idx] + new_dialog + content[end_idx:]

with open('ui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Success')
