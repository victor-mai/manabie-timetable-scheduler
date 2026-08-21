"""Dịch vụ TKB (Phase 4): solve + lưu kết quả vào bảng `tkb`, đọc, lưới theo lớp, xung đột."""

from app.models import GiaoVien, Khoi, Lop, Mon, PhanCong, Tiet, Tkb
from app.solver import solver as sv
from app.solver.z3_solver import BUOI_ORDER, build_slots


def allowed_buoi(session, *khoi_ids):
    """Set buổi (set[str]) được học. Nếu không truyền khối → mặc định chỉ Sáng.
    Khối hoc_chieu=True được thêm Chiều."""
    ids = [x for x in khoi_ids if x is not None]
    if not ids:
        return {'Sáng'}
    chieu = any(bool(k.hoc_chieu) for k in session.query(Khoi).filter(Khoi.id.in_(ids)).all())
    return {'Sáng', 'Chiều'} if chieu else {'Sáng'}


def da_co(session) -> bool:
    return session.query(Tkb).first() is not None


def solve(session, timeout_ms=60000):
    """Chạy solver; nếu sat thì lưu vào bảng tkb. Trả dict status/cells/error."""
    from app.solver import z3_solver
    r = z3_solver.solve_timetable(session, timeout_ms=timeout_ms)
    if r['status'] == 'sat':
        _replace_all(session, r['cells'])
        session.commit()
        return {'status': 'sat', 'so_o': len(r['cells']), 'error': ''}
    return {'status': r['status'], 'so_o': 0, 'error': r.get('error', '')}


def clear(session):
    for t in session.query(Tkb).all():
        session.delete(t)
    session.commit()


def load(session):
    """List dict các ô hiện có."""
    mon = {m.id: m.ma for m in session.query(Mon).all()}
    gv = {g.id: g.ten for g in session.query(GiaoVien).all()}
    lop = {l.id: l.ten for l in session.query(Lop).all()}
    return [{'id': t.id, 'lop': lop.get(t.lop_id, '?'), 'mon': mon.get(t.mon_id, '?'),
             'gv': gv.get(t.gv_id, '?'), 'thu': t.thu, 'buoi': t.buoi,
             'tiet': t.tiet_stt} for t in session.query(Tkb).all()]


def _replace_all(session, cells):
    for t in session.query(Tkb).all():
        session.delete(t)
    session.flush()
    for c in cells:
        session.add(Tkb(lop_id=c['lop_id'], mon_id=c['mon_id'], gv_id=c['gv_id'],
                        thu=c['thu'], buoi=c['buoi'], tiet_stt=c['tiet_stt']))


def grid(session, lop_id):
    """Lưới TKB của 1 lớp: rows = tiết (buổi+stt), cols = ngày, ô = 'MA - Ten GV'.
    Chỉ hiện buổi mà khối của lớp được học (hoc_chieu)."""
    slot_list, _ = build_slots(session)
    lop = session.query(Lop).get(lop_id)
    buoi_ok = allowed_buoi(session, lop.khoi_id if lop else None)
    days = sorted({s[0] for s in slot_list})
    tiet_labels = []
    seen = set()
    for _thu, buoi, stt in slot_list:
        key = (buoi, stt)
        if key not in seen and buoi in buoi_ok:
            seen.add(key)
            tiet_labels.append(f'{buoi} {stt}')
    mon = {m.id: m.ma for m in session.query(Mon).all()}
    gv = {g.id: g.ten for g in session.query(GiaoVien).all()}
    day_nhan = {2: 'Thứ 2', 3: 'Thứ 3', 4: 'Thứ 4', 5: 'Thứ 5', 6: 'Thứ 6', 7: 'Thứ 7', 8: 'Chủ nhật'}
    rows = {tl: {day_nhan.get(d, str(d)): '' for d in days} for tl in tiet_labels}
    for t in session.query(Tkb).filter_by(lop_id=lop_id).all():
        lbl = f'{t.buoi} {t.tiet_stt}'
        if lbl in rows and t.thu in days:
            rows[lbl][day_nhan.get(t.thu, str(t.thu))] = f'{mon.get(t.mon_id, "?")} — {gv.get(t.gv_id, "?")}'
    return rows, tiet_labels, days


def grid_gv(session, gv_id):
    """Lịch giảng dạy của 1 GV: rows = tiết, cols = ngày, ô = 'Lớp · Môn'.
    Chỉ hiện buổi mà các lớp GV dạy dùng (hợp của các khối)."""
    slot_list, _ = build_slots(session)
    lop_ids = {t.lop_id for t in session.query(Tkb).filter_by(gv_id=gv_id).all()}
    khoi_ids = {l.khoi_id for l in session.query(Lop).filter(Lop.id.in_(lop_ids or {-1})).all()}
    buoi_ok = allowed_buoi(session, *khoi_ids)
    days = sorted({s[0] for s in slot_list})
    tiet_labels = []
    seen = set()
    for _thu, buoi, stt in slot_list:
        key = (buoi, stt)
        if key not in seen and buoi in buoi_ok:
            seen.add(key)
            tiet_labels.append(f'{buoi} {stt}')
    mon = {m.id: m.ma for m in session.query(Mon).all()}
    lop = {l.id: l.ten for l in session.query(Lop).all()}
    day_nhan = {2: 'Thứ 2', 3: 'Thứ 3', 4: 'Thứ 4', 5: 'Thứ 5', 6: 'Thứ 6', 7: 'Thứ 7', 8: 'Chủ nhật'}
    rows = {tl: {day_nhan.get(d, str(d)): '' for d in days} for tl in tiet_labels}
    for t in session.query(Tkb).filter_by(gv_id=gv_id).all():
        lbl = f'{t.buoi} {t.tiet_stt}'
        if lbl in rows and t.thu in days:
            rows[lbl][day_nhan.get(t.thu, str(t.thu))] = f'{lop.get(t.lop_id, "?")} · {mon.get(t.mon_id, "?")}'
    return rows, tiet_labels, days


def xung_dot(session) -> list:
    """Các xung đột hiện có trong bảng tkb (GV trùng giờ / Lớp trùng giờ)."""
    slots = {}
    for t in session.query(Tkb).all():
        slots.setdefault((t.thu, t.buoi, t.tiet_stt), len(slots))
    cells = [sv.Cell(str(t.lop_id), str(t.mon_id), str(t.gv_id), t.thu,
                     slots[(t.thu, t.buoi, t.tiet_stt)])
             for t in session.query(Tkb).all()]
    return sv.find_conflicts(cells)


# ---- chỉnh tay: các môn 1 lớp được phép gán ----
def mon_options_for_lop(session, lop_id):
    """Trả [(mon_ten, mon_id, gv_id)] các môn được phân công cho lớp (so_tiet>0)."""
    from app.services import phan_cong as pc_svc
    prog = pc_svc.program_map(session)
    lop = session.query(Lop).get(lop_id)
    mon_of = {m.id: m.ten for m in session.query(Mon).all()}
    out = []
    for p in session.query(PhanCong).filter_by(lop_id=lop_id).all():
        so = prog.get(lop.khoi_id, {}).get(p.mon_id, 0)
        if so > 0:
            out.append({'ten': mon_of.get(p.mon_id, '?'), 'mon_id': p.mon_id, 'gv_id': p.gv_id})
    return out


def replace_lop(session, lop_id, cells):
    """Thay toàn bộ ô của 1 lớp (dùng cho chỉnh tay). cells: list dict(lop_id,...)."""
    for t in session.query(Tkb).filter_by(lop_id=lop_id).all():
        session.delete(t)
    session.flush()
    for c in cells:
        session.add(Tkb(lop_id=c['lop_id'], mon_id=c['mon_id'], gv_id=c['gv_id'],
                        thu=c['thu'], buoi=c['buoi'], tiet_stt=c['tiet_stt']))
    session.commit()