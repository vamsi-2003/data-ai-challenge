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
    TEXT_COLOR_DARK = RGBColor(15, 23, 42)     # Slate 900
    TEXT_COLOR_BODY = RGBColor(51, 65, 85)     # Slate 700
    TEXT_COLOR_MUTED = RGBColor(100, 116, 139) # Slate 500
    ACCENT_COLOR = RGBColor(13, 148, 136)      # Teal 600
    BORDER_COLOR = RGBColor(226, 232, 240)     # Slate 200
    
    def apply_bg(slide, slide_num):
        # Insert extracted reference slide image as background
        bg_path = f"template_images/slide_{slide_num}.png"
        slide.shapes.add_picture(bg_path, 0, 0, prs.slide_width, prs.slide_height)
        return slide
        
    def apply_content_mask(slide):
        # Add a white shape mask to cover placeholder bullets/questions in the reference PDF
        # We start at y=2.0 (below header and title) and stop at y=6.9 (above footer)
        mask = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(2.0), Inches(11.933), Inches(4.9))
        mask.fill.solid()
        mask.fill.fore_color.rgb = RGBColor(255, 255, 255) # Pure White
        mask.line.color.rgb = RGBColor(255, 255, 255)      # Pure White border
        return slide

    def add_content_bullets(slide, content_dict):
        # Adds content in two columns or single column
        apply_content_mask(slide)
        
        # Left column textbox
        txBox_l = slide.shapes.add_textbox(Inches(0.75), Inches(2.1), Inches(5.6), Inches(4.6))
        tf_l = txBox_l.text_frame
        tf_l.word_wrap = True
        tf_l.margin_left = tf_l.margin_top = tf_l.margin_right = tf_l.margin_bottom = 0
        
        # Right column textbox
        txBox_r = slide.shapes.add_textbox(Inches(6.98), Inches(2.1), Inches(5.6), Inches(4.6))
        tf_r = txBox_r.text_frame
        tf_r.word_wrap = True
        tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0
        
        # Populate Left
        left_data = content_dict.get('left', [])
        for i, item in enumerate(left_data):
            p = tf_l.add_paragraph() if i > 0 else tf_l.paragraphs[0]
            p.text = "• " + item['header']
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = TEXT_COLOR_DARK
            p.font.name = 'Segoe UI'
            p.space_after = Pt(4)
            p.space_before = Pt(10) if i > 0 else Pt(0)
            
            for sub in item.get('bullets', []):
                p_sub = tf_l.add_paragraph()
                p_sub.text = "   " + sub
                p_sub.font.size = Pt(12)
                p_sub.font.color.rgb = TEXT_COLOR_BODY
                p_sub.font.name = 'Segoe UI'
                p_sub.space_after = Pt(2)
                
        # Populate Right
        right_data = content_dict.get('right', [])
        for i, item in enumerate(right_data):
            p = tf_r.add_paragraph() if i > 0 else tf_r.paragraphs[0]
            p.text = "• " + item['header']
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = TEXT_COLOR_DARK
            p.font.name = 'Segoe UI'
            p.space_after = Pt(4)
            p.space_before = Pt(10) if i > 0 else Pt(0)
            
            for sub in item.get('bullets', []):
                p_sub = tf_r.add_paragraph()
                p_sub.text = "   " + sub
                p_sub.font.size = Pt(12)
                p_sub.font.color.rgb = TEXT_COLOR_BODY
                p_sub.font.name = 'Segoe UI'
                p_sub.space_after = Pt(2)

    # =========================================================================
    # Slide 1: Title Slide
    # =========================================================================
    slide1 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide1, 1)
    
    # Mask out reference labels at bottom
    mask1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(4.0), Inches(11.933), Inches(2.9))
    mask1.fill.solid()
    mask1.fill.fore_color.rgb = RGBColor(255, 255, 255)
    mask1.line.color.rgb = RGBColor(255, 255, 255)
    
    # Overwrite custom metadata text box
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
    
    s2_data = {
        'left': [
            {
                'header': "Proposed Solution: Hybrid Scorer",
                'bullets': [
                    "Blends semantic text similarity (TF-IDF cosine similarity) with a multi-criteria structured profile scorer.",
                    "Builds unified candidate document strings from Headlines, Summaries, Job Histories, and Skills.",
                    "Optimized for zero-network, local execution within strict CPU and memory bounds."
                ]
            },
            {
                'header': "Zero-Honeypot Enforcement Engine",
                'bullets': [
                    "Applies hard heuristics to catch fake profiles claiming start dates at Krutrim or Sarvam AI prior to their actual 2023 founding.",
                    "Catches zero-duration skills where candidates claim 'expert' status but specify exactly 0 months of duration."
                ]
            }
        ],
        'right': [
            {
                'header': "Key Differentiators",
                'bullets': [
                    "Operational Feasibility: Incorporates notice period (favoring <=30 days) and location compatibilities (Pune/Noida focus).",
                    "Behavioral Reachability Model: Adjusts scores using actual activity, response rates, and interview completion flags.",
                    "No Hallucinations: Uses factual template compilation for candidate reasonings instead of generative LLMs."
                ]
            }
        ]
    }
    add_content_bullets(slide2, s2_data)

    # =========================================================================
    # Slide 3: JD Understanding & Candidate Evaluation
    # =========================================================================
    slide3 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide3, 3)
    
    s3_data = {
        'left': [
            {
                'header': "Core Job Description Requirements",
                'bullets': [
                    "Experience Band: 5-9 years of total experience preferred.",
                    "Technical Depth: Sentence-transformers, embeddings, and vector databases (Pinecone, Qdrant, Milvus, Weaviate, FAISS).",
                    "Rigorous Evaluation: Production knowledge of ranking metrics (NDCG, MAP, MRR) and online A/B testing.",
                    "Background Filter: Disqualifies candidates whose entire careers are solely in services/consulting firms (TCS, Wipro, Infosys)."
                ]
            }
        ],
        'right': [
            {
                'header': "Signal Weights & Importance",
                'bullets': [
                    "Experience Years (25% Weight): Scored at 1.0 for preferred 5-9 years, with linear decay below 5 and slow decay above 9.",
                    "Role Alignment (25% Weight): Scours headlines and current/past titles for AI/ML keywords vs backend/unrelated titles.",
                    "Skill Match (50% Weight): Core skills weighted strictly by proficiency (expert=1.0) and duration (capped at 36 months).",
                    "Multipliers: Location (Noida/Pune local = 1.0, relocations = 0.95), Availability (<=30d = 1.0, <=90d = 0.8), Engagement (Activity recency)."
                ]
            }
        ]
    }
    add_content_bullets(slide3, s3_data)

    # =========================================================================
    # Slide 4: Ranking Methodology
    # =========================================================================
    slide4 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide4, 4)
    
    s4_data = {
        'left': [
            {
                'header': "Vectorization & Cosine Similarity",
                'bullets': [
                    "Fits a local TfidfVectorizer on all 100K candidates with a vocabulary cap of 15,000 features.",
                    "Computes the cosine similarity of candidate document vectors against the job description text.",
                    "Offsets TF-IDF score by +0.05 to allow structured criteria to rank candidates even with lower text overlap."
                ]
            },
            {
                'header': "Hard Vetting & Exclusions",
                'bullets': [
                    "Honeypot Filter: Disqualifies all fake candidate records (score set to 0.0).",
                    "Consulting Excluder: Drops candidates whose entire careers lie in consulting (TCS/Infosys/Wipro).",
                    "Current Role Check: Rejects candidates with unrelated current roles."
                ]
            }
        ],
        'right': [
            {
                'header': "Mathematical Signal Fusion",
                'bullets': [
                    "Calculates Score = (Sim + 0.05) x Structured_Score x Location_Mult x Notice_Mult x Behavior_Mult.",
                    "Location Multiplier: Noida/Pune preferred (1.0), Tier-1 India relocations (0.95), other India (0.7), international (0.1).",
                    "Availability Multiplier: <=30 days notice (1.0), <=90 days (0.8), >90 days (0.5).",
                    "Behavioral Multiplier: inactivity_decay x open_to_work x response_rate x response_time x interview_completion."
                ]
            }
        ]
    }
    add_content_bullets(slide4, s4_data)

    # =========================================================================
    # Slide 5: Explainability & Data Validation
    # =========================================================================
    slide5 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide5, 5)
    
    s5_data = {
        'left': [
            {
                'header': "Deterministic Factual Explanations",
                'bullets': [
                    "Explanations are generated programmatically using a compiler with four distinct grammatical templates.",
                    "Injects actual profile variables (years of experience, current title, key skills, location, notice period, response rate).",
                    "Factual Guarantee: Completely eliminates hallucinations, ensuring every generated reasoning is backed by database properties."
                ]
            },
            {
                'header': "Dynamic Concern Flags",
                'bullets': [
                    "Automatically appends warning flags to the reasoning for candidates who have high notice periods (>60 days).",
                    "Notes if experience falls slightly outside the preferred 5-9 years band, providing recruiters full visibility."
                ]
            }
        ],
        'right': [
            {
                'header': "Data Validation & Suspicious Profile Handling",
                'bullets': [
                    "Krutrim/Sarvam Founders: Excludes profiles claiming start dates before the startups' actual 2023 registration.",
                    "Zero-month Experts: Identifies keyword-stuffers claiming 'expert' skills but recording 0 months of duration.",
                    "Deterministic Tie-Breaker: Sorts score ties by candidate_id ascending to ensure strict schema validation compatibility.",
                    "Failsafe Format Check: Output runs through validate_submission.py to guarantee monotonicity and 100 rows."
                ]
            }
        ]
    }
    add_content_bullets(slide5, s5_data)

    # =========================================================================
    # Slide 6: End-to-End Workflow
    # =========================================================================
    slide6 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide6, 6)
    
    s6_data = {
        'left': [
            {
                'header': "Data Ingest & Parsing",
                'bullets': [
                    "Ingests candidates.jsonl line-by-line using a memory-friendly generator.",
                    "Loads and parses job_description.md to extract search keywords.",
                    "First-pass scan detects the latest platform activity date (2026-05-27) for relative inactivity math."
                ]
            },
            {
                'header': "Pre-filtering & Text Indexing",
                'bullets': [
                    "Instantly excludes 94 honeypot candidates and non-product profiles.",
                    "Builds combined profile text and runs scikit-learn TF-IDF fit-transform on the remaining candidates."
                ]
            }
        ],
        'right': [
            {
                'header': "Structured Scoring & Signal Fusion",
                'bullets': [
                    "Calculates structured experience, title, and skill duration scores.",
                    "Applies location, availability, and behavioral multipliers to scale the base score.",
                    "Sorts candidates descending by final score, breaking ties by candidate_id ascending."
                ]
            },
            {
                'header': "Reasoning Compilation & Output",
                'bullets': [
                    "Compiles reasoning strings for the top 100 candidates based on actual metrics.",
                    "Writes output to vamsi_krishna.csv.",
                    "Runs format validation checks."
                ]
            }
        ]
    }
    add_content_bullets(slide6, s6_data)

    # =========================================================================
    # Slide 7: System Architecture
    # =========================================================================
    slide7 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide7, 7)
    apply_content_mask(slide7)
    
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
        shape.line.color.rgb = RGBColor(15, 23, 42)        # Slate 900 border
        shape.line.width = Pt(1.5)
        
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
            arrow.fill.fore_color.rgb = RGBColor(15, 23, 42) # Slate 900
            arrow.line.fill.background()
            
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
    
    s8_data = {
        'left': [
            {
                'header': "Execution Benchmarks",
                'bullets': [
                    "Total Runtime: 117.07 seconds end-to-end (well within the 5-minute constraint).",
                    "Memory Footprint: Under 500 MB RAM peak (limit is 16 GB).",
                    "Honeypot Removal: 100% of the 94 identified fake candidates were caught and excluded (Honeypot rate = 0% in top 100).",
                    "Format Verification: 100% Validated via validate_submission.py."
                ]
            }
        ],
        'right': [
            {
                'header': "Ranking Insights & Quality",
                'bullets': [
                    "Top Match (CAND_0081846): 6.7 years of experience, current title matches Senior AI Engineer, expertise in Elasticsearch & Vector Search, Noida/Pune compatible.",
                    "Rank 2 (CAND_0018499): 7.2 years, expert in Weaviate & Pinecone, 15-day notice period.",
                    "Rank 3 (CAND_0039754): 16.2 years, expert in Fine-tuning LLMs, Qdrant, OpenSearch, noted experience seniority concern.",
                    "Rank 5 (CAND_0099806): 4.6 years, expert in RAG & FAISS, noted experience slightly below range."
                ]
            }
        ]
    }
    add_content_bullets(slide8, s8_data)

    # =========================================================================
    # Slide 9: Technologies Used
    # =========================================================================
    slide9 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide9, 9)
    
    s9_data = {
        'left': [
            {
                'header': "Codebase & Core Stack",
                'bullets': [
                    "Python: Standard language for pipeline scripting, streaming generator pipelines, and YAML parsing.",
                    "Scikit-learn: Utilized TfidfVectorizer for vector representation and cosine_similarity matrix operations.",
                    "NumPy & Pandas: Used for vectorized candidate matrix sorting, fast scoring calculations, and CSV operations."
                ]
            }
        ],
        'right': [
            {
                'header': "Design Rationale",
                'bullets': [
                    "Zero-GPU requirement: Opted for TF-IDF + Cosine similarity over Transformer embeddings to run local scoring within the tight CPU timeline.",
                    "Streaming/Iterative parsing: Reads JSONL line-by-line to stay well within the 16 GB memory limit.",
                    "Rule-based compilation: Uses deterministic template logic for generating explanations, guaranteeing speed, zero API cost, and zero hallucinations."
                ]
            }
        ]
    }
    add_content_bullets(slide9, s9_data)

    # =========================================================================
    # Slide 10: Submission Assets
    # =========================================================================
    slide10 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(slide10, 10)
    
    s10_data = {
        'left': [
            {
                'header': "Completed Deliverables",
                'bullets': [
                    "GitHub Repository: https://github.com/vamsi-2003/data-ai-challenge",
                    "HuggingFace Space Demo Link: https://huggingface.co/spaces/vamsi-2003/data-ai-challenge",
                    "Ranked Output (CSV): vamsi_krishna.csv (contains the top 100 candidates with custom rationales)"
                ]
            }
        ],
        'right': [
            {
                'header': "Submission Configuration",
                'bullets': [
                    "Submission Metadata: submission_metadata.yaml (containing team name, leader name, and methodology)",
                    "Approach Presentation: vamsi_krishna_approach.pptx (this generated slide deck, ready for PDF export)"
                ]
            }
        ]
    }
    add_content_bullets(slide10, s10_data)

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
    
    prs.save('vamsi_krishna_approach_v2.pptx')
    print("Successfully created template-identical widescreen vamsi_krishna_approach_v2.pptx!")

if __name__ == '__main__':
    create_presentation()
