"""Solver Z3 cho bài toán xếp TKB (Phase 4).

Mô hình SAT:
- Biến B[a, s] = 1 nếu (lớp, môn, GV) = a có 1 tiết tại slot s.
- slot s = (thu, buoi, stt) — sinh từ NgayHoc(active) × Tiet.
Ràng buộc hard: đủ số tiết/môn, lớp không 2 môn cùng giờ, GV không 2 lớp cùng giờ,
tôn trọng GV nghỉ/ngày+tiết, môn cố định, giới hạn số tiết/GV/buổi.

OR-Tools là lựa chọn ưu tiên (bị chặn mạng) — interface giữ để đổi solver sau.
"""
from collections import defaultdict

from z3 import (Bool, If, Not, Solver, Sum, sat, unknown, unsat)

from app.models import (Khoi, KhoiMonTiet, Lop, NgayHoc, PhanCong, RangBuoc, Tiet)

BUOI_ORDER = {'Sáng': 0, 'Chiều': 1}


def build_slots(session):
    """Trả (slot_list, slot_index): slot_list = [(thu,buoi,stt), ...] sắp theo ngày*buổi*tiết."""
    days = sorted(n.thu for n in session.query(NgayHoc).filter_by(active=True).all())
    tiet = sorted(session.query(Tiet).all(),
                  key=lambda t: (BUOI_ORDER.get(t.buoi, 9), t.stt, t.id))
    periods = [(t.buoi, t.stt) for t in tiet]
    slot_list = [(thu, buoi, stt) for thu in days for (buoi, stt) in periods]
    slot_index = {sl: i for i, sl in enumerate(slot_list)}
    return slot_list, slot_index


def build_assignments(session):
    """Danh sách các (lop_id, mon_id, gv_id, so_tiet) cần xếp (so_tiet từ khối-môn)."""
    prog = {}
    for km in session.query(KhoiMonTiet).filter(KhoiMonTiet.so_tiet > 0).all():
        prog.setdefault(km.khoi_id, {})[km.mon_id] = km.so_tiet
    lop_khoi = {l.id: l.khoi_id for l in session.query(Lop).all()}
    assigns = []
    for pc in session.query(PhanCong).all():
        so = prog.get(lop_khoi.get(pc.lop_id), {}).get(pc.mon_id, 0)
        if so and so > 0:
            assigns.append({'lop_id': pc.lop_id, 'mon_id': pc.mon_id,
                            'gv_id': pc.gv_id, 'so_tiet': so})
    return assigns


def solve_timetable(session, timeout_ms=60000):
    """Trả dict: {status: 'sat'|'unsat'|'unknown', cells:[...], n_var, error}."""
    slot_list, slot_index = build_slots(session)
    assigns = build_assignments(session)
    if not assigns:
        return {'status': 'unsat', 'error': 'Chưa có phân công/số tiết để xếp.', 'cells': []}
    if not slot_list:
        return {'status': 'unsat', 'error': 'Chưa có ngày học / tiết học (khai báo ở Phase 1).', 'cells': []}
    n_slot = len(slot_list)
    n_assign = len(assigns)

    sol = Solver()
    sol.set('timeout', timeout_ms)
    B = {}
    for a in range(n_assign):
        for s in range(n_slot):
            B[(a, s)] = Bool(f'x{a}_{s}')
    v = B  # alias Bool x[a][s]

    # 0) khối hoc_chieu=False → không được dùng ô buổi Chiều (ép biến về False)
    lop_khoi = {l.id: l.khoi_id for l in session.query(Lop).all()}
    khoi_chieu = {k.id: bool(k.hoc_chieu) for k in session.query(Khoi).all()}
    for a in range(n_assign):
        khoi = lop_khoi.get(assigns[a]['lop_id'])
        buoi_ok = ('Sáng', 'Chiều') if khoi_chieu.get(khoi) else ('Sáng',)
        for s in range(n_slot):
            if slot_list[s][1] not in buoi_ok:
                sol.add(Not(v[(a, s)]))

    # 1) đủ số tiết mỗi (lớp,mon,gv)
    for a in range(n_assign):
        sol.add(Sum([If(v[(a, s)], 1, 0) for s in range(n_slot)]) == assigns[a]['so_tiet'])

    # 2) lớp không 2 môn cùng slot
    by_lop = defaultdict(list)
    for a in range(n_assign):
        by_lop[assigns[a]['lop_id']].append(a)
    for lop_id, alist in by_lop.items():
        for s in range(n_slot):
            sol.add(Sum([If(v[(a, s)], 1, 0) for a in alist]) <= 1)

    # 3) GV không 2 lớp cùng slot
    by_gv = defaultdict(list)
    for a in range(n_assign):
        by_gv[assigns[a]['gv_id']].append(a)
    for gv_id, alist in by_gv.items():
        for s in range(n_slot):
            sol.add(Sum([If(v[(a, s)], 1, 0) for a in alist]) <= 1)

    # 4) rang buoc
    for rb in session.query(RangBuoc).all():
        if rb.loai == 'GV_NGAY_NGHI' and rb.gv_id and rb.thu:
            for a in range(n_assign):
                if assigns[a]['gv_id'] == rb.gv_id:
                    for s, sl in enumerate(slot_list):
                        if sl[0] == rb.thu:
                            sol.add(Not(v[(a, s)]))
        elif rb.loai == 'GV_TIET_NGHI' and rb.gv_id and rb.thu and rb.buoi and rb.tiet_stt:
            s = slot_index.get((rb.thu, rb.buoi, rb.tiet_stt))
            if s is not None:
                for a in range(n_assign):
                    if assigns[a]['gv_id'] == rb.gv_id:
                        sol.add(Not(v[(a, s)]))
        elif rb.loai == 'MON_CO_DINH' and rb.mon_id and rb.thu and rb.buoi and rb.tiet_stt:
            s = slot_index.get((rb.thu, rb.buoi, rb.tiet_stt))
            if s is not None:
                for a in range(n_assign):
                    if assigns[a]['mon_id'] == rb.mon_id:
                        sol.add(v[(a, s)])
        elif rb.loai == 'GIOI_HAN_TIET_BUOI' and rb.gv_id and rb.buoi and rb.gia_tri:
            buf_slots = [s for s, sl in enumerate(slot_list) if sl[1] == rb.buoi]
            for a in range(n_assign):
                if assigns[a]['gv_id'] == rb.gv_id:
                    sol.add(Sum([If(v[(a, s)], 1, 0) for s in buf_slots]) <= rb.gia_tri)

    r = sol.check()
    if r == sat:
        m = sol.model()
        cells = []
        for a in range(n_assign):
            for s in range(n_slot):
                if is_true(m.eval(v[(a, s)])):
                    thu, buoi, stt = slot_list[s]
                    cells.append({'lop_id': assigns[a]['lop_id'],
                                  'mon_id': assigns[a]['mon_id'],
                                  'gv_id': assigns[a]['gv_id'],
                                  'thu': thu, 'buoi': buoi, 'tiet_stt': stt})
        return {'status': 'sat', 'cells': cells, 'n_assign': n_assign, 'n_slot': n_slot}
    if r == unsat:
        return {'status': 'unsat', 'error': 'Không tồn tại TKB thoả mãn ràng buộc (kiểm tra mâu thuẫn ràng buộc).',
                'cells': []}
    return {'status': 'unknown', 'error': 'Solver hết thời gian / không xác định.', 'cells': []}


def is_true(v):
    try:
        return v is True or str(v) == 'True'
    except Exception:
        return False