# Nghiên cứu sâu: OLM TKB — phần mềm xếp thời khóa biểu online

> Trang nghiên cứu: [https://tkb.olm.vn](https://tkb.olm.vn) (+ trung tâm trợ giúp & FAQ trong cùng tên miền).
> Thời điểm khảo sát: 20/08/2026. Tất cả điểm trình bày dưới đây được trích từ trang chủ / trang hướng dẫn / bài FAQ chính thức của OLM TKB.
> Mục tiêu: nắm được **mô hình dữ liệu & hệ thống ràng buộc (constraints)** mà OLM TKB dùng cho thời khóa biểu Việt Nam (1 buổi/2 buổi, sáng–chiều, số tiết, tiết tránh…), làm tham chiếu cho dự án `manabie-timetable-scheduler`.

---

## 1. Vị thế & mô hình sản phẩm

- **Online, không cần cài đặt**: chạy trên trình duyệt (Chrome), nền OLM cloud; phù hợp TH, THCS, THPT, liên cấp, trung tâm bồi dưỡng văn hóa.
- **Định vị marketing**: "Giảm thiểu tối đa thao tác nhập liệu", "Xếp tự động sử dụng trí tuệ nhân tạo (AI)", "Thỏa mãn nhiều loại ràng buộc", "Công cụ chỉnh sửa, xem TKB trực quan", "Chia sẻ, copy, nhân bản đơn giản", "Chạy online, không cần cài đặt".
- **Đơn vị vận hành**: Công ty Cổ phần Khoa học và Công nghệ Giáo dục (MST 0106303886) — hệ sinh thái OLM.VN. (Video hướng dẫn gắn nhãn "OLM TKB SVIP", ám chỉ có gói trả phí SVIP.)
- **Hỗ trợ trực tiếp**: SĐT/Zalo (thầy Hoàn 0915343532, thầy Hùng 0985328866), có nhóm Zalo hỗ trợ xếp TKB — bán kèm **dịch vụ hỗ trợ con người**, đây là lợi thế bán hàng của họ.

### Các "loại hình thời khóa biểu" OLM TKB hỗ trợ (đặc thù VN)
1. **1 buổi hoặc 2 buổi** (học sáng, học sáng–chiều)
2. **Chính khóa hoặc tăng cường** (lớp bồi dưỡng/khích thêm ngoài giờ chính)
3. **Các môn tổ hợp** (GDPT 2018: khối 10–12 chọn tổ hợp KHTN / KHXH…)
4. **Tiết ghép lớp** (1 GV dạy đồng thời nhiều lớp) **và ghép giáo viên** (nhiều GV cùng dạy chung 1 tiết/môn)

Họ cung cấp sẵn **6 mẫu TKB** để dùng thử không cần nhập liệu: THPT (2 buổi), THPT (1 buổi), THCS (2 buổi) ×2, THCS (1 buổi), Tiểu học (2 buổi).

---

## 2. Quy trình xếp TKB (8 bước) — chính là "mô hình dữ liệu" theo kiểu OLM

| Bước | Tên | Nội dung -> tương đương khái niệm |
|---|---|---|
| 1 | **Khởi tạo** | Cấu hình chung: **số ngày học/tuần, số buổi/ngày (1 hay 2), số tiết học** ("hạn chế thay đổi khi đã xếp") → *khung thời gian* |
| 2 | **Thêm môn học** | Nhập tên rút gọn; **không đặt quá nhiều tiết tránh** → *danh mục môn* |
| 3 | **Tổ chuyên môn** | Đặt **số tiết học của cả tổ** → *nhóm GV* |
| 4 | **Giáo viên** | Đặt **số tiết/ngày**, **số ngày nghỉ/tiết tránh** của từng GV → *ràng buộc GV* |
| 5 | **Danh sách khối/nhóm** | Tạo khối hoặc **nhóm lớp có cùng khung chương trình**; đặt **tiết nghỉ cho toàn khối** nếu cần → *khung CT chuẩn* |
| 6 | **Danh sách lớp** | Điều chỉnh chương trình từng lớp dựa trên khối; **đảm bảo số tiết chương trình ≤ số tiết trống** → *đồng bộ khung CT xuống lớp* |
| 7 | **Phân công giảng dạy** | Gán GV cho môn-lớp; **kiểm tra số tiết/GV/tuần không vượt quy định** → *phân công* |
| 8 | **Tinh chỉnh thủ công** | Đặt tiết cần sửa ra ngoài, xếp lại bằng **công cụ trực quan** → *chỉnh tay + solver lại* |

Đây là phát hiện đáng giá: **OLM xây dựng mô hình quanh khái niệm "Khung chương trình (Khung CT)" theo khối/nhóm rồi đồng bộ xuống lớp**, giúp giảm nhập liệu khi nhiều lớp giống nhau — đúng bài toán tổ hợp khối ở VN.

---

## 3. Hệ thống ràng buộc (constraints) — các loại tìm thấy

Tổng hợp từ trang chủ (8 bước) + FAQ chính thức:

### Ràng buộc về THỜI GIAN / KHUNG GIỜ
- **Số ngày học / tuần, số buổi / ngày (1 buổi hoặc 2 buổi sáng–chiều), số tiết / buổi** — cấu hình ở Bước 1.
- **Xếp TKB sáng + chiều**: FAQ cho 2 cách:
  - Cách 1: tạo **2 TKB riêng** (sáng, chiều), dùng **nhân bản TKB** để giảm nhập.
  - Cách 2: tạo **1 TKB cho 2 buổi** bằng cách chọn "2 buổi/ngày" ở Bước 1; nếu một môn phân rõ sáng/chiều bao nhiêu tiết thì **tách thành 2 môn** (vd *Toán-Sáng* 4 tiết, *Toán-Chiều* 2 tiết).

### Ràng buộc về MÔN / KHUNG CT
- **Số tiết/tuần của mỗi môn** theo khối/nhóm (Khung CT).
- **Tiết tối đa liên tiếp** của một môn (vd đặt = 1 để không dồn).
- **Cấu hình phân bổ tiết liên tiếp** dạng danh sách: FAQ ví dụ *Toán 4 tiết -> nhập `2,1,1`* nghĩa là 1 buổi 2 tiết liền + 2 buổi mỗi buổi 1 tiết. → Đây là ràng buộc phân bố tiết rất Việt Nam, cần hỗ trợ.
- **Tổ hợp môn khác nhau trong khối** (GDPT 2018): tạo **nhóm lớp** cùng "khung chương trình (số môn + tiết/tuần)" – vd nhóm 10KHTN (10A,B,C), 10KHXH (10D,E), đồng bộ khung CT xuống lớp.

### Ràng buộc về GIÁO VIÊN
- **Số tiết/ngày**, **số tiết/tuần** tối đa.
- **Ngày nghỉ**, **tiết tránh** (unavailable periods) cho từng GV (Bước 4).
- **Nhiều GV cùng dạy một môn** (KHTN 3 GV, Lịch sử–Địa lý 2 GV, Tiếng Anh 2 GV: 1 Việt + 1 ngoại ngữ) — mỗi GV dạy một phần tiết của môn đó.
- **Một GV dạy nhiều lớp ghép** (Tổng phụ trách dạy Hoạt động trải nghiệm cả khối cùng thời điểm), **GV dạy ghép 2+ lớp**.

### Ràng buộc về KHẢ THI / chất lượng lời giải (quan trọng!)
- Lưu ý chính thức: để auto-xếp kín, **không phân quá nhiều GV dạy 1 lớp nghỉ/tránh cùng ngày/tiết; không để quá nhiều GV của trường cùng nghỉ 1 ngày.** → thể hiện đây là bài toán **hard ràng buộc khiến thuật toán bế tắc**, cần kiểm soát mật độ ràng buộc (đúng như phân tích hard/soft trong README).
- Khi vẫn còn tiết chưa xếp -> dùng **tinh chỉnh thủ công trực quan**.

### Điều OLM TKB KHÔNG nhấn mạnh trong tài liệu công khai
- **Phòng học/phòng bộ môn dùng chung** gần như không được nhắc trong trang công khai — khác với TKB (desktop của tkb.com.vn) vốn liệt kê phòng. → Cần kiểm chứng thực tế khi so sánh: nếu trường có Phòng Bộ Môn/Câu lạc bộ/Lớp bán trú, "1 phòng không trùng 2 lớp" vẫn là ràng buộc cứng cần có.

---

## 4. Đánh giá công nghệ & cách làm

- **Thuật toán**: xếp tự động dùng "AI" (theo họ tự giới thiệu); quan trọng là **hỗ trợ xếp thủ công trước, xếp tự động sau, rồi chỉnh tay** — tức hiểu đúng bản chất "máy gợi ý + người tinh chỉnh", không phải một cú "bấm là xong".
- **Nhập liệu**: tinh giản theo khối/nhóm + đồng bộ + nhân bản → tối ưu cho trường nhiều lớp giống nhau.
- **Không đặt phòng**: mô hình xoay quanh **thời gian × lớp × môn × GV** + khung CT; "lớp" là nút chính (khác hướng "phòng-trung-tâm" của các hệ thống đại học).
- **Gói/giá**: xuất hiện nhãn **SVIP** (gói cao cấp trả phí) bên cạnh trải nghiệm miễn phí — mô hình freemium.

---

## 5. Ý nghĩa & khác biệt cho dự án `manabie-timetable-scheduler`

1. **Xác nhận trọng tâm ràng buộc Việt Nam** cần hỗ trợ tối thiểu (để cạnh tranh được):
   - 1 buổi / 2 buổi (sáng–chiều), số ngày/tuần, số tiết/buổi;
   - Khung CT theo **khối/nhóm** rồi đồng bộ xuống lớp (tổ hợp GDPT 2018);
   - **Số tiết/tuần, tiết tối đa liên tiếp, cấu hình phân bổ** (vd `2,1,1`);
   - Ngày nghỉ / **tiết tránh** của GV; số tiết tối đa/ngày, /tuần của GV;
   - **Nhiều GV 1 môn**, **1 GV dạy ghép nhiều lớp**, ghép GV cùng tiết;
   - Kiểm soát mật độ ràng buộc để đảm bảo tồn tại lời giải.
2. **Điểm có thể tạo khác biệt** đối thủ chưa làm mạnh:
   - **Nhập liệu trực tiếp từ dữ liệu sổ điểm/CRM sẵn có** (vnEdu, hệ sinh thái DotB/Manabie) để bỏ xong công nhập hộ tốn sức nhất — đúng đúng nỗi đau "nhập liệu".
   - **Xử lý phòng bộ môn/phòng chức năng** nếu hướng tới trường có cơ sở trải rộng.
   - Gói **offline/local** (như README đã đề xuất) — phân khúc ngược lại với OLM (cloud bắt buộc).
3. **Kiến trúc tái khẳng định**: mô hình quanh "Khung CT + nhóm lớp + ràng buộc GV/thời gian" là hợp lý và khớp với phần đề xuất trước đó; có thể bổ sung khái niệm **"khoảng nghỉ/tiết tránh"** và **"cấu hình phân bổ tiết liên tiếp"** như hạng ràng buộc riêng.

---

*Tài liệu nghiên cứu OLM TKB phục vụ việc thiết kế chuẩn ràng buộc TKB Việt Nam cho dự án. Bổ sung khi có dữ liệu mới / kiểm chứng thêm.*