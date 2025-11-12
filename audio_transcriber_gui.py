#!/usr/bin/env python3
"""
Audio Transcriber GUI
Giao diện đồ họa cho Audio Segmentation & Transcription Tool
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import queue

# Import AudioTranscriber từ file chính
from audio_transcriber import AudioTranscriber


class AudioTranscriberGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Transcriber - Trích xuất và Chuyển đổi Audio sang Text")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # Biến lưu trữ
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.model_choice = tk.StringVar(value="base")
        self.language_choice = tk.StringVar(value="vi")
        self.is_processing = False
        self.transcriber = None

        # Queue để update UI từ thread khác
        self.log_queue = queue.Queue()

        # Tạo UI
        self.create_widgets()

        # Bắt đầu check queue
        self.check_log_queue()

    def create_widgets(self):
        """Tạo các widget cho giao diện"""

        # ===== Header =====
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)

        title_label = ttk.Label(
            header_frame,
            text="🎵 Audio Transcriber 🇻🇳",
            font=("Arial", 18, "bold")
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            header_frame,
            text="Trích xuất audio thành các đoạn 8 giây và chuyển đổi thành Script",
            font=("Arial", 10)
        )
        subtitle_label.pack()

        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)

        # ===== Input File =====
        input_frame = ttk.LabelFrame(self.root, text="1. Chọn File Audio", padding="10")
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        input_entry_frame = ttk.Frame(input_frame)
        input_entry_frame.pack(fill=tk.X)

        self.input_entry = ttk.Entry(input_entry_frame, textvariable=self.input_file, width=60)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        input_btn = ttk.Button(input_entry_frame, text="📁 Chọn File", command=self.browse_input)
        input_btn.pack(side=tk.RIGHT)

        # Supported formats
        formats_label = ttk.Label(
            input_frame,
            text="Hỗ trợ: MP3, WAV, M4A, MP4, OGG, FLAC, AAC",
            font=("Arial", 8),
            foreground="gray"
        )
        formats_label.pack(anchor=tk.W, pady=(5, 0))

        # ===== Output File =====
        output_frame = ttk.LabelFrame(self.root, text="2. Chọn File Đầu Ra", padding="10")
        output_frame.pack(fill=tk.X, padx=10, pady=5)

        output_entry_frame = ttk.Frame(output_frame)
        output_entry_frame.pack(fill=tk.X)

        self.output_entry = ttk.Entry(output_entry_frame, textvariable=self.output_file, width=60)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        output_btn = ttk.Button(output_entry_frame, text="💾 Chọn Nơi Lưu", command=self.browse_output)
        output_btn.pack(side=tk.RIGHT)

        # ===== Settings =====
        settings_frame = ttk.LabelFrame(self.root, text="3. Cài Đặt", padding="10")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)

        # Model selection
        model_frame = ttk.Frame(settings_frame)
        model_frame.pack(fill=tk.X, pady=5)

        ttk.Label(model_frame, text="Model AI:", width=15).pack(side=tk.LEFT)

        models = [
            ("tiny - Nhanh nhất (60-70%)", "tiny"),
            ("base - Cân bằng (75-85%) ⭐", "base"),
            ("small - Chính xác (85-92%)", "small"),
            ("medium - Rất tốt (90-95%)", "medium"),
            ("large - Xuất sắc (92-97%)", "large")
        ]

        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_choice,
            values=[m[1] for m in models],
            state="readonly",
            width=40
        )
        model_combo.pack(side=tk.LEFT, padx=5)

        # Model description
        self.model_desc = ttk.Label(
            settings_frame,
            text="⭐ Khuyến nghị: base (cân bằng tốt) hoặc small (chính xác cao)",
            font=("Arial", 8),
            foreground="blue"
        )
        self.model_desc.pack(anchor=tk.W, pady=(0, 10))

        # Language selection
        lang_frame = ttk.Frame(settings_frame)
        lang_frame.pack(fill=tk.X, pady=5)

        ttk.Label(lang_frame, text="Ngôn ngữ:", width=15).pack(side=tk.LEFT)

        languages = [
            ("Tiếng Việt 🇻🇳", "vi"),
            ("Tiếng Anh 🇺🇸", "en"),
            ("Tự động phát hiện", "auto")
        ]

        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.language_choice,
            values=[l[1] for l in languages],
            state="readonly",
            width=40
        )
        lang_combo.pack(side=tk.LEFT, padx=5)

        # ===== Process Button =====
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)

        self.process_btn = ttk.Button(
            button_frame,
            text="🚀 BẮT ĐẦU XỬ LÝ",
            command=self.start_processing,
            style="Accent.TButton"
        )
        self.process_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(
            button_frame,
            text="⏹ DỪNG",
            command=self.stop_processing,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(
            button_frame,
            text="🗑 Xóa Log",
            command=self.clear_log
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=5)

        # ===== Progress =====
        progress_frame = ttk.LabelFrame(self.root, text="Tiến Trình", padding="10")
        progress_frame.pack(fill=tk.X, padx=10, pady=5)

        self.progress = ttk.Progressbar(
            progress_frame,
            mode="indeterminate",
            length=300
        )
        self.progress.pack(fill=tk.X)

        self.status_label = ttk.Label(
            progress_frame,
            text="Sẵn sàng",
            font=("Arial", 9)
        )
        self.status_label.pack(pady=(5, 0))

        # ===== Log Output =====
        log_frame = ttk.LabelFrame(self.root, text="Log & Kết Quả", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Thêm màu cho log
        self.log_text.tag_config("info", foreground="black")
        self.log_text.tag_config("success", foreground="green", font=("Consolas", 9, "bold"))
        self.log_text.tag_config("error", foreground="red", font=("Consolas", 9, "bold"))
        self.log_text.tag_config("warning", foreground="orange")

        # Initial message
        self.log("Chào mừng bạn đến với Audio Transcriber! 🎉\n", "success")
        self.log("Vui lòng chọn file audio và bắt đầu xử lý.\n\n", "info")

    def browse_input(self):
        """Chọn file audio input"""
        filename = filedialog.askopenfilename(
            title="Chọn File Audio",
            filetypes=[
                ("All Audio", "*.mp3 *.wav *.m4a *.mp4 *.ogg *.flac *.aac"),
                ("MP3", "*.mp3"),
                ("WAV", "*.wav"),
                ("M4A/MP4", "*.m4a *.mp4"),
                ("OGG", "*.ogg"),
                ("FLAC", "*.flac"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            self.input_file.set(filename)

            # Auto-suggest output filename
            if not self.output_file.get():
                base_name = Path(filename).stem
                suggested_output = str(Path(filename).parent / f"{base_name}_transcript.txt")
                self.output_file.set(suggested_output)

            self.log(f"✓ Đã chọn file: {filename}\n", "info")

    def browse_output(self):
        """Chọn file output"""
        filename = filedialog.asksaveasfilename(
            title="Lưu File Text",
            defaultextension=".txt",
            filetypes=[
                ("Text File", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            self.output_file.set(filename)
            self.log(f"✓ Sẽ lưu kết quả vào: {filename}\n", "info")

    def log(self, message, tag="info"):
        """Thêm message vào log"""
        self.log_queue.put((message, tag))

    def check_log_queue(self):
        """Kiểm tra và update log từ queue"""
        try:
            while True:
                message, tag = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message, tag)
                self.log_text.see(tk.END)
        except queue.Empty:
            pass

        # Lặp lại sau 100ms
        self.root.after(100, self.check_log_queue)

    def clear_log(self):
        """Xóa log"""
        self.log_text.delete(1.0, tk.END)
        self.log("Log đã được xóa.\n\n", "info")

    def validate_inputs(self):
        """Kiểm tra input hợp lệ"""
        if not self.input_file.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn file audio đầu vào!")
            return False

        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("Lỗi", f"File không tồn tại:\n{self.input_file.get()}")
            return False

        if not self.output_file.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn file đầu ra!")
            return False

        return True

    def start_processing(self):
        """Bắt đầu xử lý audio"""
        if not self.validate_inputs():
            return

        if self.is_processing:
            messagebox.showwarning("Cảnh báo", "Đang xử lý, vui lòng đợi!")
            return

        # Disable buttons
        self.process_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.is_processing = True

        # Clear log
        self.log_text.delete(1.0, tk.END)

        # Start progress bar
        self.progress.start(10)
        self.status_label.config(text="Đang xử lý...")

        # Log info
        self.log("=" * 60 + "\n", "info")
        self.log("BẮT ĐẦU XỬ LÝ AUDIO\n", "success")
        self.log("=" * 60 + "\n", "info")
        self.log(f"Input: {self.input_file.get()}\n", "info")
        self.log(f"Output: {self.output_file.get()}\n", "info")
        self.log(f"Model: {self.model_choice.get()}\n", "info")
        self.log(f"Ngôn ngữ: {self.language_choice.get()}\n", "info")
        self.log("\n", "info")

        # Run processing in separate thread
        thread = threading.Thread(target=self.process_audio_thread, daemon=True)
        thread.start()

    def process_audio_thread(self):
        """Thread xử lý audio"""
        import time
        start_time = time.time()

        try:
            # Tạo transcriber
            self.log(f"Đang tải model '{self.model_choice.get()}'...\n", "info")

            self.transcriber = AudioTranscriber(
                model_name=self.model_choice.get(),
                verbose=False
            )
            self.log("✓ Model đã được tải!\n\n", "success")

            # Xử lý
            language = self.language_choice.get()
            if language == "auto":
                language = None

            # Custom logging
            self.log("Đang load file audio...\n", "info")
            audio = self.transcriber.load_audio(self.input_file.get())
            self.log("✓ Đã load audio!\n", "info")

            self.log("Đang chia audio thành các đoạn 8 giây...\n", "info")
            segments = self.transcriber.split_audio(audio)
            self.log(f"✓ Đã chia thành {len(segments)} đoạn!\n\n", "success")

            self.log(f"Đang transcribe {len(segments)} đoạn audio...\n", "info")
            self.log("(Quá trình này có thể mất vài phút tùy độ dài audio)\n\n", "warning")

            # Track time per segment
            segment_times = []

            # Transcribe từng segment
            import tempfile
            transcriptions = []  # List of tuples: (scene_number, text)

            with tempfile.TemporaryDirectory() as temp_dir:
                for i, segment in enumerate(segments, 1):
                    if not self.is_processing:
                        self.log("\n⚠ Đã dừng bởi người dùng!\n", "warning")
                        return

                    seg_start = time.time()
                    self.log(f"Đang xử lý cảnh {i}/{len(segments)}...\n", "info")

                    text = self.transcriber.transcribe_segment(
                        segment, i, temp_dir, language=language or 'vi'
                    )

                    seg_time = time.time() - seg_start
                    segment_times.append(seg_time)

                    # Luôn lưu scene number và text (kể cả khi rỗng)
                    transcriptions.append((i, text))

                    if text:
                        preview = text[:60] + "..." if len(text) > 60 else text
                        self.log(f"  ✓ Cảnh {i}: {preview} ({seg_time:.1f}s)\n", "success")
                    else:
                        self.log(f"  ⚠ Cảnh {i}: (không có âm thanh) ({seg_time:.1f}s)\n", "warning")

            # Xuất kết quả
            self.log("\nĐang lưu kết quả...\n", "info")
            self.transcriber.export_transcriptions(transcriptions, self.output_file.get())

            # Calculate statistics
            end_time = time.time()
            total_time = end_time - start_time
            audio_duration = len(audio) / 1000.0  # giây
            avg_time = sum(segment_times) / len(segment_times) if segment_times else 0

            # Success with detailed stats
            self.log("\n" + "=" * 60 + "\n", "info")
            self.log("✓ HOÀN THÀNH!\n", "success")
            self.log("=" * 60 + "\n", "info")
            self.log(f"✓ Đã lưu Script vào: {self.output_file.get()}\n", "success")
            self.log(f"✓ Tổng số cảnh: {len(transcriptions)}\n", "success")
            # Tính độ dài trung bình chỉ cho các cảnh có nội dung
            if transcriptions:
                texts_with_content = [t for _, t in transcriptions if t]
                if texts_with_content:
                    avg_len = sum(len(t) for t in texts_with_content) / len(texts_with_content)
                    self.log(f"✓ Độ dài trung bình: {avg_len:.0f} ký tự/cảnh\n", "success")

            # Performance stats
            self.log("\n📊 THỐNG KÊ HIỆU NĂNG:\n", "info")
            self.log(f"⏱️  Thời gian tổng: {total_time:.1f}s ({total_time/60:.1f} phút)\n", "info")
            self.log(f"⚡ Tốc độ trung bình: {avg_time:.1f}s/cảnh\n", "info")
            self.log(f"🎵 Độ dài audio: {audio_duration:.1f}s ({audio_duration/60:.1f} phút)\n", "info")
            self.log(f"📈 Tỷ lệ: {audio_duration/total_time:.2f}x (audio/thời gian xử lý)\n", "info")
            if audio_duration < total_time:
                self.log(f"   → Xử lý chậm hơn audio thực tế\n", "warning")
            else:
                self.log(f"   → Xử lý nhanh hơn audio thực tế ⚡\n", "success")

            self.status_label.config(text="Hoàn thành!")

            messagebox.showinfo(
                "Thành công!",
                f"Đã xử lý xong!\n\n" +
                f"Tổng số cảnh: {len(transcriptions)}\n" +
                f"Thời gian: {total_time/60:.1f} phút\n" +
                f"Tốc độ: {avg_time:.1f}s/cảnh\n" +
                f"File: {self.output_file.get()}"
            )

        except Exception as e:
            self.log(f"\n✗ LỖI: {str(e)}\n", "error")
            import traceback
            self.log(traceback.format_exc(), "error")
            self.status_label.config(text="Lỗi!")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra:\n{str(e)}")

        finally:
            self.finish_processing()

    def stop_processing(self):
        """Dừng xử lý"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn dừng xử lý?"):
            self.is_processing = False
            self.log("\n⚠ Đang dừng...\n", "warning")

    def finish_processing(self):
        """Kết thúc xử lý"""
        self.is_processing = False
        self.progress.stop()
        self.process_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)


def main():
    """Main function"""
    root = tk.Tk()

    # Style
    style = ttk.Style()
    style.theme_use('clam')  # hoặc 'alt', 'default', 'classic'

    # Create app
    app = AudioTranscriberGUI(root)

    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    # Run
    root.mainloop()


if __name__ == "__main__":
    main()
