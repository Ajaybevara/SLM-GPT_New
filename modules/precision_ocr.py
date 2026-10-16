# modules/precision_ocr.py
import streamlit as st
import os
import io
import pymupdf as fitz
from PIL import Image
import markdown
from xhtml2pdf import pisa
from docx import Document
from docx.shared import Pt
import re

# Import from your upgraded db_utils
from database.db_utils import save_chat_message, archive_document
from modules.local_models import models_configured, vision_complete

def convert_pdf_to_images(uploaded_file):
    """Converts a multi-page PDF into a list of PIL Images."""
    images = []
    pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

def clean_markdown(raw_text):
    """Removes AI code block artifacts from the output."""
    text = raw_text.strip()
    if text.startswith("```markdown"):
        text = text[11:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def calculate_confidence(text):
    """SaaS Validation: Analyzes the structural integrity of the extraction."""
    score = 100
    if "|" in text and text.count("|") < 4: 
        score -= 20 # Penalize broken tables
    if "**: " not in text and text.count("**") < 2: 
        score -= 15 # Penalize missing metadata pairs
    return max(0, score)

def classify_doc_type(images):
    """SaaS Pre-processor: Identifies the document type."""
    try:
        prompt = "Classify this document: INVOICE, MEDICAL_FORM, LEGAL_CONTRACT, GOVERNMENT_ID, or GENERAL. Return ONLY the category name."
        return vision_complete(prompt, [images[0]]).strip().upper()
    except:
        return "GENERAL"

def generate_word_from_markdown(md_text):
    """Bulletproof Word Export with XML Safety."""
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(10)

    lines = md_text.split('\n')
    table_data = []
    in_table = False

    for i, line in enumerate(lines):
        strip_line = line.strip()
        
        if strip_line.startswith('|'):
            if '---' in strip_line: 
                continue
            cells = [c.strip() for c in strip_line.strip('|').split('|')]
            if cells:
                table_data.append(cells)
                in_table = True
            if i != len(lines) - 1:
                continue

        if in_table and (not strip_line.startswith('|') or i == len(lines) - 1):
            if table_data:
                try:
                    max_cols = max(len(row) for row in table_data)
                    table = doc.add_table(rows=len(table_data), cols=max_cols)
                    table.style = 'Table Grid'
                    
                    for r_idx, row_data in enumerate(table_data):
                        for c_idx in range(max_cols):
                            val = row_data[c_idx] if c_idx < len(row_data) else ""
                            table.cell(r_idx, c_idx).text = str(val)
                    doc.add_paragraph("") 
                except Exception:
                    for row in table_data:
                        doc.add_paragraph(" | ".join(row))
                table_data = []
                in_table = False

        if not in_table and strip_line and not strip_line.startswith('|'):
            p = doc.add_paragraph()
            if '**' in strip_line:
                parts = strip_line.split('**')
                for idx, pt in enumerate(parts):
                    run = p.add_run(pt)
                    if idx % 2 == 1: 
                        run.bold = True
            else:
                p.add_run(strip_line)

    file_stream = io.BytesIO()
    doc.save(file_stream)
    return file_stream.getvalue()

def generate_pdf_from_markdown(md_text):
    """Your Custom PDF logic with dynamic A4 sizing."""
    html_content = markdown.markdown(md_text, extensions=['tables', 'sane_lists'])
    
    max_columns = 0
    for line in md_text.split('\n'):
        if line.strip().startswith('|'):
            cols = line.count('|') - 1 
            if cols > max_columns:
                max_columns = cols
                
    page_layout = "A4 landscape" if max_columns >= 4 else "A4 portrait"
    
    styled_html = f"""
    <html>
    <head>
    <style>
        @page {{ 
            size: {page_layout}; 
            margin: 2cm 1.5cm 1.5cm 1.5cm;
        }}
        body {{ 
            font-family: Helvetica, Arial, sans-serif; 
            font-size: 10px; 
            line-height: 1.5; 
            color: #000; 
        }}
        .first-line {{ margin-top: 20px; font-weight: bold; font-size: 14px; text-align: center; margin-bottom: 15px; }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            margin-top: 15px;
            margin-bottom: 25px; 
        }}
        th, td {{ 
            border: 1px solid #000; 
            padding: 6px; 
            vertical-align: top; 
        }}
        th {{ background-color: #f2f2f2; }}
        p {{ margin-bottom: 5px; }}
    </style>
    </head>
    <body>
        <div class="first-line">DOCUMENT EXTRACTION</div>
        {html_content}
    </body>
    </html>
    """
    result_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(styled_html), dest=result_file)
    return result_file.getvalue() if not pisa_status.err else None


def render_ocr_app():
    st.header("📄 Precision OCR & Universal Extraction")
    
    if not models_configured():
        st.error("Local model configuration is missing. Please configure VLLM_API_BASE and VLLM_MODEL in .env.")
        return

    # User ID check for SaaS logic
    user_id = st.session_state.get("user_id", 1) # Fallback to 1 if testing without login
    if 'ocr_result' not in st.session_state: 
        st.session_state.ocr_result = None

    with st.sidebar:
        st.subheader("🌐 Output Options")
        target_language = st.selectbox("Output Language", ["Keep Original", "English", "Hindi", "Spanish", "Telugu"])
        st.divider()
        st.subheader("📤 Upload Document")
        uploaded_file = st.file_uploader("Upload Medical Form / Scanned PDF", type=["png", "jpg", "jpeg", "pdf"])
        process_btn = st.button("Extract & Reconstruct", use_container_width=True)

    if process_btn:
        if not uploaded_file:
            st.warning("Please upload a file.")
        else:
            with st.spinner("Analyzing document layout and translating handwriting..."):
                try:
                    images_to_process = convert_pdf_to_images(uploaded_file) if uploaded_file.name.lower().endswith(".pdf") else [Image.open(uploaded_file)]
                    
                    # AI Pre-processing
                    doc_category = classify_doc_type(images_to_process)
                    st.toast(f"Detected Document Type: {doc_category}", icon="🔍")

                    lang_inst = f"Translate the final output to {target_language}." if target_language != "Keep Original" else "Keep the text in its original language."
                    
                    # Your Exact Master Prompt
                    sys_prompt = f"""
                    You are an elite Data Extraction AI. Reconstruct this {doc_category} document perfectly in strict Markdown.
                    Process the document logically from top to bottom.
                    
                    CRITICAL INSTRUCTIONS:
                    Before extracting, identify the layout zones. You must decide the format based on the visual structure if its form then capture in tabluar way all form data:

                    1. METADATA & FORM FIELDS: Do not ignore text outside of tables. Capture all info, dates, and standalone fields at the top/bottom. Format them cleanly as bold key-value pairs (e.g., **Field Name:** Value). Use line breaks, do not squash them into one line.
                    2. MULTIPLE TABLES: If there are multiple separate grids/tables on the page, you MUST output them as separate Markdown tables. Do not miss any.
                    3. SEPARATOR ROW: You MUST include the Markdown separator row (e.g., |---|---|---|) immediately after every table header.
                    4. CHECKBOXES: Use [ ] for an empty box and [x] for a ticked/checked box. Ensure the label is adjacent.
                    5. HANDWRITING: Transcribe handwritten notes directly into their corresponding physical location (whether in a paragraph or a specific table cell).
                    6. NO FILLER: Output ONLY the Markdown code.
                    7. look for overwriting texts and capture according to flow of doc if handwritten thing is ontop of something else tye to extract 
                    8. look if its a form based input then make sure u provide form based out in structured format to export in better form way, if its tablualr then tabluar as mentioend above, and if its normal then normal.
                    
                    {lang_inst}
                    """
                    
                    page_outputs = []
                    for page_number, page_image in enumerate(images_to_process, start=1):
                        page_text = vision_complete(sys_prompt, [page_image])
                        if len(images_to_process) > 1:
                            page_outputs.append(f"## Page {page_number}\n\n{page_text}")
                        else:
                            page_outputs.append(page_text)
                    cleaned_output = clean_markdown("\n\n".join(page_outputs))
                    st.session_state.ocr_result = cleaned_output
                    
                    # SaaS Data Archiving
                    conf_score = calculate_confidence(cleaned_output)
                    archive_document(user_id, uploaded_file.name, doc_category, cleaned_output, conf_score)
                    save_chat_message(user_id, "OCR", "standalone", "user", f"Uploaded: {uploaded_file.name}")
                    
                except Exception as e:
                    st.error(f"Error extracting document: {str(e)}")

    if st.session_state.ocr_result:
        st.success("Extraction Complete & Saved to Vault!")
        
        with st.container(border=True): 
            st.markdown(st.session_state.ocr_result)
            
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="📥 Download Markdown (.md)", 
                data=st.session_state.ocr_result, 
                file_name="extracted_form.md", 
                mime="text/markdown", 
                use_container_width=True
            )
        with col2:
            with st.spinner("Compiling styled PDF..."):
                pdf_bytes = generate_pdf_from_markdown(st.session_state.ocr_result)
                if pdf_bytes: 
                    st.download_button(
                        label="📥 Download Styled PDF (.pdf)", 
                        data=pdf_bytes, 
                        file_name="extracted_form.pdf", 
                        mime="application/pdf", 
                        use_container_width=True
                    )
                else:
                    st.error("PDF Compilation Failed.")
        with col3:
            word_bytes = generate_word_from_markdown(st.session_state.ocr_result)
            st.download_button(
                label="📥 Download Word (.docx)",
                data=word_bytes,
                file_name="reconstructed_form.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
