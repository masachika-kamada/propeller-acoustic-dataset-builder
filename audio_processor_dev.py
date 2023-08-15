import os
import matplotlib.pyplot as plt
import numpy as np
from pydub import AudioSegment
from matplotlib.widgets import Button
import simpleaudio as sa

def extract_audio_from_wav(file_path):
    return AudioSegment.from_wav(file_path)

def play_audio_segment(audio_segment):
    samples = np.array(audio_segment.get_array_of_samples())
    return sa.play_buffer(samples, 1, 2, audio_segment.frame_rate)

def stop_audio_playback(playback_obj):
    if playback_obj:
        playback_obj.stop()

def process_audio(input_audio_path, output_dir):
    final_audio_path = os.path.join(output_dir, "dst.wav")
    audio = extract_audio_from_wav(input_audio_path)
    audio = audio.split_to_mono()[0]
    samples = np.array(audio.get_array_of_samples())
    fs = audio.frame_rate

    fig, ax = plt.subplots(figsize=(14, 6))
    plt.subplots_adjust(bottom=0.2)
    ax.plot(np.linspace(0, len(samples) / fs, num=len(samples)), samples)
    ax.set_title("Select start and end points")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Amplitude")

    start_point, end_point = None, None
    selecting = "Start"
    current_playback = None

    def onclick(event):
        nonlocal start_point, end_point, current_playback
        if "Start" in selecting:
            start_point = event.xdata
            print(f"Start point: {start_point}, End point: {end_point}")
            segment_to_play = audio[int(start_point * 1000) : int(start_point * 1000) + 2000]
            current_playback = play_audio_segment(segment_to_play)
        else:
            end_point = event.xdata
            print(f"Start point: {start_point}, End point: {end_point}")
            segment_to_play = audio[int(end_point * 1000) - 2000 : int(end_point * 1000)]
            current_playback = play_audio_segment(segment_to_play)

    def toggle_selection(label):
        nonlocal selecting
        if label == "Start":
            selecting = "Start"
            start_button.color = "yellow"
            end_button.color = "lightgray"
        else:
            selecting = "End"
            end_button.color = "yellow"
            start_button.color = "lightgray"
        stop_audio_playback(current_playback)

    def save_audio(event):
        nonlocal start_point, end_point
        print(f"Saving audio from {start_point} to {end_point}")
        trimmed_audio = audio[int(start_point * 1000) : int(end_point * 1000)]
        trimmed_audio.export(final_audio_path, format="wav")
        print(f"Saved selected audio to {final_audio_path}")
        plt.close()

    save_button_ax = plt.axes([0.8, 0.05, 0.1, 0.04])
    save_button = Button(save_button_ax, "Save Audio", color="lightgoldenrodyellow", hovercolor="0.975")
    save_button.on_clicked(save_audio)

    start_button_ax = plt.axes([0.1, 0.05, 0.1, 0.04])
    start_button = Button(start_button_ax, "Start", color="yellow")
    start_button.on_clicked(toggle_selection)

    end_button_ax = plt.axes([0.21, 0.05, 0.1, 0.04])
    end_button = Button(end_button_ax, "End", color="lightgray")
    end_button.on_clicked(toggle_selection)

    cid = fig.canvas.mpl_connect("button_press_event", onclick)
    plt.show()
