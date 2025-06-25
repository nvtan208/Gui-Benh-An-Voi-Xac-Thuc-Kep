# Secure File Transfer - Medical Record

## Mô tả
Hệ thống truyền file bệnh án an toàn với xác thực kép (chữ ký số RSA và mật khẩu SHA-256), mã hóa AES-CBC, và kiểm tra toàn vẹn SHA-512.

## Cài đặt
1. Cài Python 3.7+.
2. Cài thư viện: `pip install pycryptodome`.
3. Chạy `generate_keys.py` để tạo khóa RSA.

## Cách chạy
1. Chạy server: `python server.py`.
2. Chạy client: `python client.py`.
3. (Tùy chọn) Chạy GUI: `python gui.py`.

## Cấu trúc file
- client.py: Gửi file.
- server.py: Nhận file.
- crypto_utils.py: Hàm mã hóa/giải mã.
- gui.py: Giao diện người dùng.