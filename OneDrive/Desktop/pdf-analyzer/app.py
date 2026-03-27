from flask import Flask, render_template, request
import PyPDF2
import requests

app = Flask(__name__)

# 🔹 Extract text safely
def extract_text(pdf_file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content
    except Exception as e:
        print("PDF Error:", e)
    return text


# 🔹 Fallback summary (always works)
def summarize_text(text):
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    sentences.sort(key=len, reverse=True)
    return '. '.join(sentences[:5])


# 🔹 AI Summary (SAFE)
def get_summary_api(text):
    try:
        url = "https://api.nlpcloud.io/v1/bart-large-cnn/summarization"

        headers = {
            "Authorization": "9a0f999643bac7ee16bae7d300e00e60f341e3ef",  # 👈 PUT YOUR KEY HERE
            "Content-Type": "application/json"
        }

        payload = {
            "text": text[:1000]
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json().get("summary_text", summarize_text(text))
        else:
            print("API Error:", response.status_code)
            return summarize_text(text)

    except Exception as e:
        print("API Exception:", e)
        return summarize_text(text)


# 🔹 Keyword search
def search_keyword(text, keyword):
    if keyword:
        return keyword.lower() in text.lower()
    return None


# 🔹 Text stats
def get_text_stats(text):
    words = text.split()
    word_count = len(words)
    reading_time = max(1, word_count // 200)
    return word_count, reading_time


@app.route('/', methods=['GET', 'POST'])
def index():
    text = ""
    summary = ""
    keyword_result = None
    word_count = 0
    reading_time = 0

    if request.method == 'POST':
        try:
            file = request.files.get('pdf')
            keyword = request.form.get('keyword')

            if not file or not file.filename.endswith('.pdf'):
                return "Please upload a valid PDF file"

            text = extract_text(file)

            if not text.strip():
                return "Could not extract text from PDF"

            # 🔥 AI summary with fallback
            summary = get_summary_api(text)

            keyword_result = search_keyword(text, keyword)
            word_count, reading_time = get_text_stats(text)

            text = text[:1000]

        except Exception as e:
            return f"Error occurred: {str(e)}"

    return render_template(
        'index.html',
        text=text,
        summary=summary,
        keyword_result=keyword_result,
        word_count=word_count,
        reading_time=reading_time
    )


if __name__ == "__main__":
    app.run(debug=True)