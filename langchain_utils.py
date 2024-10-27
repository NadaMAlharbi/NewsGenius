from dotenv import load_dotenv
load_dotenv()
import re  # To clean text using regular expressions
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.schema import SystemMessage
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
import os
import json
from langsmith import traceable


# Setting up API keys using environment variables
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Nada_2"

# Initialize LLM once for reuse
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

# Function to create a vector store using FAISS
def create_vectorstore(text: str) -> FAISS:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_text(text)
    embeddings = OpenAIEmbeddings()
    return FAISS.from_texts(texts, embeddings)

@traceable
# Function to extract key information from the article
def extract_key_info(article: str) -> dict:
    vectorstore = create_vectorstore(article)
    retriever = vectorstore.as_retriever()

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever
    )

    questions = [
        "What are the main technical concepts discussed in this article?",
        "What are the key findings or advancements mentioned?",
        "What potential impacts or applications are discussed?"
        ]

    return {question: qa_chain.run(question) for question in questions}

@traceable
# Function to generate a structured summary from the article and key information
def generate_summary(article: str, key_info: dict) -> str:
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content="You are an expert in summarizing technical news articles. Your task is to create a concise and structured summary of the given article, focusing on the key technical information."),
        HumanMessagePromptTemplate.from_template("""
Article: {article}

Key Information:
{key_info}

Please provide a structured summary of this article, following these strict guidelines:

1. **Start with what was done**: Begin the summary by explaining what was developed, achieved, issued, or discovered (e.g., "The company developed a new AI system").
2. **State the goal**: In the second sentence, explicitly mention the goal or purpose behind this action (e.g., "The goal of this development is to improve customer service").
3. **Describe the features**: Highlight key features, advantages, or disadvantages, and ensure that any important numbers are enclosed in parentheses (e.g., "The new system reduced processing time by (30%)").
4. **Future plans**: Conclude with future expectations or anticipated actions, such as "It is expected" . Do not include specific dates unless explicitly mentioned in the article. Focus on general future developments.

Ensure that proper nouns or brand names are transliterated into Arabic and their English name is placed in parentheses for the first occurrence (Google).

Format your response as follows:

[Title]


[Summary]

The summary should be natural and flowing without using bullet points or headers.
""")
    ])
    llm_s = ChatOpenAI(model_name="ft:gpt-4o-mini-2024-07-18:personal:summary3:AHmKWopu")
    chain = LLMChain(llm=llm_s, prompt=prompt)
    return chain.run(article=article, key_info=str(key_info))

@traceable
# Function to translate text to Arabic
def translate_to_arabic(text: str) -> str:
    prompt_s = ChatPromptTemplate.from_messages([
        SystemMessage(
            content="You are an expert translator specializing in technical translations from English to Arabic. Your task is to provide an accurate and fluent translation that preserves the technical nuances and structure of the original text."),
        HumanMessagePromptTemplate.from_template(""" {text}, translate the following text to Arabic following these strict guidelines:

1. **Start with what was done**: Translate the first sentence to describe what the company, government, or organization did (e.g., announced, developed, issued, approved, etc.).
2. **State the goal**: In the second sentence, explicitly mention the goal or purpose behind this action.
3. **Describe the features**: Translate the third sentence, highlighting key features (advantages or disadvantages), and ensure that any important numbers are enclosed in parentheses (e.g., "30%" becomes "(30%)").
4. **Future plans**: Translate the future plans or expectations (e.g., "It is expected" or "من المتوقع") without adding any dates unless they are explicitly mentioned in the article. Focus on expected actions or future developments rather than specific dates.

Additional Guidelines:
- Ensure that proper nouns (like companies or brands) are transliterated into Arabic and their English name is placed in parentheses for the first occurrence (e.g., جوجل(Google)).
- Ensure that all numerical values, such as percentages or statistics, are placed in parentheses (e.g., "30%" becomes "(30%)").

Provide the translation in this structured format:
[Arabic Title]

[Translation]

The translation should flow naturally as a cohesive paragraph, without using headers or numbered sections.

""")

    ])
    Fine_tunes_llm = ChatOpenAI(model_name="ft:gpt-4o-mini-2024-07-18:personal:translate:AHmy4few")
    chain = LLMChain(llm=Fine_tunes_llm, prompt=prompt_s)
    return chain.run(text=text)

# Function to clean JSON output from LLM results
def clean_json_output(output):
    json_match = re.search(r'\[\s*{.*?}\s*\]', output, re.DOTALL)
    if json_match:
        return json_match.group(0)  # Extract the JSON array
    return output

@traceable
# Function to match summary sentences with corresponding article sentences
def match_summary_with_article(article: str, summary: str) -> str:
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content="You are tasked with analyzing an article and its summary. Your goal is to identify and match each sentence in the summary with the corresponding sentence(s) in the article. The matching sentence(s) may be identical or convey the same meaning, even if rephrased. Provide an output where each sentence from the summary is mapped to one or more corresponding sentences from the article."),
        HumanMessagePromptTemplate.from_template("""
Instruction:
Provide the output strictly as a JSON array. Do not include any additional text or explanations. Each object in the JSON array should have the following fields:

- "summary_sentence": The exact text of the summary sentence.
- "article_sentences": An array containing one or more sentences from the article that correspond to the summary sentence.

Ensure that the output is valid JSON and contains no extra characters or formatting outside of the array.
the Summary:
{summary}/n/n

Article:
{article}                                                                                  
""")
    ])

    llm_h = ChatOpenAI(model_name="gpt-4o")
    chain = LLMChain(llm=llm_h, prompt=prompt)

    output = chain.run(article=article, summary=summary)

    cleaned_output = clean_json_output(output)
    try:
        parsed_output = json.loads(cleaned_output)  # Parse the cleaned JSON string
        return json.dumps(parsed_output)  # Return the validated and cleaned JSON string
    except json.JSONDecodeError as e:
        print("Error: Invalid JSON returned by LLM.")
        print("Raw Output:", output)  # Log the raw output for debugging
        return output  # Return the raw output if it's not valid JSON
