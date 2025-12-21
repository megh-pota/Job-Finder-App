from app.ml.recommender import extract_text_from_pdf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_match_score(resume_pdf_path, job_description):
    """
    Returns match percentage between resume & job description
    """

    resume_text = extract_text_from_pdf(resume_pdf_path)

    if not resume_text or not job_description:
        return 0.0

    texts = [resume_text, job_description]

    tfidf = TfidfVectorizer(
        stop_words="english",
        max_features=3000
    )

    vectors = tfidf.fit_transform(texts)

    score = cosine_similarity(vectors[0:1], vectors[1:])[0][0]

    return round(score * 100, 2)
