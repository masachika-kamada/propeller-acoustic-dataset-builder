import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import SpanSelector
from pydub import AudioSegment


def extract_audio_from_wav(file_path):
    return AudioSegment.from_wav(file_path)


def process_audio(input_audio_path, output_dir):
    # Paths for output files
    impulse_check_path = os.path.join(output_dir, "audio_impulse_check.wav")
    final_audio_path = os.path.join(output_dir, "dst.wav")

    # Extract audio from the WAV file
    audio = extract_audio_from_wav(input_audio_path)
    samples = np.array(audio.get_array_of_samples())

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
        trimmed_audio.export(impulse_check_path, format="wav")

        # Extract final audio
        start_final_audio_time_sec = max_idx / fs + 0.5
        end_final_audio_time_sec = start_final_audio_time_sec + 20
        final_audio = audio[start_final_audio_time_sec * 1000 : end_final_audio_time_sec * 1000]
        final_audio.export(final_audio_path, format="wav")

        print(f"Saved impulse check audio to {impulse_check_path}")
        print(f"Saved final audio to {final_audio_path}")
        plt.close()

    span = SpanSelector(ax, onselect, "horizontal", useblit=True)
    plt.show()
