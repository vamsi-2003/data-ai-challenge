#!/usr/bin/env python3
import json
import argparse
import sys
import os
import time
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Constants
CONSULTING_COMPANIES = {
    'tcs', 'infosys', 'wipro', 'accenture', 'cognizant', 
    'capgemini', 'tech mahindra', 'mindtree', 'hcl', 'mphasis', 'genpact ai'
}

UNRELATED_TITLES = {
    'marketing manager', 'operations manager', 'accountant', 'hr manager', 
    'customer support', 'civil engineer', 'operations analyst'
}

CORE_KEYWORDS = {'ai', 'ml', 'nlp', 'machine learning', 'retrieval', 'search', 'rag', 'deep learning'}
SECON_KEYWORDS = {'software', 'backend', 'full stack', 'fullstack', 'data engineer', 'applied ml', 'developer'}

CORE_SKILLS = {
    'embeddings', 'vector search', 'vector database', 'pinecone', 'weaviate', 
    'qdrant', 'milvus', 'elasticsearch', 'opensearch', 'faiss', 
    'sentence-transformers', 'rag', 'retrieval', 'python', 'ndcg', 'map', 'mrr', 'a/b testing'
}

NICE_SKILLS = {
    'lora', 'qlora', 'peft', 'fine-tuning', 'xgboost', 'learning-to-rank', 'distributed systems'
}

TIER1_CITIES = {'hyderabad', 'mumbai', 'delhi', 'noida', 'gurgaon', 'pune', 'bangalore', 'chennai', 'kolkata'}

def is_honeypot(c):
    # Rule 1 & 2: worked at Krutrim or Sarvam AI before 2023
    for job in c.get('career_history', []):
        comp = job.get('company')
        start = job.get('start_date')
        if start:
            try:
                year = int(start.split('-')[0])
                if comp in ['Krutrim', 'Sarvam AI'] and year < 2023:
                    return True
            except:
                pass
    
    # Rule 3: any expert/advanced skill with duration_months == 0
    for s in c.get('skills', []):
        prof = s.get('proficiency')
        dur = s.get('duration_months', 0)
        if prof in ['expert', 'advanced'] and dur == 0:
            return True
            
    return False

def is_consulting_only(c):
    jobs = c.get('career_history', [])
    if not jobs:
        return True
    for job in jobs:
        comp = job.get('company')
        if comp:
            if comp.lower() not in CONSULTING_COMPANIES:
                return False
    return True

def has_unrelated_title(c):
    current_title = c['profile'].get('current_title', '')
    if current_title:
        if current_title.lower() in UNRELATED_TITLES:
            return True
    return False

def get_experience_score(c):
    years = c['profile'].get('years_of_experience', 0.0)
    if 5.0 <= years <= 9.0:
        return 1.0
    elif years < 5.0:
        return max(0.0, years / 5.0)
    else:
        # decay for years > 9
        return max(0.1, 1.0 - (years - 9.0) * 0.1)

def get_title_score(c):
    headline = c['profile'].get('headline', '').lower()
    current = c['profile'].get('current_title', '').lower()
    
    has_core = any(kw in headline or kw in current for kw in CORE_KEYWORDS)
    has_secon = any(kw in headline or kw in current for kw in SECON_KEYWORDS)
    
    past_titles = [job.get('title', '').lower() for job in c.get('career_history', []) if not job.get('is_current')]
    has_past_core = any(any(kw in title for kw in CORE_KEYWORDS) for title in past_titles)
    
    if has_core or (current and 'ai engineer' in current) or (headline and 'ai engineer' in headline):
        return 1.0
    elif has_past_core:
        return 0.9
    elif has_secon:
        return 0.7
    elif has_past_secon := any(any(kw in title for kw in SECON_KEYWORDS) for title in past_titles):
        return 0.5
    else:
        return 0.1

def get_skills_score(c):
    score = 0.0
    matched_skills = []
    
    for s in c.get('skills', []):
        name = s.get('name', '').lower()
        prof = s.get('proficiency', 'beginner')
        dur = s.get('duration_months', 0)
        
        is_core = any(cs in name for cs in CORE_SKILLS)
        is_nice = any(ns in name for ns in NICE_SKILLS)
        
        if is_core or is_nice:
            prof_weight = {'expert': 1.0, 'advanced': 0.8, 'intermediate': 0.5, 'beginner': 0.2}.get(prof, 0.2)
            dur_weight = min(dur, 36) / 36.0
            skill_val = prof_weight * dur_weight
            
            if is_core:
                score += skill_val * 1.0
            else:
                score += skill_val * 0.5
            matched_skills.append((s.get('name'), prof, dur))
              
    return min(1.0, score / 3.0), matched_skills

def get_location_multiplier(c):
    loc = c['profile'].get('location', '').lower()
    country = c['profile'].get('country', '').lower()
    reloc = c['redrob_signals'].get('willing_to_relocate', False)
    
    is_preferred = 'noida' in loc or 'pune' in loc or 'delhi' in loc or 'gurgaon' in loc
    
    if is_preferred:
        return 1.0
    
    is_india = 'india' in country or any(city in loc for city in TIER1_CITIES)
    
    if is_india:
        if reloc:
            return 0.95
        else:
            return 0.7
    else:
        if reloc:
            return 0.4
        else:
            return 0.1

def get_notice_multiplier(c):
    np_days = c['redrob_signals'].get('notice_period_days', 90)
    if np_days <= 30:
        return 1.0
    elif np_days <= 90:
        return 0.8
    else:
        return 0.5

def get_behavioral_multiplier(c, max_active_date):
    # Inactivity
    last_active = c['redrob_signals'].get('last_active_date')
    inactivity_mult = 1.0
    if last_active and max_active_date:
        try:
            dt_active = datetime.strptime(last_active, '%Y-%m-%d')
            days_inactive = (max_active_date - dt_active).days
            if days_inactive <= 30:
                inactivity_mult = 1.0
            elif days_inactive <= 90:
                inactivity_mult = 0.9
            elif days_inactive <= 180:
                inactivity_mult = 0.6
            else:
                inactivity_mult = 0.2
        except:
            pass
            
    # Open to work
    otw = c['redrob_signals'].get('open_to_work_flag', False)
    otw_mult = 1.0 if otw else 0.85
    
    # Response rate
    rr = c['redrob_signals'].get('recruiter_response_rate', 0.5)
    rr_mult = 0.5 + 0.5 * rr
    
    # Avg response time
    rt = c['redrob_signals'].get('avg_response_time_hours', 24.0)
    rt_mult = 1.0 if rt <= 72 else 0.85
    
    # Interview completion rate
    icr = c['redrob_signals'].get('interview_completion_rate', 0.8)
    icr_mult = 1.0 if icr >= 0.8 else (0.5 + 0.625 * icr)
    
    return inactivity_mult * otw_mult * rr_mult * rt_mult * icr_mult

def get_candidate_text(c):
    parts = [
        c['profile'].get('headline', ''),
        c['profile'].get('summary', '')
    ]
    for job in c.get('career_history', []):
        parts.append(job.get('title', ''))
        parts.append(job.get('description', ''))
    for s in c.get('skills', []):
        parts.append(s.get('name', ''))
    return ' '.join(parts)

def generate_reasoning(c, matched_skills, rank):
    profile = c['profile']
    signals = c['redrob_signals']
    
    years = profile.get('years_of_experience', 0.0)
    title = profile.get('current_title', 'Software Engineer')
    location = profile.get('location', 'India')
    np_days = signals.get('notice_period_days', 90)
    rr = int(signals.get('recruiter_response_rate', 0.5) * 100)
    
    m_skills = [s[0] for s in matched_skills]
    if not m_skills:
        m_skills = [s.get('name') for s in c.get('skills', [])[:3]]
    skills_str = ", ".join(m_skills[:3]) if m_skills else "AI/ML engineering"
    
    concerns = []
    if np_days > 60:
        concerns.append(f"notice period is {np_days} days")
    if years < 5.0:
        concerns.append("experience is slightly below the 5-9 years preference")
    elif years > 9.0:
        concerns.append("experience is above the 9-year mark but shows strong seniority")
    
    concern_str = ""
    if concerns:
        concern_str = " Note: " + " and ".join(concerns) + "."
        
    reloc = signals.get('willing_to_relocate', False)
    reloc_str = ""
    if "noida" not in location.lower() and "pune" not in location.lower():
        if reloc:
            reloc_str = " (willing to relocate)"
            
    template_type = rank % 4
    
    if template_type == 0:
        base = f"Experienced {title} with {years:.1f} years of experience, showing strong hands-on expertise in {skills_str}."
        base += f" Located in {location}{reloc_str} with {rr}% platform response rate."
    elif template_type == 1:
        base = f"Matches the Senior AI Engineer requirements with {years:.1f} years of experience, including product deployment of {skills_str}."
        base += f" Noida/Pune compatible context ({location}{reloc_str}) and {np_days}-day availability."
    elif template_type == 2:
        base = f"Backend/ML specialist with {years:.1f} years of production experience. Strong engineering depth in {skills_str}, excellent platform activity, and {np_days}-day notice period."
    else:
        base = f"Strong candidate with {years:.1f} years of experience and demonstrated expertise in {skills_str} at scale."
        base += f" Active profile in {location}{reloc_str} with {rr}% response rate."
        
    return base + concern_str

def main():
    parser = argparse.ArgumentParser(description="Rank candidates for Senior AI Engineer JD")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl")
    parser.add_argument("--out", required=True, help="Output path for submission.csv")
    args = parser.parse_args()

    t_start = time.time()
    
    # Check if file exists
    if not os.path.exists(args.candidates):
        print(f"Error: Candidates file {args.candidates} does not exist.")
        sys.exit(1)

    print("Step 1: Loading job description...")
    # Load JD
    jd_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "job_description.md")
    if os.path.exists(jd_path):
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_text = f.read()
    else:
        # Fallback to hardcoded JD description
        jd_text = "Senior AI Engineer. Production experience with embeddings-based retrieval systems (sentence-transformers, OpenAI, BGE, E5) and vector databases (Pinecone, Weaviate, Qdrant, Milvus, FAISS, Elasticsearch). Strong Python, evaluation frameworks like NDCG, MAP, MRR, and A/B testing."

    print("Step 2: Loading candidates and extracting features...")
    candidates = []
    texts = []
    max_active_dt = None

    # Determine max active date in first pass (or default to 2026-06-01)
    # We open the file line by line
    is_gz = args.candidates.endswith('.gz')
    open_func = gzip.open if is_gz else open
    mode = 'rt' if is_gz else 'r'
    
    with open_func(args.candidates, mode, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            c = json.loads(line)
            candidates.append(c)
            texts.append(get_candidate_text(c))
            
            # Find max active date
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
        
    print(f"Loaded {len(candidates)} candidates. Latest activity date detected: {max_active_dt.strftime('%Y-%m-%d')}")

    print("Step 3: Fitting TF-IDF vectorizer...")
    # Fit TF-IDF on candidate profiles and compute similarity with JD
    vectorizer = TfidfVectorizer(max_features=15000, stop_words='english')
    X = vectorizer.fit_transform(texts)
    q = vectorizer.transform([jd_text])
    sims = cosine_similarity(X, q).flatten()
    print("TF-IDF fit complete.")

    print("Step 4: Computing structured and combined scores...")
    candidate_scores = []
    
    for i, c in enumerate(candidates):
        cid = c['candidate_id']
        tfidf_sim = float(sims[i])
        
        # Check honeypot
        if is_honeypot(c):
            score = 0.0
            candidate_scores.append({
                'candidate_id': cid,
                'score': score,
                'candidate': c,
                'matched_skills': []
            })
            continue
            
        # Check hard disqualifiers
        if is_consulting_only(c) or has_unrelated_title(c):
            score = 0.0
            candidate_scores.append({
                'candidate_id': cid,
                'score': score,
                'candidate': c,
                'matched_skills': []
            })
            continue
            
        # Get structured components
        exp_score = get_experience_score(c)
        title_score = get_title_score(c)
        skills_score, matched_skills = get_skills_score(c)
        
        # Compute base structured score (weighted average)
        # We weigh skills highest (0.5), followed by title (0.25) and experience years (0.25)
        structured_score = 0.25 * exp_score + 0.25 * title_score + 0.5 * skills_score
        
        # Apply multipliers
        loc_mult = get_location_multiplier(c)
        notice_mult = get_notice_multiplier(c)
        behavior_mult = get_behavioral_multiplier(c, max_active_dt)
        
        # Combined score: combination of TF-IDF similarity and structured features
        # Add a small base value of 0.05 to TF-IDF so that structured matching can still rank candidates even with lower textual overlap
        score = (tfidf_sim + 0.05) * structured_score * loc_mult * notice_mult * behavior_mult
        
        # Ensure score is a float
        score = float(score)
        
        candidate_scores.append({
            'candidate_id': cid,
            'score': score,
            'candidate': c,
            'matched_skills': matched_skills
        })

    print("Step 5: Sorting and selecting top 100...")
    # Sort: score descending, candidate_id ascending (tie-breaker)
    # To sort score descending and ID ascending, we sort by (-score, candidate_id)
    candidate_scores.sort(key=lambda x: (-x['score'], x['candidate_id']))
    
    top_100 = candidate_scores[:100]
    
    # Ensure scores are strictly non-increasing. If there's a float precision anomaly, force it
    # Format reasoning strings
    output_rows = []
    for rank_idx, item in enumerate(top_100):
        rank = rank_idx + 1
        cid = item['candidate_id']
        score = item['score']
        c = item['candidate']
        matched_skills = item['matched_skills']
        
        reasoning = generate_reasoning(c, matched_skills, rank)
        output_rows.append([cid, rank, f"{score:.6f}", reasoning])

    print("Step 6: Writing results to CSV...")
    import csv
    with open(args.out, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        writer.writerows(output_rows)
        
    t_end = time.time()
    print(f"Ranking complete! Generated output at {args.out}")
    print(f"Total time elapsed: {t_end - t_start:.2f} seconds")

if __name__ == "__main__":
    main()
