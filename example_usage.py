#!/usr/bin/env python3
"""
Ví dụ sử dụng Audio Transcriber
Demo script cho việc sử dụng thư viện trong Python
"""

from audio_transcriber import AudioTranscriber


def example_basic():
    """Ví dụ cơ bản"""
    print("=" * 60)
    print("VÍ DỤ 1: Sử dụng cơ bản")
    print("=" * 60)

    # Tạo transcriber với model base
    transcriber = AudioTranscriber(model_name="base")

    # Xử lý file audio tiếng Việt
    transcriber.process_audio(
        audio_path="input.mp3",
        output_path="output.txt",
        language="vi"
    )


def example_high_quality():
    """Ví dụ với model chất lượng cao"""
    print("=" * 60)
    print("VÍ DỤ 2: Sử dụng model chất lượng cao")
    print("=" * 60)

    # Tạo transcriber với model small (chính xác hơn)
    transcriber = AudioTranscriber(model_name="small")

    # Xử lý file audio tiếng Việt
    transcriber.process_audio(
        audio_path="input.mp3",
        output_path="output_hq.txt",
        language="vi"
    )


def example_english():
    """Ví dụ với audio tiếng Anh"""
    print("=" * 60)
    print("VÍ DỤ 3: Xử lý audio tiếng Anh")
    print("=" * 60)

    # Tạo transcriber
    transcriber = AudioTranscriber(model_name="base")

    # Xử lý file audio tiếng Anh
    transcriber.process_audio(
        audio_path="english_audio.mp3",
        output_path="english_output.txt",
        language="en"
    )


def example_quiet_mode():
    """Ví dụ với chế độ im lặng"""
    print("=" * 60)
    print("VÍ DỤ 4: Chế độ im lặng")
    print("=" * 60)

    # Tạo transcriber với verbose=False
    transcriber = AudioTranscriber(model_name="base", verbose=False)

    # Xử lý audio
    success = transcriber.process_audio(
        audio_path="input.mp3",
        output_path="output.txt",
        language="vi"
    )

    if success:
        print("✓ Hoàn thành!")
    else:
        print("✗ Có lỗi xảy ra")


def example_batch_processing():
    """Ví dụ xử lý nhiều file"""
    print("=" * 60)
    print("VÍ DỤ 5: Xử lý nhiều file")
    print("=" * 60)

    # Danh sách các file cần xử lý
    audio_files = [
        "audio1.mp3",
        "audio2.mp3",
        "audio3.mp3"
    ]

    # Tạo transcriber một lần
    transcriber = AudioTranscriber(model_name="base")

    # Xử lý từng file
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\nXử lý file {i}/{len(audio_files)}: {audio_file}")

        output_file = audio_file.replace(".mp3", "_transcript.txt")

        try:
            transcriber.process_audio(
                audio_path=audio_file,
                output_path=output_file,
                language="vi"
            )
            print(f"✓ Đã xử lý: {audio_file} -> {output_file}")

        except Exception as e:
            print(f"✗ Lỗi khi xử lý {audio_file}: {str(e)}")


def example_read_output():
    """Ví dụ đọc kết quả output"""
    print("=" * 60)
    print("VÍ DỤ 6: Đọc và xử lý kết quả")
    print("=" * 60)

    # Giả sử đã có file output.txt
    try:
        with open("output.txt", "r", encoding="utf-8") as f:
            scenes = f.readlines()

        print(f"Tổng số cảnh: {len(scenes)}")
        print("\nNội dung các cảnh:")

        for i, scene in enumerate(scenes, 1):
            scene_text = scene.strip()
            print(f"  Cảnh {i}: {scene_text}")

    except FileNotFoundError:
        print("Chưa có file output.txt. Hãy chạy transcriber trước.")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DEMO: Audio Transcriber cho Tiếng Việt")
    print("=" * 60)
    print("\nCác ví dụ sử dụng:")
    print("1. example_basic() - Sử dụng cơ bản")
    print("2. example_high_quality() - Model chất lượng cao")
    print("3. example_english() - Xử lý tiếng Anh")
    print("4. example_quiet_mode() - Chế độ im lặng")
    print("5. example_batch_processing() - Xử lý nhiều file")
    print("6. example_read_output() - Đọc kết quả")
    print("\nĐể chạy ví dụ, gọi function tương ứng trong Python:")
    print("  from example_usage import example_basic")
    print("  example_basic()")
    print("\nHoặc chạy từng function trong file này.")
    print("=" * 60 + "\n")
