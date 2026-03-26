import os
from flask import Flask, request, render_template_string, abort
from werkzeug.utils import secure_filename
import PyPDF2
import unittest

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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


TEMPLATES = {
    "minimal": """
    <html>
    <head><title>{{name}}</title></head>
    <body style='font-family:sans-serif;'>
        <h1>{{name}}</h1>
        <p>{{summary}}</p>

        <h2>Skills</h2>
        <ul>{% for s in skills %}<li>{{s}}</li>{% endfor %}</ul>

        <h2>Projects</h2>
        <ul>{% for p in projects %}<li>{{p}}</li>{% endfor %}</ul>
    </body>
    </html>
    """,

    "card": """
    <html>
    <head>
    <style>
        body { font-family: Arial; background:#f4f4f4; }
        .card { background:white; padding:20px; margin:20px; border-radius:10px; }
    </style>
    </head>
    <body>
        <div class='card'>
            <h1>{{name}}</h1>
            <p>{{summary}}</p>
        </div>

        <div class='card'>
            <h2>Skills</h2>
            <ul>{% for s in skills %}<li>{{s}}</li>{% endfor %}</ul>
        </div>

        <div class='card'>
            <h2>Projects</h2>
            <ul>{% for p in projects %}<li>{{p}}</li>{% endfor %}</ul>
        </div>
    </body>
    </html>
    """
}


@app.route('/')
def home():
    return '''
    <h2>Upload Resume</h2>
    <form method="post" action="/upload" enctype="multipart/form-data">
        <input type="file" name="resume" required><br><br>
        <label>Select Template:</label>
        <select name="template">
            <option value="minimal">Minimal</option>
            <option value="card">Card</option>
        </select><br><br>
        <button type="submit">Generate Portfolio</button>
    </form>
    '''


@app.route('/upload', methods=['POST'])
def upload():
    if 'resume' not in request.files:
        abort(400)

    file = request.files['resume']

    if file.filename == '':
        abort(400)

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    template_choice = request.form.get('template', 'minimal')

    text = extract_text_from_pdf(filepath)
    data = parse_resume(text)

    template = TEMPLATES.get(template_choice, TEMPLATES['minimal'])

    return render_template_string(template, **data)


class TestResumeParser(unittest.TestCase):

    def test_empty_text(self):
        result = parse_resume("")
        self.assertEqual(result["name"], "")
        self.assertEqual(result["skills"], [])
        self.assertEqual(result["projects"], [])

    def test_basic_parsing(self):
        text = "John Doe\nSummary line\nSkills: Python\nProject: Website"
        result = parse_resume(text)
        self.assertEqual(result["name"], "John Doe")
        self.assertTrue(any("skill" in s.lower() for s in result["skills"]))
        self.assertTrue(any("project" in p.lower() for p in result["projects"]))

    def test_summary_extraction(self):
        text = "Jane Doe\nLine1\nLine2\nLine3\nLine4\nLine5"
        result = parse_resume(text)
        self.assertEqual(result["summary"], "Line1 Line2 Line3 Line4")

    def test_no_skills_projects(self):
        text = "Jane Doe\nJust some text"
        result = parse_resume(text)
        self.assertEqual(result["skills"], [])
        self.assertEqual(result["projects"], [])

    def test_name_only(self):
        text = "Only Name"
        result = parse_resume(text)
        self.assertEqual(result["name"], "Only Name")
        self.assertEqual(result["summary"], "")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
    else:
        app.run(debug=True)

