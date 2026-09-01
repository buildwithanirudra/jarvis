import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace _listen_audio
start_idx = content.find('    async def _listen_audio(self):')
end_idx = content.find('    async def _receive_audio(self):')

listen_audio_new = '''    async def _listen_audio(self):
        print("[E.V.O] 🎤 Mic started")
        loop = asyncio.get_event_loop()

        while True:
            self._restart_event.clear()
            mic_idx = None
            try:
                import json
                if SETTINGS_FILE.exists():
                    d = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
                    mic_idx = d.get("mic_device_index")
            except Exception:
                pass
            
            actual_rate = SEND_SAMPLE_RATE
            dev_name = "System Default"

            try:
                import sounddevice as sd
                if mic_idx is not None:
                    info = sd.query_devices(mic_idx)
                    actual_rate = int(info['default_samplerate'])
                    dev_name = info['name']
                else:
                    info = sd.query_devices(kind='input')
                    actual_rate = int(info['default_samplerate'])
                    dev_name = info['name']
            except Exception as e:
                print(f"[E.V.O] ⚠️ Mic {mic_idx} failed: {e}. Falling back to default.")
                mic_idx = None
                try:
                    import sounddevice as sd
                    info = sd.query_devices(kind='input')
                    actual_rate = int(info['default_samplerate'])
                    dev_name = info['name']
                except Exception:
                    actual_rate = SEND_SAMPLE_RATE

            needs_resample = (actual_rate != SEND_SAMPLE_RATE)
            if needs_resample:
                try:
                    from scipy.signal import resample_poly
                    import math
                    _gcd = math.gcd(SEND_SAMPLE_RATE, actual_rate)
                    _up   = SEND_SAMPLE_RATE // _gcd
                    _down = actual_rate       // _gcd
                except ImportError:
                    print("[E.V.O] ⚠️ scipy not installed — resampling disabled.")
                    needs_resample = False

            def callback(indata, frames, time_info, status):
                with self._speaking_lock:
                    jarvis_speaking = self._is_speaking
                if jarvis_speaking or self.ui.muted:
                    return
                if needs_resample:
                    import numpy as np
                    mono = indata[:, 0] if indata.ndim > 1 else indata.flatten()
                    resampled = resample_poly(mono, _up, _down).astype("int16")
                    data = resampled.tobytes()
                else:
                    data = indata.copy().tobytes()
                loop.call_soon_threadsafe(
                    self.audio_queue.put_nowait,
                    {"data": data, "mime_type": "audio/pcm"}
                )

            try:
                import sounddevice as sd
                with sd.InputStream(
                    device=mic_idx,
                    samplerate=actual_rate,
                    channels=1,
                    dtype="int16",
                    blocksize=CHUNK_SIZE,
                    callback=callback,
                ):
                    print(f"[E.V.O] 🎤 Mic stream open on {dev_name} ({actual_rate}Hz)")
                    await self._restart_event.wait()
            except Exception as e:
                print(f"[E.V.O] ❌ Mic stream error: {e}")
                # Don't spin rapidly on failure
                try:
                    await asyncio.wait_for(self._restart_event.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    pass

'''
content = content[:start_idx] + listen_audio_new + content[end_idx:]

# Replace _play_audio
start_play = content.find('    async def _play_audio(self):')
end_play = content.find('    async def _on_text_command(self, text: str):')
if end_play == -1: # just to be safe
    end_play = content.find('    def request_reconnect(self):')
    if end_play == -1:
        end_play = content.find('    def _on_restart_audio(self):')

play_audio_new = '''    async def _play_audio(self):
        print("[E.V.O] 🔊 Play task started")
        import numpy as np

        while True:
            self._restart_event.clear()
            spk_idx = None
            try:
                import json
                if SETTINGS_FILE.exists():
                    d = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
                    spk_idx = d.get("speaker_device_index")
            except Exception:
                pass

            try:
                import sounddevice as sd
                with sd.OutputStream(
                    device=spk_idx,
                    samplerate=24000,
                    channels=1,
                    dtype="int16",
                    blocksize=0,
                    latency="low"
                ) as stream:
                    _silence = np.zeros(1024, dtype=np.int16)
                    while not self._restart_event.is_set():
                        try:
                            chunk = await asyncio.wait_for(self.audio_in_queue.get(), timeout=0.2)
                            self.set_speaking(True)
                            audio_array = np.frombuffer(chunk, dtype=np.int16)
                            stream.write(audio_array)
                            print(f"[E.V.O] 🔊 Playing chunk: {len(chunk)} bytes")
                            
                            if self.audio_in_queue.empty():
                                stream.write(_silence)
                                self.set_speaking(False)
                        except asyncio.TimeoutError:
                            pass
            except Exception as e:
                print(f"[E.V.O] ❌ Speaker stream error: {e}")
                try:
                    await asyncio.wait_for(self._restart_event.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    pass

'''
content = content[:start_play] + play_audio_new + content[end_play:]

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Second replacements done")
