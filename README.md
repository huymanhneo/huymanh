# Audio Segmentation & Transcription Tool

Phần mềm trích xuất audio thành các đoạn 8 giây và chuyển đổi thành Script văn bản - **Tối ưu hóa cho Tiếng Việt** 🇻🇳

## Tính năng nổi bật

- ✂️ **Chia audio tự động**: Tách audio thành các đoạn 8 giây chính xác
- 🎯 **AI Transcription**: Sử dụng OpenAI Whisper - AI chuyển giọng nói thành text hàng đầu
- 🇻🇳 **Tối ưu cho Tiếng Việt**: Xử lý và làm sạch text tiếng Việt tự động
- 📝 **Format Script**: Mỗi đoạn 8 giây = 1 cảnh trên 1 dòng, không có dòng trống
- 🎵 **Đa định dạng**: Hỗ trợ MP3, WAV, M4A, MP4, OGG, FLAC, AAC
- 🌍 **Đa ngôn ngữ**: Tiếng Việt (mặc định), Tiếng Anh, và 90+ ngôn ngữ khác
- 📊 **Progress Bar**: Theo dõi tiến trình xử lý real-time
- 🧹 **Text Cleaning**: Tự động chuẩn hóa khoảng trắng, dấu câu
- 🚀 **Nhanh & Chính xác**: Nhiều model lựa chọn, cân bằng tốc độ/chất lượng

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

### Sử dụng cơ bản (Tiếng Việt)

```bash
python audio_transcriber.py input.mp3 output.txt
```

Lệnh trên sẽ:
1. Load file `input.mp3`
2. Chia thành các đoạn 8 giây
3. Transcribe mỗi đoạn bằng AI
4. Lưu kết quả vào `output.txt` (mỗi cảnh 1 dòng)

### Các tùy chọn nâng cao

```bash
# Model chính xác hơn cho tiếng Việt (khuyến nghị)
python audio_transcriber.py input.mp3 output.txt --model small

# Model nhanh nhất (cho test)
python audio_transcriber.py input.mp3 output.txt --model tiny

# Model chất lượng cao nhất
python audio_transcriber.py input.mp3 output.txt --model medium

# Audio tiếng Anh
python audio_transcriber.py english.mp3 output.txt --language en

# Tự động detect ngôn ngữ
python audio_transcriber.py audio.mp3 output.txt --language auto

# Chế độ im lặng (chỉ hiển thị progress bar)
python audio_transcriber.py input.mp3 output.txt --quiet

# Xem tất cả tùy chọn
python audio_transcriber.py --help
```

### Các model có sẵn

| Model  | Kích thước | VRAM | Thời gian (10 phút audio) | Độ chính xác Tiếng Việt |
|--------|-----------|------|---------------------------|-------------------------|
| tiny   | ~39 MB    | ~1 GB| ~1 phút   | ⭐⭐ Thấp (60-70%)      |
| base   | ~74 MB    | ~1 GB| ~2 phút   | ⭐⭐⭐ Khá (75-85%)     |
| small  | ~244 MB   | ~2 GB| ~5 phút   | ⭐⭐⭐⭐ Tốt (85-92%)   |
| medium | ~769 MB   | ~5 GB| ~12 phút  | ⭐⭐⭐⭐⭐ Rất tốt (90-95%) |
| large  | ~1550 MB  | ~10 GB| ~25 phút | ⭐⭐⭐⭐⭐ Xuất sắc (92-97%) |

**Khuyến nghị cho Tiếng Việt:**
- 🚀 **Nhanh**: `base` - Cân bằng tốt nhất cho hầu hết trường hợp
- 🎯 **Chính xác**: `small` - Tốt cho content quan trọng
- 💎 **Chuyên nghiệp**: `medium` hoặc `large` - Cho sản xuất chuyên nghiệp

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
├── audio_transcriber.py    # File chính - CLI tool
├── example_usage.py         # Ví dụ sử dụng trong Python
├── requirements.txt         # Thư viện cần thiết
├── README.md               # Hướng dẫn này
└── .gitignore              # Git ignore
```

## Sử dụng trong Python

Ngoài CLI, bạn có thể import và sử dụng trong code Python:

```python
from audio_transcriber import AudioTranscriber

# Tạo transcriber
transcriber = AudioTranscriber(model_name="base")

# Xử lý audio
transcriber.process_audio(
    audio_path="input.mp3",
    output_path="output.txt",
    language="vi"
)
```

Xem file `example_usage.py` để biết thêm ví dụ chi tiết.

## Tips cho Tiếng Việt

### 1. Chất lượng audio
- ✅ **Tốt**: Audio rõ ràng, ít nhiễu
- ✅ **Tốt**: Giọng nói tự nhiên, không quá nhanh
- ⚠️ **Khó**: Audio có nhiều nhiễu, âm nhạc nền lớn
- ⚠️ **Khó**: Giọng địa phương đặc trưng, nói nhanh

### 2. Tối ưu độ chính xác
- Sử dụng model `small` trở lên cho tiếng Việt
- Đảm bảo audio có chất lượng tốt (16kHz trở lên)
- Giảm nhiễu nền trước khi xử lý nếu có thể

### 3. Xử lý kết quả
- Text output đã được tự động làm sạch (khoảng trắng, dấu câu)
- Chữ cái đầu câu tự động viết hoa
- Có thể cần review và sửa một số từ đặc biệt/chuyên ngành

## Xử lý lỗi thường gặp

### Lỗi: "ffmpeg not found"
**Nguyên nhân**: Chưa cài đặt ffmpeg

**Giải pháp**:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### Lỗi: "Out of memory" / "CUDA out of memory"
**Nguyên nhân**: Model quá lớn so với RAM/VRAM

**Giải pháp**:
- Dùng model nhỏ hơn: `--model tiny` hoặc `--model base`
- Đóng các ứng dụng khác
- Trên CPU: Đảm bảo có ít nhất 4GB RAM trống

### Transcription không chính xác với tiếng Việt
**Nguyên nhân**: Model quá nhỏ hoặc audio chất lượng thấp

**Giải pháp**:
- Dùng model lớn hơn: `--model small` hoặc `--model medium`
- Kiểm tra chất lượng audio (nhiễu, âm lượng)
- Đảm bảo đã chỉ định đúng language: `--language vi`

### File audio không được hỗ trợ
**Nguyên nhân**: Format audio không phổ biến

**Giải pháp**:
- Convert sang MP3 hoặc WAV bằng ffmpeg:
  ```bash
  ffmpeg -i input.xxx output.mp3
  ```

### Chương trình chạy chậm
**Nguyên nhân**: Model lớn, audio dài, hoặc chạy trên CPU

**Giải pháp**:
- Dùng model nhỏ hơn cho test: `--model tiny`
- Nếu có GPU NVIDIA, cài đặt CUDA để tăng tốc
- Cắt audio thành các file nhỏ hơn để xử lý

## FAQ - Câu hỏi thường gặp

**Q: Tools có hoạt động offline không?**
A: Có! Sau khi tải model lần đầu, tools hoạt động 100% offline.

**Q: Độ chính xác với tiếng Việt như thế nào?**
A:
- Model `base`: 75-85% (đủ dùng cho hầu hết trường hợp)
- Model `small`: 85-92% (tốt)
- Model `medium/large`: 90-97% (rất tốt, gần professional)

**Q: Có thể xử lý audio dài không?**
A: Có! Tools tự động chia nhỏ, có thể xử lý audio vài giờ.

**Q: Tại sao mỗi cảnh 8 giây?**
A: 8 giây là độ dài tối ưu để:
- Dễ quản lý và edit
- Đủ ngắn để tìm kiếm nhanh
- Đủ dài để câu nói hoàn chỉnh

**Q: Có thể thay đổi độ dài segment không?**
A: Hiện tại cố định 8 giây. Nếu cần custom, có thể sửa `segment_duration` trong code.

**Q: Tools có thu thập dữ liệu không?**
A: Không! Tools chạy hoàn toàn local, không gửi data đi đâu cả.

## Hỗ trợ

Nếu gặp vấn đề:
1. Đọc phần "Xử lý lỗi thường gặp" ở trên
2. Kiểm tra log output của chương trình
3. Đảm bảo đã cài đặt đầy đủ dependencies
4. Kiểm tra file audio có hợp lệ không

## License

MIT License
