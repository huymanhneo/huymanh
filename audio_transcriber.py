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
        import torch

        self.verbose = verbose

        # Kiểm tra và sử dụng GPU nếu có
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        if verbose:
            if self.device == "cuda":
                gpu_name = torch.cuda.get_device_name(0)
                print(f"✓ Đang sử dụng GPU: {gpu_name}")
            else:
                print("⚠ Đang sử dụng CPU (không có GPU)")
            print(f"Đang tải model Whisper '{model_name}'...")

        self.model = whisper.load_model(model_name, device=self.device)
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

        Returns:
            dict với thông tin xử lý (thời gian, số cảnh, tốc độ...)
        """
        import time

        start_time = time.time()

        try:
            # Load audio
            audio = self.load_audio(audio_path)

            # Chia audio thành segments
            segments = self.split_audio(audio)

            # Tạo thư mục tạm
            with tempfile.TemporaryDirectory() as temp_dir:
                transcriptions = []  # List of tuples: (scene_number, text)

                print(f"\nĐang transcribe các đoạn audio (Ngôn ngữ: {language})...")

                # Sử dụng tqdm để hiển thị progress bar
                for i, segment in enumerate(tqdm(segments, desc="Transcribing", unit="cảnh"), 1):
                    # Transcribe segment
                    text = self.transcribe_segment(segment, i, temp_dir, language=language)

                    # Luôn lưu scene number và text (kể cả khi rỗng) để đảm bảo đánh số đúng
                    transcriptions.append((i, text))

                    if text:
                        if self.verbose:
                            preview = text[:60] + "..." if len(text) > 60 else text
                            tqdm.write(f"  Cảnh {i}: {preview}")
                    else:
                        if self.verbose:
                            tqdm.write(f"  Cảnh {i}: (không có âm thanh)")

            # Xuất kết quả ra file
            self.export_transcriptions(transcriptions, output_path)

            # Tính toán thống kê
            end_time = time.time()
            total_time = end_time - start_time
            audio_duration = len(audio) / 1000.0  # giây
            avg_time_per_segment = total_time / len(segments) if segments else 0

            print(f"\n✓ Hoàn thành! Đã lưu Script vào: {output_path}")
            print(f"✓ Tổng số cảnh: {len(transcriptions)}")
            # Tính độ dài trung bình chỉ cho các cảnh có nội dung
            texts_with_content = [t for _, t in transcriptions if t]
            print(f"✓ Độ dài trung bình: {sum(len(t) for t in texts_with_content) / len(texts_with_content):.0f} ký tự/cảnh" if texts_with_content else "")
            print(f"✓ Thời gian xử lý: {total_time:.1f} giây ({total_time/60:.1f} phút)")
            print(f"✓ Tốc độ: {avg_time_per_segment:.1f} giây/cảnh")
            print(f"✓ Tỷ lệ: {audio_duration/total_time:.2f}x (audio {audio_duration:.0f}s / xử lý {total_time:.0f}s)")

            return {
                'success': True,
                'total_scenes': len(transcriptions),
                'total_time': total_time,
                'audio_duration': audio_duration,
                'avg_time_per_segment': avg_time_per_segment,
                'speed_ratio': audio_duration / total_time if total_time > 0 else 0
            }

        except Exception as e:
            print(f"\n✗ Lỗi: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def export_transcriptions(self, transcriptions, output_path):
        """
        Xuất transcriptions ra file text
        Mỗi cảnh trên 1 dòng với format: Cảnh X: nội dung

        Args:
            transcriptions: List of tuples (scene_number, text)
            output_path: Đường dẫn file output
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for scene_num, text in transcriptions:
                if text:
                    f.write(f'Cảnh {scene_num}: {text}\n')
                else:
                    # Ghi cảnh rỗng với placeholder
                    f.write(f'Cảnh {scene_num}: (im lặng)\n')


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
        result = transcriber.process_audio(args.input, args.output, language=language or 'vi')

        if result.get('success'):
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
