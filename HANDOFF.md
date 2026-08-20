# HANDOFF — manabie-timetable-scheduler

> Đọc tài liệu này ĐẦU TIÊN khi tiếp tục. Cập nhật khi có thay đổi trạng thái.
> Repo: `E:\Python Projects\manabie-timetable-scheduler` · GitHub: `victor-mai/manabie-timetable-scheduler` (public, nhánh `main`).

---

## 1. Mục tiêu
App xếp **thời khóa biểu toàn trường** (1 trường, có thể nhiều cơ sở), **mở local**, lưu bằng **1 file `.sqlite`** (xuất/load lại được). Nghiên cứu thị trường + 2 đối thủ (OLM TKB, tkb.com.vn) nằm trong `MARKET_RESEARCH.md`, `OLM_TKB_RESEARCH.md`, `TKBDOTCOM_RESEARCH.md`. Thiết kế & lộ trình: `README.md` + `ROADMAP.md`.

## 2. Tech stack (đã CHỐT)
- **UI/Backend:** Streamlit (thuần Python, 1 process, tự mở trình duyệt localhost).
- **Solver:** **Z3** (SAT). **OR-Tools (CP-SAT) là ưu tiên NHƯNG bị chặn mạng** (PyPI 404) → đang dùng Z3; viết dạng abstraction (`app/solver/`) để đổi khi mạng cho.
- **DB:** SQLite (SQLAlchemy) — 1 file `data.sqlite` = nguồn và là file xuất/load.
- **Excel:** openpyxl. **Đóng gói tương lai:** PyInstaller → thư mục `run.exe` → ZIP (portable, không cài).
- Python 3.12, venv `.venv` (dựng bằng uv từ `E:\Program Files\Python\Python312\python.exe`).

## 3. Cách chạy (dev)
```bash
cd "E:/Python Projects/manabie-timetable-scheduler"
env -u PYTHONPATH .venv/Scripts/python.exe -m streamlit run app.py --server.headless true --server.port 8501
# hoặc Windows: double-click run.bat (nó set PYTHONPATH rỗng sẵn)
```
URL: `http://localhost:8501`. Dữ liệu test (trường THCS 2 buổi) đã seed sẵn trong `data.sqlite`.

## 4. Cấu trúc
```
app.py                    # Streamlit entry + st.navigation
app/models.py             # SQLAlchemy models
app/db.py                 # engine/session, data_path()
app/solver/z3_solver.py   # solver Z3 (SAT, hard constraints)
app/solver/solver.py      # abstraction + find_conflicts
app/services/             # seeder, phan_cong, rang_buoc, tkb, xuat, feasibility, import_export
app/ui/pages.py           # các trang UI
```

## 5. Đã làm (Phase 0–5, verified)
- **P0–1** Khai báo (Khối/Lớp/Môn/GV/Tiết&Buổi/Ngày); tải/lưu file `.sqlite`; xuất Excel bảng nền.
- **P2** Số tiết khối–môn (+ phân bổ `2,1,1`); Phân công + kiểm tra khả thi.
- **P3** Ràng buộc: GV nghỉ/bận, môn cố định, giới hạn tiết/GV/buổi (`rang_buoc`).
- **P4** Xếp TKB: Z3 SAT → mẫu THCS 8 lớp **sat ~11s / 208 tiết / 0 xung đột**; xem lịch theo **lớp / giáo viên**; xếp–chỉnh tay; tìm xung đột.
- **P5** Xuất **Excel TKB** theo lớp / giáo viên / toàn trường.

## 6. Trạng thái verified
- Mọi trang **render không lỗi** (Streamlit **AppTest**), mọi service đã test logic.
- **Lưu ý:** kiểm thử là **script ad-hoc** (tạo tạm trong `%LOCALAPPDATA%\Temp\hermes-verify-*.py`, chạy rồi xoá) — **KHÔNG phải** test-suite chuẩn (chưa có pytest/CI). Đừng gọi kết quả là "test suite green".

## 7. Quirk / blocker môi trường (rất quan trọng)
1. **PYTHONPATH rò từ môi trường Hermes** vào venv dự án → khi cài/chạy/test phải `env -u PYTHONPATH` (hoặc `run.bat` đã set PYTHONPATH rỗng). Nếu import ra gói "trong venv khác" (numpy cp311...) là do quên cái này.
2. **OR-Tools bị chặn mạng** → `requirements.txt` để dòng `or-tools` comment; bỏ comment khi mạng cho; solver đã abstraction.
3. **Không `&` trong terminal tool** (phải `background=true`).
4. `/tmp` của MSYS flaky → ghi file tạm vào `~` hoặc `%LOCALAPPDATA%\Temp`.

## 8. Bước tiếp theo
- **Đóng gói portable (còn lại của Phase 5):** PyInstaller. Vấn đề kỹ thuật cần xử lý:
  - Streamlit cần nhúng **static files** + chạy qua `streamlit.web.bootstrap.run` (không phải `streamlit run`).
  - Folder-mode (khuyên, ổn định) + nén ZIP `tkb-truong.zip` → trường giải nén chạy `run.exe`, không cần cài Python.
  - Thêm `aiohttp`/`altair`/`pyarrow` (streamlit deps) vào `--hidden-import` nếu cần.
- **Phase 6 (nâng cao, chưa làm):** đa cơ sở, tổ hợp môn GDPT2018, ghép/tách lớp, nhiều GV cùng đồng giảng, xếp phòng, đổ PCCM dashboard, công khai link.

## 9. Quyết định mở (cần user chốt)
- Sau đóng gói: có cần **5 tiết sáng + 5 tiết chiều** làm mặc định (hiện mẫu 4+4) — có thể thêm qua Khai báo → Tiết.
- Mức ưu tiên Phase 6: đa cơ sở trước hay tổ hợp môn trước?

## 10. Lệnh hữu ích
- Chạy app: xem §3.
- Verify cách chạy: xem §6 (AppTest thủ công).
- Dữ liệu mẫu: `streamlit` mở Trang chủ → nút "Tạo dữ liệu mẫu", hoặc `python -c "from app import db; from app.services import seeder; s=db.make_session(db.build_engine()); seeder.seed(s); s.commit()"`.

---
*Cập nhật lần cuối: 20/08/2026 (`main` = `275b540`).*