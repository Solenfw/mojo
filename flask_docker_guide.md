# 🚀 Flask + Docker: Tổng quan & Cách chạy

## 1. Tổng quan hệ thống

Luồng hoạt động:

Browser → HTTP → Docker → Flask → Response

-   Trình duyệt gửi request
-   Docker chạy server
-   Flask xử lý route
-   Trả response về client

------------------------------------------------------------------------

## 2. Cấu trúc project

    server/
    │
    ├── app.py
    ├── requirements.txt
    └── Dockerfile

------------------------------------------------------------------------

## 3. Code cơ bản

### app.py

``` python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello Flask!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

------------------------------------------------------------------------

### requirements.txt

    Flask

------------------------------------------------------------------------

### Dockerfile

``` dockerfile
FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

------------------------------------------------------------------------

## 4. Cách chạy

### Bước 1: Build image

``` bash
docker build -t serverpy .
```

------------------------------------------------------------------------

### Bước 2: Run container

``` bash
docker run -p 5000:5000 serverpy
```

------------------------------------------------------------------------

### Bước 3: Truy cập

    http://localhost:5000

👉 Kết quả: `Hello Flask!`

------------------------------------------------------------------------

## 5. Luồng hoạt động

1.  Browser gửi request:

```{=html}
<!-- -->
```
    GET /

2.  Docker nhận qua port mapping:

```{=html}
<!-- -->
```
    localhost:5000 → container:5000

3.  Flask xử lý route:

``` python
@app.route("/")
```

4.  Trả response:

```{=html}
<!-- -->
```
    Hello Flask!

------------------------------------------------------------------------

## 6. Lỗi thường gặp

### ❌ docker not recognized

→ Docker chưa chạy hoặc chưa add PATH

------------------------------------------------------------------------

### ❌ Dockerfile not found

→ Build sai thư mục

------------------------------------------------------------------------

### ❌ ERR_EMPTY_RESPONSE

→ Flask: \* chưa chạy \* hoặc bind sai host

------------------------------------------------------------------------

### ❌ Container tự tắt

    STATUS: Exited (0)

→ App đã kết thúc → container dừng

------------------------------------------------------------------------

## 7. Lưu ý quan trọng

### 🔴 Phải dùng:

``` python
host="0.0.0.0"
```

------------------------------------------------------------------------

### 🔴 Không dùng debug trong Docker

``` python
debug=True ❌
```

------------------------------------------------------------------------

### 🔴 URL đầy đủ

    /api/user ❌
    http://localhost:5000/api/user ✅

------------------------------------------------------------------------

## 8. Kiến thức cốt lõi

Một URL gồm:

    http://localhost:5000/api/user

  Thành phần   Ý nghĩa
  ------------ -----------
  http         giao thức
  localhost    địa chỉ
  5000         port
  /api/user    route

------------------------------------------------------------------------

## 9. Tóm tắt

Bạn đã học:

    Flask → Docker → chạy server → truy cập qua HTTP

------------------------------------------------------------------------

## 10. Hướng phát triển

-   Kết nối database (MySQL/PostgreSQL)
-   Xây dựng API (/api/users)
-   Authentication (JWT)
-   Docker Compose
-   Deploy production (Gunicorn)
