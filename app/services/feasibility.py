"""Tính chỉ số khả thi (theo hướng 'Phân tích PCCM' của tkb.com.vn).

Phase 0-1: dùng cho dashboard tổng quan. Quỹ = số ô thời gian trống của GV.
"""
from collections import defaultdict

from app.models import (GiaoVien, Khoi, KhoiMonTiet, Lop, Mon, NgayHoc,
                        PhanCong, Tiet)


def counts(session) -> dict:
    return {
        'co_so': session.query(Lop).with_entities(Lop.co_so_id).distinct().count(),
        'khoi': session.query(Khoi).count(),
        'lop': session.query(Lop).count(),
        'mon': session.query(Mon).count(),
        'gv': session.query(GiaoVien).count(),
        'phan_cong': session.query(PhanCong).count(),
        'ngay_hoc': session.query(NgayHoc).filter_by(active=True).count(),
        'tiet': session.query(Tiet).count(),
    }


def khung_gio(session) -> dict:
    """Số buổi/ngày, số tiết mỗi buổi (cho dashboard/khả thi)."""
    ngay = session.query(NgayHoc).filter_by(active=True).all()
    tiet = session.query(Tiet).all()
    buoi_map = defaultdict(list)
    for t in tiet:
        buoi_map[t.buoi].append(t.stt)
    return {'so_ngay': len(ngay), 'buoi': dict(buoi_map),
            'tong_o_tuan': len(ngay) * len(tiet)}


def bao_cao_phan_cong(session) -> list[dict]:
    """Mỗi GV: tổng tiết phân công, quỹ tối đa (khả dụng), tải công suất."""
    kmt = {(k.khoi_id, k.mon_id): k.so_tiet for k in session.query(KhoiMonTiet).all()}
    pc = defaultdict(int)          # (gv_id) -> tổng tiết/tuần
    lop_id_ten = {l.id: l.ten for l in session.query(Lop).all()}
    lop_khoi = {l.id: l.khoi_id for l in session.query(Lop).all()}
    chi_tiet = defaultdict(list)
    for p in session.query(PhanCong).all():
        so = kmt.get((lop_khoi.get(p.lop_id), p.mon_id), 0)
        pc[p.gv_id] += so
        chi_tiet[p.gv_id].append((lop_id_ten.get(p.lop_id, '?'), '', so))

    tiet = session.query(Tiet).count()
    ngay = session.query(NgayHoc).filter_by(active=True).count()
    quy = ngay * tiet                      # tổng ô GV có thể có (ước lượng)

    rows = []
    for gv in session.query(GiaoVien).all():
        tong = pc.get(gv.id, 0)
        quy_gv = quy  # sẽ cần trừ tiết ${môn}...  giữ đơn giản
        tai = round(tong / quy_gv * 100, 1) if quy_gv else 0
        rows.append({'Mã GV': gv.ma, 'GV': gv.ten, 'Tổng tiết/tuần': tong,
                     'Quỹ ô (tuần)': quy_gv, 'Tải (%)': tai,
                     'Trạng thái': 'An toàn' if tai <= 60 else ('Chú ý' if tai <= 80 else 'Quá tải')})
    return rows