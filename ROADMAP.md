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
| **UI/Backend** | **Streamlit** | Thuần Python, dựng CRUD/form/bảng cực nhanh, tự mở trình duyệt local — hợp "1 dev + mở local" |
| **Solver xếp TKB** | **Google OR-Tools (CP-SAT)** | Chuẩn công nghiệp cho timetable; tách bạch hard/soft + trọng số |
| **DB / lưu trữ** | **SQLite** (1 file `.sqlite`) + SQLAlchemy | Chính là nguồn lưu trữ; **xuất/load lại bằng cách download/upload file này** |
| **Xuất Excel/Import** | **openpyxl** | Đọc/ghi .xlsx, nhà trường quen Excel; song song với file SQLite |
| **Phân phối local** | **PyInstaller** → thư mục + `run.exe`, nén ZIP | Trường giải nén chạy exe, **không cần cài Python**; đóng gói cần hidden-import cho OR-Tools |
| **Tooling** | uv/pip, pytest, git | Phát triển, test, version |

### Dependencies cốt lõi (requirements)
`streamlit`, `or-tools`, `sqlalchemy`, `openpyxl`, `python-multipart`, `pandas`, `pytest`, `pyinstaller` (lúc đóng gói).

---

## 4. Kiến trúc (tổng quan)

```
Người dùng (giáo vụ/BGH) — trình duyệt
        │
        ▼
Streamlit app (1 process, `streamlit run app.py` / `run.exe`)
 ├─ pages theo chức năng: khai-báo / phan-cong / set-tiet / cau-hinh / xep-tkb / xuat-ban (xem §3 doc TKB)
 ├─ solver: module OR-Tools CP-SAT (biến, hard/soft, tối ưu)
 ├─ services: validate, khả thi (PCCM), import/export Excel
 └─ ORM: SQLAlchemy → SQLite  (1 file `data.sqlite` — xuất/import được)
```

- Thiết kế **tách logic nghiệp vụ + solver thành module riêng** (không nhét vào UI) để dễ test và, nếu sau cần UI đẹp hơn, gắn bằng Streamlit component hoặc tách frontend.
- **Mô hình dữ liệu** gồm: `Truong`(cơ sở), `Khoi`, `Lop`(→cơ sở), `Mon`, `GiaoVien`, `Tiet`(buổi+lý tự), `NgayHoc`, `PhanCong`, `KhoiMonTiet`(số tiết+phân bổ liên tiếp), `RangBuoc`(ngày/buổi/tiết nghỉ, môn cố định, giới hạn, nguyện vọng).

---

## 5. Frontend & Phân phối — chốt theo nguyện vọng "trường tự mở local"

### 5.1 UI — **Streamlit** (khuyên dùng cho MVP)
- Thuần Python: sidebar-nav, `st.form` (nhập liệu), `st.dataframe`/`st.data_editor` (bảng), `st.file_uploader` (import), `st.download_button` (xuất), `st.progress` (chạy solver).
- Chạy `streamlit run app.py` là có ngay, tự mở trình duyệt localhost.
- **Giới hạn đã thừa nhận**: thao tác **kéo-thả ô TKB không native**. Xếp tay MVP dùng **`st.data_editor`** (chọn môn từng ô) + **nút kiểm tra xung đột**. Có thể nâng bằng Streamlit component tuỳ biến nếu trường cần drag-drop thật.

### 5.2 Phân phối — **ZIP chứa thư mục + `run.exe`** (PyInstaller)
- Đóng `app.py` + UI + môi trường → thư mục chạy được → nén ZIP.
- Trường: **giải nén → double-click `run.exe`/`.bat`** → trình duyệt tự mở. **Không cần cài Python.**
- Dòng `run` giúp chọn file dữ liệu, mở đúng port, log lỗi ra file.

### 5.3 Lưu trữ & di dời dữ liệu (đúng mong muốn "file SQLite")
- App đọc/ghi **1 file `data.sqlite`** (mặc định trong thư mục app; có thể chọn đường dẫn khác).
- **Xuất để lưu trữ**: nút *Tải dữ liệu (SQLite)* → download `data.sqlite`; option tự backup theo ngày.
- **Load lại khi cần**: nút *Tải lên / chọn file SQLite* → app mở file đó làm CSDL.
- **Excel** song song: xuất từng bảng / toàn TKB (openpyxl); import dữ liệu nền từ Excel lần đầu.
- Nhờ đó: mang thư mục (hoặc chỉ file `.sqlite`) đi đâu cũng mở lại được, không mất dữ liệu.

---

## 6. Lộ trình 6 phase (deliverable + tiêu chí "xong")

| Phase | Nội dung | Deliverable | "Xong" khi |
|---|---|---|---|
| **0. Khung sườn** | Init repo, Streamlit app chạy được, schema SQLite entities, shell trang + nav | App `streamlit run app.py` mở local, shell các trang | Mở được app, DB `data.sqlite` tự tạo |
| **1. Khai báo dữ liệu** | CRUD khối/lớp/môn/GV/tiết+buổi/ngày học + **import Excel** | Màn nhập liệu + import | Nhập được 1 trường mẫu; xuất danh sách ra Excel |
| **2. Phân công + Set tiết** | Phân công GV–môn–lớp (check trùng); Set số tiết khối–môn + phân bổ liên tiếp | Màn phân công + khối–môn–tiết | Phân công + số tiết chuẩn; **chỉ số khả thi** hiển thị |
| **3. Ràng buộc cấu hình** | ngày học, buổi, tiết nghỉ, môn cố định, giới hạn tiết/GV/buổi, nguyện vọng | Form cấu hình theo loại ràng buộc | Xác định được hard/soft; lưu/đổi được |
| **4. Solver + Xếp + Chỉnh tay** | OR-Tools CP-SAT (hard đúng, soft trọng số); **auto xếp**; **màn TKB kéo-thả**; tinh chỉnh; **tìm & thay thế trùng** | Bấm "Auto xếp" → ra TKB; chỉnh tay tô đỏ xung đột | Xếp được TKB 1 trường thật; không vi phạm hard |
| **5. Xuất bản + Phân phối** | Xuất Excel (lớp/GV), in theo mẫu; **Xuất/Load lại file `data.sqlite`**; backup/restore; **đóng gói PyInstaller → ZIP "mở local"** | Nút xuất Excel + tải/lưu file SQLite; file ZIP trường chạy được | File Excel mở đúng; đổi `data.sqlite` là đổi dữ liệu; trường chạy được `run.exe` không cần Python |
| **6. Nâng cao** | Tổ hợp môn, ghép/tách lớp, nhiều GV, 2 buổi, **đa cơ sở**, xếp phòng, PCCM, công khai link | Các module nâng cao | Mỗi module test được với dữ liệu trường mẫu |

> Phase 1–5 là **MVP**; Phase 6 là nâng cao dần theo nhu cầu.

---

## 7. Rủi ro & quyết định cần chốt (để bạn duyệt trước khi code)

1. ✅ **UI**: đã chốt **Streamlit** cho MVP (mở local + file SQLite như bạn yêu cầu). Còn 1 điểm cần xác nhận: xếp tay MVP bằng `st.data_editor` (chọn môn từng ô) — **bạn có chấp nhận tạm thời chưa có kéo-thả mượt** không? (nâng drag-drop thật là Phase 6/component).
2. **Phạm vi MVP**: chỉ làm tới Phase 5 (không phòng/đa cơ sở/PCCM ngay), hay cần ưu tiên đa cơ sở sớm?
3. **Dữ liệu mẫu**: bạn có 1 trường thật (khối/lớp/môn/GV/tiết) để test từ đầu không, hay mình tạo dữ liệu mẫu giả lập 1 trường THPT 2 buổi?
4. **Xếp phòng** có phải ràng buộc bắt buộc ngay không (nhiều trường cần) hay gác lại?

---

## 8. Cách xem bước tiến
- Mỗi phase là 1 **commit** rõ ràng lên `main` (repo: victor-mai/manabie-timetable-scheduler).
- Cập nhật README đánh dấu phase đang làm.
- Sau mỗi phase, minh bạch trạng thái "thật sự chạy được" so với "chỉ code sườn".

*Bản roadmap sơ khởi — sẽ chỉnh theo quyết định của bạn mục 7.*