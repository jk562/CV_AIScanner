# AI Resume Screener

An AI-powered web application that helps recruiters rank candidates by matching resumes against a job description. Upload multiple resumes (PDF or DOCX), enter a job description, and instantly receive a ranked list of candidates scored by relevance powered by TF-IDF and Cosine Similarity.

---

## Features

- **User Authentication** — Secure signup and login with hashed passwords
- **Resume Upload** — Supports PDF and DOCX files (up to 10 MB each)
- **AI Match Scoring** — Ranks candidates from 0–100% using TF-IDF + Cosine Similarity
- **Score Badges** — Color-coded results: Strong (green), Moderate (yellow), Weak (red)
- **Matched Keywords** — Shows which job description keywords appear in each resume
- **Screening History** — Revisit past job screenings from the dashboard
- **Export CSV** — Download ranked results as a `.csv` file
- **Loading Indicator** — Spinner shown while resumes are being analyzed
- **Custom Error Pages** — Styled 404 and 500 error pages
- **Activity Logging** — All logins, uploads, and errors are recorded in `app.log`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Frontend | HTML, Bootstrap 5 |
| Database | SQLite |
| AI / ML | scikit-learn (TF-IDF + Cosine Similarity) |
| PDF Parsing | pdfplumber |
| DOCX Parsing | python-docx |
| Auth Security | Werkzeug |

---

## Project Structure

```
CV_SCANNER/
├── Backend/
│   ├── app.py              # Flask routes and application logic
│   ├── database.py         # Database functions (SQLite)
│   ├── model.py            # AI scoring and text extraction
│   └── resume_screener.db  # SQLite database (auto-created)
├── frontend/
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── results.html
│   ├── 404.html
│   └── 500.html
├── StaticBG/               # Background images
├── uploads/                # Uploaded resume files (auto-created)
├── requirements.txt
├── app.log                 # Activity log (auto-created)
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/CV_SCANNER.git
   cd CV_SCANNER
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   cd Backend
   python app.py
   ```

4. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

The database and uploads folder are created automatically on first run — no additional setup needed.

---

## How It Works

1. **Sign up** and log in as a recruiter
2. Click **+ New Screening** on the dashboard
3. Enter a **Job Title** and **Job Description**
4. Upload one or more resumes (PDF or DOCX)
5. The app extracts text from each resume and calculates a match score using TF-IDF + Cosine Similarity
6. Results are displayed ranked from highest to lowest match
7. View matched keywords, export to CSV, or revisit results anytime from the dashboard

---

## Dependencies

```
flask
pdfplumber
python-docx
scikit-learn
werkzeug
```

Install all with:
```bash
pip install -r requirements.txt
```

---
