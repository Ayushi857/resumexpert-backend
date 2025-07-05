from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openai
import os
from utils import extract_text_from_pdf, convert_text_to_pdf

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/match-job", methods=["POST"])
def match_job():
    data = request.get_json()
    resume = data.get("resume")
    job = data.get("job")

    prompt = f"""
You are an ATS system. Compare the following resume with the job description and give a match score out of 100 and explain why:

Resume:
{resume}

Job Description:
{job}

Output format:
Score: [number]/100
Explanation:
- Match areas
- Improvement areas
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        result = response["choices"][0]["message"]["content"]
        pdf_path = convert_text_to_pdf(result, filename="match_result.pdf")
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/rewrite-resume", methods=["POST"])
def rewrite_resume():
    data = request.get_json()
    resume = data.get("resume")

    prompt = f"""
You are a resume improvement assistant. Rewrite and improve the following resume:

{resume}

Return the improved version in clear bullet points or sections.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        result = response["choices"][0]["message"]["content"]
        pdf_path = convert_text_to_pdf(result, filename="rewritten_resume.pdf")
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/extract-text", methods=["POST"])
def extract_text():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    text = extract_text_from_pdf(file)
    return jsonify({"text": text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)