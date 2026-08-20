"""Các trang Streamlit cho manabie-timetable-scheduler (Phase 0-1)."""

import os

import pandas as pd
import streamlit as st

from app import db
from app.models import GiaoVien, Khoi, KhoiMonTiet, Lop, Mon, NgayHoc, Tiet
from app.services import feasibility, phan_cong as pc_svc, rang_buoc as rb_svc, seeder, tkb as tkb_svc
from app.services.import_export import build_workbook
from streamlit import column_config as cfc


# ---------- tiện ích ----------
def session():
    return db.make_session(st.session_state['engine'])


def _nl(s):
    return s or ''


# ---------- Trang tổng quan ----------
def home():
    st.subheader('Tổng quan trường')
    c = feasibility.counts(session())
    left, right = st.columns(2)
    for k, v in [('Cơ sở', c['co_so']), ('Khối', c['khoi']), ('Lớp', c['lop']), ('Môn', c['mon']),
                 ('Giáo viên', c['gv']), ('Phân công', c['phan_cong']), ('Ngày học (bật)', c['ngay_hoc']), ('Tiết/ngày', c['tiet'])]:
        (left if k in ('Cơ sở', 'Khối', 'Lớp', 'Môn') else right).write(f'**{k}:** {v}')
    st.caption(f"Khung giờ: {feasibility.khung_gio(session())}")

    st.divider()
    if st.button('Tạo dữ liệu mẫu 1 trường THCS (2 buổi)', help='Chỉ chạy khi DB trống'):
        r = seeder.seed(session())
        st.write(r)
        st.rerun()

    st.divider()
    st.markdown('**Lưu trữ & di dời dữ liệu (file `.sqlite`)**')
    path = db.data_path()
    c1, c2 = st.columns(2)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            c1.download_button('Tải xuống file dữ liệu (SQLite)', f.read(),
                               file_name=os.path.basename(path), mime='application/octet-stream')
    up = c2.file_uploader('Load lại file SQLite (thay thế dữ liệu hiện tại)', type=['sqlite', 'db'])
    if up is not None:
        eng = st.session_state['engine']
        eng.dispose()
        with open(path, 'wb') as f:
            f.write(up.getvalue())
        st.session_state['engine'] = db.init_db()
        st.success('Đã nạp file SQLite mới.')
        st.rerun()

    st.divider()
    st.markdown('**Xuất Excel (các bảng nền)**')
    s = session()
    sheets = {
        'Khoi': [{'Tên': k.ten} for k in s.query(Khoi).all()],
        'Lop': [{'Lớp': l.ten, 'Khối': l.khoi.ten if l.khoi else '', 'Sĩ số': l.si_so,
                 'Cơ sở': l.co_so.ten if l.co_so else ''} for l in s.query(Lop).all()],
        'Mon': [{'Mã': m.ma, 'Tên': m.ten} for m in s.query(Mon).all()],
        'GiaoVien': [{'Mã': g.ma, 'Tên': g.ten} for g in s.query(GiaoVien).all()],
        'NgayHoc': [{'Thứ': n.nhan, 'Học': 'x' if n.active else ''} for n in s.query(NgayHoc).all()],
        'Tiet': [{'Buổi': t.buoi, 'Thứ tự': t.stt, 'Nhãn': t.nhan} for t in s.query(Tiet).all()],
    }
    st.download_button('Tải xuống Excel (.xlsx)', build_workbook(sheets).getvalue(),
                       file_name='tkb_khaibao.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# ---------- CRUD text đơn giản ----------
def _crud_text(title, Model, fields, cols_def, rows_fn):
    """fields: [(attr, label)]. Chỉ dùng cho entity toàn text."""
    st.subheader(title)
    with st.form(f'form_{title}'):
        vals = [st.text_input(label, key=f'{title}_{attr}') for attr, label in fields]
        if st.form_submit_button('Thêm'):
            try:
                s = session()
                s.add(Model(**dict((a, v) for (a, _), v in zip(fields, vals))))
                s.commit()
                st.toast('Đã thêm')
                st.rerun()
            except Exception as e:
                st.error(f'Lỗi: {e}')
    rows = rows_fn(session())
    if rows:
        st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True)
    else:
        st.info('Chưa có dữ liệu — thêm ở trên hoặc dùng "Tạo dữ liệu mẫu" ở Trang chủ.')


def page_khoi():
    _crud_text('Khai báo — Khối', Khoi, [('ten', 'Tên khối (vd: Khối 6)')],
               [('ten', 'Khối')],
               lambda s: [{'ten': k.ten} for k in s.query(Khoi).order_by(Khoi.stt).all()])


def page_mon():
    _crud_text('Khai báo — Môn học', Mon, [('ma', 'Mã (vd: TOAN)'), ('ten', 'Tên môn')],
               [('ma', 'Mã'), ('ten', 'Môn')],
               lambda s: [{'ma': m.ma, 'ten': m.ten} for m in s.query(Mon).all()])


def page_gv():
    _crud_text('Khai báo — Giáo viên', GiaoVien, [('ma', 'Mã (vd: LAN)'), ('ten', 'Họ tên GV')],
               [('ma', 'Mã'), ('ten', 'Giáo viên')],
               lambda s: [{'ma': g.ma, 'ten': g.ten} for g in s.query(GiaoVien).all()])


def page_lop():
    st.subheader('Khai báo — Lớp học')
    s = session()
    khoi_list = s.query(Khoi).order_by(Khoi.stt).all()
    if not khoi_list:
        st.info('Hãy khai báo Khối trước.')
        return
    khoi_opt = {k.ten: k.id for k in khoi_list}
    with st.form('form_lop'):
        ten = st.text_input('Lớp (vd: 6A)')
        khoi_label = st.selectbox('Khối', list(khoi_opt.keys()))
        ss = st.number_input('Sĩ số', min_value=0, value=30, step=1)
        cid = st.selectbox('Cơ sở', [1], disabled=True)  # đơn cơ sở ở Phase này
        if st.form_submit_button('Thêm'):
            try:
                s.add(Lop(ten=ten.strip(), khoi_id=khoi_opt[khoi_label], si_so=int(ss)))
                s.commit()
                st.toast('Đã thêm')
                st.rerun()
            except Exception as e:
                st.error(f'Lỗi: {e}')
    rows = [{'Lớp': l.ten, 'Khối': l.khoi.ten if l.khoi else '', 'Sĩ số': l.si_so}
            for l in s.query(Lop).all()]
    st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True) if rows else st.info('Chưa có lớp.')


def page_tiet():
    st.subheader('Khai báo — Tiết học & Buổi')
    s = session()
    with st.form('form_tiet'):
        buoi = st.selectbox('Buổi', ['Sáng', 'Chiều', 'Tối'])
        stt = st.number_input('Thứ tự trong buổi (1..n)', min_value=1, value=1, step=1)
        nhan = st.text_input('Nhãn (vd: T5)')
        if st.form_submit_button('Thêm tiết'):
            try:
                s.add(Tiet(buoi=buoi, stt=int(stt), nhan=nhan.strip()))
                s.commit()
                st.toast('Đã thêm')
                st.rerun()
            except Exception as e:
                st.error(f'Lỗi: {e}')
    rows = [{'Buổi': t.buoi, 'Thứ tự': t.stt, 'Nhãn': t.nhan} for t in s.query(Tiet).all()]
    st.dataframe(pd.DataFrame(rows), width='stretch', hide_index=True) if rows else st.info('Chưa có tiết.')


def page_ngay():
    st.subheader('Khai báo — Ngày học trong tuần')
    s = session()
    rows = s.query(NgayHoc).order_by(NgayHoc.thu).all()
    if not rows:
        st.info('Chưa có dữ liệu — dùng "Tạo dữ liệu mẫu" ở Trang chủ.')
        return
    st.caption('Bật/tắt ngày học ở cột "Học".')
    edit = st.data_editor(pd.DataFrame([{'Thứ': n.nhan, 'Học': bool(n.active)} for n in rows]),
                          width='stretch', hide_index=True, key='ded_ngay')
    if st.button('Lưu ngày học'):
        for n, ch in zip(rows, edit['Học'].tolist()):
            n.active = bool(ch)
        s.commit()
        st.toast('Đã lưu')
        st.rerun()


# ---------- Phase 2 ----------
def page_so_tiet():
    st.subheader('Khối – Môn – Số tiết')
    s = session()
    khoi_list = s.query(Khoi).order_by(Khoi.stt).all()
    mon_list = s.query(Mon).order_by(Mon.ten).all()
    if not khoi_list or not mon_list:
        st.info('Cần khai báo Khối và Môn trước (hoặc dùng "Tạo dữ liệu mẫu" ở Trang chủ).')
        return

    kmt = {(k.khoi_id, k.mon_id): k for k in s.query(KhoiMonTiet).all()}
    k_by_ten = {k.ten: k.id for k in khoi_list}
    mcols = [m.ten for m in mon_list]

    st.caption('Ô = số tiết/tuần môn đó của khối (0 = môn không có trong chương trình khối).')
    df = [{**{'Khối': k.ten}, **{m.ten: (kmt[(k.id, m.id)].so_tiet if (k.id, m.id) in kmt else 0) for m in mon_list}}
          for k in khoi_list]
    edited = st.data_editor(pd.DataFrame(df), width='stretch', hide_index=True, key='ed_so_tiet')

    st.caption('Phân bổ tiết liên tiếp (tuỳ chọn), vd Toán 4 tiết -> `2,1,1`. Để trống nếu không có.')
    df_bo = [{**{'Khối': k.ten},
              **{m.ten: (kmt[(k.id, m.id)].phan_bo if (k.id, m.id) in kmt and kmt[(k.id, m.id)].so_tiet else '') for m in mon_list}}
             for k in khoi_list]
    ed_bo = st.data_editor(pd.DataFrame(df_bo), width='stretch', hide_index=True, key='ed_phanbo')

    if st.button('Lưu số tiết khối–môn'):
        for _, r in edited.iterrows():
            kid = k_by_ten[r['Khối']]
            for m in mon_list:
                v = int(r[m.ten] or 0)
                pb = ''
                if v > 0:
                    poc = ed_bo.loc[(ed_bo['Khối'] == r['Khối'])]
                    pb = (poc.iloc[0][m.ten] or '') if not poc.empty else ''
                pc_svc.set_so_tiet(s, kid, m.id, v, phan_bo=pb.strip())
        s.commit()
        st.toast('Đã lưu số tiết')
        st.rerun()

    prog = pc_svc.program_map(s)
    st.caption('Tổng tiết/tuần theo khối:')
    for k in khoi_list:
        st.caption(f'  • {k.ten}: **{sum(prog.get(k.id, {}).values())} tiết/tuần**')


def page_phan_cong():
    st.subheader('Phân công giảng dạy (GV – Môn – Lớp)')
    s = session()
    prog = pc_svc.program_map(s)
    if not prog:
        st.info('Chưa có chương trình (số tiết khối–môn). Vào "Số tiết khối-môn" đặt số tiết trước.')
        return

    lop_id_of = {l.ten: l.id for l in s.query(Lop).all()}
    mon_ten_of = {m.id: m.ten for m in s.query(Mon).all()}
    mon_id_of = {m.ten: m.id for m in s.query(Mon).all()}
    gv = {g.id: g.ten for g in s.query(GiaoVien).all()}
    lop = {l.id: l for l in s.query(Lop).all()}
    pc = pc_svc.pc_map(s)

    rows = []
    for lid in sorted(lop, key=lambda x: (lop[x].khoi_id, lop[x].ten)):
        for mid, so in prog.get(lop[lid].khoi_id, {}).items():
            gvid = pc.get((lid, mid))
            rows.append({'Lớp': lop[lid].ten, 'Môn': mon_ten_of.get(mid, '?'),
                         'Số tiết': so, 'Giáo viên': gv.get(gvid, '')})

    gv_names = ['' ] + sorted(gv.values())
    gv_by_name = {t: i for i, t in gv.items()}

    from streamlit import column_config as cfc
    edited = st.data_editor(
        pd.DataFrame(rows), width='stretch', hide_index=True, key='ed_phan_cong',
        column_config={'Giáo viên': cfc.SelectboxColumn('Giáo viên', options=gv_names, required=False)},
        disabled=['Lớp', 'Môn', 'Số tiết'])

    col_b, col_c = st.columns([3, 1])
    if col_b.button('Lưu phân công'):
        for _, r in edited.iterrows():
            lop_id = lop_id_of.get(r['Lớp'])
            mon_id = mon_id_of.get(r['Môn'])
            if lop_id is None or mon_id is None:
                continue
            gvid = gv_by_name.get(r['Giáo viên'])
            pc_svc.set_phan_cong(s, lop_id, mon_id, gvid)
        s.commit()
        st.toast('Đã lưu phân công')
        st.rerun()

    if col_c.button('Kiểm tra phân công'):
        issues = pc_svc.kiem_tra(s)
        if issues:
            st.warning(f'Có {len(issues)} vấn đề:')
            st.dataframe(pd.DataFrame(issues), width='stretch', hide_index=True)
        else:
            st.success('Phân công khả thi: mọi (lớp, môn) đã có GV & số tiết.')


DAY_NHAN = {2: 'T2', 3: 'T3', 4: 'T4', 5: 'T5', 6: 'T6', 7: 'T7', 8: 'CN'}
DAY_SO = {v: k for k, v in DAY_NHAN.items()}


def page_xep_tkb():
    st.subheader('Xếp thời khóa biểu')
    s = session()

    has = tkb_svc.da_co(s)
    # ---- Xuất / quản lý kết quả ----
    c1, c2, c3 = st.columns([1, 1, 3])
    to = c1.selectbox('Thời gian solver (giây)', [15, 60, 120, 300], index=1)
    if c2.button('🧮 Auto xếp'):
        with st.spinner('Đang xếp...'):
            r = tkb_svc.solve(s, timeout_ms=int(to) * 1000)
        if r['status'] == 'sat':
            st.success(f"Đã xếp **{r['so_o']}** tiết (bấm lại trang để cập nhật)."); st.rerun()
        else:
            st.error(r['error'] or 'Không xếp được.')
    if c3.button('🗑 Xóa TKB đã xếp', disabled=not has):
        tkb_svc.clear(s); st.rerun()

    # ---- Trạng thái & xung đột ----
    if not has:
        st.info('Chưa có TKB. Nhấn "Auto xếp" (cần đã Phân công + Số tiết ở Phase 2) hoặc xếp tay bên dưới.')
        return
    cells = tkb_svc.load(s)
    st.caption(f'Đã xếp {len(cells)} tiết.')
    xd = tkb_svc.xung_dot(s)
    st.warning(f'Xung đột hiện có: **{len(xd)}**') if xd else st.success('Không có xung đột trùng giờ.')

    # ---- Xem theo lớp ----
    st.markdown('#### Xem TKB theo lớp')
    lop_list = [(l.id, l.ten) for l in s.query(Lop).order_by(Lop.khoi_id, Lop.ten).all()]
    lop_of = dict(lop_list)
    lop_id = st.selectbox('Chọn lớp', list(lop_of.keys()),
                          format_func=lambda x: f"{lop_of[x]}", key='sel_lop')
    rows, tiet_labels, days = tkb_svc.grid(s, lop_id)
    cols = ['Tiết'] + [DAY_NHAN.get(d, str(d)) for d in days]
    dfg = pd.DataFrame([{'Tiết': tl, **rows[tl]} for tl in tiet_labels])[cols]
    st.dataframe(dfg, width='stretch', hide_index=True)
    if len(xd):
        st.caption('Chi tiết xung đột:')
        st.json([{k: v for k, v in x.items()} for x in xd][:20])

    # ---- Chỉnh tay theo lớp ----
    st.markdown('#### Xếp / chỉnh tay cho lớp')
    opts = tkb_svc.mon_options_for_lop(s, lop_id)
    if not opts:
        st.info('Lớp này chưa có môn được phân công để xếp.')
    else:
        mon_names = [''] + [o['ten'] for o in opts]
        day_cols = [DAY_NHAN.get(d, str(d)) for d in days]
        edit = [{**{'Tiết': tl}, **{dc: (rows[tl].get(dc, '') or '').rsplit(' (', 1)[0] for dc in day_cols}}
                for tl in tiet_labels]
        ed = st.data_editor(
            pd.DataFrame(edit)[['Tiết'] + day_cols], width='stretch', hide_index=True,
            key=f'ed_tkb_{lop_id}', disabled=['Tiết'],
            column_config={dc: cfc.SelectboxColumn(dc, options=mon_names, required=False) for dc in day_cols})
        if st.button('Lưu TKB lớp này', key=f'save_{lop_id}'):
            ten2id = {o['ten']: (o['mon_id'], o['gv_id']) for o in opts}
            new = []
            for _, r in ed.iterrows():
                buoi, stt = r['Tiết'].split()
                stt = int(stt)
                for dc in day_cols:
                    val = (r[dc] or '').strip()
                    if val and val in ten2id:
                        mid, gid = ten2id[val]
                        new.append({'lop_id': lop_id, 'mon_id': mid, 'gv_id': gid,
                                    'thu': DAY_SO[dc], 'buoi': buoi, 'tiet_stt': stt})
            tkb_svc.replace_lop(s, lop_id, new)
            xd2 = tkb_svc.xung_dot(s)
            st.toast(f'Đã lưu {len(new)} ô. Xung đột toàn trường: {len(xd2)}')
            st.rerun()


def page_cau_hinh():
    st.subheader('Cấu hình ràng buộc')
    st.caption('Đây là các ràng buộc solver sẽ tôn trọng khi xếp (Phase 4). Có thể thêm/xoá/sửa bằng bảng dưới.')
    s = session()

    gv_list = [g.ten for g in s.query(GiaoVien).order_by(GiaoVien.ten).all()]
    mon_list = [m.ten for m in s.query(Mon).order_by(Mon.ten).all()]
    thu_opt = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
    buoi_opt = ['Sáng', 'Chiều', 'Tối']

    # ---- 1) GV nghỉ / bận ----
    st.markdown('#### 1. Giáo viên nghỉ / bận')
    st.caption('GV + Thứ, **để trống Buổi/Tiết = nghỉ cả ngày**; nhập Buổi + Tiết = bận đúng tiết đó buổi đó.')
    rows = rb_svc.df_gv_nghi(s)
    ed_gv = st.data_editor(
        pd.DataFrame(rows), width='stretch', hide_index=True, num_rows='dynamic', key='ed_rb_gv',
        column_config={'GV': cfc.SelectboxColumn('GV', options=[''] + gv_list, required=True),
                       'Thứ': cfc.SelectboxColumn('Thứ', options=thu_opt),
                       'Buổi': cfc.SelectboxColumn('Buổi', options=buoi_opt, required=False),
                       'Tiết': cfc.NumberColumn('Tiết', min_value=1, max_value=12)})
    if st.button('Lưu GV nghỉ'):
        rb_svc.save_gv_nghi(s, ed_gv.to_dict('records')); s.commit()
        st.toast('Đã lưu ràng buộc GV nghỉ'); st.rerun()

    # ---- 2) Môn cố định ----
    st.markdown('#### 2. Môn cố định (phải học đúng thứ – buổi – tiết)')
    rows = rb_svc.df_mon_co_dinh(s)
    ed_mon = st.data_editor(
        pd.DataFrame(rows), width='stretch', hide_index=True, num_rows='dynamic', key='ed_rb_mon',
        column_config={'Môn': cfc.SelectboxColumn('Môn', options=mon_list, required=True),
                       'Thứ': cfc.SelectboxColumn('Thứ', options=thu_opt),
                       'Buổi': cfc.SelectboxColumn('Buổi', options=buoi_opt, required=True),
                       'Tiết': cfc.NumberColumn('Tiết', min_value=1, max_value=12)})
    if st.button('Lưu môn cố định'):
        rb_svc.save_mon_co_dinh(s, ed_mon.to_dict('records')); s.commit()
        st.toast('Đã lưu môn cố định'); st.rerun()

    # ---- 3) Giới hạn số tiết / buổi ----
    st.markdown('#### 3. Giới hạn số tiết mỗi buổi cho 1 giáo viên')
    rows = rb_svc.df_gioi_han(s)
    ed_gh = st.data_editor(
        pd.DataFrame(rows), width='stretch', hide_index=True, num_rows='dynamic', key='ed_rb_gh',
        column_config={'GV': cfc.SelectboxColumn('GV', options=[''] + gv_list, required=True),
                       'Buổi': cfc.SelectboxColumn('Buổi', options=buoi_opt, required=True),
                       'Giới hạn (tiết/buổi)': cfc.NumberColumn('Giới hạn (tiết/buổi)', min_value=1, max_value=12)})
    if st.button('Lưu giới hạn'):
        rb_svc.save_gioi_han(s, ed_gh.to_dict('records')); s.commit()
        st.toast('Đã lưu giới hạn'); st.rerun()

    st.caption(f"Tổng: {rb_svc.tong_hop(s)}")


def trang_xuat():
    st.subheader('Xuất bản & Phân phối (Phase 5)')
    st.info('Sẽ xây ở Phase 5: xuất Excel TKB, in, đóng gói ZIP/exe.')


def trang_nang_cao():
    st.subheader('Nâng cao (Phase 6)')
    st.info('Sẽ xây ở Phase 6: tổ hợp môn, ghép/tách lớp, nhiều GV, đa cơ sở, xếp phòng, PCCM.')