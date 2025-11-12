# 🚀 Hướng Dẫn Nhanh - Audio Transcriber

Hướng dẫn nhanh 5 phút để bắt đầu sử dụng!

## Bước 1: Cài đặt (Chỉ làm 1 lần)

### Windows

1. **Cài ffmpeg** (bắt buộc):
   ```bash
   # Tải từ: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
   # Giải nén và thêm vào PATH
   ```

2. **Cài thư viện Python**:
   ```bash
   cd D:\1-Manh-Tu-Build-Tools\ClaudeCodeWeb\huymanh
   pip install -r requirements.txt
   ```

   Hoặc:
   ```bash
   pip install pydub openai-whisper torch numpy tqdm
   ```

### macOS / Linux

```bash
# Cài ffmpeg
brew install ffmpeg   # macOS
sudo apt install ffmpeg   # Ubuntu/Debian

# Cài thư viện Python
pip install -r requirements.txt
```

## Bước 2: Chạy chương trình

### ⭐ Cách 1: Dùng GUI (Khuyến nghị - Dễ nhất!)

```bash
python audio_transcriber_gui.py
```

Sau đó:
1. Click "📁 Chọn File" → Chọn file audio của bạn
2. Click "💾 Chọn Nơi Lưu" → Chọn nơi lưu kết quả
3. Chọn Model (khuyến nghị: `base` hoặc `small`)
4. Chọn Ngôn ngữ (`vi` cho tiếng Việt)
5. Click "🚀 BẮT ĐẦU XỬ LÝ"
6. Chờ xử lý xong và xem kết quả!

### 💻 Cách 2: Dùng Command Line

```bash
python audio_transcriber.py input.mp3 output.txt
```

## Bước 3: Xem kết quả

Mở file `output.txt`, bạn sẽ thấy:
```
Xin chào các bạn, hôm nay tôi sẽ chia sẻ về công nghệ AI
Trí tuệ nhân tạo đang phát triển rất nhanh chóng
...
```

Mỗi dòng = 1 cảnh 8 giây!

## Các lỗi thường gặp

### ❌ ModuleNotFoundError: No module named 'pydub'

**Giải pháp**: Chưa cài thư viện
```bash
pip install -r requirements.txt
```

### ❌ ffmpeg not found

**Giải pháp**: Chưa cài ffmpeg
- Windows: Tải từ https://ffmpeg.org/download.html và thêm vào PATH
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

### ❌ Out of memory

**Giải pháp**: Dùng model nhỏ hơn
```bash
python audio_transcriber.py input.mp3 output.txt --model tiny
```

## Tips

### Chọn Model nào?

| Use Case | Model | Tốc độ | Chất lượng |
|----------|-------|--------|------------|
| Test nhanh | tiny | Rất nhanh | Thấp (70%) |
| Dùng hàng ngày | base | Nhanh | Khá (80%) ⭐ |
| Content quan trọng | small | TB | Tốt (90%) |
| Chuyên nghiệp | medium | Chậm | Rất tốt (95%) |

### Xử lý nhanh hơn?

- Dùng model `tiny` để test
- Chia audio thành file nhỏ hơn
- Nếu có GPU NVIDIA, cài CUDA để tăng tốc

### Cải thiện độ chính xác?

- Dùng model `small` hoặc `medium`
- Đảm bảo audio rõ ràng, ít nhiễu
- Giảm âm nhạc nền nếu có thể

## Ví dụ sử dụng

### Ví dụ 1: Basic (Tiếng Việt)
```bash
python audio_transcriber_gui.py
```

### Ví dụ 2: CLI với model chính xác
```bash
python audio_transcriber.py podcast.mp3 transcript.txt --model small
```

### Ví dụ 3: Audio tiếng Anh
```bash
python audio_transcriber.py english.mp3 output.txt --language en
```

### Ví dụ 4: Tự động detect ngôn ngữ
```bash
python audio_transcriber.py audio.mp3 output.txt --language auto
```

## Cần trợ giúp?

1. Đọc file README.md để biết thêm chi tiết
2. Kiểm tra phần FAQ trong README.md
3. Xem file example_usage.py để biết cách dùng trong Python

## Thành công!

Nếu bạn thấy file output.txt với nội dung transcription, chúc mừng! Bạn đã setup thành công! 🎉

---

**Lưu ý quan trọng:**
- Lần đầu chạy sẽ tải model (100MB-3GB), cần internet
- Sau khi tải xong, tools hoạt động 100% offline
- Quá trình transcribe có thể mất vài phút tùy độ dài audio
