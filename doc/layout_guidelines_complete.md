# Quy Tắc Thiết Kế Layout Web Chuẩn (Complete Edition v2.0)

**Design Style**: Modern Clean Minimalism (Enterprise SaaS)  
*Inspired by: Geist Design (Vercel), Shadcn/UI, Linear, Stripe*

Tài liệu style-guide tổng hợp cho layout web/app: grid, spacing, alignment, components, color system, accessibility và responsive.

---

## 0. Design Philosophy - Modern Clean Minimalism

### 🎨 Nguồn Cảm Hứng

Kiểu thiết kế này gọi là **"Modern Clean Minimalism"** hoặc **"Enterprise SaaS Style"**, lấy cảm hứng từ:

- **Shadcn/UI**: Component library với utility-first approach
- **Geist Design (Vercel)**: Clean, airy, minimal aesthetic  
- **Linear**: Thoughtful interactions và micro-animations
- **Stripe**: Professional, trustworthy, scannable
- **Notion**: Card-based, hierarchical information architecture

### 🎯 Core Principles

#### 1. Clean & Airy (Thoáng Đãng)
**Đặc điểm**:
- Nhiều whitespace (khoảng trắng) giữa elements
- Ít đường kẻ thừa, chỉ dùng borders khi thực sự cần thiết
- Borders: subtle (1px, màu nhạt #e5e7eb), KHÔNG dùng thick borders
- Shadows: soft và minimal để tạo depth thay vì borders

**Tại sao**: Giúp content "thở", giảm cognitive load, dễ scan thông tin.

#### 2. No Pure Black (Không Dùng Đen Tuyền)
**Đặc điểm**:
- ❌ Tránh `#000000` - gây căng thẳng thị giác, harsh contrast
- ✅ Dùng Neutral Gray scale: #1f2933, #111827, #374151
- Text màu đen "ấm" hơn, dịu mắt hơn

**Tại sao**: Pure black tạo contrast quá mạnh trên màn hình phát sáng, gây mỏi mắt. Xám đậm vẫn đủ contrast nhưng softer.

#### 3. Card-Based Layout (Bố Cục Dựa Trên Card)
**Đặc điểm**:
- Gom nhóm data vào Cards với border radius 8-12px
- Elevation: subtle shadow thay vì thick borders
- Hierarchy rõ ràng: card > section > page
- Mỗi card là một content unit độc lập

**Tại sao**: Dễ scan, dễ hiểu mối quan hệ giữa các nhóm thông tin, responsive tốt.

#### 4. Utility-First (Đồng Bộ Theo Utility Classes)
**Đặc điểm**:
- Component sizes đồng bộ: 40px, 48px (divisible by 8)
- 8pt grid cho ALL spacing
- Reusable patterns, không tạo custom size mỗi component
- Consistent naming và values

**Tại sao**: Giảm decision fatigue, tăng consistency, dễ maintain.

#### 5. Subtle Motion (Chuyển Động Tinh Tế)
**Đặc điểm**:
- Micro-interactions với animations smooth (150-250ms)
- Transitions cho hover, focus, state changes
- Không flashy, không over-animate

**Tại sao**: Tạo feedback tức thì, guided user attention, premium feeling.

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

### 1.2 Touch Targets (Mobile)

**Quy tắc bắt buộc**:
- ✅ ALL interactive elements ≥ **44px** height trên mobile (iOS/Android guideline)
- ✅ Spacing giữa touch targets ≥ 8px
- ✅ Buttons, links, inputs phải đủ lớn để tap dễ dàng

```css
@media (max-width: 767px) {
  .button, .link, input, select {
    min-height: 44px;
    min-width: 44px; /* For icon buttons */
  }
}
```

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

**Tại sao 8pt?**:
- Divisible by 2, 4 → dễ scale (half, quarter)
- Match common screen densities (1x, 1.5x, 2x)
- Align với typical font sizes (16px base)

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
- Tránh justify (gây rivers of whitespace)

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

### 5.1 Type Scale

| Element | Size | Line-height | Weight | Usage |
|---------|------|-------------|--------|-------|
| H1 | 48px | 1.2 | 600-700 | Page title |
| H2 | 32px | 1.3 | 600 | Section title |
| H3 | 24px | 1.4 | 600 | Subsection |
| H4 | 20px | 1.5 | 600 | Card title |
| Body | 16px | 1.5-1.6 | 400 | Main text |
| Small | 14px | 1.5 | 400 | Meta, labels |
| Caption | 13px | 1.4 | 400 | Captions |

### 5.2 Font Family Recommendations

**Modern SaaS Stack**:
```css
:root {
  /* Option 1: Geist (Vercel's font) */
  --font-sans: 'Geist', system-ui, sans-serif;
  
  /* Option 2: Inter (most popular) */
  --font-sans: 'Inter', system-ui, sans-serif;
  
  /* Option 3: System fonts (no loading) */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
               'Roboto', 'Helvetica', sans-serif;
  
  /* Monospace for code */
  --font-mono: 'Geist Mono', 'Fira Code', 'Consolas', monospace;
}
```

**Quy tắc**:
- Variable fonts (Inter, Geist) cho smooth weight transitions
- Font-feature-settings: `'liga' 1, 'calt' 1` (ligatures)
- Letter-spacing: `-0.01em` cho headings lớn (48px+)

### 5.3 Vertical Rhythm

Line-height body ~24px cho 16px font. Margin heading/paragraph là bội số line-height.

```css
body {
  font-size: 16px;
  line-height: 24px; /* 1.5 */
}

h2 {
  margin-top: 48px; /* 2x line-height */
  margin-bottom: 16px;
}

p + p {
  margin-top: 16px;
}
```

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

### 7.1 Card Anatomy

**Cấu trúc chuẩn**:
```
┌─────────────────────────┐
│ [Image/Thumbnail]       │ ← Optional
├─────────────────────────┤
│ Title (H3/H4)           │ ← Required
│ Meta (date, author)     │ ← Optional
│                         │
│ Description text...     │ ← Optional
│                         │
│ [Button] [Link]         │ ← Actions (optional)
└─────────────────────────┘
```

**Styling**:
```css
.card {
  background: var(--bg-elevated);
  border-radius: var(--radius-lg); /* 12px */
  box-shadow: var(--shadow-sm);
  padding: 16-20px;
  transition: box-shadow var(--transition-base) var(--ease-out);
}

.card:hover {
  box-shadow: var(--shadow-md);
}
```

**Quy tắc**:
- Bám grid (3 cards → mỗi card span 4 columns)
- Padding: 16-20px
- Gap giữa cards: 16-24px
- Border radius: 12px (consistent)

### 7.2 Layout 2 Cột

**QUY TẮC QUAN TRỌNG**:
- Mỗi card bắt đầu từ CÙNG cột grid
- Width rõ ràng: 6/12 - 6/12
- Padding đồng nhất
- Section header canh trái cùng left edge với cards
- KHÔNG mix full-width + half-width trong 1 hàng

#### ❌ SAI - Cards không align grid

```html
<!-- KHÔNG LÀM NHƯ NÀY -->
<div class="container">
  <div class="card" style="width: 45%; margin-right: 5%">...</div>
  <div class="card" style="width: 50%">...</div>
</div>
```

**Vấn đề**: Width arbitrary (45%, 50%), không bám grid, spacing inconsistent.

#### ✅ ĐÚNG - Cards bám grid chính xác

```html
<div class="grid grid-cols-12 gap-6">
  <!-- Card 1 - chiếm 6 cột -->
  <div class="col-span-6">
    <div class="card">
      <h3>Card Title 1</h3>
      <p>Content...</p>
    </div>
  </div>
  
  <!-- Card 2 - chiếm 6 cột -->
  <div class="col-span-6">
    <div class="card">
      <h3>Card Title 2</h3>
      <p>Content...</p>
    </div>
  </div>
</div>
```

#### Visual Diagram

```
Grid: [1][2][3][4][5][6]│[7][8][9][10][11][12]
      └───────────────┘  └─────────────────┘
         Card A (6)           Card B (6)

Section Header
├─ [1-12] Full width
│
Cards Row
├─ [1-6]   Card A
└─ [7-12]  Card B
```

**Responsive**:
```css
/* Desktop: 2-4 cột */
@media (min-width: 1024px) {
  .grid-responsive { grid-template-columns: repeat(2, 1fr); }
}

/* Tablet: 2 cột */
@media (min-width: 768px) and (max-width: 1023px) {
  .grid-responsive { grid-template-columns: repeat(2, 1fr); }
}

/* Mobile: 1 cột */
@media (max-width: 767px) {
  .grid-responsive { grid-template-columns: 1fr; }
}
```

---

## 8. Dropdown, Tabs, Navigation

### 8.1 Dropdown
- Menu align với trigger (left/right edge match)
- Item height: 40-48px
- Icon-text spacing: 8px
- Max-height: 320px với scroll nếu dài

```css
.dropdown-menu {
  background: var(--bg-elevated);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: 4px;
  min-width: 200px;
}

.dropdown-item {
  height: 40px;
  padding: 0 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: var(--radius-sm);
}

.dropdown-item:hover {
  background: var(--bg-hover);
}
```

### 8.2 Tabs

```css
.tabs {
  display: flex;
  gap: 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.tab {
  padding: 8px 16px;
  height: 40-44px;
  border-bottom: 2px solid transparent;
  transition: all var(--transition-fast) var(--ease-out);
}

.tab--active {
  border-bottom-color: var(--color-primary);
  color: var(--color-primary);
  font-weight: 500;
}

.tab:hover:not(.tab--active) {
  color: var(--text-primary);
}
```

**Quy tắc**:
- Height: 40-44px
- Gap tabs → content: 16-24px
- States rõ ràng: default/active/hover/focus
- Focus visible bằng keyboard
- Nhiều tabs: scroll ngang (mobile) hoặc dropdown (desktop)

**Responsive**:
```html
<!-- Desktop: All tabs visible -->
<div class="tabs-scrollable">
  <button class="tab">Tab 1</button>
  <button class="tab">Tab 2</button>
  <!-- ... nhiều tabs -->
</div>

<!-- Mobile: Scrollable horizontal -->
<style>
@media (max-width: 767px) {
  .tabs-scrollable {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none; /* Firefox */
  }
  .tabs-scrollable::-webkit-scrollbar {
    display: none; /* Chrome, Safari */
  }
}
</style>
```

---

## 9. Form & Selection Controls

### 9.1 Input Fields

**Anatomy**:
```css
.form-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-input {
  height: 40-48px;
  padding: 8-12px 12-16px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 16px; /* Prevent zoom on iOS */
  transition: all var(--transition-fast);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
}

.form-helper {
  font-size: 13px;
  color: var(--text-muted);
}

.form-error {
  font-size: 13px;
  color: var(--color-danger);
}
```

**Quy tắc**:
- Height: 40-48px (match buttons)
- Label trên input, cách 4-8px
- Helper text dưới, cách 4-8px
- Error state: red border + error message
- Font-size ≥ 16px trên mobile (tránh auto-zoom iOS)

### 9.2 Spacing

- Label → input: 4-8px
- Giữa fields: 16-24px
- Giữa nhóm: 24-32px
- Form section padding: 24-32px

### 9.3 Selection Controls

#### **Radio Buttons** - Chọn 1

**Khi nào dùng**:
- Mutually exclusive options (chỉ chọn được 1)
- 2-5 options (nếu nhiều hơn → dropdown)
- Cần show all options cùng lúc

**Cấu trúc**:
```html
<fieldset class="radio-group">
  <legend>Select payment method</legend>
  <label class="radio-option">
    <input type="radio" name="payment" value="card">
    <span class="radio-label">Credit Card</span>
  </label>
  <label class="radio-option">
    <input type="radio" name="payment" value="bank">
    <span class="radio-label">Bank Transfer</span>
  </label>
</fieldset>
```

**Styling**:
```css
.radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: var(--radius-sm);
}

.radio-option:hover {
  background: var(--bg-hover);
}

input[type="radio"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
}
```

#### **Checkbox** - Chọn nhiều

**Khi nào dùng**:
- Options độc lập (có thể chọn 0, 1, hoặc nhiều)
- Cần "Select all" option
- Toggle features on/off

**States đặc biệt**:
- **Indeterminate**: Khi chỉ một số sub-items được chọn
  ```javascript
  checkbox.indeterminate = true;
  ```

**Ví dụ**:
```html
<label class="checkbox-option">
  <input type="checkbox" id="select-all">
  <span>Select All</span>
</label>
<div class="checkbox-group">
  <label class="checkbox-option">
    <input type="checkbox" name="features" value="1">
    <span>Feature 1</span>
  </label>
  <label class="checkbox-option">
    <input type="checkbox" name="features" value="2">
    <span>Feature 2</span>
  </label>
</div>
```

#### **Toggle/Switch** - ON/OFF tức thì

**Khi nào dùng**:
- Binary state (bật/tắt)
- Thay đổi có hiệu ứng NGAY LẬP TỨC (không cần save button)
- Settings, preferences

**KHÔNG dùng cho**:
- Destructive actions (delete, reset)
- Actions cần confirmation
- Khi cần submit form mới apply

**Styling**:
```css
.toggle {
  width: 44px;
  height: 24px;
  border-radius: 12px;
  background: var(--color-border-strong);
  position: relative;
  transition: background var(--transition-fast);
}

.toggle-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  position: absolute;
  left: 2px;
  top: 2px;
  transition: transform var(--transition-fast);
}

.toggle--on {
  background: var(--color-primary);
}

.toggle--on .toggle-thumb {
  transform: translateX(20px);
}
```

#### **Segmented Control** - Grouped options

**Khi nào dùng**:
- 2-4 mutually exclusive options (như radio)
- Options ngắn (1-2 words)
- UI đẹp hơn radio buttons
- View switching (List/Grid, Day/Week/Month)

**Cấu trúc**:
```html
<div class="segmented-control">
  <button class="segment segment--active">List</button>
  <button class="segment">Grid</button>
</div>
```

**Styling**:
```css
.segmented-control {
  display: inline-flex;
  background: var(--bg-subtle);
  border-radius: var(--radius-md);
  padding: 2px;
}

.segment {
  height: 32px;
  padding: 0 12px;
  border-radius: calc(var(--radius-md) - 2px);
  border: none;
  background: transparent;
  transition: all var(--transition-fast);
}

.segment--active {
  background: var(--bg-elevated);
  box-shadow: var(--shadow-sm);
}
```

### 9.4 Table

**Quy tắc**:
- Text: align left
- Numbers: align right
- Dates: align left (or right if sorting)
- Header sticky khi scroll
- Cell padding: 8-16px
- Row height: 40-48px
- Hover row: subtle background change

```css
.table {
  width: 100%;
  border-collapse: collapse;
}

.table thead {
  position: sticky;
  top: 0;
  background: var(--bg-elevated);
  box-shadow: 0 1px 0 var(--border-subtle);
  z-index: 10;
}

.table th {
  text-align: left;
  padding: 12px 16px;
  font-weight: 600;
  font-size: 14px;
  color: var(--text-muted);
}

.table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.table tbody tr:hover {
  background: var(--bg-hover);
}

/* Numbers align right */
.table td.numeric {
  text-align: right;
  font-variant-numeric: tabular-nums;
}
```

---

## 10. Button, Filter & Pagination

### 10.1 Buttons

**Hierarchy**:
```css
/* Primary - Main action */
.button-primary {
  background: var(--color-primary);
  color: white;
  border: none;
}

/* Secondary - Secondary actions */
.button-secondary {
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-strong);
}

/* Ghost - Tertiary actions */
.button-ghost {
  background: transparent;
  color: var(--text-primary);
  border: none;
}

/* Danger - Destructive actions */
.button-danger {
  background: var(--color-danger);
  color: white;
  border: none;
}
```

**Sizes**:
```css
.button {
  /* Base */
  height: 40px;
  padding: 0 16px;
  border-radius: var(--radius-md);
  font-weight: 500;
  transition: all var(--transition-fast);
}

.button--sm {
  height: 32px;
  padding: 0 12px;
  font-size: 14px;
}

.button--lg {
  height: 48px;
  padding: 0 24px;
  font-size: 16px;
}
```

**States (BẮT BUỘC)**:
```css
.button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.button:active:not(:disabled) {
  transform: translateY(0);
}

.button:focus-visible {
  outline: 2px solid var(--focus-ring-color);
  outline-offset: 2px;
}

.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

**Quy tắc**:
- Cùng hàng: cùng height, align baseline
- Gap giữa buttons: 8-16px
- Icon + text: gap 8px
- Loading state: spinner + disable interaction

### 10.2 Filter Bar

**Cấu trúc**:
```html
<div class="filter-bar">
  <div class="filter-group">
    <select class="filter-select">
      <option>All Categories</option>
    </select>
    <input type="search" class="filter-search" placeholder="Search...">
    <button class="filter-button">
      <icon>Filter</icon>
    </button>
  </div>
  <div class="filter-actions">
    <button class="button-secondary">Clear</button>
    <button class="button-primary">Apply</button>
  </div>
</div>
```

**Placement**:
- Nằm trên list/table
- Sticky khi scroll (optional)
- Gap controls: 8-16px
- Có "Clear" và "Apply" buttons (nếu filter không auto-apply)

### 10.3 Pagination

**Pattern**:
```html
<nav class="pagination">
  <button class="pagination-button" disabled>
    <icon>ChevronLeft</icon>
    Previous
  </button>
  
  <div class="pagination-pages">
    <button class="pagination-page pagination-page--active">1</button>
    <button class="pagination-page">2</button>
    <button class="pagination-page">3</button>
    <span class="pagination-ellipsis">...</span>
    <button class="pagination-page">10</button>
  </div>
  
  <button class="pagination-button">
    Next
    <icon>ChevronRight</icon>
  </button>
</nav>
```

**Styling**:
```css
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
}

.pagination-page {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  border: none;
  background: transparent;
}

.pagination-page--active {
  background: var(--color-primary);
  color: white;
}
```

**Quy tắc**:
- Dưới list/table
- Item height: 32-40px
- Gap: 4-8px
- Show: First | 1 2 3 ... Last | Next
- Mobile: Simple Prev/Next only

---

## 11. Images & Media

### 11.1 Aspect Ratios

| Type | Ratio | Use Case |
|------|-------|----------|
| Hero | 16:9 | Header images, banners |
| Ultra-wide | 21:9 | Cinematic banners |
| Thumbnail | 4:3 | Product cards, media cards |
| Square | 1:1 | Avatars, icons, Instagram-style |
| Portrait | 3:4 | Mobile hero, vertical cards |

### 11.2 Responsive Images

```css
img {
  max-width: 100%;
  height: auto;
  display: block;
}

.image-container {
  aspect-ratio: 16 / 9;
  overflow: hidden;
  border-radius: var(--radius-lg);
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

### 11.3 Loading & Performance

```html
<!-- Lazy loading -->
<img src="image.jpg" loading="lazy" alt="Description">

<!-- Responsive srcset -->
<img 
  src="image-800.jpg"
  srcset="image-400.jpg 400w,
          image-800.jpg 800w,
          image-1200.jpg 1200w"
  sizes="(max-width: 768px) 100vw,
         (max-width: 1200px) 50vw,
         33vw"
  alt="Description">
```

---

## 12. Banner & Hero

### 12.1 Hero Section

**Anatomy**:
```html
<section class="hero">
  <div class="hero-content">
    <h1>Main Headline</h1>
    <p>Supporting text or value proposition</p>
    <div class="hero-actions">
      <button class="button-primary">Get Started</button>
      <button class="button-secondary">Learn More</button>
    </div>
  </div>
  <div class="hero-visual">
    <img src="hero-image.jpg" alt="">
  </div>
</section>
```

**Styling**:
```css
.hero {
  min-height: 60vh; /* or 80vh, 100vh */
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 48px;
  padding: 48px 0;
}

.hero-content {
  max-width: 600px;
}

.hero h1 {
  font-size: 48px;
  line-height: 1.2;
  margin-bottom: 16px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  margin-top: 32px;
}

@media (max-width: 768px) {
  .hero {
    grid-template-columns: 1fr;
    min-height: auto;
  }
}
```

### 12.2 Banner

**Types**:
- Announcement banner (top of page, dismissable)
- Marketing banner (between sections)
- Alert banner (contextual, colored)

```css
.banner {
  width: 100%;
  padding: 48-80px 0;
  background: var(--bg-subtle);
  text-align: center;
}

.banner--full-bleed {
  padding: 80px 0;
  background: linear-gradient(to right, #667eea, #764ba2);
  color: white;
}
```

### 12.3 Overlay Text on Images

**Quy tắc**:
- Safe area: 24-40px từ cạnh
- Contrast đạt chuẩn WCAG (≥ 4.5:1)
- Dùng gradient overlay hoặc scrim

```css
.hero-image-overlay {
  position: relative;
}

.hero-image-overlay::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0) 0%,
    rgba(0, 0, 0, 0.6) 100%
  );
}

.hero-image-overlay .content {
  position: relative;
  z-index: 1;
  padding: 40px;
  color: white;
}
```

---

## 13. Modal & Dialog

### 13.1 Kích thước

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--bg-elevated);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  width: 90vw;
  max-width: 600px; /* Small modal */
  max-width: 900px; /* Large modal */
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}
```

### 13.2 Cấu trúc 3 phần

#### ✅ QUY TẮC QUAN TRỌNG - CHỈ MỘT NÚT X

```html
<div class="modal">
  <!-- Header: CHỈ 1 nút X duy nhất ở đây -->
  <div class="modal-header">
    <div class="modal-title-group">
      <icon>AlertCircle</icon>
      <h2>Confirm Action</h2>
    </div>
    <!-- ✅ NÚT X CHỈ Ở HEADER -->
    <button class="modal-close" aria-label="Close">
      <icon>X</icon>
    </button>
  </div>
  
  <!-- Body: Scrollable content -->
  <div class="modal-body">
    <p>Are you sure you want to continue?</p>
    <!-- Content có thể dài và scroll -->
  </div>
  
  <!-- Footer: Actions -->
  <div class="modal-footer">
    <button class="button-secondary">Hủy</button>
    <button class="button-primary">Lưu</button>
  </div>
</div>
```

**❌ KHÔNG BAO GIỜ**:
- ❌ Có 2 nút X (header + overlay)
- ❌ Chỉ có nút X trên overlay mà không có ở header
- ❌ Modal không có cách đóng rõ ràng

**✅ ĐÚNG**:
- ✅ CHỈ 1 nút X ở header
- ✅ Footer bắt buộc khi có form: [Hủy] [Lưu]
- ✅ ESC key đóng modal
- ✅ Click outside có confirm nếu có unsaved changes

**Styling**:
```css
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-subtle);
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.modal-close {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
}

.modal-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-subtle);
}
```

### 13.3 Behavior

**Keyboard & Focus**:
```javascript
// Focus vào title/first input khi mở
modal.addEventListener('open', () => {
  const firstFocusable = modal.querySelector('input, button');
  firstFocusable?.focus();
});

// ESC để đóng
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && modalOpen) {
    closeModal();
  }
});

// Tab trap trong modal
modal.addEventListener('keydown', (e) => {
  if (e.key === 'Tab') {
    trapFocus(e);
  }
});

// Trả focus về trigger khi đóng
function closeModal() {
  modal.close();
  triggerButton.focus();
}
```

**Body Scroll Lock**:
```javascript
function openModal() {
  document.body.style.overflow = 'hidden';
  modal.showModal();
}

function closeModal() {
  document.body.style.overflow = '';
  modal.close();
}
```

### 13.4 Alignment & Spacing

**Quy tắc nội dung**:
- Heading + ít nhất 1-2 fields nên visible trong viewport đầu
- Tránh khoảng trắng lớn khi content ít
- Nếu form dài, cho phép scroll body, footer sticky

```css
/* Modal với form dài */
.modal-body--scrollable {
  max-height: 60vh;
  overflow-y: auto;
}

.modal-footer {
  position: sticky;
  bottom: 0;
  background: var(--bg-elevated);
  border-top: 1px solid var(--border-subtle);
}
```

---

## 14. Document/PDF/Embed

**Quy tắc**:
- Container max-width = content width (không full viewport)
- Height: 60-80vh
- Tránh nested scroll (page scroll + iframe scroll)
- Preview + link mở cho document dài

```html
<div class="document-viewer">
  <div class="document-controls">
    <button>Download</button>
    <button>Print</button>
    <button>Fullscreen</button>
  </div>
  <iframe 
    src="document.pdf" 
    width="100%" 
    height="600px"
    style="border: 1px solid var(--border-subtle); border-radius: var(--radius-lg)">
  </iframe>
</div>
```

---

## 15. Loading States

### 15.1 Spinner

```css
.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Sizes */
.spinner--sm { width: 16px; height: 16px; border-width: 2px; }
.spinner--md { width: 24px; height: 24px; border-width: 3px; }
.spinner--lg { width: 40px; height: 40px; border-width: 4px; }
```

**Usage**:
- Small (16px): Inline trong button
- Medium (24px): Card loading
- Large (40-48px): Page loading

### 15.2 Skeleton Screen

**Quy tắc**:
- Shape giống component thật
- Neutral color gradient (#e5e7eb → #f3f4f6)
- Shimmer animation 1.5-2s
- Số lượng = số items dự kiến

```css
.skeleton {
  background: linear-gradient(
    90deg,
    #e5e7eb 0%,
    #f3f4f6 50%,
    #e5e7eb 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-md);
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.skeleton-text {
  height: 16px;
  margin: 8px 0;
}

.skeleton-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.skeleton-card {
  height: 200px;
}
```

### 15.3 Progress Bar

**Linear Progress** (top of page):
```css
.progress-linear {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--color-primary);
  transform-origin: left;
  animation: progress-indeterminate 2s infinite;
  z-index: 9999;
}

@keyframes progress-indeterminate {
  0% { transform: scaleX(0) translateX(0); }
  50% { transform: scaleX(0.3) translateX(100%); }
  100% { transform: scaleX(0) translateX(200%); }
}
```

**Circular Progress** (center of modal):
```css
.progress-circular {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
```

**Determinate Progress** (với phần trăm):
```html
<div class="progress-bar">
  <div class="progress-fill" style="width: 60%"></div>
  <span class="progress-label">60%</span>
</div>
```

---

## 16. Toast, Notification & Alert

### 16.1 Toast

**Position & Styling**:
```css
.toast {
  position: fixed;
  top: 16px;
  right: 16px;
  min-width: 320px;
  max-width: 480px;
  padding: 12px 16px;
  background: var(--bg-elevated);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 10000;
  display: flex;
  align-items: center;
  gap: 12px;
  animation: toast-enter 250ms var(--ease-out);
}

@keyframes toast-enter {
  from {
    opacity: 0;
    transform: translateY(-16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Types */
.toast--success { border-left: 4px solid var(--color-success); }
.toast--error { border-left: 4px solid var(--color-danger); }
.toast--warning { border-left: 4px solid var(--color-warning); }
.toast--info { border-left: 4px solid var(--color-primary); }
```

**Auto-dismiss Times**:
- Success: 3-4s
- Info/Warning: 5-7s
- Error: manual hoặc ~10s (để user đọc kỹ)

**Mobile Responsive**:
```css
@media (max-width: 767px) {
  .toast {
    top: auto;
    bottom: 16px;
    left: 16px;
    right: 16px;
    max-width: none;
  }
}
```

### 16.2 Alert Banner

**In-page contextual alerts**:
```css
.alert {
  padding: 12px 16px;
  border-radius: var(--radius-md);
  border-left: 4px solid;
  display: flex;
  align-items: start;
  gap: 12px;
}

.alert--info {
  background: rgba(59, 130, 246, 0.1);
  border-color: var(--color-primary);
  color: #1e40af;
}

.alert--success {
  background: rgba(34, 197, 94, 0.1);
  border-color: var(--color-success);
  color: #166534;
}

.alert--warning {
  background: rgba(249, 171, 0, 0.1);
  border-color: var(--color-warning);
  color: #92400e;
}

.alert--error {
  background: rgba(239, 68, 68, 0.1);
  border-color: var(--color-danger);
  color: #991b1b;
}
```

### 16.3 Notification Panel

**Dropdown notification center**:
```css
.notification-panel {
  width: 360px;
  max-height: 480px;
  background: var(--bg-elevated);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.notification-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notification-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  gap: 12px;
  cursor: pointer;
}

.notification-item:hover {
  background: var(--bg-hover);
}

.notification-item--unread {
  background: rgba(59, 130, 246, 0.05);
}

.notification-item--unread::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary);
  flex-shrink: 0;
  margin-top: 8px;
}
```

**Badge Count**:
```css
.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  background: var(--color-danger);
  color: white;
  font-size: 11px;
  font-weight: 600;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

---

## 17. Empty & Error States

### 17.1 Empty State

**Anatomy**:
```html
<div class="empty-state">
  <div class="empty-icon">
    <icon>Inbox</icon>
  </div>
  <h3>No messages yet</h3>
  <p>When someone sends you a message, it will appear here.</p>
  <button class="button-primary">Compose Message</button>
</div>
```

**Styling**:
```css
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 64px 24px;
  max-width: 400px;
  margin: 0 auto;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 24px;
  color: var(--text-muted);
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.empty-state p {
  color: var(--text-muted);
  margin-bottom: 24px;
}
```

**Spacing**:
```
Icon (64-120px)
↓ 16-24px
Heading
↓ 8px
Description
↓ 24px
CTA Button
```

### 17.2 Error State

**Types**:
1. **API Failed**: Retry button
2. **Network Error**: Offline indicator
3. **403 Forbidden**: Contact admin CTA
4. **404 Not Found**: Go home link
5. **500 Server Error**: Status page link

```html
<div class="error-state">
  <div class="error-icon">
    <icon>AlertTriangle</icon>
  </div>
  <h2>Something went wrong</h2>
  <p>We couldn't load this page. Please try again.</p>
  <div class="error-code">Error Code: 500</div>
  <div class="error-actions">
    <button class="button-primary" onclick="location.reload()">
      Try Again
    </button>
    <button class="button-secondary" onclick="history.back()">
      Go Back
    </button>
  </div>
</div>
```

**Styling**:
```css
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 80px 24px;
  max-width: 500px;
  margin: 0 auto;
}

.error-icon {
  width: 64px;
  height: 64px;
  color: var(--color-danger);
  margin-bottom: 24px;
}

.error-code {
  font-size: 13px;
  color: var(--text-muted);
  font-family: var(--font-mono);
  margin: 16px 0 24px;
}

.error-actions {
  display: flex;
  gap: 12px;
}
```

---

## 18. Navigation Patterns

### 18.1 Breadcrumb

```html
<nav class="breadcrumb" aria-label="Breadcrumb">
  <a href="/">Home</a>
  <span class="breadcrumb-separator">/</span>
  <a href="/products">Products</a>
  <span class="breadcrumb-separator">/</span>
  <span class="breadcrumb-current">Product Name</span>
</nav>
```

**Styling**:
```css
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  padding: 12px 0;
}

.breadcrumb a {
  color: var(--text-muted);
  text-decoration: none;
}

.breadcrumb a:hover {
  color: var(--text-primary);
  text-decoration: underline;
}

.breadcrumb-separator {
  color: var(--text-disabled);
}

.breadcrumb-current {
  color: var(--text-primary);
  font-weight: 500;
}
```

**Mobile Pattern**:
```html
<!-- Show: First + ... + Current -->
<nav class="breadcrumb">
  <a href="/">Home</a>
  <span>/</span>
  <span>...</span>
  <span>/</span>
  <span class="breadcrumb-current">Current Page</span>
</nav>
```

### 18.2 Sidebar Navigation

**Desktop**:
```css
.sidebar {
  width: 280px;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  background: var(--bg-elevated);
  border-right: 1px solid var(--border-subtle);
  overflow-y: auto;
  padding: 16px;
}

.sidebar--collapsed {
  width: 64px;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 40px;
  padding: 0 12px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.sidebar-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.sidebar-item--active {
  background: var(--color-primary);
  color: white;
  font-weight: 500;
}

.sidebar-item--active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--color-primary);
}
```

**Mobile Drawer**:
```css
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform var(--transition-slow);
    z-index: 1000;
  }
  
  .sidebar--open {
    transform: translateX(0);
  }
  
  .sidebar-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 999;
  }
}
```

### 18.3 Drawer

```css
.drawer {
  position: fixed;
  top: 0;
  right: 0; /* or left: 0 */
  width: 300px;
  max-width: 85vw;
  height: 100vh;
  background: var(--bg-elevated);
  box-shadow: var(--shadow-xl);
  transform: translateX(100%);
  transition: transform var(--transition-slow) var(--ease-out);
  z-index: 1000;
  overflow-y: auto;
}

.drawer--open {
  transform: translateX(0);
}

.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity var(--transition-slow);
  z-index: 999;
  pointer-events: none;
}

.drawer-overlay--visible {
  opacity: 1;
  pointer-events: auto;
}
```

**Behavior**:
- Animation: 250-350ms
- Lock body scroll khi open
- Click overlay để đóng
- ESC key để đóng

### 18.4 Accordion & Collapsible

**Accordion** (chỉ 1 panel mở):
```html
<div class="accordion">
  <div class="accordion-item">
    <button class="accordion-header" aria-expanded="true">
      <span>Section 1</span>
      <icon class="accordion-icon">ChevronDown</icon>
    </button>
    <div class="accordion-content">
      <p>Content for section 1...</p>
    </div>
  </div>
  <!-- More items -->
</div>
```

**Collapsible** (nhiều panels mở):
```html
<div class="collapsible-group">
  <div class="collapsible-item">
    <button class="collapsible-header">
      <icon>ChevronRight</icon>
      <span>Item 1</span>
    </button>
    <div class="collapsible-content">
      <p>Content...</p>
    </div>
  </div>
</div>
```

**Styling**:
```css
.accordion-header {
  width: 100%;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border: none;
  background: transparent;
  text-align: left;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.accordion-header:hover {
  background: var(--bg-hover);
}

.accordion-icon {
  transition: transform var(--transition-fast);
}

.accordion-header[aria-expanded="true"] .accordion-icon {
  transform: rotate(180deg);
}

.accordion-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height var(--transition-slow) var(--ease-out);
}

.accordion-content--open {
  max-height: 1000px; /* Arbitrary large value */
  padding: 16px;
}
```

---

## 19. Contextual Help

### 19.1 Tooltip

**Anatomy**:
```html
<div class="tooltip-wrapper">
  <button>Hover me</button>
  <div class="tooltip" role="tooltip">
    Helpful information here
    <div class="tooltip-arrow"></div>
  </div>
</div>
```

**Styling**:
```css
.tooltip {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 12px;
  background: var(--color-text-primary);
  color: white;
  font-size: 13px;
  border-radius: var(--radius-sm);
  max-width: 280px;
  white-space: normal;
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--transition-fast);
  z-index: 100;
}

.tooltip-wrapper:hover .tooltip {
  opacity: 1;
  transition-delay: 500ms; /* Delay before showing */
}

.tooltip-arrow {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid var(--color-text-primary);
}
```

**Auto-flip** (khi gần viewport edge):
```javascript
function positionTooltip(tooltip, trigger) {
  const rect = trigger.getBoundingClientRect();
  const tooltipRect = tooltip.getBoundingClientRect();
  
  // Check if overflows right
  if (rect.left + tooltipRect.width > window.innerWidth) {
    tooltip.style.left = 'auto';
    tooltip.style.right = '0';
  }
  
  // Check if overflows top
  if (rect.top - tooltipRect.height < 0) {
    tooltip.style.bottom = 'auto';
    tooltip.style.top = 'calc(100% + 8px)';
  }
}
```

### 19.2 Popover

**Larger, richer content than tooltip**:
```html
<div class="popover-wrapper">
  <button class="popover-trigger">More Info</button>
  <div class="popover" role="dialog">
    <div class="popover-header">
      <h4>Additional Information</h4>
      <button class="popover-close" aria-label="Close">×</button>
    </div>
    <div class="popover-content">
      <p>Rich content with lists, links, etc.</p>
      <ul>
        <li>Item 1</li>
        <li>Item 2</li>
      </ul>
      <a href="#">Learn more</a>
    </div>
  </div>
</div>
```

**Styling**:
```css
.popover {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  width: 320px;
  background: var(--bg-elevated);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border-subtle);
  opacity: 0;
  transform: translateY(-8px);
  pointer-events: none;
  transition: all var(--transition-base) var(--ease-out);
  z-index: 100;
}

.popover--open {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

.popover-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.popover-content {
  padding: 16px;
}
```

**Behavior**:
- Click trigger để mở/đóng
- ESC + click outside để đóng
- Tab trap, return focus khi đóng

---

## 20. Color System & Accessibility

### 20.1 Color Palette

```css
:root {
  /* Semantic Colors */
  --color-primary: #1a73e8;
  --color-primary-hover: #185abc;
  --color-primary-rgb: 26, 115, 232; /* For rgba() */
  
  --color-accent: #ff6d00;
  --color-success: #34a853;
  --color-warning: #f9ab00;
  --color-danger: #ea4335;
  
  /* Neutral Scale - NO PURE BLACK */
  --color-text-heading: #111827;    /* Headers, most prominent text */
  --color-text-main: #1f2933;       /* Body text */
  --color-text-muted: #6b7280;      /* Secondary text, labels */
  --color-text-disabled: #9ca3af;   /* Disabled text */
  
  --color-border-subtle: #e5e7eb;   /* Dividers, soft borders */
  --color-border-strong: #cbd5e1;   /* Inputs, strong borders */
  
  --color-bg: #ffffff;              /* Page background */
  --color-bg-subtle: #f9fafb;       /* Alternate sections */
  --color-bg-elevated: #ffffff;     /* Cards, modals */
  --color-bg-hover: #f3f4f6;        /* Hover states */
  
  /* Focus Ring */
  --focus-ring-color: #2563eb;
  --focus-ring-width: 2px;
  --focus-ring-offset: 2px;
}
```

### 20.2 Quy Tắc CHỐNG "ĐEN THUI"

#### ❌ **KHÔNG BAO GIỜ dùng `#000000`**

**Tại sao?**
- Pure black (#000000) tạo contrast quá harsh trên màn hình phát sáng
- Gây căng thẳng thị giác, mỏi mắt khi đọc lâu
- Không natural - trong thực tế không có vật gì "đen tuyền"

#### ✅ **Thay vào đó**:

| Use Case | Color Variable | Hex | When |
|----------|---------------|-----|------|
| Page titles, H1 | `--color-text-heading` | #111827 | Prominent headlines |
| Body text | `--color-text-main` | #1f2933 | Paragraphs, content |
| Labels, meta | `--color-text-muted` | #6b7280 | Secondary info |
| Placeholders | `--color-text-disabled` | #9ca3af | Inactive elements |

#### ✅ **Section numbers/icons**: 

**KHÔNG dùng đen** - Thay vào đó:
- Dùng `--color-primary` (primary action color)
- Hoặc màu xám trung tính `--color-text-muted`

```css
/* ❌ SAI */
.section-number {
  color: #000000; /* Hard, stark */
}

/* ✅ ĐÚNG */
.section-number {
  color: var(--color-primary); /* Branded, soft */
}
```

#### ✅ **Background sections**:

Dùng `--color-bg-subtle` để phân biệt sections:
```css
/* ❌ SAI - Text đen đặc trên nền trắng phẳng */
section {
  background: #ffffff;
  color: #000000;
}

/* ✅ ĐÚNG - Alternating subtle backgrounds */
section:nth-child(even) {
  background: var(--color-bg-subtle); /* #f9fafb */
}

section {
  color: var(--color-text-main); /* #1f2933 */
}
```

### 20.3 Text Roles

| Role | Color | Weight | Size | Usage |
|------|-------|--------|------|-------|
| Page Title | `--color-text-heading` | 600-700 | 24-32px | H1, main page header |
| Section Title | `--color-text-heading` | 600 | 18-20px | H2, section dividers |
| Body Text | `--color-text-main` | 400 | 16px | Paragraphs, content |
| Label/Meta | `--color-text-muted` | 400 | 13-14px | Form labels, timestamps |
| Disabled | `--color-text-disabled` | 400 | inherit | Inactive elements |

### 20.4 Focus & States

```css
/* Universal Focus Style */
:where(button, a, input, select, textarea):focus-visible {
  outline: var(--focus-ring-width) solid var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
}

/* Remove default browser focus */
:where(button, a, input, select, textarea):focus {
  outline: none;
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
- Normal text (<18px): ≥ **4.5:1** contrast ratio
- Large text (≥18px or ≥14px bold): ≥ **3:1**
- UI components & graphics: ≥ **3:1**

**Công cụ kiểm tra**:
- WebAIM Contrast Checker (https://webaim.org/resources/contrastchecker/)
- Chrome DevTools Accessibility Panel
- Stark Plugin (Figma/Sketch)

**Example kiểm tra**:
```css
/* Check: Text #1f2933 on background #ffffff */
/* Ratio: 16.1:1 ✅ PASS (> 4.5:1) */

/* Check: Text #6b7280 on background #f9fafb */
/* Ratio: 4.8:1 ✅ PASS (> 4.5:1) */

/* Check: Text #9ca3af on background #ffffff */
/* Ratio: 3.1:1 ❌ FAIL for normal text */
/* → Only use for disabled/placeholder */
```

### 20.6 States Differentiation

Mỗi state phải có **sự khác biệt RÕ RÀNG**:
- Thay đổi màu + weight
- Hoặc màu + underline
- Hoặc background + border
- **KHÔNG** chỉ thay đổi độ sáng rất nhẹ

```css
/* ❌ SAI - Khác biệt không rõ */
.link { color: #666; }
.link:hover { color: #555; } /* Chỉ đậm 1 chút */

/* ✅ ĐÚNG - Khác biệt rõ ràng */
.link { 
  color: var(--text-muted);
  text-decoration: none;
}
.link:hover { 
  color: var(--color-primary);
  text-decoration: underline;
}
```

### 20.7 Shadows & Elevation

Sử dụng shadows để tạo depth thay vì borders dày.

#### Elevation Scale

```css
:root {
  /* NO shadow */
  --shadow-none: none;
  
  /* Subtle - For cards, resting state */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  
  /* Default - For dropdowns, hover states */
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
              0 2px 4px -1px rgba(0, 0, 0, 0.06);
  
  /* Elevated - For modals, popovers */
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
              0 4px 6px -2px rgba(0, 0, 0, 0.05);
  
  /* Strong - For sticky elements, dropdowns */
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
              0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
```

#### Usage Guidelines

| Component | Shadow | When |
|-----------|--------|------|
| Card (default) | `--shadow-sm` | Resting state |
| Card (hover) | `--shadow-md` | Interactive cards |
| Button (hover) | `--shadow-sm` | Lift effect |
| Dropdown | `--shadow-md` | When open |
| Modal | `--shadow-lg` | Overlay trên page |
| Popover | `--shadow-lg` | Floating content |
| Sticky Header | `--shadow-xl` | When scrolled |
| Flat elements | `--shadow-none` | Buttons, inline text |

#### Quy Tắc

- ❌ KHÔNG dùng `box-shadow: 0 0 10px black` (hard shadows)
- ✅ Dùng subtle, soft shadows với low opacity (0.05-0.1)
- ✅ Multiple layered shadows cho realistic depth
- ✅ Transitions: `transition: box-shadow 150ms ease`

```css
/* Example: Card with hover */
.card {
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-base) var(--ease-out);
}

.card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
```

### 20.8 Border Radius Scale

Card-based design cần consistent border radius.

```css
:root {
  --radius-sm: 4px;   /* Badges, tags, small elements */
  --radius-md: 8px;   /* Buttons, inputs, controls */
  --radius-lg: 12px;  /* Cards, panels */
  --radius-xl: 16px;  /* Modals, large containers */
  --radius-full: 9999px; /* Pills, avatars, circular */
}
```

#### Usage

| Component | Radius | Value |
|-----------|--------|-------|
| Badge | `--radius-sm` | 4px |
| Button | `--radius-md` | 8px |
| Input | `--radius-md` | 8px |
| Card | `--radius-lg` | 12px |
| Modal | `--radius-xl` | 16px |
| Avatar | `--radius-full` | 9999px |
| Pill button | `--radius-full` | 9999px |

#### Quy Tắc

- Consistent trong toàn app
- KHÔNG mix 4px với 16px trong cùng 1 component group
- Nested elements: inner radius = outer radius - padding

```css
/* ✅ ĐÚNG - Nested radius calculation */
.card {
  border-radius: var(--radius-lg); /* 12px */
  padding: 16px;
}

.card-image {
  border-radius: calc(var(--radius-lg) - 4px); /* 8px */
}
```

### 20.9 Dark Mode Support

```css
:root {
  /* Light mode (default) */
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --bg-elevated: #ffffff;
  --text-primary: #1f2933;
  --text-secondary: #6b7280;
  --border-color: #e5e7eb;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #111827;
    --bg-secondary: #1f2937;
    --bg-elevated: #1f2937;
    --text-primary: #f9fafb;
    --text-secondary: #9ca3af;
    --border-color: #374151;
    
    /* Adjust shadows for dark mode */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
  }
}
```

#### Quy Tắc Dark Mode

1. **KHÔNG dùng pure white (#fff) trong dark mode** → Dùng #f9fafb
2. **KHÔNG dùng pure black (#000) trong dark mode** → Dùng #111827
3. Contrast vẫn phải đạt WCAG AA (≥ 4.5:1)
4. Shadows: subtle với increased opacity, không dùng black shadows
5. Images/logos: có thể cần invert hoặc alternative version

---

## 21. Micro-interactions & Animations

Modern Clean Minimalism sử dụng subtle animations để tăng trải nghiệm.

### 21.1 Transition Speeds

```css
:root {
  --transition-fast: 150ms;    /* Color changes, hover states */
  --transition-base: 250ms;    /* Dropdowns, tooltips */
  --transition-slow: 350ms;    /* Modals, drawers */
  --transition-slower: 500ms;  /* Page transitions, major shifts */
}
```

| Speed | Duration | Use Case |
|-------|----------|----------|
| Fast | 150ms | Hover states, color changes, focus |
| Base | 250ms | Dropdowns, tooltips, popovers |
| Slow | 350ms | Modals, drawers, accordions |
| Slower | 500ms | Page transitions, major layout shifts |

### 21.2 Easing Functions

```css
:root {
  /* Standard easing curves */
  --ease-out: cubic-bezier(0, 0, 0.2, 1);        /* Decelerating */
  --ease-in: cubic-bezier(0.4, 0, 1, 1);         /* Accelerating */
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);   /* Symmetric */
  
  /* Custom easing for specific effects */
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

**When to use**:
- **ease-out**: Enter animations (fade in, slide in) - bắt đầu nhanh, kết thúc chậm
- **ease-in**: Exit animations (fade out) - bắt đầu chậm, kết thúc nhanh
- **ease-in-out**: State changes, transforms - smooth cả 2 đầu

### 21.3 Common Patterns

#### Button Hover
```css
.button {
  transition: all var(--transition-fast) var(--ease-out);
}

.button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.button:active:not(:disabled) {
  transform: translateY(0);
  transition-duration: 50ms; /* Faster on click */
}
```

#### Card Hover
```css
.card {
  transition: box-shadow var(--transition-base) var(--ease-out);
}

.card:hover {
  box-shadow: var(--shadow-md);
}

/* Optional: Subtle lift */
.card--interactive {
  transition: all var(--transition-base) var(--ease-out);
}

.card--interactive:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
```

#### Modal Enter/Exit
```css
/* Modal backdrop */
.modal-overlay {
  animation: fade-in var(--transition-slow) var(--ease-out);
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Modal content */
.modal {
  animation: modal-enter var(--transition-slow) var(--ease-out);
}

@keyframes modal-enter {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Exit animation */
.modal--exiting {
  animation: modal-exit var(--transition-base) var(--ease-in);
}

@keyframes modal-exit {
  from {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
  to {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
}
```

#### Skeleton Shimmer
```css
.skeleton {
  background: linear-gradient(
    90deg,
    #e5e7eb 0%,
    #f3f4f6 50%,
    #e5e7eb 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
```

#### Slide Down/Up (Accordion)
```css
.accordion-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height var(--transition-slow) var(--ease-out);
}

.accordion-content--open {
  max-height: 1000px; /* Large arbitrary value */
}
```

### 21.4 Performance Rules

**✅ CHỈ animate**:
- `transform` (translateX/Y/Z, scale, rotate)
- `opacity`

**❌ TRÁNH animate**:
- `width`, `height` (causes reflow)
- `margin`, `padding` (causes reflow)
- `top`, `left`, `right`, `bottom` (causes repaint)

**✅ Optimize với `will-change`**:
```css
.element-with-complex-animation {
  will-change: transform, opacity;
}

/* Remove after animation */
.element-with-complex-animation:not(.animating) {
  will-change: auto;
}
```

**❌ KHÔNG overuse animations**:
- Subtle > Flashy
- Không animate mọi thứ
- Respect `prefers-reduced-motion`

```css
/* Respect accessibility preferences */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 22. Component States (Universal)

MỌI interactive element PHẢI có 5 states sau.

### 22.1 State Definition

| State | When | Visual Change | Behavior |
|-------|------|---------------|----------|
| **Default** | Resting state | Base colors, no effects | Idle, waiting for interaction |
| **Hover** | Mouse over | Lighter bg, subtle shadow | Indicates interactivity |
| **Active** | Click/press down | Darker bg, pressed effect | Provides click feedback |
| **Focus** | Keyboard focus | Focus ring (2px, primary) | Keyboard navigation aid |
| **Disabled** | Non-interactive | 50% opacity, no pointer | Cannot be interacted with |

### 22.2 Universal State Pattern

```css
.interactive-element {
  /* Default - Resting state */
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast) var(--ease-out);
  cursor: pointer;
}

/* Hover - Mouse over */
.interactive-element:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--border-strong);
  box-shadow: var(--shadow-sm);
}

/* Active - Pressed down */
.interactive-element:active:not(:disabled) {
  background: var(--bg-active);
  transform: scale(0.98);
  box-shadow: none;
}

/* Focus - Keyboard navigation */
.interactive-element:focus-visible {
  outline: var(--focus-ring-width) solid var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
}

/* Remove default browser focus */
.interactive-element:focus {
  outline: none;
}

/* Disabled - Cannot interact */
.interactive-element:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}
```

### 22.3 State Priority

**Cascading priority** (top = highest):
1. **Disabled** - overrides all other states
2. **Active** - during click/press
3. **Focus** - keyboard navigation
4. **Hover** - mouse over
5. **Default** - resting state

**CSS selector order**:
```css
.button { /* Default */ }
.button:hover:not(:disabled) { /* Hover */ }
.button:focus-visible { /* Focus */ }
.button:active:not(:disabled) { /* Active */ }
.button:disabled { /* Disabled */ }
```

### 22.4 Checklist

Đảm bảo mỗi interactive element có:
- [ ] Default state rõ ràng (base appearance)
- [ ] Hover có visual feedback (color/shadow change)
- [ ] Active có pressed effect (scale/transform)
- [ ] Focus ring visible (keyboard accessibility)
- [ ] Disabled không thể interact (opacity + cursor)
- [ ] Transitions smooth (150-250ms)
- [ ] States không conflict với nhau

---

## 23. Icon System

Modern Clean design có icon usage patterns cụ thể.

### 23.1 Icon Sizes

| Size Name | Dimension | Use Case | Example Context |
|-----------|-----------|----------|-----------------|
| xs | 12px | Inline text, badges | "New" badge icon |
| sm | 16px | Buttons, inputs | Input prefix icon |
| md | 20px | Navigation, cards | Sidebar menu icons |
| lg | 24px | Headings, features | Section headers |
| xl | 32px | Empty states | "No data" illustration |
| 2xl | 48px+ | Hero, large illustrations | Landing page graphics |

### 23.2 Icon + Text Spacing

```css
.icon-text {
  display: inline-flex;
  align-items: center;
  gap: 8px; /* Fixed gap - đừng thay đổi */
}

/* Button với icon */
.button-with-icon {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0 16px;
  height: 40px;
}

/* Icon leading (trước text) */
.icon-leading {
  order: -1;
}

/* Icon trailing (sau text) */
.icon-trailing {
  order: 1;
}
```

### 23.3 Icon Libraries (Recommended)

**Lucide Icons** (Preferred):
- Clean, minimal, consistent stroke width
- Modern design language
- Well-balanced proportions
- https://lucide.dev

**Heroicons**:
- Designed by Tailwind CSS creators
- Solid & Outline variants
- Modern, professional
- https://heroicons.com

**Feather Icons**:
- Lightweight, simple
- Consistent 24x24 grid
- https://feathericons.com

### 23.4 Icon Styling Rules

```css
:root {
  --icon-stroke-width: 1.5px; /* or 2px for bold */
}

.icon {
  width: 20px;
  height: 20px;
  stroke-width: var(--icon-stroke-width);
  color: currentColor; /* Inherit text color */
  flex-shrink: 0; /* Prevent squishing */
}

/* Icon in buttons */
.button .icon {
  width: 16px;
  height: 16px;
}

/* Icon in headings */
h2 .icon, h3 .icon {
  width: 24px;
  height: 24px;
  color: var(--color-primary);
}
```

#### Quy Tắc

- ✅ Stroke width: **1.5-2px** cho consistency
- ✅ Align **center** với text baseline
- ❌ KHÔNG mix icon styles (outlined + filled) trong cùng context
- ✅ Icon color **match text color** trong cùng context
- ✅ Icons phải **accessible** (có aria-label hoặc hidden nếu decorative)

**Accessibility**:
```html
<!-- Icon có ý nghĩa semantic -->
<button>
  <icon aria-label="Search">Search icon</icon>
  Search
</button>

<!-- Icon chỉ decorative (có text đi kèm) -->
<button>
  <icon aria-hidden="true">Search icon</icon>
  Search
</button>

<!-- Icon-only button (phải có label) -->
<button aria-label="Search">
  <icon>Search icon</icon>
</button>
```

---

## Checklist Tổng Hợp

### Layout & Grid
- [ ] Container max-width + center
- [ ] 12-column grid system
- [ ] Spacing theo 8pt grid
- [ ] Mọi element bám grid
- [ ] Responsive breakpoints: 768/1024/1200px

### Spacing
- [ ] Internal ≤ External
- [ ] Icon-text: 8px
- [ ] Cards gap: 16-24px
- [ ] Sections: 48-80px
- [ ] Padding/margin là bội số 8

### Typography
- [ ] Scale rõ ràng (48/32/24/16/14)
- [ ] Line-height ~1.5-1.6
- [ ] Vertical rhythm align grid
- [ ] Font: Inter/Geist/System fonts
- [ ] Letter-spacing cho headings lớn

### Colors & Shadows
- [ ] ❌ KHÔNG dùng #000000
- [ ] ✅ Dùng neutral scale (#1f2933, #6b7280)
- [ ] Section numbers: primary color
- [ ] Text roles rõ ràng (heading/body/muted/disabled)
- [ ] Contrast ≥ 4.5:1 (WCAG AA)
- [ ] Shadows: subtle, layered (--shadow-sm/md/lg/xl)
- [ ] Border radius: consistent (4/8/12/16px)

### Components
- [ ] Button height 40-48px (≥44px mobile)
- [ ] Input height match buttons
- [ ] Focus states visible (2px ring, primary color)
- [ ] Loading states rõ ràng (spinner/skeleton/progress)
- [ ] Empty/error states complete
- [ ] Icons: consistent size & stroke width

### Layout 2 Cột
- [ ] Cùng cột grid start
- [ ] Width đồng đều (6/12 - 6/12)
- [ ] Padding consistent
- [ ] Header align với cards

### Modal & Dialog ⭐
- [ ] ❌ KHÔNG có 2 nút X
- [ ] ✅ CHỈ 1 nút X ở header
- [ ] ❌ KHÔNG có nút X trên overlay
- [ ] ✅ Footer bắt buộc khi có form: [Hủy] [Lưu]
- [ ] ESC key đóng modal
- [ ] Click outside có confirm nếu unsaved changes
- [ ] Focus trap trong modal
- [ ] Return focus về trigger khi đóng
- [ ] Body scroll locked khi modal mở
- [ ] Max-height 80-90vh, body scroll nếu dài

### States & Interactions
- [ ] All interactive elements có 5 states: default/hover/active/focus/disabled
- [ ] Transitions smooth (150-250ms)
- [ ] Respect prefers-reduced-motion
- [ ] Animations subtle, not flashy

### Accessibility
- [ ] Focus visible (WCAG 2.1 AA)
- [ ] Keyboard navigation (Tab, Enter, ESC, Arrows)
- [ ] ARIA labels cho icons và complex widgets
- [ ] Contrast đạt chuẩn (≥4.5:1 normal text, ≥3:1 large text)
- [ ] Screen reader friendly (semantic HTML)
- [ ] Touch targets ≥ 44px (mobile)

### Responsive
- [ ] Mobile-first CSS approach
- [ ] Breakpoints: 768px (tablet), 1024px (laptop), 1200px (desktop)
- [ ] 1 cột mobile, 2+ cột desktop
- [ ] Touch targets ≥ 44px height
- [ ] Font-size ≥ 16px trên inputs (tránh auto-zoom iOS)

---

## Best Practices Tổng Kết

### 1. **Consistency > Creativity**
Giữ patterns nhất quán quan trọng hơn sáng tạo. User cần predictability.

### 2. **8pt Grid Everything**
Mọi spacing phải là bội số 8 (8, 16, 24, 32, 40, 48, 64, 80).

### 3. **No Pure Black**
Dùng neutral scale cho text (#1f2933, #6b7280), không #000000.

### 4. **Subtle Shadows > Thick Borders**
Dùng soft shadows để tạo elevation thay vì borders dày.

### 5. **Focus States Required**
Bắt buộc cho accessibility - 2px ring, primary color, 2px offset.

### 6. **Mobile Touch Targets**
All interactive elements ≥ 44px height trên mobile.

### 7. **Loading Feedback Always**
Luôn có loading indicator (spinner/skeleton/progress).

### 8. **Error Handling Complete**
Empty states + error states đầy đủ, helpful messages.

### 9. **Semantic Colors Clear**
Primary/success/warning/danger phải rõ ràng và consistent.

### 10. **Animations: Less is More**
Subtle animations (150-250ms) > flashy effects. Respect prefers-reduced-motion.

---

## Quick Reference

### Spacing Scale
```
8px  → Tight (icon-text)
16px → Comfortable (between cards)
24px → Generous (section padding)
32px → Spacious (between groups)
48px → Large (section dividers)
64px → Extra large (hero padding)
80px → Huge (page sections)
```

### Component Heights
```
32px → Small buttons, badges
40px → Default buttons, inputs, tabs
48px → Large buttons, inputs
56px → Accordion headers, list items
```

### Border Radius
```
4px  → sm (badges, tags)
8px  → md (buttons, inputs)
12px → lg (cards)
16px → xl (modals)
9999px → full (pills, avatars)
```

### Shadows
```
--shadow-sm: Cards resting
--shadow-md: Dropdowns, hover states
--shadow-lg: Modals, popovers
--shadow-xl: Sticky headers, major elevation
```

### Transitions
```
150ms → Fast (hover, focus)
250ms → Base (dropdowns, tooltips)
350ms → Slow (modals, drawers)
500ms → Slower (page transitions)
```

---

**Version**: 2.0 (Complete Edition)  
**Last Updated**: December 2024  
**Design Philosophy**: Modern Clean Minimalism (Enterprise SaaS Style)  
**Inspired by**: Shadcn/UI, Geist Design, Linear, Stripe, Notion