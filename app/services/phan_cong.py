"""Nghiệp vụ Phase 2: phân công giảng dạy + set số tiết khối-môn + kiểm tra khả thi."""

from app.models import GiaoVien, Khoi, KhoiMonTiet, Lop, Mon, PhanCong


def program_map(session) -> dict:
    """khối_id -> {mon_id: so_tiet} chỉ lấy môn có so_tiet>0."""
    out = {}
    for k in session.query(KhoiMonTiet).filter(KhoiMonTiet.so_tiet > 0).all():
        out.setdefault(k.khoi_id, {})[k.mon_id] = k.so_tiet
    return out


def pc_map(session) -> dict:
    """(lop_id, mon_id) -> gv_id"""
    return {(p.lop_id, p.mon_id): p.gv_id for p in session.query(PhanCong).all()}


def set_so_tiet(session, khoi_id, mon_id, so_tiet, phan_bo=''):
    row = (session.query(KhoiMonTiet)
           .filter_by(khoi_id=khoi_id, mon_id=mon_id).first())
    if so_tiet <= 0:
        if row:
            row.so_tiet = 0                      # giữ row nhưng tắt (không thuộc chương trình)
            row.phan_bo = ''
        return
    if row is None:
        session.add(KhoiMonTiet(khoi_id=khoi_id, mon_id=mon_id,
                                so_tiet=so_tiet, phan_bo=phan_bo))
    else:
        row.so_tiet = so_tiet
        if phan_bo:
            row.phan_bo = phan_bo


def set_phan_cong(session, lop_id, mon_id, gv_id):
    row = (session.query(PhanCong)
           .filter_by(lop_id=lop_id, mon_id=mon_id).first())
    if gv_id is None:
        if row:
            session.delete(row)                  # bỏ phân công
        return
    if row is None:
        session.add(PhanCong(lop_id=lop_id, mon_id=mon_id, gv_id=gv_id))
    else:
        row.gv_id = gv_id


def kiem_tra(session) -> list[dict]:
    """Trả các vấn đề khi phân công: thiếu GV, môn thừa, số tiết=0, GV gán trùng (Lớp,Môn)."""
    issues = []
    lop = {l.id: l for l in session.query(Lop).all()}
    mon = {m.id: m for m in session.query(Mon).all()}
    prog = program_map(session)
    pc = pc_map(session)

    # (Lớp,Môn) đang có phân công nhưng không thuộc chương trình khối
    for (lid, mid), gvid in pc.items():
        khoi_id = lop[lid].khoi_id
        if mid not in prog.get(khoi_id, {}):
            mon_ten = mon[mid].ten if mid in mon else '?'
            issues.append({'mức': 'thừa', 'nội dung': f"{lop[lid].ten} – {mon_ten}: không thuộc chương trình khối (số tiết=0)"})

    # thiếu GV + số tiết chưa đặt
    for lid in lop:
        khoi_id = lop[lid].khoi_id
        for mid, so in prog.get(khoi_id, {}).items():
            if (lid, mid) not in pc:
                mten = mon[mid].ten if mid in mon else '?'
                issues.append({'mức': 'thiếu', 'nội dung': f"{lop[lid].ten} – {mten}: chưa phân công GV"})
    return issues


def tong_hop_phan_cong(session) -> list[dict]:
    """Mỗi lớp-môn: phân công hiện có + số tiết (phục vụ màn hình)."""
    lop = {l.id: l for l in session.query(Lop).all()}
    mon = {m.id: m for m in session.query(Mon).all()}
    gv = {g.id: g for g in session.query(GiaoVien).all()}
    prog = program_map(session)
    pc = pc_map(session)
    rows = []
    for lid in sorted(lop, key=lambda x: (lop[x].khoi_id, lop[x].ten)):
        khoi_id = lop[lid].khoi_id
        for mid, so in prog.get(khoi_id, {}).items():
            gvid = pc.get((lid, mid))
            rows.append({
                'Lớp': lop[lid].ten,
                'Môn': mon[mid].ten if mid in mon else '?',
                'Số tiết': so,
                'Giáo viên': gv[gvid].ten if gvid in gv else '',
            })
    return rows