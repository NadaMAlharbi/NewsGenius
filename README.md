# NewsGenius

**NewsGenius** is an AI-powered web application designed to analyze news articles, providing capabilities to **summarize**, **translate**, and **highlight key information**. By leveraging advanced language models, the system ensures efficient processing of large volumes of content, delivering **quick insights** and facilitating **seamless navigation** through critical information.

### Deployed Application:
[NewsGenius on Railway](https://newsgenius.up.railway.app)

## Features

- **English Input Only**: The system accepts articles and URLs written in English for analysis.
- **Bilingual Output**: Provides summaries in Arabic (according to SDAIA's writing standards) and English, along with the full English article.
- **Text Highlighting**: Key sections in the article and summary are highlighted for easy navigation.
- **Login System**: Authentication is required to use the article analysis functionality.
- **Responsive Design**: The interface adjusts seamlessly to different screen sizes and is mobile-friendly.
- **Copy to Clipboard**: Users can easily copy the Arabic summary to their clipboard.

## Local Installation

If you want to run the application locally instead of using the deployed version, follow these steps:

### Prerequisites

Ensure you have Python 3.9+ and pip installed.

### Clone the Repository

```bash
git clone https://github.com/NadaMAlharbi/NewsGenius.git
cd NewsGenius
```

### Install Dependencies

Install the necessary Python packages by running:

```bash
pip install -r requirements.txt
```

### Start the Application

Run the Flask application:

```bash
python app.py
```

The application will be accessible at `http://localhost:5002`.

## Usage

1. Open the deployed application at [NewsGenius on Railway](https://newsgenius.up.railway.app).
2. Enter a URL or article text in English for analysis.
3. Click the "Analyze" button (login is required to use this feature).
4. View the generated summaries in Arabic and English, with highlighted sections for easy navigation.
5. Optionally, you can copy the Arabic summary to your clipboard.

## Project Structure

- `app.py`: The main Flask application file that handles routing and integration with language models.
- `highlighting.py`: Contains logic for highlighting matched sentences between the article and summary.
- `langchain_utils.py`: Utility functions for content extraction, summarization, and translation using LangChain.
- `templates/`: Contains HTML files for the input and result pages.
    - `form.html`: The input form where users can submit URLs or articles.
    - `result.html`: Displays the processed article and summary.
- `static/`: Stores static assets like CSS styles and the project logo.
    - `styless.css`: Contains the styles for the web pages.
    - `logo.png`: The project logo.

## Technologies Used

- **Python 3.9+**
- **Flask**: Backend framework to handle web requests.
- **LangChain Framework**: Manages the flow and operations within the AI model.
- **Fine-Tuning**: Adapts pre-trained models to fit specific task needs.
- **Retrieval-Augmented Generation (RAG)**: Used to enhance the performance of language models by integrating external knowledge during generation.
- **Bootstrap**: For responsive and modern design.
- **aiohttp**: For asynchronous web requests to improve performance.
- **HTML/CSS**: For the frontend design.
- **Jinja2**: Templating engine for rendering dynamic content.

## Contact

For more information, feel free to contact:

- Nada Alharbi at `alharbi13nada@gmail.com`
- Musaed Albedhani at `Owdm.ai@gmail.com`
