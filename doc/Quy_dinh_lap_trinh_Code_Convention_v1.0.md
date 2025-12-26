# Quy định lập trình & Code Convention (v1.0)

> Áp dụng cho toàn bộ lập trình viên tham gia dự án: FE/BE/Mobile/DevOps/Data.

QUY ĐỊNH LẬP TRÌNH & CODE CONVENTION
(Áp dụng cho lập trình viên)
Phiên bản: 1.0   |   Ngày hiệu lực: 25/12/2025
Chủ sở hữu tài liệu: CTO/Tech Lead   |   Phạm vi: Toàn bộ dự án phần mềm

## 1. Mục tiêu

- Đảm bảo code dễ đọc - dễ bảo trì - dễ mở rộng, giảm lỗi và giảm phụ thuộc cá nhân.
- Thống nhất cách tổ chức codebase, đặt tên, format, logging, test và quy trình review.
- Tăng tốc phát triển nhưng vẫn giữ chất lượng sản phẩm và an toàn vận hành.

## 2. Nguyên tắc chung

- Ưu tiên tính rõ ràng hơn sự “thông minh” (code phải đọc hiểu nhanh).
- Một thay đổi = một mục tiêu; tránh “đi kèm tiện tay”.
- Không lặp lại (DRY) nhưng không “over-engineer”.
- Không commit bí mật (API key, password, token) dưới mọi hình thức.
- Mọi thay đổi phải có cách kiểm chứng: test, log, hoặc hướng dẫn kiểm thử.

## 3. Quy định về codebase & cấu trúc dự án


### 3.1. Chuẩn cấu trúc thư mục (gợi ý)

Tùy kiến trúc (monorepo hoặc multi-repo), nhưng phải thống nhất theo mẫu:
• /apps (web, mobile, admin)
• /services (API, worker, cron)
• /packages (shared libs, UI kit, utils)
• /db (schema, migrations, seeds)
• /infra (docker, k8s, terraform, nginx)
• /docs (đặc tả, ADR, hướng dẫn)
• /scripts (tooling, automation)

### 3.2. Quy định file cấu hình

- Bắt buộc có .env.example (hoặc config.example.*) để mô tả đầy đủ biến môi trường.
- Không commit file .env thật. Dùng secret manager hoặc CI/CD variables.
- Thông số môi trường được phân tầng: development / staging / production.
- Mọi cấu hình phải có giá trị mặc định hợp lý hoặc fail-fast với thông báo rõ.

### 3.3. Dependency & version

- Bắt buộc commit lockfile (package-lock.json / pnpm-lock.yaml / poetry.lock / go.sum...).
- Không nâng dependency “hàng loạt” nếu không có lý do; nâng theo đợt + có kiểm thử.
- Không thêm library mới nếu có thể tái sử dụng thư viện hiện có.
- Thư viện có rủi ro bảo mật phải được scan và cập nhật theo cảnh báo.

## 4. Git workflow, branch & pull request (PR)


### 4.1. Quy ước branch

- main: nhánh phát hành (deploy production).
- develop (nếu dùng): nhánh tích hợp (deploy staging).
- feature/<ticket>-<mo-ta-ngan>: phát triển tính năng.
- fix/<ticket>-<mo-ta-ngan>: sửa lỗi.
- hotfix/<ticket>-<mo-ta-ngan>: sửa nóng production.

### 4.2. Quy định PR

- Không merge trực tiếp vào main (trừ trường hợp hotfix có phê duyệt).
- Mỗi PR phải có: mô tả, phạm vi ảnh hưởng, cách test, ảnh/screenshot nếu là UI.
- PR phải nhỏ: ưu tiên < 400 dòng thay đổi. Nếu lớn hơn, chia nhỏ theo bước.
- Tối thiểu 1 reviewer; các module quan trọng (auth, payment, pricing, data) cần 2 reviewer.
- Không “approve cho xong”. Reviewer chịu trách nhiệm về rủi ro kỹ thuật.

## 5. Quy định commit message

Áp dụng “Conventional Commits” để dễ đọc lịch sử và sinh release note:
- Ví dụ: feat(api): add order pagination
- Các loại: feat, fix, refactor, perf, test, docs, chore, ci, build
- Mỗi commit chỉ tập trung 1 việc; tránh commit kiểu “update” hoặc “fix bug”.
- Không commit file build/artefact nếu không cần thiết.
- Nếu có ticket, bắt buộc gắn ticket trong branch/PR; commit nên nhắc tới ticket khi phù hợp.

## 6. Code convention (đặt tên - format - tổ chức code)


### 6.1. Quy định chung (ngôn ngữ nào cũng áp dụng)

- Hàm/Method: không quá 40-60 dòng; nếu dài hơn phải tách nhỏ.
- Một hàm làm một việc; tham số không quá 5 (nếu nhiều -> dùng object/struct).
- Tránh “magic number/string”: đưa vào constant hoặc config có tên rõ.
- Không để TODO không có hạn xử lý; TODO phải kèm ticket hoặc thời hạn.
- Ưu tiên kiểu dữ liệu rõ ràng (type hint/typing/interface) cho vùng business logic.

### 6.2. Quy ước đặt tên

- Biến/hàm: camelCase (JS/TS), snake_case (Python), lowerCamelCase (Java/Kotlin), theo chuẩn ngôn ngữ dự án.
- Class/Type: PascalCase.
- Hằng số: UPPER_SNAKE_CASE.
- Boolean: bắt đầu bằng is/has/can/should.
- Tên phải thể hiện ý nghĩa nghiệp vụ: totalAmount, orderStatus, customerTier...

### 6.3. Quy định file & folder naming

- Frontend: file component dùng PascalCase (UserCard.tsx); các file khác dùng kebab-case (order-service.ts).
- Backend: module/package theo domain (orders, customers, inventory) - không đặt theo kỹ thuật (helpers2).
- Tránh viết tắt khó hiểu. Nếu bắt buộc viết tắt, phải có trong glossary ở /docs.

### 6.4. Format & lint bắt buộc

- Bắt buộc dùng formatter tự động và chạy trước khi push: Prettier/ESLint (JS/TS), Black/isort (Python), gofmt (Go)...
- CI sẽ fail nếu lint/format fail.
- Giới hạn độ dài dòng khuyến nghị: 100 ký tự (trừ URL dài).
- Không disable lint rule nếu không có lý do. Nếu disable phải ghi chú rõ ràng.

## 7. Exception, error handling & logging


### 7.1. Error handling

- Không nuốt lỗi (try/catch rỗng). Nếu catch phải xử lý: log, wrap, hoặc trả lỗi chuẩn.
- Lỗi phải phân loại: validation (4xx), business rule (4xx), system/dependency (5xx).
- Trong API, luôn trả về format lỗi thống nhất (xem phụ lục).

### 7.2. Logging

- Log theo cấp: DEBUG (dev), INFO (flow), WARN (bất thường), ERROR (lỗi).
- Log dạng structured (JSON) nếu có thể; kèm correlationId/requestId.
- Không log dữ liệu nhạy cảm: password, token, OTP, số thẻ, thông tin cá nhân không cần thiết.

## 8. API convention (REST/JSON)

- Endpoint theo danh từ số nhiều: /v1/orders, /v1/customers.
- Sử dụng HTTP status code đúng: 200/201/204, 400/401/403/404/409, 500.
- Pagination chuẩn: ?page=1&pageSize=20 hoặc cursor-based; phải thống nhất toàn hệ thống.
- Filtering/sorting: ?status=PAID&sort=-createdAt.
- Thời gian dùng ISO 8601; timezone rõ ràng (UTC hoặc Asia/Ho_Chi_Minh theo thiết kế).

## 9. Database convention & migration

- Tên bảng/column dùng snake_case; bảng số nhiều (orders), column số ít (created_at).
- Bắt buộc có created_at, updated_at; nếu soft delete dùng deleted_at.
- Mọi thay đổi schema phải đi qua migration; cấm sửa trực tiếp production.
- Migration phải rollback được hoặc có kế hoạch rollback.
- Không lưu dữ liệu nhạy cảm dạng plaintext; dùng hashing/encryption theo chuẩn.

## 10. Testing & chất lượng


### 10.1. Quy định test tối thiểu

- Business logic bắt buộc có unit test.
- API quan trọng có integration test (đăng nhập, phân quyền, tạo đơn, thanh toán...).
- Bug fix bắt buộc kèm test để tránh tái phát.
- Coverage mục tiêu: >= 70% cho core domain (có thể tăng theo thời gian).

### 10.2. Quy ước test

- Tên test theo dạng: should_<expected>_when_<condition>.
- Sử dụng pattern Arrange - Act - Assert.
- Test độc lập, không phụ thuộc thứ tự chạy.

## 11. Security & compliance

- Validate input ở biên (API/Controller) và validate nghiệp vụ ở domain layer.
- Áp dụng nguyên tắc least privilege cho API key, service account.
- Rate limit các endpoint nhạy cảm (login, OTP, search).
- Chống SQL injection/XSS/CSRF theo framework; không tự “tự chế” auth.
- Thư viện có CVE phải xử lý theo mức độ nghiêm trọng và kế hoạch rõ ràng.

## 12. Code review checklist (bắt buộc trước khi merge)

1. Code chạy đúng theo mô tả PR và không phá luồng hiện có.
2. Naming, cấu trúc rõ ràng; không có dead code.
3. Đã có test phù hợp; CI xanh.
4. Không log/commit dữ liệu nhạy cảm.
5. Xử lý lỗi và edge case hợp lý; không swallow errors.
6. Performance: tránh N+1, query nặng; có index/memo/cache khi cần.
7. Docs/README/Swagger (nếu có) đã cập nhật.

## 13. Definition of Done (DoD)

- PR đã được review và approved theo quy định.
- Lint/format/test pass trên CI.
- Đã update tài liệu liên quan (README, API docs, ADR nếu thay đổi kiến trúc).
- Không còn TODO “mở”; nếu có, phải có ticket và được chấp thuận.
- Đã kiểm thử theo checklist và ghi lại trong PR.

## Phụ lục A - Mẫu format lỗi API (gợi ý)

Mẫu JSON response lỗi thống nhất (khuyến nghị):
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Dữ liệu không hợp lệ",
    "details": [
      {"field": "phone", "reason": "invalid_format"}
    ],
    "requestId": "8f2a..."
  }
}

## Phụ lục B - Checklist nhanh trước khi push

1. Chạy formatter + lint.
2. Chạy test tối thiểu liên quan.
3. Đảm bảo không có key/secret trong diff.
4. Đảm bảo log không in dữ liệu nhạy cảm.
5. Cập nhật README/docs nếu thay đổi cách chạy hoặc API.
