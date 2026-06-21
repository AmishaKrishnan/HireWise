from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash
from config import get_connection
from werkzeug.security import check_password_hash
import os
import PyPDF2

app = Flask(__name__)
app.secret_key = "hirewise_secret_key"

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        password = generate_password_hash(
            request.form["password"]
        )

        conn = get_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO users(fullname,email,password)
        VALUES(%s,%s,%s)
        """

        cursor.execute(
            sql,
            (fullname, email, password)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(
                user[3],
                password):

            session["user_id"] = user[0]
            session["name"] = user[1]

            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    # Latest Resume Score
    cursor.execute("""
        SELECT score
        FROM resumes
        WHERE user_id=%s
        ORDER BY id DESC
        LIMIT 1
    """, (session["user_id"],))

    resume = cursor.fetchone()

    resume_score = 0

    if resume:
        resume_score = resume[0]

    # Latest Aptitude Score
    cursor.execute("""
        SELECT score
        FROM results
        WHERE user_id=%s
        AND test_type='Aptitude'
        ORDER BY id DESC
        LIMIT 1
    """, (session["user_id"],))

    aptitude = cursor.fetchone()

    aptitude_score = 0

    if aptitude:
        aptitude_score = aptitude[0]

    # Total Tests Taken
    cursor.execute("""
        SELECT COUNT(*)
        FROM results
        WHERE user_id=%s
        AND test_type='Aptitude'
    """, (session["user_id"],))

    tests_taken = cursor.fetchone()[0]

    # Resume History
    cursor.execute("""
        SELECT filename, score, uploaded_at
        FROM resumes
        WHERE user_id=%s
        ORDER BY uploaded_at DESC
        LIMIT 5
    """, (session["user_id"],))

    resume_history = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        name=session["name"],
        resume_score=resume_score,
        aptitude_score=aptitude_score,
        tests_taken=tests_taken,
        resume_history=resume_history
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/resume", methods=["GET", "POST"])
def resume():

    if "user_id" not in session:
        return redirect("/login")

    score = None

    found_skills = []
    missing_skills = []

    feedback = []

    technical_score = 0
    project_score = 0
    soft_score = 0
    certification_score = 0
    achievement_score = 0
    education_score = 0

    technical_skills = [
        "python","java","c","c++","javascript",
        "html","css","bootstrap","react",
        "flask","django","sql","mysql",
        "mongodb","git","github","aws",
        "docker","dbms","operating system",
        "computer networks","data structures",
        "algorithms"
    ]

    project_keywords = [
        "project","developed","application",
        "system","github","web application"
    ]

    soft_skills = [
        "communication","leadership","teamwork",
        "problem solving","adaptability",
        "time management"
    ]

    certifications = [
        "certificate","certification",
        "coursera","udemy","nptel",
        "infosys","aws"
    ]

    achievement_keywords = [
        "internship","award","winner",
        "hackathon","achievement",
        "volunteer"
    ]

    education_keywords = [
        "bca","mca","bachelor",
        "master","university",
        "college"
    ]

    if request.method == "POST":

        file = request.files["resume"]

        filepath = os.path.join(
            "uploads",
            file.filename
        )

        file.save(filepath)

        text = ""

        with open(filepath, "rb") as pdf:

            reader = PyPDF2.PdfReader(pdf)

            for page in reader.pages:

                extracted = page.extract_text()

                if extracted:
                    text += extracted

        text = text.lower()

        # TECHNICAL SKILLS (40)

        for skill in technical_skills:

            if skill in text:
                found_skills.append(skill)

            else:
                missing_skills.append(skill)

        technical_score = int(
            (len(found_skills) / len(technical_skills)) * 40
        )

        # PROJECTS (20)

        projects_found = 0

        for item in project_keywords:

            if item in text:
                projects_found += 1

        project_score = min(projects_found * 4, 20)

        # SOFT SKILLS (10)

        soft_found = 0

        for item in soft_skills:

            if item in text:
                soft_found += 1

        soft_score = min(soft_found * 2, 10)

        # CERTIFICATIONS (10)

        cert_found = 0

        for item in certifications:

            if item in text:
                cert_found += 1

        certification_score = min(cert_found * 2, 10)

        # ACHIEVEMENTS & INTERNSHIPS (10)

        achievement_found = 0

        for item in achievement_keywords:

            if item in text:
                achievement_found += 1

        achievement_score = min(
            achievement_found * 2,
            10
        )

        # EDUCATION (10)

        education_found = 0

        for item in education_keywords:

            if item in text:
                education_found += 1

        if education_found > 0:
            education_score = 10

        # FINAL SCORE

        score = (
            technical_score +
            project_score +
            soft_score +
            certification_score +
            achievement_score +
            education_score
        )

        # FEEDBACK

        if technical_score < 20:
            feedback.append(
                "Add more technical skills and technologies."
            )

        if project_score < 10:
            feedback.append(
                "Include more project descriptions."
            )

        if certification_score < 5:
            feedback.append(
                "Add certifications to strengthen your profile."
            )

        if soft_score < 5:
            feedback.append(
                "Mention soft skills such as communication and teamwork."
            )

        if achievement_score < 5:
            feedback.append(
                "Highlight internships, achievements or awards."
            )

        if len(feedback) == 0:
            feedback.append(
                "Excellent resume profile."
            )

        # SAVE TO DATABASE

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO resumes
            (user_id, filename, score, missing_skills)
            VALUES (%s,%s,%s,%s)
            """,
            (
                session["user_id"],
                file.filename,
                score,
                ",".join(missing_skills)
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

    return render_template(
        "resume.html",
        score=score,
        found_skills=found_skills,
        missing_skills=missing_skills,
        feedback=feedback,
        technical_score=technical_score,
        project_score=project_score,
        soft_score=soft_score,
        certification_score=certification_score,
        achievement_score=achievement_score,
        education_score=education_score
    )

@app.route("/aptitude", methods=["GET", "POST"])
def aptitude():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        question_ids = request.form.getlist("question_ids")

        score = 0

        for qid in question_ids:

            cursor.execute(
                """
                SELECT correct_answer
                FROM aptitude_questions
                WHERE id=%s
                """,
                (qid,)
            )

            correct = cursor.fetchone()[0]

            selected = request.form.get(qid)

            if selected == correct:
                score += 1

        cursor.execute(
            """
            INSERT INTO results
            (user_id,test_type,score)
            VALUES(%s,%s,%s)
            """,
            (
                session["user_id"],
                "Aptitude",
                score
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        return render_template(
            "results.html",
            score=score
        )

    cursor.execute(
        """
        SELECT *
        FROM aptitude_questions
        ORDER BY RAND()
        LIMIT 10
        """
    )

    questions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "aptitude.html",
        questions=questions
    )

@app.route("/interview", methods=["GET", "POST"])
def interview():

    if "user_id" not in session:
        return redirect("/login")

    questions = []

    if request.method == "POST":

        category = request.form["category"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM questions
            WHERE category=%s
            """,
            (category,)
        )

        questions = cursor.fetchall()

        cursor.close()
        conn.close()

    return render_template(
        "interview.html",
        questions=questions
    )

@app.route("/performance")
def performance():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    labels = []
    scores = []

    resume_score = 0
    latest_aptitude = 0
    best_aptitude = 0
    tests_taken = 0

    # Resume Score

    cursor.execute("""
        SELECT score
        FROM resumes
        WHERE user_id=%s
        ORDER BY id DESC
        LIMIT 1
    """, (session["user_id"],))

    resume = cursor.fetchone()

    if resume:
        resume_score = resume[0]

    # Latest Aptitude Score

    cursor.execute("""
        SELECT score
        FROM results
        WHERE user_id=%s
        AND test_type='Aptitude'
        ORDER BY id DESC
        LIMIT 1
    """, (session["user_id"],))

    latest = cursor.fetchone()

    if latest:
        latest_aptitude = latest[0]

    # Best Aptitude Score

    cursor.execute("""
        SELECT MAX(score)
        FROM results
        WHERE user_id=%s
        AND test_type='Aptitude'
    """, (session["user_id"],))

    best = cursor.fetchone()

    if best and best[0]:
        best_aptitude = best[0]

    # Total Tests

    cursor.execute("""
        SELECT COUNT(*)
        FROM results
        WHERE user_id=%s
    """, (session["user_id"],))

    tests_taken = cursor.fetchone()[0]

    # Chart Data

    labels = [
        "Resume Score",
        "Latest Aptitude",
        "Best Aptitude"
    ]

    scores = [
    resume_score,
    latest_aptitude * 10,
    best_aptitude * 10
    ]

    cursor.close()
    conn.close()

    return render_template(
        "performance.html",
        labels=labels,
        scores=scores,
        resume_score=resume_score,
        latest_aptitude=latest_aptitude,
        best_aptitude=best_aptitude,
        tests_taken=tests_taken
    )

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["admin"] = True

            return redirect("/admin_dashboard")

    return render_template("admin_login.html")


@app.route("/admin_dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM questions")
    total_questions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM aptitude_questions")
    total_aptitude = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_questions=total_questions,
        total_aptitude=total_aptitude
    )


@app.route("/admin_logout")
def admin_logout():

    session.pop("admin", None)

    return redirect("/admin")
@app.route("/view_users")
def view_users():

    if "admin" not in session:
        return redirect("/admin")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users"
    )

    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "view_users.html",
        users=users
    )
@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):

    if "admin" not in session:
        return redirect("/admin")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id=%s",
        (user_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/view_users")
@app.route("/add_question", methods=["GET", "POST"])
def add_question():

    if "admin" not in session:
        return redirect("/admin")

    if request.method == "POST":

        category = request.form["category"]
        question = request.form["question"]
        answer = request.form["answer"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO questions
            (category, question, answer)
            VALUES(%s,%s,%s)
            """,
            (category, question, answer)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/admin_dashboard")

    return render_template(
        "add_question.html"
    )
@app.route("/add_aptitude", methods=["GET", "POST"])
def add_aptitude():

    if "admin" not in session:
        return redirect("/admin")

    if request.method == "POST":

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO aptitude_questions
            (
            question,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_answer
            )
            VALUES(%s,%s,%s,%s,%s,%s)
            """,
            (
                request.form["question"],
                request.form["a"],
                request.form["b"],
                request.form["c"],
                request.form["d"],
                request.form["correct"]
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/admin_dashboard")

    return render_template(
        "add_aptitude.html"
    )
@app.route("/reports")
def reports():

    if "admin" not in session:
        return redirect("/admin")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM results"
    )

    reports = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "reports.html",
        reports=reports
    )
if __name__ == "__main__":
    app.run(debug=True)