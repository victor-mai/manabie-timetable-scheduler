"""Dữ liệu mẫu: 1 trường THCS (2 buổi) — giả lập để test từ Phase 1.

Số tiết/tuần chỉ là số mẫu hợp lý (theo GDPT 2018), nhà trường sẽ chỉnh số thật.
"""
from app.models import (CoSo, GiaoVien, Khoi, KhoiMonTiet, Lop, Mon, NgayHoc,
                        PhanCong, Tiet)

# (ma, ten)
MON = [
    ('TOAN', 'Toán'), ('NV', 'Ngữ văn'), ('TA', 'Tiếng Anh'),
    ('KHTN', 'Khoa học tự nhiên'), ('LS-DL', 'Lịch sử và Địa lí'),
    ('GDCD', 'Giáo dục công dân'), ('TIN', 'Tin học'), ('CN', 'Công nghệ'),
    ('TD', 'Giáo dục thể chất'), ('HDTN', 'Hoạt động trải nghiệm - hướng nghiệp'),
    ('AN', 'Âm nhạc'), ('MT', 'Mĩ thuật'),
]

# số tiết/tuần theo khối (chỉ môn nào khối đó có)
SO_TIET = {
    6: {'TOAN':4, 'NV':4, 'TA':3, 'KHTN':4, 'LS-DL':3, 'GDCD':1, 'TIN':2, 'CN':2, 'TD':2, 'HDTN':1, 'AN':1, 'MT':1},
    7: {'TOAN':4, 'NV':4, 'TA':3, 'KHTN':4, 'LS-DL':3, 'GDCD':1, 'TIN':2, 'CN':2, 'TD':2, 'HDTN':1, 'AN':1, 'MT':1},
    8: {'TOAN':4, 'NV':4, 'TA':3, 'KHTN':3, 'LS-DL':2, 'GDCD':1, 'TIN':2, 'CN':2, 'TD':2, 'HDTN':1},
    9: {'TOAN':4, 'NV':4, 'TA':3, 'KHTN':3, 'LS-DL':2, 'GDCD':1, 'TIN':2, 'CN':2, 'TD':2, 'HDTN':1},
}

# phân bổ tiết liên tiếp (thử 1 môn theo ví dụ OLM '2,1,1')
PHAN_BO = {('TOAN', 6): '2,1,1'}

# (ma, ten) giáo viên — phân theo môn đảm nhiệm
GV = [
    ('LAN', 'Nguyễn Thị Lan', 'TOAN'), ('HUNG', 'Trần Quốc Hùng', 'TOAN'),
    ('MAI', 'Lê Thị Mai', 'NV'), ('QUAN', 'Phạm Văn Quân', 'NV'),
    ('NGAN', 'Hoàng Thu Ngân', 'TA'), ('VIET', 'Trần Minh Việt', 'TA'),
    ('THAO', 'Đỗ Thị Thảo', 'KHTN'), ('DUC', 'Nguyễn Văn Đức', 'KHTN'),
    ('HUONG', 'Phan Thanh Hương', 'LS-DL'), ('KHOA', 'Vũ Đình Khoa', 'LS-DL'),
    ('BINH', 'Ngô Thị Bình', 'GDCD'), ('SON', 'Đặng Quang Sơn', 'TIN'),
    ('DUONG', 'Lê Văn Dương', 'CN'), ('THANH', 'Bùi Minh Thanh', 'TIN'),
    ('PHUONG', 'Vũ Thị Phương', 'TD'), ('GIA', 'Nguyễn Thế Gia', 'TD'),
    ('TIEP', 'Cao Văn Tiếp', 'HDTN'), ('YEN', 'Trịnh Thu Yến', 'AN'),
    ('LAM', 'Phạm Quỳnh Lam', 'MT'),
]

# Giả lập: 1 cơ sở, 8 lớp (2 mỗi khối), si_so mẫu
LOP = [(6, '6A', 36), (6, '6B', 35), (7, '7A', 34), (7, '7B', 33),
       (8, '8A', 35), (8, '8B', 34), (9, '9A', 36), (9, '9B', 35)]


def _chua_co(session) -> bool:
    return session.query(CoSo).first() is None


def seed(session) -> dict:
    """Seed dữ liệu mẫu nếu DB trống. Trả về dict đếm."""
    if not _chua_co(session):
        return {'status': 'đã có dữ liệu', 'created': 0}

    cs = CoSo(ten='Trường THCS Cơ sở chính')
    session.add(cs)
    session.flush()

    # thêm môn tường minh
    mon_obj = {}
    for ma, ten in MON:
        m = Mon(ma=ma, ten=ten)
        session.add(m)
        session.flush()
        mon_obj[ma] = m

    gv_obj = []
    gphai_by_ma = {}
    for ma, ten, monda in GV:
        g = GiaoVien(ma=ma, ten=ten)
        session.add(g)
        session.flush()
        gv_obj.append(g)
        gphai_by_ma.setdefault(monda, []).append(g)

    khoi_obj = {}
    for k in (6, 7, 8, 9):
        ko = Khoi(ten=f'Khối {k}', stt=k)
        session.add(ko)
        session.flush()
        khoi_obj[k] = ko

    lop_obj = []
    for k, ten, ss in LOP:
        lo = Lop(ten=ten, si_so=ss, co_so_id=cs.id, khoi_id=khoi_obj[k].id)
        session.add(lo)
        session.flush()
        lop_obj.append(lo)

    # tiết: 2 buổi, mỗi buổi 4 tiết
    for buoi, tiet_list in (('Sáng', ['T1', 'T2', 'T3', 'T4']),
                            ('Chiều', ['T5', 'T6', 'T7', 'T8'])):
        for i, n in enumerate(tiet_list, start=1):
            session.add(Tiet(buoi=buoi, stt=i, nhan=n))

    # ngày học: Thứ 2 - 7 học (Chủ nhật nghỉ)
    for thu, nhan, active in ((2, 'Thứ 2', True), (3, 'Thứ 3', True), (4, 'Thứ 4', True),
                              (5, 'Thứ 5', True), (6, 'Thứ 6', True), (7, 'Thứ 7', True),
                              (8, 'Chủ nhật', False)):
        session.add(NgayHoc(thu=thu, nhan=nhan, active=active))

    # KhoiMonTiet + PhanCong
    n_pc = n_kmt = 0
    for k, mons in SO_TIET.items():
        for ma, so in mons.items():
            kmt = KhoiMonTiet(khoi_id=khoi_obj[k].id, mon_id=mon_obj[ma].id,
                              so_tiet=so, phan_bo=PHAN_BO.get((ma, k), ''))
            session.add(kmt)
            n_kmt += 1
            # phân công: mỗi lớp trong khối -> 1 GV môn đó (round robin theo môn)
            teachers = gphai_by_ma.get(ma, [GiaoVien(ma='N/A', ten='(chưa xếp)')])
            for lop in [l for l in lop_obj if l.khoi_id == khoi_obj[k].id]:
                gv = teachers[(lop.id) % len(teachers)]
                session.add(PhanCong(lop_id=lop.id, mon_id=mon_obj[ma].id, gv_id=gv.id))
                n_pc += 1

    session.commit()
    return {'status': 'đã seed', 'co_so': 1, 'khoi': 4, 'lop': len(lop_obj),
            'mon': len(MON), 'gv': len(gv_obj), 'phan_cong': n_pc, 'khoi_mon_tiet': n_kmt}