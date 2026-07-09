import os
import csv
import io
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

import database
import model

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx"}

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, "frontend"),
            static_folder=os.path.join(BASE_DIR, "StaticBG"))
app.secret_key = "change-this-secret-key"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB limit

logging.basicConfig(
    filename=os.path.join(BASE_DIR, "app.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
database.init_db()
logger.info("Application started. Database initialised.")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        conn.close()

        if user is None:
            logger.warning(f"Login failed — unknown username: '{username}'.")
            flash("Account not found. Please sign up first.")
        elif check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = username
            logger.info(f"User '{username}' logged in successfully.")
            return redirect(url_for("dashboard"))
        else:
            logger.warning(f"Login failed — wrong password for user: '{username}'.")
            flash("Incorrect password.")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing = cur.fetchone()
        conn.close()

        if existing:
            logger.warning(f"Signup failed — username already taken: '{username}'.")
            flash("Username already taken. Please choose another.")
        else:
            conn = database.get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                        (username, generate_password_hash(password)))
            conn.commit()
            user_id = cur.lastrowid
            conn.close()
            session["user_id"] = user_id
            session["username"] = username
            logger.info(f"New user registered: '{username}' (user_id={user_id}).")
            return redirect(url_for("dashboard"))

    return render_template("signup.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    jobs = database.get_jobs_for_user(session["user_id"])
    return render_template("dashboard.html", username=session.get("username"), jobs=jobs)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        job_title = request.form["job_title"]
        job_description = request.form["job_description"]
        files = request.files.getlist("resumes")

        job_id = database.add_job(job_title, job_description, session["user_id"])
        logger.info(f"Job '{job_title}' created (job_id={job_id}) by user_id={session['user_id']}.")

        success_count = 0
        fail_count = 0
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                try:
                    resume_text = model.extract_text(filepath)
                    score = model.calculate_match_score(job_description, resume_text)
                    database.add_candidate(job_id, filename, resume_text, score)
                    success_count += 1
                    logger.info(f"Processed '{filename}' for job_id={job_id} — score: {score}.")
                except Exception as e:
                    fail_count += 1
                    logger.error(f"Failed to process '{filename}' for job_id={job_id}: {e}.")
            elif file.filename:
                fail_count += 1
                logger.warning(f"Rejected file '{file.filename}' — unsupported format.")

        logger.info(f"Upload complete for job_id={job_id}: {success_count} succeeded, {fail_count} failed.")

        if fail_count > 0:
            flash(f"{success_count} resume(s) processed successfully, {fail_count} failed.")
        else:
            flash(f"All {success_count} resume(s) processed successfully.")

        return redirect(url_for("results", job_id=job_id))

    return render_template("upload.html")


@app.route("/results/<int:job_id>")
def results(job_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    job = database.get_job(job_id)
    candidates = database.get_ranked_candidates(job_id)

    keywords_by_candidate = {}
    if job:
        for c in candidates:
            kw = model.extract_matched_keywords(job["description"], c["extracted_text"] or "")
            keywords_by_candidate[c["filename"]] = kw

    return render_template("results.html", candidates=candidates, job_id=job_id,
                           job=job, keywords_by_candidate=keywords_by_candidate)


@app.route("/results/<int:job_id>/export")
def export_csv(job_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    candidates = database.get_ranked_candidates(job_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Rank", "Resume File", "Match Score (%)"])
    for i, c in enumerate(candidates, 1):
        writer.writerow([i, c["filename"], c["match_score"]])
    output.seek(0)
    logger.info(f"CSV exported for job_id={job_id} by user_id={session['user_id']}.")
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=results_job_{job_id}.csv"}
    )


@app.route("/logout")
def logout():
    username = session.get("username", "unknown")
    session.clear()
    logger.info(f"User '{username}' logged out.")
    return redirect(url_for("login"))


@app.errorhandler(404)
def page_not_found(_e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"Internal server error: {e}.")
    return render_template("500.html"), 500


@app.errorhandler(413)
def file_too_large(_e):
    logger.warning("File upload rejected — exceeded 10 MB limit.")
    flash("File too large. Maximum allowed size is 10 MB.")
    return redirect(url_for("upload"))


if __name__ == "__main__":
    print("Static folder:", app.static_folder)
    app.run(debug=True)
