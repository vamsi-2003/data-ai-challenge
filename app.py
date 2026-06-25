import streamlit as st
import json
import pandas as pd
import numpy as np
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Import ranking logic helper functions
from rank import (
    is_honeypot, is_consulting_only, has_unrelated_title,
    get_experience_score, get_title_score, get_skills_score,
    get_location_multiplier, get_notice_multiplier, get_behavioral_multiplier,
    get_candidate_text, generate_reasoning
)

# Set page configuration for a premium dark-themed look
st.set_page_config(
    page_title="Intelligent Candidate Discovery & Ranking",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS for modern typography and styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF4B4B, #FF8F8F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #B0B0B0;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #262730;
        border-radius: 10px;
        padding: 1.5rem;
        border-left: 5px solid #FF4B4B;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #A0A0A0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar UI
st.sidebar.image("https://img.icons8.com/color/144/artificial-intelligence.png", width=80)
st.sidebar.markdown("## Configuration & Controls")
st.sidebar.info("This is the interactive Sandbox running the **Senior AI Engineer** candidate ranking engine.")

# Load the Job Description
jd_path = "job_description.md"
if os.path.exists(jd_path):
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()
else:
    jd_text = """### Senior AI Engineer
- **Experience**: 5-9 years preferred
- **Key Skills**: Embeddings, Vector search, Vector databases (Pinecone/Weaviate/Qdrant/Milvus/Elasticsearch), sentence-transformers, Python, RAG evaluation metrics (NDCG, MAP, MRR), A/B testing.
- **Location**: Noida/Pune preferred (India Tier-1 compatible)
- **Notice Period**: Short notice (<= 30 days) preferred.
"""

st.sidebar.markdown("### Job Description")
show_jd = st.sidebar.checkbox("View Job Description Details", value=False)
if show_jd:
    st.sidebar.markdown(jd_text)

# Main Page Layout
st.markdown('<div class="main-title">Intelligent Candidate Discovery & Ranking</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Hugging Face Sandbox Environment — Candidate Vetting & Scoring Engine</div>', unsafe_allow_html=True)

# Data source selection
data_source = st.radio(
    "Choose Candidate Data Source:",
    ("Use Sample Candidates (sample_candidates.json)", "Upload Custom Candidates File (JSON/JSONL)")
)

candidates_data = []

if data_source == "Use Sample Candidates (sample_candidates.json)":
    sample_path = "sample_candidates.json"
    if os.path.exists(sample_path):
        try:
            with open(sample_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                # Check if it is a list of candidates
                if isinstance(content, list):
                    candidates_data = content
                elif isinstance(content, dict) and "candidates" in content:
                    candidates_data = content["candidates"]
            st.success(f"Successfully loaded {len(candidates_data)} sample candidates from {sample_path}.")
        except Exception as e:
            st.error(f"Error reading sample file: {e}")
    else:
        st.warning("sample_candidates.json file not found in directory. Please upload a file instead.")
else:
    uploaded_file = st.file_uploader("Upload candidates JSON/JSONL file:", type=["json", "jsonl"])
    if uploaded_file is not None:
        try:
            lines = uploaded_file.getvalue().decode("utf-8").splitlines()
            # Try parsing as JSONL
            try:
                candidates_data = [json.loads(line) for line in lines if line.strip()]
                st.success(f"Successfully loaded {len(candidates_data)} candidates (JSONL format).")
            except:
                # Try parsing as standard JSON list
                uploaded_file.seek(0)
                content = json.loads(uploaded_file.getvalue().decode("utf-8"))
                if isinstance(content, list):
                    candidates_data = content
                elif isinstance(content, dict) and "candidates" in content:
                    candidates_data = content["candidates"]
                st.success(f"Successfully loaded {len(candidates_data)} candidates (JSON list format).")
        except Exception as e:
            st.error(f"Error parsing file: {e}. Ensure it is a valid JSON list or JSONL file.")

if len(candidates_data) > 0:
    st.markdown("### Ranking Execution")
    
    if st.button("Run Candidate Scoring Engine", type="primary"):
        with st.spinner("Processing profiles, checking honeypots, and running TF-IDF matcher..."):
            t_start = datetime.now()
            
            # Step 1: Pre-process texts and find max active date
            texts = []
            max_active_dt = None
            for c in candidates_data:
                texts.append(get_candidate_text(c))
                last_active = c['redrob_signals'].get('last_active_date')
                if last_active:
                    try:
                        dt = datetime.strptime(last_active, '%Y-%m-%d')
                        if max_active_dt is None or dt > max_active_dt:
                            max_active_dt = dt
                    except:
                        pass
            if max_active_dt is None:
                max_active_dt = datetime(2026, 6, 1)

            # Step 2: Compute TF-IDF similarities
            vectorizer = TfidfVectorizer(max_features=10000, stop_words='english')
            X = vectorizer.fit_transform(texts)
            q = vectorizer.transform([jd_text])
            sims = cosine_similarity(X, q).flatten()

            # Step 3: Compute scores and check exclusions
            candidate_scores = []
            honeypots_count = 0
            disqualified_count = 0
            
            for idx, c in enumerate(candidates_data):
                cid = c['candidate_id']
                tfidf_sim = float(sims[idx])
                
                # Exclusions
                if is_honeypot(c):
                    honeypots_count += 1
                    score = 0.0
                    candidate_scores.append({
                        'candidate_id': cid, 'score': score, 'candidate': c, 'matched_skills': [],
                        'status': 'Honeypot Disqualified'
                    })
                    continue
                    
                if is_consulting_only(c) or has_unrelated_title(c):
                    disqualified_count += 1
                    score = 0.0
                    candidate_scores.append({
                        'candidate_id': cid, 'score': score, 'candidate': c, 'matched_skills': [],
                        'status': 'Vetting Disqualified'
                    })
                    continue
                
                # Structured components
                exp_score = get_experience_score(c)
                title_score = get_title_score(c)
                skills_score, matched_skills = get_skills_score(c)
                structured_score = 0.25 * exp_score + 0.25 * title_score + 0.5 * skills_score
                
                # Multipliers
                loc_mult = get_location_multiplier(c)
                notice_mult = get_notice_multiplier(c)
                behavior_mult = get_behavioral_multiplier(c, max_active_dt)
                
                # Combined Score
                score = (tfidf_sim + 0.05) * structured_score * loc_mult * notice_mult * behavior_mult
                
                candidate_scores.append({
                    'candidate_id': cid, 'score': float(score), 'candidate': c, 'matched_skills': matched_skills,
                    'status': 'Qualified'
                })
            
            # Sort: score descending, ID ascending
            candidate_scores.sort(key=lambda x: (-x['score'], x['candidate_id']))
            
            # Select top 100 or total candidate count
            top_n = min(100, len([x for x in candidate_scores if x['status'] == 'Qualified']))
            qualified_scores = [x for x in candidate_scores if x['status'] == 'Qualified'][:top_n]
            
            # Formulate final output
            output_rows = []
            for rank_idx, item in enumerate(qualified_scores):
                rank = rank_idx + 1
                cid = item['candidate_id']
                score = item['score']
                c = item['candidate']
                matched_skills = item['matched_skills']
                reasoning = generate_reasoning(c, matched_skills, rank)
                
                output_rows.append({
                    "Rank": rank,
                    "Candidate ID": cid,
                    "Score": round(score, 6),
                    "Reasoning": reasoning,
                    "Experience": f"{c['profile'].get('years_of_experience', 0.0):.1f} Years",
                    "Current Title": c['profile'].get('current_title', 'N/A'),
                    "Location": c['profile'].get('location', 'N/A'),
                    "Notice Period": f"{c['redrob_signals'].get('notice_period_days', 90)} Days"
                })
                
            t_end = datetime.now()
            duration = (t_end - t_start).total_seconds()
            
            # Display Statistics
            st.markdown("### Run Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val">{len(candidates_data)}</div>
                    <div class="metric-label">Total Evaluated</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val">{honeypots_count}</div>
                    <div class="metric-label">Honeypots Detected</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val">{disqualified_count}</div>
                    <div class="metric-label">Vetting Disqualifications</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val">{duration:.3f}s</div>
                    <div class="metric-label">Execution Time</div>
                </div>
                """, unsafe_allow_html=True)
                
            # Results Table
            st.markdown(f"### Top {top_n} Ranked Candidates")
            if len(output_rows) > 0:
                df_results = pd.DataFrame(output_rows)
                
                # Display DataFrame
                st.dataframe(
                    df_results,
                    use_container_width=True,
                    column_config={
                        "Rank": st.column_config.NumberColumn("Rank", width="small"),
                        "Candidate ID": st.column_config.TextColumn("Candidate ID", width="medium"),
                        "Score": st.column_config.NumberColumn("Score", format="%.6f", width="small"),
                        "Reasoning": st.column_config.TextColumn("Reasoning", width="large"),
                        "Experience": st.column_config.TextColumn("Experience", width="small"),
                        "Current Title": st.column_config.TextColumn("Current Title", width="medium"),
                        "Location": st.column_config.TextColumn("Location", width="medium"),
                        "Notice Period": st.column_config.TextColumn("Notice Period", width="small")
                    }
                )
                
                # Convert output to CSV for download
                csv_df = df_results[["Candidate ID", "Rank", "Score", "Reasoning"]].copy()
                csv_df.columns = ["candidate_id", "rank", "score", "reasoning"]
                csv_data = csv_df.to_csv(index=False)
                
                st.download_button(
                    label="Download Submission CSV",
                    data=csv_data,
                    file_name="vamsi_krishna.csv",
                    mime="text/csv",
                    type="secondary"
                )
            else:
                st.warning("No candidates qualified after vetting filters.")
else:
    st.info("Please load sample data or upload a candidate list above.")

# Footer info
st.markdown("---")
st.markdown("Developed by **vamsi krishna** (vamshi krishna vemula - leader)")
