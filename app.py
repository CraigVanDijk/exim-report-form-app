from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)
DATA_FILE = "report.xlsx"
RESPONSES_FILE = "responses.txt"  # Use Render's persistent directory

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        df = pd.read_excel(DATA_FILE)
        df["email"] = df["email"].str.strip().str.lower()
        user_reports = df[df["email"] == email]["report"].tolist()

        if user_reports:
            return render_template("form.html", email=email, reports=user_reports)
        else:
            return "No reports found for this email."

    email_from_query = request.args.get('email', None)

    if email_from_query:
        df = pd.read_excel(DATA_FILE)
        df["email"] = df["email"].str.strip().str.lower()
        user_reports = df[df["email"] == email_from_query]["report"].tolist()

        # Fetch previous reasons for the reports
        previous_reasons = {}
        if os.path.exists(RESPONSES_FILE):
            with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    if email_from_query in line:
                        parts = line.strip().split(", ")
                        report = parts[1].split(": ")[1]
                        reason = parts[2].split(": ")[1]
                        previous_reasons[report] = reason

        return render_template("form.html", email=email_from_query, reports=user_reports, selected_reports=user_reports, previous_reasons=previous_reasons)

    return render_template("login.html")

# Route to handle the form submission
@app.route("/submit", methods=["POST"])
def submit():
    email = request.form.get("email", "").strip().lower()
    selected_reports = request.form.getlist("report")

    if not selected_reports:
        return "No reports selected."

    lines = []
    for report in selected_reports:
        reason_key = f"reason_{report}"
        reason = request.form.get(reason_key, "").strip()
        line = f"Email: {email}, Report: {report}, Reason: {reason}\n"
        lines.append(line)

    # Write responses to the persistent text file on Render
    with open(RESPONSES_FILE, "a", encoding="utf-8") as f:
        f.writelines(lines)

    # Hardcoded Thank You Page after submission
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Thank You</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{
            background-color: #f8f9fa;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            font-family: Arial, sans-serif;
        }}
        .thank-you-box {{
            background: white;
            padding: 2rem 3rem;
            border-radius: 1rem;
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="thank-you-box">
        <h2 class="mb-3 text-success">Thank you!</h2>
        <p>Your responses have been recorded for <strong>{email}</strong>.</p>
        <a href="/?email={email}">Return to form</a>
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
