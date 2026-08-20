# School Timetable Scheduler — Tạo thời khóa biểu toàn trường

> Tài liệu tổng hợp kiến thức & các buổi trao đổi về việc xây dựng ứng dụng xếp thời khóa biểu (TKB) cho cả trường: nhiều lớp, nhiều khối, nhiều môn.
> Ngôn ngữ: Tiếng Việt (giữ các thuật ngữ chuyên môn tiếng Anh ở những chỗ quen dùng).

> 📊 **Nghiên cứu thị trường (VN & thế giới):** xem **[MARKET_RESEARCH.md](MARKET_RESEARCH.md)** — các bên đã cung cấp giải pháp này, điểm mạnh/yếu, và ý nghĩa định vị cho dự án.
> 🔍 **Nghiên cứu sâu OLM TKB (đối thủ mạnh nhất VN):** xem **[OLM_TKB_RESEARCH.md](OLM_TKB_RESEARCH.md)** — mô hình dữ liệu & toàn bộ ràng buộc TKB Việt Nam (1/2 buổi, sáng–chiều, tiết liên tiếp, tiết tránh, tổ hợp môn, ghép lớp/GV…).
> 🖥️ **Nghiên cứu sâu TKB (tkb.com.vn) — admin thực tế:** xem **[TKBDOTCOM_RESEARCH.md](TKBDOTCOM_RESEARCH.md)** — feature map, flow 8 bước, toàn bộ ràng buộc, PCCM, đa cơ sở, phòng → nguồn tham chiếu để liệt kê tính năng cần build.

> 🗺️ **Bản đồ tiến hành (tech stack + 6 phase):** xem **[ROADMAP.md](ROADMAP.md)** — plan xây dựng app cho 1 trường, tech stack, kiến trúc, và mục "quyết định cần chốt" trước khi code.

---

## 1. Bản chất bài toán

Tạo TKB cả trường **không phải** chuyện "xếp tay" hay brute-force — bản chất là một bài toán **ràng buộc (Constraint-Satisfaction Problem / Scheduling)**. Không tự viết thuật toán từ đầu mà phải dùng **constraint solver** chuyên dụng.

- Tên tiếng Anh chuẩn trong ngành: **School Timetable Scheduling** / **Course Timetabling**.
- Tên app hay dùng: **School Timetable Generator** hoặc **Timetable Auto-Scheduler**.
- Phần lõi thuật toán gọi là **timetabling solver** (thuộc họ **Constraint-based Scheduling** / **Timetable Optimization**).
- Ví dụ solver thương mại: **aSc TimeTables**, **Untis**.
- Công cụ open-source khuyên dùng: **Google OR-Tools (CP-SAT)** — mạnh nhất cho bài này bằng Python, miễn phí, dùng được khai báo biến + ràng buộc hard + mục tiêu soft.

---

## 2. Thông tin cần thu thập (đầu vào)

### 2.1 Dữ liệu "thực thể" (ai / cái gì)

| Nhóm | Cần biết |
|---|---|
| **Khối / Lớp** | Danh sách lớp, thuộc khối, sĩ số, phòng học chính của lớp |
| **Giáo viên** | Mã GV, bộ môn, dạy được môn gì, số tiết/tuần tối thiểu & tối đa, thời gian cố định **không rảnh** (họp chiều T4, nghỉ, kiêm nhiệm…), nguyện vọng |
| **Môn học** | Tên môn, **số tiết/tuần của mỗi môn cho từng khối**, GV nào phụ trách |
| **Phòng / tài nguyên** | Phòng bộ môn (Lý/Hóa/Sinh/Tin/Thể dục…), phòng chức năng, sân bãi — vì **nhiều lớp dùng chung, không được trùng giờ** |
| **Khung thời gian** | Mỗi ngày mấy tiết, từ giờ nào, mấy ngày/tuần, sáng/chiều, tiết chẵn/lẻ, tiết ngắn |

### 2.2 Ràng buộc — phân loại HARD / SOFT (rất quan trọng)

**Hard (bắt buộc — không thể phá):**
- 1 GV không dạy 2 lớp cùng lúc
- 1 lớp không học 2 môn cùng lúc
- 1 phòng (nhất là phòng bộ môn) không dùng 2 lớp cùng lúc
- Mỗi môn đủ số tiết quy định/tuần
- GV chỉ dạy đúng môn được phân công
- Không vượt số tiết/ngày và tiết/tuần của GV

**Soft (nên tối ưu — cho phép đánh đổi):**
- Lớp không bị "kẹt tiết trống" (cửa sổ trống) giữa ngày
- GV không bị kín cả buổi / dồn dập
- Môn khó (Toán, Văn, Lý…) đặt buổi sáng hoặc đầu tuần
- Môn chính không 3 tiết liền
- Khóa biểu mới **gần giống khóa biểu cũ** nhất có thể (yêu cầu rất hay gặp)

> ⚠️ **Kinh nghiệm thực chiến:** vấn đề đầu tiên không phải thuật toán mà là **phân loại ràng buộc**. Nhà trường hay nói "phải thế này" nhưng thật ra là "nên thế này" — phải tách bạch hard/soft ngay từ đầu, nếu không solver sẽ không bao giờ ra lời giải hoặc tìm mãi không ra.
> Cũng cần cho phép **đánh đổi soft** (ví dụ chấp nhận vài tiết trống để đổi lấy GV không bị kín cả buổi). Không có lời giải "hoàn hảo" mọi mặt.

---

## 3. Kiến trúc hệ thống đề xuất

```
Nhà trường (Excel: GV, lớp, môn, phân công) → import
        ▼
┌──────────────────────────────────────────────────┐
│  Backend (Python)                                 │
│   • FastAPI / Flask  — API nhập, chạy solve        │
│   • Google OR-Tools (CP-SAT) — solver              │
│   • SQLite — 1 file, không cần cài DB              │
└──────────────────────────────────────────────────┘
        ▼ JSON
Frontend (local web): dữ liệu → nút "Auto xếp" → xem TKB
   • Theo lớp / theo GV / theo phòng  (nhiều góc nhìn)
   • Kéo-thả chỉnh tay sau khi auto-sinh
   • Kiểm tra xung đột + gợi ý tự sửa
   • Xuất Excel / in giấy
```

**Lựa chọn công nghệ:**
- **Google OR-Tools (CP-SAT)** — solver chuẩn công nghiệp cho timetable, dùng Python.
- Backend **Python (FastAPI)** — gần OR-Tools nhất.
- DB **SQLite** — 1 file, kéo đi đâu chạy đó.
- Import/Export **Excel là bắt buộc** — nhà trường quen nhập liệu bằng Excel, ban giám hiệu muốn nhận file Excel để xem/in.

**Cách phân phối cho nhà trường dùng:**
- Dev: chạy `localhost` trên máy, mở trình duyệt. Đủ cho cá nhân / 1 trường nhỏ.
- Zero-install: đóng gói **app desktop** (Electron, hoặc PyInstaller bọc Python + OR-Tools) — kích file exe là chạy, không cần cài Python.

---

## 4. Thiết kế Front-end

App hướng tới **giáo vụ + ban giám hiệu** (người không rành máy) → chỉ cần **4 màn hình**, gọn gàng, không phô diễn:

| Màn hình | Chức năng |
|---|---|
| **A. Nhập / quản lý dữ liệu nền** | Bảng (tabular) như Excel: paste từ Excel hoặc upload file. Bảng GV, Phân công, Lớp, Môn. |
| **B. Cấu hình ràng buộc** ⭐ quan trọng nhất | Form checkbox + số: tiết/ngày, ngày/tuần, đánh dấu hard/soft, trọng số cho từng soft. |
| **C. Khóa biểu** (view chính) | Lưới thời gian × (lớp / GV / phòng) — 3 tab góc nhìn. Kéo-thả sửa tay, tự tô đỏ ô xung đột. |
| **D. Xuất bản** | Nút xuất Excel / in từng lớp, từng GV. |

**Nguyên tắc thiết kế cốt lõi:** tách tầng **"dữ liệu"** ra khỏi tầng **"luật"**.
- Dữ liệu (ai, môn gì, lớp nào) thay đổi hàng kỳ → **cho phép import**.
- Luật (hard/soft) là **cấu hình tĩnh** → set 1 lần trong form, không trộn vào Excel.

### Công nghệ front-end

**Option A — Nhẹ & nhanh (khuyên dùng nếu 1 dev):**
- Backend tự render: **FastAPI/Flask + Jinja2**.
- CSS framework: **Tailwind CSS** hoặc **Bootstrap / Fomantic-UI**.
- JS nhỏ cho TKB: **FullCalendar** (không chỉ lịch mà kéo-thả rất chuẩn) hoặc tự dựng lưới bằng **SortableJS** (kéo-thả ô).
- Đủ dùng sớm trong vài tuần với 1 người làm.

**Option B — Chuẩn web app hiện đại (đầu tư hơn):**
- Backend: FastAPI + SQLite (giữ nguyên).
- Frontend: **React + Vite** (hoặc Next.js), giao tiếp qua REST API / JSON.
- UI library làm đẹp nhanh:
  - **Ant Design** — đẹp kiểu quản lý, có sẵn table/form/calendar. ⭐ hợp bài toán này nhất.
  - **MUI (Material UI)** — gọn, hiện đại.
  - **Tailwind** — tự do styling.
- Kéo-thả TKB: **react-grid-layout** hoặc **@dnd-kit**.

> **Khuyến nghị:** ưu tiên **Option A** để dùng được sớm, chuyển sang B khi cần giao diện động/đẹp hơn. TKB chỉ là lưới thời gian × lớp — CSS framework + 1 thư viện kéo-thả là đủ, không cần thứ cầu kỳ.

---

## 5. Phân luồng nhập dữ liệu vs ràng buộc

Chia làm **3 luồng nhập khác nhau** — đây là điểm tách bạch quan trọng nhất về UX:

| Loại | Ví dụ | Cách nhập | Tần suất |
|---|---|---|---|
| **Dữ liệu nền** | GV, lớp, môn, phân công dạy | **Import Excel** (hoặc paste từ Excel) — số lượng lớn | Hàng kỳ / hàng năm |
| **Ràng buộc cấu hình** | tiết/ngày, số tiết môn/khối, hard/soft nào | **Form cấu hình trên web**, lưu thành template | Chỉnh từng đợt, dùng lại |
| **Ràng buộc tạm thời / ngoại lệ** | "Cô Lan nghỉ chiều T4 tuần này", "10A không học TD tiết cuối" | **Đánh dấu trực tiếp** trên view lớp/GV (click ô → chặn), chỉ áp dụng 1 lần | Linh hoạt, từng tuần |

> ⚠️ Hai nhóm "ràng buộc" **không nên trộn vào file Excel import**. Nếu gộp hết vào Excel, mỗi lần đổi ràng buộc lại phải sửa file, gửi lại, reload — rất rối. Cấu hình để trong app, treo vào 1 file config / bảng lưu trữ riêng.

```
[ Excel nhập: GV, lớp, môn, phân công ]     ← dữ liệu, đổi hàng kỳ
[ Web form: hard/soft, khung giờ, trọng số ] ← cấu hình, set 1 lần
[ Click trên view: ngoại lệ tuần này ]        ← tạm thời
                    │  ▼
          Solver (OR-Tools) → Khóa biểu → sửa tay → xuất Excel
```

---

## 6. Vòng đời sử dụng thực tế

1. **Nhập dữ liệu** — copy/tải từ Excel.
2. **"Auto xếp"** — solver chạy vài giây tới vài phút, ra khóa biểu sơ bộ.
3. **Co-review** — giáo vụ xem theo lớp/GV, **kéo-thả sửa tay**.
4. **Tự kiểm tra xung đột** sau mỗi lần sửa.
5. **Duyệt & xuất bản** — xuất Excel / in.

---

## 7. Lưu ý thực chiến (ít người nhắc)

- Dữ liệu nhập vào **luôn thiếu/sai** → bắt buộc có bước validate đầu vào trước khi solve (GV chưa khai, môn thiếu tiết…).
- Ràng buộc thực tế **linh hoạt & thay đổi** (GV nghỉ, mẹo phòng, thêm tiết) → thiết kế ràng buộc **thêm bớt được**, không hard-code.
- Cho phép **đánh đổi soft** — không có lời giải hoàn hảo mọi mặt.
- Việc **mô hình hóa + thu thập dữ liệu chiếm ~70%** công sức, thuật toán chỉ ~30%.

---

## 8. Hướng phát triển tiếp theo

- ✅ Đã chốt: bản chất bài toán, danh sách dữ liệu đầu vào, phân loại hard/soft, kiến trúc backend, thiết kế 4 màn hình front-end, phân luồng nhập dữ liệu vs ràng buộc, công nghệ lựa chọn.
- ⬜ (tùy chọn) Dựng **prototype chạy được** — web app local (Python + OR-Tools) với dữ liệu mẫu + form hard/soft, 4 màn hình.
- ⬜ (tùy chọn) Viết **doc thiết kế chi tiết** để bàn với nhà trường/đồng nghiệp.
- ⬜ (tùy chọn) Nếu Manabie đã có dữ liệu lớp/GV/môn sẵn → xem cách nhập từ đó.

---

*Tài liệu được tổng hợp từ buổi trao đổi về yêu cầu & thiết kế ứng dụng xếp thời khóa biểu toàn trường.*