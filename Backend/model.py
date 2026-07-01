import pdfplumber
import docx
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_text_from_pdf(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(filepath):
    doc = docx.Document(filepath)
    return "\n".join(para.text for para in doc.paragraphs)


def extract_text(filepath):
    if filepath.lower().endswith(".pdf"):
        return extract_text_from_pdf(filepath)
    elif filepath.lower().endswith(".docx"):
        return extract_text_from_docx(filepath)
    else:
        raise ValueError("Unsupported file type")


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def calculate_match_score(job_description, resume_text):
    """
    Returns a 0-100 score representing how well the resume
    matches the job description, using TF-IDF + cosine similarity.
    """
    jd_clean = clean_text(job_description)
    resume_clean = clean_text(resume_text)

    documents = [jd_clean, resume_clean]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    score = round(similarity * 100, 2)
    return score


def extract_matched_keywords(job_description, resume_text, top_n=15):
    """
    Bonus: shows which important JD keywords appear in the resume.
    Helps recruiter see WHY a score was given.
    """
    jd_words = set(clean_text(job_description).split())
    resume_words = set(clean_text(resume_text).split())
    matched = jd_words.intersection(resume_words)
    return list(matched)[:top_n]