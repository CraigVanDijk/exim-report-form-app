from flask import Flask, render_template, request
import pandas as pd
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()  # Load from .env

GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
DATA_FILE = os.getenv("DATA_FILE")

scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_PATH, scope)
client = gspread.authorize(creds)

print("DEBUG - GOOGLE_CREDENTIALS_PATH:", GOOGLE_CREDENTIALS_PATH)


sheet = client.open(GOOGLE_SHEET_NAME).sheet1

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
        .no-email {{
            background: white;
            padding: 2rem 3rem;
            border-radius: 1rem;
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="no-email">
        <h2 class="mb-3 text-success">No email found! Please try again</h2>
        <p>Email used:<strong>{email}</strong>.</p>
        <a href="/?email={email}"></a>
    </div>
</body>
</html>
"""

    email_from_query = request.args.get('email', None)

    if email_from_query:
        df = pd.read_excel(DATA_FILE)
        df["email"] = df["email"].str.strip().str.lower()
        user_reports = df[df["email"] == email_from_query]["report"].tolist()

        # Fetch previous reasons for the reports
        previous_reasons = {}
        # Add your previous reason fetching logic here...

        return render_template("form.html", email=email_from_query, reports=user_reports, selected_reports=user_reports, previous_reasons=previous_reasons)

    return render_template("login.html")

@app.route("/submit", methods=["POST"])
def submit():
    email = request.form.get("email", "").strip().lower()
    selected_reports = request.form.getlist("report")
    lines = []

    # 1. If "I don't use any of these reports" is selected, record only that and return Thank You
    if request.form.get("no_reports_used"):
        lines.append([email, "NONE", "I don't use any of these reports"])
    else:
        # 2. If standard reports are selected, collect them
        if selected_reports:
            for report in selected_reports:
                reason_key = f"reason_{report}"
                reason = request.form.get(reason_key, "").strip()
                lines.append([email, report, reason])

        # 3. If "I use other reports" is selected, record that too
        if request.form.get("uses_other_reports"):
            other_reason = request.form.get("other_reports_reason", "").strip()
            lines.append([email, "OTHER", other_reason])

        # 4. If nothing was selected at all, return error page
        if not selected_reports and not request.form.get("uses_other_reports"):
            return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>No Reports Selected</title>
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
        .thank-you {{
            background: white;
            padding: 2rem 3rem;
            border-radius: 1rem;
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="thank-you">
        <h2 class="mb-3 text-danger">No reports selected</h2>
        <p>Please select at least one report or indicate that you don’t use any of them.</p>
        <a href="/" class="btn btn-primary mt-3">Go Back</a>
    </div>
</body>
</html>
"""

    # Write all collected responses to Google Sheets
    for line in lines:
        sheet.append_row(line)

    # Show thank you page
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
        .thank-you {{
            background: white;
            padding: 2rem 3rem;
            border-radius: 1rem;
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="thank-you">
        <h2 class="mb-3 text-success">Thank you for your submission!</h2>
        <p>Your responses have been recorded.</p>
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
