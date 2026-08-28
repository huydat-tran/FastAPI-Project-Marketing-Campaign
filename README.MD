# Marketing Campaign Management Backend

Backend REST API xây dựng bằng **FastAPI**, **SQLAlchemy** và **Pydantic** phục vụ quản lý chiến dịch marketing, phân quyền thành viên, quản lý đầu việc (tasks), thảo luận (comments) và tệp đính kèm (attachments).

---

## Tính năng chính

### 1. Xác thực & Phân quyền (Auth & Users)
* Đăng ký, đăng nhập cấp token JWT (`access_token` và `refresh_token`).
* Mã hóa mật khẩu bằng `bcrypt`.
* Phân quyền 2 cấp:
  * **System Role:** `ADMIN` (quản trị user) và `USER` (người dùng thường).
  * **Campaign Role:** `OWNER` (chủ chiến dịch) và `MEMBER` (thành viên).
* Chặn brute-force login bằng Rate Limiting theo IP.

### 2. Quản lý Chiến dịch (Campaigns)
* CRUD chiến dịch: tạo mới, xem chi tiết, chỉnh sửa thông tin.
* Xóa mềm (Soft Delete) qua trường `deleted_at`.
* Quản lý thành viên: tự động gán người tạo làm `OWNER`, hỗ trợ thêm/xóa thành viên.
* Tự động ghi log hoạt động quan trọng vào bảng `activity_logs`.

### 3. Quản lý Công việc (Campaign Tasks)
* Quản lý trạng thái (`TODO`, `IN_PROGRESS`, `DONE`) và độ ưu tiên (`LOW`, `MEDIUM`, `HIGH`).
* Kiểm tra hợp lệ người nhận việc (chỉ được gán task cho thành viên trong campaign).
* Bộ lọc theo trạng thái, độ ưu tiên, người làm, tìm kiếm theo tiêu đề.
* Hỗ trợ phân trang (`limit`, `offset`) và sắp xếp (`created_at`, `due_date`).

### 4. Bình luận & Tệp đính kèm (Comments & Attachments)
* Gửi bình luận trao đổi trong từng task.
* Upload tệp đính kèm (ảnh, PDF, tài liệu văn phòng).
* Lưu trữ an toàn bằng UUID ngẫu nhiên trên ổ cứng để tránh trùng tên và path traversal.
* Tải xuống và xem chi tiết thông tin file.

---

## Sơ đồ Cơ sở Dữ liệu (ERD)

```mermaid
erDiagram
    users ||--o{ campaigns : "owner_id"
    users ||--o{ campaign_members : "user_id"
    users ||--o{ campaign_tasks : "assignee_id"
    users ||--o{ task_comments : "user_id"
    users ||--o{ task_attachments : "uploaded_by"
    users ||--o{ activity_logs : "user_id"

    campaigns ||--o{ campaign_members : "campaign_id"
    campaigns ||--o{ campaign_tasks : "campaign_id"
    campaigns ||--o{ activity_logs : "campaign_id"

    campaign_tasks ||--o{ task_comments : "task_id"
    campaign_tasks ||--o{ task_attachments : "task_id"
```

---

## Cấu trúc Dự án

```text
marketing_campaign/
├── app/
│   ├── core/                  # Config, bảo mật, JWT
│   │   ├── config.py
│   │   └── security.py
│   ├── db/                    # Kết nối Database
│   │   └── database.py
│   ├── dependencies/          # Dependency get_current_user, require_role
│   │   ├── auth.py
│   │   └── role.py
│   ├── models/                # SQLAlchemy Models
│   │   ├── campaign.py
│   │   ├── campaign_task.py
│   │   ├── task_attachment.py
│   │   ├── task_comment.py
│   │   └── user.py
│   ├── routers/               # API Endpoints
│   │   ├── auth.py
│   │   ├── campaign.py
│   │   ├── campaign_task.py
│   │   ├── task_attachment.py
│   │   ├── task_comment.py
│   │   └── users.py
│   ├── schemas/               # Pydantic Schemas
│   │   ├── auth.py
│   │   ├── campaign.py
│   │   ├── campaign_task.py
│   │   ├── task_attachment.py
│   │   ├── task_comment.py
│   │   └── user.py
│   ├── services/              # Business Logic & Phân quyền
│   │   ├── auth.py
│   │   ├── campaign.py
│   │   ├── campaign_task.py
│   │   ├── task_attachment.py
│   │   ├── task_comment.py
│   │   └── user.py
│   ├── utils/                 # Exception handler, validate file
│   │   ├── exceptions.py
│   │   ├── file.py
│   │   └── rate_limit.py
│   └── main.py                # File khởi chạy FastAPI
├── uploads/                   # Thư mục lưu file đính kèm
├── .env.example               # Mẫu file cấu hình
├── requirements.txt           # Thư viện phụ thuộc
├── CHECKLIST_TEST.md          # Kịch bản kiểm thử chi tiết
└── README.md
```

---

## Danh sách API chính

| Nhóm | Method | Endpoint | Quyền | Mô tả |
| :--- | :--- | :--- | :---: | :--- |
| **Auth** | `POST` | `/auth/register` | Public | Đăng ký tài khoản |
| | `POST` | `/auth/login` | Public | Đăng nhập lấy Token |
| | `POST` | `/auth/refresh` | Public | Cấp lại Access Token |
| **Users** | `GET` | `/users/me` | User | Thông tin tài khoản hiện tại |
| | `GET` | `/users` | Admin | Danh sách người dùng |
| **Campaigns** | `POST` | `/campaigns` | User | Tạo chiến dịch |
| | `GET` | `/campaigns` | User | Danh sách chiến dịch đang tham gia |
| | `GET` | `/campaigns/{id}` | Member | Chi tiết chiến dịch |
| | `PATCH` | `/campaigns/{id}` | Owner | Cập nhật chiến dịch |
| | `DELETE` | `/campaigns/{id}` | Owner | Xóa mềm chiến dịch |
| **Members** | `POST` | `/campaigns/{id}/members` | Owner | Thêm thành viên |
| | `GET` | `/campaigns/{id}/members` | Member | Xem danh sách thành viên |
| | `DELETE` | `/campaigns/{id}/members/{user_id}` | Owner | Xóa thành viên |
| **Tasks** | `POST` | `/campaigns/{id}/campaign-tasks` | Member | Tạo task mới |
| | `GET` | `/campaigns/{id}/campaign-tasks` | Member | Lấy danh sách task (kèm lọc) |
| | `GET` | `/campaign-tasks/{task_id}` | Member | Xem chi tiết 1 task |
| | `PATCH` | `/campaign-tasks/{task_id}` | Member/Owner | Cập nhật task |
| | `DELETE` | `/campaign-tasks/{task_id}` | Owner | Xóa task |
| **Comments** | `POST` | `/campaign-tasks/{task_id}/comments` | Member | Gửi bình luận |
| | `GET` | `/campaign-tasks/{task_id}/comments` | Member | Danh sách bình luận |
| **Attachments** | `POST` | `/campaign-tasks/{task_id}/attachments` | Member | Upload file đính kèm |
| | `GET` | `/campaign-tasks/{task_id}/attachments` | Member | Danh sách file của task |
| | `GET` | `/campaign-tasks/attachments/{attachment_id}` | Member | Xem metadata file |
| | `GET` | `/campaign-tasks/attachments/{attachment_id}/download` | Member | Tải file vật lý |
| | `DELETE` | `/campaign-tasks/attachments/{attachment_id}` | Uploader/Owner | Xóa file |

---

## Hướng dẫn Cài đặt & Chạy Dự án

### 1. Chuẩn bị môi trường
* Python 3.10+
* MySQL Server hoặc SQLite

### 2. Cài đặt

```bash
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt môi trường ảo
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### 3. Cấu hình `.env`

Tạo file `.env` ở thư mục gốc:

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/marketing_campaign
SECRET_KEY=your-super-secret-key-at-least-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
LOGIN_RATE_LIMIT=5
LOGIN_RATE_WINDOW_SECONDS=60
```

### 4. Chạy Server

```bash
uvicorn app.main:app --reload
```

* Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Chuẩn hóa Format Lỗi (Error Handling)

Khi xảy ra lỗi, API luôn trả về JSON theo định dạng chuẩn:

```json
{
  "statusCode": 403,
  "message": "You are not a member of this campaign",
  "detail": null
}
```
