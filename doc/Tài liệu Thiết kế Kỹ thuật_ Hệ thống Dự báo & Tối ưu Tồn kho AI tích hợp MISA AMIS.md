# **Tài liệu Thiết kế Kỹ thuật (SDD)**

Dự án: Hệ thống Dự báo Nhu cầu & Tối ưu Tồn kho (AI Demand Planning)  
Phiên bản: 1.0.0  
Ngày cập nhật: 23/12/2025  
Nguồn dữ liệu: MISA AMIS CRM & ERP

## ---

**1\. Tổng quan Kiến trúc (System Architecture)**

Hệ thống được thiết kế theo mô hình **Microservices** để đảm bảo khả năng mở rộng và bảo trì độc lập giữa các module lấy dữ liệu và module tính toán AI.

### **Sơ đồ luồng dữ liệu (Data Flow)**

Code snippet

graph LR  
    A \-- JSON (Orders, Products) \--\> B(Data Ingestion Service)  
    B \-- Raw Data \--\> C  
    C \-- Historical Data \--\> D\[AI Engine (Python/FastAPI)\]  
    D \-- Forecast & PO Recommendations \--\> C  
    C \--\> E  
    C \--\> F

## ---

**2\. Đặc tả Tích hợp MISA AMIS API (Integration Spec)**

### **2.1. Xác thực (Authentication)**

* **Giao thức:** Service Token hoặc OAuth 2.0 (tùy gói license).  
* **Token Lifecycle:** Token thường có hiệu lực trong 12-24h. Service cần implement cơ chế **Auto-refresh** khi gặp lỗi 401 Unauthorized.

### **2.2. Chi tiết Endpoints & Chiến lược Đồng bộ**

#### **A. Dữ liệu Đơn hàng (Sales Orders) \- Transaction Data**

Đây là dữ liệu quan trọng nhất để huấn luyện mô hình dự báo nhu cầu.

* **API Endpoint:** POST api/order/GetOrderInfo \[1, 2\]  
* **Method:** POST (Lưu ý: MISA sử dụng POST để truy vấn dữ liệu thay vì GET trong một số endpoint).  
* **Payload Request Mẫu:**  
  JSON  
  {  
    "serviceToken": "{{SERVICE\_TOKEN}}",  
    "PageSize": 100,  
    "PageIndex": 1,  
    "FromDate": "2024-01-01",  // Dùng cho Incremental Sync  
    "ToDate": "2024-12-31"  
  }

* **Chiến lược Đồng bộ (Sync Strategy):**  
  * **Initial Load:** Chạy loop qua tất cả PageIndex để lấy toàn bộ lịch sử 3 năm gần nhất.  
  * **Incremental Sync:** Chạy Cronjob mỗi 1 giờ. Lưu LastSyncTimestamp. Chỉ query các đơn hàng có ModifiedDate \>= LastSyncTimestamp. Nếu API không hỗ trợ lọc ModifiedDate, sử dụng phương pháp "Look-back Window" (lấy dữ liệu 7 ngày qua và Upsert).

#### **B. Dữ liệu Danh mục Sản phẩm (Product Master) \- Master Data**

Dữ liệu này cung cấp các đặc trưng tĩnh (Static Features) cho AI (Nhóm hàng, Màu sắc, Đơn vị).

* **API Endpoint:** GET /api/v2/Products (hoặc POST /api/v2/Products/paging tùy version API server) \[3, 4\]  
* **Mapping Quan trọng:**  
  * ProductCode \-\> sku\_id (Khóa chính)  
  * ProductGroup \-\> category (Feature cho Hierarchical Forecasting)  
  * Color, Model, Unit \-\> attributes (JSONB)

#### **C. Dữ liệu Tồn kho (Inventory Levels)**

* **Thách thức:** API thường chỉ trả về tồn kho *hiện tại*, không có lịch sử.  
* **Giải pháp:** Xây dựng bảng inventory\_snapshots.  
* **Cronjob:** Chạy lúc 23:59 hàng ngày.  
  * Gọi API lấy tồn kho hiện tại của tất cả SKU.  
  * Ghi một bản ghi vào bảng inventory\_snapshots với snapshot\_date \= today.  
  * **Mục đích:** Giúp AI phân biệt được ngày "không bán được hàng do hết hàng" (Stockout) vs "không bán được do không có nhu cầu" (Zero Demand).

## ---

**3\. Thiết kế Cơ sở Dữ liệu (Database Schema)**

Sử dụng **PostgreSQL** với extension **TimescaleDB** để tối ưu cho dữ liệu chuỗi thời gian.

### **Bảng dim\_products (Danh mục)**

| Column | Type | Description |
| :---- | :---- | :---- |
| sku\_id | VARCHAR(50) | **PK**. Mã sản phẩm từ MISA. |
| name | VARCHAR(255) | Tên sản phẩm. |
| category | VARCHAR(100) | Nhóm hàng (Feature quan trọng). |
| attributes | JSONB | Các thuộc tính (Màu, Size...). |
| lead\_time\_avg | INT | Thời gian nhập hàng trung bình (ngày). |
| demand\_class | VARCHAR(20) | Phân loại: SMOOTH, LUMPY, INTERMITTENT. |

### **Bảng fact\_sales (Lịch sử bán hàng)**

| Column | Type | Description |
| :---- | :---- | :---- |
| order\_id | VARCHAR(50) | Mã đơn hàng (MISA ID). |
| sku\_id | VARCHAR(50) | **FK**. |
| date | TIMESTAMPTZ | Ngày ghi nhận doanh số. |
| quantity | DECIMAL | Số lượng bán. |
| price\_unit | DECIMAL | Đơn giá bán thực tế. |
| customer\_id | VARCHAR(50) | Mã khách hàng (cho phân tích hành vi). |

### **Bảng forecast\_results (Kết quả dự báo)**

| Column | Type | Description |
| :---- | :---- | :---- |
| run\_id | UUID | Mã đợt chạy dự báo. |
| sku\_id | VARCHAR(50) | **FK**. |
| forecast\_date | DATE | Ngày thực hiện dự báo. |
| target\_date | DATE | Ngày được dự báo. |
| y\_pred | DECIMAL | Giá trị dự báo trung bình (Mean). |
| y\_pred\_p90 | DECIMAL | Cận trên khoảng tin cậy 90% (Dùng tính Safety Stock). |
| model\_name | VARCHAR(50) | Tên thuật toán sử dụng (VD: Croston, XGBoost). |

## ---

**4\. Module AI Engine (Python Specification)**

### **4.1. Thư viện & Công nghệ**

* **Language:** Python 3.10+  
* **Forecasting Lib:** nixtla/statsforecast (Hiệu năng cao, hỗ trợ Croston/ADIDA cho lumpy demand) .  
* **ML Lib:** scikit-learn, xgboost (cho mô hình hồi quy Lead Time).  
* **Data Processing:** pandas, numpy.

### **4.2. Logic Phân loại & Dự báo (Forecasting Logic)**

Hệ thống sẽ tự động chọn thuật toán dựa trên đặc tính chuỗi thời gian của từng SKU:

Python

from statsforecast import StatsForecast  
from statsforecast.models import AutoARIMA, CrostonOptimized, ADIDA

def select\_and\_train(df\_history):  
    \# 1\. Phân loại Demand Profile (Smooth vs Lumpy)  
    \# Tính ADI (Average Demand Interval) và CV2  
    adi \= calculate\_adi(df\_history)  
    cv2 \= calculate\_cv2(df\_history)

    models \=  
      
    if adi \> 1.32 and cv2 \> 0.49:  
        \# Lumpy Demand (Hàng bán chậm/biến động) \-\> Dùng Croston hoặc ADIDA  
        models \=  
    else:  
        \# Smooth Demand (Hàng bán chạy) \-\> Dùng ARIMA hoặc ETS  
        models \=  
      
    \# 2\. Huấn luyện  
    sf \= StatsForecast(models=models, freq='D', n\_jobs=-1)  
    sf.fit(df\_history)  
      
    \# 3\. Dự báo 30 ngày tới  
    forecast \= sf.predict(h=30, level=) \# Lấy confidence interval 90%  
    return forecast

### **4.3. Thuật toán Đề xuất Mua hàng (Reorder Logic)**

Input từ AI Forecast sẽ được đưa vào công thức tính toán tồn kho an toàn động:

1. **Dự báo Lead Time ($LT$):** Sử dụng trung bình trượt hoặc mô hình ML đơn giản từ lịch sử nhập hàng.  
2. Tính Safety Stock ($SS$):

   $$SS \= Z\_{95\\%} \\times \\sqrt{LT \\times \\sigma\_{error}^2}$$

   Trong đó $\\sigma\_{error}$ là độ lệch chuẩn của sai số dự báo (RMSE) trên tập validation, không phải độ lệch chuẩn của nhu cầu gốc.  
3. Tính Reorder Point ($ROP$):

   $$ROP \= (\\text{Daily Forecast} \\times LT) \+ SS$$  
4. **Quyết định:** Nếu Current\_Inventory \<= ROP $\\rightarrow$ Tạo cảnh báo "Cần nhập hàng".

## ---

**5\. Triển khai & Vận hành (Deployment)**

* **Dockerize:** Đóng gói Data Ingestion và AI Engine thành các container riêng biệt.  
* **Job Scheduler:** Sử dụng **Celery Beat** hoặc **Airflow** để điều phối quy trình:  
  * 01:00 AM: Sync Orders & Products từ MISA.  
  * 02:00 AM: Retrain models & Generate Forecast.  
  * 03:00 AM: Update Dashboard & Send Alert Email.  
* **Monitoring:** Theo dõi chỉ số **MAPE** (Mean Absolute Percentage Error) và **Bias** hàng tuần để phát hiện sự suy giảm độ chính xác của mô hình.