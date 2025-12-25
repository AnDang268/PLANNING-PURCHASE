# Đề xuất Phát triển: Hệ thống Báo cáo Phân tích Mua hàng & Dự báo (PRO)

Dựa trên nghiên cứu các mô hình quản trị chuỗi cung ứng hiện đại và cơ sở dữ liệu hiện có (`backend/models.py`), tôi đề xuất phát triển 3 Dashboard chuyên sâu sau để nâng tầm hệ thống Planning Purchase.

## 1. Purchasing Intelligence Dashboard (Phân tích Mua bản & Chi tiêu)
**Mục tiêu**: Giúp quản lý dòng tiền, theo dõi hiệu quả chi tiêu và phát hiện "Maverick Spend" (mua ngoài kế hoạch).

### Các chỉ số (Metrics)
*   **Spend Under Management (SUM)**: % Chi tiêu được quản lý (dựa trên `FactPurchasePlans`).
*   **Planned vs Actual Cost**: So sánh ngân sách dự kiến và giá thực tế (cần bổ sung thông tin giá vào `FactPurchasePlans`).
*   **Cost Savings**: Tiết kiệm đạt được do đàm phán hoặc mua đúng thời điểm.
*   **Purchase Price Variance (PPV)**: Biến động giá nhập theo thời gian.

### Mockup/Visual Suggestion
*   **Biểu đồ**: Bar Chart (Top 10 Category Spend), Line Chart (Spending Trend MoM), Donut Chart (Spend by Vendor).
*   **Layout**: Header KPI Cards + 2 cột (Spend Analysis | Category Drill-down).

---

## 2. Supplier 360° Performance (Đánh giá Hiệu quả Nhà cung cấp)
**Mục tiêu**: Đánh giá khách quan năng lực nhà cung cấp để ra quyết định tái ký hợp đồng hoặc tìm nguồn mới.
**Dữ liệu nguồn**: `FactVendorPerformance`, `DimVendors`.

### Các chỉ số (Metrics)
*   **OTIF (On-Time In-Full)**: Tỷ lệ giao hàng đúng hạn và đủ số lượng.
*   **Lead Time Variance**: Độ lệch giữa Lead Time cam kết và thực tế (`avg_lead_time_actual`).
*   **Quality Defect Rate**: Tỷ lệ hàng lỗi/trả về (`quality_score`).
*   **Compliance Rate**: Tỷ lệ tuân thủ các điều khoản hợp đồng.

### Mockup/Visual Suggestion
*   **Biểu đồ**: Spider Chart (So sánh các Vendor trên 5 trục: Price, Quality, Delivery, Flexibility, Risk).
*   **Layout**: Bảng xếp hạng Vendor (Leaderboard) bên trái, chi tiết từng Vendor bên phải.

---

## 3. Advanced Demand Forecasting (Dự báo Nhu cầu Nâng cao)
**Mục tiêu**: Tối ưu hóa tồn kho thông qua dự báo chính xác, giảm thiểu Stock-out (hết hàng) và Over-stock (tồn đọng).
**Dữ liệu nguồn**: `FactForecasts`, `FactSales`, `FactInventorySnapshots`.

### Các chỉ số (Metrics)
*   **Forecast Accuracy (MAPE/FA)**: Độ chính xác của dự báo so với thực tế bán hàng.
*   **Safety Stock Coverage**: Thời gian tồn kho an toàn có thể đáp ứng (`safety_stock_required`).
*   **Inventory Turnover**: Vòng quay hàng tồn kho.
*   **Bias Tracking**: Xu hướng dự báo cao hơn hay thấp hơn thực tế liên tục.

### Mockup/Visual Suggestion
*   **Biểu đồ**: 
    *   **Combo Chart**: Cột (Actual Sales) + Đường (Forecast) + Vùng bóng mờ (Confidence Interval 95%).
    *   **Heatmap**: Độ chính xác dự báo theo Category/SKU.
*   **Công cụ**: What-if Scenario (Nếu tăng giá 5% thì Demand giảm bao nhiêu?).

---

## Đánh giá Kỹ thuật (Gap Analysis)
Hiện tại `backend/models.py` đã hỗ trợ tốt cho Dashboard 2 & 3. Để triển khai trọn vẹn, cần bổ sung:
1.  **Dữ liệu Giá (Price)**: Bổ sung cột `unit_price`, `total_amount` vào `FactPurchasePlans` để tính toán Spend.
2.  **Dữ liệu Đơn hàng Thực tế (Purchase Orders)**: Cần tách biệt rõ giữa "Kế hoạch" (`FactPurchasePlans`) và "Đơn đặt hàng thực tế" (Purchase Orders) nếu muốn đo lường `Planned vs Actual`.

**Bạn muốn ưu tiên triển khai Dashboard nào trước?**
