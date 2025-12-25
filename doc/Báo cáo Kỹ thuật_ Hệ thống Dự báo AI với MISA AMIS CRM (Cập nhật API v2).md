# **Báo cáo Phân tích Kỹ thuật: Hệ thống Dự báo Mua hàng & Bán hàng AI với MISA AMIS CRM**

## **1\. Tổng quan Điều hành**

Báo cáo này trình bày phương án kỹ thuật để xây dựng hệ thống "Intelligent Demand Planning" (Hoạch định Nhu cầu Thông minh), kết nối trực tiếp với MISA AMIS CRM. Mục tiêu là thay thế các quyết định nhập hàng dựa trên cảm tính hoặc trung bình quá khứ bằng các mô hình Trí tuệ nhân tạo (AI) và Học máy (Machine Learning).

Hệ thống giải quyết hai bài toán cốt lõi:

1. **Sales Forecasting (Dự báo Bán hàng):** Dự đoán nhu cầu tiêu thụ trong tương lai dựa trên lịch sử đơn hàng và các tín hiệu thị trường.  
2. **Purchase Optimization (Tối ưu Mua hàng):** Xác định thời điểm và số lượng nhập hàng tối ưu để giảm chi phí tồn kho nhưng vẫn đảm bảo hàng hóa sẵn sàng.

## **2\. Chiến lược Dữ liệu & Tích hợp MISA AMIS**

Dữ liệu là nhiên liệu cho AI. Việc khai thác dữ liệu từ MISA AMIS CRM cần tuân thủ các đặc tả kỹ thuật API mới nhất (v2) để đảm bảo độ tin cậy.

### **2.1. Tích hợp API và Đồng bộ Dữ liệu**

Dựa trên tài liệu kỹ thuật API MISA AMIS \[1, 2, 4\], chiến lược tích hợp được đề xuất như sau:

* **Dữ liệu Giao dịch (Orders):** Sử dụng endpoint POST api/order/GetOrderInfo. Đây là điểm khác biệt so với chuẩn RESTful thông thường (dùng POST để lấy dữ liệu). Hệ thống cần xử lý phân trang (PageSize, PageIndex) để lấy toàn bộ lịch sử bán hàng.  
  * *Lưu ý kỹ thuật:* Cần xây dựng cơ chế "Watermark" (lưu dấu thời gian lần cuối đồng bộ) để chỉ tải về các đơn hàng mới hoặc có thay đổi, giảm tải cho hệ thống mạng.  
* **Dữ liệu Danh mục (Products):** Sử dụng GET /api/v2/Products hoặc POST.../Get để lấy thông tin sản phẩm.  
  * *Feature Engineering:* Tận dụng triệt để các trường ProductGroup (Nhóm hàng), Unit, Color để làm đặc trưng cho mô hình AI. Việc này giúp mô hình học được các mẫu hình bán hàng chéo (cross-learning) giữa các sản phẩm tương tự.

### **2.2. Xử lý Dữ liệu Tồn kho (Inventory Snapshots)**

Hệ thống CRM/ERP thường chỉ cung cấp tồn kho tại thời điểm hiện tại (Current Stock). Để AI học được mối quan hệ giữa "Tồn kho" và "Doanh số" (ví dụ: phát hiện việc mất doanh số do hết hàng), hệ thống cần một tiến trình chạy nền (Background Service) để chụp ảnh trạng thái tồn kho (Snapshot) vào cuối mỗi ngày và lưu vào Kho dữ liệu (Data Warehouse).

## **3\. Phương pháp luận AI & Thuật toán Dự báo**

Đặc thù của dữ liệu bán hàng, đặc biệt là B2B hoặc bán lẻ chuyên dụng, thường là dữ liệu không liên tục.

### **3.1. Phân loại Nhu cầu (Demand Segmentation)**

Trước khi dự báo, hệ thống sẽ phân loại từng mã hàng (SKU) dựa trên hai chỉ số:

* **ADI (Average Demand Interval):** Khoảng cách trung bình giữa các đơn hàng.  
* **CV² (Coefficient of Variation):** Độ biến động của số lượng đặt hàng.

### **3.2. Lựa chọn Thuật toán (Model Selection)**

Hệ thống sử dụng chiến lược "Best Fit" tự động chọn mô hình tối ưu cho từng nhóm hàng:

| Nhóm Hàng | Đặc điểm | Thuật toán Đề xuất | Lý do Kỹ thuật |
| :---- | :---- | :---- | :---- |
| **Bán chạy (Fast-moving)** | Đơn hàng đều đặn, độ biến động thấp. | **AutoARIMA, ETS** | Hiệu quả cao, nhanh, nắm bắt tốt tính mùa vụ (Seasonality). |
| **Bán chậm/Ngắt quãng (Intermittent)** | Nhu cầu thưa thớt, nhiều ngày bằng 0\. | **Croston Optimized, ADIDA** | Tách biệt dự báo "khi nào có đơn" và "số lượng bao nhiêu". Tránh việc dự báo ra các số lẻ vô nghĩa (VD: 0.1 cái/ngày).\[5, 6\] |
| **Sản phẩm mới/Khuyến mãi** | Ít dữ liệu lịch sử, phụ thuộc sự kiện. | **XGBoost, LightGBM** | Mô hình cây quyết định xử lý tốt các biến ngoại sinh (Exogenous variables) như lịch khuyến mãi, thuộc tính sản phẩm. |

## **4\. Tối ưu Hóa Mua hàng (Purchase Optimization)**

Đầu ra của dự báo bán hàng chỉ là con số dự đoán. Để chuyển đổi thành quyết định mua hàng, hệ thống áp dụng thuật toán **Dynamic Safety Stock** (Tồn kho an toàn động).

### **4.1. Dự báo Lead Time (Thời gian giao hàng)**

Thay vì dùng Lead Time cố định (VD: 7 ngày), hệ thống tính toán Lead Time thực tế dựa trên lịch sử giao hàng của nhà cung cấp, có tính đến các yếu tố mùa vụ (tắc biên, lễ tết).

### **4.2. Công thức Đặt hàng (Reorder Point Logic)**

Hệ thống tính toán điểm đặt hàng ($ROP$) hàng ngày:

$$ROP \= \\text{Lead Time Demand} \+ \\text{Safety Stock}$$  
Điểm đột phá là cách tính Safety Stock ($SS$):  
Thay vì dựa trên biến động nhu cầu thô (thường rất lớn), hệ thống dựa trên sai số của mô hình dự báo ($RMSE$). Khi mô hình AI dự báo càng chính xác, sai số $RMSE$ càng nhỏ, dẫn đến lượng $SS$ cần giữ càng thấp. Điều này trực tiếp giúp doanh nghiệp giảm vốn tồn kho (Working Capital) mà không làm tăng rủi ro đứt hàng.

## **5\. Kết luận và Khuyến nghị**

Việc triển khai hệ thống này đòi hỏi sự kết hợp chặt chẽ giữa Kỹ thuật phần mềm (để lấy dữ liệu ổn định từ MISA API) và Khoa học dữ liệu (để tinh chỉnh mô hình).

**Lộ trình triển khai khuyến nghị:**

1. **Giai đoạn 1 (Foundation):** Xây dựng Data Pipeline lấy dữ liệu Orders và Products từ MISA về Data Warehouse. Thiết lập quy trình Snapshot tồn kho hàng ngày.  
2. **Giai đoạn 2 (Pilot):** Chạy thử nghiệm mô hình dự báo thống kê (StatsForecast) cho top 20% sản phẩm chủ lực (nhóm A).  
3. **Giai đoạn 3 (Scale & Optimize):** Mở rộng cho toàn bộ danh mục. Tích hợp module đề xuất nhập hàng tự động vào quy trình mua hàng.

Giải pháp này không chỉ giúp tự động hóa quy trình mà còn chuyển đổi dữ liệu thụ động trên MISA AMIS thành tài sản chiến lược, giúp doanh nghiệp tối ưu hóa dòng tiền và gia tăng lợi thế cạnh tranh.