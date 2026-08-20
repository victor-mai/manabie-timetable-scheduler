"""Ràng buộc (Phase 3) — đọc/xuất ra bảng chỉnh + lưu thay thế theo loại.

Quy ước thu: 2..8 (2=Thứ 2 .. 8=Chủ nhật).
"""
from app.models import GiaoVien, Mon, RangBuoc

THU_NHAN = {2: 'Thứ 2', 3: 'Thứ 3', 4: 'Thứ 4', 5: 'Thứ 5',
            6: 'Thứ 6', 7: 'Thứ 7', 8: 'Chủ nhật'}
THU_SO = {v: k for k, v in THU_NHAN.items()}
BUOI_NHAN = ['Sáng', 'Chiều', 'Tối']


def _gv_names(s):
    return {g.id: g.ten for g in s.query(GiaoVien).all()}


def _mon_names(s):
    return {m.id: m.ten for m in s.query(Mon).all()}


def _thu_nhan(t):
    return THU_NHAN.get(t, '')


# ---------- Xuất df cho từng loại ----------
def df_gv_nghi(s):
    """GV nghỉ; dòng không có Buổi = nghỉ cả ngày, có Buổi+Tiết = bận tiết đó."""
    gv = _gv_names(s)
    rows = []
    for r in s.query(RangBuoc).filter(RangBuoc.loai.in_(['GV_NGAY_NGHI', 'GV_TIET_NGHI'])).all():
        rows.append({'GV': gv.get(r.gv_id, ''), 'Thứ': _thu_nhan(r.thu),
                     'Buổi': r.buoi or '', 'Tiết': r.tiet_stt if r.tiet_stt else ''})
    return rows


def df_mon_co_dinh(s):
    mon = _mon_names(s)
    return [{'Môn': mon.get(r.mon_id, ''), 'Thứ': _thu_nhan(r.thu),
             'Buổi': r.buoi or '', 'Tiết': r.tiet_stt if r.tiet_stt else ''}
            for r in s.query(RangBuoc).filter_by(loai='MON_CO_DINH').all()]


def df_gioi_han(s):
    gv = _gv_names(s)
    return [{'GV': gv.get(r.gv_id, ''), 'Buổi': r.buoi or '', 'Giới hạn (tiết/buổi)': r.gia_tri}
            for r in s.query(RangBuoc).filter_by(loai='GIOI_HAN_TIET_BUOI').all()]


# ---------- Lưu thay thế theo loại ----------
def _replace(s, loai, new_rows):
    for old in s.query(RangBuoc).filter_by(loai=loai).all():
        s.delete(old)
    for row in new_rows:
        s.add(RangBuoc(**row))
    s.flush()


def save_gv_nghi(s, df_rows):
    gv_id = {t: i for i, t in _gv_names(s).items()}
    new = []
    for r in df_rows:
        gid = gv_id.get(r['GV'])
        thu = THU_SO.get(r.get('Thứ'), None)
        if gid is None or thu is None:
            continue
        buoi = (r.get('Buổi') or '').strip()
        tiet = r.get('Tiết')
        if buoi:
            try:
                tiet = int(tiet)
            except (TypeError, ValueError):
                tiet = None
            if tiet:
                new.append({'loai': 'GV_TIET_NGHI', 'gv_id': gid, 'thu': thu,
                            'buoi': buoi, 'tiet_stt': tiet})
        else:
            new.append({'loai': 'GV_NGAY_NGHI', 'gv_id': gid, 'thu': thu})
    _replace(s, 'GV_NGAY_NGHI', [n for n in new if n['loai'] == 'GV_NGAY_NGHI'])
    _replace(s, 'GV_TIET_NGHI', [n for n in new if n['loai'] == 'GV_TIET_NGHI'])


def save_mon_co_dinh(s, df_rows):
    mon_id = {t: i for i, t in _mon_names(s).items()}
    new = []
    for r in df_rows:
        mid = mon_id.get(r.get('Môn'))
        thu = THU_SO.get(r.get('Thứ'))
        buoi = (r.get('Buổi') or '').strip()
        try:
            tiet = int(r.get('Tiết'))
        except (TypeError, ValueError):
            tiet = None
        if mid and thu and buoi and tiet:
            new.append({'loai': 'MON_CO_DINH', 'mon_id': mid, 'thu': thu,
                        'buoi': buoi, 'tiet_stt': tiet})
    _replace(s, 'MON_CO_DINH', new)


def save_gioi_han(s, df_rows):
    gv_id = {t: i for i, t in _gv_names(s).items()}
    new = []
    for r in df_rows:
        gid = gv_id.get(r.get('GV'))
        buoi = (r.get('Buổi') or '').strip()
        try:
            gi = int(r.get('Giới hạn (tiết/buổi)'))
        except (TypeError, ValueError):
            gi = None
        if gid and buoi and gi:
            new.append({'loai': 'GIOI_HAN_TIET_BUOI', 'gv_id': gid,
                        'buoi': buoi, 'gia_tri': gi})
    _replace(s, 'GIOI_HAN_TIET_BUOI', new)


def tong_hop(s) -> dict:
    return {'gv_nghi': len(df_gv_nghi(s)), 'mon_co_dinh': len(df_mon_co_dinh(s)),
            'gioi_han': len(df_gioi_han(s))}