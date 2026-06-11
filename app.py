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
    def __init__(self, store_name="Your TpT Store", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.store_name = store_name  # รับค่าชื่อร้านค้าเพื่อไปแสดงผลที่ Footer
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
        
        # ป้ายระบุระดับชั้น (Kindergarten Badge)
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
        # ✨ แก้ไขพิกัด: ขยับขึ้นมาที่ -18 มม. และปรับลดความสูงเซลล์เหลือ 4 มม. เพื่อให้อยู่ในกรอบอย่างปลอดภัย ไม่ทับเส้น
        self.set_y(-18)
        self.set_x(14)
        self.set_font("ComicNeue", "", 9)
        self.set_text_color(140, 140, 140)
        
        copyright_text = f"(c) {self.store_name}  |  All Rights Reserved."
        self.cell(182, 4, copyright_text, align="R")
        self.set_text_color(0, 0, 0)
        
# ==========================================
# PART 2: Math Question Generation Engine (Anti-Duplicate)
# ==========================================
def generate_questions_data(topic, num_questions):
    # ตรวจสอบระบบเลเอาต์: หากเป็นแบบ 2 คอลัมน์ จะปรับจำนวนโจทย์ให้เป็นเลขคู่เสมอเพื่อความสมดุล
    is_two_col = any(k in topic for k in ["Next", "Name", "Missing", "True", "More", "5's", "Roll"])
    if is_two_col and num_questions % 2 != 0:
        num_questions += 1

    questions = []
    used_keys = set()  # ตัวแปรสำหรับเช็คความซ้ำซ้อนของโจทย์
    
    # 💎 จัดเตรียมสระสุ่มแบบไม่ใส่คืน (Unique Pool) ล่วงหน้าสำหรับหัวข้อที่ตัวเลขจำกัด
    if "Teen Numbers" in topic or "Write Number's Name" in topic:
        chosen_nums = random.sample(range(11, 21), min(num_questions, 10))
    elif "What Comes Next" in topic:
        chosen_starts = random.sample(range(1, 17), min(num_questions, 16))
    elif "Count by 5's" in topic:
        # แก้ปัญหารูปแบบดั้งเดิม โดยการสุ่มสุ่มตัวเริ่มแบบไม่ซ้ำจาก Pool ทั้งหมดที่มี
        pool_5s = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
        chosen_starts = random.sample(pool_5s, min(num_questions, len(pool_5s)))
    elif "How Many Sides" in topic:
        shapes_pool = [
            {"shape": "Triangle", "sides": 3}, {"shape": "Square", "sides": 4},
            {"shape": "Rectangle", "sides": 4}, {"shape": "Pentagon", "sides": 5},
            {"shape": "Hexagon", "sides": 6}, {"shape": "Circle", "sides": 0}
        ]
        extended_pool = shapes_pool.copy()
        random.shuffle(extended_pool)
        while len(extended_pool) < num_questions:
            extra = shapes_pool.copy()
            random.shuffle(extra)
            extended_pool.extend(extra)

    # วงลูปสร้างโจทย์และตรวจสอบความซ้ำซ้อนระดับสมบูรณ์
    for i in range(num_questions):
        attempts = 0
        while attempts < 100:  # จำกัดจำนวนรอบเพื่อป้องกัน infinite loop
            attempts += 1
            q_item = None
            key = None  # ใช้คีย์นี้ระบุเอกลักษณ์ของโจทย์แต่ละข้อ
            
            if "Teen Numbers" in topic:
                num = chosen_nums[i % len(chosen_nums)]
                q_item = {"num": num}
                key = num
                
            elif "What Comes Next" in topic:
                start = chosen_starts[i % len(chosen_starts)]
                seq = [start, start + 1, start + 2]
                ans = start + 3
                q_item = {"seq": seq, "ans": ans}
                key = start
                
            elif "Order Numbers" in topic:
                nums = random.sample(range(1, 21), 4)
                sorted_nums = sorted(nums)
                q_item = {"nums": nums, "sorted": sorted_nums}
                key = tuple(sorted_nums)
                
            elif "Write Number's Name" in topic:
                num = chosen_nums[i % len(chosen_nums)]
                words_map = {
                    11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
                    16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen", 20: "twenty"
                }
                q_item = {"num": num, "word": words_map[num]}
                key = num
                
            elif "Missing Addends" in topic:
                ans = random.randint(5, 20)
                a = random.randint(1, ans - 1)
                b = ans - a
                q_item = {"a": a, "b": b, "ans": ans}
                key = (a, b, ans)
                
            elif "Picture Subtraction" in topic:
                a = random.randint(5, 10)
                b = random.randint(1, a)
                ans = a - b
                q_item = {"a": a, "b": b, "ans": ans}
                key = (a, b)
                
            elif "Color by Answer" in topic:
                a = random.randint(1, 5)
                b = random.randint(1, 5)
                ans = a + b
                colors = ["Red", "Blue", "Green", "Yellow", "Pink", "Purple", "Orange"]
                chosen_color = colors[i % len(colors)]  # เกลี่ยสีให้ไม่ซ้ำซ้อนกันในหน้าเดียว
                q_item = {"a": a, "b": b, "ans": ans, "color": chosen_color}
                key = (a, b)
                
            elif "How Many Sides" in topic:
                q_item = extended_pool[i]
                key = i  # ผ่านการจัดระเบียบในขั้นกระจายพูลแล้ว
                
            elif "Tens and Ones" in topic:
                tens = random.randint(1, 2)
                ones = random.randint(0, 9)
                total = (tens * 10) + ones
                q_item = {"tens": tens, "ones": ones, "total": total}
                key = total
                
            elif "True or False" in topic:
                a = random.randint(1, 10)
                b = random.randint(1, 10)
                is_true = random.choice([True, False])
                if is_true:
                    eq_ans = a + b
                else:
                    eq_ans = a + b + random.choice([-2, -1, 1, 2])
                    if eq_ans < 0: eq_ans = a + b + 1
                    if eq_ans == a + b: eq_ans += 1
                q_item = {"a": a, "b": b, "eq_ans": eq_ans, "is_true": (a + b == eq_ans)}
                key = (a, b, eq_ans)
                
            elif "Which is More" in topic:
                a, b = random.sample(range(1, 21), 2)
                q_item = {"a": a, "b": b, "more": max(a, b)}
                key = tuple(sorted([a, b]))
                
            elif "Count by 5's" in topic:
                start = chosen_starts[i % len(chosen_starts)]
                seq = [start, start + 5, start + 10, start + 15]
                q_item = {"seq": seq}
                key = start
                
            elif "Roll It On" in topic:
                d1 = random.randint(1, 6)
                d2 = random.randint(1, 6)
                q_item = {"d1": d1, "d2": d2, "ans": d1 + d2}
                key = (d1, d2)

            # ตรวจสอบว่าชุดตัวเลข/คำถามนี้ เคยใช้หรือยัง ถ้ายังไม่เคย ให้บันทึกและผ่านข้อนี้ไปได้
            if key not in used_keys:
                used_keys.add(key)
                questions.append(q_item)
                break
        else:
            # กรณีหลุดการสุ่มมาได้ (Fallback)
            questions.append(q_item)
            
    return questions

# ==========================================
# PART 3: Premium Grid Render Layout Engine
# ==========================================
def render_pdf_worksheet_updated(topic, theme, questions_data, store_name, is_answer_key=False):
    # ส่งตัวแปร store_name เข้าไปในคลาสเพื่อแสดงที่ Footer มุมขวาล่าง
    pdf = PremiumWorksheetPDF(store_name=store_name, orientation="P", unit="mm", format="A4")
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

    # Directions - คำสั่งแยกตามพฤติกรรมการเรียนรู้ของเด็กอนุบาล
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
    
    # ปรับแต่งความสูงกล่องตามความจำเป็นของกราฟิก
    if "Order Numbers" in topic: box_h = 32
    if "Subtraction" in topic or "Color by" in topic or "Ones" in topic: box_h = 52

    num_q = len(questions_data)
    pdf.set_y(54) 

    for i, q in enumerate(questions_data, start=1):
        if is_two_col:
            col_idx = (i - 1) % 2  # 0 = ซ้าย, 1 = ขวา
            x_start = 14 if col_idx == 0 else 108
            
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
        
        # วาดกรอบสี่เหลี่ยมพื้นหลัง
        pdf.set_draw_color(180, 180, 180)
        pdf.set_line_width(0.4)
        pdf.rect(x_start, y_start, col_w, box_h, style="D")
        
        # ป้ายเลขข้อดีไซน์โมเดิร์น
        pdf.set_font("ComicNeue", "B", 11)
        pdf.set_text_color(110, 110, 110)
        pdf.set_xy(x_start + 3, y_start + 3)
        pdf.cell(10, 5, f"Q{i}", align="L")
        pdf.set_text_color(0, 0, 0)
        
        ans_color = (220, 50, 50) if is_answer_key else (0, 0, 0)
        
        # --- เริ่มเรนเดอร์ดีไซน์ตามเงื่อนไขรายหัวข้อ ---
        if "Teen Numbers" in topic:
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.2)
            pdf.set_dash_pattern(dash=1.5, gap=1.5)
            pdf.rect(x_start + 15, y_start + 6, 75, box_h - 12, style="D")
            pdf.set_dash_pattern()
            
            pdf.set_font("ComicNeue", "", 9)
            pdf.set_text_color(150, 150, 150)
            pdf.set_xy(x_start + 15, y_start + (box_h / 2) - 3)
            pdf.cell(75, 6, f"[ Place {theme} Clipart x{q.get('num', '')} Here ]", align="C")
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("ComicNeue", "B", 26)
            pdf.set_xy(x_start + 95, y_start + (box_h / 2) - 8)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(75, 14, f"Count = {q.get('num', '')}", align="C")
            else:
                pdf.cell(75, 14, "Count = [      ]", align="C")

        elif "What Comes Next" in topic:
            pdf.set_font("ComicNeue", "B", 24)
            pdf.set_xy(x_start + 5, y_start + 12)
            seq = q.get('seq', [0,0,0])
            seq_text = f"{seq[0]},  {seq[1]},  {seq[2]},  "
            pdf.cell(58, 12, seq_text, align="R")
            
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(20, 12, str(q.get('ans', '')), align="L")
            else:
                pdf.set_draw_color(0, 0, 0)
                pdf.set_line_width(0.6)
                pdf.line(pdf.get_x() + 1, y_start + 22, pdf.get_x() + 14, y_start + 22)

        elif "Order Numbers" in topic:
            pdf.set_font("ComicNeue", "B", 24)
            pdf.set_xy(x_start + 15, y_start + 10)
            num_str = "   .   ".join(map(str, q.get('nums', [])))
            pdf.cell(70, 12, f"Mix:  {num_str}", align="L")
            
            pdf.set_xy(x_start + 95, y_start + 11)
            if is_answer_key:
                pdf.set_font("ComicNeue", "B", 20)
                pdf.set_text_color(*ans_color)
                ans_str = "  <  ".join(map(str, q.get('sorted', [])))
                pdf.cell(75, 10, f"Ans: {ans_str}", align="C")
            else:
                pdf.set_font("ComicNeue", "B", 22)
                pdf.cell(75, 10, "[    ] < [    ] < [    ] < [    ]", align="C")

        elif "Write Number's Name" in topic:
            pdf.set_font("ComicNeue", "B", 24)
            pdf.set_xy(x_start + 5, y_start + 11)
            pdf.cell(28, 12, f"{q.get('num', '')}  = ", align="R")
            
            if is_answer_key:
                pdf.set_font("ComicNeue", "B", 18)
                pdf.set_text_color(*ans_color)
                pdf.cell(50, 12, str(q.get('word', '')).upper(), align="L")
            else:
                pdf.set_font("ComicNeue", "", 15)
                pdf.cell(50, 12, "__________________", align="L")

        elif "Missing Addends" in topic:
            pdf.set_font("ComicNeue", "B", 24)
            pdf.set_xy(x_start + 5, y_start + 11)
            pdf.cell(22, 12, f"{q.get('a', '')}  +", align="R")
            
            box_x = pdf.get_x() + 2
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(0.5)
            pdf.rect(box_x, y_start + 11, 13, 13)
            
            if is_answer_key:
                pdf.set_xy(box_x, y_start + 11)
                pdf.set_text_color(*ans_color)
                pdf.cell(13, 13, str(q.get('b', '')), align="C")
                pdf.set_text_color(0, 0, 0)
            
            pdf.set_xy(box_x + 16, y_start + 11)
            pdf.cell(30, 12, f"=  {q.get('ans', '')}", align="L")

        elif "Picture Subtraction" in topic:
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.2)
            pdf.set_dash_pattern(dash=1.5, gap=1.5)
            pdf.rect(x_start + 15, y_start + 5, 152, 24, style="D")
            pdf.set_dash_pattern()
            
            pdf.set_font("ComicNeue", "", 9)
            pdf.set_text_color(150, 150, 150)
            pdf.set_xy(x_start + 15, y_start + 14)
            pdf.cell(152, 6, f"[ Drop {q.get('a', '')} copies of {theme} clipart here. Students cross out {q.get('b', '')} ]", align="C")
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("ComicNeue", "B", 26)
            pdf.set_xy(x_start + 15, y_start + 34)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(152, 14, f"{q.get('a', '')}   -   {q.get('b', '')}   =   {q.get('ans', '')}", align="C")
            else:
                pdf.cell(152, 14, f"{q.get('a', '')}   -   {q.get('b', '')}   =   ______", align="C")

        elif "Color by Answer" in topic:
            pdf.set_font("ComicNeue", "B", 26)
            pdf.set_xy(x_start + 15, y_start + 14)
            pdf.cell(65, 14, f"{q.get('a', '')}  +  {q.get('b', '')}  =  ?", align="L")
            
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.2)
            pdf.set_dash_pattern(dash=1.5, gap=1.5)
            pdf.rect(x_start + 90, y_start + 6, 80, box_h - 12, style="D")
            pdf.set_dash_pattern()
            
            pdf.set_font("ComicNeue", "", 9)
            pdf.set_text_color(150, 150, 150)
            pdf.set_xy(x_start + 90, y_start + (box_h / 2) - 3)
            pdf.cell(80, 6, f"[ Place {theme} Clipart with Text '{q.get('ans', '')}' Inside ]", align="C")
            
            pdf.set_xy(x_start + 15, y_start + 35)
            pdf.set_font("ComicNeue", "B", 12)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(65, 6, f"CODE {q.get('ans', '')}  ->  {q.get('color', '')}", align="L")
            else:
                pdf.set_text_color(90, 90, 90)
                pdf.cell(65, 6, f"If Answer is {q.get('ans', '')}  ->  Color it {q.get('color', '')}", align="L")

        elif "How Many Sides" in topic:
            pdf.set_font("ComicNeue", "B", 24)
            pdf.set_xy(x_start + 15, y_start + 16)
            pdf.cell(85, 12, f"Shape:  {q.get('shape', '')}", align="L")
            
            pdf.set_xy(x_start + 110, y_start + 16)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(55, 12, f"Sides = {q.get('sides', '')}", align="R")
            else:
                pdf.cell(55, 12, "Sides = [      ]", align="R")

        elif "Tens and Ones" in topic:
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.2)
            pdf.set_dash_pattern(dash=1.5, gap=1.5)
            pdf.rect(x_start + 15, y_start + 6, 75, box_h - 12, style="D")
            pdf.set_dash_pattern()
            
            pdf.set_font("ComicNeue", "", 9)
            pdf.set_text_color(150, 150, 150)
            pdf.set_xy(x_start + 15, y_start + (box_h / 2) - 3)
            pdf.cell(75, 6, f"[ Drop {q.get('tens', '')} Tens & {q.get('ones', '')} Ones Blocks Here ]", align="C")
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("ComicNeue", "B", 16)
            pdf.set_xy(x_start + 95, y_start + 12)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(75, 8, f"{q.get('tens', '')} Tens and {q.get('ones', '')} Ones", align="C")
                pdf.set_xy(x_start + 95, y_start + 26)
                pdf.set_font("ComicNeue", "B", 26)
                pdf.cell(75, 12, f"=   {q.get('total', '')}", align="C")
            else:
                pdf.cell(75, 8, "____ Tens and ____ Ones", align="C")
                pdf.set_xy(x_start + 95, y_start + 26)
                pdf.set_font("ComicNeue", "B", 26)
                pdf.cell(75, 12, "=   [      ]", align="C")

        elif "True or False" in topic:
            pdf.set_font("ComicNeue", "B", 24)
            pdf.set_xy(x_start + 4, y_start + 8)
            pdf.cell(80, 12, f"{q.get('a', '')}  +  {q.get('b', '')}  =  {q.get('eq_ans', '')}", align="C")
            
            pdf.set_font("ComicNeue", "B", 14)
            pdf.set_xy(x_start + 4, y_start + 23)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                choice_text = "[ TRUE ]      FALSE" if q.get('is_true') else "TRUE      [ FALSE ]"
                pdf.cell(80, 8, choice_text, align="C")
            else:
                pdf.set_text_color(110, 110, 110)
                pdf.cell(80, 8, "TRUE   /   FALSE", align="C")

        elif "Which is More" in topic:
            pdf.set_font("ComicNeue", "B", 26)
            pdf.set_xy(x_start + 5, y_start + 12)
            
            if is_answer_key:
                if q.get('a') == q.get('more'):
                    pdf.set_text_color(*ans_color)
                    pdf.cell(39, 12, f"({q.get('a', '')})", align="C")
                    pdf.set_text_color(0, 0, 0)
                    pdf.cell(39, 12, str(q.get('b', '')), align="C")
                else:
                    pdf.cell(39, 12, str(q.get('a', '')), align="C")
                    pdf.set_text_color(*ans_color)
                    pdf.cell(39, 12, f"({q.get('b', '')})", align="C")
            else:
                pdf.cell(39, 12, str(q.get('a', '')), align="C")
                pdf.cell(39, 12, str(q.get('b', '')), align="C")

        elif "Count by 5's" in topic:
            pdf.set_font("ComicNeue", "B", 20)
            pdf.set_xy(x_start + 4, y_start + 12)
            seq = q.get('seq', [0,0,0,0])
            pdf.cell(24, 12, f"{seq[0]},  ", align="R")
            
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(56, 12, f"{seq[1]},   {seq[2]},   {seq[3]}", align="L")
            else:
                pdf.set_font("ComicNeue", "", 18)
                pdf.cell(56, 12, "__ ,   __ ,   __", align="L")

        elif "Roll It On" in topic:
            pdf.set_font("ComicNeue", "B", 16)
            pdf.set_xy(x_start + 4, y_start + 8)
            pdf.cell(80, 8, f"Dice:  [{q.get('d1', '')}]  +  [{q.get('d2', '')}]", align="C")
            
            pdf.set_font("ComicNeue", "B", 22)
            pdf.set_xy(x_start + 4, y_start + 20)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(80, 10, f"Total  =  {q.get('ans', '')}", align="C")
            else:
                pdf.cell(80, 10, "Total  =  [      ]", align="C")

        pdf.set_text_color(0, 0, 0)
        
        if is_two_col:
            if col_idx == 1:
                pdf.set_y(y_start + box_h + 5)
        else:
            pdf.set_y(y_start + box_h + 5)
            
    if is_two_col and (num_q % 2 != 0):
        pdf.set_y(pdf.get_y() + box_h + 5)

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
        คุณสามารถใส่ชื่อแบรนด์หรือชื่อร้านค้าของคุณที่เมนูด้านซ้าย เพื่อให้ระบบพิมพ์เครื่องหมายลิขสิทธิ์ 
        และชื่อร้านค้าของคุณลงที่ <strong>มุมขวาล่าง</strong> ของใบงานโดยอัตโนมัติ พร้อมระบบจัดเลเอาต์สมมาตร (Symmetry Grid) 
        และตีเส้นประมาร์กตำแหน่งสำหรับนำไปลากรูป Clipart ตกแต่งต่อใน Canva ได้อย่างแม่นยำ
    </div>
    """, unsafe_allow_html=True
)

# แถบควบคุมด้านข้าง (Sidebar Settings)
st.sidebar.header("⚙️ ใบงานสไตล์เลเอาต์พรีเมียม")

# ช่องใส่ชื่อร้านค้าสำหรับไปแสดงผลใน Footer ลิขสิทธิ์มุมขวาล่าง
tpt_store_name = st.sidebar.text_input(
    "🏪 ชื่อร้านค้าของคุณ (TpT Store / Brand Name):", 
    value="Kindergarten Learning Press"
)

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
num_q = st.sidebar.slider("📌 จำนวนโจทย์ต่อหน้า (หากเป็นข้อสั้นระบบจะปัดเป็นเลขคู่เพื่อความสมบูรณ์):", min_value=2, max_value=8, value=4, step=2)
include_ans = st.sidebar.checkbox("✅ สร้างใบงานคู่ขนานพร้อมแผ่นเฉลย (Answer Key)", value=True)

st.sidebar.markdown("---")

# ปุ่มสุ่มโจทย์ใหม่โดยใช้ตัวเลขเดิมตามการตั้งค่า
if st.sidebar.button("🎲 สุ่มตัวเลขโจทย์ใหม่ (Shuffle Numbers)", use_container_width=True):
    st.session_state.force_reroll = True

# ตรวจสอบความเปลี่ยนแปลงของค่าเงื่อนไขรวมถึงชื่อร้านค้า เพื่อเรนเดอร์ PDF ใหม่แบบ Real-time
current_settings = f"{topic}_{theme}_{num_q}_{include_ans}_{tpt_store_name}"
if 'last_settings' not in st.session_state or st.session_state.last_settings != current_settings or st.session_state.get('force_reroll', False):
    with st.spinner("กำลังเรนเดอร์โครงสร้างกระดาษความละเอียดสูง..."):
        # 1. คำนวณค่าและสร้างชุดข้อมูลโจทย์
        st.session_state.q_data = generate_questions_data(topic, num_q)
        # 2. เรนเดอร์ไฟล์ PDF จริงลงหน่วยความจำชั่วคราว พร้อมส่งค่าชื่อร้านค้า
        st.session_state.ws_path = render_pdf_worksheet_updated(topic, theme, st.session_state.q_data, tpt_store_name, is_answer_key=False)
        if include_ans:
            st.session_state.ans_path = render_pdf_worksheet_updated(topic, theme, st.session_state.q_data, tpt_store_name, is_answer_key=True)
        
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
            file_name=f"Worksheet_{topic.split('. ')[1].replace(' ', '_')}.pdf", 
            mime="application/pdf", 
            use_container_width=True,
            type="primary"
        )
        st.markdown(f"🔒 **สิทธิ์การใช้งาน:** ออกให้ในนามแบรนด์ **{tpt_store_name}** ท้ายหน้ากระดาษขวาล่างเรียบร้อย")
        
        # กล่องแนะนำขั้นตอนการต่อยอดเพื่อสร้างมูลค่าใน Canva
        st.markdown(
            f"""
            <div style='background-color: #e3f2fd; padding: 15px; border-radius: 6px; margin-top: 15px; color: #0d47a1;'>
                <strong>💡 คำแนะนำสไตล์ครูนักขาย TpT:</strong><br>
                1. พิมพ์ชื่อร้านค้าของคุณในเมนูซ้ายมือเพื่อฝังลิขสิทธิ์<br>
                2. กดดาวน์โหลดไฟล์ PDF ด้านบนนี้<br>
                3. นำไปอัปโหลดเข้าสู่หน้าออกแบบของ <strong>Canva</strong><br>
                4. ค้นหาองค์ประกอบกราฟิกธีม <strong>"{theme}"</strong> ที่สวยงาม น่ารัก<br>
                5. นำรูปภาพการ์ตูนเหล่านั้นไปลากวางซ้อนบนกล่องเส้นประ <code>[ Place {theme} Clipart ]</code> ที่ระบบตีเส้นจัดสัดส่วนไว้ให้<br>
                6. กดเซฟเป็นไฟล์รูปภาพหรือ PDF คุณภาพสูงเพื่อนำไปลิสต์ขายได้ทันที!
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
                file_name=f"AnswerKey_{topic.split('. ')[1].replace(' ', '_')}.pdf", 
                mime="application/pdf", 
                use_container_width=True
            )
            st.info("🎯 แผ่นเฉลยจะใช้ตัวเลขชุดเดียวกับใบงานหลัก แต่ทำการพิมพ์คำตอบและแสดงเครื่องหมายวงเล็บ/คำตอบขนาดใหญ่ด้วยสีแดง (RGB: 220, 50, 50) เพื่อให้ครูและผู้ปกครองตรวจทานได้ง่ายและรวดเร็ว")
            
        with col2: 
            st.markdown("<div class='premium-paper'>", unsafe_allow_html=True)
            display_pdf_preview(st.session_state.ans_path)
            st.markdown("</div>", unsafe_allow_html=True)
