"""Dịch vụ TKB (Phase 4): solve + lưu kết quả vào bảng `tkb`, đọc, lưới theo lớp, xung đột."""

from app.models import GiaoVien, Lop, Mon, PhanCong, Tiet, Tkb
from app.solver import solver as sv
from app.solver.z3_solver import BUOI_ORDER, build_slots


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
    """Lưới TKB của 1 lớp: {tiet_label: {day->'mon(gv)'}}. Dùng cho xem."""
    slot_list, _ = build_slots(session)
    days = sorted({s[0] for s in slot_list})
    tiet_labels = []
    seen = set()
    for _thu, buoi, stt in slot_list:
        key = (buoi, stt)
        if key not in seen:
            seen.add(key)
            tiet_labels.append(f'{buoi} {stt}')
    mon = {m.id: m.ma for m in session.query(Mon).all()}
    gv = {g.id: g.ten for g in session.query(GiaoVien).all()}
    day_nhan = {2: 'T2', 3: 'T3', 4: 'T4', 5: 'T5', 6: 'T6', 7: 'T7', 8: 'CN'}
    rows = {tl: {day_nhan.get(d, str(d)): '' for d in days} for tl in tiet_labels}
    for t in session.query(Tkb).filter_by(lop_id=lop_id).all():
        lbl = f'{t.buoi} {t.tiet_stt}'
        if lbl in rows and t.thu in days:
            rows[lbl][day_nhan.get(t.thu, str(t.thu))] = f'{mon.get(t.mon_id, "?")} ({gv.get(t.gv_id, "?")})'
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