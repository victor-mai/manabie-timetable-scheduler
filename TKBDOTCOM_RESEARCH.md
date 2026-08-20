# Nghiên cứu sâu: TKB (tkb.com.vn) — Phần mềm xếp TKB trưởng thành nhất VN (desktop/web)

> Nghiên cứu qua giao diện **admin** (`tkb.com.vn/admin/`) bằng session `PHPSESSID` do người dùng cấp, đúng ngày 20/08/2026.
> Mục tiêu: **liệt kê các tính năng cần build** và **lộ trình/flow xếp thời khóa biểu**, làm đối chiếu để xây `manabie-timetable-scheduler`.
> Lưu ý minh bạch: khảo sát bằng HTTP (curl) với cookie; các màn hình tương tác (kéo-thả, auto-solve) render bằng JS nên phần mô tả của chúng dựa vào tham số/khung chức năng hiển thị, chưa click trực tiếp.

---

## 1. Vị thế

- tkb.com.vn là một trong những phần mềm xếp TKB **được dùng lâu và nhiều nhất ở VN**, có bản **desktop (Windows)** và **bản online (web)**.
- Giao diện admin đầy đủ module, kèm **27 video hướng dẫn**, bán kèm **hỗ trợ Zalo trực tiếp** (0347.113.012).
- Đánh giá chung: mạnh về **độ chi tiết ràng buộc + công cụ tinh chỉnh + in ấn/báo cáo**, phủ mọi cấp học (tiểu học → THPT, thêm bồi dưỡng văn hóa).

---

## 2. Toàn bộ feature map (menu admin)

| Nhóm | Module / Chức năng |
|---|---|
| **Khai báo** | Khối, Lớp học, Tiết học, Môn học, Giáo viên |
| **Xếp lịch** | Giáo viên chủ nhiệm, Phân công giảng dạy, Khối–Môn–Số tiết, **Phân tích PCCM** (mới), **AI TKB** (mới), Xếp thời khoá biểu |
| **Cấu hình** | Set cơ sở, Set buổi học, Set ngày học, Set tiết nghỉ, Môn cố định, **Giới hạn số tiết**, **Giới hạn số lớp** |
| **Ghép lớp** | Chọn lớp, TKB ghép lớp |
| **Tách lớp** | Chọn lớp, TKB tách lớp |
| **Xuất/In** | Xuất Excel TKB; In TKB (Học sinh / Giáo viên); Công khai TKB (HS / GV / Toàn trường / Đổi link) |
| **Backup** | Sao lưu, Khôi phục, Làm mới |
| **Xếp phòng** | Phòng, Sắp xếp |
| **Khác** | Gia hạn tài khoản, Tài khoản, Thoát |

→ Đây gần như là **danh sách "tính năng tối thiểu để cạnh tranh"** ở phân khúc phần mềm xếp TKB VN chuyên sâu.

---

## 3. Flow xếp thời khóa biểu (luồng nghiệp vụ chính thức)

Hệ thống đóng khung thành **8 bước** và **6 giai đoạn**:

### 8 bước xếp TKB
1. **Khai báo khối** — danh sách khối lớp
2. **Khai báo lớp** — danh sách lớp theo từng khối
3. **Khai báo tiết học** — số tiết + **khung thời gian các buổi sáng/chiều**
4. **Khai báo môn học** — danh mục môn + ký hiệu viết tắt
5. **Khai báo giáo viên** — danh sách GV + tên viết tắt
6. **Chủ nhiệm lớp** — phân GVCN cho từng lớp
7. **Phân công giảng dạy** — gán GV dạy từng môn cho từng lớp
8. **Set số tiết** — số tiết theo chương trình GDPT của từng khối/môn

→ Tiếp theo là **Xếp TKB** (bước 9) và **Cấu hình ràng buộc**.

### 6 giai đoạn
1. **Khai báo** (dữ liệu)
2. **Phân công** (GVCN, phân công môn, khối–môn–tiết)
3. **Xếp TKB** (xếp tay / xếp auto / AI)
4. **Cấu hình** (rát buộc: ngày, buổi, tiết nghỉ, môn cố định, giới hạn…)
5. **Sao lưu** (backup–restore–làm mới)
6. **In ấn / Xuất bản** (Excel, in GV/HS/toàn trường, công khai link)

---

## 4. Mô hình dữ liệu (các thực thể)

- **Khối** (khoi): khối lớp.
- **Lớp học** (lop): thuộc khối, gán **cơ sở**.
- **Tiết học** (tiet): cấu trúc `$ten [$viewbuoi]` → tiết gắn buổi (Sáng/Chiều/Tối). Lưu theo thứ tự (`data-tiet-seq`).
- **Môn học** (mon-hoc): tên + **ký hiệu viết tắt**, có **môn cố định** (tiet-co-dinh).
- **Giáo viên** (giao-vien): tên + viết tắt, đơn vị (khoa/tổ), có **nguyện vọng/lịch bận**.
- **GVCN** (chu-nhiem-lop): liên kết GV–lớp.
- **Phân công giảng dạy** (phan-cong-giang-day): khối–môn–lớp–GV.
- **Khối–Môn–Số tiết** (khoi-mon-tiet): số tiết quy định/tuần theo khối.
- **Cơ sở** (set-co-so): CS1–CS6, **gán lớp cho từng cơ sở** → đa điểm trường.
- **Phòng** (phong): phòng học, dùng cho Xếp phòng.

---

## 5. Hệ thống ràng buộc (cấu hình) — các loại phát hiện

| Ràng buộc | Nguồn (trang) | Ý nghĩa |
|---|---|---|
| **Ngày học** | set-ngay-hoc | Bật/tắt ngày học toàn trường: Thứ 2 → Chủ nhật |
| **Buổi học** | set-buoi-hoc | **Sáng / Chiều / Tối** (tới 3 buổi/ngày) |
| **Tiết nghỉ** | set-ngay-nghi | Khóa tiết theo **thứ + buổi** (không xếp vào) |
| **Môn cố định** | tiet-co-dinh | Khóa 1 môn vào **thứ + tiết** nhất định |
| **Giới hạn số tiết dạy** | gioi-han-so-tiet-day | **Số tiết tối đa mỗi buổi cho 1 GV** (title: "…cho 1 GV / buổi") |
| **Giới hạn số lớp** | mon-hoc/gioi-han | **Số lớp tối đa học cùng lúc 1 môn** (cho môn đặc thù, phòng hạn chế) |
| **Nguyện vọng GV** | (video 'Nguyện vọng giáo viên') | Lịch bận, nguyện vọng nghỉ dạy của từng GV |
| **Ưu tiên GV** | (video 'Xếp ưu tiên GV') | Ưu tiên lịch cho BGH, GV con nhỏ… (soft) |
| **Cấu hình phân bổ tiết** | (GTVT 2018, trong 'Set số tiết') | Số tiết/tuần môn theo khối, tiết liên tiếp |
| **2 buổi sáng/chiều** | (video 'Xếp TKB 2 buổi') | Trường học cả ngày sáng + chiều |

→ Điểm khác biệt so với OLM: tkb.com.vn tách rõ **"Giới hạn số tiết (theo GV/buổi)"** và **"Giới hạn số lớp/1 tiết"** thành các trang ràng buộc riêng, quản lý phòng & cơ sở đa điểm trường rõ ràng.

---

## 6. Công cụ xếp lịch (scheduling engine)

- **Xếp tay (click)**: kéo-thả / click chọn tiết trực quan, **gợi ý thông minh**.
- **Xếp auto**: màn hình TKB có tham số **Auto**, lọc **Trường/Lớp**, **Số môn / buổi**, **Chọn môn** → thuật toán tự động xếp nhanh toàn bộ lớp.
- **AI TKB**: tính năng mới (dùng AI hỗ trợ xếp/tối ưu).
- **Trợ lý TKB**: hệ thống gợi ý + trợ lý xếp thông minh.
- **Tinh chỉnh TKB**: thao tác chỉnh chi tiết sau khi auto.
- **Tìm & thay thế tiết trùng**: tự động tìm và giải quyết **xung đột tiết trùng**.

### Luồng xếp cụ thể (suy ra từ UI/flow)
```
Khai báo nền (khối, lớp, tiết+buổi, môn, GV)
  → GVCN → Phân công giảng dạy → Set số tiết (khối–môn–tiết)
  → Cấu hình ràng buộc (ngày/buổi/tiết nghỉ/môn cố định/giới hạn/ưu tiên)
  → XÉP TKB: chọn lọc (buổi, môn) → Auto / AI / Xếp tay
  → Tinh chỉnh (kéo-thả, tìm trùng, trợ lý)
  → Kiểm tra PCCM (quá tải/an toàn/nhiều cơ sở)
  → Xuất Excel / In / Công khai / Backup
```

---

## 7. Tính năng xử lý nghiệp vụ nâng cao (đặc thù VN)

- **Ghép lớp**: chọn lớp; nhiều lớp học chung 1 môn/1 GV trong 1 tiết.
- **Tách lớp**: 1 lớp thành nhiều nhóm học các môn khác nhau cùng giờ.
- **Nhiều GV dạy 1 lớp – khác tiết**: môn trong 1 lớp do nhiều GV, xếp khác tiết.
- **Nhiều GV dạy 1 lớp – cùng tiết (đồng giảng)**: nhiều GV cùng đứng lớp 1 tiết (vd cô Việt + GV ngoại ngữ).
- **2 buổi sáng/chiều**: xử lý trường học cả ngày.

---

## 8. Phân tích phân công chuyên môn (PCCM) — tính năng "kiểm định khả thi"

Phân tích PCCM là **dashboard kiểm tra chất lượng phân công trước khi xếp** rất đáng tham khảo:

| Chỉ số | Ý nghĩa |
|---|---|
| Tổng GV / Đã phân công | Tỷ lệ GV chưa được phân công |
| **Quá tải** | GV vượt quá số tiết có thể dạy → phải "xếp đè" vào tiết xin nghỉ |
| **Nhiều cơ sở** | GV dạy từ 2 cơ sở trở lên, gần kín lịch |
| **An toàn** | Phân công cân đối, xếp lịch thuận lợi |

Bảng chi tiết từng GV: **Môn đảm nhiệm · Tổng tiết · Quỹ tối đa · Số tiết nghỉ · Quỹ khả dụng · Tải công suất · Cơ sở · Trạng thái · Thao tác**
→ Cho phép phát hiện sớm ràng buộc "quá tải" (không thể tồn tại lời giải) — đúng tinh thần hard/soft feasibility trong README.

---

## 9. Đa cơ sở (điểm trường) & Xếp phòng

- **Set cơ sở**: hệ thống hỗ trợ **nhiều cơ sở (CS1–CS6)**; bước 1 chọn cơ sở đang dùng, bước 2 **gán lớp học cho từng cơ sở**. → quản lý trường liên cấp/nhiều điểm trường.
- **Phòng & Xếp phòng**: khai báo phòng, sau đó **sắp xếp phòng** (cho môn cần phòng đặc thù như thể dục, thí nghiệm, ngoại khóa).

---

## 10. Đối chiếu & ý nghĩa cho dự án `manabie-timetable-scheduler`

### Tính năng "phải có" để cạnh tranh (kế thừa từ cả OLM + TKB)
1. **Khai báo đầy đủ thực thể** (khối, lớp, tiết+buổi, môn+ký hiệu, GV+viết tắt).
2. **Phân công giảng dạy** kèm **kiểm tra trùng lặp / xóa dư thừa / import nhanh**.
3. **Set số tiết theo khối–môn** (GFGDPT) + **cấu hình phân bổ tiết liên tiếp**.
4. **Hệ ràng buộc cấu hình** tách riêng từng loại: ngày học, buổi (sáng/chiều/tối), tiết nghỉ, môn cố định, giới hạn số tiết/buổi/GV, giới hạn số lớp/1 tiết, nguyện vọng + ưu tiên GV.
5. **3 chế độ xếp**: xếp tay (kéo-thả + gợi ý), xếp auto (solver), **AI/trợ lý gợi ý**.
6. **Công cụ tinh chỉnh + tìm-thay thế xung đột trùng tiết**.
7. **Ghép lớp / tách lớp / nhiều GV (khác & cùng tiết)**.
8. **Xuất Excel + In (GV/HS/toàn trường) + Công khai link + Backup/Restore**.
9. **Dashboard kiểm định PCCM** (quá tải / an toàn / nhiều cơ sở) — điểm hay ít nơi làm.
10. **Đa cơ sở** (nhiều điểm trường) + **Xếp phòng** (môn đặc thù).

### Điểm ta có thể làm khác / vượt trội
- **Nhập liệu từ dữ liệu sổ điểm/CRM** (vnEdu, hệ sinh thái DotB/Manabie) để bỏ xong công nhập hộ tốn nhất — OLM/TKB vẫn bắt nhập tay (dù có "import nhanh").
- **Local/offline** (theo README) ngược lại với cloud bắt buộc của OLM; vừa offline vừa có bản online khi cần.
- **UX hiện đại** hơn (cả hai đều có giao diện hơi cũ; tkb.com.vn mang phong cách desktop/quản trị cổ điển).
- Về **solver**: dùng **OR-Tools (CP-SAT)** chuẩn, hỗ trợ rõ hard/soft + trọng số, thay vì giải thuật di truyền/tabu thủ công — kiểm soát "quá tải" và trọng số ưu tiên tốt hơn.

---

## 11. Tài nguyên tham chiếu
- Giao diện admin: `tkb.com.vn/admin/` (các trang: khoi, lop, tiet, mon-hoc, giao-vien, chu-nhiem-lop, phan-cong-giang-day, khoi-mon-tiet, phan-tich-phan-cong-chuyen-mon, set-co-so, set-buoi-hoc, set-ngay-hoc, set-ngay-nghi, tiet-co-dinh, gioi-han-so-tiet-day, mon-hoc/gioi-han, thoi-khoa-bieu, tkb-ghep-lop, tkb-tach-lop, export-file, in-thoi-khoa-bieu-*, backup-tkb, restore-tkb, reset-thoi-khoa-bieu, phong, xep-phong, gia-han-tai-khoan).
- 27 video hướng dẫn chia theo 6 giai đoạn và các tính năng đặc thù.

---

*Tài liệu nghiên cứu TKB (tkb.com.vn) phục vụ việc liệt kê tính năng cần build và chuẩn hóa flow xếp TKB cho dự án. Bổ sung khi khảo sát tương tác trực tiếp hoặc kiểm chứng thêm.*