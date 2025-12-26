# Hướng Dẫn Triển Khai (Deployment Guide)
**Dự án**: Planning & Purchasing System
**Last Updated**: 2025-12-25

Tài liệu này hướng dẫn chi tiết cách đóng gói và triển khai ứng dụng lên môi trường Production (Windows Server).

---

## 1. Yêu cầu Hệ thống
*   **OS**: Windows Server 2016/2019/2022.
*   **Database**: SQL Server 2017+ (Standard hoặc Enterprise).
*   **Runtime**:
    *   Python 3.10+
    *   Node.js 18+ (LTS)
    *   PM2 (Quản lý Process Node/Python) hoặc NSSM (Windows Service).
*   **Network**:
    *   Port 8000 (Backend API - FastAPI)
    *   Port 3000 (Frontend - Next.js)
    *   Port 3000 (Frontend - Next.js)
    *   Kết nối Internet (để sync MISA AMIS).

## 1.1 Môi trường Hybrid (Dev + Prod chung máy)
Nếu bạn sử dụng chính máy phát triển làm Server chạy thật (Local Production), bạn có thể bỏ qua việc cài đặt Service phức tạp.
*   **Chạy nhanh**: Sử dụng file `run_prod_local.bat` ở thư mục gốc.
    *   Nó sẽ tự động chạy Backend ở chế độ Production (multiprocess).
    *   Nó kiểm tra và chạy Frontend ở chế độ Production (`npm start`) thay vì Dev (`npm run dev`) để tối ưu tốc độ.
*   **Lưu ý**: Đảm bảo máy tính không bị Sleep/Hibernate để hệ thống hoạt động liên tục.

---

## 2. Chuẩn bị Production Build

### 2.1 Backend (FastAPI)
Không cần "build" như JS, nhưng nên tạo môi trường ảo sạch.

1.  **Cài đặt Python**: (Nếu chưa có)
2.  **Tạo venv**:
    ```powershell
    cd C:\App\PlanningSystem
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  **Cài dependencies**:
    ```powershell
    pip install -r requirements.txt
    ```
4.  **Kiểm tra file cấu hình**:
    *   Đảm bảo file `.env` (hoặc biến môi trường System) trỏ đúng Production DB.
    *   `DEBUG=False` trong `config.py` (nếu có).

### 2.2 Frontend (Next.js)
Frontend cần được build thành static/server-optimized files.

1.  **Cài dependencies**:
    ```powershell
    cd frontend
    npm install --production=false  # Cần dev deps để build
    ```
2.  **Chạy Build**:
    ```powershell
    npm run build
    ```
    *Kết quả thành công sẽ tạo thư mục `.next`.*

3.  **Dọn dẹp (Optional)**:
    ```powershell
    npm prune --production
    ```

---

## 3. Cấu hình Windows Service (Khuyên dùng NSSM)

Để ứng dụng tự chạy khi khởi động Server và tự restart khi crash.

### 3.1 Cài đặt NSSM
Download [NSSM](https://nssm.cc/download) và giải nén vào `C:\Tools\nssm`.

### 3.2 Service: Backend API
1.  Mở CMD (Admin).
2.  Chạy:
    ```cmd
    nssm install PlanningBackend
    ```
3.  **Tab Application**:
    *   **Path**: `C:\App\PlanningSystem\venv\Scripts\python.exe`
    *   **Startup directory**: `C:\App\PlanningSystem`
    *   **Arguments**: `-m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4`
4.  **Tab Details**:
    *   **Display name**: Planning System Backend
    *   **Startup type**: Automatic
5.  Click **Install service**.

### 3.3 Service: Frontend UI
1.  Chạy:
    ```cmd
    nssm install PlanningFrontend
    ```
2.  **Tab Application**:
    *   **Path**: `C:\Program Files\nodejs\npm.cmd`
    *   **Startup directory**: `C:\App\PlanningSystem\frontend`
    *   **Arguments**: `start`
3.  **Tab Details**:
    *   **Display name**: Planning System Frontend UI
    *   **Startup type**: Automatic
4.  Click **Install service**.

---

## 4. Cấu hình IIS (Reverse Proxy - Optional)

Nếu muốn chạy trên Port 80/443 (HTTPS) thay vì 3000.

1.  Cài đặt **IIS** và **URL Rewrite Module**.
2.  Cài đặt **Application Request Routing (ARR)**.
3.  Tạo Website mới (VD: `planning.company.com`).
4.  Cấu hình **URL Rewrite**:
    *   Match URL: `(.*)`
    *   Action: Rewrite to `http://localhost:3000/{R:1}`
5.  (Tương tự cho API `/api/*` nếu muốn chung domain, rewrite sang `http://localhost:8000`).

---

## 5. Vận hành & Maintenance

### 5.1 Logs
*   **Backend**: Xem logs qua Event Viewer (nếu dùng NSSM) hoặc redirect stdout trong tab I/O của NSSM.
*   **Frontend**: `npm start` logs ra console.

### 5.2 Update phiên bản
1.  Stop Services:
    ```cmd
    net stop PlanningBackend
    net stop PlanningFrontend
    ```
2.  Pull code mới từ Git.
3.  Chạy lại `npm run build` (Frontend).
4.  Chạy Migrations (Backend):
    ```powershell
    python migrate_schema.py
    ```
5.  Start Services:
    ```cmd
    net start PlanningBackend
    net start PlanningFrontend
    ```

### 5.3 Backup
*   Cấu hình SQL Server Agent để backup Database `PlanningDB` hàng ngày lúc 23:00.

---
**Hỗ trợ kỹ thuật**: Liên hệ Team Dev hoặc CTO.
