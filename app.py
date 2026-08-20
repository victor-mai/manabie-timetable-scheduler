"""manabie-timetable-scheduler — ứng dụng xếp thời khóa biểu (Streamlit, Phase 0-1).

Chạy:  streamlit run app.py   (hoặc .venv/Scripts/python.exe -m streamlit run app.py)
Cửa sổ trình duyệt tự mở localhost. Toàn bộ dữ liệu lưu trong 1 file `data.sqlite`.
"""
import os
import sys

import streamlit as st

# đảm bảo import được gói app khi chạy từ repo root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import db
from app.ui import pages

st.set_page_config(page_title='Xếp Thời Khóa Biểu', page_icon='🗓️', layout='wide')


def boots():
    """Khởi tạo engine một lần (lưu trong session_state)."""
    if 'engine' not in st.session_state:
        st.session_state['engine'] = db.init_db()
    return st.session_state['engine']


def main():
    boots()

    nav = {
        'Trang chủ': [
            st.Page(pages.home, title='🏠 Tổng quan & Dữ liệu', url_path='home'),
        ],
        'Khai báo dữ liệu': [
            st.Page(pages.page_khoi, title='Khối', url_path='khoi'),
            st.Page(pages.page_lop, title='Lớp học', url_path='lop'),
            st.Page(pages.page_mon, title='Môn học', url_path='mon'),
            st.Page(pages.page_gv, title='Giáo viên', url_path='giao-vien'),
            st.Page(pages.page_tiet, title='Tiết & Buổi', url_path='tiet'),
            st.Page(pages.page_ngay, title='Ngày học', url_path='ngay-hoc'),
        ],
        'Phân công & Số tiết (P2)': [
            st.Page(pages.page_phan_cong, title='Phân công giảng dạy', url_path='phan-cong'),
            st.Page(pages.page_so_tiet, title='Số tiết khối-môn', url_path='so-tiet'),
        ],
        'Cấu hình ràng buộc (P3)': [
            st.Page(pages.page_cau_hinh, title='Ràng buộc (GV nghỉ / môn cố định / giới hạn)', url_path='cau-hinh'),
        ],
        'Sắp tới (P4–6)': [
            st.Page(pages.trang_xep_tkb, title='Xếp TKB (P4)', url_path='xep-tkb'),
            st.Page(pages.trang_xuat, title='Xuất bản (P5)', url_path='xuat-ban'),
            st.Page(pages.trang_nang_cao, title='Nâng cao (P6)', url_path='nang-cao'),
        ],
    }

    pg = st.navigation(nav)
    # thông tin file dữ liệu ở sidebar
    st.sidebar.caption('')
    st.sidebar.caption(f'📄 File dữ liệu: `{db.data_path()}`')
    st.sidebar.caption('Phase hiện tại: 0–3 (Khai báo + Phân công + Số tiết + Ràng buộc)')

    pg.run()


if __name__ == '__main__':
    main()