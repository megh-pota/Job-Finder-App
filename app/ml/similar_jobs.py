from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def find_similar_jobs(current_job, jobs, top_n=3):
    texts = [current_job.description] + [
        job.description for job in jobs if job.id != current_job.id
    ]

    tfidf = TfidfVectorizer(stop_words="english")
    vectors = tfidf.fit_transform(texts)

    similarities = cosine_similarity(vectors[0:1], vectors[1:])[0]

    ranked = sorted(
        zip(jobs, similarities),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:top_n]
