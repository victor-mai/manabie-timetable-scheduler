# ROADMAP — Xây dựng `manabie-timetable-scheduler` (v0)

> Bản đồ tiến hành (plan/PRD) cho việc xây một **app xếp thời khóa biểu cho 1 trường** (có thể nhiều cơ sở/điểm trường), chạy local.
> Căn cứ: README.md (thiết kế), MARKET_RESEARCH (thị trường), OLM_TKB_RESEARCH + TKBDOTCOM_RESEARCH (tính năng & ràng buộc đối thủ).
> Ngôn ngữ: Tiếng Việt.

---

## 1. Mục tiêu & phạm vi

- **Mục tiêu:** một **web app local** mà 1 nhà trường (giáo vụ + BGH) tự chạy trên máy/ít máy để khai báo dữ liệu, cấu hình ràng buộc, **xếp TKB tự động** (solver) + **chỉnh tay**, rồi **xuất Excel/in**.
- **Quy mô:** đúng 1 trường, **hỗ trợ nhiều cơ sở (điểm trường)**. Cấp học: tiểu học → THPT (đặc thù VN: 1 buổi / 2 buổi sáng–chiều, tổ hợp môn, ghép lớp, tiết tránh…).
- **Triết lý bản này:** đúng như đề xuất trước — phân tầng **dữ liệu (import Excel) ≠ luật/ràng buộc (cấu hình form)**; solver dùng OR-Tools chuẩn ngành (không tự bào); hỗ trợ "khối/nhóm → đồng bộ xuống lớp" giống OLM để giảm nhập liệu.

---

## 2. Quyết định phạm vi: MVP trước, nâng cao sau

Từ nghiên cứu 2 đối thủ, mình gom thành **2 mức**:

### MVP (bản chạy được đầu tiên — ưu tiên hàng đầu)
- Khai báo: **khối, lớp, môn (+ký hiệu), giáo viên, tiết+buổi (sáng/chiều), ngày học**.
- **Phân công giảng dạy** (GV–môn–lớp, kèm kiểm tra trùng).
- **Set số tiết** theo khối–môn (kèm cấu hình tiết liên tiếp như `2,1,1`).
- **Ràng buộc cấu hình**: ngày học, buổi học, **tiết nghỉ (thứ+buổi)**, **môn cố định (thứ+tiết)**, **giới hạn số tiết/GV/buổi**, nguyện vọng/ưu tiên GV.
- **Xếp: auto (OR-Tools) + xếp tay (kéo-thả) + tinh chỉnh + tìm xung đột trùng tiết**.
- **Xuất Excel + In (GV/lớp)**. Backup/restore đơn giản.

### Phase nâng cao (sau khi MVP ổn định)
- Tổ hợp môn GDPT 2018 (nhóm lớp), ghép lớp / tách lớp / nhiều GV (khác & cùng tiết), 2 buổi sáng–chiều 1 khung.
- **Đa cơ sở** (gán lớp cho từng cơ sở, GV nhiều cơ sở).
- **Xếp phòng** (môn đặc thù) + dashboard **PCCM** (quá tải/an toàn).
- Công khai TKB theo link, in "toàn trường".

---

## 3. Tech stack & libraries (chốt đề xuất)

| Thành phần | Lựa chọn | Lý do |
|---|---|---|
| **Ngôn ngữ** | Python 3.11+ | Solver + backend một xích, sinh ra cho bài này |
| **Backend framework** | **FastAPI + Uvicorn** | Nhẹ, hiện đại, API + serve static/template tốt |
| **Solver xếp TKB** | **Google OR-Tools (CP-SAT)** | Chuẩn công nghiệp cho timetable; tách bạch hard/soft + trọng số |
| **DB** | **SQLite + SQLAlchemy** | 1 file, 0 cài đặt, kéo đi đâu chạy đó — hợp "1 trường xài local" |
| **Xuất Excel/Import** | **openpyxl** (kèm pandas nếu cần) | Đọc/ghi .xlsx chuẩn, nhà trường quen Excel |
| **Frontend** | Xem mục 5 | Hai phương án: nhanh (server-render) hoặc đẹp (React) |
| **Tooling** | pip/uv, pytest, git, python-dotenv | Phát triển, test, version |

### Dependencies cốt lõi (requirements)
`fastapi`, `uvicorn[standard]`, `or-tools`, `sqlalchemy`, `jinja2`, `python-multipart`, `openpyxl`, `pydantic` (bundle trong FastAPI), `pytest`.

---

## 4. Kiến trúc (tổng quan)

```
Người dùng (giáo vụ/BGH) — trình duyệt
        │  (HTML+JS / hoặc React)
        ▼
FastAPI app (1 process, uvicorn)
 ├─ routes: khai-báo / phan-cong / set-tiet / cau-hinh / ghep-lop ... (xem §3 doc TKB)
 ├─ solver: module OR-Tools CP-SAT (biến, hard/soft, tối ưu)
 ├─ services: validate, counts (khả thi), export excel, import excel
 └─ ORM: SQLAlchemy → SQLite  (1 file)
```

- Thiết kế **API tách rời** (endpoint rõ ràng) để sau có thể đổi frontend lên React mà không đụng logic.
- **Mô hình dữ liệu** gồm: `School`(cơ sở), `Khoi`, `Lop`(→cơ sở), `Mon`, `GiaoVien`, `Tiet`(buổi+lý tự), `NgayHoc`, `PhanCong`, `KhoiMonTiet`(số tiết+phân bổ liên tiếp), `RangBuoc`(ngày/buổi/tiết nghỉ, môn cố định, giới hạn, nguyện vọng).

---

## 5. Frontend — 2 phương án (CẦN BẠN CHỐT)

**Phương án A — Nhanh, 1 process (khuyên cho MVP):**
- **Jinja2** server-side + **Tailwind CSS** + **SortableJS** (kéo-thả ô TKB) / **FullCalendar** tùy chọn. Vanilla JS.
- Ưu: dựng nhanh nhất, không hai tiến trình, đúng đối tượng "1 dev".
- Nhược: UI "động" phức tạp khó hơn code.js.

**Phương án B — Đẹp/chuẩn web-app (bản "hoàn chỉnh"):**
- Tách frontend: **React + Vite + Ant Design** (Table, Select, Calendar) giao tiếp REST API.
- Ưu: giao diện quản trị chuẩn, kéo-thả grid tốt cho màn TKB.
- Nhược: thêm 1 build/2 tiến trình, lâu hơn.

> **Khuyến nghị:** Phương án A để có bản chạy được nhanh; giữ API sạch để sau này nâng lên B khi cần.

---

## 6. Lộ trình 6 phase (deliverable + tiêu chí "xong")

| Phase | Nội dung | Deliverable | "Xong" khi |
|---|---|---|---|
| **0. Khung sườn** | Setup repo, app FastAPI chạy được, SQLite, schema entities, shell trang | App `uvicorn` chạy local, trang trống | `GET /` ra trang, DB tạo được |
| **1. Khai báo dữ liệu** | CRUD khối/lớp/môn/GV/tiết+buổi/ngày học + **import Excel** | Màn nhập liệu + import | Nhập được 1 trường mẫu; xuất được danh sách |
| **2. Phân công + Set tiết** | Phân công GV–môn–lớp (check trùng); Set số tiết khối–môn + phân bổ liên tiếp | Màn phân công + khối–môn–tiết | Phân công + số tiết chuẩn; **chỉ số khả thi** hiển thị |
| **3. Ràng buộc cấu hình** | ngày học, buổi, tiết nghỉ, môn cố định, giới hạn tiết/GV/buổi, nguyện vọng | Form cấu hình theo loại ràng buộc | Xác định được hard/soft; lưu/đổi được |
| **4. Solver + Xếp + Chỉnh tay** | OR-Tools CP-SAT (hard đúng, soft trọng số); **auto xếp**; **màn TKB kéo-thả**; tinh chỉnh; **tìm & thay thế trùng** | Bấm "Auto xếp" → ra TKB; chỉnh tay tô đỏ xung đột | Xếp được TKB 1 trường thật; không vi phạm hard |
| **5. Xuất bản** | Xuất Excel (lớp/GV), in theo mẫu; backup/restore | Nút xuất Excel/in | File Excel mở đúng, đã đủ cột, in được |
| **6. Nâng cao** | Tổ hợp môn, ghép/tách lớp, nhiều GV, 2 buổi, **đa cơ sở**, xếp phòng, PCCM, công khai link | Các module nâng cao | Mỗi module test được với dữ liệu trường mẫu |

> Phase 1–5 là **MVP**; Phase 6 là nâng cao dần theo nhu cầu.

---

## 7. Rủi ro & quyết định cần chốt (để bạn duyệt trước khi code)

1. **Frontend**: Phương án A (nhanh) hay B (đẹp)? *(khuyến nghị A trước)*
2. **Phạm vi MVP**: chỉ làm tới Phase 5 (không phòng/đa cơ sở/PCCM ngay), hay cần ưu tiên đa cơ sở sớm?
3. **Dữ liệu mẫu**: bạn có 1 trường thật (khối/lớp/môn/GV/tiết) để test từ đầu không, hay mình tạo dữ liệu mẫu giả lập 1 trường THPT 2 buổi?
4. **Xếp phòng** có phải ràng buộc bắt buộc ngay không (nhiều trường cần) hay gác lại?

---

## 8. Cách xem bước tiến
- Mỗi phase là 1 **commit** rõ ràng lên `main` (repo: victor-mai/manabie-timetable-scheduler).
- Cập nhật README đánh dấu phase đang làm.
- Sau mỗi phase, minh bạch trạng thái "thật sự chạy được" so với "chỉ code sườn".

*Bản roadmap sơ khởi — sẽ chỉnh theo quyết định của bạn mục 7.*