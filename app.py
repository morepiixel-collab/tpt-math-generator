import streamlit as st
from fpdf import FPDF
import random
import fitz  
from PIL import Image
import os
import urllib.request

# ==========================================
# 0. ระบบดาวน์โหลดฟอนต์ (Comic Neue)
# ==========================================
FONT_FILE = "ComicNeue.ttf"
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/comicneue/ComicNeue-Bold.ttf"

if not os.path.exists(FONT_FILE):
    try:
        urllib.request.urlretrieve(FONT_URL, FONT_FILE)
    except Exception as e:
        st.error(f"⚠️ ไม่สามารถดาวน์โหลดฟอนต์ได้: {e}")

# ==========================================
# 1. ฐานข้อมูลหัวข้อ
# ==========================================
PRE_K_CURRICULUM = {
    "1. Number Sense (การรู้ค่าตัวเลข)": [
        "1. Find the Number",
        "2. Trace the Numbers",
        "3. Counting Objects",
        "4. Count and Match",
        "5. More or Less?",
        "6. Color by Number",
        "7. Missing Numbers",
        "8. Number Mazes"
    ],
    "2. Operations (การดำเนินการทางคณิตศาสตร์)": [
        "1. Color to Add",
        "2. Count and Color Total",
        "3. Take Away and Color",
        "4. Color the Addition Path",
        "5. Color to Make Target",
        "6. Draw and Color More",
        "7. Cross Out and Color",
        "8. Color the Correct Sum"
    ]
}

THEME_COLORS = {
    "Sweet Pink (ชมพูหวานแหวว) 🎀": {"primary": (244, 143, 177), "secondary": (129, 212, 250), "box": (255, 240, 245)},
    "Cotton Candy (ฟ้า-ชมพู)": {"primary": (118, 165, 234), "secondary": (244, 164, 185), "box": (248, 250, 255)},
    "Minty Fresh (เขียวมิ้นต์)": {"primary": (104, 195, 163), "secondary": (243, 156, 18), "box": (245, 255, 250)},
    "Lavender Dream (ม่วงอ่อน)": {"primary": (155, 89, 182), "secondary": (26, 188, 156), "box": (252, 248, 255)},
    "Sunshine (เหลือง-ส้ม)": {"primary": (243, 156, 18), "secondary": (231, 76, 60), "box": (255, 253, 240)}
}

# ==========================================
# 2. คลาสหน้ากระดาษ Premium Border
# ==========================================
class PremiumTpTPDF(FPDF):
    def __init__(self, topic_name, color_theme, shop_name, target_num, is_key=False):
        super().__init__(orientation='P', unit='mm', format='Letter')
        self.topic_name = topic_name
        self.colors = color_theme
        self.shop_name = shop_name 
        self.target_num = target_num 
        self.is_key = is_key
        self.set_auto_page_break(auto=True, margin=15)
        
        if os.path.exists(FONT_FILE):
            self.add_font("ComicNeue", "", FONT_FILE)
        else:
            self.add_font("ComicNeue", "", "helvetica") 

    def header(self):
        self.set_line_width(2.0)
        self.set_draw_color(*self.colors["primary"])
        self.rect(8, 8, 200, 263)
        
        self.set_line_width(0.3)
        self.set_draw_color(*self.colors["secondary"])
        if hasattr(self, 'set_dash_pattern'):
            self.set_dash_pattern(dash=2, gap=2)
            self.rect(11, 11, 194, 257)
            self.set_dash_pattern()
        else:
            self.rect(11, 11, 194, 257) 

        self.set_fill_color(*self.colors["primary"])
        self.rect(11, 11, 194, 28, style='F')
        
        self.set_font("ComicNeue", "", 12)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, " P R E - K   M A T H", ln=True, align="C")
        
        self.set_font("ComicNeue", "", 24)
        clean_topic = self.topic_name.split(". ", 1)[-1].upper()
        title = f"{clean_topic} : NUMBER {self.target_num}" + (" (KEY)" if self.is_key else "")
        self.cell(0, 10, title, ln=True, align="C")
        self.ln(6)
        
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.rect(11, 41, 194, 12, style='DF')
        
        self.set_font("ComicNeue", "", 14)
        self.set_text_color(100, 100, 100)
        self.set_y(44)
        self.cell(10, 5, "", ln=0)
        self.cell(90, 5, "Name: ___________________________", ln=0, align="L")
        self.cell(80, 5, "Date: _______________", ln=1, align="R")
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("ComicNeue", "", 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"© {self.shop_name} | All Rights Reserved.", align="C")

# ==========================================
# 3. Helpers สำหรับวาด 
# ==========================================
def draw_rounded_box(pdf, x, y, w, h, r, bg_color, text="", font_size=12, text_color=(150, 150, 150)):
    pdf.set_fill_color(*bg_color)
    pdf.set_draw_color(*bg_color) 
    pdf.rect(x + r, y, w - 2*r, h, 'F')
    pdf.rect(x, y + r, w, h - 2*r, 'F')
    pdf.ellipse(x, y, 2*r, 2*r, 'F')
    pdf.ellipse(x + w - 2*r, y, 2*r, 2*r, 'F')
    pdf.ellipse(x, y + h - 2*r, 2*r, 2*r, 'F')
    pdf.ellipse(x + w - 2*r, y + h - 2*r, 2*r, 2*r, 'F')
    
    if text:
        pdf.set_font("ComicNeue", "", font_size)
        pdf.set_text_color(*text_color)
        text_w = pdf.get_string_width(text)
        text_h_offset = (font_size * 0.352777) / 2.8 
        pdf.text(x + (w/2) - (text_w/2), y + (h/2) + text_h_offset, text)

def draw_solid_circle(pdf, x, y, d, text="", font_size=28, is_path=False):
    if pdf.is_key and is_path:
        pdf.set_fill_color(*pdf.colors["secondary"])
        pdf.set_draw_color(*pdf.colors["primary"])
        text_color = (255, 255, 255)
    else:
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(*pdf.colors["primary"])
        text_color = pdf.colors["primary"]
        
    pdf.set_line_width(0.8)
    pdf.ellipse(x, y, d, d, style='DF') 
    
    if text:
        pdf.set_font("ComicNeue", "", font_size)
        pdf.set_text_color(*text_color)
        text_w = pdf.get_string_width(text)
        text_h_offset = (font_size * 0.352777) / 3.0 
        pdf.text(x + (d/2) - (text_w/2), y + (d/2) + text_h_offset, text)

def draw_circle_placeholder(pdf, x, y, d, text="?"):
    pdf.set_fill_color(255, 255, 255) 
    pdf.set_draw_color(230, 230, 230)
    pdf.set_line_width(0.5)
    pdf.ellipse(x, y, d, d, style='DF')
        
    if text:
        pdf.set_font("ComicNeue", "", 28)
        pdf.set_text_color(180, 180, 180)
        text_w = pdf.get_string_width(text)
        text_h_offset = (28 * 0.352777) / 3.0
        pdf.text(x + (d/2) - (text_w/2), y + (d/2) + text_h_offset, text)

# ==========================================
# 4. BESPOKE LAYOUT ENGINE
# ==========================================
def generate_worksheet(sub_topic, theme_colors, num_q, shop_name, target_num, session_seed, is_key=False):
    random.seed(session_seed)
    
    pdf = PremiumTpTPDF(sub_topic, theme_colors, shop_name, target_num, is_key)
    pdf.add_page()
    
    center_x = 107.95 
    clean_sub = sub_topic.lower()
    pdf.set_font("ComicNeue", "", 14)
    pdf.set_text_color(80, 80, 80)

    # 1. FIND THE NUMBER
    if "find" in clean_sub:
        pdf.cell(0, 10, f" Directions: Find and color the number {target_num} in the picture below.", ln=True)
        pdf.ln(5)
        pdf.set_font("ComicNeue", "", 20)
        pdf.set_text_color(*theme_colors["primary"])
        pdf.cell(0, 10, f"Target: {target_num}", ln=True, align="C")
        draw_rounded_box(pdf, 15, 85, 185, 160, r=8, bg_color=theme_colors["box"], text=f"~ Canva: Add a large scene. Scatter number {target_num} everywhere! ~", font_size=14)

    # 2. TRACE THE NUMBERS
    elif "trace" in clean_sub:
        pdf.cell(0, 10, f" Directions: Trace and write the number {target_num}.", ln=True)
        pdf.ln(5)
        for i in range(num_q + 1): 
            if pdf.get_y() > 240: pdf.add_page()
            y = pdf.get_y()
            draw_rounded_box(pdf, 15, y, 185, 40, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (160 / 2)
            draw_rounded_box(pdf, start_x, y+5, 30, 30, r=5, bg_color=(255, 255, 255), text=f"~ {target_num} Items ~")
            draw_rounded_box(pdf, start_x+40, y+5, 120, 30, r=5, bg_color=(255, 255, 255), text=f"~ Canva: Dotted number {target_num} ~")
            pdf.ln(45)

    # 3. COUNTING OBJECTS
    elif "counting" in clean_sub:
        pdf.cell(0, 10, f" Directions: Count the objects. Color the circle with the correct number.", ln=True)
        pdf.ln(5)
        seen_choices = set() 
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            actual_count = target_num 
            for _ in range(50):
                choices = [actual_count]
                while len(choices) < 3:
                    wrong = random.randint(1, 10)
                    if wrong not in choices: choices.append(wrong)
                random.shuffle(choices) 
                sig = tuple(choices)
                if sig not in seen_choices:
                    seen_choices.add(sig)
                    break
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (172 / 2)
            draw_rounded_box(pdf, start_x, y+5, 80, 35, r=5, bg_color=(255, 255, 255), text=f"~ Add {actual_count} items ~")
            
            draw_solid_circle(pdf, start_x+90, y+11.5, 22, str(choices[0]), font_size=28, is_path=(choices[0]==target_num))
            draw_solid_circle(pdf, start_x+118, y+11.5, 22, str(choices[1]), font_size=28, is_path=(choices[1]==target_num))
            draw_solid_circle(pdf, start_x+146, y+11.5, 22, str(choices[2]), font_size=28, is_path=(choices[2]==target_num))
            pdf.ln(50)

    # 4. COUNT AND MATCH
    elif "match" in clean_sub:
        pdf.cell(0, 10, f" Directions: Draw a line to match the groups of {target_num}.", ln=True)
        pdf.ln(5)
        
        draw_solid_circle(pdf, center_x - 22.5, 120, 45, str(target_num), font_size=50)
        wrong_count = random.choice([x for x in range(1, 11) if x != target_num])
        boxes = [
            f"~ {target_num} dots ~",
            f"~ {target_num} fingers ~",
            f"~ {target_num} animals ~",
            f"~ {wrong_count} items ~" 
        ]
        random.shuffle(boxes) 
        
        draw_rounded_box(pdf, 25, 80, 50, 35, r=6, bg_color=theme_colors["box"], text=boxes[0])
        draw_rounded_box(pdf, 140, 80, 50, 35, r=6, bg_color=theme_colors["box"], text=boxes[1])
        draw_rounded_box(pdf, 25, 160, 50, 35, r=6, bg_color=theme_colors["box"], text=boxes[2]) 
        draw_rounded_box(pdf, 140, 160, 50, 35, r=6, bg_color=theme_colors["box"], text=boxes[3])

    # 5. MORE OR LESS
    elif "more" in clean_sub:
        pdf.cell(0, 10, f" Directions: Color the box that has exactly {target_num} items.", ln=True)
        pdf.ln(5)
        seen_options = set()
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            for _ in range(50):
                wrong = random.choice([x for x in range(1, 11) if x != target_num])
                options = [target_num, wrong]
                random.shuffle(options) 
                sig = tuple(options)
                if sig not in seen_options:
                    seen_options.add(sig)
                    break
            
            txt_left = f"~ {options[0]} items ~" + (" (CORRECT)" if (pdf.is_key and options[0] == target_num) else "")
            txt_right = f"~ {options[1]} items ~" + (" (CORRECT)" if (pdf.is_key and options[1] == target_num) else "")
            
            draw_rounded_box(pdf, 15, y, 185, 55, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (150 / 2)
            draw_rounded_box(pdf, start_x, y+5, 60, 45, r=5, bg_color=(255, 255, 255), text=txt_left)
            
            pdf.set_font("ComicNeue", "", 20)
            pdf.set_text_color(*theme_colors["secondary"])
            tw = pdf.get_string_width("VS")
            pdf.text(center_x - (tw/2), y + 33, "VS") 
            draw_rounded_box(pdf, start_x+90, y+5, 60, 45, r=5, bg_color=(255, 255, 255), text=txt_right)
            pdf.ln(60)

    # 6. COLOR BY NUMBER
    elif "color" in clean_sub:
        pdf.cell(0, 10, f" Directions: Find and color all the number {target_num}s.", ln=True)
        pdf.ln(5)
        y = pdf.get_y()
        
        all_colors = ["Red", "Blue", "Yellow", "Green", "Pink", "Purple", "Orange"]
        chosen_color = random.choice(all_colors)
        
        code_text = f"Color {target_num} = {chosen_color}"
        pdf.set_font("ComicNeue", "", 18)
        tw = pdf.get_string_width(code_text)
        code_w = tw + 20 
        
        draw_rounded_box(pdf, center_x - (code_w/2), y, code_w, 20, r=5, bg_color=theme_colors["box"])
        pdf.set_text_color(100, 100, 100)
        pdf.text(center_x - (tw/2), y + 14, code_text)
            
        pdf.ln(30)
        draw_rounded_box(pdf, 15, pdf.get_y(), 185, 150, r=8, bg_color=theme_colors["box"], text=f"~ Canva: Add a picture with hidden {target_num}s to color ~", font_size=14)

    # 7. MISSING NUMBERS
    elif "missing" in clean_sub:
        pdf.cell(0, 10, f" Directions: Fill in the missing numbers. Can you find where {target_num} goes?", ln=True)
        pdf.ln(10)
        seen_sequences = set() 
        for i in range(num_q):
            if pdf.get_y() > 240: pdf.add_page()
            y = pdf.get_y()
            
            for _ in range(50):
                start_val = max(1, target_num - random.randint(0, 4))
                seq = [start_val + k for k in range(5)]
                hidden = [seq.index(target_num)] if target_num in seq else [2]
                other_hidden = random.choice([x for x in range(5) if x not in hidden])
                hidden.append(other_hidden)
                
                sig = (start_val, frozenset(hidden))
                if sig not in seen_sequences:
                    seen_sequences.add(sig)
                    break
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (172 / 2)
            
            for j in range(5):
                x = start_x + (j * 36)
                if j in hidden:
                    val = str(seq[j]) if pdf.is_key else "?"
                    draw_circle_placeholder(pdf, x, y+8.5, 28, val)
                else:
                    draw_solid_circle(pdf, x, y+8.5, 28, str(seq[j]), font_size=28)
            pdf.ln(50)

    # 8. NUMBER MAZES (แก้ไข: สุ่มตัวเลขหลอกหลากหลาย 100%)
    elif "maze" in clean_sub:
        pdf.cell(0, 10, f" Directions: Color the number {target_num} to find the way out of the maze!", ln=True)
        pdf.ln(5)
        
        start_x = center_x - (125 / 2)
        start_y = pdf.get_y() + 10
        box_s = 25
        
        pdf.set_font("ComicNeue", "", 16)
        pdf.set_text_color(*theme_colors["primary"])
        tw_start = pdf.get_string_width("START")
        pdf.text(start_x + (box_s/2) - (tw_start/2), start_y - 5, "START")
        
        # --- อัลกอริทึมสร้างเส้นทางที่ถูกต้อง (Path Generator) ---
        path = set()
        r, c = 0, 0
        path.add((r, c))
        while r < 4 or c < 4:
            if r == 4:
                c += 1
            elif c == 4:
                r += 1
            else:
                if random.choice([True, False]): r += 1
                else: c += 1
            path.add((r, c))
            
        # สร้าง List ตัวเลือกหลอกที่ไม่ใช่คำตอบ (1-10)
        wrong_options = [x for x in range(1, 11) if x != target_num]
            
        for row in range(5):
            for col in range(5):
                # ตรวจสอบว่าช่องนี้อยู่ในเส้นทางที่ถูกต้องหรือไม่
                is_correct_path = (row, col) in path
                
                if is_correct_path:
                    val = str(target_num)
                else:
                    # สุ่มหลอกด้วยเลขเป้าหมายนิดหน่อย แต่ส่วนใหญ่เป็นเลขหลอก "ที่สุ่มมาหลากหลาย" 
                    if random.random() > 0.85:
                        val = str(target_num)
                    else:
                        val = str(random.choice(wrong_options))
                    
                draw_solid_circle(pdf, start_x + (col*box_s) + 2, start_y + (row*box_s) + 2, 20, val, font_size=22, is_path=is_correct_path)
                
        tw_finish = pdf.get_string_width("FINISH")
        pdf.text(start_x + (4*box_s) + (box_s/2) - (tw_finish/2), start_y + (5*box_s) + 5, "FINISH")




    # ==========================================
    # โซนแกนที่ 2 : OPERATIONS (Pre-K เน้นระบายสี)
    # ==========================================

    # 1. COLOR TO ADD (ระบายสี 2 กลุ่มรวมกันให้ได้ผลลัพธ์)
    elif "color to add" in clean_sub:
        pdf.cell(0, 10, f" Directions: Color the pictures to add them together.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            n1 = random.randint(1, target_num - 1) if target_num > 1 else 1
            n2 = target_num - n1 if target_num > 1 else 0
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (160 / 2)
            
            draw_rounded_box(pdf, start_x, y+5, 50, 35, r=5, bg_color=(255,255,255), text=f"~ Color {n1} ~")
            pdf.set_font("ComicNeue", "", 24)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(start_x + 56, y + 27, "+")
            
            draw_rounded_box(pdf, start_x + 65, y+5, 50, 35, r=5, bg_color=(255,255,255), text=f"~ Color {n2} ~")
            pdf.text(start_x + 121, y + 27, "=")
            
            draw_rounded_box(pdf, start_x + 130, y+5, 30, 35, r=5, bg_color=(255,255,255), text=str(target_num) if pdf.is_key else "?", font_size=28)
            pdf.ln(50)

    # 2. COUNT AND COLOR TOTAL (นับภาพรวมกันแล้วระบายสีวงกลมคำตอบ)
    elif "count and color total" in clean_sub:
        pdf.cell(0, 10, f" Directions: Count all the items and color the correct circle.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            n1 = random.randint(1, target_num - 1) if target_num > 1 else 1
            n2 = target_num - n1 if target_num > 1 else 0
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (170 / 2)
            
            draw_rounded_box(pdf, start_x, y+5, 45, 35, r=5, bg_color=(255,255,255), text=f"~ {n1} items ~")
            pdf.set_font("ComicNeue", "", 24)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(start_x + 48, y + 27, "+")
            
            draw_rounded_box(pdf, start_x + 55, y+5, 45, 35, r=5, bg_color=(255,255,255), text=f"~ {n2} items ~")
            pdf.text(start_x + 103, y + 27, "=")
            
            choices = [target_num]
            while len(choices) < 3:
                wrong = random.randint(1, 10)
                if wrong not in choices: choices.append(wrong)
            random.shuffle(choices)
            
            draw_solid_circle(pdf, start_x + 112, y+11.5, 18, str(choices[0]), font_size=20, is_path=(choices[0]==target_num))
            draw_solid_circle(pdf, start_x + 132, y+11.5, 18, str(choices[1]), font_size=20, is_path=(choices[1]==target_num))
            draw_solid_circle(pdf, start_x + 152, y+11.5, 18, str(choices[2]), font_size=20, is_path=(choices[2]==target_num))
            pdf.ln(50)

    # 3. TAKE AWAY AND COLOR (ฝึกการลบ ระบายสีกากบาทของที่เอาออก)
    elif "take away and color" in clean_sub:
        pdf.cell(0, 10, f" Directions: Cross out the items to take away and color the rest.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            take = random.randint(1, target_num) if target_num > 1 else 1
            left = target_num - take
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (160 / 2)
            
            draw_rounded_box(pdf, start_x, y+5, 90, 35, r=5, bg_color=(255,255,255), text=f"~ Total {target_num}. Cross out {take} ~", font_size=12)
            
            pdf.set_font("ComicNeue", "", 24)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(start_x + 95, y + 27, "->")
            
            ans_txt = f"Left: {left}" if pdf.is_key else "? Left"
            draw_rounded_box(pdf, start_x + 110, y+5, 50, 35, r=5, bg_color=(255,255,255), text=ans_txt, font_size=16)
            pdf.ln(50)

    # 4. COLOR THE ADDITION PATH (ระบายสีทางเดินผลบวกที่ได้เท่ากับ Target)
    elif "addition path" in clean_sub:
        pdf.cell(0, 10, f" Directions: Color the bubbles that add up to {target_num} to find the path!", ln=True)
        pdf.ln(5)
        
        start_x = center_x - (125 / 2)
        start_y = pdf.get_y() + 10
        box_s = 25
        
        pdf.set_font("ComicNeue", "", 16)
        pdf.set_text_color(*theme_colors["primary"])
        tw_start = pdf.get_string_width("START")
        pdf.text(start_x + (box_s/2) - (tw_start/2), start_y - 5, "START")
        
        path = set()
        r, c = 0, 0
        path.add((r, c))
        while r < 4 or c < 4:
            if r == 4: c += 1
            elif c == 4: r += 1
            else:
                if random.choice([True, False]): r += 1
                else: c += 1
            path.add((r, c))
            
        for row in range(5):
            for col in range(5):
                is_correct = (row, col) in path
                if is_correct:
                    n1 = random.randint(0, target_num)
                    n2 = target_num - n1
                else:
                    wrong_ans = random.choice([x for x in range(1, 11) if x != target_num])
                    n1 = random.randint(0, wrong_ans)
                    n2 = wrong_ans - n1
                
                text_eq = f"{n1}+{n2}"
                draw_solid_circle(pdf, start_x + (col*box_s) + 2, start_y + (row*box_s) + 2, 20, text_eq, font_size=14, is_path=is_correct)
                
        tw_finish = pdf.get_string_width("FINISH")
        pdf.text(start_x + (4*box_s) + (box_s/2) - (tw_finish/2), start_y + (5*box_s) + 5, "FINISH")

    # 5. COLOR TO MAKE TARGET (ระบายสีส่วนที่ขาดให้ครบ Target)
    elif "make target" in clean_sub:
        pdf.cell(0, 10, f" Directions: Color more items to make exactly {target_num}.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            have = random.randint(1, target_num - 1) if target_num > 1 else 0
            need = target_num - have
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (160 / 2)
            
            draw_rounded_box(pdf, start_x, y+5, 70, 35, r=5, bg_color=(255,255,255), text=f"~ Have {have}. Color {need} more ~", font_size=12)
            
            pdf.set_font("ComicNeue", "", 24)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(start_x + 75, y + 27, "=")
            
            draw_rounded_box(pdf, start_x + 90, y+5, 70, 35, r=5, bg_color=(255,255,255), text=f"~ Total: {target_num} ~", font_size=16)
            pdf.ln(50)

    # 6. DRAW AND COLOR MORE (วาดและระบายสีเพิ่ม)
    elif "draw and color" in clean_sub:
        pdf.cell(0, 10, f" Directions: Draw and color more items to reach {target_num}.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            have = random.randint(1, target_num - 1) if target_num > 1 else 0
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (160 / 2)
            
            draw_rounded_box(pdf, start_x, y+5, 160, 35, r=5, bg_color=(255,255,255), text=f"~ Start with {have}. Draw more to make {target_num} ~", font_size=12)
            pdf.ln(50)

    # 7. CROSS OUT AND COLOR (ลบรูปแบบกากบาทแล้วระบายผลลัพธ์)
    elif "cross out" in clean_sub:
        pdf.cell(0, 10, f" Directions: Cross out the number given, then color the rest.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            take = random.randint(1, target_num) if target_num > 1 else 1
            left = target_num - take
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (160 / 2)
            
            draw_rounded_box(pdf, start_x, y+5, 60, 35, r=5, bg_color=(255,255,255), text=f"~ Total {target_num} ~")
            
            pdf.set_font("ComicNeue", "", 24)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(start_x + 63, y + 27, "-")
            
            draw_rounded_box(pdf, start_x + 70, y+5, 40, 35, r=5, bg_color=(255,255,255), text=str(take), font_size=24)
            
            pdf.text(start_x + 113, y + 27, "=")
            
            ans_txt = str(left) if pdf.is_key else "?"
            draw_rounded_box(pdf, start_x + 120, y+5, 40, 35, r=5, bg_color=(255,255,255), text=ans_txt, font_size=28)
            pdf.ln(50)

    # 8. COLOR THE CORRECT SUM (หาผลรวมแล้วระบายสีกล่องที่ตัวเลขถูกต้อง)
    elif "correct sum" in clean_sub:
        pdf.cell(0, 10, f" Directions: Add the pictures and color the box with the correct number.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            n1 = random.randint(1, target_num - 1) if target_num > 1 else 1
            n2 = target_num - n1 if target_num > 1 else 0
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (170 / 2)
            
            draw_rounded_box(pdf, start_x, y+5, 70, 35, r=5, bg_color=(255,255,255), text=f"~ {n1} items + {n2} items ~", font_size=12)
            
            pdf.set_font("ComicNeue", "", 24)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(start_x + 75, y + 27, "=")
            
            choices = [target_num]
            while len(choices) < 3:
                wrong = random.randint(1, 10)
                if wrong not in choices: choices.append(wrong)
            random.shuffle(choices)
            
            bg1 = theme_colors["secondary"] if (pdf.is_key and choices[0]==target_num) else (255,255,255)
            bg2 = theme_colors["secondary"] if (pdf.is_key and choices[1]==target_num) else (255,255,255)
            bg3 = theme_colors["secondary"] if (pdf.is_key and choices[2]==target_num) else (255,255,255)
            
            draw_rounded_box(pdf, start_x + 90, y+10, 22, 25, r=4, bg_color=bg1, text=str(choices[0]), font_size=20)
            draw_rounded_box(pdf, start_x + 118, y+10, 22, 25, r=4, bg_color=bg2, text=str(choices[1]), font_size=20)
            draw_rounded_box(pdf, start_x + 146, y+10, 22, 25, r=4, bg_color=bg3, text=str(choices[2]), font_size=20)
            pdf.ln(50)
    

    return bytes(pdf.output(dest='S'))

# ==========================================
# 5. พรีวิวด้วย PyMuPDF 
# ==========================================
def display_pdf_preview(pdf_bytes):
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc.load_page(0) 
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        st.markdown(
            """
            <style>
            .premium-paper { box-shadow: 0 15px 35px rgba(0,0,0,0.1); border-radius: 12px; background: white; padding: 10px; border: 1px solid #f0f0f0; }
            </style>
            """, unsafe_allow_html=True
        )
        st.markdown("<div class='premium-paper'>", unsafe_allow_html=True)
        st.image(img, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        doc.close()
    except Exception as e:
        st.error(f"⚠️ พรีวิวขัดข้อง: {e}")

# ==========================================
# 6. Streamlit UI
# ==========================================
st.set_page_config(page_title="Pre-K Focus Number Gen", layout="wide", page_icon="🎨")

st.markdown("""
<style>
    .main-header { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); padding: 2rem; border-radius: 15px; color: #2c3e50; text-align: center; margin-bottom: 2rem; }
    div.stButton > button { background-color: #ff7494; color: white; border: none; border-radius: 8px; font-weight: bold; }
</style>
<div class="main-header">
    <h1 style="margin:0; font-weight:800;">🎨 Pre-K Focus Number Generator</h1>
    <p style="margin:5px 0 0 0; font-size:1.1rem;">(เวอร์ชันอัปเกรด: เขาวงกตตัวลวงหลากหลาย + เลย์เอาต์โค้งมนปลอดภัย 100%)</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("🎨 ตกแต่งใบงาน (Customize)")
    
    shop_name = st.text_input("🏪 ชื่อร้าน (Copyright):", value="Kindergarten Learning Press")
    st.markdown("---")
    
    main_topic = "1. Number Sense (การรู้ค่าตัวเลข)" 
    sub_topic = st.selectbox("🎯 1. เลือกกิจกรรม (Activity):", PRE_K_CURRICULUM[main_topic])
    
    theme_choice = st.selectbox("🖌️ 2. โทนสี (Color Palette):", list(THEME_COLORS.keys()))
    selected_colors = THEME_COLORS[theme_choice]
    
    st.markdown("---")
    target_num = st.selectbox("🎯 3. เลือกตัวเลขเป้าหมาย (Focus Number):", list(range(1, 11)))
    
    num_q = st.slider("📝 4. จำนวนข้อต่อหน้า:", min_value=2, max_value=5, value=3)
    
    st.markdown("---")
    generate_btn = st.button("🚀 สร้างโครงร่าง (Generate PDF)", use_container_width=True)

if generate_btn:
    current_session_seed = random.randint(1, 9999999)
    
    with st.spinner(f"กำลังสร้างใบงานแบบ Dynamic โฟกัสเลข {target_num}..."):
        ws_bytes = generate_worksheet(sub_topic, selected_colors, num_q, shop_name, target_num, session_seed=current_session_seed, is_key=False)
        ans_bytes = generate_worksheet(sub_topic, selected_colors, num_q, shop_name, target_num, session_seed=current_session_seed, is_key=True)

        col1, col2 = st.columns([1.5, 1])
        with col1:
            display_pdf_preview(ws_bytes)
            
        with col2:
            st.subheader(f"📥 ดาวน์โหลดไฟล์ (Number {target_num})")
            st.success(f"✅ สร้างใบงานสำเร็จ! เลย์เอาต์โค้งมนปลอดภัย 100%")
            
            file_title = sub_topic.split('. ')[1].replace(' ', '_')
            
            st.download_button(
                label=f"📄 โหลดโครงร่าง (Worksheet - Num {target_num})",
                data=ws_bytes,
                file_name=f"PreK_{file_title}_Number_{target_num}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.download_button(
                label=f"🔑 โหลดเฉลย (Answer Key - Num {target_num})",
                data=ans_bytes,
                file_name=f"PreK_{file_title}_Number_{target_num}_KEY.pdf",
                mime="application/pdf",
                use_container_width=True
            )
else:
    st.info("👈 กรุณาเลือก **ตัวเลขที่ต้องการ** แล้วกดปุ่มสร้างใบงานได้เลยครับ (ไม่มีปัญหากรอบเหลี่ยม หรือการจัดหน้าเบี้ยวแน่นอนครับ!)")
