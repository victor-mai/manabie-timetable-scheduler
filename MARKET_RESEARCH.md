# Nghiên cứu thị trường — Giải pháp xếp thời khóa biểu (timetable scheduling)

> Mục đích: trả lời 2 câu — (1) tại Việt Nam đã có những bên nào cung cấp giải pháp này cho nhà trường, (2) trên thế giới có những giải pháp gì.
> Thời điểm khảo sát: 20/08/2026. Tư liệu được trích trực tiếp từ trang chủ / bài viết chính thức (kèm nguồn).

---

## Kết luận nhanh

- **Tại Việt Nam, chắc chắn đã có và đang cạnh tranh sôi động** — không còn là "thị trường trống". Có ít nhất 4–5 tên đáng chú ý, đang truyền thông rầm rộ cụm từ "AI xếp TKB tự động". Một số là sản phẩm độc lập (TKB desktop), một số gắn với nền tảng giáo dục lớn (OLM).
- **Nhu cầu của hiệu trưởng là có thật** và được các bên đánh vào đúng điểm đau: xếp tự động, chỉnh tay kéo-thả, xuất Excel/PDF, gửi email/SMS, công bố lịch lên website.
- **Trên thế giới** bài toán này đã "trưởng thành": có cả sản phẩm thương mại đã tồn tại 30 năm (aSc), hệ sinh thái lớn (Untis/WebUntis), lẫn mã nguồn mở miễn phí uy tín (FET, UniTime).

---

## 1. Thị trường Việt Nam

### Các sản phẩm tiêu biểu (đã xác minh trang chủ/bài viết)

| Sản phẩm | Nền tảng | Điểm nổi bật (theo tư liệu chính thức) | Nguồn |
|---|---|---|---|
| **TKB** (tkb.com.vn) | Desktop Windows, offline | Xếp tự động, **>20 loại ràng buộc** (tiết liên tiếp, nghỉ bù, thực hành…), nhiều màn hình tinh chỉnh (Main Loop, Triple View), xếp 2 buổi sáng–chiều trên 1 khung, gửi email/SMS, xuất Excel/PDF; quảng bá là "AI – Tự động". Rất trưởng thành, bài toán được mô tả đúng là tối ưu hóa tổ hợp (nhánh cận, di truyền, Tabu…) | tkb.com.vn |
| **OLM TKB** (tkb.olm.vn) | Web (cloud), không cài đặt | AI hỗ trợ giảm nhập liệu, xếp tự động, kéo-thả chỉnh sửa, nhân bản/chia sẻ qua link nhanh. Gắn với hệ sinh thái OLM | tkb.olm.vn |
| **FTKB** | Web/cloud, tích hợp AI | "Tự động 100% trong vài phút", hỗ trợ mô hình phổ thông & quốc tế, ghi chú bảo mật và lưu trữ đám mây | RDSIC (đánh giá) |
| **VietSchool** | Web | Xếp online, công khai lịch lên website trường, đa cấp (tiểu học → đại học), phù hợp GV ít kinh nghiệm | vietschool.vn |
| **TKBTUDONG** (thoikhoabieutudong.com) | Web | "Phần mềm xếp TKB tự động" — site thiếu chín (WordPress), mức độ đáng tin cậy thấp hơn các tên trên | thoikhoabieutudong.com |

> Các tên khác được nhắc tới trong bài tổng hợp: **TKB.NET**, **TKB Tự động**.

### Nhận định về cạnh tranh (nguồn: RDSIC + quan sát tư liệu)

- Trường nhỏ (<20 lớp): xu hướng dùng web như **OLM TKB**, **VietSchool** (không cài đặt).
- Trường lớn (>50 lớp) / ràng buộc phức tạp: ưu tiên **TKB desktop** hoặc **FTKB**.
- Phần mềm Việt tính năng đã khá "chuẩn quốc tế" (hard/soft constraints, kéo-thả, xuất báo cáo), **điểm yếu được nhắc nhiều nhất ở bản miễn phí là giới hạn tính năng nâng cao** và cần tinh chỉnh tay sau khi xếp tự động.
- Lưu ý: **DotB (dotb.vn)** — nhà cung cấp nền tảng EdTech liên quan đến phía mình — có *bài viết* giới thiệu "Top 7 TKB", nhưng **không có sản phẩm xếp TKB riêng** trong danh mục (DotB cung cấp EMS/SIS, E-Learning, sổ liên lạc…). → Đây vừa là khoảng trống sản phẩm, vừa là cơ hội nghiên cứu xem có nên thêm module TKB hay không.

---

## 2. Thị trường thế giới

### Thương mại

| Sản phẩm | Quốc gia / tổ chức | Điểm nổi bật (đã xác minh) | Nguồn |
|---|---|---|---|
| **aSc Timetables** | Séc | 30 năm kinh nghiệm, **tăng cường AI**, "trusted by 200,000 schools worldwide", sinh TKB tự động, đa ngôn ngữ, đoạt giải | asctimetables.com |
| **Untis / WebUntis** | Áo (Unit4) | Nền tảng lập TKB (Stundenplanung) cho trường học, có **WebUntis trực tuyến** + app di động, tích hợp **thay thế giáo viên (Vertretungen)**, sổ điểm, giao tiếp với phụ huynh. Phổ biến rộng ở châu Âu | untis.at |

### Mã nguồn mở / miễn phí

| Sản phẩm | Giấy phép | Điểm nổi bật (đã xác minh) | Nguồn |
|---|---|---|---|
| **FET** (Free Timetabling Software) | GNU AGPL v3 | Dành cho trường phổ thông & đại học; **thuật toán hiệu quả, giải TKB phức tạp trong 5–20 phút** (đơn giản vài giây, cực khó vài giờ). Phiên bản mới FET-7.10.1 (20/08/2026). Rất uy tín trong cộng đồng mã nguồn mở | lalescu.ro/liviu/fet |
| **UniTime** | Open source | Hệ thống xếp lịch toàn diện cho **đại học**: course + exam timetabling, student sectioning (chia nhóm SV), quản lý thay đổi; có demo online và mã trên GitHub | unitime.org |

> Tham khảo thêm (well-known, chưa mở lại trang trong lần khảo sát này): **Prime Timetable** & **TimeTabler** (UK, phổ thông), **Tablix** & **OpenTimetable** (open source, web/.NET), nhóm chuyên đại học thương mại như **ASC/Infosilem**, **Scientia Syllabus+**.

### Nhận định quốc tế

- **Hai hướng chính tồn tại song song**: thương mại "trọn gói + hỗ trợ" (aSc, Untis) và mã nguồn mở "miễn phí + linh hoạt, tự triển khai" (FET, UniTime).
- **Xu hướng rõ**: chuyển sang **web/cloud và mobile** (WebUntis), và tích hợp **AI** (aSc quảng bá "AI-enhanced").
- Lõi thuật toán đều dựa trên **constraint satisfaction / tối ưu hóa tổ hợp** — đúng hướng kiến trúc đã đề xuất trong README (dùng constraint solver như OR-Tools, không tự bào).

---

## 3. Ý nghĩa với dự án `manabie-timetable-scheduler`

1. **Thị trường không trống → cần phân biệt định vị.** Nếu chỉ làm công cụ xếp TKB đơn thuần, sẽ đối đầu trực tiếp với TKB, OLM TKB, VietSchool… phải có khác biệt.
2. **Cơ hội rõ nhất là "khoảng trống"**: (a) các sản phẩm Việt phổ biến dùng **AI** để giảm nhập liệu thay vì dùng solver cổ điển — ta có thể tận dụng flow nhập dữ liệu từ phần mềm sổ điểm/CRM (vnEdu, DotB…) để giảm công nhập, (b) chưa thấy ai làm trọn "TKB là module trong hệ sinh thái quản lý trường" sâu sát như hướng của DotB/Manabie.
3. **Kiến trúc đề xuất trong README vẫn đứng vững**: solver constraint (OR-Tools) là đúng chuẩn ngành; thêm vào đó **AI-assisted input** (nhận diện/nhập nhanh dữ liệu, gợi ý ràng buộc) giúp bắt kịp xu hướng cạnh tranh.
4. **Tham khảo trực tiếp 2 mã nguồn mở để chuẩn hóa tính năng**: FET (chuẩn ràng buộc, tốc độ solve) và UniTime (phần đại học/phòng + agent) — tránh làm lại từ số 0 về mô hình dữ liệu.

---

*Doc nghiên cứu thị trường cho dự án xếp thời khóa biểu. Bổ sung định kỳ khi có dữ liệu mới.*