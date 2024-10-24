from flask import Flask, render_template, request
import json
from highlighting import normalize_sentence, generate_distinct_colors, highlight_text
from langchain_utils import extract_key_info, generate_summary, translate_to_arabic, match_summary_with_article
from concurrent.futures import ThreadPoolExecutor
import os
import re
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter

app = Flask(__name__)

max_workers = os.cpu_count() * 2

# Function to use Extractor API to clean the text and split it into smaller chunks if it's too long
def get_documents_from_web(url):
    api_key = "25ed2d37fd3cd193d679e28dab9bf23ec0e3bd06"
    extractor_url = f"https://extractorapi.com/api/v1/extractor/?apikey={api_key}&url={url}"

    response = requests.get(extractor_url)

    if response.status_code == 200:
        data = response.json()
        document_text = data.get("text", "")
    else:
        print(f"Failed to fetch the webpage: {response.status_code}")
        return ""

    soup = BeautifulSoup(document_text, "html.parser")
    cleaned_text = soup.get_text()

    cleaned_text = re.sub(r'[^\w\s.,!?؛،]', '', cleaned_text)

    # Split the text into smaller chunks if it's too long using RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    docs = splitter.split_text(cleaned_text)

    # Combine the chunks together into one text since we don't need to process each chunk separately
    full_text = "\n\n".join(docs)

    return full_text

# Function to remove unwanted content such as sponsored sections, ads, and external links
def remove_unwanted_content(text):
    unwanted_patterns = [
        r'\bSponsored\b',
        r'Advertisement',
        r'https?://[^\s]+',
    ]

    for pattern in unwanted_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return text

# Function to process input, whether it's a URL (using Extractor API) or plain text
def process_input(input_data: str, input_type: str) -> tuple:
    if input_type == "url":
        extracted_text = get_documents_from_web(input_data)
    else:
        extracted_text = input_data

    cleaned_text = remove_unwanted_content(extracted_text)

    if not cleaned_text.strip():
        raise ValueError("The extracted text or article content is empty after cleaning. Please provide a valid input.")

    # Execute tasks in parallel using ThreadPoolExecutor with max_workers
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        key_info_future = executor.submit(extract_key_info, cleaned_text)
        summary_future = executor.submit(generate_summary, cleaned_text, key_info_future.result())
        arabic_summary_future = executor.submit(translate_to_arabic, summary_future.result())
        match_sentences_future = executor.submit(match_summary_with_article, cleaned_text, summary_future.result())

        key_info = key_info_future.result()
        summary = summary_future.result()
        arabic_summary = arabic_summary_future.result()
        matched_sentences = match_sentences_future.result()

    arabic_summary = arabic_summary.replace('\n', '<br>')
    summary = summary.replace('\n', '<br>')

    highlighted_summary, highlighted_article = highlight_summary_and_article(cleaned_text, summary, matched_sentences)

    return arabic_summary, summary, cleaned_text, matched_sentences

# Function to highlight matching sentences in both the summary and article
def highlight_summary_and_article(article, summary, matched_sentences):
    try:
        parsed_sentences = json.loads(matched_sentences) if isinstance(matched_sentences, str) else matched_sentences
        colors = generate_distinct_colors(len(parsed_sentences))

        highlighted_article = article
        highlighted_summary = summary
        for index, mapping in enumerate(parsed_sentences):
            color = colors[index]
            summary_sentence = normalize_sentence(mapping["summary_sentence"])
            highlighted_summary = highlight_text(highlighted_summary, [summary_sentence], color)

            for article_sentence in mapping["article_sentences"]:
                normalized_article_sentence = normalize_sentence(article_sentence)
                highlighted_article = highlight_text(highlighted_article, [normalized_article_sentence], color)

        return highlighted_summary, highlighted_article
    except json.JSONDecodeError:
        return summary, article
    except Exception as e:
        return summary, article

# Route to handle the form submission and display the results
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_type = request.form.get('input_type')
        input_data = request.form.get('article') if input_type == "text" else request.form.get('article_url')

        if input_data:
            try:
                arabic_summary, summary, article, matched_sentences = process_input(input_data, input_type)

                arabic_summary = arabic_summary.replace('\n', '<br>')
                summary = summary.replace('\n', '<br>')

                highlighted_summary, highlighted_article = highlight_summary_and_article(article, summary, matched_sentences)

                return render_template('result.html', arabic_summary=arabic_summary, summary=summary,
                                       highlighted_article=highlighted_article, highlighted_summary=highlighted_summary)
            except ValueError as e:
                return render_template('form.html', error_message=str(e))

    return render_template('form.html')

# Start the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=5001)
