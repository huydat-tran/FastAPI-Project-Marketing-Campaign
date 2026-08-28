# Hướng dẫn & Kịch bản Test API (Manual Test)

File này ghi lại các bước test tay luồng nghiệp vụ chính trên Swagger UI (`/docs`) hoặc Postman, chia theo từng module từ Auth, Campaign, Task, Comment đến Attachment.

---

## Chuẩn bị

1. Chạy server:
   ```bash
   uvicorn app.main:app --reload
   ```
2. Mở trình duyệt: `http://127.0.0.1:8000/docs`
3. Cách set Token: Sau khi gọi API `/auth/login`, copy chuỗi `access_token`, bấm nút **Authorize** ở góc trên bên phải Swagger và dán token vào.

---

## Kịch bản 1: Tạo tài khoản & Phân quyền (Auth)

Tạo sẵn 3 tài khoản với 3 vai trò khác nhau để test phân quyền:
* **User 1 (Trưởng phòng / Campaign Owner):** `truongphong@gmail.com`
* **User 2 (Nhân viên / Member):** `nhanvien@gmail.com`
* **User 3 (Người ngoài / Stranger):** `nguoingoai@gmail.com`
* Mật khẩu chung: `Password@123`

### 1. Luồng chạy đúng (Happy Path)
1. Gọi `POST /auth/register` tạo lần lượt 3 user trên. (Kỳ vọng: `201 Created`).
2. Gọi `POST /auth/login` với email `truongphong@gmail.com`.
   * Lấy `access_token` dán vào Authorize.
3. Gọi `GET /users/me`: Kiểm tra thấy trả về đúng thông tin user 1. (Kỳ vọng: `200 OK`).

### 2. Luồng bắt lỗi (Error Cases)
* **Trùng email:** Gọi lại `POST /auth/register` với email `truongphong@gmail.com` -> Kỳ vọng `400 Bad Request` ("Email already registered").
* **Mật khẩu không đúng chuẩn:** Đăng ký với mật khẩu `12345` -> Kỳ vọng `422 Unprocessable Entity` (Thiếu chữ hoa, chữ thường hoặc dưới 8 ký tự).
* **Sai mật khẩu khi login:** Login với pass `111111` -> Kỳ vọng `401 Unauthorized`.

---

## Kịch bản 2: Tạo chiến dịch & Quản lý thành viên (Campaigns)

*(Thực hiện bằng token của `truongphong@gmail.com` - User 1)*

### 1. Luồng chạy đúng
1. **Tạo campaign:** `POST /campaigns`
   ```json
   {
     "name": "Chiến dịch Tết 2027",
     "description": "Quảng bá sản phẩm đợt Tết"
   }
   ```
   -> Trả về campaign `id: 1` và tự động set User 1 làm `OWNER`.
2. **Thêm User 2 vào campaign:** `POST /campaigns/1/members`
   ```json
   {
     "user_id": 2
   }
   ```
   -> Kỳ vọng `201 Created`.
3. **Xem danh sách thành viên:** `GET /campaigns/1/members`
   -> Thấy 2 user: User 1 (`OWNER`) và User 2 (`MEMBER`).

### 2. Luồng bắt lỗi
* **Người ngoài xem campaign:** Đổi sang token của `nguoingoai@gmail.com` (User 3) và gọi `GET /campaigns/1` -> Kỳ vọng `403 Forbidden` ("You are not a member of this campaign").
* **ID không tồn tại:** Gọi `GET /campaigns/999` -> Kỳ vọng `404 Not Found`.
* **Tên campaign để trống:** `POST /campaigns` với `"name": "   "` -> Kỳ vọng `400 Bad Request`.

---

## Kịch bản 3: Quản lý công việc (Campaign Tasks)

### 1. Luồng chạy đúng
1. **Trưởng phòng tạo task và gán cho Nhân viên:** `POST /campaigns/1/campaign-tasks` *(dùng token User 1)*
   ```json
   {
     "title": "Thiết kế Banner Tết",
     "description": "Size 1920x1080",
     "priority": "HIGH",
     "status": "TODO",
     "assignee_id": 2
   }
   ```
   -> Kỳ vọng `201 Created`, nhận được task `id: 1`.
2. **Nhân viên nhận việc và đổi trạng thái:** *(đổi sang token User 2)*
   * Gọi `PATCH /campaign-tasks/1`:
     ```json
     {
       "status": "IN_PROGRESS"
     }
     ```
   * Gọi `GET /campaign-tasks/1`: Thấy trạng thái đã đổi thành `IN_PROGRESS`.
3. **Lọc danh sách task:** `GET /campaigns/1/campaign-tasks?status=IN_PROGRESS`
   -> Trả về đúng danh sách các task đang làm.

### 2. Luồng bắt lỗi
* **Gán việc cho người ngoài:** Tạo task với `"assignee_id": 3` (User 3 không thuộc campaign) -> Kỳ vọng `400 Bad Request` ("Assignee must be a member of this campaign").
* **Member thường đổi người nhận việc:** User 2 gọi `PATCH /campaign-tasks/1` đổi `assignee_id` -> Kỳ vọng `403 Forbidden` (Chỉ Owner mới có quyền đổi người làm).

---

## Kịch bản 4: Bình luận trao đổi (Task Comments)

### 1. Luồng chạy đúng
1. **Nhân viên comment báo tiến độ:** `POST /campaign-tasks/1/comments` *(dùng token User 2)*
   ```json
   {
     "content": "Đã gửi bản nháp banner lên drive nhé sếp."
   }
   ```
   -> Kỳ vọng `201 Created`.
2. **Xem danh sách comment:** `GET /campaign-tasks/1/comments`
   -> Thấy comment kèm họ tên người gửi và thời gian tạo.

### 2. Luồng bắt lỗi
* **Người ngoài comment:** Dùng token User 3 gọi `POST /campaign-tasks/1/comments` -> Kỳ vọng `403 Forbidden`.
* **Nội dung rỗng:** Gửi `"content": "   "` -> Kỳ vọng `400 Bad Request` ("Content cannot be empty").

---

## Kịch bản 5: Upload & Xem file đính kèm (Task Attachments)

### 1. Luồng chạy đúng
1. **Upload file:** `POST /campaign-tasks/1/attachments` *(dùng token User 2)*
   * `task_id`: `1`
   * Chọn 1 file ảnh (`.png`, `.jpg`) hoặc pdf từ máy tính.
   -> Kỳ vọng `201 Created`, nhận được `id: 1` và tên file gốc.
2. **Xem chi tiết file:** `GET /campaign-tasks/attachments/1`
   -> Trả về metadata của file (tên file, dung lượng, ai upload).

### 2. Luồng bắt lỗi
* **Người ngoài xem file:** Dùng token User 3 gọi `GET /campaign-tasks/attachments/1` -> Kỳ vọng `403 Forbidden`.
* **Xem file không tồn tại:** `GET /campaign-tasks/attachments/999` -> Kỳ vọng `404 Not Found`.

---

## Kịch bản 6: Xóa mềm chiến dịch (Soft Delete)

### 1. Luồng chạy đúng
1. **Owner xóa campaign:** Dùng token User 1 gọi `DELETE /campaigns/1` -> Kỳ vọng `204 No Content`.
2. **Kiểm tra sau xóa:** Gọi `GET /campaigns/1` -> Kỳ vọng `404 Not Found` (Campaign đã bị xóa mềm nên không tìm thấy nữa).

### 2. Luồng bắt lỗi
* **Member thường cố xóa campaign:** Dùng token User 2 gọi `DELETE /campaigns/1` -> Kỳ vọng `403 Forbidden` ("Only the campaign owner can perform this action").

---

## Bảng mã HTTP Status Code cần nhớ khi test

| Mã lỗi | Tên mã | Trường hợp xảy ra |
| :--- | :--- | :--- |
| **200 / 201 / 204** | Success | Thao tác thành công |
| **400** | Bad Request | Dữ liệu sai logic (trùng email, giao việc cho người ngoài...) |
| **401** | Unauthorized | Chưa truyền token hoặc token sai / hết hạn |
| **403** | Forbidden | Bị chặn do không có quyền trong campaign |
| **404** | Not Found | Không tìm thấy ID hoặc dữ liệu đã bị xóa mềm |
| **422** | Unprocessable Entity | Dữ liệu sai định dạng Pydantic (mật khẩu ngắn, thiếu trường...) |
