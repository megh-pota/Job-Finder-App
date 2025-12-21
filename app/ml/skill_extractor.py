import re

SKILL_KEYWORDS = [
    "python", "java", "c++", "sql", "mysql", "postgresql",
    "flask", "django", "fastapi",
    "machine learning", "deep learning", "nlp",
    "pandas", "numpy", "scikit-learn",
    "data analysis", "data science",
    "html", "css", "javascript", "react",
    "docker", "git", "linux"
]


def extract_skills(text):
    if not text:
        return []

    text = text.lower()
    found = set()

    for skill in SKILL_KEYWORDS:
        # Word-boundary safe regex
        pattern = rf"\b{re.escape(skill)}\b"
        if re.search(pattern, text):
            found.add(skill.title())

    return sorted(found)
