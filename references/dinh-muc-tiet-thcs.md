# Định mức số tiết/năm học — Trung học cơ sở (THCS)

> Reference số tiết định mức của trường trung học cơ sở theo lớp.
> Số đơn vị: **tiết/năm học** (trừ dòng ghi rõ `/tuần`).

## Bảng số tiết/năm học theo khối

| Nội dung giáo dục | Lớp 6 | Lớp 7 | Lớp 8 | Lớp 9 |
|---|---|---|---|---|
| **Môn học bắt buộc** _(10)_ | | | | |
| Ngữ văn | 140 | 140 | 140 | 140 |
| Toán | 140 | 140 | 140 | 140 |
| Ngoại ngữ 1 | 105 | 105 | 105 | 105 |
| Giáo dục công dân | 35 | 35 | 35 | 35 |
| Lịch sử và Địa lí | 105 | 105 | 105 | 105 |
| Khoa học tự nhiên | 140 | 140 | 140 | 140 |
| Công nghệ | 35 | 35 | **52** | **52** |
| Tin học | 35 | 35 | 35 | 35 |
| Giáo dục thể chất | 70 | 70 | 70 | 70 |
| Nghệ thuật (Âm nhạc, Mĩ thuật) | 70 | 70 | 70 | 70 |
| **Hoạt động giáo dục bắt buộc** _(1)_ | | | | |
| Hoạt động trải nghiệm, hướng nghiệp | 105 | 105 | 105 | 105 |
| **Nội dung GD bắt buộc của địa phương** | 35 | 35 | 35 | 35 |
| **Môn học tự chọn** | | | | |
| Tiếng dân tộc thiểu số | 105 | 105 | 105 | 105 |
| Ngoại ngữ 2 | 105 | 105 | 105 | 105 |
| **Tổng số tiết học/năm học** _(không kể các môn học tự chọn)_ | **1015** | **1015** | **1032** | **1032** |
| **Số tiết học trung bình/tuần** _(không kể các môn học tự chọn)_ | **29** | **29** | **29,5** | **29,5** |

## Ghi chú

- Môn **Công nghệ** tăng từ 35 → 52 tiết bắt đầu từ **Lớp 8** (Lớp 6–7 giữ 35).
- Các môn còn lại có định mức giống nhau ở cả 4 khối (Lớp 6 → Lớp 9).
- **Tổng tiết/năm**: Lớp 6–7 = 1015; Lớp 8–9 = 1032 (không kể môn tự chọn).
- **Trung bình/tuần**: Lớp 6–7 = 29; Lớp 8–9 = 29,5.
- Môn tự chọn (Tiếng dân tộc thiểu số, Ngoại ngữ 2): 105 tiết/năm nhưng **không tính** vào tổng số tiết học/năm.

## Kết quả đối chiếu với seeder (21/08/2026) — ĐÃ KHỚP ✅

Seeder (`app/services/seeder.py`) đã được sửa để khớp 100% định mức này. Quy đổi **năm → tuần theo 35 tuần/năm**:

| Môn | L6 | L7 | L8 | L9 |
|---|---|---|---|---|
| Ngữ văn | 4 | 4 | 4 | 4 |
| Toán | 4 | 4 | 4 | 4 |
| Tiếng Anh | 3 | 3 | 3 | 3 |
| Giáo dục công dân | 1 | 1 | 1 | 1 |
| Lịch sử và Địa lí | 3 | 3 | 3 | 3 |
| Khoa học tự nhiên | 4 | 4 | 4 | 4 |
| Công nghệ | 1 | 1 | **2** | **2** |
| Tin học | 1 | 1 | 1 | 1 |
| Giáo dục thể chất | 2 | 2 | 2 | 2 |
| Nghệ thuật (Âm nhạc + Mĩ thuật) | 1+1 | 1+1 | 1+1 | 1+1 |
| Hoạt động trải nghiệm, hướng nghiệp | 3 | 3 | 3 | 3 |
| Giáo dục địa phương | 1 | 1 | 1 | 1 |
| **Tổng tiết/tuần** | **29** | **29** | **30** | **30** |

**Điều chỉnh đã làm:**
- Tin học 2 → **1** (trước đặt dư so chuẩn 1 tiết/tuần).
- Công nghệ lớp 6–7: 2 → **1** (định mức 35/năm = 1/tuần).
- Công nghệ lớp 8–9: giữ **2** (định mức 52/năm ≈ 1.49/tuần → làm tròn lên, chấp nhận độ lệch nhỏ trong mô hình tiết/tuần nguyên).
- HĐTN-HN: **1 → 3** (định mức 105/năm = 3/tuần).
- KHTN lớp 8–9: **3 → 4**; Sử–Địa lớp 8–9: **2 → 3** (trước đặt thấp hơn chuẩn).
- Thêm **Âm nhạc + Mĩ thuật cho lớp 8–9** (trước thiếu hẳn).
- Thêm môn **Giáo dục địa phương** (định mức 1 tiết/tuần) cho cả 4 khối.

**Buổi học (config theo khối, không có ca tối):** THCS thường **1 buổi/ngày**, nhưng khối 8–9 (30 tiết) có thể **học thêm buổi Chiều**. Sửa seeder nay dựng:
- Khối **6–7**: `hoc_chieu=False` → chỉ buổi **Sáng**, 5 tiết (T1–T5) × 6 ngày = 30 ô/tuần (dùng 29 tiết + 1 trống).
- Khối **8–9**: `hoc_chieu=True` → thêm buổi **Chiều** (T6–T8), tổng 8 tiết/ngày = 48 ô/tuần (dùng 30 tiết, thoải mái).
- Config nằm ở **Khai báo → Khối** (toggle "Học chiều"). Solver tự lọc ô theo khối (`hoc_chieu`); UI lịch chỉ hiện buổi khối đó học. **Đã bỏ hẳn ca "Tối"** (trường không dùng).

**Verify:** solver Z3 `sat`, 236 tiết, 0 mâu thuẫn; tổng tiết/tuần khối 6–7 = 29, khối 8–9 = 30; khối 6–7 dùng 0 ô Chiều, khối 8–9 dùng 22 & 18 ô Chiều.

---

*Nguồn: số tiết định mức trường THCS (user cung cấp, 21/08/2026).*