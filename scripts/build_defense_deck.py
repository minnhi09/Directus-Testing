#!/usr/bin/env python3
"""Dung ban slide bao ve (nhap) tu bao cao K05 bang python-pptx. Chay: python scripts/build_defense_deck.py

Noi dung lay tu docs/k05/BAO_CAO_CUOI_KY_K05.md; moi con so co nguon trong bao cao. Day la BAN NHAP: nhom can xem
va chinh bang mat (bo cuc, co chu) va tu phan nguoi trinh bay truoc khi dung.
"""
from __future__ import annotations

import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

OUT = Path(__file__).resolve().parents[1] / "docs" / "k05" / "wp9" / "slide-bao-ve-k05.pptx"
NAVY = RGBColor(0x1F, 0x3A, 0x5F)
TEAL = RGBColor(0x1B, 0x7F, 0x8C)
INK = RGBColor(0x22, 0x2B, 0x36)
GREY = RGBColor(0x6B, 0x74, 0x80)
LIGHT = RGBColor(0xEE, 0xF3, 0xF8)
RED = RGBColor(0xB4, 0x32, 0x32)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
TOTAL = 16
state = {"n": 0}


def textbox(slide, x, y, w, h, text="", size=18, bold=False, color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = "Calibri"
    return tb


def new_slide(title, source=None):
    state["n"] += 1
    s = prs.slides.add_slide(BLANK)
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.05))
    bar.fill.solid()
    bar.fill.fore_color.rgb = NAVY
    bar.line.fill.background()
    textbox(s, Inches(0.5), Inches(0.15), Inches(12.3), Inches(0.8), title, size=30, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    foot = f"Nguồn: báo cáo K05, {source}" if source else "Báo cáo cuối kỳ K05"
    textbox(s, Inches(0.5), Inches(7.0), Inches(10.5), Inches(0.35), foot, size=11, color=GREY)
    textbox(s, Inches(11.8), Inches(7.0), Inches(1.1), Inches(0.35), f"{state['n']} / {TOTAL}", size=11, color=GREY, align=PP_ALIGN.RIGHT)
    return s


def bullets(slide, items, x=Inches(0.7), y=Inches(1.4), w=Inches(11.9), h=Inches(5.4), size=22, gap=10):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    first = True
    for it in items:
        level = 0
        if isinstance(it, tuple):
            level, it = it
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(gap)
        r = p.add_run()
        r.text = ("•  " if level == 0 else "–  ") + it
        r.font.size = Pt(size if level == 0 else size - 3)
        r.font.color.rgb = INK if level == 0 else GREY
        r.font.name = "Calibri"
        if level:
            p.level = 1
    return tb


def table(slide, rows, x, y, w, col_w, size=15, header=True, row_h=0.42):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), x, y, w, Inches(row_h * len(rows)))
    tbl = shape.table
    for i, cw in enumerate(col_w):
        tbl.columns[i].width = Inches(cw)
    for ri, row in enumerate(rows):
        tbl.rows[ri].height = Inches(row_h)
        for ci, val in enumerate(row):
            c = tbl.cell(ri, ci)
            c.text = ""
            c.margin_left = c.margin_right = Inches(0.08)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = c.text_frame.paragraphs[0]
            r = p.add_run()
            r.text = str(val)
            r.font.size = Pt(size)
            r.font.name = "Calibri"
            if header and ri == 0:
                c.fill.solid()
                c.fill.fore_color.rgb = TEAL
                r.font.bold = True
                r.font.color.rgb = WHITE
            else:
                c.fill.solid()
                c.fill.fore_color.rgb = LIGHT if ri % 2 else WHITE
                r.font.color.rgb = INK
    return tbl


def box(slide, x, y, w, h, text, fill=LIGHT, color=INK, size=15, bold=False):
    b = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    b.fill.solid()
    b.fill.fore_color.rgb = fill
    b.line.color.rgb = TEAL
    tf = b.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = "Calibri"
    return b


def arrow(slide, x1, y1, x2, y2):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, x1, y1, x2, y2)
    c.line.color.rgb = GREY
    c.line.width = Pt(2)
    ln = c.line._get_or_add_ln()
    from lxml import etree
    tail = etree.SubElement(ln, "{http://schemas.openxmlformats.org/drawingml/2006/main}tailEnd")
    tail.set("type", "triangle")


# 1. Tieu de
state["n"] += 1
s = prs.slides.add_slide(BLANK)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid()
bg.fill.fore_color.rgb = NAVY
bg.line.fill.background()
textbox(s, Inches(0.9), Inches(2.0), Inches(11.5), Inches(1.6), "Kiểm thử API Directus bằng Schema-Based API / Fuzz Testing", size=40, bold=True, color=WHITE)
textbox(s, Inches(0.9), Inches(3.8), Inches(11.5), Inches(0.9), "R06 Directus 12.5.0  ·  K05 Schemathesis 4.30.0  ·  Môn Kiểm thử phần mềm", size=24, color=RGBColor(0xCF, 0xE3, 0xEA))
textbox(s, Inches(0.9), Inches(5.0), Inches(11.5), Inches(0.9), "Nhóm 11  ·  Đinh Thị Mai Lành  ·  Trương Võ Trọng Nhân  ·  Phan Thị Bảo Trâm", size=20, color=WHITE)
textbox(s, Inches(0.9), Inches(6.4), Inches(11.5), Inches(0.5), "BẢN NHÁP: nhóm xem, chỉnh và phân người trình bày trước khi dùng", size=14, color=RGBColor(0xF2, 0xC9, 0x4C))

# 2. Pham vi
s = new_slide("Vì sao chọn và phạm vi kiểm thử", "A.2")
bullets(s, [
    "Directus tự sinh OpenAPI theo quyền của từng actor, nên Schemathesis dùng được ngay",
    "Phạm vi: REST API trong OpenAPI của 3 actor (Editor, Reader, Anonymous)",
    "Hai collection thử nghiệm: qa_categories, qa_articles",
    "Ngoài phạm vi: GraphQL, WebSocket, Flows, extensions, giao diện Studio",
    "Không phải 'toàn bộ Directus' và không phải coverage mã nguồn",
])

# 3. He thong va actor
s = new_slide("Hệ thống, actor và dữ liệu thử nghiệm", "A.3, A.4, E.1")
table(s, [
    ["Actor", "Quyền trong lab", "Operation trong OpenAPI"],
    ["Admin", "Chuẩn bị, seed, kiểm tra trạng thái (không fuzz)", "không tính"],
    ["Editor", "CRUD hai collection", "30"],
    ["Reader", "Đọc bài published; không đọc internal_notes", "22"],
    ["Anonymous", "Không truy cập hai collection", "10"],
], Inches(0.7), Inches(1.5), Inches(11.9), [2.3, 6.6, 3.0], size=18, row_h=0.55)
textbox(s, Inches(0.7), Inches(4.6), Inches(11.9), Inches(0.5), "Fixture r06-k05-v2: 3 category, 12 article (6 draft, 6 published)", size=20, color=INK)
textbox(s, Inches(0.7), Inches(5.3), Inches(11.9), Inches(0.9), "Mẫu số kiểm thử: 62 cặp (actor, operation) = 30 + 22 + 10, trên 30 operation khác nhau", size=22, bold=True, color=TEAL)

# 4. Kien truc
s = new_slide("Kiến trúc môi trường kiểm thử", "B.1")
y = Inches(2.3)
box(s, Inches(0.5), y, Inches(2.2), Inches(1.0), "run-lab.ps1\nlab.sh", size=16)
box(s, Inches(3.2), y, Inches(2.6), Inches(1.0), "lab-components.sh\nxuất OpenAPI theo actor", size=15)
box(s, Inches(6.3), y, Inches(2.6), Inches(1.0), "Runner\nSchemathesis 4.30.0", size=16, fill=RGBColor(0xDC, 0xEE, 0xF1))
box(s, Inches(9.4), y, Inches(1.8), Inches(1.0), "Directus\n12.5.0", size=16, fill=RGBColor(0xDC, 0xEE, 0xF1))
box(s, Inches(11.5), y, Inches(1.5), Inches(1.0), "PostgreSQL\n16", size=15)
for x1, x2 in ((2.7, 3.2), (5.8, 6.3), (8.9, 9.4), (11.2, 11.5)):
    arrow(s, Inches(x1), y + Inches(0.5), Inches(x2), y + Inches(0.5))
box(s, Inches(3.2), Inches(4.2), Inches(5.7), Inches(0.9), "Snapshot, kiểm tra tác dụng phụ, restore sau mỗi run", size=16, fill=RGBColor(0xFB, 0xF1, 0xD6))
box(s, Inches(6.3), Inches(5.5), Inches(2.6), Inches(0.8), "Report, NDJSON, coverage", size=15)
arrow(s, Inches(7.6), y + Inches(1.0), Inches(7.6), Inches(5.5))
textbox(s, Inches(0.5), Inches(1.35), Inches(12.3), Inches(0.7), "Docker Compose project r06-k05: Directus chỉ mở cổng 8055 trên loopback; PostgreSQL không mở cổng ra host", size=18, color=GREY)

# 5. Moi truong va pin
s = new_slide("Môi trường và cố định phiên bản", "C.1, C.3, H.1")
table(s, [
    ["Thành phần", "Phiên bản", "Digest (rút gọn)"],
    ["Directus", "12.5.0, commit 4f77933", "sha256:7de5d6898b95..."],
    ["PostgreSQL", "16-alpine", "sha256:721873c34ceb..."],
    ["Schemathesis", "4.30.0 (tracecov 0.25.2)", "sha256:bb9cecfc9ac4..."],
], Inches(0.7), Inches(1.5), Inches(11.9), [2.6, 4.6, 4.7], size=18, row_h=0.55)
bullets(s, ["Lệnh: doctor, up, seed, export-schema, test scenarios, test designed, test raw|guided",
            "Mật khẩu và license nằm trong config/lab.env (Git bỏ qua)"],
        y=Inches(4.1), size=20)

# 6. Ba luong nghiep vu
s = new_slide("Ba luồng nghiệp vụ chạy được (demo trực tiếp)", "C.4")
table(s, [
    ["Luồng", "Lệnh replay", "Nội dung"],
    ["CRUD Editor", "replay editor-crud", "Tạo, đọc, sửa, xóa; sau xóa không còn dữ liệu"],
    ["Truy vấn", "replay query-fixture", "Lọc 6 published, sort, hai trang, search Unicode"],
    ["Quyền Reader", "replay reader-visibility, reader-write", "internal_notes bị 403; PATCH bị 403, dữ liệu không đổi"],
], Inches(0.7), Inches(1.5), Inches(11.9), [2.4, 4.0, 5.5], size=17, row_h=0.7)
textbox(s, Inches(0.7), Inches(4.9), Inches(11.9), Inches(0.8), "Demo: .\\scripts\\run-lab.ps1 replay editor-crud", size=20, color=TEAL, bold=True)

# 7. K05
s = new_slide("Kỹ thuật K05: Schema-Based API / Fuzz", "D.1 đến D.3")
bullets(s, [
    "Đọc OpenAPI do Directus xuất, sinh request hợp lệ và không hợp lệ, kiểm phản hồi",
    "Bốn pha: examples, coverage, fuzzing, stateful",
    "Raw: schema gốc, ba pha  ·  Guided: thêm example và pha stateful",
    "Bảy check: 5xx, status, content type, response schema, unsupported method, negative và positive data",
    "Đính chính: --max-time làm fuzzing lặp đến hết giờ; không phải 'chưa hoàn tất'",
], size=21)

# 8. Du nghia la gi
s = new_slide("'Đủ' nghĩa là gì: mẫu số và sáu tiêu chí", "D.4, E.1")
table(s, [
    ["Mã", "Tiêu chí", "Kết quả"],
    ["C1", "62/62 cặp có request và phản hồi", "Đạt"],
    ["C2", "10 operation CRUD của Editor có 2xx", "Đạt (10/10)"],
    ["C3", "Cả 18 run kết thúc hoàn tất", "Đạt (18/18)"],
    ["C4", "Khôi phục dữ liệu sau mỗi run", "Đạt (18/18)"],
    ["C5", "Failure được gom nhóm, phân loại, có reproducer", "Đạt"],
    ["C6", "Coverage tracecov, kèm phần chưa tới", "Đạt (đo và báo cáo)"],
], Inches(0.7), Inches(1.4), Inches(11.9), [1.2, 7.7, 3.0], size=18, row_h=0.55)
textbox(s, Inches(0.7), Inches(5.5), Inches(11.9), Inches(0.9), "Không khẳng định: 'Directus 100%', 'không có lỗi', coverage mã nguồn", size=20, bold=True, color=RED)

# 9. 13 ca
s = new_slide("Bộ 13 ca nghiệp vụ: 12 PASS, 1 FAIL", "E.2, G.1")
bullets(s, [
    "S1–S6: CRUD, lọc, sắp xếp và phân trang, Reader không đọc draft, field kín, Reader ghi bị từ chối",
    "7 ca thiết kế: chuỗi CRUD category, anonymous bị cấm, score −1/0/5/6, hợp đồng POST",
    "Chạy lại 24/11/2026: S1–S6 6 passed; ca thiết kế 6 passed, 1 failed",
    "TC13 FAIL: schema khai báo data là mảng, POST một đối tượng trả đối tượng (nghiệp vụ đạt)",
    "Không sửa expected để ca đạt",
], size=21)

# 10. Tu dong hoa
s = new_slide("Tự động hóa và bảo vệ trạng thái", "F")
bullets(s, [
    "LAB_ACTOR=editor|reader|anonymous  LAB_CAMPAIGN_SCOPE=full  ./lab.sh test raw|guided",
    "Một seed: kiểm tra health, xuất schema, chạy Schemathesis, restore, kiểm tra tác dụng phụ",
    "Chụp 21 nhóm ngoài qa_* trước và sau; tự đặt lại tài khoản lab; dừng nếu có thay đổi lạ",
    "Run hoàn tất = kết thúc tự nhiên + có report + restore PASS + tác dụng phụ sạch",
    "Mã thoát của Schemathesis được giữ nguyên: failed nghĩa là tìm thấy lỗi",
], size=21)

# 11. Chien dich
s = new_slide("Chiến dịch 18 run và phủ 62 cặp", "G.3, G.4")
table(s, [
    ["Nhóm", "Operation", "Thời gian / seed", "Ca sinh ra"],
    ["Editor raw", "30", "26–27 giây", "114–117"],
    ["Reader raw", "22", "22–23 giây", "95–98"],
    ["Anonymous raw / guided", "10", "9 giây", "32–33"],
    ["Reader guided", "22", "221–778 giây", "1.056–3.722"],
    ["Editor guided", "30", "1.594–1.734 giây", "7.831–8.639"],
], Inches(0.7), Inches(1.4), Inches(11.9), [4.2, 2.0, 3.2, 2.5], size=17, row_h=0.5)
bullets(s, ["18/18 hoàn tất, restore PASS, tác dụng phụ sạch (khoảng 1,8 giờ)",
            "62/62 cặp có phản hồi: 34 có 2xx, 18 chỉ 401/403, 10 chỉ 4xx khác"],
        y=Inches(4.8), size=20)

# 12. Coverage
s = new_slide("Coverage theo schema: báo riêng từng chiều", "G.5")
table(s, [
    ["Actor / profile", "operations", "parameters", "keywords", "examples", "responses"],
    ["Editor raw", "100% (30/30)", "51,7%", "26,2%", "92,6%", "24,6%"],
    ["Editor guided", "100%", "68,6%", "48,4%", "90,7%", "24,6%"],
    ["Reader raw", "100% (22/22)", "51,4%", "26,6%", "93,7%", "23,8%"],
    ["Reader guided", "100%", "66,2%", "42,0%", "91,3%", "26,2%"],
    ["Anonymous", "100% (10/10)", "36,4%", "17,1%", "100%", "18,8%"],
], Inches(0.7), Inches(1.4), Inches(11.9), [2.8, 2.3, 1.7, 1.7, 1.7, 1.7], size=16, row_h=0.5)
bullets(s, ["Operations 100% chỉ nghĩa là mỗi operation đã nhận request",
            "Responses thấp vì Directus trả mã không có trong schema (204, 403, 400, 500)"],
        y=Inches(4.7), size=20)

# 13. Failure
s = new_slide("Failure và nguyên nhân gốc: ba con số khác nhau", "G.6")
table(s, [
    ["Đại lượng", "Giá trị"],
    ["Request (tương tác HTTP)", "31.147"],
    ["Lần check thất bại", "1.356"],
    ["Nhóm failure", "237"],
    ["Nguyên nhân gốc", "16: 10 sản phẩm, 5 schema, 1 chưa kết luận"],
], Inches(0.7), Inches(1.4), Inches(7.0), [3.6, 3.4], size=18, row_h=0.55)
bullets(s, ["9 lỗi sản phẩm: đầu vào sai gây HTTP 500 thay vì 4xx",
            "Giải thích 923/932 tương tác 5xx",
            "Phần lớn failure còn lại: schema OpenAPI lệch hành vi thực"],
        x=Inches(8.0), y=Inches(1.4), w=Inches(4.9), size=19)
textbox(s, Inches(0.7), Inches(4.6), Inches(11.9), Inches(0.9), "Số check thất bại không bằng số lỗi", size=24, bold=True, color=RED)

# 14. Mot loi minh hoa
s = new_slide("Một lỗi minh họa: aggregate sai cấu trúc trả HTTP 500", "G.7")
bullets(s, [
    "Request: GET /items/qa_articles?aggregate={\"foo\":1}  (Editor)",
    "Mong đợi: 400 INVALID_QUERY, như aggregate=[]",
    "Thực tế: 500; admin thấy 'fields is not iterable'",
    "Nguyên nhân: sanitizeAggregate chỉ xử lý chuỗi và mảng; giá trị khác lọt tới extractPathsFromQuery",
    "Đối chiếu mã tại commit đã ghim 4f77933 (sanitize-query.ts dòng 144–164)",
], size=21)

# 15. Gioi han
s = new_slide("Giới hạn và khả năng tái lập", "G.9, H")
bullets(s, [
    "Không phải coverage mã nguồn; không chứng minh Directus không có lỗi",
    "9 tương tác 5xx chưa tái hiện được",
    "Mới chạy trên một máy; chưa dựng lại trên máy thứ hai; chưa có CI",
    "Tái lập: pin digest và commit, seed cố định, restore sau mỗi run",
    "Số liệu lưu gọn trong docs/k05 (artifact thô không nằm trong Git)",
], size=21)

# 16. Dong gop
s = new_slide("Đóng góp và quy trình nhóm (dữ kiện từ Git/GitHub)", "docs/k05/wp9/dong-gop-tu-git.md")
table(s, [
    ["Thành viên", "Commit trên main", "PR", "Issue được giao"],
    ["Đinh Thị Mai Lành", "107", "3", "6"],
    ["Trương Võ Trọng Nhân", "55", "10", "5"],
    ["Phan Thị Bảo Trâm", "0", "0", "5"],
], Inches(0.7), Inches(1.4), Inches(11.9), [4.6, 2.8, 1.8, 2.7], size=19, row_h=0.6)
bullets(s, ["Số commit không phải thước đo đóng góp; nhiều việc không để lại commit",
            "Nhóm bổ sung bằng chứng đóng góp của Trâm và đánh giá chéo trước bảo vệ"],
        y=Inches(4.2), size=20)

OUT.parent.mkdir(parents=True, exist_ok=True)
assert state["n"] == TOTAL, state["n"]
prs.save(OUT)
print("da ghi", OUT, "-", state["n"], "slide")
