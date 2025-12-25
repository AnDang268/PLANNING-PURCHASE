# Modal & Dialog - Code Review Checklist

Checklist chi tiết để review Modal/Dialog components trong code.

---

## ✅ **MANDATORY CHECKS - Phải Pass 100%**

### 1. Close Buttons Structure

**❌ CRITICAL VIOLATIONS:**

```html
<!-- ❌ SAI: 2 nút X -->
<div class="modal-overlay">
  <button class="close-btn">X</button>  <!-- ❌ Không được có -->
  <div class="modal">
    <div class="modal-header">
      <button class="close-btn">X</button>  <!-- ❌ Duplicate -->
    </div>
  </div>
</div>

<!-- ✅ ĐÚNG: Chỉ 1 nút X -->
<div class="modal-overlay">
  <!-- ✅ Không có nút X ở đây -->
  <div class="modal">
    <div class="modal-header">
      <h3>Title</h3>
      <button class="modal-close">×</button>  <!-- ✅ Chỉ ở đây -->
    </div>
  </div>
</div>
```

**Checklist:**
- [ ] ❌ Không có nút X trên `.modal-overlay`
- [ ] ✅ CHỈ có 1 nút X duy nhất ở `.modal-header`
- [ ] Nút X ở góc phải header
- [ ] Nút X có `aria-label="Close"` hoặc tương đương

---

### 2. Footer Requirements

**❌ VIOLATION: Thiếu Footer**

```html
<!-- ❌ SAI: Modal có form nhưng không có footer -->
<div class="modal">
  <div class="modal-header">...</div>
  <div class="modal-body">
    <form>
      <input type="text" />
      <!-- Form fields... -->
    </form>
  </div>
  <!-- ❌ THIẾU FOOTER -->
</div>

<!-- ✅ ĐÚNG: Footer bắt buộc khi có form -->
<div class="modal">
  <div class="modal-header">...</div>
  <div class="modal-body">
    <form>
      <input type="text" />
    </form>
  </div>
  <div class="modal-footer">
    <button class="button button--secondary">Hủy</button>
    <button class="button button--primary">Lưu</button>
  </div>
</div>
```

**Checklist:**
- [ ] Modal có form/input fields? → Footer BẮT BUỘC
- [ ] Footer có nút Cancel/Hủy (secondary)
- [ ] Footer có nút Save/Lưu/OK (primary)
- [ ] Buttons align phải
- [ ] Gap giữa buttons: 8-16px
- [ ] Border-top: 1px subtle

---

### 3. CSS Structure

```css
/* ✅ ĐÚNG: CSS Structure */

/* Overlay - KHÔNG CÓ NÚT X */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal-backdrop);
  padding: 16px;
}

/* Modal Container */
.modal {
  background: white;
  border-radius: 8px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

/* Header với NÚT X */
.modal-header {
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-close {
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #f9fafb;
}

/* Body */
.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

/* Footer - BẮT BUỘC khi có form */
.modal-footer {
  padding: 24px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 16px;
  justify-content: flex-end;
}
```

**Checklist:**
- [ ] `max-height: 80-90vh`
- [ ] `overflow-y: auto` ở `.modal-body`
- [ ] Footer có `border-top`
- [ ] Footer buttons `justify-content: flex-end`
- [ ] Z-index đúng thứ tự

---

### 4. JavaScript Behavior

```javascript
// ✅ ĐÚNG: Complete Modal Behavior

let hasUnsavedChanges = false;

// Track changes
function trackChanges() {
  const inputs = document.querySelectorAll('.modal input, .modal textarea');
  inputs.forEach(input => {
    input.addEventListener('input', () => {
      hasUnsavedChanges = true;
    });
  });
}

// Close Modal Function
function closeModal() {
  if (hasUnsavedChanges) {
    const confirmed = confirm('Có thay đổi chưa lưu. Bạn có chắc muốn đóng?');
    if (!confirmed) return;
  }
  
  document.getElementById('modal').style.display = 'none';
  document.body.style.overflow = 'auto'; // Unlock scroll
  
  // Return focus
  const trigger = document.querySelector('[data-modal-trigger]');
  if (trigger) trigger.focus();
  
  hasUnsavedChanges = false;
}

// X Button Click
document.querySelector('.modal-close').addEventListener('click', closeModal);

// Cancel Button Click
document.querySelector('.button--secondary').addEventListener('click', closeModal);

// ESC Key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && modalIsOpen) {
    closeModal();
  }
});

// Click Outside
document.querySelector('.modal-overlay').addEventListener('click', (e) => {
  if (e.target === e.currentTarget) {
    closeModal();
  }
});

// Save Button
document.querySelector('.button--primary').addEventListener('click', () => {
  // Validate
  if (!validateForm()) return;
  
  // Save
  saveData();
  
  // Close
  hasUnsavedChanges = false;
  closeModal();
  
  // Show success
  showToast('Lưu thành công!');
});

// Focus Management
function openModal() {
  document.getElementById('modal').style.display = 'flex';
  document.body.style.overflow = 'hidden'; // Lock scroll
  
  // Focus first input or title
  const firstInput = document.querySelector('.modal-body input');
  if (firstInput) {
    setTimeout(() => firstInput.focus(), 100);
  }
  
  // Setup change tracking
  trackChanges();
}
```

**Checklist:**
- [ ] Close modal: Nút X + Hủy + ESC + Click outside
- [ ] Có warning khi close với unsaved changes
- [ ] Body scroll locked khi modal mở
- [ ] Focus vào first input khi mở
- [ ] Return focus về trigger khi đóng
- [ ] Save button: validate → save → close → feedback

---

## 📋 **Review Process**

### Step 1: Visual Check
```bash
✓ Mở modal trong browser
✓ Đếm số nút X → phải = 1
✓ Kiểm tra có footer không (nếu có form)
✓ Click tất cả close methods
✓ Test với unsaved changes
```

### Step 2: Code Check
```bash
✓ Search ".modal-overlay" → không có nút close
✓ Search ".modal-header" → có 1 nút close duy nhất  
✓ Search ".modal-footer" → có khi có form
✓ Check onclick handlers
✓ Check ESC key handler
```

### Step 3: Behavior Check
```bash
✓ Click X → đóng (có confirm nếu có changes)
✓ Click Hủy → đóng
✓ Click Lưu → save → đóng → toast
✓ Press ESC → đóng
✓ Click outside → đóng (có confirm)
✓ Tab key → focus trap trong modal
```

---

## 🚨 **Critical Issues Priority**

### P0 - Block PR (Phải fix ngay)
- ❌ Có 2 nút X
- ❌ Modal có form nhưng không có footer
- ❌ Không có nút Lưu/Hủy
- ❌ Body scroll không lock

### P1 - Must Fix Before Merge
- ⚠️ Click outside không có confirm
- ⚠️ ESC key không work
- ⚠️ Focus không trap trong modal
- ⚠️ Không return focus về trigger

### P2 - Should Fix
- 💡 Animation không smooth
- 💡 Mobile responsive chưa tốt
- 💡 Loading state chưa có

---

## ✅ **Approval Criteria**

Modal được approve khi:

```markdown
✅ Structure
- [x] CHỈ 1 nút X ở header
- [x] KHÔNG có nút X trên overlay
- [x] Footer đầy đủ: [Hủy] [Lưu]

✅ Behavior  
- [x] X button works
- [x] Hủy button works
- [x] Lưu button works
- [x] ESC key works
- [x] Click outside works (với confirm)

✅ UX
- [x] Body scroll locked
- [x] Focus management correct
- [x] Unsaved changes warning
- [x] Success feedback after save

✅ Code Quality
- [x] CSS structure clean
- [x] JavaScript có error handling
- [x] Accessible (ARIA labels)
- [x] Responsive mobile
```

---

## 📖 **Examples**

### ✅ Perfect Modal Example

```html
<div class="modal-overlay" id="editModal" onclick="handleOverlayClick(event)">
  <div class="modal" onclick="event.stopPropagation()">
    
    <!-- Header với 1 nút X duy nhất -->
    <div class="modal-header">
      <h3 class="modal-title">Chỉnh Sửa Hồ Sơ</h3>
      <button 
        class="modal-close" 
        onclick="closeModal()" 
        aria-label="Đóng"
      >
        ×
      </button>
    </div>

    <!-- Body -->
    <div class="modal-body">
      <form id="editForm">
        <div class="field">
          <label>Họ và tên *</label>
          <input 
            type="text" 
            class="input" 
            required
            oninput="markAsChanged()"
          >
        </div>
        <!-- More fields... -->
      </form>
    </div>

    <!-- Footer bắt buộc -->
    <div class="modal-footer">
      <button 
        type="button"
        class="button button--secondary" 
        onclick="closeModal()"
      >
        Hủy
      </button>
      <button 
        type="submit"
        class="button button--primary" 
        onclick="handleSave(event)"
      >
        Lưu thay đổi
      </button>
    </div>

  </div>
</div>
```

---

## 🎯 **Quick Test Script**

Copy vào Console để test nhanh:

```javascript
// Test Modal Compliance
function testModal() {
  console.log('🔍 Testing Modal Compliance...\n');
  
  const modal = document.querySelector('.modal');
  const overlay = document.querySelector('.modal-overlay');
  const header = document.querySelector('.modal-header');
  const footer = document.querySelector('.modal-footer');
  const body = document.querySelector('.modal-body');
  
  let errors = [];
  
  // Test 1: Count X buttons
  const closeButtons = document.querySelectorAll('.modal-close, .close-btn, [aria-label*="Close"], [aria-label*="Đóng"]');
  if (closeButtons.length !== 1) {
    errors.push(`❌ CRITICAL: Found ${closeButtons.length} close buttons (should be 1)`);
  } else {
    console.log('✅ Only 1 close button');
  }
  
  // Test 2: X button position
  const xInOverlay = overlay?.querySelector('.modal-close, .close-btn');
  if (xInOverlay && !header?.contains(xInOverlay)) {
    errors.push('❌ CRITICAL: Close button on overlay (should be in header)');
  } else {
    console.log('✅ Close button in correct position');
  }
  
  // Test 3: Footer exists when form exists
  const hasForm = body?.querySelector('form, input, textarea, select');
  if (hasForm && !footer) {
    errors.push('❌ CRITICAL: Form exists but no footer');
  } else if (hasForm && footer) {
    console.log('✅ Footer exists with form');
  }
  
  // Test 4: Footer buttons
  if (footer) {
    const cancelBtn = footer.querySelector('.button--secondary');
    const saveBtn = footer.querySelector('.button--primary');
    if (!cancelBtn) errors.push('⚠️ Missing Cancel button in footer');
    if (!saveBtn) errors.push('⚠️ Missing Save button in footer');
    if (cancelBtn && saveBtn) console.log('✅ Footer has both buttons');
  }
  
  // Results
  console.log('\n═══════════════════════════════════');
  if (errors.length === 0) {
    console.log('✅ PASS: Modal tuân thủ quy định!');
  } else {
    console.log(`❌ FAIL: Found ${errors.length} issues:`);
    errors.forEach(err => console.log('  ' + err));
  }
  console.log('═══════════════════════════════════\n');
  
  return errors.length === 0;
}

// Run test
testModal();
```

---

**Version**: 1.0  
**Last Updated**: December 2024  
**Reference**: Quy Tắc Thiết Kế Layout Web Chuẩn - Section 13