# Quy định lập trình & Code Convention (v2.0)

> **Phiên bản cải tiến** - Áp dụng cho toàn bộ lập trình viên: FE/BE/Mobile/DevOps/Data

---

**QUY ĐỊNH LẬP TRÌNH & CODE CONVENTION**  
Phiên bản: **2.0** | Ngày hiệu lực: 25/12/2025  
Chủ sở hữu: CTO/Tech Lead | Phạm vi: Toàn bộ dự án phần mềm

---

## 📑 MỤC LỤC

1. [Mục tiêu & Nguyên tắc](#1-mục-tiêu--nguyên-tắc)
2. [Codebase & Cấu trúc](#2-codebase--cấu-trúc-dự-án)
3. [Git Workflow & PR](#3-git-workflow--pull-request)
4. [Code Convention](#4-code-convention)
5. [API Convention](#5-api-convention)
6. [Database Convention](#6-database-convention)
7. [Testing & Quality](#7-testing--quality-assurance)
8. [Security & Compliance](#8-security--compliance)
9. [Performance & Optimization](#9-performance--optimization) ⭐ MỚI
10. [Monitoring & Observability](#10-monitoring--observability) ⭐ MỚI
11. [Documentation](#11-documentation) ⭐ MỚI
12. [Mobile-Specific](#12-mobile-specific-guidelines) ⭐ MỚI
13. [Incident Response](#13-incident-response--rollback) ⭐ MỚI
14. [Code Review & DoD](#14-code-review--definition-of-done)
15. [Phụ lục](#phụ-lục)

---

## 1. Mục tiêu & Nguyên tắc

### 1.1. Mục tiêu
- Code dễ đọc, dễ bảo trì, dễ mở rộng
- Giảm technical debt và rủi ro vận hành
- Tăng tốc development nhưng đảm bảo chất lượng
- **Tự động hóa quality gate tối đa** ⭐

### 1.2. Nguyên tắc SOLID
- **Clarity over Cleverness**: Code phải đọc hiểu nhanh
- **DRY but not OVER**: Không lặp nhưng không over-engineer
- **One Change = One Purpose**: Một PR/commit = một mục tiêu
- **Fail Fast**: Lỗi phải phát hiện sớm nhất có thể
- **Security by Default**: Secure coding là bắt buộc, không phải optional

---

## 2. Codebase & Cấu trúc dự án

### 2.1. Chuẩn cấu trúc thư mục

```
project-root/
├── apps/                   # Ứng dụng chính (web, mobile, admin)
├── services/               # Microservices (API, worker, cron)
├── packages/               # Shared libs (UI kit, utils, types)
├── db/                     # Database (schema, migrations, seeds)
├── infra/                  # Infrastructure (docker, k8s, terraform)
├── docs/                   # Documentation
│   ├── adr/               # Architecture Decision Records ⭐
│   ├── api/               # API specs (OpenAPI/Swagger)
│   ├── runbooks/          # Operational guides ⭐
│   └── diagrams/          # System diagrams
├── scripts/                # Automation scripts
├── tests/                  # E2E và integration tests
│   ├── e2e/
│   ├── integration/
│   └── performance/       # Load testing ⭐
└── .github/workflows/      # CI/CD pipelines
```

### 2.2. File cấu hình

**Bắt buộc có:**
- `.env.example` với mô tả đầy đủ biến môi trường
- `README.md` với hướng dẫn setup và chạy project
- `.editorconfig` để thống nhất editor settings
- `.gitignore` chuẩn theo ngôn ngữ/framework

**Phân tầng môi trường:**
```
.env.development
.env.staging
.env.production
.env.test          # ⭐ Riêng cho testing
```

**Quy tắc:**
- ❌ KHÔNG commit file `.env` thật
- ✅ Dùng secret manager (AWS Secrets, Azure Key Vault, HashiCorp Vault)
- ✅ Config phải có giá trị mặc định hợp lý hoặc fail-fast với message rõ
- ✅ Validate config khi khởi động application

### 2.3. Dependency Management

**Quy tắc:**
- ✅ Bắt buộc commit lockfile (`package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`, `go.sum`)
- ✅ Pin exact versions cho production dependencies
- ✅ Chạy `npm audit` / `snyk test` trong CI
- ⚠️ Không nâng dependency hàng loạt; nâng theo đợt + test kỹ
- ⚠️ Không thêm library mới nếu có thể reuse hiện có

**Dependency Scanning (bắt buộc):**
```yaml
# CI/CD phải có bước:
- dependency-check (OWASP)
- license-check (compliance)
- outdated-check (security patches)
```

---

## 3. Git Workflow & Pull Request

### 3.1. Branch Convention

| Branch Type | Pattern | Ví dụ | Deploy to |
|------------|---------|-------|-----------|
| Main | `main` | `main` | Production |
| Develop | `develop` | `develop` | Staging |
| Feature | `feature/<ticket>-<desc>` | `feature/PROJ-123-user-auth` | Dev |
| Bugfix | `fix/<ticket>-<desc>` | `fix/PROJ-456-login-error` | Dev |
| Hotfix | `hotfix/<ticket>-<desc>` | `hotfix/PROJ-789-payment-bug` | Production |
| Release | `release/v<version>` | `release/v1.2.0` | Staging |

**Quy tắc:**
- Branch name: chữ thường, dấu gạch ngang, không ký tự đặc biệt
- Ticket ID bắt buộc (trừ chore nhỏ)
- Mô tả ngắn gọn, dưới 50 ký tự

### 3.2. Commit Message (Conventional Commits)

**Format:**
```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types:**
- `feat`: Tính năng mới
- `fix`: Sửa lỗi
- `refactor`: Refactor code (không thay đổi behavior)
- `perf`: Cải thiện performance
- `test`: Thêm/sửa test
- `docs`: Cập nhật documentation
- `style`: Format code (không ảnh hưởng logic)
- `chore`: Công việc maintenance (update deps, config)
- `ci`: Thay đổi CI/CD
- `build`: Thay đổi build system
- `revert`: Revert commit trước

**Ví dụ:**
```bash
feat(api): add pagination for order list

- Implement cursor-based pagination
- Add page size limit (max 100)
- Update API docs

Refs: PROJ-123
```

**Quy tắc:**
- Subject: dưới 72 ký tự, không dấu chấm cuối
- Body: giải thích WHY, không phải WHAT
- Footer: gắn ticket ID, breaking changes

### 3.3. Pull Request (PR)

**Template bắt buộc:**
```markdown
## 📝 Mô tả
[Tóm tắt thay đổi]

## 🎯 Ticket
- Jira: PROJ-123
- Related: PROJ-456

## 🔄 Loại thay đổi
- [ ] Feature mới
- [ ] Bug fix
- [ ] Refactor
- [ ] Performance improvement
- [ ] Breaking change

## ✅ Checklist
- [ ] Code đã pass lint/format
- [ ] Đã thêm/cập nhật tests
- [ ] Đã cập nhật docs (nếu cần)
- [ ] Đã test locally
- [ ] Không có secrets trong code
- [ ] Performance impact: ✅ OK / ⚠️ Check / ❌ Issue

## 🧪 Cách test
[Hướng dẫn test/verify]

## 📸 Screenshots (nếu có UI)
[Ảnh/video]

## ⚠️ Rủi ro & Side effects
[Ảnh hưởng đến module khác]
```

**Quy tắc PR:**
- ❌ Không merge trực tiếp vào `main` (trừ emergency hotfix)
- ✅ PR phải nhỏ: < 400 dòng (lý tưởng < 250 dòng)
- ✅ Tối thiểu 1 reviewer; module critical cần 2+ reviewers
- ✅ CI phải xanh (lint, test, build)
- ✅ Không "approve cho xong" - reviewer chịu trách nhiệm

**Branch Protection Rules:**
```yaml
main:
  - Require PR review (min 1)
  - Require status checks (CI)
  - No force push
  - No delete
  
develop:
  - Require PR review (min 1)
  - Require status checks
```

---

## 4. Code Convention

### 4.1. Nguyên tắc chung

**Giới hạn độ phức tạp:**
- Hàm/method: không quá 50 dòng (lý tưởng < 30)
- Cyclomatic Complexity: không quá 10 ⭐
- Nesting level: không quá 3 cấp
- Parameters: không quá 5 (nếu nhiều → dùng object/struct)

**Quy tắc SOLID áp dụng:**
- **S**ingle Responsibility: Một hàm làm một việc
- **O**pen/Closed: Mở rộng bằng abstraction, không sửa code cũ
- **L**iskov Substitution: Subclass phải thay thế được parent
- **I**nterface Segregation: Interface nhỏ, tập trung
- **D**ependency Inversion: Phụ thuộc vào abstraction

### 4.2. Naming Convention

**Biến & Hàm:**
```javascript
// JavaScript/TypeScript
const totalAmount = 1000;          // camelCase
function calculateDiscount() {}    // camelCase

// Python
total_amount = 1000                # snake_case
def calculate_discount():          # snake_case

// Java/Kotlin
int totalAmount = 1000;            // camelCase
public void calculateDiscount() {} // camelCase

// Go
var totalAmount = 1000             // camelCase
func CalculateDiscount() {}        // PascalCase (exported)
```

**Class & Type:**
```typescript
// PascalCase cho mọi ngôn ngữ
class OrderService {}
interface IPaymentGateway {}
type UserRole = 'admin' | 'user';
```

**Constants:**
```typescript
const MAX_RETRY_COUNT = 3;         // UPPER_SNAKE_CASE
const API_BASE_URL = 'https://...';
const DEFAULT_PAGE_SIZE = 20;
```

**Boolean:**
```typescript
// Bắt đầu bằng is/has/can/should/will
const isActive = true;
const hasPermission = false;
const canEdit = true;
const shouldRetry = false;
const willExpire = true;
```

**Private members:**
```typescript
class User {
  private _id: string;              // Prefix _ cho private
  #password: string;                // Hoặc dùng # (modern JS)
}
```

### 4.3. Code Organization

**File & Folder Naming:**
```
// Frontend (React/Vue)
components/
  ├── UserCard.tsx              # PascalCase cho component
  ├── order-list.tsx            # kebab-case cũng OK
  └── user-profile/
      ├── UserProfile.tsx
      └── user-profile.test.tsx

// Backend
services/
  ├── order-service.ts          # kebab-case
  ├── payment-gateway.ts
  └── user/
      ├── user.controller.ts
      ├── user.service.ts
      └── user.repository.ts    # Theo layer/responsibility
```

**Import Organization:**
```typescript
// 1. External dependencies
import React from 'react';
import { useQuery } from '@tanstack/react-query';

// 2. Internal packages/shared
import { Button } from '@/components/ui';
import { formatCurrency } from '@/lib/utils';

// 3. Local imports
import { UserCard } from './UserCard';
import styles from './styles.module.css';

// 4. Types
import type { User } from '@/types';
```

### 4.4. Format & Lint

**Bắt buộc sử dụng:**
- **JavaScript/TypeScript**: Prettier + ESLint
- **Python**: Black + isort + Ruff
- **Go**: gofmt + golangci-lint
- **Java**: Google Java Format
- **Kotlin**: ktlint

**Config chuẩn (Prettier):**
```json
{
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "bracketSpacing": true,
  "arrowParens": "always"
}
```

**Pre-commit Hook (Husky):**
```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

npm run lint-staged  # Auto format + lint changed files
npm run test:changed # Run tests for changed files
```

**CI Check:**
```yaml
- name: Lint & Format Check
  run: |
    npm run lint
    npm run format:check
  # Fail nếu không pass
```

### 4.5. Comments & Documentation

**Quy tắc comment code:**

**KHI NÀO CẦN COMMENT:**
- ✅ Giải thích WHY (lý do business logic phức tạp)
- ✅ Complex algorithm với độ phức tạp > O(n)
- ✅ Workaround/hack tạm thời (kèm link issue)
- ✅ Security considerations (tại sao validate cách này)
- ✅ Performance optimization (tại sao dùng cách này)
- ✅ Regex pattern phức tạp (giải thích pattern)
- ✅ Magic numbers quan trọng
- ❌ KHÔNG comment WHAT (code đã rõ ràng)

**CẤM TUYỆT ĐỐI:**
```typescript
// ❌ CẤM: Comment rõ ràng (code đã nói lên)
// Get user by id
const user = await getUser(id);

// ❌ CẤM: Comment sai với code
// Calculate total price
const discount = price * 0.1; // ❌ Đang tính discount chứ không phải total

// ❌ CẤM: Comment code ra (phải xóa)
// const oldLogic = something();
// return oldResult;

// ❌ CẤM: Comment có thông tin nhạy cảm
// Admin password: P@ssw0rd123
// API key: sk_live_xxxxx
```

**COMMENT TỐT:**
```typescript
// ✅ GOOD: Giải thích WHY business logic
// Discount chỉ áp dụng cho đơn > 1 triệu vì policy kinh doanh Q4/2025
if (orderAmount > 1_000_000) {
  discount = calculateDiscount(orderAmount);
}

// ✅ GOOD: Giải thích algorithm phức tạp
// Sử dụng Binary Search để tối ưu từ O(n) xuống O(log n)
// với dataset lớn (>10k records)
const index = binarySearch(sortedArray, target);

// ✅ GOOD: Giải thích regex
// Pattern: Vietnamese phone number (10 digits, start with 0)
// Valid: 0912345678, 0987654321
// Invalid: 912345678, 0912-345-678
const phoneRegex = /^0\d{9}$/;

// ✅ GOOD: Workaround với reference
// WORKAROUND: Fix cho bug trong library X v1.2.3
// TODO(team, 2025-02-01): Remove khi upgrade lên v1.3.0
// Issue: https://github.com/lib-x/issues/123
const tempFix = workaroundFunction();

// ✅ GOOD: Security consideration
// SECURITY: Không dùng raw SQL vì SQL injection risk
// Phải dùng parameterized query
const users = await db.query('SELECT * FROM users WHERE id = $1', [id]);

// ✅ GOOD: Performance note
// PERFORMANCE: Cache 5 phút vì API external này rate limit 100 req/min
// và data không thay đổi thường xuyên
const cachedData = await cache.get(key, 300);
```

**JSDoc/TSDoc cho function (BẮT BUỘC cho public API):**
```typescript
/**
 * Calculate discount based on user tier and order amount
 * 
 * Business Rules:
 * - VIP users: 15% discount
 * - Gold users: 10% discount
 * - Silver users: 5% discount
 * - Regular users: No discount
 * 
 * @param userId - User ID to check tier
 * @param orderAmount - Total order amount in VND (must be positive)
 * @returns Discount percentage (0-100)
 * @throws {ValidationError} If orderAmount < 0
 * @throws {UserNotFoundError} If user doesn't exist
 * 
 * @example
 * ```typescript
 * const discount = await calculateDiscount('user123', 1000000);
 * // Returns: 15 (for VIP tier)
 * ```
 * 
 * @see {@link https://docs.internal.com/discount-policy}
 */
async function calculateDiscount(
  userId: string, 
  orderAmount: number
): Promise<number> {
  if (orderAmount < 0) {
    throw new ValidationError('Order amount must be positive');
  }
  
  const user = await userService.findById(userId);
  if (!user) {
    throw new UserNotFoundError(`User ${userId} not found`);
  }
  
  // Mapping tier to discount percentage
  const discountMap: Record<UserTier, number> = {
    VIP: 15,
    GOLD: 10,
    SILVER: 5,
    REGULAR: 0,
  };
  
  return discountMap[user.tier];
}
```

**TODO Format (BẮT BUỘC):**
```typescript
// ❌ BAD: Không rõ ràng
// TODO: fix this
// TODO: optimize later

// ✅ GOOD: Đầy đủ thông tin
// TODO(username, 2025-01-15): Optimize query performance - PROJ-123
// Current: O(n²) with nested loop
// Target: O(n log n) using sort + binary search
// Impact: Slow with >1000 records

// TODO(team-backend, 2025-02-01): Migrate to new payment gateway - PROJ-456
// Reason: Current gateway deprecating API v1
// Action: Implement PaymentGatewayV2 adapter

// FIXME(username): Critical bug - app crashes when input is null
// Steps to reproduce: [link to bug report]
// Temporary workaround: Added null check at line 45
```

**Comment cho Complex Business Logic:**
```typescript
/**
 * Tính phí ship theo chính sách phức tạp của công ty
 */
function calculateShippingFee(
  weight: number,      // kg
  distance: number,    // km
  isExpress: boolean,
  userTier: UserTier
): number {
  // Base fee theo khoảng cách (policy updated 2025-12-01)
  // < 5km: 20k
  // 5-10km: 30k
  // > 10km: 30k + 5k/km
  let baseFee = 0;
  if (distance < 5) {
    baseFee = 20_000;
  } else if (distance <= 10) {
    baseFee = 30_000;
  } else {
    baseFee = 30_000 + (distance - 10) * 5_000;
  }
  
  // Phí theo trọng lượng (chỉ áp dụng > 5kg)
  // 5-10kg: +10k
  // >10kg: +10k + 5k/kg
  let weightFee = 0;
  if (weight > 5 && weight <= 10) {
    weightFee = 10_000;
  } else if (weight > 10) {
    weightFee = 10_000 + (weight - 10) * 5_000;
  }
  
  // Express fee: +50%
  const expressMultiplier = isExpress ? 1.5 : 1;
  
  // VIP free ship nếu đơn hàng đủ điều kiện
  // (được check ở nơi gọi function này)
  const tierDiscount = userTier === 'VIP' ? 0.5 : 1;
  
  const totalFee = (baseFee + weightFee) * expressMultiplier * tierDiscount;
  
  // Làm tròn đến 1000đ (policy)
  return Math.ceil(totalFee / 1000) * 1000;
}
```

---

## 5. API Convention

### 5.1. RESTful Design

**Resource Naming:**
```
✅ GOOD:
  GET    /api/v1/orders                  # List
  GET    /api/v1/orders/:id              # Detail
  POST   /api/v1/orders                  # Create
  PUT    /api/v1/orders/:id              # Full update
  PATCH  /api/v1/orders/:id              # Partial update
  DELETE /api/v1/orders/:id              # Delete
  
  GET    /api/v1/orders/:id/items        # Nested resource
  POST   /api/v1/orders/:id/cancel       # Action endpoint

❌ BAD:
  /api/getOrders                         # Verb in URL
  /api/order                             # Singular
  /api/v1/orders/delete/:id              # Verb in path
```

**Query Parameters:**
```
# Pagination
?page=1&pageSize=20
?cursor=eyJ...&limit=50                  # Cursor-based

# Filtering
?status=PAID&createdAfter=2025-01-01
?userId=123&orderType=ONLINE

# Sorting
?sort=-createdAt,amount                  # - for DESC
?orderBy=name&direction=asc

# Search
?q=laptop&fields=name,description

# Partial response (chỉ lấy field cần thiết)
?fields=id,name,price
```

### 5.2. HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | GET, PUT, PATCH thành công |
| 201 | Created | POST thành công |
| 204 | No Content | DELETE thành công |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Chưa đăng nhập |
| 403 | Forbidden | Không có quyền |
| 404 | Not Found | Resource không tồn tại |
| 409 | Conflict | Business rule conflict |
| 422 | Unprocessable Entity | Validation error (alternative) |
| 429 | Too Many Requests | Rate limit |
| 500 | Internal Server Error | Lỗi server |
| 502 | Bad Gateway | Downstream service error |
| 503 | Service Unavailable | Maintenance mode |

### 5.3. Response Format

**Success Response:**
```json
{
  "data": {
    "id": "order_123",
    "amount": 1000000,
    "status": "PAID"
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2025-12-25T10:30:00Z"
  }
}
```

**List Response với Pagination:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "total": 156,
    "totalPages": 8,
    "hasNext": true,
    "hasPrev": false
  },
  "meta": {
    "requestId": "req_abc123"
  }
}
```

**Error Response (chuẩn RFC 7807):**
```json
{
  "error": {
    "type": "VALIDATION_ERROR",
    "title": "Dữ liệu không hợp lệ",
    "status": 400,
    "detail": "Số điện thoại không đúng định dạng",
    "instance": "/api/v1/orders",
    "errors": [
      {
        "field": "phone",
        "code": "INVALID_FORMAT",
        "message": "Số điện thoại phải có 10 chữ số"
      }
    ],
    "meta": {
      "requestId": "req_abc123",
      "timestamp": "2025-12-25T10:30:00Z"
    }
  }
}
```

### 5.4. Versioning

```
Semantic Versioning: /api/v{major}

v1 → v2: Breaking changes
v1.1 → v1.2: Backward compatible additions

Header-based versioning (alternative):
Accept: application/vnd.api+json; version=2
```

### 5.5. Rate Limiting

**Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1640000000

# Khi hit limit:
HTTP 429 Too Many Requests
Retry-After: 3600
```

**Strategy:**
- Public endpoints: 100 req/hour/IP
- Authenticated: 1000 req/hour/user
- Critical endpoints (login, OTP): 5 req/minute/IP

---

## 6. Database Convention

### 6.1. Naming Convention

**Table Names:**
```sql
-- ✅ GOOD: snake_case, số nhiều
users
order_items
payment_transactions

-- ❌ BAD
User
orderItem
tblPayment
```

**Column Names:**
```sql
-- ✅ GOOD: snake_case, số ít
id, user_id, created_at, is_active

-- ❌ BAD
userId, CreatedAt, IsActive
```

**Indexes:**
```sql
-- Format: idx_{table}_{columns}
idx_users_email
idx_orders_user_id_created_at
idx_order_items_order_id

-- Unique: uniq_{table}_{columns}
uniq_users_email
uniq_products_sku
```

**Foreign Keys:**
```sql
-- Format: fk_{table}_{ref_table}
fk_orders_users
fk_order_items_orders
```

### 6.2. Standard Columns

**Bắt buộc có:**
```sql
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,              -- hoặc UUID
  
  -- Audit fields (bắt buộc)
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  
  -- Soft delete (nếu cần)
  deleted_at TIMESTAMP NULL,
  
  -- Who did what (optional)
  created_by BIGINT REFERENCES users(id),
  updated_by BIGINT REFERENCES users(id),
  
  -- Optimistic locking (nếu cần)
  version INT NOT NULL DEFAULT 1
);
```

### 6.3. Migration Convention

**File naming:**
```
{timestamp}_{action}_{table}.sql

V20251225120000__create_users_table.sql
V20251225120100__add_email_to_users.sql
V20251225120200__create_index_users_email.sql
```

**Migration rules:**
- ✅ Mỗi migration phải có UP và DOWN script
- ✅ Test trên staging trước khi apply production
- ✅ Large migration phải có progress tracking
- ⚠️ Không sửa migration đã deploy
- ⚠️ Breaking change phải có deprecation period

**Backward Compatible Migrations:**
```sql
-- ✅ GOOD: Thêm column với default
ALTER TABLE users ADD COLUMN phone VARCHAR(20) DEFAULT '';

-- ❌ BAD: Thêm column NOT NULL không có default
ALTER TABLE users ADD COLUMN phone VARCHAR(20) NOT NULL;

-- Strategy cho breaking change:
-- Step 1: Add new column (nullable)
-- Step 2: Backfill data
-- Step 3: Make NOT NULL
-- Step 4: Drop old column (sau khi app updated)
```

### 6.4. Indexing Strategy

**Khi nào cần index:**
- ✅ Foreign keys
- ✅ WHERE clause columns (thường xuyên filter)
- ✅ ORDER BY columns
- ✅ JOIN columns
- ✅ Unique constraints

**Composite Index:**
```sql
-- Index order matters!
-- Query: WHERE user_id = ? AND status = ? ORDER BY created_at
CREATE INDEX idx_orders_user_status_created 
  ON orders(user_id, status, created_at);

-- Left-most prefix: index này support:
-- - WHERE user_id = ?
-- - WHERE user_id = ? AND status = ?
-- - WHERE user_id = ? AND status = ? ORDER BY created_at
```

**Monitor & Optimize:**
```sql
-- PostgreSQL: Check unused indexes
SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;

-- Check slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC LIMIT 10;
```

---

## 7. Testing & Quality Assurance

### 7.1. Testing Pyramid

```
        /\
       /E2E\         5%  - End-to-end tests
      /------\
     /Integr.\      15%  - Integration tests
    /----------\
   /   Unit     \   80%  - Unit tests
  /--------------\
```

### 7.2. Coverage Requirements ⭐

| Layer | Min Coverage | Target |
|-------|-------------|--------|
| Business Logic | 80% | 90% |
| API Controllers | 70% | 80% |
| Utils/Helpers | 90% | 95% |
| UI Components | 60% | 70% |
| Overall | 70% | 80% |

**Quality Gate (CI phải pass):**
```yaml
coverage:
  threshold:
    global: 70%
    file: 60%
  diff: 
    enabled: true
    threshold: 80%  # New code phải > 80%
```

### 7.3. Unit Test Convention

**Naming:**
```typescript
// Pattern: should_{expected}_when_{condition}
describe('OrderService', () => {
  describe('calculateTotal', () => {
    it('should_return_discounted_total_when_user_is_vip', () => {
      // Test implementation
    });
    
    it('should_throw_error_when_amount_is_negative', () => {
      // Test implementation
    });
  });
});
```

**AAA Pattern (Arrange-Act-Assert):**
```typescript
it('should_create_order_with_valid_data', async () => {
  // Arrange
  const userId = 'user123';
  const items = [{ productId: 'p1', quantity: 2 }];
  const mockRepo = createMockRepository();
  const service = new OrderService(mockRepo);
  
  // Act
  const order = await service.createOrder(userId, items);
  
  // Assert
  expect(order.id).toBeDefined();
  expect(order.userId).toBe(userId);
  expect(order.items).toHaveLength(1);
});
```

**Test Isolation:**
```typescript
// ✅ GOOD: Độc lập, không phụ thuộc thứ tự
beforeEach(() => {
  // Setup fresh state cho mỗi test
  database.clear();
  cache.flush();
});

afterEach(() => {
  // Cleanup
  jest.clearAllMocks();
});

// ❌ BAD: Test phụ thuộc lẫn nhau
it('test1', () => { globalState.value = 10; });
it('test2', () => { expect(globalState.value).toBe(10); }); // ❌
```

### 7.4. Integration Test

**Scope:**
- API endpoints (request → response)
- Database transactions
- External service integration (với mock/stub)
- Authentication & authorization flow

**Example:**
```typescript
describe('POST /api/v1/orders', () => {
  it('should_create_order_and_return_201', async () => {
    // Arrange
    const token = await createTestUser('testuser');
    const orderData = { items: [...] };
    
    // Act
    const response = await request(app)
      .post('/api/v1/orders')
      .set('Authorization', `Bearer ${token}`)
      .send(orderData);
    
    // Assert
    expect(response.status).toBe(201);
    expect(response.body.data.id).toBeDefined();
    
    // Verify database
    const order = await db.orders.findById(response.body.data.id);
    expect(order).toBeDefined();
  });
});
```

### 7.5. E2E Test (Playwright/Cypress)

**Critical Flows (bắt buộc có):**
- User registration & login
- Checkout process (cart → payment → confirmation)
- Search & filter products
- Admin CRUD operations

**Best Practices:**
```typescript
// Page Object Pattern
class LoginPage {
  async login(email: string, password: string) {
    await this.page.fill('[data-testid="email"]', email);
    await this.page.fill('[data-testid="password"]', password);
    await this.page.click('[data-testid="login-btn"]');
  }
}

test('should_complete_checkout_flow', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.login('test@example.com', 'password');
  
  // Continue with checkout...
});
```

### 7.6. Performance Testing ⭐

**Load Testing (k6/Gatling):**
```javascript
// k6 example
export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% < 500ms
    http_req_failed: ['rate<0.01'],   // Error rate < 1%
  },
};
```

**Requirements:**
- p95 latency < 500ms (API)
- p99 latency < 1000ms
- Error rate < 0.1%
- Throughput: >= 1000 req/s (tùy service)

---

## 8. Security & Compliance

### 8.0. QUY ĐỊNH NGHIÊM CẤM HARDCODE ⚠️

**CẤM TUYỆT ĐỐI HARDCODE:**

```typescript
// ❌ CẤM: Hardcode credentials
const API_KEY = 'sk_live_abc123xyz';
const DB_PASSWORD = 'P@ssw0rd123';
const JWT_SECRET = 'my-super-secret';

// ❌ CẤM: Hardcode URLs production
const API_URL = 'https://api.production.com';
const PAYMENT_URL = 'https://payment.gateway.com';

// ❌ CẤM: Hardcode business logic critical
const VIP_DISCOUNT = 15; // Nếu thay đổi phải deploy lại
const MAX_WITHDRAWAL = 50_000_000;

// ❌ CẤM: Hardcode sensitive data
const ADMIN_USERS = ['admin@company.com', 'ceo@company.com'];
const BANK_ACCOUNT = '1234567890';

// ❌ CẤM: Hardcode IP/Port
const DATABASE_HOST = '192.168.1.100:5432';
const REDIS_HOST = '10.0.0.5:6379';

// ❌ CẤM: Hardcode encryption keys
const ENCRYPTION_KEY = Buffer.from('0123456789abcdef');
const IV = Buffer.from('fedcba9876543210');

// ❌ CẤM: Hardcode magic strings
if (status === 'PAID_COMPLETED_SUCCESS') { // Không rõ ràng, dễ typo
  // ...
}
```

**✅ ĐÚNG CÁCH:**

```typescript
// ✅ GOOD: Dùng environment variables
const API_KEY = process.env.API_KEY!;
const DB_PASSWORD = process.env.DB_PASSWORD!;
const JWT_SECRET = process.env.JWT_SECRET!;

// Validate config khi startup
if (!API_KEY || !JWT_SECRET) {
  throw new Error('Missing required environment variables');
}

// ✅ GOOD: Config file theo môi trường
// config/default.ts
export const config = {
  apiUrl: process.env.API_URL || 'http://localhost:3000',
  paymentUrl: process.env.PAYMENT_URL!,
  database: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '5432'),
    name: process.env.DB_NAME || 'mydb',
  },
};

// ✅ GOOD: Constants file với tên rõ ràng
// constants/discount.ts
export const DISCOUNT_RATES = {
  VIP: 15,
  GOLD: 10,
  SILVER: 5,
  REGULAR: 0,
} as const;

// ✅ GOOD: Enum cho status
export enum OrderStatus {
  PENDING = 'PENDING',
  PAID = 'PAID',
  SHIPPED = 'SHIPPED',
  DELIVERED = 'DELIVERED',
  CANCELLED = 'CANCELLED',
}

// Usage
if (order.status === OrderStatus.PAID) {
  // Type-safe, không typo
}

// ✅ GOOD: Feature flags (cho business logic có thể thay đổi)
const MAX_WITHDRAWAL = await featureFlags.getNumber('max_withdrawal', 50_000_000);
const isNewCheckoutEnabled = await featureFlags.getBoolean('new_checkout_flow', false);

// ✅ GOOD: Database-driven config (cho data thay đổi thường xuyên)
const vipDiscount = await configService.get('vip_discount_rate');
const shippingRates = await configService.getJson('shipping_rates');
```

**Kiểm tra trước khi commit:**
```bash
# Dùng git-secrets hoặc gitleaks
$ git secrets --scan
$ gitleaks detect --source . --verbose

# Tự động scan trong pre-commit hook
#!/bin/sh
# .git/hooks/pre-commit
gitleaks protect --staged --verbose
if [ $? -ne 0 ]; then
  echo "❌ Detected secrets in your changes!"
  exit 1
fi
```

---

### 8.1. Input Validation & Sanitization

**Validate ở mọi biên:**
```typescript
// Controller layer
@Post('/users')
@ValidateBody(CreateUserDto)
async createUser(@Body() data: CreateUserDto) {
  // data đã validated
}

// DTO with validation
class CreateUserDto {
  @IsEmail()
  email: string;
  
  @IsStrongPassword()
  @MinLength(8)
  password: string;
  
  @IsPhoneNumber('VN')
  phone: string;
}

// Domain layer validation
class User {
  setEmail(email: string) {
    if (!this.isValidEmail(email)) {
      throw new ValidationError('Invalid email');
    }
    this.email = email;
  }
}
```

### 8.2. Authentication & Authorization

**JWT Best Practices:**
```typescript
// ✅ GOOD
const token = jwt.sign(
  { userId: user.id, role: user.role },
  process.env.JWT_SECRET!,
  { 
    expiresIn: '15m',              // Short-lived
    issuer: 'myapp.com',
    audience: 'myapp.com',
  }
);

// Refresh token (long-lived, stored in httpOnly cookie)
const refreshToken = jwt.sign(
  { userId: user.id, tokenVersion: user.tokenVersion },
  process.env.REFRESH_SECRET!,
  { expiresIn: '7d' }
);

// ❌ BAD
const token = jwt.sign({ ...user }, 'hardcoded-secret'); // ❌
```

**Authorization:**
```typescript
// Role-based
@Roles('admin', 'manager')
@Get('/admin/users')
async getUsers() { }

// Permission-based (better)
@RequirePermission('users:read')
@Get('/users/:id')
async getUser(@Param('id') id: string) { }

// Resource-based (best)
@Get('/orders/:id')
async getOrder(@Param('id') id: string, @CurrentUser() user: User) {
  const order = await this.orderService.findById(id);
  if (order.userId !== user.id && !user.hasRole('admin')) {
    throw new ForbiddenException();
  }
  return order;
}
```

### 8.3. Data Protection ⭐

**Sensitive Data Handling:**
```typescript
// ✅ GOOD: Hash passwords
import bcrypt from 'bcrypt';
const hashedPassword = await bcrypt.hash(password, 12);

// ✅ GOOD: Encrypt PII
import { encrypt, decrypt } from './crypto';
const encryptedPhone = encrypt(user.phone);

// ✅ GOOD: Mask in logs
logger.info('User logged in', { 
  userId: user.id,
  email: maskEmail(user.email),  // t***@example.com
});

// ❌ BAD: Plaintext sensitive data
logger.info('User data', { user }); // ❌ Might contain password/token
```

**GDPR/PDPA Compliance:**
```typescript
// Right to be forgotten
async deleteUserData(userId: string) {
  await this.db.transaction(async (trx) => {
    // Anonymize instead of hard delete
    await trx.users.update(userId, {
      email: `deleted_${userId}@example.com`,
      phone: null,
      name: '[DELETED]',
      deletedAt: new Date(),
    });
    
    // Delete non-essential data
    await trx.userPreferences.delete({ userId });
    await trx.userSessions.delete({ userId });
  });
}

// Data retention policy
@Cron('0 0 * * *')  // Daily
async cleanupOldData() {
  const retentionDays = 90;
  await this.db.logs.deleteOlderThan(retentionDays);
  await this.db.sessions.deleteExpired();
}
```

### 8.4. Security Checklist

**Bắt buộc:**
- [ ] SQL Injection: Dùng parameterized queries/ORM
- [ ] XSS: Sanitize input, CSP headers
- [ ] CSRF: CSRF token cho state-changing operations
- [ ] Rate Limiting: Áp dụng cho login, OTP, search
- [ ] HTTPS: Enforce HTTPS, HSTS header
- [ ] CORS: Whitelist allowed origins
- [ ] Security Headers: Helmet.js / equivalent
  ```
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  X-XSS-Protection: 1; mode=block
  Strict-Transport-Security: max-age=31536000
  Content-Security-Policy: default-src 'self'
  ```
- [ ] Secrets: Không commit secrets, dùng secret manager
- [ ] Dependencies: Scan vulnerabilities (npm audit, Snyk)
- [ ] Error Messages: Không expose stack trace ở production

---

## 9. Performance & Optimization ⭐

### 9.1. Database Optimization

**Query Optimization:**
```sql
-- ❌ BAD: N+1 Query
SELECT * FROM orders;
-- Then in loop:
SELECT * FROM order_items WHERE order_id = ?;

-- ✅ GOOD: JOIN or eager loading
SELECT o.*, oi.*
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id;

-- ✅ GOOD: Batch query
SELECT * FROM order_items WHERE order_id IN (?, ?, ?);
```

**Pagination:**
```sql
-- ❌ BAD: OFFSET (slow cho large offset)
SELECT * FROM orders OFFSET 10000 LIMIT 20;

-- ✅ GOOD: Cursor-based (keyset pagination)
SELECT * FROM orders 
WHERE created_at < '2025-01-01' AND id < 10000
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

**Connection Pooling:**
```typescript
// ✅ GOOD
const pool = new Pool({
  host: 'localhost',
  database: 'mydb',
  max: 20,                    // Max connections
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// ❌ BAD: Tạo connection mới mỗi request
```

### 9.2. Caching Strategy

**Multi-layer Caching:**
```
┌─────────────┐
│   Browser   │ (Cache-Control, ETag)
└─────────────┘
       ↓
┌─────────────┐
│     CDN     │ (Static assets)
└─────────────┘
       ↓
┌─────────────┐
│   API GW    │ (Response cache)
└─────────────┘
       ↓
┌─────────────┐
│ Application │ (Redis/Memcached)
└─────────────┘
       ↓
┌─────────────┐
│  Database   │ (Query cache)
└─────────────┘
```

**Implementation:**
```typescript
// Cache-aside pattern
async getUser(id: string): Promise<User> {
  // 1. Try cache first
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);
  
  // 2. Query DB
  const user = await db.users.findById(id);
  if (!user) throw new NotFoundException();
  
  // 3. Set cache (with TTL)
  await redis.setex(`user:${id}`, 3600, JSON.stringify(user));
  
  return user;
}

// Cache invalidation
async updateUser(id: string, data: UpdateUserDto) {
  const user = await db.users.update(id, data);
  
  // Invalidate cache
  await redis.del(`user:${id}`);
  
  return user;
}
```

**Cache Headers:**
```typescript
// Static assets
res.set('Cache-Control', 'public, max-age=31536000, immutable');

// Dynamic content
res.set('Cache-Control', 'private, max-age=300, must-revalidate');

// No cache
res.set('Cache-Control', 'no-store, no-cache, must-revalidate');
```

### 9.3. API Performance

**Response Time Targets:**
| Endpoint | p50 | p95 | p99 |
|----------|-----|-----|-----|
| GET simple | < 50ms | < 100ms | < 200ms |
| GET complex | < 200ms | < 500ms | < 1s |
| POST/PUT | < 300ms | < 1s | < 2s |
| Search | < 500ms | < 1s | < 2s |

**Optimization Techniques:**
```typescript
// 1. Parallel execution
const [user, orders, preferences] = await Promise.all([
  db.users.findById(userId),
  db.orders.findByUserId(userId),
  db.preferences.findByUserId(userId),
]);

// 2. Streaming for large data
async function* streamOrders() {
  const pageSize = 100;
  let page = 0;
  
  while (true) {
    const orders = await db.orders.find({ 
      skip: page * pageSize, 
      take: pageSize 
    });
    
    if (orders.length === 0) break;
    
    yield orders;
    page++;
  }
}

// 3. Compression
app.use(compression());

// 4. Rate limiting with Redis
const limiter = rateLimit({
  store: new RedisStore({ client: redis }),
  windowMs: 15 * 60 * 1000,  // 15 min
  max: 100,
});
```

### 9.4. Frontend Performance ⭐

**Core Web Vitals Targets:**
- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): < 0.1

**Optimization:**
```typescript
// 1. Code splitting
const AdminPanel = lazy(() => import('./AdminPanel'));

// 2. Image optimization
<img 
  src="/image.jpg" 
  loading="lazy" 
  width="800" 
  height="600"
  srcset="/image-400.jpg 400w, /image-800.jpg 800w"
  sizes="(max-width: 600px) 400px, 800px"
/>

// 3. Prefetch/preload
<link rel="prefetch" href="/next-page.js" />
<link rel="preload" href="/font.woff2" as="font" />

// 4. Memoization
const ExpensiveComponent = React.memo(({ data }) => {
  const processed = useMemo(() => heavyProcess(data), [data]);
  return <div>{processed}</div>;
});

// 5. Virtualization (cho long lists)
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={1000}
  itemSize={50}
>
  {Row}
</FixedSizeList>
```

---

## 10. Monitoring & Observability ⭐

### 10.1. Logging

**Log Levels:**
```typescript
// DEBUG: Chi tiết cho debugging (chỉ dev/staging)
logger.debug('Cache hit', { key: 'user:123' });

// INFO: Flow chính, milestone
logger.info('Order created', { orderId, userId, amount });

// WARN: Bất thường nhưng không lỗi
logger.warn('Payment gateway slow', { duration: 3000, gateway: 'stripe' });

// ERROR: Lỗi cần xử lý
logger.error('Payment failed', { error, orderId, userId });

// FATAL: Lỗi nghiêm trọng, service down
logger.fatal('Database connection lost', { error });
```

**Structured Logging (JSON):**
```json
{
  "timestamp": "2025-12-25T10:30:00.000Z",
  "level": "INFO",
  "service": "order-service",
  "traceId": "abc123",
  "spanId": "def456",
  "message": "Order created",
  "context": {
    "orderId": "ord_789",
    "userId": "usr_123",
    "amount": 1000000,
    "duration_ms": 150
  }
}
```

**Không log:**
- ❌ Passwords, tokens, API keys
- ❌ Credit card numbers
- ❌ Full personal data (email OK nếu cần, phone number nên mask)
- ❌ Large payloads (> 1KB)

### 10.2. Metrics (Prometheus)

**Application Metrics:**
```typescript
import { Counter, Histogram } from 'prom-client';

// Request counter
const httpRequestsTotal = new Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'route', 'status'],
});

// Response time
const httpRequestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration',
  labelNames: ['method', 'route'],
  buckets: [0.1, 0.5, 1, 2, 5],
});

// Business metrics
const ordersCreated = new Counter({
  name: 'orders_created_total',
  help: 'Total orders created',
  labelNames: ['status', 'payment_method'],
});
```

**Key Metrics:**
- Request rate (req/s)
- Error rate (%)
- Latency (p50, p95, p99)
- Active connections
- Queue depth
- Cache hit/miss ratio
- Database query time

### 10.3. Tracing (OpenTelemetry)

```typescript
import { trace } from '@opentelemetry/api';

async function createOrder(userId: string, items: Item[]) {
  const tracer = trace.getTracer('order-service');
  
  return await tracer.startActiveSpan('createOrder', async (span) => {
    span.setAttribute('user.id', userId);
    span.setAttribute('items.count', items.length);
    
    try {
      // Calculate total
      const total = await tracer.startActiveSpan('calculateTotal', async (calcSpan) => {
        const result = items.reduce((sum, item) => sum + item.price * item.qty, 0);
        calcSpan.end();
        return result;
      });
      
      // Save to DB
      const order = await tracer.startActiveSpan('saveOrder', async (saveSpan) => {
        const result = await db.orders.create({ userId, items, total });
        saveSpan.end();
        return result;
      });
      
      span.setStatus({ code: 1 });  // OK
      return order;
    } catch (error) {
      span.setStatus({ code: 2, message: error.message });  // ERROR
      throw error;
    } finally {
      span.end();
    }
  });
}
```

### 10.4. Alerting

**Alert Rules (Prometheus):**
```yaml
groups:
  - name: api_alerts
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          
      # Slow response time
      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
        for: 10m
        labels:
          severity: warning
          
      # Service down
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
```

**Alert Channels:**
- Critical: PagerDuty / OpsGenie (24/7)
- Warning: Slack / Email
- Info: Dashboard only

---

## 11. Documentation ⭐

### 11.1. Code Documentation

**README.md (bắt buộc):**
```markdown
# Project Name

## 