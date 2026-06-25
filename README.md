# Intelligent Candidate Discovery & Ranking System

This repository contains the source code, metadata, and submission for the **Intelligent Candidate Discovery & Ranking Challenge**.

Our system ranks candidates based on a hybrid matching system of semantic TF-IDF text alignment and a multi-dimensional structured profile score. It operates locally on CPU under the strict compute budget of 5 minutes for 100,000 candidates (completing in under 2 minutes).

## Project Structure

```text
├── rank.py                       # Core ranking and scoring script
├── vamsi_krishna.csv          # Generated ranked output of top 100 candidates
├── submission_metadata.yaml      # Submission metadata
├── README.md                     # Documentation and setup (this file)
├── validate_submission.py        # Provided validator script
├── candidate_schema.json         # Candidate JSON schema
└── job_description.md            # Role description markdown
```

## Quick Start & Setup

### Prerequisites

Ensure you have Python 3.8+ installed along with the required libraries:

```bash
pip install numpy pandas scikit-learn pyyaml python-docx
```

### Reproducing the Submission

To run the ranker and generate the ranked list, execute the following command from the repository root:

```bash
python rank.py --candidates ./candidates.jsonl --out ./vamsi_krishna.csv
```

### Validation

To validate the format of the generated CSV file, run:

```bash
python validate_submission.py vamsi_krishna.csv
```

## Methodology

Our system avoids simple keyword matching by integrating multiple layers of candidate vetting:

1. **Honeypot Filtering (0% Honeypot Rate)**
   - **Date Inconsistency Check**: We identify and exclude candidates who claim to have worked at early-stage startups like **Krutrim** or **Sarvam AI** prior to their founding year (2023).
   - **Zero-Duration Skill Check**: We exclude candidates who list skills with `expert` or `advanced` proficiency but have a `duration_months` of exactly 0.

2. **Hard Disqualifiers**
   - **Consulting-Only Careers**: Candidates who have worked *only* at large IT consulting/services firms (e.g. TCS, Infosys, Wipro, Accenture) are filtered out, as the JD explicitly targets candidates with product-company background.
   - **Unrelated Current Roles**: Keyword-stuffers whose current title is unrelated to software engineering/analytics (e.g., Marketing Manager, Accountant, HR Manager) are filtered out.

3. **Structured Scorer**
   - **Experience Years Score**: Evaluates total years of experience, scoring `1.0` for the preferred 5-9 years range, and applying a linear decay for candidates outside the band.
   - **Title Alignment Score**: Evaluates current title, headline, and past titles against AI/ML and software engineering keyword hierarchies.
   - **Skills Score**: Matches candidate skills against core JD requirements (embeddings, vector search, Pinecone, evaluation metrics), weighting them by proficiency and duration (making it robust to keyword stuffing).

4. **Multipliers & Multi-dimensional Signals**
   - **Location**: Noida/Pune local candidates are prioritized. Relocations from Tier-1 Indian cities are supported, while international candidates are down-weighted due to lack of visa sponsorship.
   - **Notice Period**: Notice periods <= 30 days are prioritized.
   - **Behavioral Signals**: Models candidate reachability by evaluating their inactivity period (days since last active on the platform), responsiveness rate, and willingness to accept interviews.

5. **TF-IDF Semantic Matching**
   - Combines the candidate's headline, summary, job titles, descriptions, and skills into a single profile document.
   - Computes cosine similarity between all candidate profile texts and the raw Job Description text.

6. **Deterministic Tie-Breaking**
   - Sorts candidates by their combined score descending. In case of ties, sorts by `candidate_id` ascending to comply with validation requirements.

7. **Fact-Based Reasoning**
   - Programmatically generates a 1-2 sentence explanation for each of the top 100 candidates. The reasoning references actual years of experience, titles, specific matching skills, location, notice period, and responsiveness, ensuring zero hallucination.

## Benchmarks & Performance
- **Dataset Size**: 100,000 candidates (JSONL, ~487 MB)
- **Execution Time**: **117 seconds** (on CPU only)
- **Memory Footprint**: ~400 MB RAM
- **Honeypot Rate**: **0%** in the top 100