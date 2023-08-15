import os
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
from matplotlib.widgets import Button
import simpleaudio as sa


class AudioProcessor:
    def __init__(self, input_audio_path, output_dir):
        self.input_audio_path = input_audio_path
        self.output_dir = output_dir
        self.audio = self._extract_audio_from_wav().split_to_mono()[0]
        self.current_playback = None
        self.selecting_start = True
        self.points = [None, None]

    # Public methods
    def get_audio_length(self):
        if self.points[0] is not None and self.points[1] is not None:
            return self.points[1] - self.points[0]
        return None

    def process(self):
        samples = np.array(self.audio.get_array_of_samples())
        fs = self.audio.frame_rate

        fig, ax = plt.subplots(figsize=(14, 6))
        plt.subplots_adjust(bottom=0.2)
        ax.plot(np.linspace(0, len(samples) / fs, num=len(samples)), samples)
        ax.set_title("Select start and end points")
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Amplitude")

        self.start_button = self._create_button([0.1, 0.05, 0.1, 0.04], "Start", "yellow", self._select_start)
        self.end_button = self._create_button([0.21, 0.05, 0.1, 0.04], "End", "lightgray", self._select_end)
        self.save_button = self._create_button([0.8, 0.05, 0.1, 0.04], "Save Audio", "lightgoldenrodyellow", self._save_audio)

        cid = fig.canvas.mpl_connect("button_press_event", self._onclick)
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
        if self.selecting_start:
            return self.audio[int(point * 1000): int(point * 1000) + 2000]
        else:
            return self.audio[int(point * 1000) - 2000: int(point * 1000)]

    def _onclick(self, event):
        if event.inaxes in [self.start_button.ax, self.end_button.ax, self.save_button.ax]:
            return

        idx = 0 if self.selecting_start else 1
        self.points[idx] = event.xdata

        segment_to_play = self._get_audio_segment_to_play(self.points[idx])
        self.current_playback = self._play_audio_segment(segment_to_play)
        print(f"Start point: {self.points[0]}, End point: {self.points[1]}")

    def _select_start(self, event):
        self.selecting_start = True
        self._update_button_colors()
        self._stop_audio_playback()

    def _select_end(self, event):
        self.selecting_start = False
        self._update_button_colors()
        self._stop_audio_playback()

    def _update_button_colors(self):
        colors = ["yellow", "lightgray"] if self.selecting_start else ["lightgray", "yellow"]
        self.start_button.color = colors[0]
        self.end_button.color = colors[1]

    def _save_audio(self, event):
        final_audio_path = os.path.join(self.output_dir, "dst.wav")
        trimmed_audio = self.audio[int(self.points[0] * 1000): int(self.points[1] * 1000)]
        trimmed_audio.export(final_audio_path, format="wav")
        print(f"Saved selected audio to {final_audio_path}")
        plt.close()

    def _create_button(self, ax_position, label, color, callback):
        ax = plt.axes(ax_position)
        button = Button(ax, label, color=color)
        button.on_clicked(callback)
        return button
