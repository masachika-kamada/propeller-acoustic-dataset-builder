import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import simpleaudio as sa
from matplotlib.widgets import Button, SpanSelector
from pydub import AudioSegment


class VideoProcessor:
    def __init__(self, input_video_path, output_dir, duration_sec=20):
        self.input_video_path = input_video_path
        self.output_video_path = os.path.join(output_dir, "video_for_ocr.mp4")
        self.audio = self._extract_audio_from_video()
        self.samples = np.array(self.audio.get_array_of_samples())
        if self.audio.channels == 2:
            self.samples = self._convert_stereo_to_mono(self.samples)
        self.start_point = None
        self.duration_sec = duration_sec
        self.preview_ms = 500
        self.margin_sec = 0.5

    def process(self):
        os.makedirs(os.path.dirname(self.output_video_path), exist_ok=True)

        fs = self.audio.frame_rate
        duration = len(self.samples) / fs
        fig, ax = plt.subplots(figsize=(14, 6))
        plt.subplots_adjust(bottom=0.2)
        ax.plot(np.linspace(0, duration, num=len(self.samples)), self.samples)
        ax.set_title(os.path.basename(self.input_video_path))
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Amplitude")

        self.span = SpanSelector(ax, self._onselect, "horizontal", useblit=True)
        self.save_button = self._create_button([0.8, 0.05, 0.1, 0.04], "Save Video", "yellow", self._save_video)
        plt.show()

    def _extract_audio_from_video(self):
        return AudioSegment.from_file(self.input_video_path)

    def _convert_stereo_to_mono(self, samples):
        # return samples[::2] + samples[1::2]
        return (samples[::2] + samples[1::2]) // 2

    def _play_audio_segment(self, segment):
        samples = np.array(segment.get_array_of_samples())
        return sa.play_buffer(samples, 1, 2, segment.frame_rate)

    def _get_audio_segment_to_play(self, point):
        point_in_ms = int(point * 1000)
        preview_start = max(0, point_in_ms - self.preview_ms / 2)
        preview_end = min(len(self.audio), point_in_ms + self.preview_ms / 2)
        return self.audio[preview_start : preview_end]

    def _onselect(self, xmin, xmax):
        start_idx = int(xmin * self.audio.frame_rate)
        end_idx = int(xmax * self.audio.frame_rate)
        max_idx = start_idx + np.argmax(np.abs(self.samples[start_idx:end_idx]))
        self.start_point = max_idx / self.audio.frame_rate + self.margin_sec

        segment_to_play = self._get_audio_segment_to_play(max_idx / self.audio.frame_rate)
        self.current_playback = self._play_audio_segment(segment_to_play)

    def _trim_video(self, start_time_sec, end_time_sec):
        cap = cv2.VideoCapture(self.input_video_path)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(self.output_video_path, fourcc, fps, (width, height))

        cap.set(cv2.CAP_PROP_POS_MSEC, start_time_sec * 1000)

        while cap.get(cv2.CAP_PROP_POS_MSEC) < end_time_sec * 1000:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)

        cap.release()
        out.release()

    def _save_video(self, event):
        if self.start_point is not None:
            print(f"Saving video to {self.output_video_path}")
            self._trim_video(self.start_point, self.start_point + self.duration_sec)
            print(f"Saved video to {self.output_video_path}")
            plt.close()
        else:
            print("Please select a range first.")

    def _create_button(self, ax_position, label, color, callback):
        ax = plt.axes(ax_position)
        button = Button(ax, label, color=color)
        button.on_clicked(callback)
        return button
