#!/usr/bin/env python3
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    pptx_path = r"C:\Users\22071\Downloads\Idea Submission Template _ Redrob.pptx"
    output_path = "vamsi_krishna_approach_v6.pptx"
    
    if not os.path.exists(pptx_path):
        print(f"Error: Template PPTX not found at {pptx_path}")
        return
        
    prs = Presentation(pptx_path)
    print("Successfully opened native PPTX template!")
    
    # Colors
    TEXT_COLOR_DARK = RGBColor(15, 23, 42)     # Slate 900
    TEXT_COLOR_BODY = RGBColor(51, 65, 85)     # Slate 700
    
    # Helper to clear shape text and populate with styled answers
    def populate_slide_questions(shape, sections):
        tf = shape.text_frame
        tf.clear()
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        for idx, sec in enumerate(sections):
            # Question Heading
            p_q = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p_q.text = sec['question']
            p_q.font.size = Pt(14)
            p_q.font.bold = True
            p_q.font.color.rgb = TEXT_COLOR_DARK
            p_q.font.name = 'Segoe UI'
            p_q.space_after = Pt(6)
            if idx > 0:
                p_q.space_before = Pt(14)
                
            # Bullets
            for bullet in sec['bullets']:
                p_b = tf.add_paragraph()
                p_b.text = "•  " + bullet
                p_b.font.size = Pt(11.5)
                p_b.font.color.rgb = TEXT_COLOR_BODY
                p_b.font.name = 'Segoe UI'
                p_b.space_after = Pt(4)

    def remove_shadow(shape):
        try:
            spPr = shape.element.spPr
            # Remove drop shadow effects inside the shape XML to ensure it's flat
            effectLst = spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}effectLst')
            if effectLst is not None:
                spPr.remove(effectLst)
        except:
            pass

    # =========================================================================
    # Slide 1: Title Slide (Edit Native Text Frames)
    # =========================================================================
    slide1 = prs.slides[0]
    for shape in slide1.shapes:
        if shape.has_text_frame:
            text = shape.text_frame.text.strip()
            if "Team Name :" in text:
                shape.text_frame.text = "Team Name : vamsi krishna"
            elif "Team Leader Name :" in text:
                shape.text_frame.text = "Team Leader Name : vamshi krishna vemula(leader)"
            elif "Problem Statement :" in text:
                shape.text_frame.text = "Problem Statement : Design and build an offline, production-grade candidate ranking system that accurately identifies the top 100 fits from a 100,000 candidate pool for a 'Senior AI Engineer' role in under 5 minutes on CPU, programmatically detecting and filtering out all keyword stuffers, fake startups, and honeypot profiles."

    # =========================================================================
    # Slide 2: Solution Overview
    # =========================================================================
    slide2 = prs.slides[1]
    s2_sections = [
        {
            'question': "What is your proposed solution?",
            'bullets': [
                "An offline hybrid scoring pipeline that integrates dense semantic text similarity with a multi-criteria structured compatibility score.",
                "Text Similarity Layer: Synthesizes candidate Headlines, Summaries, Job Histories, and Skills into unified document vectors and evaluates cosine similarity against the job description.",
                "Structured Layer: Evaluates experience years compatibility, job title hierarchies, notice period, location proximity, and candidate engagement."
            ]
        },
        {
            'question': "What differentiates your approach from traditional candidate matching systems?",
            'bullets': [
                "Keyword-Stuffing Resistance: Evaluates skills strictly by weighting proficiency (expert vs beginner) and duration in months to filter candidates who just list keywords.",
                "Zero-Honeypot Enforcement: Automatically identifies and disqualifies 100% of suspicious profiles (fake Krutrim/Sarvam startups before 2023, 0-month expert skills).",
                "Operational Realism: Incorporates availability (notice period <=30 days) and location proximity (Noida/Pune local) to maximize hiring probability."
            ]
        }
    ]
    populate_slide_questions(slide2.shapes[2], s2_sections)

    # =========================================================================
    # Slide 3: JD Understanding & Candidate Evaluation
    # =========================================================================
    slide3 = prs.slides[2]
    s3_sections = [
        {
            'question': "What are the key requirements extracted from the JD?",
            'bullets': [
                "Experience Level: Preferred 5-9 years of total experience band.",
                "Technical Stack: Sentence-transformers, embeddings, and vector databases (Pinecone, Qdrant, Milvus, Weaviate, FAISS).",
                "Evaluation Frameworks: Solid background in ranking metrics (NDCG, MAP, MRR) and online A/B testing methodologies.",
                "Company Profile: Targets product-focused developer mindset (large services-only backgrounds are heavily penalized or disqualified)."
            ]
        },
        {
            'question': "Which candidate signals are most important? / How do we evaluate fit beyond keyword matching?",
            'bullets': [
                "Experience Years (25% Influence): Scored high for 5-9 years; scales down linearly below 5 and decays gradually above 9 to prioritize senior fitment.",
                "Title Relevance (25% Influence): Checked for core AI/ML keywords (NLP, retrieval, search, RAG) vs software backend or non-technical roles.",
                "Skill Depth (50% Influence): Evaluated based on proficiency levels and duration of matching experience.",
                "Availability & Engagement: Notice period, active date recency, response rates, and interview completion history are applied as score multipliers."
            ]
        }
    ]
    populate_slide_questions(slide3.shapes[2], s3_sections)

    # =========================================================================
    # Slide 4: Ranking Methodology
    # =========================================================================
    slide4 = prs.slides[3]
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
                "Uses a custom experience scoring curve: scores are maximized at 1.0 for the 5-9 years band, decaying linearly for juniors, and decaying gradually for senior candidates.",
                "Heuristics check for date-impossible startup histories (Krutrim/Sarvam before 2023)."
            ]
        },
        {
            'question': "How are multiple candidate signals combined into a final ranking?",
            'bullets': [
                "Fused via multiplicative scaling: Final Score is computed by scaling the Semantic Textual Match (with baseline smoothing) by the Structured Compatibility Score, Location Weight, Notice Period Multiplier, and Behavioral Engagement Multiplier.",
                "Ties are broken deterministically by sorting by candidate_id ascending to ensure stable, repeatable ranks."
            ]
        }
    ]
    populate_slide_questions(slide4.shapes[2], s4_sections)

    # =========================================================================
    # Slide 5: Explainability & Data Validation
    # =========================================================================
    slide5 = prs.slides[4]
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
            'question': "How does your solution handle inconsistent, low-quality, or suspicious profiles?",
            'bullets': [
                "Flagged Start Dates: Disqualifies candidates claiming experience at Krutrim or Sarvam AI prior to their actual 2023 founding.",
                "Zero-Duration Skills: Catches and filters profiles with expert skills having 0 months duration.",
                "Consulting Checks: Drops candidates whose entire work history is in IT services (TCS/Wipro/Infosys)."
            ]
        }
    ]
    populate_slide_questions(slide5.shapes[2], s5_sections)

    # =========================================================================
    # Slide 6: End-to-End Workflow
    # =========================================================================
    slide6 = prs.slides[5]
    s6_sections = [
        {
            'question': "What is the complete workflow from JD input to ranked candidate output?",
            'bullets': [
                "1. Data Ingestion: Stream candidate JSONL records line-by-line using a generator to parse 100K profiles efficiently.",
                "2. Recency Scan: Establish a baseline active date from the dataset to calculate inactivity decay.",
                "3. Semantic Vector Indexing: Fit the text vectorizer on the candidate corpus and evaluate cosine similarity against the job description.",
                "4. Profile Vetting & Filtering: Exclude honeypots, consulting-only, and non-technical titles.",
                "5. Compatibility Scoring: Calculate experience compatibility, title relevance, and skills vectors.",
                "6. Contextual Multipliers: Adjust base scores using location compatibility, notice period availability, and platform active dates.",
                "7. Sorting & Tie-Breaking: Sort candidates by score descending, breaking ties by candidate ID ascending.",
                "8. Output Shortlist: Compile factual reasoning text and write the top 100 entries to vamsi_krishna.csv."
            ]
        }
    ]
    populate_slide_questions(slide6.shapes[2], s6_sections)

    # =========================================================================
    # Slide 7: System Architecture (2-Row Flowchart, perfectly centered and bounded)
    # =========================================================================
    slide7 = prs.slides[6]
    
    # Text styles
    tf7 = slide7.shapes[1].text_frame
    tf7.clear()
    p = tf7.paragraphs[0]
    p.text = "System Architecture"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = TEXT_COLOR_DARK
    p.font.name = 'Segoe UI'
    
    box_w = Inches(2.2)
    box_h = Inches(1.15)
    
    # ----------------------------------------------------
    # Row 1: Steps 1, 2, 3
    # ----------------------------------------------------
    start_x_r1 = Inches(2.2)
    y_r1 = Inches(2.0)
    gap_r1 = Inches(1.2)
    
    row1_steps = [
        ("1. Data Ingest", ["JSONL Stream Ingest", "Max Active Scan", "JD Parsing"]),
        ("2. Vetting Filters", ["Honeypots Excluded", "Consulting Excluded", "Non-Tech Title Filter"]),
        ("3. TF-IDF Engine", ["Vocabulary Fitting", "Cosine Similarity", "Baseline Offset"])
    ]
    
    for idx, (title, details) in enumerate(row1_steps):
        x = start_x_r1 + idx * (box_w + gap_r1)
        
        # Rounded Rectangle Box
        shape = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y_r1, box_w, box_h)
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor(248, 250, 252) # Light gray
        shape.line.color.rgb = TEXT_COLOR_DARK             # Slate 900 border
        shape.line.width = Pt(1.5)
        remove_shadow(shape)
        
        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0.04)
        
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_COLOR_DARK
        p_t.font.name = 'Segoe UI'
        p_t.alignment = 1 # Center
        
        for det in details:
            p_d = tf.add_paragraph()
            p_d.text = "• " + det
            p_d.font.size = Pt(8.5)
            p_d.font.color.rgb = TEXT_COLOR_BODY
            p_d.font.name = 'Segoe UI'
            p_d.space_before = Pt(1.5)
            
        # Draw Arrow (Right)
        if idx < len(row1_steps) - 1:
            arrow_x = x + box_w + Inches(0.1)
            arrow_y = y_r1 + box_h / 2.0 - Inches(0.12)
            arrow = slide7.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, arrow_x, arrow_y, gap_r1 - Inches(0.2), Inches(0.24))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = TEXT_COLOR_DARK # Slate 900
            arrow.line.fill.background()
            remove_shadow(arrow)
            
    # Draw Vertical Down Arrow connecting Row 1 to Row 2
    # Positioned right below the 3rd box (x=9.0", end at 11.2", y=2.0")
    arrow_v = slide7.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(10.0), Inches(3.22), Inches(0.24), Inches(0.28))
    arrow_v.fill.solid()
    arrow_v.fill.fore_color.rgb = TEXT_COLOR_DARK
    arrow_v.line.fill.background()
    remove_shadow(arrow_v)

    # ----------------------------------------------------
    # Row 2: Steps 4, 5
    # ----------------------------------------------------
    start_x_r2 = Inches(3.9)
    y_r2 = Inches(3.65)
    gap_r2 = Inches(1.2)
    
    row2_steps = [
        ("4. Scoring & Scaling", ["Experience/Title Scores", "Location proximity check", "Reachability factors"]),
        ("5. Sort & Export", ["Stable score sorting", "Factual explanations", "vamsi_krishna.csv output"])
    ]
    
    for idx, (title, details) in enumerate(row2_steps):
        x = start_x_r2 + idx * (box_w + gap_r2)
        
        # Rounded Rectangle Box
        shape = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y_r2, box_w, box_h)
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor(248, 250, 252) # Light gray
        shape.line.color.rgb = TEXT_COLOR_DARK             # Slate 900 border
        shape.line.width = Pt(1.5)
        remove_shadow(shape)
        
        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0.04)
        
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_COLOR_DARK
        p_t.font.name = 'Segoe UI'
        p_t.alignment = 1 # Center
        
        for det in details:
            p_d = tf.add_paragraph()
            p_d.text = "• " + det
            p_d.font.size = Pt(8.5)
            p_d.font.color.rgb = TEXT_COLOR_BODY
            p_d.font.name = 'Segoe UI'
            p_d.space_before = Pt(1.5)
            
        # Draw Arrow (Right)
        if idx < len(row2_steps) - 1:
            arrow_x = x + box_w + Inches(0.1)
            arrow_y = y_r2 + box_h / 2.0 - Inches(0.12)
            arrow = slide7.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, arrow_x, arrow_y, gap_r2 - Inches(0.2), Inches(0.24))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = TEXT_COLOR_DARK # Slate 900
            arrow.line.fill.background()
            remove_shadow(arrow)
            
    # Architecture highlights at bottom
    desc_box = slide7.shapes.add_textbox(Inches(0.75), Inches(5.1), Inches(11.833), Inches(1.8))
    tf_desc = desc_box.text_frame
    tf_desc.word_wrap = True
    tf_desc.margin_left = tf_desc.margin_top = tf_desc.margin_right = tf_desc.margin_bottom = 0
    
    p = tf_desc.paragraphs[0]
    p.text = "System Architecture Highlights:"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = TEXT_COLOR_DARK
    p.font.name = 'Segoe UI'
    p.space_after = Pt(2)
    
    highlights = [
        "Streaming Execution: Reads JSONL records line-by-line using a memory-efficient generator to process 100K profiles under 500MB RAM.",
        "Deterministic Fusion: Melds semantic similarity with multi-criteria physical compatibility multipliers (location, availability, and engagement metrics) to produce a unified score.",
        "Ground-Truth Compliance: Evaluates and handles ties via deterministic ID sorting and filters 100% of honeypot anomalies."
    ]
    for h in highlights:
        p2 = tf_desc.add_paragraph()
        p2.text = "✔  " + h
        p2.font.size = Pt(11.5)
        p2.font.color.rgb = TEXT_COLOR_BODY
        p2.font.name = 'Segoe UI'
        p2.space_before = Pt(4)

    # =========================================================================
    # Slide 8: Results & Performance
    # =========================================================================
    slide8 = prs.slides[7]
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
    populate_slide_questions(slide8.shapes[2], s8_sections)

    # =========================================================================
    # Slide 9: Technologies Used
    # =========================================================================
    slide9 = prs.slides[8]
    s9_sections = [
        {
            'question': "What technologies, frameworks, and tools were used and why were they selected for this solution?",
            'bullets': [
                "Python: Core language for pipeline scripting, stream parsing, and data cleaning.",
                "Scikit-learn: Utilized for vector representation and cosine similarity matrix operations (enables fast CPU text similarity).",
                "NumPy & Pandas: Used for vectorized candidate matrix sorting, fast scoring calculations, and CSV operations.",
                "python-pptx: Enabled editing and updating the native PowerPoint presentation template."
            ]
        }
    ]
    populate_slide_questions(slide9.shapes[2], s9_sections)

    # =========================================================================
    # Slide 10: Submission Assets
    # =========================================================================
    slide10 = prs.slides[9]
    s10_sections = [
        {
            'question': "What are the core deliverables submitted for this challenge?",
            'bullets': [
                "Candidate Shortlist CSV: The final vamsi_krishna.csv file containing the top 100 candidates with validated ranks, scores, and custom rationales.",
                "Approach Presentation Deck: This document summarizing our methodology, scoring logic, and engineering design.",
                "System Metadata: A yaml configuration file specifying the compute environment, reproducibility commands, and AI usage declarations."
            ]
        },
        {
            'question': "Where are the code and live demonstration hosted?",
            'bullets': [
                "GitHub Code Repository: Complete codebase, including the ranking algorithm, PowerPoint generator, and setup instructions (https://github.com/vamsi-2003/data-ai-challenge).",
                "Hugging Face Space Sandbox: A live interactive environment running the candidate scoring engine on profile data."
            ]
        }
    ]
    populate_slide_questions(slide10.shapes[2], s10_sections)

    # =========================================================================
    # Slide 11: Thank You
    # =========================================================================
    # Left completely empty as designed by your template to avoid any cluttering / out-of-box text.
    
    prs.save(output_path)
    print(f"Successfully created native, clean PPTX at: {output_path}")

if __name__ == '__main__':
    create_presentation()
