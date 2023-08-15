import os
from audio_processor import AudioProcessor
from video_processor import process_video


def get_video_and_audio_paths(input_dir):
    video_extensions = [".mov", ".mp4"]
    audio_extensions = [".wav"]

    video_path = None
    audio_path = None

    for filename in os.listdir(input_dir):
        # Convert the filename to lowercase before checking its extension
        lowercase_filename = filename.lower()
        if any(lowercase_filename.endswith(ext) for ext in video_extensions):
            video_path = os.path.join(input_dir, filename)
        elif any(lowercase_filename.endswith(ext) for ext in audio_extensions):
            audio_path = os.path.join(input_dir, filename)

    if not video_path:
        raise ValueError("No video file found in the specified directory.")
    if not audio_path:
        raise ValueError("No audio file found in the specified directory.")

    return video_path, audio_path


def main():
    input_dir = "data/raw/propeller/p2000_2"
    output_dir = input_dir.replace("raw", "processed")
    input_video_path, input_audio_path = get_video_and_audio_paths(input_dir)

    audio_processor = AudioProcessor(input_audio_path, output_dir)
    audio_processor.process()
    audio_length = audio_processor.get_audio_length()

    # process_video(input_video_path, output_dir)


if __name__ == "__main__":
    main()
