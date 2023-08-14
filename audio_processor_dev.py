import os
import matplotlib.pyplot as plt
import numpy as np
from pydub import AudioSegment, playback
from matplotlib.widgets import Button
import tempfile


def extract_audio_from_wav(file_path):
    return AudioSegment.from_wav(file_path)


def play_audio_segment(audio_segment):
    with tempfile.NamedTemporaryFile(delete=False, dir="tmp", suffix=".wav") as f:
        audio_segment.export(f.name, format="wav")
        playback._play_with_ffplay(f.name)
        os.remove(f.name)


def process_audio(input_audio_path, output_dir):
    impulse_check_path = os.path.join(output_dir, "audio_impulse_check.wav")
    final_audio_path = os.path.join(output_dir, "dst.wav")
    audio = extract_audio_from_wav(input_audio_path)
    samples = np.array(audio.get_array_of_samples())
    fs = audio.frame_rate

    fig, ax = plt.subplots(figsize=(15, 5))
    ax.plot(np.linspace(0, len(samples) / fs, num=len(samples)), samples)
    ax.set_title("Select start and end points")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Amplitude")

    start_point, end_point = [None], [None]

    def onclick(event):
        if start_point[0] is None:
            start_point[0] = event.xdata
            segment_to_play = audio[int(start_point[0] * 1000) : int(start_point[0] * 1000) + 5000]
            play_audio_segment(segment_to_play)
        elif end_point[0] is None:
            end_point[0] = event.xdata
            segment_to_play = audio[int(start_point[0] * 1000) : int(end_point[0] * 1000)]
            play_audio_segment(segment_to_play)

    def save_audio(event):
        trimmed_audio = audio[int(start_point[0] * 1000) : int(end_point[0] * 1000)]
        trimmed_audio.export(final_audio_path, format="wav")
        print(f"Saved selected audio to {final_audio_path}")
        plt.close()

    save_button_ax = plt.axes([0.8, 0.025, 0.1, 0.04])
    save_button = Button(save_button_ax, "Save Audio", color="lightgoldenrodyellow", hovercolor="0.975")
    save_button.on_clicked(save_audio)

    cid = fig.canvas.mpl_connect("button_press_event", onclick)
    plt.show()
