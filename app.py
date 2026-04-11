import os
from flask import Flask, request, jsonify, abort, render_template
from werkzeug.utils import secure_filename
import PyPDF2

__version__ = "1.0.1"

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(filepath):
    text = ""
    try:
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"
    except Exception:
        return ""
    return text.strip()


def parse_resume(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    name = lines[0] if lines else ""

    skills = []
    projects = []

    for line in lines:
        lower = line.lower()
        if "skill" in lower:
            skills.append(line)
        elif "project" in lower:
            projects.append(line)

    summary = " ".join(lines[1:5]) if len(lines) > 1 else ""

    return {
        "name": name,
        "summary": summary,
        "skills": skills,
        "projects": projects
    }


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/api/upload', methods=['POST'])
def upload():
    if 'resume' not in request.files:
        abort(400)

    file = request.files['resume']

    if file.filename == '' or not allowed_file(file.filename):
        abort(400)

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    text = extract_text_from_pdf(filepath)
    data = parse_resume(text)

    return jsonify(data)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
