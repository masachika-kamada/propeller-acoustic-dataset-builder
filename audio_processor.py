import os

import matplotlib.pyplot as plt
import numpy as np
import simpleaudio as sa
from matplotlib.widgets import Button, SpanSelector
from pydub import AudioSegment


class AudioProcessor:
    def __init__(self, input_audio_path, output_dir):
        self.input_audio_path = input_audio_path
        self.output_audio_path = os.path.join(output_dir, "dst.wav")
        self.audio = self._extract_audio_from_wav().split_to_mono()[0]
        self.current_playback = None
        self.start_modes = ["impulse", "manual"]
        self.end_modes = ["20sec", "manual"]
        self.current_start_mode = self.start_modes[0]
        self.current_end_mode = self.end_modes[0]
        self.current_mode = "start"
        self.points = [None, None]
        self.preview_ms = 500
        self.margin_sec = 0.5

    # Public methods
    def get_audio_length(self):
        if self.points[0] is not None and self.points[1] is not None:
            return self.points[1] - self.points[0]
        return None

    def process(self):
        os.makedirs(os.path.dirname(self.output_audio_path), exist_ok=True)

        samples = np.array(self.audio.get_array_of_samples())
        fs = self.audio.frame_rate

        fig, ax = plt.subplots(figsize=(14, 6))
        self.ax = ax  # Store ax for later use with SpanSelector
        plt.subplots_adjust(bottom=0.2)
        ax.plot(np.linspace(0, len(samples) / fs, num=len(samples)), samples)
        ax.set_title(os.path.basename(self.input_audio_path))
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Amplitude")

        self.start_button = self._create_button([0.13, 0.05, 0.12, 0.04], f"Start ({self.current_start_mode})",
                                                "yellow", self._select_start)
        self.end_button = self._create_button([0.26, 0.05, 0.12, 0.04], f"End ({self.current_end_mode})",
                                              "lightgray", self._select_end)
        self.save_button = self._create_button([0.8, 0.05, 0.1, 0.04], "Save Audio", "yellow", self._save_audio)

        if self.current_start_mode == "impulse":
            self.span = SpanSelector(self.ax, self._onselect, "horizontal", useblit=True)

        _ = fig.canvas.mpl_connect("button_press_event", self._onclick)
        plt.show()

    # Private helper methods
    def _extract_audio_from_wav(self):
        return AudioSegment.from_wav(self.input_audio_path)

    def _play_audio_segment(self, segment):
        samples = np.array(segment.get_array_of_samples())
        return sa.play_buffer(samples, 1, 2, segment.frame_rate)

    def _stop_audio_playback(self):
        if self.current_playback:
            self.current_playback.stop()

    def _get_audio_segment_to_play(self, point):
        point_in_ms = int(point * 1000)
        if self.current_mode == "start":
            return self.audio[point_in_ms : min(len(self.audio), point_in_ms + self.preview_ms)]
        elif self.current_mode == "end":
            return self.audio[max(0, point_in_ms - self.preview_ms) : point_in_ms]

    def _onclick(self, event):
        if event.inaxes in [self.start_button.ax, self.end_button.ax, self.save_button.ax] or \
           (self.current_mode == "end" and self.current_end_mode == "20sec") or \
           (self.current_mode == "start" and self.current_start_mode == "impulse") or \
           (event.xdata is None or event.xdata < 0 or event.xdata > self.audio.duration_seconds):
            return

        idx = 0 if self.current_mode == "start" else 1
        self.points[idx] = event.xdata

        segment_to_play = self._get_audio_segment_to_play(self.points[idx])
        self.current_playback = self._play_audio_segment(segment_to_play)
        print(f"Start point: {self.points[0]}, End point: {self.points[1]}")

    def _onselect(self, start, end):
        samples = np.array(self.audio.get_array_of_samples())
        fs = self.audio.frame_rate
        start_idx, end_idx = int(start * fs), int(end * fs)
        max_idx = start_idx + np.argmax(np.abs(samples[start_idx:end_idx]))
        self.points[0] = max_idx / fs + self.margin_sec

        offset = self.preview_ms / 1000 / 2 + self.margin_sec
        segment_to_play = self._get_audio_segment_to_play(max(0, self.points[0] - offset))
        self.current_playback = self._play_audio_segment(segment_to_play)
        print(f"Start point: {self.points[0]}, End point: {self.points[1]}")
        self._update_button_colors()

    def _select_start(self, event):
        if self.current_mode == "start":
            idx = (self.start_modes.index(self.current_start_mode) + 1) % len(self.start_modes)
            self.current_start_mode = self.start_modes[idx]
            self.start_button.label.set_text(f"Start ({self.current_start_mode})")
        else:
            self.current_mode = "start"

        if self.current_start_mode == "impulse":
            self.span = SpanSelector(self.ax, self._onselect, "horizontal", useblit=True)
        else:
            # Disable span selector if exists
            if hasattr(self, "span"):
                self.span.set_active(False)
        self._update_button_colors()
        self._stop_audio_playback()

    def _select_end(self, event):
        if self.current_mode == "end":
            idx = (self.end_modes.index(self.current_end_mode) + 1) % len(self.end_modes)
            self.current_end_mode = self.end_modes[idx]
            self.end_button.label.set_text(f"End ({self.current_end_mode})")
        else:
            self.current_mode = "end"

        # Disable span selector if exists
        if hasattr(self, "span"):
            self.span.set_active(False)

        self._update_button_colors()
        self._stop_audio_playback()

    def _update_button_colors(self):
        if self.current_mode == "start":
            self.start_button.color = "yellow"
            self.end_button.color = "lightgray"
        elif self.current_mode == "end":
            self.end_button.color = "yellow"
            self.start_button.color = "lightgray"

    def _save_audio(self, event):
        if self.current_end_mode == "20sec" and self.points[0] is not None:
            desired_end_point = self.points[0] + 20
            if desired_end_point * 1000 > len(self.audio):
                print(f"Cannot extract 20 sec from the selected start point. "
                      f"Only {len(self.audio) / 1000 - self.points[0]:.2f} sec remains.")
                return
            else:
                self.points[1] = desired_end_point
        trimmed_audio = self.audio[int(self.points[0] * 1000): int(self.points[1] * 1000)]
        trimmed_audio.export(self.output_audio_path, format="wav")
        print(f"Saved selected audio to {self.output_audio_path}")
        plt.close()

    def _create_button(self, ax_position, label, color, callback):
        ax = plt.axes(ax_position)
        button = Button(ax, label, color=color)
        button.on_clicked(callback)
        return button
