import streamlit as st
from fpdf import FPDF

# ==========================================
# 1. ฐานข้อมูลหลักสูตร Pre-K (4 หลัก x 8 ย่อย)
# ==========================================
PRE_K_CURRICULUM = {
    "1. Number Sense (ความเข้าใจตัวเลข)": [
        "1. Find the Number",
        "2. Trace the Numbers 1-5",
        "3. Counting 1-5",
        "4. Count and Match",
        "5. More or Less?",
        "6. Color by Number",
        "7. Missing Numbers 1-5",
        "8. Number Mazes"
    ],
    "2. Geometry (เรขาคณิต)": [
        "1. Trace Basic Shapes",
        "2. Shape Recognition",
        "3. Match the Shapes",
        "4. Match Shapes to Real Objects",
        "5. Sort the Shapes",
        "6. Color by Shape",
        "7. Big and Small Shapes",
        "8. Draw the Shape"
    ],
    "3. Measurement (การวัด)": [
        "1. Big or Small?",
        "2. Tall or Short?",
        "3. Long or Short?",
        "4. Heavy or Light?",
        "5. Same Size",
        "6. Order by Size",
        "7. Measure with Blocks",
        "8. Which Holds More?"
    ],
    "4. Algebraic Thinking (พีชคณิตเบื้องต้น)": [
        "1. Complete the AB Pattern",
        "2. Complete the AAB Pattern",
        "3. Create Your Own Pattern",
        "4. Sort by Color",
        "5. Sort by Category",
        "6. Same or Different?",
        "7. Spot the Odd One Out",
        "8. Matching Pairs"
    ]
}

# ==========================================
# 2. คลาสสร้างเอกสาร PDF (ขนาด US Letter)
# ==========================================
class MathWorksheetPDF(FPDF):
    def __init__(self, theme_name, title, is_answer_key=False):
        super().__init__(orientation='P', unit='in', format='letter')
        self.theme_name = theme_name
        self.title_text = title
        self.is_answer_key = is_answer_key
        self.set_auto_page_break(auto=True, margin=0.5)

    def header(self):
        # กรอบเอกสารมาตรฐาน
        self.set_line_width(0.05)
        self.set_draw_color(44, 62, 80)
        self.rect(0.25, 0.25, 8.0, 10.5)
        
        self.set_line_width(0.01)
        self.set_draw_color(0, 0, 0)
        self.rect(0.3, 0.3, 7.9, 10.4)

        # ช่องกรอกชื่อ-วันที่
        self.set_font("helvetica", "B", 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 0.5, "Name: _______________________      Date: ______________", ln=True, align="C")
        
        # ชื่อหัวข้อกิจกรรม
        self.set_font("helvetica", "B", 16)
        clean_title = self.title_text.split(". ", 1)[-1] if ". " in self.title_text else self.title_text
        display_title = f"{clean_title} ({self.theme_name})"
        
        if self.is_answer_key:
            display_title += " - KEY"
            self.set_text_color(220, 20, 60)
            
        self.cell(0, 0.4, display_title, ln=True, align="C")
        self.ln(0.2)

# ==========================================
# 3. ฟังก์ชันจัด Layout อัตโนมัติตามหัวข้อ
# ==========================================
def generate_pdf_layout(main_topic, sub_topic, theme, num_q, is_key=False):
    pdf = MathWorksheetPDF(theme, sub_topic, is_key)
    pdf.add_page()
    pdf.set_font("helvetica", "", 12)
    
    clean_sub = sub_topic.lower()
    
    # ---------------------------------------------------------
    # Layout 1: เปรียบเทียบ (Measurement / Comparisons)
    # ---------------------------------------------------------
    if any(k in clean_sub for k in ["big", "tall", "long", "heavy", "more", "different", "odd"]):
        pdf.cell(0, 0.3, "Directions: Compare the pictures and circle the correct answer.", ln=True)
        pdf.ln(0.3)
        for i in range(num_q):
            if pdf.get_y() > 8.5: pdf.add_page()
            
            pdf.set_fill_color(245, 245, 245)
            # กล่องซ้าย
            pdf.rect(1.0, pdf.get_y(), 2.5, 1.5, style='FD')
            pdf.text(1.2, pdf.get_y() + 0.8, f"[ {theme} A ]")
            # คำว่า OR
            pdf.set_font("helvetica", "B", 12)
            pdf.text(4.0, pdf.get_y() + 0.8, "VS")
            pdf.set_font("helvetica", "", 12)
            # กล่องขวา
            pdf.rect(4.8, pdf.get_y(), 2.5, 1.5, style='FD')
            pdf.text(5.0, pdf.get_y() + 0.8, f"[ {theme} B ]")
            
            pdf.ln(1.8)

    # ---------------------------------------------------------
    # Layout 2: อนุกรมและลวดลาย (Patterns)
    # ---------------------------------------------------------
    elif "pattern" in clean_sub:
        pdf.cell(0, 0.3, "Directions: Look at the pattern. Draw what comes next.", ln=True)
        pdf.ln(0.3)
        for i in range(num_q):
            if pdf.get_y() > 8.5: pdf.add_page()
            
            for col in range(4):
                pdf.rect(1.0 + (col * 1.3), pdf.get_y(), 1.0, 1.0, style='D')
                pdf.text(1.1 + (col * 1.3), pdf.get_y() + 0.6, "Item")
                
            # กล่องคำตอบ (เส้นประ/เส้นหนา)
            pdf.set_line_width(0.03)
            pdf.rect(1.0 + (4 * 1.3), pdf.get_y(), 1.0, 1.0, style='D')
            pdf.text(1.1 + (4 * 1.3), pdf.get_y() + 0.6, "Next?")
            pdf.set_line_width(0.01)
            
            pdf.ln(1.4)

    # ---------------------------------------------------------
    # Layout 3: นับจำนวนและวาด/เขียน (Counting / Matching)
    # ---------------------------------------------------------
    elif any(k in clean_sub for k in ["count", "match", "how many", "number"]):
        pdf.cell(0, 0.3, f"Directions: Count the {theme.lower()} and write or match.", ln=True)
        pdf.ln(0.3)
        for i in range(num_q):
            if pdf.get_y() > 8.5: pdf.add_page()
            
            # กล่องโจทย์กว้างๆ
            pdf.set_fill_color(240, 248, 255)
            pdf.rect(1.0, pdf.get_y(), 4.5, 1.5, style='FD')
            pdf.text(2.0, pdf.get_y() + 0.8, f"[ Place 1-5 {theme} Here ]")
            
            # กล่องคำตอบ
            pdf.rect(6.0, pdf.get_y() + 0.2, 1.0, 1.0, style='D')
            pdf.text(6.1, pdf.get_y() + 0.8, "Ans")
            
            pdf.ln(1.8)

    # ---------------------------------------------------------
    # Layout 4: รูปทรงและฝึกเขียน (Tracing / Shapes / General)
    # ---------------------------------------------------------
    else:
        pdf.cell(0, 0.3, "Directions: Follow the instructions to complete the activity.", ln=True)
        pdf.ln(0.3)
        for i in range(num_q):
            if pdf.get_y() > 8.5: pdf.add_page()
            
            pdf.rect(1.0, pdf.get_y(), 6.5, 1.8, style='D')
            pdf.set_font("helvetica", "I", 10)
            pdf.text(1.2, pdf.get_y() + 0.9, f"[ Place {theme} Activity / Traceable Items Here ]")
            pdf.set_font("helvetica", "", 12)
            
            pdf.ln(2.1)

    if is_key:
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 0.3, "Note for Teachers:", ln=True)
        pdf.set_font("helvetica", "", 12)
        pdf.multi_cell(0, 0.3, "Since this is a visual worksheet, answers will depend on the clip art you insert. Please fill in the correct answers/lines in red before saving the final PDF for your customers.")

    return bytes(pdf.output(dest='S'))

# ==========================================
# 4. Streamlit UI (มี Sidebar คัดกรองหัวข้อ)
# ==========================================
st.set_page_config(page_title="TpT Pre-K Generator", page_icon="🧸", layout="wide")

st.title("🧸 TpT Worksheet Generator (Pre-K Edition)")
st.markdown("ระบบวางโครงสร้างใบงานเตรียมอนุบาล (3-4 ขวบ) 32 รูปแบบ ตามมาตรฐาน US Common Core พร้อม Placeholder สำหรับ Nano Banana")

with st.sidebar:
    st.header("⚙️ การตั้งค่าใบงาน")
    
    st.markdown("**ระดับชั้น:** Pre-K (เตรียมอนุบาล)")
    
    # 1. เลือกหมวดหลัก
    main_topic = st.selectbox("📌 1. เลือกหมวดหลักคณิตศาสตร์", list(PRE_K_CURRICULUM.keys()))
    
    # 2. เลือกหมวดย่อยแบบสัมพันธ์กับหมวดหลัก
    sub_topic = st.selectbox("🎯 2. เลือกประเภทใบงาน", PRE_K_CURRICULUM[main_topic])
    
    # 3. ธีมและจำนวนข้อ
    theme = st.selectbox("🎨 3. ธีมภาพประกอบ (Theme)", ["Animals", "Space", "Dinosaurs", "Underwater", "Monsters"])
    num_questions = st.slider("🔢 4. จำนวนข้อต่อหน้า", min_value=2, max_value=6, value=4, help="Pre-K ควรมีข้อไม่เยอะ เพื่อให้รูปภาพมีขนาดใหญ่ สังเกตง่าย")
    
    generate_btn = st.button("🚀 สร้างโครงร่าง PDF", use_container_width=True)

# Processing
if generate_btn:
    with st.spinner("กำลังสร้างเอกสาร Layout ขั้นสูง..."):
        
        # เจน PDF โจทย์ และ เฉลย
        worksheet_pdf = generate_pdf_layout(main_topic, sub_topic, theme, num_questions, is_key=False)
        answer_pdf = generate_pdf_layout(main_topic, sub_topic, theme, num_questions, is_key=True)
        
        st.success("✅ สร้างโครงสร้างใบงานสำเร็จ! โปรแกรมได้วิเคราะห์เลย์เอาต์ให้เข้ากับหัวข้ออัตโนมัติ")
        
        # พรีวิวข้อมูล
        st.info(f"**กำลังสร้าง:** {sub_topic} | **เลย์เอาต์จัดให้แบบ:** ไดนามิก (ปรับตามคีย์เวิร์ดกิจกรรม)")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 ดาวน์โหลดใบงาน (Worksheet PDF)",
                data=worksheet_pdf,
                file_name=f"PreK_{theme}_{sub_topic.split('. ')[-1].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with col2:
            st.download_button(
                label="🔑 ดาวน์โหลดเฉลย (Answer Key PDF)",
                data=answer_pdf,
                file_name=f"PreK_{theme}_{sub_topic.split('. ')[-1].replace(' ', '_')}_KEY.pdf",
                mime="application/pdf",
                use_container_width=True
            )
