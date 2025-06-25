import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from client import send_file

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Medical Record Transfer")
        self.root.geometry("600x400")  # Kích thước cửa sổ
        self.root.resizable(False, False)  # Không cho thay đổi kích thước
        self.root.configure(bg="#f0f4f8")  # Màu nền nhẹ

        # Thiết lập biểu tượng (nếu có file icon)
        # self.root.iconbitmap("medical_icon.ico")  # Bỏ comment nếu có file .ico

        # Biến trạng thái
        self.is_sending = False

        # Tạo khung chính
        self.main_frame = tk.Frame(root, bg="#f0f4f8", padx=20, pady=20)
        self.main_frame.pack(expand=True, fill="both")

        # Tiêu đề
        tk.Label(
            self.main_frame,
            text="Gửi Bệnh Án An Toàn",
            font=("Segoe UI", 18, "bold"),
            bg="#f0f4f8",
            fg="#2c3e50"
        ).pack(pady=10)

        # Khung chọn file
        file_frame = tk.Frame(self.main_frame, bg="#f0f4f8")
        file_frame.pack(fill="x", pady=5)
        tk.Label(
            file_frame,
            text="File Bệnh Án:",
            font=("Segoe UI", 10),
            bg="#f0f4f8",
            fg="#34495e"
        ).pack(side="left", padx=5)
        self.file_entry = tk.Entry(
            file_frame,
            width=40,
            font=("Segoe UI", 10),
            bd=1,
            relief="solid"
        )
        self.file_entry.pack(side="left", padx=5, fill="x", expand=True)
        tk.Button(
            file_frame,
            text="Browse",
            command=self.browse_file,
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            activebackground="#2980b9"
        ).pack(side="left", padx=5)

        # Khung nhập mật khẩu
        pwd_frame = tk.Frame(self.main_frame, bg="#f0f4f8")
        pwd_frame.pack(fill="x", pady=5)
        tk.Label(
            pwd_frame,
            text="Mật Khẩu:",
            font=("Segoe UI", 10),
            bg="#f0f4f8",
            fg="#34495e"
        ).pack(side="left", padx=5)
        self.pwd_entry = tk.Entry(
            pwd_frame,
            width=40,
            show="*",
            font=("Segoe UI", 10),
            bd=1,
            relief="solid"
        )
        self.pwd_entry.pack(side="left", padx=5, fill="x", expand=True)

        # Thanh tiến trình
        self.progress = ttk.Progressbar(
            self.main_frame,
            mode="indeterminate",
            length=400
        )
        self.progress.pack(pady=10)
        self.progress.stop()

        # Khung nút
        button_frame = tk.Frame(self.main_frame, bg="#f0f4f8")
        button_frame.pack(pady=10)
        self.send_button = tk.Button(
            button_frame,
            text="Gửi File",
            command=self.start_send_file,
            bg="#2ecc71",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            activebackground="#27ae60",
            width=15
        )
        self.send_button.pack(side="left", padx=5)
        tk.Button(
            button_frame,
            text="Xóa",
            command=self.clear_fields,
            bg="#e74c3c",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            activebackground="#c0392b",
            width=15
        ).pack(side="left", padx=5)

        # Nhãn trạng thái
        self.status_label = tk.Label(
            self.main_frame,
            text="Trạng thái: Sẵn sàng",
            font=("Segoe UI", 10, "italic"),
            bg="#f0f4f8",
            fg="#7f8c8d"
        )
        self.status_label.pack(pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def clear_fields(self):
        self.file_entry.delete(0, tk.END)
        self.pwd_entry.delete(0, tk.END)
        self.status_label.config(text="Trạng thái: Sẵn sàng")
        self.progress.stop()

    def start_send_file(self):
        if self.is_sending:
            return
        file_path = self.file_entry.get()
        password = self.pwd_entry.get()
        if not file_path or not password:
            messagebox.showerror("Lỗi", "Vui lòng chọn file và nhập mật khẩu!")
            return

        self.is_sending = True
        self.send_button.config(state="disabled")
        self.status_label.config(text="Trạng thái: Đang gửi...")
        self.progress.start()

        # Chạy gửi file trong luồng riêng
        threading.Thread(
            target=self.send_file_thread,
            args=(file_path, password),
            daemon=True
        ).start()

    def send_file_thread(self, file_path, password):
        try:
            success, message = send_file("localhost", 9999, file_path, password)
            if success:
                self.root.after(0, self.update_status, "Trạng thái: Gửi file thành công!", "success")
                messagebox.showinfo("Thành công", "File đã được gửi thành công!")
            else:
                self.root.after(0, self.update_status, f"Trạng thái: Gửi file thất bại - {message}", "error")
                messagebox.showerror("Lỗi", f"Gửi file thất bại: {message}")
        except Exception as e:
            self.root.after(0, self.update_status, f"Trạng thái: Lỗi - {str(e)}", "error")
            messagebox.showerror("Lỗi", f"Gửi file thất bại: {str(e)}")
        finally:
            self.root.after(0, self.reset_ui)

    def update_status(self, message, status_type):
        self.status_label.config(
            text=message,
            fg="#27ae60" if status_type == "success" else "#c0392b"
        )

    def reset_ui(self):
        self.is_sending = False
        self.send_button.config(state="normal")
        self.progress.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()