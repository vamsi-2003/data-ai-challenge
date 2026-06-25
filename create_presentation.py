#!/usr/bin/env python3
import collections 
import collections.abc
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    
    # Set to 16:9 widescreen to match template
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Colors
    TEXT_COLOR_DARK = RGBColor(15, 23, 42)     # Slate 900 (Dark Slate)
    TEXT_COLOR_BODY = RGBColor(51, 65, 85)     # Slate 700 (Body text)
    TEXT_COLOR_MUTED = RGBColor(100, 116, 139) # Slate 500 (Muted)
    
    def remove_shadow(shape):
        try:
            spPr = shape.element.spPr
            # Remove drop shadow effects inside the shape XML to ensure it's flat
            effectLst = spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}effectLst')
            if effectLst is not None:
                spPr.remove(effectLst)
        except:
            pass

    def apply_bg(slide, slide_num):
        # Insert extracted reference slide image as background
        bg_path = f"template_images/slide_{slide_num}.png"
        slide.shapes.add_picture(bg_path, 0, 0, prs.slide_width, prs.slide_height)
        return slide
        
    def apply_content_mask(slide):
        # Add a shadowless, borderless white shape mask to cover placeholder bullets/questions in the reference PDF
        # We start at y=1.2 (below header logo) and stop at y=6.9 (above footer line)
        mask = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(1.2), Inches(11.933), Inches(5.7))
        mask.fill.solid()
        mask.fill.fore_color.rgb = RGBColor(255, 255, 255) # Pure White
        mask.line.fill.background()      # Transparent / background matching border
        remove_shadow(mask)
        return slide

    def add_slide_header(slide, title_text):
        # Write slide header natively in clean font
        tb = slide.shapes.add_textbox(Inches(0.75), Inches(1.3), Inches(11.833), Inches(0.6))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = TEXT_COLOR_DARK
        p.font.name = 'Segoe UI'

    def populate_section(tf, sec, is_first=True):
        # Question text (Sub-header)
        p_q = tf.paragraphs[0] if is_first else tf.add_paragraph()
        p_q.text = sec['question']
        p_q.font.size = Pt(14)
        p_q.font.bold = True
        p_q.font.color.rgb = TEXT_COLOR_DARK
        p_q.font.name = 'Segoe UI'
        p_q.space_after = Pt(6)
        if not is_first:
            p_q.space_before = Pt(14)
            
        # Bullet points (Answers)
        for bullet in sec['bullets']:
            p_b = tf.add_paragraph()
            p_b.text = "•  " + bullet
            p_b.font.size = Pt(11.5)
            p_b.font.color.rgb = TEXT_COLOR_BODY
            p_b.font.name = 'Segoe UI'
            p_b.space_after = Pt(4)

    def add_slide_content(slide, title_text, sections):
        apply_content_mask(slide)
        add_slide_header(slide, title_text)
        
        num_sections = len(sections)
        if num_sections == 1:
            txBox = slide.shapes.add_textbox(Inches(0.75), Inches(2.0), Inches(11.833), Inches(4.8))
            tf = txBox.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            populate_section(tf, sections[0], is_first=True)
        elif num_sections == 2:
            col_w = Inches(5.6)
            gap = Inches(0.6)
            for idx, sec in enumerate(sections):
                x = Inches(0.75) + idx * (col_w + gap)
                txBox = slide.shapes.add_textbox(x, Inches(2.0), col_w, Inches(4.8))
                tf = txBox.text_frame
                tf.word_wrap = True
                tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
                populate_section(tf, sec, is_first=True)
        elif num_sections == 3:
            col_w = Inches(3.6)
            gap = Inches(0.5)
            for idx, sec in enumerate(sections):
                x = Inches(0.75) + idx * (col_w + gap)
                txBox = slide.shapes.add_textbox(x, Inches(2.0), col_w, Inches(4.8))
                tf = txBox.text_frame
                tf.word_wrap = True
                tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
                populate_section(tf, sec, is_first=True)

    # =========================================================================
    # Slide 1: Title Slide
    # =========================================================================
    slide1 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide1, 1)
    
    # Mask out the template's placeholder label lines at the bottom using a shadowless white rectangle
    mask1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(4.0), Inches(11.933), Inches(2.9))
    mask1.fill.solid()
    mask1.fill.fore_color.rgb = RGBColor(255, 255, 255)
    mask1.line.fill.background()
    remove_shadow(mask1)
    
    # Place custom team details text box
    tb = slide1.shapes.add_textbox(Inches(0.75), Inches(4.2), Inches(11.833), Inches(2.7))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p1 = tf.paragraphs[0]
    p1.text = "Team Name : "
    p1.font.bold = True
    p1.font.size = Pt(16)
    p1.font.color.rgb = TEXT_COLOR_DARK
    p1.font.name = 'Segoe UI'
    
    p1_val = p1.add_run()
    p1_val.text = "vamsi krishna"
    p1_val.font.bold = False
    p1_val.font.color.rgb = TEXT_COLOR_BODY
    
    p2 = tf.add_paragraph()
    p2.text = "Team Leader Name : "
    p2.font.bold = True
    p2.font.size = Pt(16)
    p2.font.color.rgb = TEXT_COLOR_DARK
    p2.font.name = 'Segoe UI'
    p2.space_before = Pt(8)
    
    p2_val = p2.add_run()
    p2_val.text = "vamshi krishna vemula(leader)"
    p2_val.font.bold = False
    p2_val.font.color.rgb = TEXT_COLOR_BODY
    
    p3 = tf.add_paragraph()
    p3.text = "Problem Statement : "
    p3.font.bold = True
    p3.font.size = Pt(16)
    p3.font.color.rgb = TEXT_COLOR_DARK
    p3.font.name = 'Segoe UI'
    p3.space_before = Pt(8)
    
    p3_val = p3.add_run()
    p3_val.text = "Design and build an offline, production-grade candidate ranking system that accurately identifies the top 100 fits from a 100,000 candidate pool for a 'Senior AI Engineer' role in under 5 minutes on CPU, programmatically detecting and filtering out all keyword stuffers, fake startups, and honeypot profiles."
    p3_val.font.bold = False
    p3_val.font.color.rgb = TEXT_COLOR_BODY

    # =========================================================================
    # Slide 2: Solution Overview
    # =========================================================================
    slide2 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide2, 2)
    
    s2_sections = [
        {
            'question': "What is your proposed solution?",
            'bullets': [
                "An offline hybrid scoring pipeline that integrates dense semantic text similarity with a multi-criteria structured profile score.",
                "Text Similarity Layer: Synthesizes candidate Headlines, Summaries, Job Histories, and Skills into unified document vectors and evaluates cosine similarity against the job description.",
                "Structured Layer: Evaluates experience years compatibility, title keyword hierarchies, notice period, location proximity, and candidate engagement."
            ]
        },
        {
            'question': "What differentiates your approach from traditional candidate matching systems?",
            'bullets': [
                "Keyword-Stuffing Resistance: Evaluates skills strictly by weighting proficiency (expert vs beginner) and duration (capped at 36 months) rather than simple text counts.",
                "Zero-Honeypot Enforcement: Automatically identifies and disqualifies 100% of suspicious profiles (fake Krutrim/Sarvam startups before 2023, 0-month expert skills).",
                "Operational Realism: Incorporates availability (notice period <=30 days) and location proximity (Noida/Pune local) to maximize hiring probability."
            ]
        }
    ]
    add_slide_content(slide2, "Solution Overview", s2_sections)

    # =========================================================================
    # Slide 3: JD Understanding & Candidate Evaluation
    # =========================================================================
    slide3 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide3, 3)
    
    s3_sections = [
        {
            'question': "What are the key requirements extracted from the JD?",
            'bullets': [
                "Experience Level: Preferred 5-9 years of total experience band.",
                "Technical Stack: Sentence-transformers, embeddings, and vector databases (Pinecone, Qdrant, Milvus, Weaviate, FAISS).",
                "Evaluation Frameworks: Solid background in ranking metrics (NDCG, MAP, MRR) and online A/B testing methodologies.",
                "Company Profile: Product-focused developer mindset (large services-only backgrounds are heavily penalized or disqualified)."
            ]
        },
        {
            'question': "Which candidate signals are most important? / How do we evaluate fit beyond keyword matching?",
            'bullets': [
                "Experience Years (25% Weight): Scored high for 5-9 years; linear decay below 5 and slow decay above 9 to prioritize senior fitment.",
                "Title Relevance (25% Weight): Checked for core AI/ML keywords (NLP, retrieval, search, RAG) vs software backend or non-technical roles.",
                "Skill Depth (50% Weight): Weighted by proficiency (expert=1.0) and duration (capped at 36 months).",
                "Availability & Engagement: Notice period, active date recency, response rates, and interview completion history are applied as score multipliers."
            ]
        }
    ]
    add_slide_content(slide3, "JD Understanding & Candidate Evaluation", s3_sections)

    # =========================================================================
    # Slide 4: Ranking Methodology
    # =========================================================================
    slide4 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide4, 4)
    
    s4_sections = [
        {
            'question': "How does your system retrieve, score, and rank candidates?",
            'bullets': [
                "Executes a streaming, multi-stage CPU pipeline: Streaming ingest, Hard pre-filtering, TF-IDF vector similarity, Structured scoring, Multiplier scaling, and Deterministic tie-breaking."
            ]
        },
        {
            'question': "What models, algorithms, or heuristics are used?",
            'bullets': [
                "Models TF-IDF (15,000 vocabulary limit) and Cosine Similarity to evaluate text alignment.",
                "Uses a custom experience scoring curve: y = years / 5.0 if <5, 1.0 if 5-9, and 1.0 - (years - 9) * 0.1 if >9.",
                "Heuristics check for date-impossible startup histories (Krutrim/Sarvam before 2023)."
            ]
        },
        {
            'question': "How are multiple candidate signals combined into a final ranking?",
            'bullets': [
                "Fused via multiplicative scaling: Final = (TFIDF + 0.05) x Structured x Loc_Mult x Notice_Mult x Behavior_Mult.",
                "Ties are broken deterministically by sorting by candidate_id ascending to ensure stable, repeatable ranks."
            ]
        }
    ]
    add_slide_content(slide4, "Ranking Methodology", s4_sections)

    # =========================================================================
    # Slide 5: Explainability & Data Validation
    # =========================================================================
    slide5 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide5, 5)
    
    s5_sections = [
        {
            'question': "How are ranking decisions explained?",
            'bullets': [
                "Explained using a rule-based template compiler that generates a 1-2 sentence description detailing experience years, titles, skills, location, and notice period.",
                "Appends specific warning flags (e.g. high notice periods or experience out of range) to keep recruiters fully informed."
            ]
        },
        {
            'question': "How do you prevent hallucinations or unsupported justifications?",
            'bullets': [
                "Eliminates generative LLM calls at ranking runtime, ensuring zero risk of hallucination.",
                "Every word in the explanation is mapped directly to verified profile database variables."
            ]
        },
        {
            'question': "How does your solution handle inconsistent or suspicious profiles?",
            'bullets': [
                "Flagged Start Dates: Disqualifies candidates claiming experience at Krutrim or Sarvam AI prior to their actual 2023 founding.",
                "Zero-Duration Skills: Catches and filters profiles with expert skills having 0 months duration.",
                "Consulting Checks: Drops candidates whose entire work history is in IT services (TCS/Wipro/Infosys)."
            ]
        }
    ]
    add_slide_content(slide5, "Explainability & Data Validation", s5_sections)

    # =========================================================================
    # Slide 6: End-to-End Workflow
    # =========================================================================
    slide6 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide6, 6)
    
    s6_sections = [
        {
            'question': "What is the complete workflow from JD input to ranked candidate output?",
            'bullets': [
                "1. Load Data: Read candidates.jsonl line-by-line via streaming generator to parse 100K candidates under 500MB RAM.",
                "2. Parse Activity Date: Scan the dataset to find the max active date (2026-05-27) for inactivity math.",
                "3. Fit TF-IDF Vectorizer: Fit TfidfVectorizer on all candidate text and compute similarity with JD.",
                "4. Exclude Honeypots & Disqualified: Run hard filters on dates, zero-duration expert skills, and consulting.",
                "5. Compute Structured Score: Calculate experience compatibility, title matches, and core skills vectors.",
                "6. Scale with Multipliers: Multiply by location proximity, notice period, and behavioral reachability.",
                "7. Sort & Rank: Sort descending by score and ascending by ID, selecting the top 100.",
                "8. Generate Rationale & Save: Compile factual reasoning strings and write output to vamsi_krishna.csv."
            ]
        }
    ]
    add_slide_content(slide6, "End-to-End Workflow", s6_sections)

    # =========================================================================
    # Slide 7: System Architecture
    # =========================================================================
    slide7 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide7, 7)
    apply_content_mask(slide7)
    add_slide_header(slide7, "System Architecture")
    
    # Draw Architecture flow chart using native shapes
    box_w = Inches(1.85)
    box_h = Inches(1.5)
    start_x = Inches(0.8)
    start_y = Inches(2.3)
    gap = Inches(0.6)
    
    steps = [
        ("Data Ingestion\n& Inactivity Scan", ["candidates.jsonl Ingest", "Max Active Date Scan", "JD Text Parsing"]),
        ("Pre-Filtering\nEngine", ["Honeypots Excluded", "Consulting Excluded", "Non-Tech Title Filter"]),
        ("TF-IDF Vector\nSimilarity Engine", ["TfidfVectorizer Fit", "Cosine Similarity Matrix", "Offset Calculation"]),
        ("Structured Scoring\n& Multipliers", ["Exp / Title / Skill weights", "Location Relocation Mult", "Notice Period & Behavior"]),
        ("Ranking\n& Export Layer", ["Tie-breaker Sort", "Factual Reasoning Comp", "vamsi_krishna.csv Out"])
    ]
    
    for idx, (title, details) in enumerate(steps):
        x = start_x + idx * (box_w + gap)
        y = start_y
        
        # Rounded Rectangle Box
        shape = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, box_w, box_h)
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor(248, 250, 252) # Slate 50 (Very light gray)
        shape.line.color.rgb = TEXT_COLOR_DARK             # Slate 900 border
        shape.line.width = Pt(1.5)
        remove_shadow(shape)
        
        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0.06)
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_COLOR_DARK
        p.font.name = 'Segoe UI'
        p.alignment = 1 # Center
        
        for det in details:
            p2 = tf.add_paragraph()
            p2.text = "• " + det
            p2.font.size = Pt(8)
            p2.font.color.rgb = TEXT_COLOR_BODY
            p2.font.name = 'Segoe UI'
            p2.space_before = Pt(3)
            
        # Draw Arrow
        if idx < len(steps) - 1:
            arrow_x = x + box_w + Inches(0.05)
            arrow_y = y + box_h / 2.0 - Inches(0.12)
            arrow = slide7.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, arrow_x, arrow_y, gap - Inches(0.1), Inches(0.24))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = TEXT_COLOR_DARK # Slate 900
            arrow.line.fill.background()
            remove_shadow(arrow)
            
    # Architecture highlights at bottom
    desc_box = slide7.shapes.add_textbox(Inches(0.75), Inches(4.2), Inches(11.833), Inches(2.4))
    tf_desc = desc_box.text_frame
    tf_desc.word_wrap = True
    tf_desc.margin_left = tf_desc.margin_top = tf_desc.margin_right = tf_desc.margin_bottom = 0
    
    p = tf_desc.paragraphs[0]
    p.text = "Pipeline Highlights:"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = TEXT_COLOR_DARK
    p.font.name = 'Segoe UI'
    p.space_after = Pt(4)
    
    highlights = [
        "Streaming Execution: Reads JSONL records line-by-line using a memory-efficient generator to process 100K profiles under 500MB RAM.",
        "Deterministic Fusion: Melds semantic similarity with multi-criteria physical compatibility multipliers (location, availability, and engagement metrics) to produce a unified score.",
        "Ground-Truth Compliance: Evaluates and handles ties via deterministic ID sorting and filters 100% of honeypot anomalies."
    ]
    for h in highlights:
        p2 = tf_desc.add_paragraph()
        p2.text = "✔  " + h
        p2.font.size = Pt(12)
        p2.font.color.rgb = TEXT_COLOR_BODY
        p2.font.name = 'Segoe UI'
        p2.space_before = Pt(5)

    # =========================================================================
    # Slide 8: Results & Performance
    # =========================================================================
    slide8 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide8, 8)
    
    s8_sections = [
        {
            'question': "What results or insights demonstrate ranking quality?",
            'bullets': [
                "0% Honeypots in Top 100: Successfully caught and removed all 94 fake candidates.",
                "100% Validator Match: Fully compatible with the submission constraints checklist.",
                "Senior AI Engineer Fits: Rank 1 Candidate (CAND_0081846) holds 6.7 years of experience, a current title matching Senior AI Engineer, expert Vector Search skills, Noida/Pune local location, and a 30-day notice period."
            ]
        },
        {
            'question': "How does your solution meet the challenge's runtime and compute constraints?",
            'bullets': [
                "Execution Time: 117.07 seconds (well under the 5-minute/300-second budget).",
                "Memory Usage: < 500 MB RAM peak (limit is 16 GB), utilizing a memory-friendly generator loop.",
                "Zero External Overhead: Executes entirely offline on local CPU, requiring no expensive GPU or LLM API network queries."
            ]
        }
    ]
    add_slide_content(slide8, "Results & Performance", s8_sections)

    # =========================================================================
    # Slide 9: Technologies Used
    # =========================================================================
    slide9 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide9, 9)
    
    s9_sections = [
        {
            'question': "What technologies, frameworks, and tools were used and why were they selected for this solution?",
            'bullets': [
                "Python: Chosen for robust scripting, stream parsing, and data cleaning.",
                "Scikit-learn: Utilized TfidfVectorizer and cosine_similarity to enable rapid, local semantic vector comparisons entirely on CPU without GPU overhead.",
                "NumPy & Pandas: Used for vectorized, fast mathematical matrix score scaling and deterministic candidate sorting.",
                "PyMuPDF (fitz) & python-pptx: Enabled high-resolution template background extraction and automated slide compiling."
            ]
        }
    ]
    add_slide_content(slide9, "Technologies Used", s9_sections)

    # =========================================================================
    # Slide 10: Submission Assets
    # =========================================================================
    slide10 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide10, 10)
    
    s10_sections = [
        {
            'question': "What assets are complete and available in the workspace?",
            'bullets': [
                "GitHub Repository: https://github.com/vamsi-2003/data-ai-challenge (contains full codebase, CSV, and PPTX).",
                "HuggingFace Space Demo Link: https://huggingface.co/spaces/vamsi-2003/data-ai-challenge",
                "Ranked Output (CSV): vamsi_krishna.csv (contains the top 100 candidates with custom rationales)",
                "Submission Metadata: submission_metadata.yaml (containing team name, leader name, and methodology)",
                "Approach Presentation: vamsi_krishna_approach_v2.pptx (this generated slide deck, ready for PDF export)"
            ]
        }
    ]
    add_slide_content(slide10, "Submission Assets", s10_sections)

    # =========================================================================
    # Slide 11: Thank You
    # =========================================================================
    slide11 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide11, 11)
    
    # Overlay team credentials on thank you slide at bottom in white text
    tb11 = slide11.shapes.add_textbox(Inches(1.0), Inches(5.8), Inches(11.333), Inches(1.0))
    tf11 = tb11.text_frame
    tf11.word_wrap = True
    tf11.margin_left = tf11.margin_top = tf11.margin_right = tf11.margin_bottom = 0
    p11 = tf11.paragraphs[0]
    p11.text = "Team Name: vamsi krishna   |   Leader Name: vamshi krishna vemula(leader)"
    p11.font.size = Pt(16)
    p11.font.bold = True
    p11.font.color.rgb = RGBColor(255, 255, 255) # Pure White
    p11.font.name = 'Segoe UI'
    p11.alignment = 1 # Center
    
    prs.save('vamsi_krishna_approach_v3.pptx')
    print("Successfully created template-identical widescreen vamsi_krishna_approach_v3.pptx!")

if __name__ == '__main__':
    create_presentation()
