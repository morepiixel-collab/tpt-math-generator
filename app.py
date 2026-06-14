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
    ],
    "3. Geometry & Patterns (รูปร่างและแบบรูป)": [
        "1. Trace the Shapes",
        "2. Find the Hidden Shapes",
        "3. Match to Real Objects",
        "4. Big vs Small",
        "5. Tall vs Short",
        "6. Odd One Out",
        "7. Finish the Pattern",
        "8. Where is it?"
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
        
        # แก้ไขจุดที่ 1: ดักจับคำของแกนที่ 3 เพื่อซ่อน : NUMBER
        hide_keywords = ["color by number", "shape", "match to real", "big", "tall", "odd", "pattern", "where"]
        if any(kw in clean_topic.lower() for kw in hide_keywords):
            title = f"{clean_topic}" + (" (KEY)" if self.is_key else "")
        else:
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

    # ==========================================
    # โซนแกนที่ 1 : NUMBER SENSE
    # ==========================================
    # แก้ไขจุดที่ 2: เปลี่ยนคีย์เวิร์ดให้เจาะจง ป้องกันการชนกับแกนที่ 3
    if "find the number" in clean_sub:
        pdf.cell(0, 10, f" Directions: Find and color the number {target_num} in the picture below.", ln=True)
        pdf.ln(5)
        pdf.set_font("ComicNeue", "", 20)
        pdf.set_text_color(*theme_colors["primary"])
        pdf.cell(0, 10, f"Target: {target_num}", ln=True, align="C")
        draw_rounded_box(pdf, 15, 85, 185, 160, r=8, bg_color=theme_colors["box"], text=f"~ Canva: Add a large scene. Scatter number {target_num} everywhere! ~", font_size=14)

    elif "trace the numbers" in clean_sub:
        pdf.cell(0, 10, f" Directions: Color the pictures. Then trace and write the number {target_num}.", ln=True)
        pdf.ln(5)
        for i in range(num_q): 
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            draw_rounded_box(pdf, 20, y+5, 110, 35, r=5, bg_color=(255,255,255), text=f"~ Canva: {target_num} Items to color ~", font_size=11)
            draw_rounded_box(pdf, 135, y+5, 60, 35, r=5, bg_color=(255,255,255), text=f"~ Canva: Dotted {target_num} ~", font_size=11)
            pdf.ln(55)

    elif "counting objects" in clean_sub or ("counting" in clean_sub and "objects" in clean_sub):
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

    elif "count and match" in clean_sub:
        pdf.cell(0, 10, f" Directions: Draw a line to match the groups of {target_num}.", ln=True)
        pdf.ln(5)
        
        # วงกลมตัวเลขเป้าหมายตรงกลาง
        draw_solid_circle(pdf, center_x - 22.5, 120, 45, str(target_num), font_size=50)
        
        wrong_count = random.choice([x for x in range(1, 11) if x != target_num])
        boxes = [
            f"~ {target_num} dots ~",
            f"~ {target_num} fingers ~",
            f"~ {target_num} animals ~",
            f"~ {wrong_count} items ~" 
        ]
        random.shuffle(boxes) 
        
        # แก้ไขพิกัด Y ของกล่องแถวบน (เปลี่ยนจาก 60 เป็น 70 เพื่อไม่ให้ทับโจทย์)
        draw_rounded_box(pdf, 18, 70, 65, 50, r=6, bg_color=theme_colors["box"], text=boxes[0])
        draw_rounded_box(pdf, 133, 70, 65, 50, r=6, bg_color=theme_colors["box"], text=boxes[1])
        
        # กล่องแถวเล่างอยู่ที่ตำแหน่ง 175 เหมือนเดิม
        draw_rounded_box(pdf, 18, 175, 65, 50, r=6, bg_color=theme_colors["box"], text=boxes[2]) 
        draw_rounded_box(pdf, 133, 175, 65, 50, r=6, bg_color=theme_colors["box"], text=boxes[3])

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

    elif "color by number" in clean_sub:
        pdf.cell(0, 10, f" Directions: Look at the color key. Color the picture using the right colors!", ln=True)
        pdf.ln(5)
        y = pdf.get_y()
        
        wrong_nums = random.sample([x for x in range(1, 11) if x != target_num], 3)
        key_nums = [target_num] + wrong_nums
        random.shuffle(key_nums)
        
        color_names = ["RED", "BLUE", "YELLOW", "GREEN"]
        
        draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
        
        pdf.set_font("ComicNeue", "", 16)
        pdf.set_text_color(*theme_colors["primary"])
        tw = pdf.get_string_width("C O L O R   K E Y")
        pdf.text(center_x - (tw/2), y + 10, "C O L O R   K E Y")
        
        start_x = 22
        for idx, n in enumerate(key_nums):
            cx = start_x + (idx * 42)
            draw_solid_circle(pdf, cx, y + 16, 16, str(n), font_size=18)
            draw_rounded_box(pdf, cx + 18, y + 18, 22, 12, r=3, bg_color=(255,255,255), text=color_names[idx], font_size=9)
        
        pdf.ln(55)
        
        nums_str = ", ".join(map(str, key_nums))
        placeholder_text = f"~ Canva: Add a 'Color by Number' graphic using numbers {nums_str} ~"
        draw_rounded_box(pdf, 15, pdf.get_y(), 185, 115, r=8, bg_color=theme_colors["box"], text=placeholder_text, font_size=12)

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
            
        wrong_options = [x for x in range(1, 11) if x != target_num]
            
        for row in range(5):
            for col in range(5):
                is_correct_path = (row, col) in path
                
                if is_correct_path:
                    val = str(target_num)
                else:
                    if random.random() > 0.85:
                        val = str(target_num)
                    else:
                        val = str(random.choice(wrong_options))
                    
                draw_solid_circle(pdf, start_x + (col*box_s) + 2, start_y + (row*box_s) + 2, 20, val, font_size=22, is_path=is_correct_path)
                
        tw_finish = pdf.get_string_width("FINISH")
        pdf.text(start_x + (4*box_s) + (box_s/2) - (tw_finish/2), start_y + (5*box_s) + 5, "FINISH")


    # ==========================================
    # โซนแกนที่ 2 : OPERATIONS
    # ==========================================
    elif "color to add" in clean_sub:
        pdf.cell(0, 10, f" Directions: Color the first group, then color the second group. Add them together!", ln=True)
        pdf.ln(5)
        
        # เพิ่มลิสต์สีสำหรับสุ่ม เพื่อให้ใบงานดูน่าสนุกขึ้น
        color_choices = ["red", "blue", "yellow", "green", "pink", "purple", "orange"]
        
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            n1 = random.randint(1, target_num - 1) if target_num > 1 else 1
            n2 = target_num - n1 if target_num > 1 else 0
            
            # สุ่มดึงสีมา 2 สีที่ไม่ซ้ำกันในแต่ละข้อ
            c1, c2 = random.sample(color_choices, 2)
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (160 / 2)
            
            # --- กล่องที่ 1 ---
            draw_rounded_box(pdf, start_x, y+5, 50, 35, r=5, bg_color=(255,255,255), text=f"~ Canva: {n1} outlines ~", font_size=11)
            
            # วางข้อความบอกสี ไว้ด้านล่าง "ข้างใน" กล่องขาว
            pdf.set_font("ComicNeue", "", 10)
            pdf.set_text_color(130, 130, 130)
            txt1 = f"Color {n1} {c1}."
            w1 = pdf.get_string_width(txt1)
            pdf.text(start_x + (50/2) - (w1/2), y + 36, txt1)
            
            # เครื่องหมายบวก
            pdf.set_font("ComicNeue", "", 28)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(start_x + 55, y + 28, "+")
            
            # --- กล่องที่ 2 ---
            draw_rounded_box(pdf, start_x + 65, y+5, 50, 35, r=5, bg_color=(255,255,255), text=f"~ Canva: {n2} outlines ~", font_size=11)
            
            # วางข้อความบอกสี ไว้ด้านล่าง "ข้างใน" กล่องขาว
            pdf.set_font("ComicNeue", "", 10)
            pdf.set_text_color(130, 130, 130)
            txt2 = f"Color {n2} {c2}."
            w2 = pdf.get_string_width(txt2)
            pdf.text(start_x + 65 + (50/2) - (w2/2), y + 36, txt2)
            
            # เครื่องหมายเท่ากับ
            pdf.set_font("ComicNeue", "", 28)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(start_x + 120, y + 28, "=")
            
            # --- กล่องคำตอบ ---
            ans_val = str(target_num) if pdf.is_key else ""
            draw_rounded_box(pdf, start_x + 130, y+5, 30, 35, r=5, bg_color=(255,255,255), text=ans_val, font_size=28)
            
            pdf.ln(55)

    elif "count and color total" in clean_sub:
        pdf.cell(0, 10, f" Directions: Count all the pictures together. Color the circle with the correct total.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            n1 = random.randint(1, target_num - 1) if target_num > 1 else 1
            n2 = target_num - n1 if target_num > 1 else 0
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            
            start_x = center_x - (170 / 2)
            
            draw_rounded_box(pdf, start_x, y+5, 40, 35, r=5, bg_color=(255,255,255), text=f"~ Canva: {n1} items ~", font_size=11)
            
            pdf.set_font("ComicNeue", "", 28)
            pdf.set_text_color(*theme_colors["primary"])
            w_plus = pdf.get_string_width("+")
            pdf.text(start_x + 46 - (w_plus/2), y + 25, "+")
            
            draw_rounded_box(pdf, start_x + 52, y+5, 40, 35, r=5, bg_color=(255,255,255), text=f"~ Canva: {n2} items ~", font_size=11)
            
            pdf.set_font("ComicNeue", "", 28)
            pdf.set_text_color(*theme_colors["primary"])
            w_eq = pdf.get_string_width("=")
            pdf.text(start_x + 98 - (w_eq/2), y + 25, "=")
            
            choices = [target_num]
            while len(choices) < 3:
                wrong = random.randint(1, 10)
                if wrong not in choices: choices.append(wrong)
            random.shuffle(choices)
            
            draw_solid_circle(pdf, start_x + 104, y+11.5, 18, str(choices[0]), font_size=20, is_path=(choices[0]==target_num))
            draw_solid_circle(pdf, start_x + 128, y+11.5, 18, str(choices[1]), font_size=20, is_path=(choices[1]==target_num))
            draw_solid_circle(pdf, start_x + 152, y+11.5, 18, str(choices[2]), font_size=20, is_path=(choices[2]==target_num))
            
            pdf.ln(55)
            
    elif "take away and color" in clean_sub:
        pdf.cell(0, 10, f" Directions: Look at the pictures. Cross out the number given, then color the rest.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            total = target_num if target_num > 1 else 2
            take = random.randint(1, total - 1)
            left = total - take
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (160 / 2)
            
            draw_rounded_box(pdf, start_x, y+5, 90, 35, r=5, bg_color=(255,255,255), text=f"~ Canva: Add {total} items here ~", font_size=11)
            
            pdf.set_font("ComicNeue", "", 18)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(start_x + 95, y + 20, f"Take away {take}")
            pdf.text(start_x + 95, y + 32, "How many left?")
            
            ans_txt = str(left) if pdf.is_key else ""
            draw_rounded_box(pdf, start_x + 140, y+5, 30, 35, r=5, bg_color=(255,255,255), text=ans_txt, font_size=24)
            pdf.ln(55)

    elif "addition path" in clean_sub:
        pdf.cell(0, 10, f" Directions: Find the way out! Color the bubbles that add up to {target_num}.", ln=True)
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
                    wrong_ans = random.choice([x for x in range(1, 15) if x != target_num])
                    n1 = random.randint(0, wrong_ans)
                    n2 = wrong_ans - n1
                
                text_eq = f"{n1}+{n2}"
                draw_solid_circle(pdf, start_x + (col*box_s) + 2, start_y + (row*box_s) + 2, 20, text_eq, font_size=12, is_path=is_correct)
                
        tw_finish = pdf.get_string_width("FINISH")
        pdf.text(start_x + (4*box_s) + (box_s/2) - (tw_finish/2), start_y + (5*box_s) + 5, "FINISH")

    elif "make target" in clean_sub:
        pdf.cell(0, 10, f" Directions: We need {target_num} in total. Color more items to make {target_num}.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            have = random.randint(1, target_num - 1) if target_num > 1 else 0
            need = target_num - have
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            
            draw_rounded_box(pdf, 20, y+5, 95, 35, r=5, bg_color=(255,255,255), text=f"~ Canva: Add {target_num} items. Show {have} filled, {need} empty ~", font_size=11)
            
            right_x = 120
            
            pdf.set_font("ComicNeue", "", 18)
            pdf.set_text_color(*theme_colors["primary"])
            w_colored = pdf.get_string_width("I colored ")
            
            pdf.text(right_x, y + 26, "I colored")
            
            box_w = 20
            box_h = 20
            ans_text = str(need) if pdf.is_key else ""
            draw_rounded_box(pdf, right_x + w_colored, y + 12.5, box_w, box_h, r=4, bg_color=(255,255,255), text=ans_text, font_size=18)
            
            pdf.set_font("ComicNeue", "", 18)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(right_x + w_colored + box_w + 4, y + 26, "more.")
            
            pdf.ln(55)

    elif "draw and color" in clean_sub:
        pdf.cell(0, 10, f" Directions: Draw and color more pictures to make exactly {target_num}.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            have = random.randint(1, target_num - 1) if target_num > 1 else 0
            need = target_num - have
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (160 / 2)
            
            draw_rounded_box(pdf, start_x, y+5, 50, 35, r=5, bg_color=(255,255,255), text=f"~ Canva: {have} items ~", font_size=11)
            pdf.set_font("ComicNeue", "", 24)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(start_x + 55, y + 27, "+")
            
            ans_text = f"~ (Key: Draw {need}) ~" if pdf.is_key else f"~ Draw more here ~"
            draw_rounded_box(pdf, start_x + 65, y+5, 50, 35, r=5, bg_color=(255,255,255), text=ans_text, font_size=11)
            
            pdf.text(start_x + 120, y + 27, "=")
            draw_rounded_box(pdf, start_x + 130, y+5, 30, 35, r=5, bg_color=(255,255,255), text=str(target_num), font_size=24)
            pdf.ln(55)

    elif "cross out" in clean_sub:
        pdf.cell(0, 10, f" Directions: Read the problem. Cross out the pictures to match, then write the answer.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            take = random.randint(1, target_num) if target_num > 1 else 1
            left = target_num - take
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (170 / 2)
            
            draw_rounded_box(pdf, start_x, y+5, 60, 35, r=5, bg_color=(255,255,255), text=f"~ Canva: {target_num} items ~", font_size=11)
            
            pdf.set_font("ComicNeue", "", 28)
            pdf.set_text_color(*theme_colors["primary"])
            
            pdf.text(start_x + 75, y + 28, "-")
            pdf.text(start_x + 90, y + 28, str(take))
            pdf.text(start_x + 110, y + 28, "=")
            
            ans_txt = str(left) if pdf.is_key else ""
            draw_rounded_box(pdf, start_x + 130, y+5, 35, 35, r=5, bg_color=(255,255,255), text=ans_txt, font_size=28)
            
            if pdf.is_key:
                pdf.set_font("ComicNeue", "", 12)
                pdf.set_text_color(255, 100, 100)
                pdf.text(start_x + 5, y + 35, f"(Cross out {take})")
            pdf.ln(55)

    elif "correct sum" in clean_sub:
        pdf.cell(0, 10, f" Directions: Add the numbers. Color the box with the correct answer.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            n1 = random.randint(0, target_num)
            n2 = target_num - n1
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (160 / 2)
            
            draw_rounded_box(pdf, start_x, y+5, 60, 35, r=5, bg_color=(255,255,255), text=f" {n1} + {n2} ", font_size=28)
            
            pdf.set_font("ComicNeue", "", 24)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(start_x + 65, y + 27, "=")
            
            choices = [target_num]
            while len(choices) < 3:
                wrong = random.randint(1, 15)
                if wrong not in choices: choices.append(wrong)
            random.shuffle(choices)
            
            bg1 = theme_colors["secondary"] if (pdf.is_key and choices[0]==target_num) else (255,255,255)
            bg2 = theme_colors["secondary"] if (pdf.is_key and choices[1]==target_num) else (255,255,255)
            bg3 = theme_colors["secondary"] if (pdf.is_key and choices[2]==target_num) else (255,255,255)
            
            draw_rounded_box(pdf, start_x + 80, y+10, 22, 25, r=4, bg_color=bg1, text=str(choices[0]), font_size=20)
            draw_rounded_box(pdf, start_x + 108, y+10, 22, 25, r=4, bg_color=bg2, text=str(choices[1]), font_size=20)
            draw_rounded_box(pdf, start_x + 136, y+10, 22, 25, r=4, bg_color=bg3, text=str(choices[2]), font_size=20)
            pdf.ln(55)

# ==========================================
    # โซนแกนที่ 3 : GEOMETRY & PATTERNS
    # ==========================================
    elif "trace the shapes" in clean_sub:
        pdf.cell(0, 10, f" Directions: Trace the shapes and color them.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            draw_rounded_box(pdf, 20, y+5, 175, 35, r=5, bg_color=(255,255,255), text=f"~ Canva: Dashed Shapes for Tracing ~", font_size=12)
            pdf.ln(55)

    elif "hidden shapes" in clean_sub:
        pdf.cell(0, 10, f" Directions: Find and color the hidden shapes in the picture.", ln=True)
        pdf.ln(5)
        draw_rounded_box(pdf, 15, pdf.get_y(), 185, 160, r=8, bg_color=theme_colors["box"], text=f"~ Canva: Big scene with hidden shapes ~", font_size=14)

    elif "match to real objects" in clean_sub:
        pdf.cell(0, 10, f" Directions: Draw a line to match the shape to the real object.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            draw_rounded_box(pdf, 25, y+5, 45, 35, r=5, bg_color=(255,255,255), text=f"~ Basic Shape ~", font_size=10)
            draw_rounded_box(pdf, 145, y+5, 45, 35, r=5, bg_color=(255,255,255), text=f"~ Real Object ~", font_size=10)
            pdf.ln(55)

    elif "big vs small" in clean_sub:
        pdf.cell(0, 10, f" Directions: Color the BIG picture in each box.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            draw_rounded_box(pdf, 15, y, 185, 55, r=8, bg_color=theme_colors["box"])
            start_x = center_x - 70
            draw_rounded_box(pdf, start_x, y+5, 60, 45, r=5, bg_color=(255,255,255), text=f"~ Big Item ~", font_size=11)
            draw_rounded_box(pdf, start_x+80, y+5, 60, 45, r=5, bg_color=(255,255,255), text=f"~ Small Item ~", font_size=11)
            pdf.ln(65)

    elif "tall vs short" in clean_sub:
        pdf.cell(0, 10, f" Directions: Color the TALL picture in each box.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            draw_rounded_box(pdf, 15, y, 185, 60, r=8, bg_color=theme_colors["box"])
            start_x = center_x - 70
            draw_rounded_box(pdf, start_x, y+5, 60, 50, r=5, bg_color=(255,255,255), text=f"~ Tall Item ~", font_size=11)
            draw_rounded_box(pdf, start_x+80, y+5, 60, 50, r=5, bg_color=(255,255,255), text=f"~ Short Item ~", font_size=11)
            pdf.ln(70)

    elif "odd one out" in clean_sub:
        pdf.cell(0, 10, f" Directions: Cross out (X) the picture that is different.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            for j in range(4):
                draw_rounded_box(pdf, 25 + (j*42), y+5, 35, 35, r=5, bg_color=(255,255,255), text=f"~ Item ~", font_size=10)
            pdf.ln(55)

    elif "finish the pattern" in clean_sub:
        pdf.cell(0, 10, f" Directions: Look at the pattern. Draw or color what comes next.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            draw_rounded_box(pdf, 25, y+5, 30, 35, r=5, bg_color=(255,255,255), text="~ A ~", font_size=10)
            draw_rounded_box(pdf, 60, y+5, 30, 35, r=5, bg_color=(255,255,255), text="~ B ~", font_size=10)
            draw_rounded_box(pdf, 95, y+5, 30, 35, r=5, bg_color=(255,255,255), text="~ A ~", font_size=10)
            draw_rounded_box(pdf, 145, y+5, 40, 35, r=5, bg_color=(255,255,255), text="~ ? ~", font_size=14)
            pdf.ln(55)

    elif "where is it" in clean_sub:
        pdf.cell(0, 10, f" Directions: Follow the instructions below.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            draw_rounded_box(pdf, 15, y, 185, 55, r=8, bg_color=theme_colors["box"])
            draw_rounded_box(pdf, 25, y+5, 100, 45, r=5, bg_color=(255,255,255), text=f"~ Canva: Scene with objects ~", font_size=11)
            pdf.set_font("ComicNeue", "", 12)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(135, y + 25, "Color the object")
            pdf.set_font("ComicNeue", "", 14) 
            pdf.text(135, y + 35, "UNDER / ON")
            pdf.ln(65)

    # ส่งคืนไฟล์ PDF ในรูปแบบ bytes
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
        st.image(img, use_container_width=True)
    except Exception as e:
        st.error(f"⚠️ ไม่สามารถแสดงพรีวิวได้: {e}")

# ==========================================
# 6. Streamlit User Interface
# ==========================================
st.set_page_config(page_title="Pre-K Math Generator", layout="wide")

st.title("🖍️ Pre-K Math Worksheet Generator")

with st.sidebar:
    st.header("⚙️ Settings")
    shop_name = st.text_input("Shop Name:", value="Kindergarten Learning Press")
    
    main_topic = st.selectbox("Category:", list(PRE_K_CURRICULUM.keys()))
    sub_topic = st.selectbox("Topic:", PRE_K_CURRICULUM[main_topic])
    
    target_num = st.number_input("Target Number (For Axis 1 & 2):", min_value=1, max_value=20, value=1)
    
    theme_choice = st.selectbox("Color Theme:", list(THEME_COLORS.keys()))
    selected_colors = THEME_COLORS[theme_choice]
    
    num_q = st.slider("Questions per page:", min_value=1, max_value=5, value=3)
    session_seed = st.number_input("Random Seed:", value=42)
    
    st.markdown("---")
    generate_btn = st.button("🚀 Generate Worksheet", use_container_width=True)

if generate_btn:
    with st.spinner("Generating PDF..."):
        # สร้าง PDF หลัก
        pdf_bytes = generate_worksheet(sub_topic, selected_colors, num_q, shop_name, target_num, session_seed, is_key=False)
        # สร้าง PDF เฉลย
        key_bytes = generate_worksheet(sub_topic, selected_colors, num_q, shop_name, target_num, session_seed, is_key=True)
        
        col1, col2 = st.columns([1.5, 1])
        with col1:
            st.subheader("Preview (Page 1)")
            display_pdf_preview(pdf_bytes)
            
        with col2:
            st.subheader("Download")
            clean_name = sub_topic.replace(" ", "_").replace("?", "")
            
            st.download_button(
                label="⬇️ Download Worksheet",
                data=pdf_bytes,
                file_name=f"PreK_{clean_name}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            st.download_button(
                label="🔑 Download Answer Key",
                data=key_bytes,
                file_name=f"PreK_{clean_name}_KEY.pdf",
                mime="application/pdf",
                use_container_width=True
            )
