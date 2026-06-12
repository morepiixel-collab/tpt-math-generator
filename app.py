import streamlit as st
from fpdf import FPDF
import tempfile
import os
import random
import urllib.request
import fitz  # PyMuPDF
from PIL import Image

# ==========================================
# PART 1: Ultra-Premium Setup & Colorful Template
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
    def __init__(self, store_name="Your TpT Store", grade_level="KINDERGARTEN", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.store_name = store_name
        self.grade_level = grade_level  # รับค่าระดับชั้นเพื่อไปแสดงผลที่หัวกระดาษ
        if os.path.exists("ComicNeue-Regular.ttf"):
            self.add_font("ComicNeue", style="", fname="ComicNeue-Regular.ttf")
        if os.path.exists("ComicNeue-Bold.ttf"):
            self.add_font("ComicNeue", style="B", fname="ComicNeue-Bold.ttf")

    def header(self):
        self.set_fill_color(224, 243, 255)
        self.rect(10, 10, 190, 24, style="F")
        
        self.set_draw_color(40, 60, 90)
        self.set_line_width(1.0)
        self.rect(10, 10, 190, 277)
        self.set_line_width(0.3)
        self.rect(12, 12, 186, 273)
        
        self.set_fill_color(255, 223, 100)
        self.rect(15, 14, 55, 8, style="DF")
        self.set_font("ComicNeue", "B", 10)
        self.set_text_color(20, 20, 20)
        self.set_xy(15, 14)
        # ✨ เปลี่ยนชื่อบนป้ายเหลืองตามระดับชั้นที่เลือก
        self.cell(55, 8, f"  {self.grade_level.upper()} MATH  ", align="C")
        
        self.set_text_color(0, 0, 0)
        self.set_font("ComicNeue", "B", 11)
        self.set_xy(110, 14)
        self.cell(85, 8, "Name: _____________________", align="R")
        
        self.set_xy(15, 24)
        self.set_font("ComicNeue", "B", 10)
        self.cell(50, 6, "Date: _______________", align="L")
        self.set_xy(140, 24)
        self.cell(55, 6, "Score: _________ / _________", align="R")
        
        self.set_draw_color(40, 60, 90)
        self.set_line_width(0.6)
        self.line(10, 34, 200, 34)
        self.ln(12)

    def footer(self):
        self.set_y(-18)
        self.set_x(14)
        self.set_font("ComicNeue", "B", 9)
        self.set_text_color(120, 130, 150)
        
        copyright_text = f"(c) {self.store_name}  |  All Rights Reserved."
        self.cell(182, 4, copyright_text, align="R")
        self.set_text_color(0, 0, 0)

# ==========================================
# PART 2: Math Question Generation Engine (PreK - K2 Adaptive)
# ==========================================
def generate_questions_data(topic, num_questions, grade_level):
    is_two_col = any(k in topic for k in ["Next", "Name", "Missing", "True", "More", "5's", "Roll"])
    if is_two_col and num_questions % 2 != 0:
        num_questions += 1

    questions = []
    used_keys = set()
    
    if grade_level == "Pre-K":
        num_pool = range(1, 6)
        sum_limit = 5
        dice_pool = range(1, 4)
    elif grade_level == "K1":
        num_pool = range(1, 11)
        sum_limit = 10
        dice_pool = range(1, 7)
    else: # K2
        num_pool = range(11, 21)
        sum_limit = 15
        dice_pool = range(1, 7)

    for i in range(num_questions):
        attempts = 0
        while attempts < 100:
            attempts += 1
            q_item = None
            key = None
            
            # ✨ อัปเดตรองรับชื่อหัวข้อที่เปลี่ยนไปตามวัย
            if any(k in topic for k in ["Count the Objects", "Count to Ten", "Teen Numbers"]):
                num = random.choice(num_pool)
                q_item = {"num": num}
                key = num
                
            elif "What Comes Next" in topic:
                start_max = 2 if grade_level == "Pre-K" else (7 if grade_level == "K1" else 16)
                start = random.randint(1, start_max)
                q_item = {"seq": [start, start+1, start+2], "ans": start+3}
                key = start
                
            elif "Order Numbers" in topic:
                nums = random.sample(num_pool, 4)
                q_item = {"nums": nums, "sorted": sorted(nums)}
                key = tuple(sorted(nums))
                
            elif "Write Number's Name" in topic:
                num = random.choice(num_pool)
                words_map = {
                    1:"one", 2:"two", 3:"three", 4:"four", 5:"five",
                    6:"six", 7:"seven", 8:"eight", 9:"nine", 10:"ten",
                    11:"eleven", 12:"twelve", 13:"thirteen", 14:"fourteen", 15:"fifteen",
                    16:"sixteen", 17:"seventeen", 18:"eighteen", 19:"nineteen", 20:"twenty"
                }
                q_item = {"num": num, "word": words_map[num]}
                key = num
                
            elif "Missing Addends" in topic:
                ans = random.randint(3, sum_limit)
                a = random.randint(1, ans - 1)
                q_item = {"a": a, "b": ans - a, "ans": ans}
                key = (a, ans)
                
            elif "Picture Subtraction" in topic:
                a = random.randint(2, sum_limit)
                b = random.randint(1, a - 1)
                q_item = {"a": a, "b": b, "ans": a - b}
                key = (a, b)
                
            elif "Color by Answer" in topic:
                ans = random.randint(2, sum_limit)
                a = random.randint(1, ans - 1)
                colors = ["Red", "Blue", "Green", "Yellow", "Pink", "Purple", "Orange"]
                q_item = {"a": a, "b": ans - a, "ans": ans, "color": colors[i % len(colors)]}
                key = (a, ans)
                
            elif "How Many Sides" in topic:
                shapes = [{"shape": "Triangle", "sides": 3}, {"shape": "Square", "sides": 4},
                          {"shape": "Rectangle", "sides": 4}, {"shape": "Circle", "sides": 0}]
                if grade_level != "Pre-K": 
                    shapes.extend([{"shape": "Pentagon", "sides": 5}, {"shape": "Hexagon", "sides": 6}])
                q_item = random.choice(shapes)
                key = q_item["shape"]
                
            elif "Tens and Ones" in topic:
                if grade_level == "Pre-K": tens, ones = 1, random.randint(0, 5)
                elif grade_level == "K1": tens, ones = 1, random.randint(0, 9)
                else: tens, ones = random.randint(1, 2), random.randint(0, 9)
                q_item = {"tens": tens, "ones": ones, "total": (tens * 10) + ones}
                key = (tens, ones)
                
            elif "True or False" in topic:
                a = random.randint(1, max(1, sum_limit - 2))
                b = random.randint(1, sum_limit - a)
                is_true = random.choice([True, False])
                eq_ans = (a + b) if is_true else (a + b + random.choice([-1, 1]))
                if eq_ans <= 0: eq_ans = a + b + 1
                q_item = {"a": a, "b": b, "eq_ans": eq_ans, "is_true": is_true}
                key = (a, b, eq_ans)
                
            elif "Which is More" in topic:
                a, b = random.sample(num_pool, 2)
                q_item = {"a": a, "b": b, "more": max(a, b)}
                key = tuple(sorted([a, b]))
                
            elif "Count by 5's" in topic:
                start_pool = [5, 10, 15] if grade_level == "Pre-K" else [5, 10, 15, 20, 25, 30, 35, 40]
                start = random.choice(start_pool)
                q_item = {"seq": [start, start + 5, start + 10, start + 15]}
                key = start
                
            elif "Roll It On" in topic:
                d1, d2 = random.choice(dice_pool), random.choice(dice_pool)
                q_item = {"d1": d1, "d2": d2, "ans": d1 + d2}
                key = (d1, d2)

            if key not in used_keys:
                used_keys.add(key)
                questions.append(q_item)
                break
        else:
            questions.append(q_item)
            
    return questions

# ==========================================
# PART 3: Premium Grid Render Layout Engine
# ==========================================
def render_pdf_worksheet_updated(topic, theme, questions_data, store_name, grade_level, is_answer_key=False):
    pdf = PremiumWorksheetPDF(store_name=store_name, grade_level=grade_level, orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)
    
    pdf.set_font("ComicNeue", "B", 22)
    title_text = topic.split(". ")[1]
    if is_answer_key:
        pdf.set_text_color(220, 50, 50)
        title_text += " (ANSWER KEY)"
    pdf.set_y(36)
    pdf.cell(0, 12, title_text, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)

    pdf.set_font("ComicNeue", "B", 12)
    pdf.set_x(14)
    
    # อัปเดตคำสั่งชี้แจงให้เข้ากับหัวข้อที่ถูกเปลี่ยนชื่อ
    directions_map = {
        "1. Count the Objects": f"Directions: Count the cute {theme.lower()} items and write the number in the box.",
        "1. Count to Ten": f"Directions: Count the cute {theme.lower()} items and write the number in the box.",
        "1. Teen Numbers": f"Directions: Count the cute {theme.lower()} items and write the correct teen number in the box.",
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
        "13. Roll It On": "Directions: Count the dots on the dice. Write the total sum in the box below."
    }
    # ใช้ค่า Fallback ถ้าไม่มีตรงตัว
    matched_direction = directions_map.get(topic, "Directions: Solve the math problems on this worksheet carefully.")
    pdf.multi_cell(182, 6, matched_direction)
    pdf.ln(4)

    is_two_col = any(k in topic for k in ["Next", "Name", "Missing", "True", "More", "5's", "Roll"])
    col_w = 88 if is_two_col else 182
    box_h = 36 if is_two_col else 46
    
    if "Order Numbers" in topic: box_h = 32
    if "Subtraction" in topic or "Color by" in topic or "Ones" in topic: box_h = 52

    num_q = len(questions_data)
    pdf.set_y(54) 

    for i, q in enumerate(questions_data, start=1):
        if is_two_col:
            col_idx = (i - 1) % 2 
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
        
        pdf.set_draw_color(180, 180, 180)
        pdf.set_line_width(0.4)
        pdf.rect(x_start, y_start, col_w, box_h, style="D")
        
        pdf.set_font("ComicNeue", "B", 11)
        pdf.set_text_color(110, 110, 110)
        pdf.set_xy(x_start + 3, y_start + 3)
        pdf.cell(10, 5, f"Q{i}", align="L")
        pdf.set_text_color(0, 0, 0)
        
        ans_color = (220, 50, 50) if is_answer_key else (0, 0, 0)
        
        # --- เช็คเงื่อนไขตามชื่อหัวข้อ ---
        if any(k in topic for k in ["Count the Objects", "Count to Ten", "Teen Numbers"]):
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
            pdf.set_font("ComicNeue", "B", 20)
            pdf.set_xy(x_start + 95, y_start + (box_h / 2) - 6)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(75, 12, f"Count = {q.get('num', '')}", align="C")
            else:
                pdf.cell(75, 12, "Count = [      ]", align="C")

        elif "What Comes Next" in topic:
            pdf.set_font("ComicNeue", "B", 18)
            pdf.set_xy(x_start + 5, y_start + 12)
            seq = q.get('seq', [0,0,0])
            if is_answer_key:
                full_str = f"{seq[0]},  {seq[1]},  {seq[2]},  {q.get('ans', '')}"
                pdf.set_text_color(*ans_color)
                pdf.cell(78, 12, full_str, align="C")
            else:
                full_str = f"{seq[0]},  {seq[1]},  {seq[2]},  ____"
                pdf.cell(78, 12, full_str, align="C")

        elif "Order Numbers" in topic:
            pdf.set_font("ComicNeue", "B", 16)
            pdf.set_xy(x_start + 10, y_start + 6)
            num_str = "   ,   ".join(map(str, q.get('nums', [])))
            pdf.cell(162, 8, f"Mix:  {num_str}", align="C")
            
            pdf.set_xy(x_start + 10, y_start + 18)
            if is_answer_key:
                pdf.set_font("ComicNeue", "B", 16)
                pdf.set_text_color(*ans_color)
                ans_str = "  <  ".join(map(str, q.get('sorted', [])))
                pdf.cell(162, 8, f"Ans: {ans_str}", align="C")
            else:
                pdf.set_font("ComicNeue", "B", 14)
                pdf.cell(162, 8, "[      ]  <  [      ]  <  [      ]  <  [      ]", align="C")

        elif "Write Number's Name" in topic:
            pdf.set_font("ComicNeue", "B", 18)
            pdf.set_xy(x_start + 5, y_start + 12)
            num = q.get('num', '')
            if is_answer_key:
                pdf.cell(30, 12, f"{num}  =  ", align="R")
                pdf.set_text_color(*ans_color)
                pdf.cell(48, 12, str(q.get('word', '')).upper(), align="L")
            else:
                pdf.cell(30, 12, f"{num}  =  ", align="R")
                pdf.cell(48, 12, "___________", align="L")

        elif "Missing Addends" in topic:
            pdf.set_font("ComicNeue", "B", 18)
            pdf.set_xy(x_start + 5, y_start + 12)
            if is_answer_key:
                pdf.cell(25, 12, f"{q.get('a', '')}  +", align="R")
                pdf.set_text_color(*ans_color)
                pdf.cell(15, 12, f" {q.get('b', '')} ", align="C")
                pdf.set_text_color(0, 0, 0)
                pdf.cell(33, 12, f"=  {q.get('ans', '')}", align="L")
            else:
                pdf.cell(25, 12, f"{q.get('a', '')}  +", align="R")
                pdf.cell(15, 12, "[    ]", align="C")
                pdf.cell(33, 12, f"=  {q.get('ans', '')}", align="L")

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
            pdf.set_font("ComicNeue", "B", 22)
            pdf.set_xy(x_start + 15, y_start + 34)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(152, 14, f"{q.get('a', '')}   -   {q.get('b', '')}   =   {q.get('ans', '')}", align="C")
            else:
                pdf.cell(152, 14, f"{q.get('a', '')}   -   {q.get('b', '')}   =   ______", align="C")

        elif "Color by Answer" in topic:
            pdf.set_font("ComicNeue", "B", 22)
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
            pdf.set_font("ComicNeue", "B", 20)
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
                pdf.set_font("ComicNeue", "B", 22)
                pdf.cell(75, 12, f"=   {q.get('total', '')}", align="C")
            else:
                pdf.cell(75, 8, "____ Tens and ____ Ones", align="C")
                pdf.set_xy(x_start + 95, y_start + 26)
                pdf.set_font("ComicNeue", "B", 22)
                pdf.cell(75, 12, "=   [      ]", align="C")

        elif "True or False" in topic:
            pdf.set_font("ComicNeue", "B", 18)
            pdf.set_xy(x_start + 4, y_start + 8)
            pdf.cell(80, 12, f"{q.get('a', '')}  +  {q.get('b', '')}  =  {q.get('eq_ans', '')}", align="C")
            
            pdf.set_font("ComicNeue", "B", 12)
            pdf.set_xy(x_start + 4, y_start + 22)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                choice_text = "[ TRUE ]      FALSE" if q.get('is_true') else "TRUE      [ FALSE ]"
                pdf.cell(80, 8, choice_text, align="C")
            else:
                pdf.set_text_color(110, 110, 110)
                pdf.cell(80, 8, "TRUE   /   FALSE", align="C")

        elif "Which is More" in topic:
            pdf.set_font("ComicNeue", "B", 20)
            pdf.set_xy(x_start + 4, y_start + 12)
            if is_answer_key:
                if q.get('a') == q.get('more'):
                    pdf.set_text_color(*ans_color)
                    pdf.cell(40, 12, f"({q.get('a', '')})", align="C")
                    pdf.set_text_color(0, 0, 0)
                    pdf.cell(40, 12, str(q.get('b', '')), align="C")
                else:
                    pdf.set_text_color(0, 0, 0)
                    pdf.cell(40, 12, str(q.get('a', '')), align="C")
                    pdf.set_text_color(*ans_color)
                    pdf.cell(40, 12, f"({q.get('b', '')})", align="C")
            else:
                pdf.cell(40, 12, str(q.get('a', '')), align="C")
                pdf.cell(40, 12, str(q.get('b', '')), align="C")

        elif "Count by 5's" in topic:
            pdf.set_font("ComicNeue", "B", 18)
            pdf.set_xy(x_start + 5, y_start + 12)
            seq = q.get('seq', [0,0,0,0])
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                full_seq = f"{seq[0]},  {seq[1]},  {seq[2]},  {seq[3]}"
                pdf.cell(78, 12, full_seq, align="C")
            else:
                full_seq = f"{seq[0]},  ____,  ____,  ____"
                pdf.cell(78, 12, full_seq, align="C")

        elif "Roll It On" in topic:
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.2)
            pdf.set_dash_pattern(dash=1.5, gap=1.5)
            pdf.rect(x_start + 10, y_start + 6, 68, 14, style="D")
            pdf.set_dash_pattern()
            
            pdf.set_font("ComicNeue", "", 9)
            pdf.set_text_color(150, 150, 150)
            pdf.set_xy(x_start + 10, y_start + 10)
            pdf.cell(68, 6, f"[ Place Dice {q.get('d1', '')} & {q.get('d2', '')} Here ]", align="C")
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("ComicNeue", "B", 18)
            pdf.set_xy(x_start + 4, y_start + 22)
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
    file_path = os.path.join(temp_dir, f"{grade_level}_{file_prefix}{safe_topic}.pdf")
    pdf.output(file_path)
    return file_path

# ==========================================
# PART 4: Premium Streamlit UI & Execution
# ==========================================
def display_pdf_preview(file_path):
    try:
        doc = fitz.open(file_path)
        page = doc.load_page(0) 
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
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
        st.error(f"⚠️ ไม่สามารถแสดงพรีวิวได้ชั่วคราว: {e}")

st.set_page_config(page_title="PreK - K2 Math Worksheet Generator", page_icon="✏️", layout="wide")

st.title("✏️ PreK - K2 Math Worksheet Generator")
st.markdown(
    """
    <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #ffaa00; margin-bottom: 20px;'>
        <strong>🌟 อัปเกรดระบบปรับระดับชั้นแบบเต็มรูปแบบ (Adaptive Syllabus)</strong><br>
        เมื่อคุณเลือกระดับชั้น (Pre-K, K1, K2) หัวข้อกิจกรรมใน Dropdown จะถูกคัดกรองให้เหลือเฉพาะบทเรียนที่เหมาะสมกับวัยนั้นๆ โดยอัตโนมัติ พร้อมทั้งปรับป้ายชื่อบนหัวใบงานให้ตรงกับระดับที่คุณเลือกด้วย!
    </div>
    """, unsafe_allow_html=True
)

st.sidebar.header("⚙️ การตั้งค่าใบงาน (Settings)")

tpt_store_name = st.sidebar.text_input("🏪 ชื่อร้านค้าของคุณ (TpT Store):", value="Kindergarten Learning Press")
grade_level = st.sidebar.radio("📚 เลือกระดับชั้น (Difficulty Level):", ["Pre-K", "K1", "K2"], index=1)

# ✨ อัปเกรดจุดนี้: กรองลิสต์หัวข้อให้เหมาะสมกับระดับชั้นที่เลือก
if grade_level == "Pre-K":
    available_topics = [
        "1. Count the Objects", "2. What Comes Next?", "3. Order Numbers (Smallest to Largest)",
        "4. Write Number's Name", "6. Picture Subtraction", "8. How Many Sides?", 
        "11. Which is More?", "13. Roll It On"
    ]
elif grade_level == "K1":
    available_topics = [
        "1. Count to Ten", "2. What Comes Next?", "3. Order Numbers (Smallest to Largest)",
        "4. Write Number's Name", "5. Missing Addends", "6. Picture Subtraction",
        "7. Color by Answer", "8. How Many Sides?", "10. True or False",
        "11. Which is More?", "13. Roll It On"
    ]
else: # K2
    available_topics = [
        "1. Teen Numbers", "2. What Comes Next?", "3. Order Numbers (Smallest to Largest)",
        "4. Write Number's Name", "5. Missing Addends", "6. Picture Subtraction",
        "7. Color by Answer", "8. How Many Sides?", "9. Tens and Ones",
        "10. True or False", "11. Which is More?", "12. Count by 5's", "13. Roll It On"
    ]

topic = st.sidebar.selectbox("🎯 เลือกหัวข้อกิจกรรม:", available_topics)
theme = st.sidebar.selectbox("🎨 เลือกธีมตัวละคร Clipart:", ["Space", "Ocean", "Animals", "Monsters", "School", "Food", "Dinosaurs"])
num_q = st.sidebar.slider("📌 จำนวนโจทย์ต่อหน้า:", min_value=2, max_value=8, value=4, step=2)
include_ans = st.sidebar.checkbox("✅ สร้างใบงานคู่ขนานพร้อมแผ่นเฉลย", value=True)

st.sidebar.markdown("---")

if st.sidebar.button("🎲 สุ่มตัวเลขโจทย์ใหม่ (Shuffle Numbers)", use_container_width=True):
    st.session_state.force_reroll = True

current_settings = f"{topic}_{theme}_{num_q}_{include_ans}_{tpt_store_name}_{grade_level}"
if 'last_settings' not in st.session_state or st.session_state.last_settings != current_settings or st.session_state.get('force_reroll', False):
    with st.spinner(f"กำลังเรนเดอร์โครงสร้างกระดาษระดับ {grade_level}..."):
        st.session_state.q_data = generate_questions_data(topic, num_q, grade_level)
        st.session_state.ws_path = render_pdf_worksheet_updated(topic, theme, st.session_state.q_data, tpt_store_name, grade_level, is_answer_key=False)
        if include_ans:
            st.session_state.ans_path = render_pdf_worksheet_updated(topic, theme, st.session_state.q_data, tpt_store_name, grade_level, is_answer_key=True)
        
        st.session_state.last_settings = current_settings
        st.session_state.force_reroll = False

st.subheader(f"🔍 พรีวิวหน้ากระดาษ ({grade_level} Level)")
tabs = st.tabs(["📄 Worksheet", "🔑 Answer Key"]) if include_ans else st.tabs(["📄 Worksheet"])

with tabs[0]:
    with open(st.session_state.ws_path, "rb") as f: ws_bytes = f.read()
    col1, col2 = st.columns([1, 2])
    with col1:
        st.download_button(
            label=f"🚀 Download {grade_level} Worksheet", 
            data=ws_bytes, 
            file_name=f"{grade_level}_Worksheet_{topic.split('. ')[1].replace(' ', '_')}.pdf", 
            mime="application/pdf", 
            use_container_width=True, type="primary"
        )
        st.markdown(f"**ระดับที่เลือก:** {grade_level}")
        st.markdown(f"**หัวข้อ:** {topic}")
    with col2: 
        st.markdown("<div class='premium-paper'>", unsafe_allow_html=True)
        display_pdf_preview(st.session_state.ws_path)
        st.markdown("</div>", unsafe_allow_html=True)

if include_ans:
    with tabs[1]:
        with open(st.session_state.ans_path, "rb") as f: ans_bytes = f.read()
        col1, col2 = st.columns([1, 2])
        with col1:
            st.download_button(
                label=f"📥 Download {grade_level} Answer Key", 
                data=ans_bytes, 
                file_name=f"{grade_level}_AnswerKey_{topic.split('. ')[1].replace(' ', '_')}.pdf", 
                mime="application/pdf", use_container_width=True
            )
        with col2: 
            st.markdown("<div class='premium-paper'>", unsafe_allow_html=True)
            display_pdf_preview(st.session_state.ans_path)
            st.markdown("</div>", unsafe_allow_html=True)
