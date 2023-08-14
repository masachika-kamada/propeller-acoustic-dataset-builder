import os
import cv2
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import SpanSelector
from pydub import AudioSegment


def extract_audio_from_mov(file_path):
    return AudioSegment.from_file(file_path)


def convert_stereo_to_mono(samples):
    return samples[::2] + samples[1::2]


def trim_video(file_path, start_time_sec, end_time_sec, output_path):
    cap = cv2.VideoCapture(file_path)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    cap.set(cv2.CAP_PROP_POS_MSEC, start_time_sec * 1000)

    while cap.get(cv2.CAP_PROP_POS_MSEC) < end_time_sec * 1000:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()


def process_video(input_video_path, output_dir):
    output_video_path = os.path.join(output_dir, "video_for_ocr.mp4")
    output_audio_path = os.path.join(output_dir, "video_impulse_check.wav")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    audio = extract_audio_from_mov(input_video_path)
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = convert_stereo_to_mono(samples)

    fs = audio.frame_rate
    duration = len(samples) / fs
    fig, ax = plt.subplots(figsize=(15, 5))
    ax.plot(np.linspace(0, duration, num=len(samples)), samples)
    ax.set_title("Audio Waveform")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Amplitude")

    def onselect(xmin, xmax):
        start_idx = int(xmin * fs)
        end_idx = int(xmax * fs)
        max_idx = start_idx + np.argmax(np.abs(samples[start_idx:end_idx]))

        # Save audio signal for verification
        start_audio_time_sec = max_idx / fs - 1.5
        end_audio_time_sec = max_idx / fs + 1.5
        trimmed_audio = audio[start_audio_time_sec * 1000 : end_audio_time_sec * 1000]
        trimmed_audio.export(output_audio_path, format="wav")

        # Extract video
        start_video_time_sec = max_idx / fs + 0.5
        end_video_time_sec = start_video_time_sec + 20
        trim_video(input_video_path, start_video_time_sec, end_video_time_sec, output_video_path)

        print(f"Saved audio to {output_audio_path}")
        print(f"Saved video to {output_video_path}")
        plt.close()

    span = SpanSelector(ax, onselect, "horizontal", useblit=True)
    plt.show()
