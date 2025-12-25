
# Quy định Đánh Phiên Bản & Quy trình Release (Versioning Policy)

Tài liệu này quy định cách đánh số phiên bản và quy trình đóng gói (build/release) cho dự án Planning & Purchase.

## 1. Nguyên tắc Đánh số Phiên bản (Semantic Versioning)
Áp dụng chuẩn **Semantic Versioning 2.0.0** (MAJOR.MINOR.PATCH):
- **MAJOR** (x.0.0): Thay đổi lớn, phá vỡ tương thích ngược (Breaking changes).
  - Ví dụ: Thay đổi hoàn toàn Database Schema, đổi công nghệ Frontend.
- **MINOR** (1.x.0): Thêm tính năng mới, nhưng vẫn tương thích ngược.
  - Ví dụ: Thêm module Dự Báo, thêm báo cáo mới.
- **PATCH** (1.1.x): Sửa lỗi nhỏ (Bug fix), không thay đổi tính năng.

**Ví dụ:** `v1.0.0` (Release đầu tiên) -> `v1.0.1` (Hotfix lỗi login) -> `v1.1.0` (Thêm tính năng Chat).

## 2. Nơi Lưu Trữ Phiên Bản
Phiên bản hiện tại của hệ thống phải được cập nhật đồng bộ tại các vị trí sau trước khi Release:

### Frontend
- **File:** `frontend/package.json`
- **Field:** `"version": "x.y.z"`
- **Hiển thị UI:** Footer hoặc trang Settings phải hiển thị version này (Lấy từ `package.json`).

### Backend
- **File:** `backend/main.py`
- **Variable:** `version="x.y.z"` trong `FastAPI(..., version="x.y.z")`
- **API Endpoint:** `GET /` phải trả về `{"version": "x.y.z"}`.

## 3. Quy trình Release (Production Deployment)

### Bước 1: Chuẩn bị Release (Pre-Release)
1. Kiểm tra toàn bộ Checklist chức năng (`task.md`).
2. Chạy toàn bộ Verification Scripts (`backend/verify_*.py`).
3. Đảm bảo không còn biến `locahost` hardcode (Kiểm tra `frontend/src/config.ts`).

### Bước 2: Tăng Version
1. Backend: Tăng version trong `backend/main.py`.
2. Frontend: Tăng version trong `package.json`.
3. Frontend Config: Tạo/Cập nhật file `.env.production` (hoặc `.env.local`) chứa link API Production.

### Bước 3: Build & Deploy
1. **Frontend Build:**
   ```bash
   cd frontend
   npm run build
   # Output: thư mục .next (hoặc out nếu export tĩnh)
   ```
2. **Backend Start:**
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

## 4. Changelog (Nhật ký thay đổi)
Mỗi bản Release phải được ghi chú vào file `CHANGELOG.md` theo format:
```markdown
## [1.1.0] - 2025-12-25
### Added
- Tính năng Dự báo nhu cầu (Forecasting).
- Module quản lý Nhà cung cấp (Supplier 360).

### Fixed
- Lỗi 500 khi import sản phẩm có ký tự đặc biệt.
```
