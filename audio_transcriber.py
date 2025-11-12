#!/usr/bin/env python3
"""
Audio Segmentation and Transcription Tool
Trích xuất audio thành các đoạn 8 giây và transcribe thành Script
"""

import os
import sys
import argparse
from pathlib import Path
from pydub import AudioSegment
import whisper
import tempfile


class AudioTranscriber:
    def __init__(self, model_name="base"):
        """
        Khởi tạo Audio Transcriber

        Args:
            model_name: Tên model Whisper (tiny, base, small, medium, large)
        """
        print(f"Đang tải model Whisper '{model_name}'...")
        self.model = whisper.load_model(model_name)
        self.segment_duration = 8000  # 8 giây = 8000 milliseconds

    def load_audio(self, audio_path):
        """
        Load file audio

        Args:
            audio_path: Đường dẫn đến file audio

        Returns:
            AudioSegment object
        """
        print(f"Đang load file audio: {audio_path}")

        # Hỗ trợ nhiều định dạng audio
        file_ext = Path(audio_path).suffix.lower()

        if file_ext == '.mp3':
            audio = AudioSegment.from_mp3(audio_path)
        elif file_ext == '.wav':
            audio = AudioSegment.from_wav(audio_path)
        elif file_ext in ['.m4a', '.mp4']:
            audio = AudioSegment.from_file(audio_path, format='m4a')
        elif file_ext == '.ogg':
            audio = AudioSegment.from_ogg(audio_path)
        elif file_ext == '.flac':
            audio = AudioSegment.from_file(audio_path, format='flac')
        else:
            # Thử load với format tự động
            audio = AudioSegment.from_file(audio_path)

        return audio

    def split_audio(self, audio):
        """
        Chia audio thành các đoạn 8 giây

        Args:
            audio: AudioSegment object

        Returns:
            List of AudioSegment (mỗi segment 8 giây)
        """
        total_duration = len(audio)  # milliseconds
        segments = []

        print(f"Tổng độ dài audio: {total_duration / 1000:.2f} giây")
        print(f"Đang chia audio thành các đoạn {self.segment_duration / 1000} giây...")

        # Chia audio thành các đoạn 8 giây
        for i in range(0, total_duration, self.segment_duration):
            segment = audio[i:i + self.segment_duration]
            segments.append(segment)

        print(f"Đã chia thành {len(segments)} đoạn")
        return segments

    def transcribe_segment(self, segment, segment_index, temp_dir):
        """
        Transcribe một đoạn audio

        Args:
            segment: AudioSegment object
            segment_index: Index của segment (để hiển thị progress)
            temp_dir: Thư mục tạm để lưu file audio

        Returns:
            Transcription text
        """
        # Xuất segment ra file tạm
        temp_file = os.path.join(temp_dir, f"segment_{segment_index}.wav")
        segment.export(temp_file, format="wav")

        # Transcribe bằng Whisper
        result = self.model.transcribe(temp_file, language="vi")  # Có thể thay đổi language

        # Xóa file tạm
        os.remove(temp_file)

        return result["text"].strip()

    def process_audio(self, audio_path, output_path, language="vi"):
        """
        Xử lý toàn bộ audio: chia segments và transcribe

        Args:
            audio_path: Đường dẫn file audio đầu vào
            output_path: Đường dẫn file text đầu ra
            language: Ngôn ngữ của audio (vi, en, ...)
        """
        # Load audio
        audio = self.load_audio(audio_path)

        # Chia audio thành segments
        segments = self.split_audio(audio)

        # Tạo thư mục tạm
        with tempfile.TemporaryDirectory() as temp_dir:
            transcriptions = []

            print("\nĐang transcribe các đoạn audio...")
            for i, segment in enumerate(segments, 1):
                print(f"Đang xử lý cảnh {i}/{len(segments)}...")

                # Transcribe segment
                text = self.transcribe_segment(segment, i, temp_dir)

                if text:  # Chỉ thêm nếu có nội dung
                    transcriptions.append(text)
                    print(f"  Cảnh {i}: {text[:50]}..." if len(text) > 50 else f"  Cảnh {i}: {text}")
                else:
                    print(f"  Cảnh {i}: (không có âm thanh)")

        # Xuất kết quả ra file
        self.export_transcriptions(transcriptions, output_path)

        print(f"\n✓ Hoàn thành! Đã lưu Script vào: {output_path}")
        print(f"✓ Tổng số cảnh: {len(transcriptions)}")

    def export_transcriptions(self, transcriptions, output_path):
        """
        Xuất transcriptions ra file text
        Mỗi cảnh trên 1 dòng, không có dòng trống

        Args:
            transcriptions: List of transcription texts
            output_path: Đường dẫn file output
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for text in transcriptions:
                f.write(text + '\n')


def main():
    parser = argparse.ArgumentParser(
        description='Trích xuất audio thành các đoạn 8 giây và transcribe thành Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  python audio_transcriber.py input.mp3 output.txt
  python audio_transcriber.py input.mp3 output.txt --model small
  python audio_transcriber.py input.mp3 output.txt --language en
        """
    )

    parser.add_argument('input', help='Đường dẫn file audio đầu vào')
    parser.add_argument('output', help='Đường dẫn file text đầu ra')
    parser.add_argument('--model', default='base',
                        choices=['tiny', 'base', 'small', 'medium', 'large'],
                        help='Model Whisper (mặc định: base)')
    parser.add_argument('--language', default='vi',
                        help='Ngôn ngữ của audio (mặc định: vi)')

    args = parser.parse_args()

    # Kiểm tra file đầu vào
    if not os.path.exists(args.input):
        print(f"Lỗi: Không tìm thấy file '{args.input}'")
        sys.exit(1)

    # Tạo thư mục output nếu chưa tồn tại
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Xử lý audio
    transcriber = AudioTranscriber(model_name=args.model)
    transcriber.process_audio(args.input, args.output, language=args.language)


if __name__ == "__main__":
    main()
