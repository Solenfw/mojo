# ORM SQLAlchemy + MySQL (Flask Guide)

## 1. Tư duy hệ thống
- MySQL: nơi lưu dữ liệu
- SQLAlchemy: ORM (viết Python thay SQL)
- Flask: backend API

Flow:
Client -> Flask -> ORM -> MySQL -> ORM -> Flask -> Client

---

## 2. Cài đặt
```bash
pip install flask flask_sqlalchemy pymysql
```

---

## 3. Kết nối Flask + MySQL
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost:3306/testdb"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
```

---

## 4. Model (Table)
```python
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
```

---

## 5. Tạo bảng
```python
from app import db
db.create_all()
```

---

## 6. CRUD ORM

### CREATE
```python
user = User(name="Hung", email="hung@gmail.com")
db.session.add(user)
db.session.commit()
```

### READ
```python
users = User.query.all()
```

### GET 1
```python
user = User.query.get(1)
```

### UPDATE
```python
user = User.query.get(1)
user.name = "New Name"
db.session.commit()
```

### DELETE
```python
db.session.delete(user)
db.session.commit()
```

---

## 7. API example
```python
@app.route("/users")
def get_users():
    users = User.query.all()
    return {"data": [u.name for u in users]}
```

---

## 8. Docker lưu ý
- Không dùng localhost trong container
- Dùng service name: db

```python
mysql+pymysql://root:root@db:3306/testdb
```

---

## 9. docker-compose
```yaml
version: "3.8"

services:
  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: testdb
    ports:
      - "3306:3306"

  server:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - db
```

---

## 10. Kết luận
- ORM = viết Python thay SQL
- Flask = API server
- MySQL = database
- Docker = môi trường chạy
