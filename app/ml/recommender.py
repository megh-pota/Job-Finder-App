import pdfplumber
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_text_from_pdf(pdf_path):
    text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
    except Exception as e:
        print("PDF read error:", e)

    return text.strip()


def recommend_jobs(resume_pdf_path, jobs, top_n=5):
    resume_text = extract_text_from_pdf(resume_pdf_path)

    # ❌ Resume text empty → no ML
    if not resume_text:
        print("Resume text EMPTY")
        return []

    job_texts = []
    valid_jobs = []

    for job in jobs:
        if job.description and len(job.description.strip()) > 20:
            job_texts.append(job.description)
            valid_jobs.append(job)

    if not job_texts:
        return []

    texts = [resume_text] + job_texts

    tfidf = TfidfVectorizer(
        stop_words="english",
        max_features=3000
    )

    vectors = tfidf.fit_transform(texts)
    similarities = cosine_similarity(vectors[0:1], vectors[1:])[0]

    recommendations = []

    for job, score in zip(valid_jobs, similarities):
        match_percent = round(score * 100, 2)

        # ✅ Show even low matches (important)
        if match_percent >= 1:
            recommendations.append({
                "job": job,
                "match_percent": match_percent
            })

    recommendations.sort(
        key=lambda x: x["match_percent"],
        reverse=True
    )

    return recommendations[:top_n]
