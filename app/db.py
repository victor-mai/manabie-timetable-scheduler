"""Kết nối SQLite — 1 file làm nguồn lưu trữ (xuất/import lại được).

Mặc định file `data.sqlite` trong thư mục làm việc; có thể đổi qua biến môi trường
TKB_DATA hoặc qua nút chọn file trong app (ROADMAP §5.3).
"""
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base


def data_path() -> str:
    p = os.environ.get('TKB_DATA')
    if p:
        return p
    return str(Path(os.getcwd()) / 'data.sqlite')


def build_engine(path: str = None):
    path = path or data_path()
    return create_engine(f'sqlite:///{path}', connect_args={'check_same_thread': False})


def init_db(engine=None, drop=False):
    """Tạo bảng (và tùy chọn drop tất cả để làm mới). Trả về engine."""
    engine = engine or build_engine()
    if drop:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return engine


def make_session(engine=None):
    engine = engine or build_engine()
    return sessionmaker(bind=engine)()