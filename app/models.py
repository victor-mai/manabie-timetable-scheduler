"""SQLAlchemy models cho manabie-timetable-scheduler.

Mô hình dữ liệu theo hướng nghiên cứu (OLM_TKB_RESEARCH + TKBDOTCOM_RESEARCH):
dữ liệu (khối/lớp/môn/GV/tiết/ngày) tách khỏi luật/ràng buộc.
Phase 0-1: các bảng nền; RangBuoc (ràng buộc) bổ sung ở Phase 3.
"""
from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class CoSo(Base):
    """Cơ sở / điểm trường (đa cơ sở)."""
    __tablename__ = 'co_so'
    id = Column(Integer, primary_key=True)
    ten = Column(String(100), nullable=False, default='CS1')
    lop = relationship('Lop', back_populates='co_so')


class Khoi(Base):
    """Khối lớp (vd: 6, 7, 8, 9)."""
    __tablename__ = 'khoi'
    id = Column(Integer, primary_key=True)
    ten = Column(String(50), nullable=False)
    stt = Column(Integer, default=0)
    lop = relationship('Lop', back_populates='khoi')
    khoimontiet = relationship('KhoiMonTiet', back_populates='khoi')


class Lop(Base):
    """Lớp học, thuộc khối và một cơ sở."""
    __tablename__ = 'lop'
    id = Column(Integer, primary_key=True)
    ten = Column(String(50), nullable=False)
    si_so = Column(Integer, default=0)
    co_so_id = Column(ForeignKey('co_so.id'))
    khoi_id = Column(ForeignKey('khoi.id'))
    co_so = relationship('CoSo', back_populates='lop')
    khoi = relationship('Khoi', back_populates='lop')
    phancong = relationship('PhanCong', back_populates='lop')


class Mon(Base):
    """Môn học + ký hiệu viết tắt."""
    __tablename__ = 'mon'
    id = Column(Integer, primary_key=True)
    ma = Column(String(20), nullable=False)
    ten = Column(String(100), nullable=False)
    phancong = relationship('PhanCong', back_populates='mon')


class GiaoVien(Base):
    """Giáo viên + mã viết tắt."""
    __tablename__ = 'giao_vien'
    id = Column(Integer, primary_key=True)
    ma = Column(String(20), nullable=False)
    ten = Column(String(100), nullable=False)
    phancong = relationship('PhanCong', back_populates='gv')


class Tiet(Base):
    """Tiết học, thuộc một buổi (Sáng/Chiều/Tối) theo thứ tự trong buổi."""
    __tablename__ = 'tiet'
    id = Column(Integer, primary_key=True)
    buoi = Column(String(20), default='Sáng')      # Sáng | Chiều | Tối
    stt = Column(Integer, default=1)               # 1..n trong buổi
    nhan = Column(String(30))                       # nhãn, vd 'T1'


class NgayHoc(Base):
    """Ngày học trong tuần (Thứ 2..Chủ nhật), bật/tắt."""
    __tablename__ = 'ngay_hoc'
    id = Column(Integer, primary_key=True)
    thu = Column(Integer, nullable=False)           # 2..8 (Chủ nhật = 8)
    nhan = Column(String(20), nullable=False)       # 'Thứ 2'...
    active = Column(Boolean, default=True)


class PhanCong(Base):
    """Phân công giáo viên dạy môn tại lớp (nền cột PC)."""
    __tablename__ = 'phan_cong'
    id = Column(Integer, primary_key=True)
    lop_id = Column(ForeignKey('lop.id'), nullable=False)
    mon_id = Column(ForeignKey('mon.id'), nullable=False)
    gv_id = Column(ForeignKey('giao_vien.id'), nullable=False)
    lop = relationship('Lop', back_populates='phancong')
    mon = relationship('Mon', back_populates='phancong')
    gv = relationship('GiaoVien', back_populates='phancong')


class KhoiMonTiet(Base):
    """Số tiết quy định/tuần theo khối-môn (+ phân bổ tiết liên tiếp, vd '2,1,1')."""
    __tablename__ = 'khoi_mon_tiet'
    id = Column(Integer, primary_key=True)
    khoi_id = Column(ForeignKey('khoi.id'), nullable=False)
    mon_id = Column(ForeignKey('mon.id'), nullable=False)
    so_tiet = Column(Integer, default=0)
    phan_bo = Column(String(30), default='')        # vd '2,1,1'
    khoi = relationship('Khoi', back_populates='khoimontiet')
    mon = relationship('Mon')