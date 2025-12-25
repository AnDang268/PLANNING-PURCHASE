# Layout & Design Verification Rules

Tài liệu này tổng hợp 2 nguồn: `layout-guidelines-all.md` (Quy tắc) và `design_system_starter.html` (Implementation). Dùng tài liệu này để kiểm tra bất kỳ màn hình nào trước khi commit.

---

## ⛔ 3 Quy tắc Bất di bất dịch (The Iron Rules)

1.  **NO Pure Black**: Tuyệt đối không dùng `#000000`. Text tối nhất là `#111827` (Heading) hoặc `#1f2933` (Body).
2.  **8pt Grid System**: Mọil spacing (margin, padding, gap) **phải** là bội số của 8px (8, 16, 24, 32...).
3.  **Focus States**: Mọi nút bấm, input, link **phải** có trạng thái focus visible (outline/border change).

---

## ✅ Checklist Kiểm tra Chi tiết

### 1. Typography & Colors
- [ ] **Heading Color**: `#111827` (Gray-900)
- [ ] **Body Color**: `#1f2933` (Gray-800) hoặc `#374151` (Gray-700)
- [ ] **Muted Text**: `#6b7280` (Gray-500)
- [ ] **Font Size Base**: 14px hoặc 16px (Không dùng lẻ 13px, 15px trừ trường hợp đặc biệt)
- [ ] **Data Contrast**: Text trên nền trắng phải đảm bảo độ tương phản (dùng Neutral Scale)

### 2. Spacing & Layout
- [ ] **Container**: `max-width: 1200px` (hoặc fluid có padding). Center align.
- [ ] **Section Gap**: Các khối nội dung lớn cách nhau 48-80px.
- [ ] **Component Gap**: Các thẻ Card cách nhau 16-24px.
- [ ] **Internal Spacing**: Padding bên trong Card/Modal phải đồng nhất (thường là 16px hoặc 24px).
- [ ] **Internal \u2264 External**: Khoảng cách bên trong thành phần luôn nhỏ hơn hoặc bằng khoảng cách giữa các thành phần.

### 3. Components

#### Buttons
- [ ] **Height**: 40px (Default) hoặc 32px (Small). Tránh dùng số lẻ.
- [ ] **Padding**: `px-4` (16px) hoặc `px-6` (24px).
- [ ] **Label**: Font weight Medium (500) hoặc Semibold (600).

#### Form Inputs
- [ ] **Height**: Khớp với Button (40px).
- [ ] **Label Spacing**: Label cách Input 4-8px.
- [ ] **Placeholder**: Màu `#9ca3af` (Gray-400), không đậm đường viền.

#### Cards
- [ ] **Border Radius**: 8px (hoặc 12px cho modal).
- [ ] **Border Color**: `border-border-subtle` (#e5e7eb/gray-200).
- [ ] **Shadow**: Dùng shadow nhẹ (`shadow-sm`) cho card thường, `shadow-lg` cho modal/dropdown.

### 4. Layout 2 Cột (Two-Column Layout)
- [ ] **Grid**: Sử dụng Grid System (VD: `grid-cols-2`).
- [ ] **Top Alignment**: Tiêu đề các cột phải thẳng hàng nhau.
- [ ] **Content Alignment**: Card đầu tiên của mỗi cột phải bắt đầu cùng trục hoành (Y-axis).

### 5. Modal & Dialog
- [ ] **Overlay**: Màu đen trong suốt (`bg-black/50`).
- [ ] **Close Button**: Luôn có nút X hoặc nút Cancel rõ ràng.
- [ ] **Scroll**: Chỉ scroll phần nội dung (Body), Header và Footer giữ cố định (Sticky) nếu nội dung dài.

---

## 🛠️ Công cụ Tự kiểm tra (Browser Console)

Bạn có thể chạy đoạn script sau trong Console để phát hiện nhanh lỗi vi phạm:

```javascript
function validateLayout() {
  const errors = [];
  
  // 1. Check Pure Black
  document.querySelectorAll('*').forEach(el => {
    const color = window.getComputedStyle(el).color;
    if (color === 'rgb(0, 0, 0)') errors.push(`Pure Black found: <${el.tagName}>`);
  });

  // 2. Check Spacing (Sample check for margins)
  document.querySelectorAll('.card, .btn, .input').forEach(el => {
    const style = window.getComputedStyle(el);
    const margin = parseInt(style.marginBottom);
    if (margin > 0 && margin % 4 !== 0) errors.push(`Bad Spacing (${margin}px): .${el.className}`);
  });

  if (errors.length > 0) {
    console.error("❌ FOUND LAYOUT VIOLATIONS:", errors);
  } else {
    console.log("✅ LAYOUT LOOKS GOOD!");
  }
}
validateLayout();
```
