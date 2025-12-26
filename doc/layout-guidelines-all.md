# Quy Tắc Thiết Kế Layout Web Chuẩn (Complete Edition)

**Design Style**: Modern Clean Minimalism (Enterprise SaaS)  
*Inspired by: Geist Design (Vercel) & Shadcn/UI*

Tài liệu style-guide tổng hợp cho layout web/app: grid, spacing, alignment, components, color system, accessibility và responsive.

---

## 1. Viewport, Breakpoints & Container

### 1.1 Breakpoints

| Thiết bị | Viewport | Breakpoint | Container max-width |
|----------|----------|------------|---------------------|
| Mobile   | 360–414px | 0–767px   | 100% viewport       |
| Tablet   | 768–1023px | 768px    | ~960px              |
| Laptop   | 1366x768  | 1024px    | ~1140px             |
| Desktop  | 1920x1080 | 1200px+   | 1200–1400px         |

**Quy tắc**: Mobile-first, container center với `max-width` + `margin: 0 auto`, padding 20-40px (desktop), 12-16px (mobile).

---

## 2. Grid System & Baseline Grid

### 2.1 12-Column Grid

```css
.grid-12 {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
}
```

### 2.2 Spacing System - 8pt Grid

**Bội số 8**: 8, 16, 24, 32, 40, 48, 64, 80px  
Tất cả margin, padding, gap phải theo hệ này.

---

## 3. Spacing Rules

### Internal ≤ External
- Padding trong component ≤ margin giữa components

### Gợi ý
- Icon + text: 8px
- Giữa dòng text trong card: 8-16px  
- Giữa cards: 16-24px
- Giữa sections: 48-80px

---

## 4. Alignment

### 4.1 Grid Alignment
- Mọi element bám cột grid
- Chọn 1 trục dọc chính (left edge) làm baseline

### 4.2 Text
- Body text: `text-align: left`
- Hero/short content: có thể center
- Tránh justify

### 4.3 Components
```css
.row {
  display: flex;
  align-items: center; /* hoặc baseline */
  justify-content: space-between;
}
```

---

## 5. Typography & Vertical Rhythm

### Scale
- H1: 48px (line-height 1.2)
- H2: 32px
- H3: 24px
- Body: 16px (line-height 1.5-1.6)
- Caption: 14px

### Rhythm
Line-height body ~24px cho 16px font. Margin heading/paragraph là bội số line-height.

---

## 6. Scroll Behavior

### Vertical
- Section padding: 48-80px
- Hero: `min-height: 60-100vh`
- Header có thể sticky

### Horizontal
- Chỉ dùng cho table rộng, carousel
- Cần hint (arrow, gradient) + sticky columns

---

## 7. Card & Multi-column

### 7.1 Card
- Bám grid (3 cards → mỗi card span 4)
- Padding: 16-20px
- Gap: 16-24px
- Structure: image → title → meta → text → actions

### 7.2 Layout 2 Cột

**QUY TẮC QUAN TRỌNG**:
- Mỗi card bắt đầu từ CÙNG cột grid
- Width rõ ràng: 6/12 - 6/12
- Padding đồng nhất
- Section header canh trái cùng left edge với cards
- Không mix full-width + half-width trong 1 hàng

```css
.grid-2-col {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}
```

**Responsive**:
- Desktop: 2-4 cột
- Tablet: 2 cột  
- Mobile: 1 cột

---

## 8. Dropdown, Tabs, Navigation

### 8.1 Dropdown
- Menu align với trigger
- Item height: 40-48px
- Icon-text spacing: 8px

### 8.2 Tabs
```css
.tabs {
  display: flex;
  gap: 16px;
  border-bottom: 1px solid #ddd;
}
.tab {
  padding: 8px 16px;
  border-bottom: 2px solid transparent;
}
.tab--active {
  border-bottom-color: currentColor;
}
```

**Quy tắc**:
- Height: 40-44px
- Gap tabs → content: 16-24px
- States rõ ràng: default/active/hover/focus
- Focus visible bằng keyboard
- Nhiều tabs: scroll ngang hoặc dropdown

---

## 9. Form & Selection Controls

### 9.1 Input
- Height: 40-48px (match button)
- Padding: 8-12px dọc, 12-16px ngang
- Label trên input, cách 4-8px
- Helper text dưới, cách 4-8px

### 9.2 Spacing
- Label → input: 4-8px
- Giữa fields: 16-24px
- Giữa nhóm: 24-32px

### 9.3 Selection Controls

**Radio** - chọn 1:
- Mutually exclusive
- 2-5 options
- Group label phía trên

**Checkbox** - chọn nhiều:
- Options độc lập
- "Select all" có indeterminate state

**Toggle/Switch**:
- ON/OFF ngay lập tức
- Tránh cho destructive actions

**Segmented Control**:
- Logic như radio
- UI group buttons
- Segments cùng height

### 9.4 Table
- Text: align left
- Numbers: align right
- Header sticky
- Cell padding: 8-16px
- Row height: 40-48px

---

## 10. Button, Filter & Pagination

### 10.1 Buttons
- Height: 40-48px (≥44px mobile)
- Padding ngang: 12-24px
- Cùng hàng: cùng height, align baseline
- Gap: 8-16px
- **States bắt buộc**: normal/hover/active/disabled/focus

### 10.2 Filter
- Nằm trên list/table
- Gap controls: 8-16px
- Có "Clear" và "Apply" buttons

### 10.3 Pagination
- Dưới list/table
- Item height: 32-40px
- Gap: 4-8px
- Pattern: Prev | 1 2 3 ... | Next

---

## 11. Images & Media

### Tỷ lệ
- Hero: 16:9 hoặc 21:9
- Thumbnail: 4:3
- Avatar: 1:1

### Responsive
```css
img {
  max-width: 100%;
  height: auto;
}
```

---

## 12. Banner & Hero

### Hero
- `min-height: 60-100vh`
- Content align grid (thường trái)

### Banner
- Section đầy đủ
- Padding: 48-80px
- Bám grid

### Overlay Text
- Safe area: 24-40px từ cạnh
- Contrast đạt chuẩn WCAG

---

## 13. Modal & Dialog

### Kích thước
- `max-width`: 600-900px
- `max-height`: 80-90vh
- Padding: 16-24px

### Cấu trúc 3 phần
1. **Header**: Icon + Title + Close (X)
2. **Body**: Content chính, `overflow-y: auto`
3. **Footer**: Buttons align phải

### Behavior
- Khóa scroll body: `overflow: hidden`
- Chỉ scroll trong modal body
- Focus vào title/first input khi mở
- Tab trap trong modal
- ESC để đóng
- Trả focus về trigger khi đóng

### Alignment
- Heading + field bám grid
- Heading nên đi kèm ít nhất 1-2 fields trong viewport đầu
- Tránh khoảng trắng lớn khi content ít

---

## 14. Document/PDF/Embed

- Container max-width = content width
- Height: 60-80vh
- Tránh nested scroll
- Preview + link mới cho document dài

---

## 15. Loading States

### 15.1 Spinner
```css
.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(0,0,0,0.1);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
```

**Sizes**: 16px (small) | 24px (medium) | 40-48px (large)

### 15.2 Skeleton
- Shape giống component thật
- Neutral color gradient
- Shimmer animation 1.5s
- Số lượng = số items dự kiến

### 15.3 Progress Bar
- Linear: top page, height 2-4px
- Circular: center modal, 40-60px
- Indeterminate khi không biết %

---

## 16. Toast, Notification & Alert

### 16.1 Toast
```css
.toast {
  position: fixed;
  top: 16px;
  right: 16px;
  min-width: 320px;
  max-width: 480px;
  padding: 12px 16px;
  z-index: 10000;
}
```

**Auto-dismiss**:
- Success: 3-4s
- Info/Warning: 5-7s  
- Error: manual hoặc ~10s

**Mobile**: top-center, full-width

### 16.2 Alert Banner
- Top của content area
- Border-left 4px
- Types: info/success/warning/error

### 16.3 Notification Panel
- Width: 360-400px
- Max-height: 480px
- Badge count trên icon
- Unread indicator
- Avatar + message + timestamp

---

## 17. Empty & Error States

### 17.1 Empty State
```
Icon (64-120px)
↓ 16-24px
Heading
↓ 8px
Description
↓ 24px
CTA Button
```

**Use**: List trống, no search results, no data

### 17.2 Error State
```
Error Icon
↓
Title: "Something went wrong"
↓
User-friendly message
↓
Error code (optional)
↓
Actions: Try again | Go back
```

**Types**: API failed, Network error, 403, 404, 500

---

## 18. Navigation Patterns

### 18.1 Breadcrumb
- Height: 32-40px
- Separator: "/" với spacing 8px
- Current page: không clickable, màu đậm
- Mobile: First + Last + "..."

### 18.2 Sidebar
- Width: 240-280px (expanded), 60-80px (collapsed)
- Fixed left, full height
- Item height: 40-48px
- Active: background + border-left 3px
- Mobile: drawer với overlay

### 18.3 Drawer
- Width: 300px, max 85vw
- Slide from left/right
- Overlay: rgba(0,0,0,0.5)
- Animation: 250-350ms
- Lock body scroll khi open

### 18.4 Accordion
- Header: 48-56px
- Chevron right → down khi mở
- Animation: 250-350ms
- Content padding: 16-24px
- **Accordion**: chỉ 1 panel mở
- **Collapsible**: nhiều panels mở

---

## 19. Contextual Help

### 19.1 Tooltip
- Trigger: hover 500ms
- Max-width: 200-280px
- Padding: 8-12px
- Font-size: 13-14px
- Arrow: 6-8px
- Auto-flip gần viewport edge

### 19.2 Popover
- Width: 320px
- Click trigger để mở/đóng
- Rich content (text, list, actions)
- ESC + click outside để đóng
- Tab trap, return focus khi đóng

---

## 20. Color System & Accessibility

### 20.1 Color Palette

```css
:root {
  /* Semantic */
  --color-primary: #1a73e8;
  --color-primary-hover: #185abc;
  --color-accent: #ff6d00;
  --color-success: #34a853;
  --color-warning: #f9ab00;
  --color-danger: #ea4335;

  /* Neutral - KHÔNG DÙNG PURE BLACK */
  --color-text-heading: #111827;
  --color-text-main: #1f2933;
  --color-text-muted: #6b7280;
  --color-text-disabled: #9ca3af;

  --color-border-subtle: #e5e7eb;
  --color-border-strong: #cbd5e1;

  --color-bg: #ffffff;
  --color-bg-subtle: #f9fafb;
  --color-bg-elevated: #ffffff;

  /* Focus */
  --focus-ring-color: #2563eb;
}
```

### 20.2 Quy Tắc CHỐNG "ĐEN THUI"

❌ **KHÔNG BAO GIỜ dùng `#000000`**

✅ **Thay vào đó**:
- Body text: `--color-text-main` (#1f2933)
- Headings: `--color-text-heading` (#111827)
- Labels/meta: `--color-text-muted` (#6b7280)
- Disabled/placeholder: `--color-text-disabled` (#9ca3af)

✅ **Section numbers/icons**: 
- Dùng `--color-primary` thay vì đen
- Hoặc màu xám trung tính

✅ **Background sections**:
- Dùng `--color-bg-subtle` (#f9fafb) để phân biệt sections
- Tránh text đen đặc trên nền trắng phẳng

### 20.3 Text Roles

| Role | Color | Weight | Size |
|------|-------|--------|------|
| Page Title | `--color-text-heading` | 600-700 | 24-32px |
| Section Title | `--color-text-heading` | 600 | 18-20px |
| Body Text | `--color-text-main` | 400 | 16px |
| Label/Meta | `--color-text-muted` | 400 | 13-14px |
| Disabled | `--color-text-disabled` | 400 | inherit |

### 20.4 Focus & States

```css
:where(button, a, input, select, textarea):focus-visible {
  outline: 2px solid var(--focus-ring-color);
  outline-offset: 2px;
}
```

**Bắt buộc mọi interactive element có**:
- Default state
- Hover state  
- Active state
- Disabled state
- **Focus state** (bắt buộc cho a11y)

### 20.5 Contrast Requirements

**WCAG 2.1 Level AA**:
- Normal text: ≥ 4.5:1
- Large text (18px+): ≥ 3:1
- UI components: ≥ 3:1

**Công cụ kiểm tra**:
- WebAIM Contrast Checker
- Chrome DevTools Accessibility

### 20.6 States Differentiation

Mỗi state phải có **sự khác biệt RÕ RÀNG**:
- Thay đổi màu + weight
- Hoặc màu + underline
- Hoặc background + border
- **KHÔNG** chỉ thay đổi độ sáng rất nhẹ

---

## Checklist Tổng Hợp

### Layout & Grid
- [ ] Container max-width + center
- [ ] 12-column grid system
- [ ] Spacing theo 8pt grid
- [ ] Mọi element bám grid

### Spacing
- [ ] Internal ≤ External
- [ ] Icon-text: 8px
- [ ] Cards gap: 16-24px
- [ ] Sections: 48-80px

### Typography
- [ ] Scale rõ ràng (48/32/24/16/14)
- [ ] Line-height ~1.5-1.6
- [ ] Vertical rhythm align grid

### Colors
- [ ] ❌ KHÔNG dùng #000000
- [ ] ✅ Dùng neutral scale
- [ ] Section numbers: primary color
- [ ] Text roles rõ ràng
- [ ] Contrast ≥ 4.5:1

### Components
- [ ] Button height 40-48px
- [ ] Input height match buttons
- [ ] Focus states visible
- [ ] Loading states rõ ràng
- [ ] Empty/error states complete

### Layout 2 Cột
- [ ] Cùng cột grid start
- [ ] Width đồng đều (6/12)
- [ ] Padding consistent
- [ ] Header align với cards

### Modal & Dialog ⭐
- [ ] ❌ KHÔNG có 2 nút X
- [ ] ✅ CHỈ 1 nút X ở header
- [ ] ❌ KHÔNG có nút X trên overlay
- [ ] ✅ Footer bắt buộc khi có form: [Hủy] [Lưu]
- [ ] ESC key đóng modal
- [ ] Click outside có confirm nếu có unsaved changes
- [ ] Focus trap trong modal
- [ ] Return focus về trigger khi đóng
- [ ] Body scroll locked khi modal mở
- [ ] Max-height 80-90vh, body scroll nếu dài

### Accessibility
- [ ] Focus visible
- [ ] Keyboard navigation
- [ ] ARIA labels
- [ ] Contrast đạt chuẩn
- [ ] Screen reader friendly

### Responsive
- [ ] Mobile-first CSS
- [ ] Breakpoints: 768/1024/1200
- [ ] 1 cột mobile, 2+ desktop
- [ ] Touch targets ≥ 44px

---

## Best Practices Tổng Kết

1. **Consistency > Creativity**: Giữ patterns nhất quán quan trọng hơn sáng tạo
2. **8pt Grid Everything**: Mọi spacing phải là bội số 8
3. **No Pure Black**: Dùng neutral scale cho text
4. **Focus States Required**: Bắt buộc cho accessibility
5. **Mobile Touch**: Targets ≥ 44px height
6. **Loading Feedback**: Luôn có loading indicator
7. **Error Handling**: Empty + error states đầy đủ
8. **Semantic Colors**: Primary/success/warning/danger rõ ràng

---

**Version**: 1.0  
**Last Updated**: December 2024