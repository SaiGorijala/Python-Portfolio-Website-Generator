import os
from flask import Flask, request, jsonify, abort, render_template
from werkzeug.utils import secure_filename
import PyPDF2

# Application version
__version__ = "1.0.2"

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
    return render_template("index.html", version=__version__)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        abort(400, "No file part")

    file = request.files['file']

    if file.filename == '':
        abort(400, "No selected file")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        text = extract_text_from_pdf(filepath)
        parsed = parse_resume(text)

        return jsonify({
            "version": __version__,
            "parsed": parsed
        })

    abort(400, "Invalid file type")


if __name__ == "__main__":
    # IMPORTANT: Run on 0.0.0.0 so EC2 can expose it
    app.run(host="0.0.0.0", port=5000, debug=True)
