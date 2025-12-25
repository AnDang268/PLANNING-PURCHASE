# **Tài liệu hướng dẫn tích hợp** 

# **MISA CRM**

[**1\. Giới thiệu	2**](#giới-thiệu)

[1.1. Thông tin cần trước khi kết nối	2](#thông-tin-cần-trước-khi-kết-nối)

[1.2. Thông tin chi tiết để kết nối	2](#thông-tin-chi-tiết-để-kết-nối)

[1.3. Mô tả cấu trúc của API	3](#mô-tả-cấu-trúc-của-api)

[1.4. Hướng dẫn xử lý Response	4](#hướng-dẫn-xử-lý-response)

[1.5. Các bước thực hiện	4](#các-bước-thực-hiện)

[**2\. API lấy mã kết nối	5**](#api-lấy-mã-kết-nối)

[**3\. API sinh dữ liệu	6**](#api-sinh-dữ-liệu)

[1\. Thêm mới	6](#thêm-mới)

[2\. Sửa	7](#sửa)

[3\. Xóa	8](#xóa)

[**4\. API lấy dữ liệu	9**](#api-lấy-dữ-liệu)

[4.1. Lấy danh sách phân trang	9](#lấy-danh-sách-phân-trang)

[4.2. Lấy thông tin theo trường dữ liệu	10](#lấy-thông-tin-theo-trường-dữ-liệu)

[4.3. Lấy thông tin kho theo trường dữ liệu	11](#lấy-thông-tin-kho-theo-trường-dữ-liệu)

[**5\. API cập nhật	12**](#api-cập-nhật)

[5.1. Cập nhật tồn kho	12](#cập-nhật-tồn-kho)

[**6\. Mô tả đối tượng	13**](#mô-tả-đối-tượng)

[6.1. Hàng hóa	13](#hàng-hóa)

[6.2. Khách hàng	15](#khách-hàng)

[6.3. Đơn đặt hàng	17](#đơn-đặt-hàng)

[6.4. Kho	23](#kho)

[**7\. Mã lỗi thường gặp	25**](#mã-lỗi-thường-gặp)

1. # **Giới thiệu** {#giới-thiệu}

Tài liệu này dành cho các nhà phát triển ứng dụng muốn ứng dụng của mình có thể kết nối với hệ thống phần mềm **AMIS CRM** . Tài liệu sẽ mô tả phương thức kết nối giữa các ứng dụng từ Client (máy chủ/máy trạm của Khách hàng) tới service của hệ thống AMIS CRM .

1. ## Thông tin cần trước khi kết nối {#thông-tin-cần-trước-khi-kết-nối}

| Thông tin | Giá trị | Diễn giải |
| ----- | ----- | ----- |
| userName | userName | Tài khoản MISAID |
| password | password | Mật khẩu tài khoản |
| client\_id | Quản trị ứng dụng CRM phải vào ứng dụng CRM thực hiện kết nối và thay đổi thông tin thiết lập AppID của ứng dụng. |  |
| client\_secret | Quản trị ứng dụng CRM phải vào ứng dụng CRM thực hiện chức năng Tạo mã mới. |  |
| callback | Nếu đối tác/kh có nhu cầu nhận phản hồi từ hệ thống AMIS CRM, vui lòng build project callback/webhook và gửi cho MISA URL của callback/webhook |  |

   2. ## Thông tin chi tiết để kết nối {#thông-tin-chi-tiết-để-kết-nối}

| Thông tin | Diễn giải |
| ----- | ----- |
| APICrmUrl | https://amisapp.misa.vn/crm/gc/api/public/api/v2 |
| Token url (lấy access\_token) | /api/oauth/actopen/connect |
| Get dictionary (lấy danh sách danh mục) | /apir/sync/actopen/get\_dictionary |
| Save dictionary (tạo danh mục) | /apir/sync/actopen/save\_dictionary |
| Save voucher (tạo yêu cầu sinh CT) | /api/sync/actopen/save |

      

   3. ## Mô tả cấu trúc của API {#mô-tả-cấu-trúc-của-api}

| Thông tin | Diễn giải |
| ----- | ----- |
| Url | Theo từng API cụ thể |
| Method | Get/Post (Theo từng API cụ thể) |
| Params | Không sử dụng |
| Header | X-MISA-AccessToken: {access\_token} |
| Body | Content-Type: application/json (Theo từng API cụ thể) |
| Response | {     "success":true/false,     "code": "Mã lỗi",     "ErrorMessage": "Mô tả lỗi",     "Data": "Dữ liệu phản hồi" } |

      ## 

   4. ## Hướng dẫn xử lý Response {#hướng-dẫn-xử-lý-response}

| Thông tin | Diễn giải |
| ----- | ----- |
| HTTP status code |  |
| 200 | OK Cho biết request đã thành công. Chú ý: Với phương thức GET đồng nghĩa với việc dữ liệu trả về đã nằm trong response \-\> Client không phải handle gì thêm và có thể sử dụng luôn dữ liệu trả về. |
| 201  | CREATED Tạo dữ liệu thành công. Sử dụng cho phương thức POST. |
| 400  | BAD REQUEST Server không hiểu cú pháp của request. Chú ý: Trong cả các trường hợp validate thông tin input lỗi cũng trả về lỗi này. |
| 401  | UNAUTHORIZED Hệ thống chưa được ủy quyền. |
| 403  | FORBIDDEN Server từ chối yêu cầu ngay cả khi Client đã được ủy quyền |
| 404  | NOT FOUND Server không tìm thấy bất kì tài nguyên nào liên quan tới request URL này. |
| 500  | INTERNAL SERVER ERROR Có lỗi xảy ra phía máy chủ. |
| Xử lý response của API |  |
| Response thành công | Được mô tả ở mỗi API |
| Response lỗi | Trả về cùng 1 định dạng, sau đây gọi là ResponseError { 	"ErrorCode": "Mã lỗi", 	"DevMsg": "mô tả thông tin lỗi cho người phát triển", 	"UserMsg": "mô tả thông tin lỗi cho người dùng", 	"TraceId": "Mã để tra cứu thông tin" } |

   5. ## Các bước thực hiện {#các-bước-thực-hiện}

| Thông tin | Diễn giải |
| ----- | ----- |
| Thực hiện cấu hình kết nối | Thực hiện mở kết nối API, lấy được các thông tin client\_id và client\_secret |
| [API lấy mã kết nối](#api-lấy-mã-kết-nối) | Lấy được giá trị của token, sử dụng cho các API về sau |
| [API sinh dữ liệu](#api-sinh-dữ-liệu) | Sinh ra các dữ liệu trên hệ thống CRM (Khách hàng, đơn hàng, hàng hóa …) |
| [API lấy dữ liệu](#api-lấy-dữ-liệu) | Lấy dữ liệu từ hệ thống CRM về ERP (Khách hàng, đơn hàng, hàng hóa …) |
| Postman tham khảo | \- [Tải về](https://drive.usercontent.google.com/u/1/uc?id=1nXSdW7d6enQoNrRWiCdS6XGnoHockeXm&export=download) |

2. # **API lấy mã kết nối** {#api-lấy-mã-kết-nối}

Sử dụng khi kết nối với ứng dụng AMIS CRM để lấy token phục vụ cho các hàm xử lý nghiệp vụ

| Thông tin | Diễn giải |
| ----- | ----- |
| URL | {[APICrmUrl](#thông-tin-chi-tiết-để-kết-nối)}/Account |
| Method | Post |
| Body request | {  "client\_id": "{client\_id}",  "client\_secret": "{client\_secret}" } |
| Response | {   "success": true/false, //trạng thái trả về của server   "code": \<trạng thái trả về của resquest\>,   "data": "token trả về" } |
| Lưu ý | Lưu lại thông tin của token ở data (token có hạn 24h) |
| [Mã lỗi thường gặp](#mã-lỗi-thường-gặp) |  |

## 

3. # **API sinh dữ liệu** {#api-sinh-dữ-liệu}

1. ## Thêm mới {#thêm-mới}

| Thông tin | Diễn giải |
| ----- | ----- |
| URL | {[APICrmUrl](#thông-tin-chi-tiết-để-kết-nối)}/{Select} **Select**:  *Product*: Hàng hóa *Contacts*: Liên hệ *Customers*: Khách hàng *SaleOrders*: Đơn hàng *Stocks*: Kho hàng |
| Method | Post |
| Header | **Authorization**: giá trị token lấy ở [bước II](#api-lấy-mã-kết-nối) **Clientid**: AppID lấy từ thiết lập trên AMIS CRM |
| Body request | \[ {Select1}, {Select2}, … {SelectN}, \] |
| Response | {   "success": true,   "code": "",\<mã lỗi nếu có\>   "data": "\<Danh sách kết quả trả về\>" } |
| [Mô tả đối tượng](#mô-tả-đối-tượng) | Xem mô tả của từng đối tượng sử dụng |
| [Mã lỗi thường gặp](#mã-lỗi-thường-gặp) |  |

   ## 

2. ## Sửa {#sửa}

| Thông tin | Diễn giải |
| ----- | ----- |
| URL | {[APICrmUrl](#thông-tin-chi-tiết-để-kết-nối)}/{Select} **Select**:  *Product*: Hàng hóa *Contacts*: Liên hệ *Customers*: Khách hàng *SaleOrders*: Đơn hàng *Stocks*: Kho hàng |
| Method | PUT |
| Header | **Authorization**: giá trị token lấy ở [bước II](#api-lấy-mã-kết-nối) **Clientid**: AppID lấy từ thiết lập trên AMIS CRM |
| Body request | \[ {Select1}, {Select2}, … {SelectN}, \] **Lưu ý**: truyền đúng ID của đối tượng muốn cập nhật, chỉ truyền lên những thông tin sửa, những thông tin không truyền lên mặc định không sửa |
| Response | {   "success": true,   "code": "",\<mã lỗi nếu có\>   "data": "\<Danh sách kết quả trả về\>" } |
| [Mô tả đối tượng](#mô-tả-đối-tượng) | Xem mô tả của từng đối tượng sử dụng |
| [Mã lỗi thường gặp](#mã-lỗi-thường-gặp) |  |

   ## 

3. ## Xóa {#xóa}

| Thông tin | Diễn giải |
| ----- | ----- |
| URL | {[APICrmUrl](#thông-tin-chi-tiết-để-kết-nối)}/{Select} Select:  *Product*: Hàng hóa *Contacts*: Liên hệ *Customers*: Khách hàng *SaleOrders*: Đơn hàng *Stocks*: Kho hàng |
| Method | DELETE |
| Header | **Authorization**: giá trị token lấy ở [bước II](#api-lấy-mã-kết-nối) **Clientid**: AppID lấy từ thiết lập trên AMIS CRM |
| Body request | \[ {ID1}, {ID2}, … {IDN}, \] **Lưu ý**: truyền đúng ID của đối tượng muốn xóa |
| Response | {   "success": true,   "code": "",\<mã lỗi nếu có\>   "data": "\<Danh sách kết quả trả về\>" } |
| [Mô tả đối tượng](#mô-tả-đối-tượng) | Xem mô tả của từng đối tượng sử dụng |
| [Mã lỗi thường gặp](#mã-lỗi-thường-gặp) |  |

   ## 

   # 

4. # **API lấy dữ liệu** {#api-lấy-dữ-liệu}

   1. ## Lấy danh sách phân trang {#lấy-danh-sách-phân-trang}

| Thông tin | Diễn giải |
| ----- | ----- |
| URL | {[APICrmUrl](#thông-tin-chi-tiết-để-kết-nối)}/{Select} **Select**:  *Product*: Hàng hóa *Contacts*: Liên hệ *Customers*: Khách hàng *SaleOrders*: Đơn hàng *Stocks*: Kho hàng |
| Method | GET |
| Header | Authorization: giá trị token lấy ở [bước II](#api-lấy-mã-kết-nối) Clientid: AppID lấy từ thiết lập trên AMIS CRM |
| Params request | {   “page”: trang muốn xem   “pageSize”: số lượng bản ghi của trang, mặc định 10, tối đa 100   “orderBy”: sắp xếp theo trường, mặc định **modified\_date**   “isDescending”: thứ tự sắp xếp, mặc định **true** } |
| Response | {   "success": true,   "code": "",\<mã lỗi nếu có\>   "data": "\<Danh sách kết quả trả về\>" } |
| [Mô tả đối tượng](#mô-tả-đối-tượng) | Xem mô tả của từng đối tượng sử dụng |
| [Mã lỗi thường gặp](#mã-lỗi-thường-gặp) |  |

### 

2. ## Lấy thông tin theo trường dữ liệu {#lấy-thông-tin-theo-trường-dữ-liệu}

API lấy Hàng hóa, liên hệ, khách hàng, đơn hàng theo trường dữ liệu

| Thông tin | Diễn giải |
| ----- | ----- |
| URL | {[APICrmUrl](#thông-tin-chi-tiết-để-kết-nối)}/{Select}/{Field} **Select**:  *Product*: Hàng hóa *Contacts*: Liên hệ *Customers*: Khách hàng *SaleOrders*: Đơn hàng **Field**: *ID:* mã duy nhất *Code*: mã quy định Ví dụ: {[APICrmUrl](#heading=h.nngox32rchgl)}/Product/ID \- lấy hàng hóa theo ID |
| Method | GET |
| Params | code: nếu lấy theo Code id: nếu lấy theo ID |
| Header | Authorization: giá trị token lấy ở [bước II](#api-lấy-mã-kết-nối) Clientid: AppID lấy từ thiết lập trên AMIS CRM |
| Params request | ID: key của dữ liệu muốn lấy Code: mã của dữ liệu muốn lấy Lưu ý: lấy theo Field nào thì truyền Params đó |
| Response | {   "success": true,   "code": "",\<mã lỗi nếu có\>   "data": "\<Danh sách kết quả trả về\>"  }  |
| [Mô tả đối tượng](#mô-tả-đối-tượng) | Xem mô tả của từng đối tượng sử dụng |
| [Mã lỗi thường gặp](#mã-lỗi-thường-gặp) |  |

### 

3. ## Lấy thông tin kho theo trường dữ liệu {#lấy-thông-tin-kho-theo-trường-dữ-liệu}

API lấy Kho theo trường dữ liệu

| Thông tin | Diễn giải |
| ----- | ----- |
| URL | {[APICrmUrl](#thông-tin-chi-tiết-để-kết-nối)}/Stocks/{Field} **Field**: *Asyncid:* Định danh kho *Code*: Mã kho Ví dụ: {[APICrmUrl](#heading=h.nngox32rchgl)}/Product/ID \- lấy hàng hóa theo ID |
| Method | GET |
| Params | stockCode: nếu lấy theo Code id: nếu lấy theo Asyncid |
| Header | Authorization: giá trị token lấy ở [bước II](#api-lấy-mã-kết-nối) Clientid: AppID lấy từ thiết lập trên AMIS CRM |
| Params request | ID: key của dữ liệu muốn lấy Code: mã của dữ liệu muốn lấy Lưu ý: lấy theo Field nào thì truyền Params đó |
| Response | {   "success": true,   "code": "",\<mã lỗi nếu có\>   "data": "\<Danh sách kết quả trả về\>"  }  |
| [Mô tả đối tượng](#mô-tả-đối-tượng) | Xem mô tả của từng đối tượng sử dụng |
| [Mã lỗi thường gặp](#mã-lỗi-thường-gặp) |  |

## 

4. ## Lấy danh sách phân trang \- tồn kho

API lấy tồn kho theo phân trang

| Thông tin | Diễn giải |
| ----- | ----- |
| URL | {[APICrmUrl](#thông-tin-chi-tiết-để-kết-nối)}/Stocks/product\_ledger |
| Method | GET |
| Params request | {   “page”: trang muốn xem   “pageSize”: số lượng bản ghi của trang, mặc định 10, tối đa 100   “stockID”: id của kho } |
| Header | Authorization: giá trị token lấy ở [bước II](#api-lấy-mã-kết-nối) Clientid: AppID lấy từ thiết lập trên AMIS CRM |
| Response | {   "success": true,   "code": "",\<mã lỗi nếu có\>   "data": "\<Danh sách kết quả trả về\>"  }  |
| [Mô tả đối tượng](#mô-tả-đối-tượng) | Xem mô tả của từng đối tượng sử dụng |
| [Mã lỗi thường gặp](#mã-lỗi-thường-gặp) |  |

## 

5. # **API cập nhật** {#api-cập-nhật}

   1. ## Cập nhật tồn kho {#cập-nhật-tồn-kho}

| Thông tin | Diễn giải |
| ----- | ----- |
| URL | {[APICrmUrl](#thông-tin-chi-tiết-để-kết-nối)}/Stocks/product\_ledger |
| Method | Post |
| Header | **Authorization**: giá trị token lấy ở [bước II](#api-lấy-mã-kết-nối) **Clientid**: AppID lấy từ thiết lập trên AMIS CRM |
| Body request | \[     {         "product\_code": "mã vật tư hàng hóa",         "stock\_code": "mã kho",         "quantity": số lượng tồn     } \] |
| Response | {   "success": true,   "code": "",\<mã lỗi nếu có\>   "data": "\<Danh sách kết quả trả về\>" } |
| [Mô tả đối tượng](#mô-tả-đối-tượng) | Xem mô tả của từng đối tượng sử dụng |
| [Mã lỗi thường gặp](#mã-lỗi-thường-gặp) |  |

      ## 

6. # **Mô tả đối tượng** {#mô-tả-đối-tượng}

   1. ## Hàng hóa {#hàng-hóa}

| Tên trường | Kiểu dữ liệu | Bắt Buộc | Ghi chú |
| ----- | ----- | ----- | ----- |
| **Thông tin chung** |  |  |  |
| id | Integer | x | Mã định danh duy nhất của sản phẩm hoặc hàng hóa |
| product\_code | String |  | Mã hàng hóa |
| product\_name | String |  | Tên của sản phẩm hoặc hàng hóa |
| usage\_unit | String |  | Đơn vị tính |
| product\_properties | String |  | Tính chất |
| source | String |  | Nguồn gốc |
| product\_category | String |  | Loại hàng hóa |
| default\_stock | String |  | Kho ngầm định |
| sale\_description | String |  | Diễn giải |
| quantity\_formula | String |  | Công thức tính toán số lượng (nếu có) |
| tag | String |  | Thẻ hoặc nhãn dán liên quan đến sản phẩm (nếu có) |
| is\_follow\_serial\_number | Boolean |  | Chỉ báo xem sản phẩm có theo dõi theo số serial hay không |
| **Thông tin giá** |  |  |  |
| unit\_price | Decimal |  | Đơn giá bán |
| purchased\_price | Decimal |  | Đơn giá mua |
| unit\_price1 | Decimal |  | Đơn giá bán 2 |
| unit\_price2 | Decimal |  | Đơn giá bán 1 |
| tax | String |  | Thuế GTGT |
| unit\_price\_fixed | Decimal |  | Đơn giá bán cố định |
| price\_after\_tax | Boolean |  | Giá bán là đơn giá sau thuế |
| is\_use\_tax | Boolean |  | Ngầm định ghi nhận DS trước thuế |
| unit\_cost | Decimal |  | Đơn giá chi phí của sản phẩm |
| **Thông tin bảo hành** |  |  |  |
| warranty\_period | String |  | Thời hạn bảo hành |
| warranty\_description | String |  | Nội dung bảo hành |
| **Thông tin mô tả** |  |  |  |
| description | String |  | Mô tả |
|  |  |  |  |
| **Thông tin hệ thống** |  |  |  |
| owner\_name | String |  | Chủ sở hữu |
| organization\_unit\_name | String |  | Đơn vị |
| created\_by | String |  | Người tạo |
| created\_date | DateTime |  | Ngày tạo |
| modified\_by | String |  | Người sửa |
| modified\_date | DateTime |  | Ngày sửa |
| is\_public | Boolean |  | Dùng chung |
| inactive | Boolean |  | Ngừng theo dõi |
| form\_layout | String |  | Bố cục |
| is\_set\_product | Boolean |  | Là combo hàng hóa |
| **Thông tin khác** |  |  |  |
| custom\_field\[x\] (x: giá trị số) | Tự định nghĩa |  | Trường tùy chỉnh tự định nghĩa, x là số của trường, ví dụ: custom\_field23 |

      ## 

   2. ## Khách hàng {#khách-hàng}

| Tên trường | Kiểu dữ liệu | Bắt Buộc | Ghi chú |
| ----- | ----- | ----- | ----- |
| **Thông tin chung** |  |  |  |
| account\_number | String |  | Mã khách hàng |
| account\_name | String |  | Tên khách hàng |
| account\_short\_name | String |  | Tên viết tắt |
| lead\_source | String |  | Nguồn gốc |
| number\_of\_days\_owed | Integer |  | Số ngày được nợ |
| tax\_code | String |  | Mã số thuế |
| office\_tel | String |  | Điện thoại |
| parent\_account\_name | String |  | Đơn vị chủ quản |
| account\_type | String |  | Loại khách hàng |
| gender | String |  | Giới tính |
| office\_email | String |  | Email |
| business\_type | String |  | Loại hình |
| sector\_name | String |  | Lĩnh vực |
| industry | String |  | Ngành hàng |
| **Thông tin giao hàng** |  |  |  |
| shipping\_country | String |  | Quốc gia |
| shipping\_province | String |  | Tỉnh/Thành phố |
| shipping\_district | String |  | Quận/Huyện (Giao hàng) |
| shipping\_ward | String |  | Phường/Xã (Giao hàng) |
| shipping\_street | String |  | Số nhà, Đường phố (Giao hàng) |
| shipping\_code | String |  | Mã vùng (Giao hàng) |
| shipping\_address | String |  | Địa chỉ (Giao hàng) |
| **Thông tin hóa đơn** |  |  |  |
| billing\_country | String |  | Quốc gia (Hóa đơn) |
| billing\_province | String |  | Mã vùng (Hóa đơn) |
| billing\_district | String |  | Quận/Huyện (Hóa đơn) |
| billing\_ward | String |  | Tỉnh/Thành phố (Hóa đơn) |
| billing\_street | String |  | Số nhà, Đường phố (Hóa đơn) |
| billing\_code | String |  | Phường/Xã (Hóa đơn) |
| billing\_address | String |  | Địa chỉ (Hóa đơn) |
| **Thông tin bổ sung** |  |  |  |
| bank\_account | String |  | Tài khoản ngân hàng |
| customer\_since\_date | DateTime |  | Là khách hàng từ |
| celebrate\_date | DateTime |  | Ngày thành lập/Ngày sinh |
| no\_of\_employee\_name | String |  | Quy mô nhân sự |
| annual\_revenue | String |  | Doanh thu |
| website | String |  | Website |
| debt | Decimal |  | Cộng nợ |
| debt\_limit | Decimal |  | Hạn mức nợ |
| **Thông tin hệ thống** |  |  |  |
| owner\_name | String |  | Chủ sở hữu |
| organization\_unit\_name | String |  | Đơn vị |
| created\_by | String |  | Người tạo |
| created\_date | DateTime |  | Ngày tạo |
| modified\_by | String |  | Người sửa |
| modified\_date | DateTime |  | Ngày sửa |
| is\_public | Boolean |  | Dùng chung |
| form\_layout | Boolean |  | Bố cục |
| form\_layout | String |  | Ngày tương tác gần nhất |
| is\_set\_product | Boolean |  | Điểm khách hàng |
| is\_personal | Boolean |  | Là KH cá nhân |
| inactive | Boolean |  | Ngừng theo dõi |
| is\_distributor | Boolean |  | Là nhà phân phối |
| related\_users | String |  | Người liên quan |
| **Thông tin thống kê mua hàng** |  |  |  |
| total\_score | Decimal |  | Tổng điểm |
| purchase\_date\_recent | DateTime |  | Ngày mua gần đây |
| **Thông tin khác** (Thông tin này KH cần định tự định nghĩa) |  |  |  |
| custom\_field\[x\] (x: giá trị số) | Tự định nghĩa |  | Trường tùy chỉnh tự định nghĩa, x là số của trường, ví dụ: custom\_field23 |

      ## 

   3. ## Đơn đặt hàng {#đơn-đặt-hàng}

| Tên trường | Kiểu dữ liệu | Bắt Buộc | Ghi chú |
| ----- | ----- | ----- | ----- |
| **Thông tin chung** |  |  |  |
| un\_invoiced\_amount | Decimal |  | Giá trị chưa xuất hóa đơn \= Giá trị thanh lý \- Giá trị đã xuất hóa đơn |
| total\_summary | Decimal |  | Tổng tiền \=\> tổng hợp từ bảng hàng hóa lên |
| balance\_receipt\_amount | Decimal |  | Còn phải thu \= Giá trị thanh lý \- Thực thu |
| tax\_summary | Decimal |  | Tiền thuế \=\> tổng hợp từ bảng hàng hóa lên |
| discount\_summary | Decimal |  | Tiền chiết khấu \=\> tổng hợp từ bảng hàng hóa lên |
| to\_currency\_summary | Decimal |  | Thành tiền \=\> tổng hợp từ bảng hàng hóa lên |
| shipping\_amount\_summary | Decimal |  | Số lượng giao \=\> tổng hợp từ bảng hàng hóa lên |
| liquidate\_amount | Decimal |  | Giá trị thanh lý |
| to\_currency\_summary\_oc | Decimal |  | Thành tiền nguyên tệ \=\> tổng hợp từ bảng hàng hóa lên |
| discount\_summary\_oc | Decimal |  | Tiền chiết khấu nguyên tệ \=\> tổng hợp từ bảng hàng hóa lên |
| tax\_summary\_oc | Decimal |  | Tiền thuế nguyên tệ \=\> tổng hợp từ bảng hàng hóa lên |
| total\_summary\_oc | Decimal |  | Tổng tiền nguyên tệ \=\> tổng hợp từ bảng hàng hóa lên |
| liquidate\_amount\_oc | Decimal |  | Giá trị thanh lý nguyên tệ |
| sale\_order\_amount\_oc | Decimal |  | Giá trị đơn hàng nguyên tệ |
| total\_receipted\_amount\_oc | Decimal |  | Thực thu nguyên tệ |
| balance\_receipt\_amount\_oc | Decimal |  | Còn phải thu nguyên tệ \= Giá trị thanh lý nguyên tệ \- Thực thu nguyên tệ |
| to\_currency\_after\_discount\_summary | Decimal |  | Thành tiền sau CK \=\> tổng hợp từ bảng hàng hóa lên |
| to\_currency\_oc\_after\_discount\_summary | Decimal |  | Thành tiền nguyên tệ sau CK \=\> tổng hợp từ bảng hàng hóa lên |
| amount\_summary | Decimal |  | Số lượng \=\> tổng hợp từ bảng hàng hóa lên |
| usage\_unit\_amount\_summary | Decimal |  | SL theo ĐVTC \=\> tổng hợp từ bảng hàng hóa lên |
| approved\_status | String |  | Trạng thái phê duyệt \- Chờ duyệt \- Đã duyệt \- Từ chối |
| approver | String |  | Người duyệt |
| approved\_date | DateTime |  | Ngày duyệt |
| is\_sync\_price\_after\_discount | Boolean |  | Đồng bộ đơn giá sau CK |
| related\_users | String |  | Người liên quan |
| is\_use\_currency | Boolean |  | Đánh dấu sử dụng ngoại tệ |
| sale\_order\_no | String |  | Số hợp đồng |
| account\_name | String |  | Khách hàng |
| due\_date | DateTime |  | Hạn thanh toán |
| sale\_order\_amount | Decimal |  | Giá trị đơn hàng |
| sale\_order\_name | String |  | Diễn giải |
| parent\_name | String |  | Đơn hàng cha |
| book\_date | DateTime |  | Ngày ghi sổ |
| quote\_name | String |  | Báo giá |
| number\_of\_days\_owed | Integer |  | Số ngày được nợ |
| campaign\_name | String |  | Chiến dịch |
| contact\_name | String |  | Liên hệ |
| sale\_order\_type | String |  | Loại đơn hàng \- Bán mới \- Nâng cấp \- Gia hạn/Cập nhật \- Dịch vụ đào tạo \- Dịch vụ tư vấn triển khai \- Dịch vụ khác |
| deadline\_date | DateTime |  | Hạn giao hàng |
| opportunity\_name | String |  | Cơ hội |
| invoice\_date | DateTime |  | Ngày hóa đơn |
| exchange\_rate | Decimal |  | Tỷ giá |
| currency\_type | String |  | Loại tiền \- VND \- USD \- EUR \- GBP \- MYR \- MMK \- CNY \- JPY |
| un\_subcrible | Boolean |  | Ngừng theo dõi |
| phone | String |  | Điện thoại |
| sale\_order\_product\_mappings | **List\<Item\>** |  | Danh sách hàng hóa |
| **Thông tin hàng hóa \<Item\>** |  |  |  |
| product\_code | String |  | Mã hàng hóa |
| to\_currency\_oc |  |  | Thành tiền nguyên tệ \= \- Nếu Đơn giá sau thuế \> 0 \=\> (Đơn giá sau thuế \* Số lượng) / (1 \+ Thuế suất / 100\) \- else \=\> Đơn giá \* Số lượng |
| total\_oc | Decimal |  | Tổng tiền nguyên tệ \= Thành tiền nguyên tệ \- Tiền chiết khấu nguyên tệ \+ Tiền thuế nguyên tệ |
| description | String |  | Diễn giải/ mô tả |
| amount | Decimal |  | Số lượng |
| stock\_name | String |  | Kho |
| price | Decimal |  | Thành tiền |
| unit | String |  | Đơn vị tính |
| usage\_unit | String |  | Đơn vị tính chính |
| discount | Decimal |  | Tiền chiết khấu |
| discount\_percent | Decimal |  | Tỷ lệ chết khấu |
| ratio | Decimal |  | Tỷ lệ |
| tax | Decimal |  | Tiền thuế |
| tax\_percent | String |  | Thuế suất |
| operator | String |  | Toán tử \- Nhân \- Chia |
| price\_after\_discount | Decimal |  | Đơn giá sau CK \= Đơn giá \* (1 \- Tỷ lệ chiết khấu / 100\) |
| to\_currency\_oc\_after\_discount | Decimal |  | Thành tiền nguyên tệ sau CK \= Thành tiền nguyên tệ \- Tiền chiết khấu nguyên tệ |
| usage\_unit\_amount | Decimal |  | SL theo ĐVTC |
| usage\_unit\_price | Decimal |  | Đơn giá theo ĐVTC |
| price | Decimal |  | Đơn giá |
| is\_promotion | Boolean |  | Hàng KM |
| description\_product | String |  | Mô tả |
| batch\_number | String |  | Số lô |
| expire\_date | DateTime |  | Hàn sử dụng |
| exist\_amount | Decimal |  | ĐG tồn theo lô |
| discount\_oc | Decimal |  | Tiền chiết khấu nguyên tệ \= \- Nếu Đơn giá sau thuế \> 0 \=\> (Đơn giá sau thuế \* Số lượng) / (1 \+ Thuế suất / 100\) \* Tỷ lệ chiết khấu / 100 \- else \=\> Đơn giá \* Số lượng \* Tỷ lệ chiết khấu / 100 |
| tax\_oc | Decimal |  | Tiền thuế nguyên tệ |
| to\_currency | Decimal |  | Thành tiền |
| total | Decimal |  | Tổng tiền |
| shipping\_amount | Decimal |  | Số lượng giao |
| price\_after\_tax | Decimal |  | Đơn giá sau thuế |
| sort\_order | Decimal |  | STT |
| height | Decimal |  | Chiều cao |
| width | Decimal |  | Chiều rộng |
| length | Decimal |  | Chiều dài |
| radius | Decimal |  | Bán kính |
| mass | Decimal |  | Lượng |
| to\_currency\_after\_discount | Decimal |  | Thành tiền sau CK \= Thành tiền \- Tiền chiết khấu |
| quantity\_ordered | Decimal |  | Số lượng đặt |
| **Thông tin tình trạng thực hiện đơn hàng** |  |  |  |
| sale\_order\_date | DateTime |  | Ngày đặt hàng |
| revenue\_status | String |  | Tình trạng ghi doanh số \- Bản nháp \- Đề nghị ghi \- Đã ghi \- Từ chối ghi |
| total\_receipted\_amount | Decimal |  | Thực thu |
| delivery\_date | DateTime |  | Ngày giao hàng |
| book\_date | DateTime |  | Ngày ghi sổ |
| status | String |  | Tình trạng \- Chưa thực hiện \- Đang thực hiện \- Đã thực hiện \- Đã hủy bỏ \- Đã giao đủ hàng |
| paid\_date | DateTime |  | Ngày thanh toán |
| invoiced\_amount\_oc | Decimal |  | Giá trị đã xuất hóa đơn |
| sale\_order\_process\_cost | Decimal |  | Dự kiến chi |
| delivery\_status | String |  | Tình trạng giao hàng \- Chưa giao hàng \- Đã giao hàng \- Đang giao hàng |
| is\_invoiced | Boolean |  | Đã xuất hóa đơn |
| pay\_status | String |  | Tình trạng thanh toán \- Chưa thanh toán \- Đã thanh toán \- Đã thanh toán một phần |
| **Thông tin giao hàng** |  |  |  |
| shipping\_country | String |  | Quốc gia (Giao hàng) |
| shipping\_province | String |  | Tỉnh/Thành phố (Giao hàng) |
| shipping\_district | String |  | Quận/Huyện (Giao hàng) |
| shipping\_ward | String |  | Phường/Xã (Giao hàng) |
| shipping\_street | String |  | Số nhà, Đường phố (Giao hàng) |
| shipping\_code | String |  | Mã vùng (Giao hàng) |
| shipping\_address | String |  | Địa chỉ (Giao hàng) |
| ? | String |  | Đơn vị vận chuyển |
| ? | String |  | Mã vận đơn |
| shipping\_contact\_name | String |  | Người nhận hàng |
| **Thông tin hóa đơn** |  |  |  |
| billing\_account | String |  | Khách hàng (Hóa đơn) |
| billing\_contact | String |  | Người mua hàng |
| billing\_country | String |  | Quốc gia (Hóa đơn) |
| billing\_province | String |  | Tỉnh/Thành phố (Hóa đơn) |
| billing\_district | String |  | Quận/Huyện (Hóa đơn) |
| billing\_ward | String |  | Phường/Xã (Hóa đơn) |
| billing\_street | String |  | Số nhà, Đường phố (Hóa đơn) |
| billing\_code | String |  | Mã vùng (Hóa đơn) |
| billing\_address | String |  | Địa chỉ (Hóa đơn) |
| **Thông tin mô tả** |  |  |  |
| description | String |  | Mô tả |
| **Thông tin hệ thống** |  |  |  |
| owner\_name | String |  | Người thực hiện xem trong Thiết lập \=\> Người dùng |
| created\_date | DateTime |  | Ngày tạo (ko đc phép truyền khi thực hiện method POST) |
| recorded\_sale\_users\_name | String |  | Nhân viên được ghi DS |
| created\_by | DateTime |  | Người tạo (ko đc phép truyền khi thực hiện method POST) |
| organization\_unit\_name | String |  | Đơn vị |
| recorded\_sale\_organization\_unit\_name | String |  | Đơn vị được ghi DS |
| modified\_by | String |  | Ngày sửa (ko đc phép truyền khi thực hiện method POST) |
| modified\_date | DateTime |  | Người sửa (ko đc phép truyền khi thực hiện method POST) |
| is\_public | Boolean |  | Dùng chung |
| form\_layout | String |  | Bố cục xem trong Thiết lập \=\> Phân hệ và trường \=\> Đơn hàng |
| related\_users | String |  | Người liên quan |
| ? |  |  | Đối tác/CTV giới thiệu |
| ? |  |  | Điểm đơn hàng |
| is\_sync\_price\_after\_discount | Boolean |  | Đồng bộ đơn giá sau CK 1 |
| is\_parent\_sale\_order |  |  | Là đơn hàng cha |
| **Thông tin khác** (Thông tin này KH cần định tự định nghĩa) |  |  |  |
| custom\_field\[x\] (x: giá trị số) | Tự định nghĩa |  | Trường tùy chỉnh tự định nghĩa, x là số của trường, ví dụ: custom\_field23 |

      ## 

   4. ## Kho {#kho}

| Tên trường | Kiểu dữ liệu | Bắt Buộc | Ghi chú |
| ----- | ----- | ----- | ----- |
| **Thông tin chung** |  |  |  |
| contact\_code | String |  | Mã liên hệ |
| first\_name | String |  | Họ và đệm |
| last\_name | String |  | Tên |
| contact\_name | String |  | Họ và tên |
| description | String |  | Mô tả |
| account\_type | String |  | Phân loại khách hàng |
| account\_name | String |  | Tổ chức |
| email\_opt\_out | Boolean |  | Không gửi mail |
| salutation | String |  | Xưng hô |
| mobile | String |  | ĐT di động |
| title | String |  | Chức danh |
| office\_tel | String |  | ĐT cơ quan |
| phone\_opt\_out | Boolean |  | Không gọi điện |
| office\_email | String |  | Email cơ quan |
| other\_phone | String |  | Điện thoại khác |
| zalo | String |  | Zalo |
| email | String |  | Email cá nhân |
| lead\_source | String |  | Nguồn gốc |
| department | String |  | Phòng ban |
| **Thông tin khác** |  |  |  |
| date\_of\_birth | DateTime |  | Ngày sinh |
| gender | String |  | Giới tính |
| married\_status | String |  | Tình trạng hôn nhân |
| facebook | String |  | Facebook |
| bank\_account | String |  | Tài khoản ngân hàng |
| bank\_name | String |  | Mở tại ngân hàng |
| custom\_field\[x\] (x: giá trị số) | Tự định nghĩa |  | Trường tùy chỉnh tự định nghĩa, x là số của trường, ví dụ: custom\_field23 |
| **Thông tin địa chỉ** |  |  |  |
| mailing\_country | String |  | Quốc gia |
| mailing\_province | String |  | Tỉnh/Thành phố |
| mailing\_district | String |  | Quận/Huyện |
| mailing\_ward | String |  | Phường/Xã |
| mailing\_street | String |  | Số nhà, Đường phố |
| mailing\_zip | String |  | Mã vùng |
| mailing\_address | String |  | Địa chỉ |
| **Thông tin địa chỉ giao hàng** |  |  |  |
| shipping\_country | String |  | Quốc gia (Giao hàng) |
| shipping\_province | String |  | Tỉnh/Thành phố (Giao hàng) |
| shipping\_district | String |  | Quận/Huyện (Giao hàng) |
| shipping\_ward | String |  | Phường/Xã (Giao hàng) |
| shipping\_street | String |  | Số nhà, Đường phố (Giao hàng) |
| shipping\_zip | String |  | Mã vùng (Giao hàng) |
| shipping\_address | String |  | Địa chỉ (Giao hàng) |
| shipping\_long | String |  | Kinh độ (Giao hàng) |
| shipping\_lat | String |  | Vĩ độ (Giao hàng) |
| **Thông tin hệ thống** |  |  |  |
| owner\_name | String |  | Chủ sở hữu |
| organization\_unit\_name | String |  | Đơn vị |
| created\_by | String |  | Người tạo |
| created\_date | DateTime |  | Ngày tạo |
| modified\_by | String |  | Người sửa |
| modified\_date | DateTime |  | Ngày sửa |
| is\_public | Boolean |  | Dùng chung |
| form\_layout | String |  | Bố cục |
| total\_score | String |  | Điểm liên hệ |
| inactive | Boolean |  | Ngừng theo dõi |
| **Thông tin khác** |  |  |  |
| custom\_field\[x\] (x: giá trị số) | Tự định nghĩa |  | Trường tùy chỉnh tự định nghĩa, x là số của trường, ví dụ: custom\_field23 |

      ## 

7. # **Mã lỗi thường gặp** {#mã-lỗi-thường-gặp}

| Mã lỗi | Mô tả | Phương án xử lý |
| ----- | ----- | ----- |
| Exception | Lỗi chưa xác định được nguyên nhân |  |
| InvalidAppID | Lỗi sai AppID (có thể do đang không sử dụng đúng appid do AMIS kế toán cung cấp cho dự án) |  |
| InvalidToken | Lỗi do token không hợp lệ | Lấy lại token |
| ExpiredToken | Lỗi do token đã hết hạn (khi xảy ra lỗi này thì cần phải gọi lại hàm connect để lấy lại token mới nhất) |  |
| InvalidParam | Tham số không hợp lệ |  |
| IsCreatedVoucher | Đã sinh chứng từ kế toán |  |
| VoucherNotFound | Không tìm thấy đề nghị sinh chứng từ kế toán |  |
| DBAmisNotConnectDBACT | Chưa thiết lập kết nối với dữ liệu kế toán nào |  |
| InvalidAccessToken | Lỗi do mã truy cập không hợp lệ |  |
| AppIDDisconnect | Đã ngắt kết nối ứng dụng |  |

### 

### 

   # 