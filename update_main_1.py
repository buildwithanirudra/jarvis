import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add SETTINGS_FILE
content = content.replace(
    'API_FILE   = CONFIG_DIR / "api_keys.json"',
    'API_FILE   = CONFIG_DIR / "api_keys.json"\nSETTINGS_FILE = CONFIG_DIR / "settings.json"'
)

# 2. Rename out_queue to audio_queue and remove maxsize
content = content.replace('self.out_queue        = asyncio.Queue(maxsize=3)', 'self.audio_queue      = asyncio.Queue()')
content = content.replace('self.out_queue', 'self.audio_queue')
# Wait, let's just make sure out_queue is fully replaced.
# In _send_realtime: msg = await self.audio_queue.get() is fine.
# In _listen_audio: self.audio_queue.put_nowait is fine.

# 3. Add _on_restart_audio to JarvisLive
# Let's insert it before def request_reconnect(self):
restart_audio_method = '''
    def _on_restart_audio(self):
        """Triggered from UI to restart audio streams."""
        if hasattr(self, '_restart_event') and self._restart_event:
            self._loop.call_soon_threadsafe(self._restart_event.set)

    def request_reconnect(self):'''
content = content.replace('    def request_reconnect(self):', restart_audio_method)

# Connect _restart_audio_sig in run()
content = content.replace(
    'self.ui.on_text_command  = self._on_text_command',
    'self.ui.on_text_command  = self._on_text_command\n        try:\n            self.ui._restart_audio_sig.connect(self._on_restart_audio)\n        except Exception:\n            pass'
)

# Also create self._restart_event in run()
content = content.replace(
    'self._turn_done_event = asyncio.Event()',
    'self._turn_done_event = asyncio.Event()\n                    self._restart_event   = asyncio.Event()'
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Basic replacements done")
