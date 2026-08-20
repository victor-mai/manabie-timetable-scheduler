"""Solver xếp TKB — dạng abstraction.

Phase 0-1: interface + hàm kiểm tra xung đột (dùng được cho màn TKB sau).
Phase 4: cài đặt đầy đủ — hiện đang dùng Z3 (OR-Tools bị chặn ở mạng này, xem requirements),
         giao diện mở để chèn `ortools.cp_model` khi mạng cho phép.
"""

from dataclasses import dataclass, field


@dataclass
class Cell:
    """Một ô TKB: học sinh Lớp học môn X ở (thu, buổi, tiết) do GV dạy."""
    lop: str
    mon: str
    gv: str
    thu: int
    tiet_global: int


def find_conflicts(cells: list[Cell]) -> list[dict]:
    """Trả các xung đột: 1 GV trùng giờ; 1 lớp trùng giờ (2 môn). Không xét phòng ở bản này."""
    conf = []
    by_gv: dict[str, list[Cell]] = {}
    by_lop: dict[str, list[Cell]] = {}
    for c in cells:
        by_gv.setdefault(c.gv, []).append(c)
        by_lop.setdefault(c.lop, []).append(c)
    for gv, arr in by_gv.items():
        seen = {}
        for c in arr:
            seen.setdefault((c.thu, c.tiet_global), []).append(c)
        for (thu, t), arr2 in seen.items():
            if len(arr2) > 1:
                conf.append({'loai': 'GV trùng giờ', 'gv': gv, 'thu': thu,
                             'tiet': t, 'chi_tiet': [f"{c.lop}-{c.mon}" for c in arr2]})
    for lop, arr in by_lop.items():
        seen = {}
        for c in arr:
            seen.setdefault((c.thu, c.tiet_global), []).append(c)
        for (thu, t), arr2 in seen.items():
            if len(arr2) > 1:
                conf.append({'loai': 'Lớp trùng giờ', 'lop': lop, 'thu': thu,
                             'tiet': t, 'chi_tiet': [f"{c.mon} ({c.gv})" for c in arr2]})
    return conf


def solve(*args, **kw):
    """Tạm thời chưa cài (Phase 4). Giữ interface để app không phụ thuộc solver cụ thể."""
    raise NotImplementedError('Solver đầy đủ sẽ cài ở Phase 4 (xếp auto).')