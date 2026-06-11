import streamlit as st
from fpdf import FPDF
import tempfile
import os
import random
import urllib.request
import fitz  # PyMuPDF
from PIL import Image

# ==========================================
# PART 1: Premium Setup & Visual Template
# ==========================================
def download_cute_fonts():
    fonts = {
        "ComicNeue-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/comicneue/ComicNeue-Regular.ttf",
        "ComicNeue-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/comicneue/ComicNeue-Bold.ttf"
    }
    for name, url in fonts.items():
        if not os.path.exists(name):
            try:
                urllib.request.urlretrieve(url, name)
            except Exception as e:
                pass

download_cute_fonts()

class PremiumWorksheetPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if os.path.exists("ComicNeue-Regular.ttf"):
            self.add_font("ComicNeue", style="", fname="ComicNeue-Regular.ttf")
        if os.path.exists("ComicNeue-Bold.ttf"):
            self.add_font("ComicNeue", style="B", fname="ComicNeue-Bold.ttf")

    def header(self):
        # กรอบนอกคู่ (Double Elegant Border)
        self.set_line_width(0.8)
        self.rect(10, 10, 190, 277)
        self.set_line_width(0.2)
        self.rect(11.5, 11.5, 187, 274)
        
        # ป้ายระบุระดับชั้น (Kindergarten Badge) - ทำให้งานดูมีแบรนด์และมืออาชีพ
        self.set_fill_color(240, 240, 240)
        self.rect(14, 14, 55, 8, style="F")
        self.set_font("ComicNeue", "B", 10)
        self.set_text_color(60, 60, 60)
        self.set_xy(14, 14)
        self.cell(55, 8, "  KINDERGARTEN MATH  ", align="C")
        
        # ช่องกรอกชื่อ วันที่ คะแนน ด้านบนขวา
        self.set_text_color(0, 0, 0)
        self.set_font("ComicNeue", "B", 11)
        self.set_xy(110, 14)
        self.cell(85, 8, "Name: _____________________", align="R")
        
        self.set_xy(14, 23)
        self.set_font("ComicNeue", "", 10)
        self.cell(50, 6, "Date: _______________", align="L")
        self.set_xy(140, 23)
        self.cell(55, 6, "Score: _________ / _________", align="R")
        
        # เส้นคั่นหัวกระดาษ
        self.set_line_width(0.4)
        self.line(14, 31, 196, 31)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("ComicNeue", "", 9)
        self.set_text_color(140, 140, 140)
        # ใส่สัญลักษณ์ลิขสิทธิ์ให้ดูเป็นงานสำหรับขาย Commercial
        self.cell(0, 10, "(c) Kindergarten Learning Press  |  All Rights Reserved.", align="C")
        self.set_text_color(0, 0, 0)

# ==========================================
# PART 2: Logic Engine (Data Formatting)
# ==========================================
def generate_questions_data(topic, num_q):
    questions = []
    used_keys = set()
    
    # บังคับเพิ่มจำนวนข้อให้เต็มหน้ากระดาษและสมดุลตามประเภท Grid
    # ถ้าเป็นแบบ 2 คอลัมน์ ควรใช้เลขคู่ เช่น 6 หรือ 8 ข้อเพื่อให้หน้ากระดาษแน่นสวย
    if any(k in topic for k in ["Missing", "True or False", "Which is More", "What Comes", "Name", "5s"]):
        if num_q % 2 != 0:
            num_q = min(num_q + 1, 8)

    for _ in range(num_q):
        q_data = {}
        for _ in range(50): # ป้องกันการสุ่มซ้ำจนลูปค้าง
            if topic == "1. Teen Numbers (11-20)":
                num = random.randint(11, 20)
                key = f"teen_{num}"
                q_data = {'num': num}
            
            elif topic == "2. What Comes Next?":
                start = random.randint(1, 16)
                key = f"next_{start}"
                q_data = {'start': start, 'seq': [start, start+1, start+2], 'ans': start+3}
                
            elif topic == "3. Order Numbers (Smallest to Largest)":
                nums = random.sample(range(1, 21), 4)
                key = f"order_{'_'.join(map(str, nums))}"
                q_data = {'nums': nums, 'sorted': sorted(nums)}
                
            elif topic == "4. Write Number's Name":
                num_words = {11:"eleven", 12:"twelve", 13:"thirteen", 14:"fourteen", 15:"fifteen", 
                             16:"sixteen", 17:"seventeen", 18:"eighteen", 19:"nineteen", 20:"twenty"}
                num = random.choice(list(num_words.keys()))
                key = f"name_{num}"
                q_data = {'num': num, 'word': num_words[num]}

            elif topic == "5. Missing Addends":
                ans = random.randint(4, 10) # เด็กอนุบาลบวกไม่เกิน 10 ตามหลักสูตรเป๊ะๆ
                a = random.randint(1, ans - 1)
                b = ans - a
                key = f"miss_{a}_{ans}"
                q_data = {'a': a, 'b': b, 'ans': ans}

            elif topic == "6. Picture Subtraction":
                a = random.randint(5, 10)
                b = random.randint(1, a - 1)
                key = f"sub_{a}_{b}"
                q_data = {'a': a, 'b': b, 'ans': a - b}

            elif topic == "7. Color by Answer":
                a = random.randint(1, 5)
                b = random.randint(1, 5)
                colors = {2:"RED", 3:"BLUE", 4:"GREEN", 5:"YELLOW", 6:"PINK", 7:"ORANGE", 8:"PURPLE", 9:"BROWN", 10:"GRAY"}
                ans = a + b
                key = f"cba_{a}_{b}"
                q_data = {'a': a, 'b': b, 'ans': ans, 'color': colors.get(ans, "RED")}

            elif topic == "8. How Many Sides?":
                shapes = [("Triangle", 3), ("Square", 4), ("Rectangle", 4), ("Pentagon", 5), ("Hexagon", 6)]
                shape, sides = random.choice(shapes)
                key = f"shape_{shape}_{random.randint(1,100)}"
                q_data = {'shape': shape, 'sides': sides}

            elif topic == "9. Tens and Ones":
                t = random.randint(1, 2) # อนุบาลเน้นไม่เกิน 20-30
                o = random.randint(1, 9)
                key = f"tens_{t}_{o}"
                q_data = {'tens': t, 'ones': o, 'total': (t*10)+o}

            elif topic == "10. True or False":
                a, b = random.randint(1, 5), random.randint(1, 5)
                is_true = random.choice([True, False])
                eq_ans = (a + b) if is_true else (a + b + random.choice([-1, 1]))
                if eq_ans < 0: eq_ans = a + b + 1
                key = f"tf_{a}_{b}_{eq_ans}"
                q_data = {'a': a, 'b': b, 'eq_ans': eq_ans, 'is_true': is_true}

            elif topic == "11. Which is More?":
                a, b = random.sample(range(1, 20), 2)
                key = f"more_{a}_{b}"
                q_data = {'a': a, 'b': b, 'more': max(a, b)}

            elif topic == "12. Count by 5's":
                multipliers = [5, 10, 15, 20, 25, 30, 35, 40, 45]
                start = random.choice(multipliers[:5])
                key = f"by5_{start}"
                q_data = {'start': start, 'seq': [start, start+5, start+10, start+15]}

            elif topic == "13. Roll It On":
                dice1 = random.randint(1, 6)
                dice2 = random.randint(1, 6)
                key = f"roll_{dice1}_{dice2}"
                q_data = {'d1': dice1, 'd2': dice2, 'ans': dice1+dice2}

            if key not in used_keys:
                used_keys.add(key)
                break
        questions.append(q_data)
    return questions

# ==========================================
# PART 3: Premium Grid Render Layout Engine
# ==========================================
def render_pdf_worksheet(topic, theme, questions_data, is_answer_key=False):
    pdf = PremiumWorksheetPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)
    
    # Title - หัวข้อหลักขนาดใหญ่สมดุลกลางหน้า
    pdf.set_font("ComicNeue", "B", 22)
    title_text = topic.split(". ")[1]
    if is_answer_key:
        pdf.set_text_color(220, 50, 50)
        title_text += " (ANSWER KEY)"
    pdf.set_y(36)
    pdf.cell(0, 12, title_text, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)

    # Directions - คำสั่งแยกตามพฤติกรรมการเรียนรู้ของเด็กอนุบาล 3 จากไฟล์ PDF
    pdf.set_font("ComicNeue", "B", 12)
    pdf.set_x(14)
    directions_map = {
        "1. Teen Numbers (11-20)": f"Directions: Count the cute {theme.lower()} items and write the correct teen number in the box.",
        "2. What Comes Next?": "Directions: Look at the number pattern. Write the missing number that comes next.",
        "3. Order Numbers (Smallest to Largest)": "Directions: Look at the group of numbers. Write them in order from smallest to largest.",
        "4. Write Number's Name": "Directions: Read the number block and write its matching word name on the line.",
        "5. Missing Addends": "Directions: Find the missing addend number to make the addition equation true.",
        "6. Picture Subtraction": f"Directions: Look at the {theme.lower()} pictures. Cross out the items to solve the subtraction question.",
        "7. Color by Answer": f"Directions: Solve the math facts. Use the code below to color the {theme.lower()} character space.",
        "8. How Many Sides?": "Directions: Identify the 2D shape. Count and write down how many sides it has.",
        "9. Tens and Ones": "Directions: Count the base-ten blocks (tens and ones), then write the total number.",
        "10. True or False": "Directions: Check the addition equation. Circle TRUE if it is correct, or FALSE if it is wrong.",
        "11. Which is More?": "Directions: Look at both numbers in the pair. Circle the number that is the largest.",
        "12. Count by 5's": "Directions: Skip count forward by 5s. Fill in the missing numbers in the blanks.",
        "13. Roll It On": "Directions: Read the dots on the dice, write the numbers, and count on to find the sum."
    }
    pdf.multi_cell(182, 6, directions_map.get(topic, "Directions: Solve the math problems on this worksheet carefully."))
    pdf.ln(4)

    # เช็คประเภทเพื่อกำหนดขนาดกรอบและระบบคอลัมน์ (2 Columns vs 1 Column)
    is_two_col = any(k in topic for k in ["Next", "Name", "Missing", "True", "More", "5's", "Roll"])
    col_w = 88 if is_two_col else 182
    box_h = 36 if is_two_col else 46
    
    # ปรับแต่งความสูงกล่องตามความจำเป็นของกราฟิกแต่ละหัวข้อ
    if "Order Numbers" in topic: box_h = 32
    if "Subtraction" in topic or "Color by" in topic or "Ones" in topic: box_h = 52

    num_q = len(questions_data)
    pdf.set_y(54) # จุดเริ่มพิกัดแนวตั้งแรกหลังคำสั่ง

    for i, q in enumerate(questions_data, start=1):
        if is_two_col:
            col_idx = (i - 1) % 2  # 0 = ซ้าย, 1 = ขวา
            x_start = 14 if col_idx == 0 else 108
            
            # ตรวจสอบการขึ้นหน้าใหม่สำหรับระบบ 2 คอลัมน์
            if col_idx == 0 and (pdf.get_y() + box_h > 265):
                pdf.add_page()
                pdf.set_y(42)
            y_start = pdf.get_y()
        else:
            x_start = 14
            if pdf.get_y() + box_h > 265:
                pdf.add_page()
                pdf.set_y(42)
            y_start = pdf.get_y()
        
        # วาดกรอบสี่เหลี่ยมพื้นหลังของข้อ (Main Card Border)
        pdf.set_draw_color(180, 180, 180)
        pdf.set_line_width(0.4)
        pdf.rect(x_start, y_start, col_w, box_h, style="D")
        
        # ป้ายเลขข้อดีไซน์โมเดิร์น (Question Number Tag)
        pdf.set_font("ComicNeue", "B", 11)
        pdf.set_text_color(110, 110, 110)
        pdf.set_xy(x_start + 3, y_start + 3)
        pdf.cell(10, 5, f"Q{i}", align="L")
        pdf.set_text_color(0, 0, 0)
        
        ans_color = (220, 50, 50) if is_answer_key else (0, 0, 0)
        
        # --- เริ่มเรนเดอร์ดีไซน์ตามเงื่อนไขรายหัวข้อ (ระดับพรีเมียมตัวเลขใหญ่พิเศษ) ---
        
        # 1. Teen Numbers (1 คอลัมน์ - จัดวางสมดุลซ้ายกราฟิก ขวาคำตอบ)
        if "Teen Numbers" in topic:
            # วาดกรอบเส้นประสำหรับพื้นที่วาง Clipart ของผู้ใช้งานใน Canva
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.2)
            pdf.set_dash_pattern(dash=1.5, gap=1.5)
            pdf.rect(x_start + 15, y_start + 6, 75, box_h - 12, style="D")
            pdf.set_dash_pattern() # เคลียร์เส้นประ
            
            pdf.set_font("ComicNeue", "", 9)
            pdf.set_text_color(150, 150, 150)
            pdf.set_xy(x_start + 15, y_start + (box_h / 2) - 3)
            pdf.cell(75, 6, f"[ Place {theme} Clipart x{q['num']} Here ]", align="C")
            
            # คำตอบขนาดใหญ่ 26pt ด้านขวา
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("ComicNeue", "B", 26)
            pdf.set_xy(x_start + 95, y_start + (box_h / 2) - 8)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(75, 14, f"Count = {q['num']}", align="C")
            else:
                pdf.cell(75, 14, "Count = [      ]", align="C")

        # 2. What Comes Next? (2 คอลัมน์ - เรียงตัวเลขแพทเทิร์นใหญ่สะใจ)
        elif "What Comes Next" in topic:
            pdf.set_font("ComicNeue", "B", 24)
            pdf.set_xy(x_start + 5, y_start + 12)
            seq_text = f"{q['seq'][0]},  {q['seq'][1]},  {q['seq'][2]},  "
            pdf.cell(58, 12, seq_text, align="R")
            
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(20, 12, str(q['ans']), align="L")
            else:
                pdf.set_draw_color(0, 0, 0)
                pdf.set_line_width(0.6)
                pdf.line(pdf.get_x() + 1, y_start + 22, pdf.get_x() + 14, y_start + 22)

        # 3. Order Numbers (1 คอลัมน์ - มีการกระจายกลุ่มตัวเลขให้เลือกจัดระเบียบ)
        elif "Order Numbers" in topic:
            pdf.set_font("ComicNeue", "B", 24)
            pdf.set_xy(x_start + 15, y_start + 10)
            num_str = "   .   ".join(map(str, q['nums']))
            pdf.cell(70, 12, f"Mix:  {num_str}", align="L")
            
            pdf.set_xy(x_start + 95, y_start + 11)
            if is_answer_key:
                pdf.set_font("ComicNeue", "B", 20)
                pdf.set_text_color(*ans_color)
                ans_str = "  <  ".join(map(str, q['sorted']))
                pdf.cell(75, 10, f"Ans: {ans_str}", align="C")
            else:
                pdf.set_font("ComicNeue", "B", 22)
                pdf.cell(75, 10, "[    ] < [    ] < [    ] < [    ]", align="C")

        # 4. Write Number's Name (2 คอลัมน์ - ฟอนต์ใหญ่บรรทัดเขียนชื่อชัดเจน)
        elif "Write Number's Name" in topic:
            pdf.set_font("ComicNeue", "B", 24)
            pdf.set_xy(x_start + 5, y_start + 11)
            pdf.cell(28, 12, f"{q['num']}  = ", align="R")
            
            if is_answer_key:
                pdf.set_font("ComicNeue", "B", 18)
                pdf.set_text_color(*ans_color)
                pdf.cell(50, 12, q['word'].upper(), align="L")
            else:
                pdf.set_font("ComicNeue", "", 15)
                pdf.cell(50, 12, "__________________", align="L")

        # 5. Missing Addends (2 คอลัมน์ - มีบล็อกสี่เหลี่ยมเว้นช่องให้เติมตัวเลขบวก)
        elif "Missing Addends" in topic:
            pdf.set_font("ComicNeue", "B", 24)
            pdf.set_xy(x_start + 5, y_start + 11)
            pdf.cell(22, 12, f"{q['a']}  +", align="R")
            
            # บล็อกสี่เหลี่ยมสำหรับเติมตัวเลขแบบมืออาชีพ
            box_x = pdf.get_x() + 2
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(0.5)
            pdf.rect(box_x, y_start + 11, 13, 13)
            
            if is_answer_key:
                pdf.set_xy(box_x, y_start + 11)
                pdf.set_text_color(*ans_color)
                pdf.cell(13, 13, str(q['b']), align="C")
                pdf.set_text_color(0, 0, 0)
            
            pdf.set_xy(box_x + 16, y_start + 11)
            pdf.cell(30, 12, f"=  {q['ans']}", align="L")

        # 6. Picture Subtraction (1 คอลัมน์ - แบ่งครึ่งพื้นที่วาดรูปด้านบน สมการด้านล่าง)
        elif "Picture Subtraction" in topic:
            # พื้นที่สำหรับให้ผู้ใช้ไปวางรูปภาพของตัวเองใน Canva เพื่อให้นักเรียนขีดฆ่า
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.2)
            pdf.set_dash_pattern(dash=1.5, gap=1.5)
            pdf.rect(x_start + 15, y_start + 5, 152, 24, style="D")
            pdf.set_dash_pattern()
            
            pdf.set_font("ComicNeue", "", 9)
            pdf.set_text_color(150, 150, 150)
            pdf.set_xy(x_start + 15, y_start + 14)
            pdf.cell(152, 6, f"[ Drop {q['a']} copies of {theme} clipart here. Students will cross out {q['b']} of them ]", align="C")
            
            # สมการขนาดใหญ่พิเศษด้านล่างกรอบ
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("ComicNeue", "B", 26)
            pdf.set_xy(x_start + 15, y_start + 34)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(152, 14, f"{q['a']}   -   {q['b']}   =   {q['ans']}", align="C")
            else:
                pdf.cell(152, 14, f"{q['a']}   -   {q['b']}   =   ______", align="C")

        # 7. Color by Answer (1 คอลัมน์ - กล่องโจทย์ฝั่งซ้าย บล็อกระบายสีฝั่งขวาชัดเจน)
        elif "Color by Answer" in topic:
            pdf.set_font("ComicNeue", "B", 26)
            pdf.set_xy(x_start + 15, y_start + 14)
            pdf.cell(65, 14, f"{q['a']}  +  {q['b']}  =  ?", align="L")
            
            # กรอบขวาสำหรับระบายสีตัวการ์ตูน
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.2)
            pdf.set_dash_pattern(dash=1.5, gap=1.5)
            pdf.rect(x_start + 90, y_start + 6, 80, box_h - 12, style="D")
            pdf.set_dash_pattern()
            
            pdf.set_font("ComicNeue", "", 9)
            pdf.set_text_color(150, 150, 150)
            pdf.set_xy(x_start + 90, y_start + (box_h / 2) - 3)
            pdf.cell(80, 6, f"[ Place {theme} Clipart with Text Code '{q['ans']}' Inside ]", align="C")
            
            # แถบคำใบ้สีด้านล่างโจทย์ซ้าย
            pdf.set_xy(x_start + 15, y_start + 35)
            pdf.set_font("ComicNeue", "B", 12)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(65, 6, f"CODE {q['ans']}  ->  {q['color']}", align="L")
            else:
                pdf.set_text_color(90, 90, 90)
                pdf.cell(65, 6, f"If Answer is {q['ans']}  ->  Color it {q['color']}", align="L")

        # 8. How Many Sides? (1 คอลัมน์ - จัดข้อความชื่อรูปทรงและช่องกรอกสมดุล)
        elif "How Many Sides" in topic:
            pdf.set_font("ComicNeue", "B", 24)
            pdf.set_xy(x_start + 15, y_start + 16)
            pdf.cell(85, 12, f"Shape:  {q['shape']}", align="L")
            
            pdf.set_xy(x_start + 110, y_start + 16)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(55, 12, f"Sides = {q['sides']}", align="R")
            else:
                pdf.cell(55, 12, "Sides = [      ]", align="R")

        # 9. Tens and Ones (1 คอลัมน์ - ซ้ายเป็นช่องสำหรับบล็อกสิบนับหน่วย ขวาบันทึกค่า)
        elif "Tens and Ones" in topic:
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.2)
            pdf.set_dash_pattern(dash=1.5, gap=1.5)
            pdf.rect(x_start + 15, y_start + 6, 75, box_h - 12, style="D")
            pdf.set_dash_pattern()
            
            pdf.set_font("ComicNeue", "", 9)
            pdf.set_text_color(150, 150, 150)
            pdf.set_xy(x_start + 15, y_start + (box_h / 2) - 3)
            pdf.cell(75, 6, f"[ Drop {q['tens']} Tens & {q['ones']} Ones Blocks Here ]", align="C")
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("ComicNeue", "B", 16)
            pdf.set_xy(x_start + 95, y_start + 12)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(75, 8, f"{q['tens']} Tens and {q['ones']} Ones", align="C")
                pdf.set_xy(x_start + 95, y_start + 26)
                pdf.set_font("ComicNeue", "B", 26)
                pdf.cell(75, 12, f"=   {q['total']}", align="C")
            else:
                pdf.cell(75, 8, "____ Tens and ____ Ones", align="C")
                pdf.set_xy(x_start + 95, y_start + 26)
                pdf.set_font("ComicNeue", "B", 26)
                pdf.cell(75, 12, "=   [      ]", align="C")

        # 10. True or False (2 คอลัมน์ - กล่องสมการด้านบน ตัวเลือกวงกลมด้านล่าง)
        elif "True or False" in topic:
            pdf.set_font("ComicNeue", "B", 24)
            pdf.set_xy(x_start + 4, y_start + 8)
            pdf.cell(80, 12, f"{q['a']}  +  {q['b']}  =  {q['eq_ans']}", align="C")
            
            pdf.set_font("ComicNeue", "B", 14)
            pdf.set_xy(x_start + 4, y_start + 23)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                choice_text = "[ TRUE ]      FALSE" if q['is_true'] else "TRUE      [ FALSE ]"
                pdf.cell(80, 8, choice_text, align="C")
            else:
                pdf.set_text_color(110, 110, 110)
                pdf.cell(80, 8, "TRUE   /   FALSE", align="C")

        # 11. Which is More? (2 คอลัมน์ - เปรียบเทียบตัวเลขขนาดใหญ่ ซ้าย-ขวา ชัดเจน)
        elif "Which is More" in topic:
            pdf.set_font("ComicNeue", "B", 26)
            pdf.set_xy(x_start + 5, y_start + 12)
            
            if is_answer_key:
                if q['a'] == q['more']:
                    pdf.set_text_color(*ans_color)
                    pdf.cell(39, 12, f"({q['a']})", align="C")
                    pdf.set_text_color(0, 0, 0)
                    pdf.cell(39, 12, str(q['b']), align="C")
                else:
                    pdf.cell(39, 12, str(q['a']), align="C")
                    pdf.set_text_color(*ans_color)
                    pdf.cell(39, 12, f"({q['b']})", align="C")
            else:
                pdf.cell(39, 12, str(q['a']), align="C")
                pdf.cell(39, 12, str(q['b']), align="C")

        # 12. Count by 5's (2 คอลัมน์ - แพทเทิร์นนับข้ามทีละ 5 ขนาดใหญ่และอ่านง่าย)
        elif "Count by 5's" in topic:
            pdf.set_font("ComicNeue", "B", 20)
            pdf.set_xy(x_start + 4, y_start + 12)
            seq = q['seq']
            pdf.cell(24, 12, f"{seq[0]},  ", align="R")
            
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(56, 12, f"{seq[1]},   {seq[2]},   {seq[3]}", align="L")
            else:
                pdf.set_font("ComicNeue", "", 18)
                pdf.cell(56, 12, "__ ,   __ ,   __", align="L")

        # 13. Roll It On (2 คอลัมน์ - สรุปยอดคะแนนจากการทอยลูกเต๋า)
        elif "Roll It On" in topic:
            pdf.set_font("ComicNeue", "B", 16)
            pdf.set_xy(x_start + 4, y_start + 8)
            pdf.cell(80, 8, f"Dice:  [{q['d1']}]  +  [{q['d2']}]", align="C")
            
            pdf.set_font("ComicNeue", "B", 22)
            pdf.set_xy(x_start + 4, y_start + 20)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(80, 10, f"Total  =  {q['ans']}", align="C")
            else:
                pdf.cell(80, 10, "Total  =  [      ]", align="C")

        pdf.set_text_color(0, 0, 0) # รีเซ็ตสีกลับเป็นปกติ
        
        # จัดพิกัดบรรทัดถัดไปตามการบล็อกของดีไซน์ระบบคอลัมน์
        if is_two_col:
            if col_idx == 1:
                pdf.set_y(y_start + box_h + 5)
        else:
            pdf.set_y(y_start + box_h + 5)
            
    if is_two_col and (num_q % 2 != 0):
        pdf.set_y(pdf.get_y() + box_h + 5)

    # ส่งออกไฟล์ PDF ไปยังไดเรกทอรีชั่วคราว
    temp_dir = tempfile.gettempdir()
    file_prefix = "Answer_Key_" if is_answer_key else "Worksheet_"
    safe_topic = topic.split(". ")[1].replace(" ", "_").replace("'", "").replace("?", "")
    file_path = os.path.join(temp_dir, f"{file_prefix}{safe_topic}.pdf")
    pdf.output(file_path)
    return file_path

# ==========================================
# PART 4: Premium Streamlit UI & Execution
# ==========================================
def display_pdf_preview(file_path):
    """ฟังก์ชันแปลงหน้าแรกของ PDF เป็นรูปภาพเพื่อแสดงผลพรีวิวแบบสมจริง พร้อมเอฟเฟกต์เงากระดาษ"""
    try:
        doc = fitz.open(file_path)
        page = doc.load_page(0)  # โหลดหน้าแรกมาพรีวิว
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # เพิ่มมิติด้วย CSS Box Shadow ให้ดูเหมือนแผ่นกระดาษใบงานวางอยู่จริง
        st.markdown(
            """
            <style>
            .premium-paper {
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                border-radius: 8px;
                background: white;
                padding: 4px;
                border: 1px solid #e0e0e0;
                display: inline-block;
            }
            </style>
            """, unsafe_allow_html=True
        )
        st.image(img, use_container_width=True)
        doc.close()
    except Exception as e:
        st.error(f"⚠️ ไม่สามารถแสดงพรีวิวได้ชั่วคราว แต่ไฟล์ PDF ถูกสร้างสมบูรณ์แล้ว: {e}")

# ตั้งค่าหน้าเว็บสไตล์ Premium Web App
st.set_page_config(
    page_title="Premium Kindergarten Math Worksheet Generator (TpT-Grade)", 
    page_icon="✏️", 
    layout="wide"
)

# หัวข้อหลักและคำแนะนำการใช้งานเชิงพาณิชย์
st.title("✏️ Premium Kindergarten Math Worksheet Generator")
st.markdown(
    """
    <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #4a90e2; margin-bottom: 20px;'>
        <strong>👑 เวอร์ชันอัปเกรดระดับมืออาชีพ (TpT Commercial Grade)</strong><br>
        ระบบได้ทำการคำนวณและปรับสัดส่วนหน้ากระดาษแบบสมดุลอัตโนมัติ: ปรับปรุงฟอนต์ขนาดใหญ่พิเศษ (22pt-28pt), 
        เพิ่มป้ายระดับชั้น <strong>KINDERGARTEN</strong>, ลิขสิทธิ์ท้ายหน้า และใช้ระบบจัดเรียง <strong>Symmetry Grid (2 คอลัมน์)</strong> 
        สำหรับข้อสั้น เพื่อไม่ให้หน้ากระดาษโล่งเกินไป พร้อมตีเส้นประระบุพื้นที่สำหรับลากรูปภาพการ์ตูนมาวางทับใน Canva ได้อย่างแม่นยำ
    </div>
    """, unsafe_allow_html=True
)

# แถบควบคุมด้านข้าง (Sidebar Settings)
st.sidebar.header("⚙️ ใบงานสไตล์เลเอาต์พรีเมียม")

all_topics = [
    "1. Teen Numbers (11-20)",
    "2. What Comes Next?",
    "3. Order Numbers (Smallest to Largest)",
    "4. Write Number's Name",
    "5. Missing Addends",
    "6. Picture Subtraction",
    "7. Color by Answer",
    "8. How Many Sides?",
    "9. Tens and Ones",
    "10. True or False",
    "11. Which is More?",
    "12. Count by 5's",
    "13. Roll It On"
]

# เมนูเลือกหัวข้อกิจกรรมและธีม
topic = st.sidebar.selectbox("🎯 เลือกหัวข้อกิจกรรม (13 รูปแบบหลัก):", all_topics)
theme = st.sidebar.selectbox("🎨 เลือกธีมตัวละคร Clipart ที่จะระบุในคำสั่ง:", ["Space", "Ocean", "Animals", "Monsters", "School", "Food", "Dinosaurs"])
num_q = st.sidebar.slider("📌 จำนวนโจทย์ต่อหน้า (หากเป็นข้อสั้นระบบจะปัดเป็นเลขคู่เพื่อความสมดุล):", min_value=2, max_value=8, value=4, step=2)
include_ans = st.sidebar.checkbox("✅ สร้างใบงานคู่ขนานพร้อมแผ่นเฉลย (Answer Key)", value=True)

st.sidebar.markdown("---")

# ปุ่มสุ่มโจทย์ใหม่โดยใช้ตัวเลขเดิมตามการตั้งค่า
if st.sidebar.button("🎲 สุ่มตัวเลขโจทย์ใหม่ (Shuffle Numbers)", use_container_width=True):
    st.session_state.force_reroll = True

# ตรวจสอบความเปลี่ยนแปลงของค่าเงื่อนไข เพื่อเรนเดอร์ PDF ใหม่แบบ Real-time
current_settings = f"{topic}_{theme}_{num_q}_{include_ans}"
if 'last_settings' not in st.session_state or st.session_state.last_settings != current_settings or st.session_state.get('force_reroll', False):
    with st.spinner("กำลังเรนเดอร์โครงสร้างกระดาษความละเอียดสูง..."):
        # 1. คำนวณค่าและสร้างชุดข้อมูลโจทย์
        st.session_state.q_data = generate_questions_data(topic, num_q)
        # 2. เรนเดอร์ไฟล์ PDF จริงลงหน่วยความจำชั่วคราว
        st.session_state.ws_path = render_pdf_worksheet(topic, theme, st.session_state.q_data, is_answer_key=False)
        if include_ans:
            st.session_state.ans_path = render_pdf_worksheet(topic, theme, st.session_state.q_data, is_answer_key=True)
        
        st.session_state.last_settings = current_settings
        st.session_state.force_reroll = False

# ส่วนแสดงผลหลัก (Main Dashboard Layout)
st.subheader("🔍 พรีวิวหน้ากระดาษจริง (Live WYSIWYG Preview)")

# ระบบแท็บสลับดู ใบงานหลัก กับ แผ่นเฉลย
tabs = st.tabs(["📄 Premium Worksheet", "🔑 Answer Key (แผ่นเฉลย)"]) if include_ans else st.tabs(["📄 Premium Worksheet"])

# --- แท็บที่ 1: ใบงานหลักสำหรับเด็กนักเรียน ---
with tabs[0]:
    with open(st.session_state.ws_path, "rb") as f: 
        ws_bytes = f.read()
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📥 ดาวน์โหลดไฟล์ไปใช้งาน")
        st.download_button(
            label="🚀 Download Premium Worksheet (PDF)", 
            data=ws_bytes, 
            file_name=f"Premium_Worksheet_{topic.split('.')[1].strip().replace(' ', '_')}.pdf", 
            mime="application/pdf", 
            use_container_width=True,
            type="primary"
        )
        
        # กล่องแนะนำขั้นตอนการต่อยอดเพื่อสร้างมูลค่าใน Canva
        st.markdown(
            f"""
            <div style='background-color: #e3f2fd; padding: 15px; border-radius: 6px; margin-top: 15px; color: #0d47a1;'>
                <strong>💡 คำแนะนำสไตล์ครูนักขาย TpT:</strong><br>
                1. กดดาวน์โหลดไฟล์ PDF ด้านบนนี้<br>
                2. นำไปอัปโหลดเข้าสู่หน้าออกแบบของ <strong>Canva</strong><br>
                3. ค้นหาองค์ประกอบกราฟิกธีม <strong>"{theme}"</strong> ที่สวยงาม น่ารัก<br>
                4. นำรูปภาพการ์ตูนเหล่านั้นไปลากวางซ้อนบนกล่องเส้นประ <code>[ Place {theme} Clipart ]</code> ที่ระบบตีเส้นจัดสัดส่วนไว้ให้<br>
                5. กดเซฟเป็นไฟล์รูปภาพหรือ PDF คุณภาพสูงเพื่อนำไปลิสต์ขายหรือแจกจ่ายได้ทันที!
            </div>
            """, unsafe_allow_html=True
        )
        
        # แสดงรายการโจทย์ที่ถูกสุ่มขึ้นมาแบบโปร่งใส
        st.markdown("#### 📑 ข้อมูลตัวเลขโจทย์ในหน้ากระดาษนี้:")
        st.json(st.session_state.q_data)
        
    with col2: 
        st.markdown("<div class='premium-paper'>", unsafe_allow_html=True)
        display_pdf_preview(st.session_state.ws_path)
        st.markdown("</div>", unsafe_allow_html=True)

# --- แท็บที่ 2: แผ่นเฉลย (หากเลือกเปิดไว้) ---
if include_ans:
    with tabs[1]:
        with open(st.session_state.ans_path, "rb") as f: 
            ans_bytes = f.read()
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### 📥 ดาวน์โหลดแผ่นเฉลย")
            st.download_button(
                label="📥 Download Answer Key (PDF)", 
                data=ans_bytes, 
                file_name=f"AnswerKey_{topic.split('.')[1].strip().replace(' ', '_')}.pdf", 
                mime="application/pdf", 
                use_container_width=True
            )
            st.info("🎯 แผ่นเฉลยจะใช้ตัวเลขชุดเดียวกับใบงานหลัก แต่ทำการพิมพ์คำตอบและแสดงเครื่องหมายวงเล็บ/คำตอบขนาดใหญ่ด้วยสีแดง (RGB: 220, 50, 50) อย่างแม่นยำ เพื่อให้ครูและผู้ปกครองตรวจทานได้ง่ายขึ้น")
            
        with col2: 
            st.markdown("<div class='premium-paper'>", unsafe_allow_html=True)
            display_pdf_preview(st.session_state.ans_path)
            st.markdown("</div>", unsafe_allow_html=True)
