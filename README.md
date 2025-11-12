# Audio Segmentation & Transcription Tool

Phần mềm trích xuất audio thành các đoạn 8 giây và chuyển đổi thành Script văn bản.

## Tính năng

- Chia audio thành các đoạn 8 giây
- Transcribe mỗi đoạn audio thành text bằng AI (Whisper)
- Mỗi đoạn 8 giây = 1 cảnh
- Xuất Script ra file text, mỗi cảnh trên 1 dòng, liên tiếp nhau
- Hỗ trợ nhiều định dạng audio: MP3, WAV, M4A, OGG, FLAC
- Hỗ trợ nhiều ngôn ngữ (mặc định: Tiếng Việt)

## Cài đặt

### Yêu cầu hệ thống

- Python 3.8 trở lên
- ffmpeg (để xử lý audio)

### Cài đặt ffmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Tải từ https://ffmpeg.org/download.html

### Cài đặt thư viện Python

```bash
pip install -r requirements.txt
```

Lưu ý: Lần đầu chạy, Whisper sẽ tự động tải model (khoảng 100MB-3GB tùy model).

## Cách sử dụng

### Sử dụng cơ bản

```bash
python audio_transcriber.py input.mp3 output.txt
```

### Các tùy chọn

```bash
# Sử dụng model nhỏ hơn (nhanh hơn, ít chính xác hơn)
python audio_transcriber.py input.mp3 output.txt --model tiny

# Sử dụng model lớn hơn (chính xác hơn, chậm hơn)
python audio_transcriber.py input.mp3 output.txt --model medium

# Transcribe audio tiếng Anh
python audio_transcriber.py input.mp3 output.txt --language en

# Xem tất cả tùy chọn
python audio_transcriber.py --help
```

### Các model có sẵn

| Model  | Kích thước | VRAM | Tốc độ | Độ chính xác |
|--------|-----------|------|--------|--------------|
| tiny   | ~39 MB    | ~1 GB| Rất nhanh | Thấp    |
| base   | ~74 MB    | ~1 GB| Nhanh  | Trung bình  |
| small  | ~244 MB   | ~2 GB| TB     | Khá         |
| medium | ~769 MB   | ~5 GB| Chậm   | Cao         |
| large  | ~1550 MB  | ~10 GB| Rất chậm | Rất cao  |

**Khuyến nghị:** Dùng `base` hoặc `small` để cân bằng giữa tốc độ và độ chính xác.

## Ví dụ

### Input: File audio dài 30 giây

```bash
python audio_transcriber.py speech.mp3 transcript.txt
```

### Output: File transcript.txt

```
Xin chào các bạn, hôm nay tôi sẽ chia sẻ về công nghệ AI
Trí tuệ nhân tạo đang phát triển rất nhanh chóng
Nhiều ứng dụng AI đã được áp dụng trong cuộc sống
Ví dụ như nhận diện giọng nói, nhận diện khuôn mặt
```

Mỗi dòng tương ứng với 1 cảnh (8 giây audio).

## Cấu trúc project

```
huymanh/
├── audio_transcriber.py    # File chính
├── requirements.txt         # Thư viện cần thiết
└── README.md               # Hướng dẫn này
```

## Xử lý lỗi thường gặp

### Lỗi: "ffmpeg not found"
- Cài đặt ffmpeg theo hướng dẫn ở trên

### Lỗi: "Out of memory"
- Dùng model nhỏ hơn: `--model tiny` hoặc `--model base`
- Đóng các ứng dụng khác để giải phóng RAM

### Audio không có tiếng/không chính xác
- Kiểm tra file audio có bị hỏng không
- Thử đổi language: `--language en` (nếu là tiếng Anh)
- Dùng model lớn hơn để tăng độ chính xác

## Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra log output của chương trình
2. Đảm bảo đã cài đặt đầy đủ dependencies
3. Kiểm tra file audio có hợp lệ không

## License

MIT License
