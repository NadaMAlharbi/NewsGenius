# NewsGenius

**NewsGenius** is an AI-powered web application designed to analyze news articles by providing capabilities to **summarize**, **translate**, and **highlight key information**. Leveraging advanced language models, the system processes large volumes of content efficiently, delivering **quick insights** and facilitating **easy navigation** through critical information.


## Features

- **English Input Only**: Accepts articles and URLs written in English for analysis.
- **Bilingual Output**: Generates summaries in Arabic (according to SDAIA's writing standards) and English, along with the full English article.
- **Text Highlighting**: Highlights key sections in the article and summary for easy navigation.
- **Login System**: Requires authentication to access article analysis functionality.
- **Responsive Design**: Adjusts seamlessly to different screen sizes and is mobile-friendly.
- **Copy to Clipboard**: Allows easy copying of the Arabic summary.

## Local Installation

To run the application locally, follow these steps:

### Prerequisites

- Python 3.9+

### Install Dependencies

Install the necessary Python packages:

```bash
pip install -r requirements.txt
```

### Start the Application

Run the Flask application:

```bash
python app.py
```

The application will be accessible at `http://localhost:5003`.

## Usage

1. Open the application: Access it in your web browser at the specified URL (e.g., http://localhost:5003).
2. Enter an English URL or article text for analysis.
3. Click "Analyze" (login required).
4. View the summaries in Arabic and English, with highlighted sections.
5. Copy the Arabic summary to your clipboard if needed.

## Project Structure

- **`app.py`**: Main Flask application file for routing and model integration.
- **`highlighting.py`**: Contains logic for highlighting matched sentences between the article and summary.
- **`langchain_utils.py`**: Utilities for content extraction, summarization, and translation using LangChain.
- **`templates/`**: HTML files for input and result pages.
    - `form.html`: Input form for URLs or articles.
    - `result.html`: Displays processed article and summary.
- **`static/`**: Static assets like CSS and project logo.
    - `styles.css`: Styles for web pages.
    - `logo.png`: Project logo.

## Technologies Used

- **Python 3.9+**
- **Flask**: Backend framework for handling web requests.
- **LangChain Framework**: Manages flow and operations within the AI model.
- **Fine-Tuning**: Adapts pre-trained models to task-specific needs.
- **Retrieval-Augmented Generation (RAG)**: Enhances language models with external knowledge.
- **Bootstrap**: Provides responsive, modern design.
- **aiohttp**: For asynchronous web requests to improve performance.
- **HTML/CSS**: Frontend design.
- **Jinja2**: Templating engine for rendering dynamic content.

## Contact

For more information, feel free to contact me:

- Nada Alharbi at alharbi13nada@gmail.com
