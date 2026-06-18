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
    ],
    "4. Measurement & Data (การวัดและข้อมูล)": [
        "1. Long or Short?",
        "2. Heavy or Light?",
        "3. Full or Empty?",
        "4. Sort by Color",
        "5. Sort by Category",
        "6. Same and Different",
        "7. Day or Night?",
        "8. Simple Picture Graph"
    ]
}

GRADE_1_CURRICULUM = {
    "1. Grade 1 Math Topics (รวมหัวข้อ ป.1)": [
        "1. Addition Within 20",
        "2. Number Bonds",
        "3. Fact Families",
        "4. Place Value Basics",
        "5. Counting to 120",
        "6. Greater Than / Less Than"
    ]
}

GRADE_2_CURRICULUM = {
    "2. Grade 2 Math Topics (รวมหัวข้อ ป.2)": [
        "1. Place Value (Hundreds, Tens, Ones)",
        "2. 2-Digit Addition & Subtraction",
        "3. Number Sense (Even or Odd)",
        "4. Comparing Numbers (3-Digit)",
        "5. Expanded Form",
        "6. Skip Counting"
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
# 2. คลาสหน้ากระดาษ Premium Border (รองรับถึง Grade 3)
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
            self.add_font("ComicNeue", "", FONT_FILE, uni=True)

    def header(self):
        # 1. วาดกรอบรอบหน้ากระดาษ
        self.set_line_width(2.0)
        self.set_draw_color(*self.colors["primary"])
        self.rect(8, 8, 200, 263)
        
        # 2. ตั้งค่าฟอนต์
        try:
            self.set_font("ComicNeue", "", 12)
        except:
            self.set_font("Arial", "", 12)
        self.set_text_color(*self.colors["primary"])
        
        # 3. พิมพ์บรรทัดแรก: บอกระดับชั้น (รองรับ Grade 1, 2, 3)
        title_upper = self.topic_name.upper()
        if any(kw in title_upper for kw in ["HUNDREDS", "2-DIGIT", "EVEN OR ODD", "3-DIGIT", "EXPANDED", "SKIP COUNTING"]):
            header_title = " G R A D E   2   M A T H "
        elif any(kw in title_upper for kw in ["120", "WITHIN 20", "FACT FAMILIES", "BONDS", "GREATER", "VALUE BASICS"]):
            header_title = " G R A D E   1   M A T H "
        elif any(kw in title_upper for kw in ["FRACTION", "MULTIPLICATION", "DIVISION", "GRADE 3"]): # รองรับ Grade 3 ในอนาคต
            header_title = " G R A D E   3   M A T H "
        else:
            header_title = " P R E - K   M A T H "
            
        self.set_y(12)
        self.cell(0, 8, header_title, ln=True, align="C")
        
        # 4. พิมพ์บรรทัดที่สอง: ชื่อหัวข้อใบงาน
        try:
            self.set_font("ComicNeue", "", 24) 
        except:
            self.set_font("Arial", "B", 24)
            
        clean_topic = self.topic_name.split(". ", 1)[-1].upper()
        
        # --- ตรรกะใหม่: โชว์ NUMBER เฉพาะ Pre-K เท่านั้น ---
        is_prek = not any(grade in header_title for grade in ["GRADE 1", "GRADE 2", "GRADE 3"])
        
        if is_prek and self.target_num:
            display_title = f"{clean_topic} : NUMBER {self.target_num}"
        else:
            display_title = clean_topic
            
        if self.is_key:
            display_title += " (KEY)"
            
        self.cell(0, 10, display_title, ln=True, align="C")
        self.ln(6)
        
        # 5. วาดกล่องใส่ชื่อ (Name / Date)
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.rect(11, 38, 194, 12, style='DF')
        
        try:
            self.set_font("ComicNeue", "", 14)
        except:
            self.set_font("Arial", "", 14)
            
        self.set_text_color(100, 100, 100)
        self.set_y(41)
        self.cell(10, 5, "", ln=0)
        self.cell(90, 5, "Name: ___________________________", ln=0, align="L")
        self.cell(80, 5, "Date: _______________", ln=1, align="R")
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        try:
            self.set_font("ComicNeue", "", 10)
        except:
            self.set_font("Arial", "", 10)
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
        
        # ขยายความสูงของกล่อง Color Key ให้ใหญ่ขึ้นนิดหน่อย (เป็น 50) เพื่อไม่ให้แออัด
        draw_rounded_box(pdf, 15, y, 185, 50, r=8, bg_color=theme_colors["box"])
        
        pdf.set_font("ComicNeue", "", 16)
        pdf.set_text_color(*theme_colors["primary"])
        tw = pdf.get_string_width("C O L O R   K E Y")
        pdf.text(center_x - (tw/2), y + 8, "C O L O R   K E Y")
        
        # จัดพิกัดใหม่ให้อยู่กึ่งกลาง และวางกล่องบอกสีไว้ "ใต้" วงกลม
        for idx, n in enumerate(key_nums):
            # คำนวณจุดกึ่งกลางของแต่ละชุดให้กระจายเท่าๆ กัน (x = 40, 85, 130, 175)
            center_item_x = 40 + (idx * 45) 
            
            # 1. วาดวงกลมตัวเลขด้านบน
            d = 18
            draw_solid_circle(pdf, center_item_x - (d/2), y + 13, d, str(n), font_size=20)
            
            # 2. วาดกล่องบอกสีด้านล่างวงกลม
            box_w = 26
            box_h = 12
            draw_rounded_box(pdf, center_item_x - (box_w/2), y + 34, box_w, box_h, r=3, bg_color=(255,255,255), text=color_names[idx], font_size=9)
        
        pdf.ln(60) # เว้นระยะบรรทัดเพิ่มชดเชยกล่องที่สูงขึ้น
        
        nums_str = ", ".join(map(str, key_nums))
        placeholder_text = f"~ Canva: Add a 'Color by Number' graphic using numbers {nums_str} ~"
        draw_rounded_box(pdf, 15, pdf.get_y(), 185, 110, r=8, bg_color=theme_colors["box"], text=placeholder_text, font_size=12)

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
                
                # กำหนดให้ซ่อนแค่เลขเป้าหมาย (target_num) ตัวเดียวเท่านั้น
                hidden = [seq.index(target_num)] if target_num in seq else [2]
                
                # ลบบรรทัด other_hidden ออก เพื่อไม่ให้มันสุ่มซ่อนเลขตัวอื่นเพิ่ม
                
                sig = (start_val, frozenset(hidden))
                if sig not in seen_sequences:
                    seen_sequences.add(sig)
                    break
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            start_x = center_x - (172 / 2)
            
            for j in range(5):
                x = start_x + (j * 36)
                if j in hidden:
                    # ถ้าเป็นหน้าเฉลยจะแสดงตัวเลข แต่ถ้าไม่ใช่จะแสดง "?"
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
        # ปรับโจทย์ใหม่ให้เพิ่มคำสั่งระบายสี (Match and color)
        pdf.cell(0, 10, f" Directions: Draw a line to match the shape to the real object. Then color them!", ln=True)
        pdf.ln(5)
        
        # คำนวณความสูงของกล่องใหญ่ตามจำนวนข้อ (เพิ่มระยะเผื่อกล่องขาวที่ขยายขึ้น)
        total_h = (num_q * 52) + 10
        if pdf.get_y() + total_h > 250: pdf.add_page()
        start_y = pdf.get_y()
        
        # วาดกล่องพื้นหลังสีชมพูใหญ่กรอบเดียว
        draw_rounded_box(pdf, 15, start_y, 185, total_h, r=8, bg_color=theme_colors["box"])
        
        for i in range(num_q):
            y = start_y + 6 + (i * 52)
            
            # กล่องด้านซ้าย (ขยายขนาดเป็น w=50, h=42 เผื่อพื้นที่ระบายสี)
            draw_rounded_box(pdf, 24, y, 50, 42, r=5, bg_color=(255,255,255), text=f"~ Basic Shape ~", font_size=10)
            
            # วาดจุดโยงเส้นด้านซ้าย (ขยับจุดมาอยู่กึ่งกลางกล่องใหม่พอดี)
            pdf.set_fill_color(*theme_colors["primary"])
            pdf.set_draw_color(*theme_colors["primary"])
            pdf.ellipse(78, y + 17, 8, 8, style='DF')
            
            # กล่องด้านขวา (ขยายขนาดเป็น w=50, h=42 เผื่อพื้นที่ระบายสี)
            draw_rounded_box(pdf, 142, y, 50, 42, r=5, bg_color=(255,255,255), text=f"~ Real Object ~", font_size=10)
            
            # วาดจุดโยงเส้นด้านขวา
            pdf.set_fill_color(*theme_colors["primary"])
            pdf.set_draw_color(*theme_colors["primary"])
            pdf.ellipse(130, y + 17, 8, 8, style='DF')
            
        pdf.ln(total_h + 10)

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
            # คืนค่าตัวตัดหน้าใหม่กลับเป็น 215 เพื่อไม่ให้มันเตะข้อ 3 ไปหน้าถัดไป
            if pdf.get_y() > 215: pdf.add_page()
            y = pdf.get_y()
            
            # ลดความสูงกล่องพื้นหลังลงจาก 60 เหลือ 55 เพื่อประหยัดพื้นที่
            draw_rounded_box(pdf, 15, y, 185, 55, r=8, bg_color=theme_colors["box"])
            start_x = center_x - 70
            
            # ลดความสูงกล่องสีขาวด้านในลงจาก 50 เหลือ 45 ให้สมส่วนกัน
            draw_rounded_box(pdf, start_x, y+5, 60, 45, r=5, bg_color=(255,255,255), text=f"~ Tall Item ~", font_size=11)
            draw_rounded_box(pdf, start_x+80, y+5, 60, 45, r=5, bg_color=(255,255,255), text=f"~ Short Item ~", font_size=11)
            
            # ลดระยะห่างบรรทัดลงเหลือ 60 เพื่อดึงทุกข้อให้ขยับขึ้นมาไม่ให้ทับขอบล่าง
            pdf.ln(60)

    elif "odd one out" in clean_sub:
        # ปรับโจทย์ใหม่ให้เพิ่มคำสั่งระบายสี
        pdf.cell(0, 10, f" Directions: Cross out (X) the picture that is different. Then color the pictures!", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            draw_rounded_box(pdf, 15, y, 185, 45, r=8, bg_color=theme_colors["box"])
            for j in range(4):
                draw_rounded_box(pdf, 25 + (j*42), y+5, 35, 35, r=5, bg_color=(255,255,255), text=f"~ Item ~", font_size=10)
            pdf.ln(55)

    elif "finish the pattern" in clean_sub:
        # แก้ไขคำสั่งจาก or เป็น and
        pdf.cell(0, 10, f" Directions: Look at the pattern. Draw and color what comes next.", ln=True)
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
        # เพิ่มคำสั่งให้ระบายสี และเปลี่ยนรูปแบบตัวเลือกให้เป็นวงกลมให้ระบายง่ายๆ
        pdf.cell(0, 10, f" Directions: Color the object. Then color the circle for UNDER or ON.", ln=True)
        pdf.ln(5)
        
        for i in range(num_q):
            if pdf.get_y() > 215: pdf.add_page()
            y = pdf.get_y()
            
            # กรอบพื้นหลัง
            draw_rounded_box(pdf, 15, y, 185, 55, r=8, bg_color=theme_colors["box"])
            
            # กล่องซ้ายสำหรับใส่รูปภาพ (Scene) ให้เด็กหารูปและระบายสี
            draw_rounded_box(pdf, 25, y+5, 60, 45, r=5, bg_color=(255,255,255), text="~ Scene ~", font_size=12)
            
            # วงกลมตัวเลือก 1: UNDER
            draw_rounded_box(pdf, 95, y+10, 35, 35, r=17.5, bg_color=(255,255,255), text="UNDER", font_size=11)
            
            # ตัวอักษรคำว่า "or" (ปรับให้กึ่งกลางเป๊ะทั้ง X และ Y)
            pdf.set_font("ComicNeue", "", 16)
            pdf.set_text_color(*theme_colors["secondary"])
            pdf.text(135, y + 30, "or")
            
            # วงกลมตัวเลือก 2: ON
            draw_rounded_box(pdf, 147, y+10, 35, 35, r=17.5, bg_color=(255,255,255), text="ON", font_size=11)
            
            pdf.ln(65)

    # ==========================================
    # โซนแกนที่ 4 : MEASUREMENT, DATA & SORTING
    # ==========================================
    elif "long or short" in clean_sub:
        pdf.cell(0, 10, f" Directions: Look at the pictures. Color the LONG one in each box.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 215: pdf.add_page()
            y = pdf.get_y()
            draw_rounded_box(pdf, 15, y, 185, 55, r=8, bg_color=theme_colors["box"])
            start_x = center_x - 70
            draw_rounded_box(pdf, start_x, y+5, 60, 45, r=5, bg_color=(255,255,255), text=f"~ Long Item ~", font_size=11)
            draw_rounded_box(pdf, start_x+80, y+5, 60, 45, r=5, bg_color=(255,255,255), text=f"~ Short Item ~", font_size=11)
            pdf.ln(60)

    elif "heavy or light" in clean_sub:
        pdf.cell(0, 10, f" Directions: Color the HEAVY object. Cross out (X) the LIGHT object.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 215: pdf.add_page()
            y = pdf.get_y()
            draw_rounded_box(pdf, 15, y, 185, 55, r=8, bg_color=theme_colors["box"])
            start_x = center_x - 70
            draw_rounded_box(pdf, start_x, y+5, 60, 45, r=5, bg_color=(255,255,255), text=f"~ Heavy Object ~", font_size=11)
            draw_rounded_box(pdf, start_x+80, y+5, 60, 45, r=5, bg_color=(255,255,255), text=f"~ Light Object ~", font_size=11)
            pdf.ln(60)

    elif "full or empty" in clean_sub:
        pdf.cell(0, 10, f" Directions: Color the FULL jar. Circle the EMPTY jar.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 215: pdf.add_page()
            y = pdf.get_y()
            draw_rounded_box(pdf, 15, y, 185, 55, r=8, bg_color=theme_colors["box"])
            start_x = center_x - 70
            draw_rounded_box(pdf, start_x, y+5, 60, 45, r=5, bg_color=(255,255,255), text=f"~ Full Jar ~", font_size=11)
            draw_rounded_box(pdf, start_x+80, y+5, 60, 45, r=5, bg_color=(255,255,255), text=f"~ Empty Jar ~", font_size=11)
            pdf.ln(60)

    elif "sort by color" in clean_sub:
        pdf.cell(0, 10, f" Directions: Draw a line to match the objects that have the SAME color.", ln=True)
        pdf.ln(5)
        total_h = (num_q * 52) + 10
        if pdf.get_y() + total_h > 250: pdf.add_page()
        start_y = pdf.get_y()
        
        # กล่องพื้นหลังใหญ่รวมทุกข้อ
        draw_rounded_box(pdf, 15, start_y, 185, total_h, r=8, bg_color=theme_colors["box"])
        for i in range(num_q):
            y = start_y + 6 + (i * 52)
            draw_rounded_box(pdf, 24, y, 50, 42, r=5, bg_color=(255,255,255), text=f"~ Object 1 ~", font_size=10)
            # จุดโยงซ้าย
            pdf.set_fill_color(*theme_colors["primary"])
            pdf.set_draw_color(*theme_colors["primary"])
            pdf.ellipse(78, y + 17, 8, 8, style='DF')
            
            draw_rounded_box(pdf, 142, y, 50, 42, r=5, bg_color=(255,255,255), text=f"~ Object 2 ~", font_size=10)
            # จุดโยงขวา
            pdf.set_fill_color(*theme_colors["primary"])
            pdf.set_draw_color(*theme_colors["primary"])
            pdf.ellipse(130, y + 17, 8, 8, style='DF')
        pdf.ln(total_h + 10)

    elif "sort by category" in clean_sub:
        pdf.cell(0, 10, f" Directions: Circle the items that belong in the same group. Cross out the odd one.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 215: pdf.add_page()
            y = pdf.get_y()
            draw_rounded_box(pdf, 15, y, 185, 55, r=8, bg_color=theme_colors["box"])
            draw_rounded_box(pdf, 25, y+5, 165, 45, r=5, bg_color=(255,255,255), text=f"~ Canva: Add 3 related items + 1 unrelated item ~", font_size=11)
            pdf.ln(60)

    elif "same and different" in clean_sub:
        pdf.cell(0, 10, f" Directions: Color the two pictures that are exactly the SAME.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 215: pdf.add_page()
            y = pdf.get_y()
            draw_rounded_box(pdf, 15, y, 185, 55, r=8, bg_color=theme_colors["box"])
            for j in range(4):
                draw_rounded_box(pdf, 25 + (j*42), y+7.5, 35, 40, r=5, bg_color=(255,255,255), text=f"~ Item ~", font_size=10)
            pdf.ln(60)

    elif "day or night" in clean_sub:
        # เปลี่ยนโจทย์เป็นการดูรูปแล้วระบายสีวงกลมคำตอบที่ถูกต้อง
        pdf.cell(0, 10, f" Directions: Does it happen in the DAY or at NIGHT? Color the correct circle.", ln=True)
        pdf.ln(5)
        
        for i in range(num_q):
            if pdf.get_y() > 215: pdf.add_page()
            y = pdf.get_y()
            
            # วาดกรอบพื้นหลังสำหรับแต่ละข้อ
            draw_rounded_box(pdf, 15, y, 185, 55, r=8, bg_color=theme_colors["box"])
            
            # ฝั่งซ้าย: กล่องสำหรับใส่รูปภาพกิจกรรม
            draw_rounded_box(pdf, 25, y+5, 60, 45, r=5, bg_color=(255,255,255), text="~ Activity ~", font_size=12)
            
            # วาดลูกศรคั่นสายตา (ปรับแกน Y ให้กึ่งกลางแล้ว จาก 35 เป็น 31)
            pdf.set_font("ComicNeue", "", 24)
            pdf.set_text_color(*theme_colors["secondary"])
            pdf.text(95, y + 31, ">")
            
            # ฝั่งขวา: ตัวเลือก DAY และ NIGHT
            # ตัวเลือก DAY
            draw_rounded_box(pdf, 115, y+10, 35, 35, r=17.5, bg_color=(255,255,255), text="DAY", font_size=12)
            
            # ตัวเลือก NIGHT
            draw_rounded_box(pdf, 155, y+10, 35, 35, r=17.5, bg_color=(255,255,255), text="NIGHT", font_size=12)
            
            pdf.ln(65)

    elif "picture graph" in clean_sub:
        # ปรับโจทย์ให้ง่ายขึ้น: นับจำนวนแล้วระบายสีทีละกล่อง
        pdf.cell(0, 10, f" Directions: Count the animals. Color one box for each animal.", ln=True)
        pdf.ln(5)
        
        # ป้องกันการโดดไปหน้าใหม่ถ้าระยะไม่พอ
        if pdf.get_y() > 80: pdf.add_page()
        y = pdf.get_y()
        
        # 1. กล่องด้านบน (ใส่รูปภาพสัตว์ปนกัน แค่ 2 ชนิดพอ)
        draw_rounded_box(pdf, 15, y, 185, 75, r=8, bg_color=theme_colors["box"], text="~ Canva: Scene with 2 types of animals (e.g. 3 Cats, 4 Dogs) ~", font_size=11)
        
        # 2. กราฟแนวนอน (Horizontal Graph) ด้านล่าง
        graph_y = y + 85
        draw_rounded_box(pdf, 15, graph_y, 185, 95, r=8, bg_color=theme_colors["box"])
        
        pdf.set_draw_color(*theme_colors["primary"])
        pdf.set_line_width(0.6)
        
        # แถวที่ 1 (สัตว์ชนิดที่ 1)
        row1_y = graph_y + 15
        draw_rounded_box(pdf, 25, row1_y, 35, 25, r=5, bg_color=(255,255,255), text="~ Animal 1 ~", font_size=10)
        # ช่องสี่เหลี่ยมให้ระบายสี 5 ช่อง (แนวนอน)
        for b in range(5):
            pdf.set_fill_color(255,255,255)
            pdf.rect(68 + (b*22), row1_y, 20, 25, 'DF')
            
        # แถวที่ 2 (สัตว์ชนิดที่ 2)
        row2_y = graph_y + 55
        draw_rounded_box(pdf, 25, row2_y, 35, 25, r=5, bg_color=(255,255,255), text="~ Animal 2 ~", font_size=10)
        # ช่องสี่เหลี่ยมให้ระบายสี 5 ช่อง (แนวนอน)
        for b in range(5):
            pdf.set_fill_color(255,255,255)
            pdf.rect(68 + (b*22), row2_y, 20, 25, 'DF')
            
        pdf.ln(185)



    # ==========================================
    # 🥉 โซน GRADE 1 (ป.1) ฉบับสมบูรณ์
    # ==========================================
    elif "addition within 20" in clean_sub: 
        pdf.cell(0, 10, f" Directions: Solve the math problems. Write the answers in the boxes.", ln=True)
        pdf.ln(5)
        
        y_start = pdf.get_y()
        box_w = 85   # ความกว้างกล่องต่อ 1 คอลัมน์
        box_h = 50   # ความสูงของกล่อง
        gap_x = 15   # ระยะห่างระหว่างคอลัมน์ซ้าย-ขวา
        gap_y = 15   # ระยะห่างระหว่างแถวบน-ล่าง
        
        for i in range(6): # บังคับให้มี 6 ข้อในหน้านี้เสมอ
            row = i // 2
            col = i % 2
            
            # คำนวณพิกัด X, Y อัตโนมัติ
            x = 15 + col * (box_w + gap_x)
            y = y_start + row * (box_h + gap_y)
            
            # วาดกรอบสีพื้นหลัง
            draw_rounded_box(pdf, x, y, box_w, box_h, r=8, bg_color=theme_colors["box"])
            
            # สุ่มตัวเลข
            a = random.randint(1, 15)
            b = random.randint(1, 20 - a) # ผลลัพธ์ไม่เกิน 20
            ans = a + b
            
            # กล่องขาวสำหรับใส่โจทย์ด้านใน
            inner_w = 70
            inner_h = 35
            inner_x = x + 7.5
            inner_y = y + 7.5
            draw_rounded_box(pdf, inner_x, inner_y, inner_w, inner_h, r=5, bg_color=(255,255,255))
            
            # จัดการตัวหนังสือให้อยู่กึ่งกลางเป๊ะ
            pdf.set_font("ComicNeue", "", 24)
            eq_text = f"{a}  +  {b}  =  "
            line_text = "____"
            ans_text = str(ans)
            
            w_eq = pdf.get_string_width(eq_text)
            w_line = pdf.get_string_width(line_text)
            w_ans = pdf.get_string_width(ans_text)
            
            total_w = w_eq + w_line
            start_text_x = inner_x + (inner_w - total_w) / 2
            
            # พิมพ์โจทย์
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(start_text_x, inner_y + 23, eq_text)
            
            # พิมพ์ช่องว่าง หรือ เฉลย
            if pdf.is_key:
                pdf.set_text_color(*theme_colors["secondary"]) # สีเฉลย
                # คำนวณให้เลขเฉลยลอยอยู่ตรงกลางของเส้นใต้พอดี
                center_line = start_text_x + w_eq + (w_line / 2)
                pdf.text(center_line - (w_ans / 2), inner_y + 22, ans_text) 
            else:
                pdf.set_text_color(*theme_colors["primary"])
                pdf.text(start_text_x + w_eq, inner_y + 23, line_text)
                
        # เลื่อนระยะบรรทัด Y ลงมาให้พ้นกล่องชุดนี้ เผื่อมีหน้าถัดไป
        pdf.set_y(y_start + 3 * (box_h + gap_y))

    elif "number bonds" in clean_sub:
        pdf.cell(0, 10, f" Directions: Fill in the missing number to complete the number bonds.", ln=True)
        pdf.ln(5)
        
        y_start = pdf.get_y()
        box_w = 85   # ความกว้างกล่อง
        box_h = 50   # ปรับความสูงกล่องลดลงอีก เหลือ 50 เพื่อให้พ้นขอบล่างแน่นอน
        gap_x = 15   # ระยะห่างซ้าย-ขวา
        gap_y = 10   # ปรับระยะห่างบน-ล่างให้กระชับขึ้น
        
        for i in range(6): # ล็อกไว้ที่ 6 ข้อ (3 แถว x 2 คอลัมน์)
            row = i // 2
            col = i % 2
            
            x = 15 + col * (box_w + gap_x)
            y = y_start + row * (box_h + gap_y)
            
            # วาดกรอบสีพื้นหลัง
            draw_rounded_box(pdf, x, y, box_w, box_h, r=8, bg_color=theme_colors["box"])
            box_center_x = x + (box_w / 2) # คำนวณจุดกึ่งกลางของกล่องนี้
            
            # สุ่มตัวเลข
            total = random.randint(5, 20)
            part1 = random.randint(1, total - 1)
            part2 = total - part1
            
            # สุ่มซ่อนตัวเลข (เอาเครื่องหมาย ? ออก เปลี่ยนเป็นช่องว่าง "")
            hide_idx = random.choice([0, 1, 2])
            val_total = str(total) if (hide_idx != 0 or pdf.is_key) else ""
            val_p1 = str(part1) if (hide_idx != 1 or pdf.is_key) else ""
            val_p2 = str(part2) if (hide_idx != 2 or pdf.is_key) else ""
            
            # วาดเส้นเชื่อม (ปรับให้สั้นลงตามขนาดกล่อง)
            pdf.set_line_width(1.2)
            pdf.set_draw_color(*theme_colors["primary"])
            pdf.line(box_center_x, y + 16, box_center_x - 18, y + 36) 
            pdf.line(box_center_x, y + 16, box_center_x + 18, y + 36) 
            
            # วาดวงกลม 3 วง (ย่อขนาดให้สมส่วนกับกล่องที่เล็กลง)
            draw_solid_circle(pdf, box_center_x - 12, y + 4, 24, val_total, font_size=20) # วงกลมบน (ผลรวม)
            draw_solid_circle(pdf, box_center_x - 28, y + 26, 20, val_p1, font_size=16)  # วงกลมซ้ายล่าง
            draw_solid_circle(pdf, box_center_x + 8, y + 26, 20, val_p2, font_size=16)   # วงกลมขวาล่าง
            
        # เลื่อนตำแหน่ง Y ให้พ้นกล่องชุดนี้ (บวกระยะห่างเผื่อไว้)
        pdf.set_y(y_start + 3 * (box_h + gap_y))

    elif "fact families" in clean_sub:
        pdf.cell(0, 10, f" Directions: Use the 3 numbers to write two addition and two subtraction facts.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 200: pdf.add_page()
            y = pdf.get_y()
            draw_rounded_box(pdf, 15, y, 185, 80, r=8, bg_color=theme_colors["box"])
            
            # สร้างตัวเลข
            p1 = random.randint(2, 9)
            p2 = random.randint(2, 9)
            if p1 == p2: p2 += 1
            total = p1 + p2
            
            # กล่องใส่ตัวเลข 3 ตัวฝั่งซ้าย (เสมือนหลังคาบ้าน)
            draw_rounded_box(pdf, 25, y+10, 60, 60, r=5, bg_color=(255,255,255))
            pdf.set_font("ComicNeue", "", 24)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(35, y + 40, f"{p1} , {p2} , {total}")
            
            # กล่องสมการ 4 บรรทัดฝั่งขวา
            start_x = 95
            h_box = 12
            draw_rounded_box(pdf, start_x, y+10, 80, h_box, r=2, bg_color=(255,255,255), text="_____ + _____ = _____", font_size=16)
            draw_rounded_box(pdf, start_x, y+25, 80, h_box, r=2, bg_color=(255,255,255), text="_____ + _____ = _____", font_size=16)
            draw_rounded_box(pdf, start_x, y+40, 80, h_box, r=2, bg_color=(255,255,255), text="_____ - _____ = _____", font_size=16)
            draw_rounded_box(pdf, start_x, y+55, 80, h_box, r=2, bg_color=(255,255,255), text="_____ - _____ = _____", font_size=16)
            
            # โชว์เฉลย
            if pdf.is_key:
                pdf.set_font("ComicNeue", "", 16)
                pdf.set_text_color(*theme_colors["secondary"])
                pdf.text(start_x+5, y+18, f"{p1}         {p2}         {total}")
                pdf.text(start_x+5, y+33, f"{p2}         {p1}         {total}")
                pdf.text(start_x+5, y+48, f"{total}         {p1}         {p2}")
                pdf.text(start_x+5, y+63, f"{total}         {p2}         {p1}")
                
            pdf.ln(90)

    elif "place value basics" in clean_sub:
        pdf.cell(0, 10, f" Directions: Count the Tens and Ones. Write the number.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            draw_rounded_box(pdf, 15, y, 185, 55, r=8, bg_color=theme_colors["box"])
            
            tens = random.randint(1, 9)
            ones = random.randint(1, 9)
            ans = (tens * 10) + ones
            
            # กล่องซ้ายใส่ Tens / Ones
            draw_rounded_box(pdf, 25, y+5, 100, 45, r=5, bg_color=(255,255,255), text=f"~ {tens} Tens & {ones} Ones ~", font_size=14)
            
            # กล่องขวาคำตอบ
            ans_text = str(ans) if pdf.is_key else ""
            draw_rounded_box(pdf, 140, y+5, 45, 45, r=5, bg_color=(255,255,255), text=ans_text, font_size=32)
            pdf.ln(65)

    elif "counting to 120" in clean_sub:
        pdf.cell(0, 10, f" Directions: Fill in the missing numbers.", ln=True)
        pdf.ln(2) # ลดระยะห่างบรรทัดตรงนี้ลงนิดหน่อยให้ประหยัดพื้นที่
        
        y_start = pdf.get_y()
        box_h = 38   # ลดความสูงกล่องลง (เพื่อให้ 4 ข้อ พอดีหน้ากระดาษ)
        gap_y = 8    # ลดระยะห่างระหว่างแถว
        
        for i in range(4): # ล็อกจำนวนข้อไว้ที่ 4 ข้อ
            y = y_start + i * (box_h + gap_y)
            
            # วาดกรอบสีพื้นหลัง
            draw_rounded_box(pdf, 15, y, 185, box_h, r=8, bg_color=theme_colors["box"])
            
            start_num = random.randint(50, 115)
            seq = [start_num + j for j in range(5)]
            hide_idx = random.sample([0, 1, 2, 3, 4], 2) # สุ่มซ่อน 2 ตำแหน่ง
            
            circle_d = 26 # ขยับขนาดวงกลมลงนิดนึงให้พอดีกับกล่องใหม่
            start_x = center_x - (165 / 2) # จัดระยะ X ใหม่ให้สมดุล
            
            for j in range(5):
                x = start_x + (j * 34) # ขยับระยะห่างแต่ละวงกลมให้พอดี
                circle_y = y + 6       # จัดให้วงกลมอยู่กึ่งกลางแนวตั้งของกล่องเป๊ะๆ
                
                if j in hide_idx:
                    val = str(seq[j]) if pdf.is_key else "" 
                    draw_circle_placeholder(pdf, x, circle_y, circle_d, val)
                else:
                    draw_solid_circle(pdf, x, circle_y, circle_d, str(seq[j]), font_size=20)
                    
        # เลื่อนเคอร์เซอร์ Y ลงมาให้พ้นกล่อง
        pdf.set_y(y_start + 4 * (box_h + gap_y))

    elif "greater than" in clean_sub:
        pdf.cell(0, 10, f" Directions: Compare the numbers. Write > , < , or = in the circle.", ln=True)
        pdf.ln(5)
        
        y_start = pdf.get_y()
        box_w = 85   # ความกว้างกล่อง
        box_h = 45   # ปรับความสูงกล่องลดลง เพื่อให้ 3 แถวไม่ล้นหน้ากระดาษ
        gap_x = 15   # ระยะห่างระหว่างคอลัมน์ซ้าย-ขวา
        gap_y = 12   # ระยะห่างระหว่างแถวบน-ล่าง
        
        for i in range(6): # ล็อกไว้ที่ 6 ข้อ (3 แถว x 2 คอลัมน์)
            row = i // 2
            col = i % 2
            
            x = 15 + col * (box_w + gap_x)
            y = y_start + row * (box_h + gap_y)
            
            # วาดกรอบสีพื้นหลัง
            draw_rounded_box(pdf, x, y, box_w, box_h, r=8, bg_color=theme_colors["box"])
            
            # สุ่มตัวเลข 2 หลัก
            n1 = random.randint(10, 99)
            n2 = random.randint(10, 99)
            if random.random() > 0.85: n2 = n1 # สุ่มให้มีโอกาส 15% ที่เลขจะเท่ากัน
            
            ans = "=" if n1 == n2 else (">" if n1 > n2 else "<")
            
            # ถ้าเป็นเฉลยโชว์เครื่องหมาย ถ้าไม่ใช่ให้เป็นค่าว่าง (เอา ? ออก)
            show_ans = ans if pdf.is_key else ""
            
            # กล่องตัวเลขฝั่งซ้าย
            draw_rounded_box(pdf, x + 6, y + 8.5, 24, 28, r=4, bg_color=(255,255,255), text=str(n1), font_size=24)
            
            # วงกลมตรงกลางสำหรับใส่เครื่องหมาย
            circle_x = x + 31.5
            circle_y = y + 11.5
            circle_d = 22
            if pdf.is_key:
                draw_solid_circle(pdf, circle_x, circle_y, circle_d, show_ans, font_size=24)
            else:
                draw_circle_placeholder(pdf, circle_x, circle_y, circle_d, show_ans) # ตอนนี้จะว่างเปล่า
                
            # กล่องตัวเลขฝั่งขวา
            draw_rounded_box(pdf, x + 55, y + 8.5, 24, 28, r=4, bg_color=(255,255,255), text=str(n2), font_size=24)
            
        # เลื่อนระยะ Y เผื่อหน้ากระดาษไว้
        pdf.set_y(y_start + 3 * (box_h + gap_y))

    # ==========================================
    # 🥈 โซน GRADE 2 (ป.2)
    # ==========================================
    elif "hundreds, tens, ones" in clean_sub:
        pdf.cell(0, 10, f" Directions: Count the Hundreds, Tens, and Ones. Write the number.", ln=True)
        pdf.ln(2) 
        
        y_start = pdf.get_y()
        box_h = 34   # เพิ่มความสูงกล่องขึ้นจาก 28 เป็น 34 ให้ดูใหญ่และเต็มตาขึ้น
        gap_y = 7    # ปรับระยะห่างระหว่างข้อเล็กน้อย
        
        for i in range(5): # 5 ข้อ
            y = y_start + i * (box_h + gap_y)
            
            # วาดกรอบสีพื้นหลัง (กว้างเต็มหน้ากระดาษ)
            draw_rounded_box(pdf, 15, y, 185, box_h, r=8, bg_color=theme_colors["box"])
            
            # สุ่มตัวเลขหลักร้อย สิบ หน่วย
            h = random.randint(1, 9)
            t = random.randint(1, 9)
            o = random.randint(1, 9)
            ans = (h * 100) + (t * 10) + o
            
            # กล่องใหญ่ด้านซ้ายสำหรับใส่ภาพบล็อก (Base Ten Blocks)
            # ขยายความสูงกล่องขาวตามกล่องหลัก
            draw_rounded_box(pdf, 22, y + 4.5, 115, 25, r=4, bg_color=(255,255,255), text=f"~ Canva: {h} Hundreds, {t} Tens, {o} Ones ~", font_size=12)
            
            # กล่องเล็กด้านขวาสำหรับเขียนคำตอบ
            ans_text = str(ans) if pdf.is_key else ""
            draw_rounded_box(pdf, 145, y + 4.5, 45, 25, r=4, bg_color=(255,255,255), text=ans_text, font_size=24) 
            
        # เลื่อนเคอร์เซอร์ Y ให้พ้นกล่องทั้งหมด
        pdf.set_y(y_start + 5 * (box_h + gap_y))

    elif "2-digit" in clean_sub:
        pdf.cell(0, 10, f" Directions: Solve the addition and subtraction problems.", ln=True)
        pdf.ln(5)
        
        y_start = pdf.get_y()
        box_w = 85
        box_h = 55
        gap_x = 15
        gap_y = 10
        
        for i in range(6):
            row = i // 2
            col = i % 2
            x = 15 + col * (box_w + gap_x)
            y = y_start + row * (box_h + gap_y)
            
            draw_rounded_box(pdf, x, y, box_w, box_h, r=8, bg_color=theme_colors["box"])
            inner_x = x + 15
            inner_y = y + 5
            draw_rounded_box(pdf, inner_x, inner_y, 55, 45, r=5, bg_color=(255,255,255))
            
            # สุ่มการตั้งบวกลบแนวตั้ง
            op = random.choice(["+", "-"])
            if op == "+":
                a = random.randint(10, 89)
                b = random.randint(10, 99 - a)
                ans = a + b
            else:
                a = random.randint(20, 99)
                b = random.randint(10, a - 1)
                ans = a - b
                
            pdf.set_font("ComicNeue", "", 28)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(inner_x + 20, inner_y + 15, str(a).rjust(2))
            pdf.text(inner_x + 10, inner_y + 25, op)
            pdf.text(inner_x + 20, inner_y + 28, str(b).rjust(2))
            
            pdf.set_line_width(0.8)
            pdf.line(inner_x + 10, inner_y + 32, inner_x + 45, inner_y + 32)
            
            if pdf.is_key:
                pdf.set_text_color(*theme_colors["secondary"])
                pdf.text(inner_x + 20, inner_y + 42, str(ans).rjust(2))
                
        pdf.set_y(y_start + 3 * (box_h + gap_y))

    elif "even or odd" in clean_sub:
        pdf.cell(0, 10, f" Directions: Look at the number. Color 'Even' or 'Odd'.", ln=True)
        pdf.ln(2) # เพิ่มระยะเว้นบรรทัดกลับมานิดหน่อยให้สวยงาม
        
        y_start = pdf.get_y()
        box_w = 85
        box_h = 32   # ขยายความสูงกล่องให้เต็มตาขึ้น (จากเดิม 28)
        gap_x = 15
        gap_y = 8    # เพิ่มระยะห่างระหว่างแถวให้กระจายเต็มหน้ากระดาษพอดี
        
        for i in range(10): # 10 ข้อ (5 แถว x 2 คอลัมน์)
            row = i // 2
            col = i % 2
            x = 15 + col * (box_w + gap_x)
            y = y_start + row * (box_h + gap_y)
            
            # วาดกรอบสีพื้นหลัง
            draw_rounded_box(pdf, x, y, box_w, box_h, r=8, bg_color=theme_colors["box"])
            
            # สุ่มตัวเลข 2 หลัก
            num = random.randint(10, 99)
            is_even = (num % 2 == 0)
            
            # กล่องสีขาวสำหรับใส่ตัวเลข (ขยายขนาดให้ใหญ่ขึ้น)
            draw_rounded_box(pdf, x + 5, y + 4, 24, 24, r=4, bg_color=(255,255,255), text=str(num), font_size=22)
            
            # วงกลมคำว่า Even / Odd (ขยายขนาดกลับมาเป็น 18 และปรับตำแหน่งให้อยู่กึ่งกลางพอดี)
            draw_solid_circle(pdf, x + 38, y + 7, 18, "Even", font_size=11, is_path=(pdf.is_key and is_even))
            draw_solid_circle(pdf, x + 62, y + 7, 18, "Odd", font_size=11, is_path=(pdf.is_key and not is_even))
            
        # เลื่อนตำแหน่ง Y เผื่อเนื้อหาด้านล่าง
        pdf.set_y(y_start + 5 * (box_h + gap_y))

    elif "3-digit" in clean_sub: # Comparing Numbers
        pdf.cell(0, 10, f" Directions: Compare the numbers. Write > , < , or = in the circle.", ln=True)
        pdf.ln(2) 
        
        y_start = pdf.get_y()
        box_w = 85
        box_h = 32   # ปรับความสูงกล่องเป็น 32 (เมื่อรวม 5 แถวจะพอดีกรอบล่างเป๊ะ)
        gap_x = 15
        gap_y = 8    # ระยะห่างระหว่างแถวเพื่อให้กระจายตัวสวยงาม
        
        for i in range(10): # เปลี่ยนเป็น 10 ข้อ (5 แถว x 2 คอลัมน์)
            row = i // 2
            col = i % 2
            x = 15 + col * (box_w + gap_x)
            y = y_start + row * (box_h + gap_y)
            
            # วาดกรอบสีพื้นหลัง
            draw_rounded_box(pdf, x, y, box_w, box_h, r=8, bg_color=theme_colors["box"])
            
            # สุ่มตัวเลข 3 หลัก
            n1 = random.randint(100, 999)
            n2 = random.randint(100, 999)
            if random.random() > 0.85: n2 = n1 
            
            ans = "=" if n1 == n2 else (">" if n1 > n2 else "<")
            show_ans = ans if pdf.is_key else ""
            
            # กล่องตัวเลขฝั่งซ้าย (ปรับตำแหน่ง Y ให้กึ่งกลางกล่อง)
            draw_rounded_box(pdf, x + 4, y + 4, 28, 24, r=4, bg_color=(255,255,255), text=str(n1), font_size=18)
            
            # วงกลมตรงกลางสำหรับเครื่องหมาย (ขนาด 18 และจัดกึ่งกลาง)
            circle_d = 18
            if pdf.is_key:
                draw_solid_circle(pdf, x + 33.5, y + 7, circle_d, show_ans, font_size=20)
            else:
                draw_circle_placeholder(pdf, x + 33.5, y + 7, circle_d, show_ans) 
                
            # กล่องตัวเลขฝั่งขวา
            draw_rounded_box(pdf, x + 53, y + 4, 28, 24, r=4, bg_color=(255,255,255), text=str(n2), font_size=18)
            
        # เลื่อนตำแหน่ง Y เผื่อเนื้อหาด้านล่าง
        pdf.set_y(y_start + 5 * (box_h + gap_y))

    elif "expanded form" in clean_sub:
        pdf.cell(0, 10, f" Directions: Write each number in expanded form.", ln=True)
        pdf.ln(2) 
        
        y_start = pdf.get_y()
        box_w = 85
        box_h = 32   # ปรับความสูงกล่องเป็น 32 เมื่อมี 5 แถวจะพอดีเต็มหน้ากระดาษเป๊ะ
        gap_x = 15
        gap_y = 8    # ระยะห่างระหว่างแถวให้กระจายตัวสวยงาม
        
        for i in range(10): # เปลี่ยนเป็น 10 ข้อ (5 แถว x 2 คอลัมน์)
            row = i // 2
            col = i % 2
            x = 15 + col * (box_w + gap_x)
            y = y_start + row * (box_h + gap_y)
            
            # วาดกรอบสีพื้นหลัง
            draw_rounded_box(pdf, x, y, box_w, box_h, r=8, bg_color=theme_colors["box"])
            
            # สุ่มเลขหลักร้อย สิบ หน่วย
            h = random.randint(1, 9) * 100
            t = random.randint(1, 9) * 10
            o = random.randint(1, 9)
            val = h + t + o
            
            # 1. กล่องตัวเลขโจทย์ (ด้านซ้ายสุด) ปรับพิกัด Y ให้กึ่งกลางกล่อง
            draw_rounded_box(pdf, x + 2, y + 8, 18, 16, r=3, bg_color=(255,255,255), text=str(val), font_size=14)
            
            # เครื่องหมาย = (ขยับ Y ตามให้ตรงกับกล่อง)
            pdf.set_font("ComicNeue", "", 16)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(x + 22, y + 19, "=")
            
            # เตรียมข้อความเฉลย (ถ้าเป็นโหมดเฉลยจะโชว์เลข ถ้าไม่ใช่จะว่างไว้)
            ans_h = str(h) if pdf.is_key else ""
            ans_t = str(t) if pdf.is_key else ""
            ans_o = str(o) if pdf.is_key else ""
            
            # 2. กล่องหลักร้อย
            draw_rounded_box(pdf, x + 26, y + 8, 15, 16, r=3, bg_color=(255,255,255), text=ans_h, font_size=12)
            
            # เครื่องหมาย +
            pdf.set_font("ComicNeue", "", 16)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(x + 43, y + 19, "+")
            
            # 3. กล่องหลักสิบ
            draw_rounded_box(pdf, x + 48, y + 8, 14, 16, r=3, bg_color=(255,255,255), text=ans_t, font_size=12)
            
            # เครื่องหมาย +
            pdf.set_font("ComicNeue", "", 16)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(x + 64, y + 19, "+")
            
            # 4. กล่องหลักหน่วย
            draw_rounded_box(pdf, x + 69, y + 8, 13, 16, r=3, bg_color=(255,255,255), text=ans_o, font_size=12)
                
        # เลื่อนตำแหน่ง Y เผื่อเนื้อหาด้านล่าง
        pdf.set_y(y_start + 5 * (box_h + gap_y))

    elif "skip counting" in clean_sub:
        pdf.cell(0, 10, f" Directions: Skip count to fill in the missing numbers.", ln=True)
        pdf.ln(2) 
        
        y_start = pdf.get_y()
        box_h = 32    # ปรับลดลงเพื่อให้มีพื้นที่เหลือด้านล่างและไม่ทะลุกรอบ
        gap_y = 6     # ลดระยะห่างเพื่อให้ 5 ข้อกระจายตัวสวยงามและอยู่ในกรอบ
        
        for i in range(5): 
            y = y_start + i * (box_h + gap_y)
            # วาดกรอบพื้นหลังแต่ละข้อ
            draw_rounded_box(pdf, 15, y, 185, box_h, r=8, bg_color=theme_colors["box"])
            
            step = random.choice([2, 5, 10])
            start_num = random.randint(1, 20) * step
            seq = [start_num + (j * step) for j in range(5)]
            hide_idx = random.sample([1, 2, 3, 4], 2)
            
            circle_d = 24 # ปรับขนาดวงกลมให้เล็กลงเพื่อให้วาง 5 วงในแนวนอนได้พอดี
            start_x = 25  # กำหนดจุดเริ่ม X ใหม่ให้ไม่เบียดซ้ายเกินไป
            
            for j in range(5):
                x = start_x + (j * 36) # ระยะห่างแนวนอน 36
                circle_y = y + 4       # จัดตำแหน่ง Y ให้อยู่กลางกล่อง
                
                if j in hide_idx:
                    val = str(seq[j]) if pdf.is_key else "" 
                    draw_circle_placeholder(pdf, x, circle_y, circle_d, val)
                else:
                    draw_solid_circle(pdf, x, circle_y, circle_d, str(seq[j]), font_size=16)
                    
        # เซ็ตจุดสิ้นสุดของ Y ให้หยุดก่อนถึงขอบล่าง
        pdf.set_y(y_start + 5 * (box_h + gap_y))

    # ==========================================
    # โซนแกนที่ 3 : GRADE 3 TOPICS (ป.3)
    # ==========================================
    elif "word problems" in clean_sub:
        pdf.cell(0, 10, f" Directions: Read carefully and solve the word problems.", ln=True)
        pdf.ln(2)
        y_start = pdf.get_y()
        box_h = 42   # 4 ข้อ ให้กล่องใหญ่หน่อยเพื่อใส่โจทย์ยาวๆ ได้
        gap_y = 8
        
        problems = [
            ("Sarah has {a} apples. She buys {b} more. How many does she have?", "+"),
            ("Tom had {a} dollars. He spent {b} dollars. How much is left?", "-"),
            ("There are {a} boxes. Each has {b} toys. How many toys in total?", "*")
        ]
        
        for i in range(4): # 4 ข้อพอดีหน้า
            y = y_start + i * (box_h + gap_y)
            draw_rounded_box(pdf, 15, y, 185, box_h, r=8, bg_color=theme_colors["box"])
            
            prob_template, op = random.choice(problems)
            a = random.randint(10, 50)
            b = random.randint(2, 9) if op == "*" else random.randint(10, 30)
            if op == "-" and a < b: a, b = b, a
            
            ans = a + b if op == "+" else (a - b if op == "-" else a * b)
            question_text = prob_template.format(a=a, b=b)
            
            pdf.set_y(y + 8)
            pdf.set_x(20)
            try:
                pdf.set_font("ComicNeue", "", 16)
            except:
                pdf.set_font("Arial", "", 16)
            pdf.multi_cell(120, 8, f"{i+1}. {question_text}")
            
            ans_text = str(ans) if pdf.is_key else ""
            draw_rounded_box(pdf, 150, y + 8, 40, 25, r=4, bg_color=(255,255,255), text=ans_text, font_size=20)
            
        pdf.set_y(y_start + 4 * (box_h + gap_y))

    elif "multiplication" in clean_sub:
        pdf.cell(0, 10, f" Directions: Find the product.", ln=True)
        pdf.ln(2)
        y_start = pdf.get_y()
        box_w, box_h = 85, 32
        gap_x, gap_y = 15, 8
        
        for i in range(10): # 10 ข้อ (5 แถว x 2 คอลัมน์) ไม่ทะลุกรอบแน่นอน
            row = i // 2
            col = i % 2
            x = 15 + col * (box_w + gap_x)
            y = y_start + row * (box_h + gap_y)
            
            draw_rounded_box(pdf, x, y, box_w, box_h, r=8, bg_color=theme_colors["box"])
            
            n1, n2 = random.randint(2, 12), random.randint(2, 12)
            ans = n1 * n2
            
            draw_rounded_box(pdf, x + 5, y + 6, 20, 20, r=4, bg_color=(255,255,255), text=str(n1), font_size=18)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.set_font("ComicNeue", "", 20)
            pdf.text(x + 29, y + 20, "x")
            draw_rounded_box(pdf, x + 37, y + 6, 20, 20, r=4, bg_color=(255,255,255), text=str(n2), font_size=18)
            pdf.text(x + 60, y + 20, "=")
            
            ans_text = str(ans) if pdf.is_key else ""
            draw_rounded_box(pdf, x + 67, y + 6, 15, 20, r=4, bg_color=(255,255,255), text=ans_text, font_size=16)
            
        pdf.set_y(y_start + 5 * (box_h + gap_y))

    elif "fractions" in clean_sub:
        pdf.cell(0, 10, f" Directions: Write the fraction for the shaded parts.", ln=True)
        pdf.ln(2)
        y_start = pdf.get_y()
        box_w, box_h = 85, 32
        gap_x, gap_y = 15, 8
        
        for i in range(10):
            row = i // 2
            col = i % 2
            x = 15 + col * (box_w + gap_x)
            y = y_start + row * (box_h + gap_y)
            
            draw_rounded_box(pdf, x, y, box_w, box_h, r=8, bg_color=theme_colors["box"])
            
            num = random.randint(1, 5)
            den = random.randint(num + 1, 8)
            
            draw_rounded_box(pdf, x + 5, y + 4, 35, 24, r=4, bg_color=(255,255,255), text=f"~ {num}/{den} shape ~", font_size=10)
            
            pdf.set_font("ComicNeue", "", 24)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(x + 45, y + 20, "=")
            
            ans_num = str(num) if pdf.is_key else ""
            ans_den = str(den) if pdf.is_key else ""
            draw_rounded_box(pdf, x + 55, y + 3, 20, 11, r=2, bg_color=(255,255,255), text=ans_num, font_size=14)
            pdf.set_line_width(0.8)
            pdf.set_draw_color(*theme_colors["primary"])
            pdf.line(x + 55, y + 16, x + 75, y + 16)
            draw_rounded_box(pdf, x + 55, y + 18, 20, 11, r=2, bg_color=(255,255,255), text=ans_den, font_size=14)

        pdf.set_y(y_start + 5 * (box_h + gap_y))

    elif "measurement" in clean_sub:
        pdf.cell(0, 10, f" Directions: Read the ruler and write the length.", ln=True)
        pdf.ln(2)
        y_start = pdf.get_y()
        box_h, gap_y = 32, 6
        for i in range(5):
            y = y_start + i * (box_h + gap_y)
            draw_rounded_box(pdf, 15, y, 185, box_h, r=8, bg_color=theme_colors["box"])
            length = random.randint(2, 12)
            draw_rounded_box(pdf, 20, y + 5, 120, 22, r=4, bg_color=(255,255,255), text=f"~ Canva: Object {length} inches long above a ruler ~", font_size=12)
            ans_text = f"{length} in" if pdf.is_key else ""
            draw_rounded_box(pdf, 145, y + 5, 35, 22, r=4, bg_color=(255,255,255), text=ans_text, font_size=16)
        pdf.set_y(y_start + 5 * (box_h + gap_y))

    elif "time" in clean_sub:
        pdf.cell(0, 10, f" Directions: Read the clock and write the time.", ln=True)
        pdf.ln(2)
        y_start = pdf.get_y()
        box_w, box_h = 85, 32
        gap_x, gap_y = 15, 8
        for i in range(10):
            row = i // 2
            col = i % 2
            x = 15 + col * (box_w + gap_x)
            y = y_start + row * (box_h + gap_y)
            draw_rounded_box(pdf, x, y, box_w, box_h, r=8, bg_color=theme_colors["box"])
            h = random.randint(1, 12)
            m = random.choice(["00", "15", "30", "45"])
            draw_rounded_box(pdf, x + 5, y + 4, 30, 24, r=12, bg_color=(255,255,255), text=f"~ Clock {h}:{m} ~", font_size=9)
            ans_text = f"{h}:{m}" if pdf.is_key else ":"
            draw_rounded_box(pdf, x + 45, y + 6, 35, 20, r=4, bg_color=(255,255,255), text=ans_text, font_size=18)
        pdf.set_y(y_start + 5 * (box_h + gap_y))

    elif "money" in clean_sub:
        pdf.cell(0, 10, f" Directions: Count the coins and write the total amount.", ln=True)
        pdf.ln(2)
        y_start = pdf.get_y()
        box_h, gap_y = 32, 6
        for i in range(5):
            y = y_start + i * (box_h + gap_y)
            draw_rounded_box(pdf, 15, y, 185, box_h, r=8, bg_color=theme_colors["box"])
            cents = random.randint(15, 99)
            draw_rounded_box(pdf, 20, y + 5, 120, 22, r=4, bg_color=(255,255,255), text=f"~ Canva: Coins totaling {cents}¢ ~", font_size=12)
            ans_text = f"{cents}¢" if pdf.is_key else "¢"
            draw_rounded_box(pdf, 145, y + 5, 35, 22, r=4, bg_color=(255,255,255), text=ans_text, font_size=18)
        pdf.set_y(y_start + 5 * (box_h + gap_y))

    elif "math logic puzzles" in clean_sub:
        pdf.cell(0, 10, f" Directions: Find the value of each shape.", ln=True)
        pdf.ln(2)
        draw_rounded_box(pdf, 15, pdf.get_y(), 185, 180, r=8, bg_color=theme_colors["box"])
        pdf.set_y(pdf.get_y() + 10)
        pdf.set_font("ComicNeue", "", 18)
        pdf.set_text_color(*theme_colors["primary"])
        
        # ตัวอย่าง Puzzle ป.3
        pdf.cell(0, 10, "★ + ★ = 10", ln=True, align="C")
        pdf.cell(0, 10, "★ + ♥ = 12", ln=True, align="C")
        pdf.cell(0, 10, "♥ - ▲ = 3", ln=True, align="C")
        pdf.ln(10)
        pdf.cell(0, 10, "What is the value of ▲ ?", ln=True, align="C")
        
        ans_text = "4" if pdf.is_key else ""
        draw_rounded_box(pdf, 107.95 - 20, pdf.get_y() + 5, 40, 25, r=4, bg_color=(255,255,255), text=ans_text, font_size=24)
        pdf.set_y(pdf.get_y() + 40)

    elif "number patterns" in clean_sub:
        pdf.cell(0, 10, f" Directions: Find the rule and complete the number pattern.", ln=True)
        pdf.ln(2)
        y_start = pdf.get_y()
        box_h, gap_y = 32, 6
        for i in range(5):
            y = y_start + i * (box_h + gap_y)
            draw_rounded_box(pdf, 15, y, 185, box_h, r=8, bg_color=theme_colors["box"])
            
            pattern_type = random.choice(["add", "sub", "mul"])
            if pattern_type == "add":
                step = random.randint(10, 50)
                start = random.randint(10, 100)
                seq = [start + (j * step) for j in range(5)]
            elif pattern_type == "sub":
                step = random.randint(5, 20)
                start = random.randint(100, 200)
                seq = [start - (j * step) for j in range(5)]
            else: 
                step = random.choice([2, 3])
                start = random.randint(2, 5)
                seq = [start * (step ** j) for j in range(5)]
            
            hide_idx = random.sample([3, 4], 2) # ซ่อน 2 ตัวท้าย
            
            for j in range(5):
                x = 25 + (j * 32)
                circle_y = y + 4
                if j in hide_idx:
                    val = str(seq[j]) if pdf.is_key else "" 
                    draw_circle_placeholder(pdf, x, circle_y, 24, val)
                else:
                    draw_solid_circle(pdf, x, circle_y, 24, str(seq[j]), font_size=16)
        pdf.set_y(y_start + 5 * (box_h + gap_y))

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
    st.header("🎨 ตกแต่งใบงาน (Customize)")
    
    shop_name = st.text_input("🏪 ชื่อร้าน (Copyright):", value="Kindergarten Learning Press")
    st.markdown("---")
    
    # เพิ่ม Grade 1 และโชว์ Grade 2, Grade 3 มารอไว้ตามสั่งครับ
    grade_level = st.selectbox("📚 1. เลือกระดับชั้น (Grade Level):", [
        "Pre-K", 
        "Grade 1", 
        "Grade 2", 
        "Grade 3 (Coming Soon)"
    ])
    
    # จัดการเมนูย่อยตามระดับชั้นที่เลือก
    if grade_level == "Pre-K":
        main_topic = st.selectbox("🎯 2. เลือกแกนหลัก:", list(PRE_K_CURRICULUM.keys()))
        sub_topic = st.selectbox("📝 3. เลือกกิจกรรม:", PRE_K_CURRICULUM[main_topic])
    elif grade_level == "Grade 1":
        main_topic = st.selectbox("🎯 2. เลือกแกนหลัก:", list(GRADE_1_CURRICULUM.keys()))
        sub_topic = st.selectbox("📝 3. เลือกกิจกรรม:", GRADE_1_CURRICULUM[main_topic])
    elif grade_level == "Grade 2":
        main_topic = st.selectbox("🎯 2. เลือกแกนหลัก:", list(GRADE_2_CURRICULUM.keys()))
        sub_topic = st.selectbox("📝 3. เลือกกิจกรรม:", GRADE_2_CURRICULUM[main_topic])
        
    # ถ้าไม่ใช่ G3 ให้โชว์ปุ่มตั้งค่าต่อ
    # ถ้าไม่ใช่ G3 ให้โชว์ปุ่มตั้งค่าต่อ
    if grade_level in ["Pre-K", "Grade 1", "Grade 2"]:
        theme_choice = st.selectbox("🖌️ 4. โทนสี (Color Palette):", list(THEME_COLORS.keys()))
        selected_colors = THEME_COLORS[theme_choice]
        
        st.markdown("---")
        
        # ปรับตรงนี้: ให้โชว์ตัวเลขเป้าหมายเฉพาะ Pre-K เท่านั้น ถ้าเป็น G1, G2 จะถูกซ่อนอัตโนมัติ
        if grade_level == "Pre-K":
            target_num = st.selectbox("🎯 5. เลือกตัวเลขเป้าหมาย:", list(range(1, 21)))
        else:
            target_num = None # สำหรับ G1, G2 ไม่ต้องมีค่าตัวเลขเป้าหมาย
            
        num_q = st.slider("📝 6. จำนวนข้อต่อหน้า:", min_value=2, max_value=8, value=3)
        
        st.markdown("---")
        generate_btn = st.button("🚀 สร้างโครงร่าง (Generate PDF)", use_container_width=True)
    else:
        st.info(f"🚧 ระบบกำลังพัฒนาเนื้อหาสำหรับ {grade_level} ครับ!")
        generate_btn = False

# ==========================================
# 5. พรีวิวด้วย PyMuPDF (ถ้ายังไม่มี ให้ใส่ไว้บนสุดก่อนส่วน UI)
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
# 6. ส่วนประมวลผลเมื่อกดปุ่ม Generate (วางไว้ล่างสุดของไฟล์)
# ==========================================
if generate_btn:
    # 1. กำหนด session_seed ก่อนเรียกใช้ฟังก์ชัน (ป้องกัน NameError)
    session_seed = random.randint(1, 9999999)
    
    with st.spinner(f"กำลังสร้างใบงานแบบ Dynamic โฟกัสเลข {target_num}..."):
        # 2. เรียกใช้งานทีละ 2 ชุด (โจทย์ และ เฉลย)
        ws_bytes = generate_worksheet(sub_topic, selected_colors, num_q, shop_name, target_num, session_seed, is_key=False)
        ans_bytes = generate_worksheet(sub_topic, selected_colors, num_q, shop_name, target_num, session_seed, is_key=True)

        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            display_pdf_preview(ws_bytes)
            
        with col2:
            st.subheader(f"📥 ดาวน์โหลดไฟล์")
            st.success(f"✅ สร้างใบงานสำเร็จ! เลย์เอาต์พร้อมสำหรับการใส่ภาพจาก Nano Banana")
            
            # จัดการชื่อไฟล์ให้สวยงาม
            clean_level = grade_level.replace(" ", "")
            file_title = sub_topic.split('. ')[-1].replace(' ', '_')
            
            st.download_button(
                label=f"📄 โหลดโครงร่าง (Worksheet)",
                data=ws_bytes,
                file_name=f"{clean_level}_{file_title}_Num_{target_num}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.download_button(
                label=f"🔑 โหลดเฉลย (Answer Key)",
                data=ans_bytes,
                file_name=f"{clean_level}_{file_title}_Num_{target_num}_KEY.pdf",
                mime="application/pdf",
                use_container_width=True
            )

elif grade_level in ["Pre-K", "Grade 1"]:
    st.info("👈 กรุณาเลือก **กิจกรรมและตัวเลขที่ต้องการ** แล้วกดปุ่มสร้างใบงานได้เลยครับ มีพื้นที่ให้ตกแต่งภาพรอไว้เพียบ!")
