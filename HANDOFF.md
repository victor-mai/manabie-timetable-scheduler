# HANDOFF — manabie-timetable-scheduler

> Đọc tài liệu này ĐẦU TIÊN khi tiếp tục. Cập nhật khi có thay đổi trạng thái.
> Repo: `E:\Python Projects\manabie-timetable-scheduler` · GitHub: `victor-mai/manabie-timetable-scheduler` (public, nhánh `main`).

---

## 1. Mục tiêu
App xếp **thời khóa biểu toàn trường** (1 trường, có thể nhiều cơ sở), **mở local**, lưu bằng **1 file `.sqlite`** (xuất/load lại được). Nghiên cứu thị trường + 2 đối thủ (OLM TKB, tkb.com.vn) nằm trong `MARKET_RESEARCH.md`, `OLM_TKB_RESEARCH.md`, `TKBDOTCOM_RESEARCH.md`. Thiết kế & lộ trình: `README.md` + `ROADMAP.md`.

**Reference mới:** `references/` (không có trước Phase này):
- `references/dinh-muc-tiet-thcs.md` — **định mức số tiết/tuần theo khối (GDPT THCS)** + kết quả đối chiếu seeder (ĐÃ KHỚP). Là chuẩn để so số tiết.
- `references/checklist-gap-hieu-truong.md` — **checklist buổi làm việc với Hiệu trưởng**: dữ liệu cần chuẩn bị, bộ ràng buộc CỨNG/MỀM cần hỏi, đặc thù nâng cao, thứ tự buổi gặp. ±Msg xin hẹn gặp (bản nháp đã gửi user, chưa lưu file).

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
URL: `http://localhost:8501`. Dữ liệu test đã seed sẵn trong `data.sqlite`.

## 4. Cấu trúc
```
app.py                    # Streamlit entry + st.navigation
app/models.py             # SQLAlchemy models (Khoi.hoc_chieu + PhanCong... )
app/db.py                 # engine/session, data_path()
app/solver/z3_solver.py   # solver Z3 (SAT), lọc ô theo hoc_chieu của khối
app/solver/solver.py      # abstraction + find_conflicts
app/services/             # seeder, phan_cong, rang_buoc, tkb, xuat, feasibility, import_export
app/ui/pages.py           # các trang UI (Khai báo Khối có toggle "Học chiều")
references/               # [MỚI] dinh-muc-tiet-thcs.md, checklist-gap-hieu-truong.md
```

## 5. Đã làm (Phase 0–5 + cập nhật gần nhất, verified)
- **P0–1** Khai báo (Khối/Lớp/Môn/GV/Tiết&Buổi/Ngày); tải/lưu file `.sqlite`; xuất Excel bảng nền.
- **P2** Số tiết khối–môn (+ phân bổ `2,1,1` **— lưu đc nhưng solver CHƯA đọc, xem §8**); Phân công + kiểm tra khả thi.
- **P3** Ràng buộc: GV nghỉ/bận, môn cố định, giới hạn tiết/GV/buổi (`rang_buoc`).
- **P4** Xếp TKB: Z3 SAT → mẫu THCS 8 lớp **sat / 236 tiết / 0 xung đột**; xem lịch theo **lớp / giáo viên**; xếp–chỉnh tay; tìm xung đột.
- **P5** Xuất **Excel TKB** theo lớp / giáo viên / toàn trường.

### Cập nhật mới nhất (21/08/2026) — buổi học & số tiết theo định mức
- **Số tiết/tuần theo ĐỊNH MỨC GDPT THCS** (không còn "số mẫu hợp lý"). Khối 6–7 = **29 tiết/tuần**, khối 8–9 = **30 tiết/tuần**. Sửa: Tin 2→1, Công nghệ 6–7 2→1, HĐTN-HN 1→3, KHTN 8–9 3→4, Sử–Địa 8–9 2→3; thêm AN+MT khối 8–9; thêm môn **Giáo dục địa phương** (`DP`). Công nghệ 8–9 52/năm≈1.5 → làm tròn 2 (độ lệch chấp nhận). → `references/dinh-muc-tiet-thcs.md`.
- **Buổi học theo khối:** thêm cột `hoc_chieu` vào `Khoi`. Khối **6–7: chỉ Sáng** (1 buổi, 5 tiết ×6 ngày = 30 ô, dùng 29 + 1 trống). Khối **8–9: `hoc_chieu=True`** → thêm buổi **Chiều** (T6–T8), 8 tiết/ngày = 48 ô, dùng 30. **Đã bỏ hẳn ca "Tối"** (không dùng).
- **Config qua UI:** Khai báo → Khối có toggle **"Học chiều"** (checkbox). Solver + lịch grid tự lọc ô theo khối.
- **Seeder:** 13 môn (thêm DP), 20 GV (thêm cô Huyền DP), 104 phân công, 52 khối-môn-tiết.
- Verify ad-hoc: solver `sat`, 236 tiết, 0 xung đột; khối 6–7 dùng **0** ô Chiều, khối 8–9 dùng 22 & 18 ô Chiều. **ALL OK.**

## 6. Trạng thái verified
- Mọi trang **render không lỗi** (Streamlit **AppTest**), mọi service đã test logic.
- **Lưu ý:** kiểm thử là **script ad-hoc** (tạo tạm trong `%LOCALAPPDATA%\Temp\hermes-verify-*.py`, chạy rồi xoá) — **KHÔNG phải** test-suite chuẩn (chưa có pytest/CI). Đừng gọi kết quả là "test suite green".

## 7. Quirk / blocker môi trường (rất quan trọng)
1. **PYTHONPATH rò từ Hermes** vào venv → khi cài/chạy/test phải `env -u PYTHONPATH` (hoặc `run.bat` set PYTHONPATH rỗng). Import ra gói "venv khác" (numpy cp311...) = quên cái này.
2. **OR-Tools bị chặn mạng** → `requirements.txt` để dòng `or-tools` comment; bỏ khi mạng cho; solver abstraction.
3. **Không `&` trong terminal tool** (phải `background=true`).
4. `/tmp` của MSYS flaky → ghi file tạm vào `~` hoặc `%LOCALAPPDATA%\Temp`.
5. Khi verify script ghi DB tạm: `tempfile.mkstemp` + set `TKB_DATA`; đóng `eng.dispose()` trước `os.remove` nếu không Windows khoá file (PermissionError).

## 8. Việc CÒN LẠI / TỒN ĐỌNG (ưu tiên session sau)
> Buổi gặp hiệu trưởng sắp diễn ra → thu thập dữ liệu/ràng buộc thực tế, rồi quay lại làm đúng. Trước mắt có thể làm các item 1–2 ngay.

1. **GVCN + tiết Chào cờ** (đã chốt hướng, CHƯA code): Chào cờ **Thứ 2 – Sáng – Tiết 1**, do **GVCN** đứng, **không tính** vào tổng tiết/tuần. Hướng A: thêm `gvcn_id` (hoặc bảng GVCN) + môn `CHAOCO` cố định + config UI. ⚠️ Khối 8–9 đang 30 tiết kín 30 ô → cần đệm (đã có hoc_chieu cho khối 8–9, sẽ ra ô Chiều). 
2. **Vị trí tiết trống** (khối 6–7 có 1 ô trống): hiện solver **đặt tùy ý** (ra giữa tuần/giữa buổi, không đẹp). Người dùng muốn **Tiết 5 Thứ 7 trống**. Chưa chốt: ràng buộc CỨNG theo khối hay MỀM tối ưu (Z3 Optimize). **Cần user chốt hướng.**
3. **Phân bổ tiết `2,1,1`**: khai báo được trong UI nhưng **solver Z3 chưa đọc `phan_bo`** → xếp tự do, không tôn trọng "2 tiết liền". Cần khớp solver với `phan_bo`.
4. **Nghi ngờ khi gặp hiệu trưởng**: tạm dùng TKB mẫu (chưa có dữ liệu trường thật). Sau buổi gặp, chuyển dữ liệu thật + chốt ràng buộc cứng/mềm.
5. **Đóng gói portable (còn lại Phase 5):** PyInstaller → thư mục `run.exe` → ZIP `tkb-truong.zip`. Streamlit cần nhúng static + chạy qua `streamlit.web.bootstrap.run`; thêm `aiohttp`/`altair`/`pyarrow` hidden-import.
6. **Phase 6 (nâng cao, chưa làm):** đa cơ sở, tổ hợp môn GDPT2018, ghép/tách lớp, nhiều GV đồng giảng, xếp phòng, PCCM dashboard, công khai link.

## 9. Quyết định OPEN (cần user chốt)
- Hướng xử lý **tiết trống** (CỨNG khối / MỀM tối ưu) — §8.2.
- Mức ưu tiên sau khi có dữ liệu trường: GVCN/Chào cờ + `2,1,1` trước, hay đi thẳng dữ liệu thật?
- Khi gặp hiệu trưởng: ưu tiên hỏi ràng buộc nào (theo checklist)? Có cần chuẩn bị demo chạy trước mắt khách?
- Phase 6: đa cơ sở trước hay tổ hợp môn trước?

## 10. Lệnh hữu ích
- Chạy app: xem §3.
- Verify cách chạy: xem §6 (AppTest thủ công).
- Dữ liệu mẫu: `streamlit` mở Trang chủ → nút "Tạo dữ liệu mẫu", hoặc:
  ```bash
  env -u PYTHONPATH .venv/Scripts/python.exe -c "from app import db; from app.services import seeder; s=db.make_session(db.init_db()); seeder.seed(s); s.commit()"
  ```
  (Khi schema đổi: `db.init_db(drop=True)` để dựng lại bảng mới, e.g. có cột `hoc_chieu`.)

---
*Cập nhật lần cuối: 21/08/2026. Chốt buổi học theo định mức THCS + config khối (1 buổi / 2 buổi), bỏ ca tối; GVCN/Chào cờ chờ triển khai; chuẩn bị gặp hiệu trưởng.*