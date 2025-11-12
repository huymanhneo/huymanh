#!/usr/bin/env python3
"""
Audio Segmentation and Transcription Tool
Trích xuất audio thành các đoạn 8 giây và transcribe thành Script
"""

import os
import sys
import argparse
import re
from pathlib import Path
from pydub import AudioSegment
import whisper
import tempfile
from tqdm import tqdm


class AudioTranscriber:
    def __init__(self, model_name="base", verbose=True):
        """
        Khởi tạo Audio Transcriber

        Args:
            model_name: Tên model Whisper (tiny, base, small, medium, large)
            verbose: Hiển thị thông tin chi tiết
        """
        self.verbose = verbose
        if verbose:
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

    def clean_vietnamese_text(self, text):
        """
        Làm sạch và chuẩn hóa text tiếng Việt

        Args:
            text: Text cần làm sạch

        Returns:
            Text đã được làm sạch
        """
        if not text:
            return ""

        # Loại bỏ khoảng trắng thừa
        text = re.sub(r'\s+', ' ', text)

        # Loại bỏ khoảng trắng đầu cuối
        text = text.strip()

        # Đảm bảo chữ cái đầu viết hoa (nếu có)
        if text and text[0].isalpha():
            text = text[0].upper() + text[1:]

        # Loại bỏ dấu câu thừa
        text = re.sub(r'([.,!?])\1+', r'\1', text)

        return text

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

    def transcribe_segment(self, segment, segment_index, temp_dir, language="vi"):
        """
        Transcribe một đoạn audio

        Args:
            segment: AudioSegment object
            segment_index: Index của segment (để hiển thị progress)
            temp_dir: Thư mục tạm để lưu file audio
            language: Ngôn ngữ của audio

        Returns:
            Transcription text
        """
        try:
            # Xuất segment ra file tạm
            temp_file = os.path.join(temp_dir, f"segment_{segment_index}.wav")
            # Tắt progress bar của pydub/ffmpeg để tránh nhiễu UI
            segment.export(temp_file, format="wav", parameters=["-loglevel", "quiet"])

            # Transcribe bằng Whisper với các tham số tối ưu cho tiếng Việt
            result = self.model.transcribe(
                temp_file,
                language=language,
                task="transcribe",
                fp16=False,  # Tắt fp16 để tăng độ chính xác
                verbose=False
            )

            # Xóa file tạm
            os.remove(temp_file)

            # Làm sạch text
            text = self.clean_vietnamese_text(result["text"])

            return text

        except Exception as e:
            if self.verbose:
                print(f"  Lỗi khi transcribe cảnh {segment_index}: {str(e)}")
            return ""

    def process_audio(self, audio_path, output_path, language="vi"):
        """
        Xử lý toàn bộ audio: chia segments và transcribe

        Args:
            audio_path: Đường dẫn file audio đầu vào
            output_path: Đường dẫn file text đầu ra
            language: Ngôn ngữ của audio (vi, en, ...)
        """
        try:
            # Load audio
            audio = self.load_audio(audio_path)

            # Chia audio thành segments
            segments = self.split_audio(audio)

            # Tạo thư mục tạm
            with tempfile.TemporaryDirectory() as temp_dir:
                transcriptions = []

                print(f"\nĐang transcribe các đoạn audio (Ngôn ngữ: {language})...")

                # Sử dụng tqdm để hiển thị progress bar
                for i, segment in enumerate(tqdm(segments, desc="Transcribing", unit="cảnh"), 1):
                    # Transcribe segment
                    text = self.transcribe_segment(segment, i, temp_dir, language=language)

                    if text:  # Chỉ thêm nếu có nội dung
                        transcriptions.append(text)
                        if self.verbose:
                            preview = text[:60] + "..." if len(text) > 60 else text
                            tqdm.write(f"  Cảnh {i}: {preview}")
                    else:
                        if self.verbose:
                            tqdm.write(f"  Cảnh {i}: (không có âm thanh)")

            # Xuất kết quả ra file
            self.export_transcriptions(transcriptions, output_path)

            print(f"\n✓ Hoàn thành! Đã lưu Script vào: {output_path}")
            print(f"✓ Tổng số cảnh: {len(transcriptions)}")
            print(f"✓ Độ dài trung bình: {sum(len(t) for t in transcriptions) / len(transcriptions):.0f} ký tự/cảnh" if transcriptions else "")

            return True

        except Exception as e:
            print(f"\n✗ Lỗi: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

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
        description='Trích xuất audio thành các đoạn 8 giây và transcribe thành Script (Tối ưu cho tiếng Việt)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  # Sử dụng cơ bản (tiếng Việt)
  python audio_transcriber.py input.mp3 output.txt

  # Sử dụng model chính xác hơn
  python audio_transcriber.py input.mp3 output.txt --model small

  # Audio tiếng Anh
  python audio_transcriber.py input.mp3 output.txt --language en

  # Tự động detect ngôn ngữ
  python audio_transcriber.py input.mp3 output.txt --language auto

  # Chế độ im lặng
  python audio_transcriber.py input.mp3 output.txt --quiet

Lưu ý:
  - Model 'tiny' nhanh nhất nhưng ít chính xác với tiếng Việt
  - Model 'base' cân bằng giữa tốc độ và độ chính xác (khuyến nghị)
  - Model 'small' trở lên chính xác hơn nhưng chậm hơn
  - Lần đầu chạy sẽ tải model (100MB-3GB)
        """
    )

    parser.add_argument('input', help='Đường dẫn file audio đầu vào')
    parser.add_argument('output', help='Đường dẫn file text đầu ra')
    parser.add_argument('--model', default='base',
                        choices=['tiny', 'base', 'small', 'medium', 'large'],
                        help='Model Whisper (mặc định: base, khuyến nghị: small cho tiếng Việt)')
    parser.add_argument('--language', default='vi',
                        help='Ngôn ngữ của audio (vi, en, auto, ... - mặc định: vi)')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Chế độ im lặng, chỉ hiển thị kết quả cuối')

    args = parser.parse_args()

    # Banner
    if not args.quiet:
        print("=" * 60)
        print("Audio Segmentation & Transcription Tool")
        print("Trích xuất audio thành các đoạn 8 giây và transcribe")
        print("=" * 60)

    # Kiểm tra file đầu vào
    if not os.path.exists(args.input):
        print(f"✗ Lỗi: Không tìm thấy file '{args.input}'")
        sys.exit(1)

    # Kiểm tra định dạng file
    valid_extensions = ['.mp3', '.wav', '.m4a', '.mp4', '.ogg', '.flac', '.aac']
    file_ext = Path(args.input).suffix.lower()
    if file_ext not in valid_extensions:
        print(f"⚠ Cảnh báo: File extension '{file_ext}' có thể không được hỗ trợ")
        print(f"   Các định dạng được khuyến nghị: {', '.join(valid_extensions)}")

    # Tạo thư mục output nếu chưa tồn tại
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        if not args.quiet:
            print(f"✓ Đã tạo thư mục: {output_dir}")

    # Xử lý language auto
    language = args.language if args.language != 'auto' else None

    # Xử lý audio
    try:
        transcriber = AudioTranscriber(model_name=args.model, verbose=not args.quiet)
        success = transcriber.process_audio(args.input, args.output, language=language or 'vi')

        if success:
            if not args.quiet:
                print("\n" + "=" * 60)
                print("Hoàn thành!")
                print("=" * 60)
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n✗ Đã bị ngắt bởi người dùng")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Lỗi không mong đợi: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
