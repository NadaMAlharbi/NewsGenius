from flask import Flask, render_template, request
import json
import time  # تم استيراد مكتبة time لقياس زمن العمليات
from highlighting import normalize_sentence, generate_distinct_colors, highlight_text
from langchain_utils import extract_key_info, generate_summary, translate_to_arabic, match_summary_with_article
from scrapegraphai.graphs import SmartScraperGraph
from concurrent.futures import ThreadPoolExecutor  # لاستدعاء الخيوط المتعددة
import os  # لاستخدام عدد الأنوية المتاحة
import re  # لاستخدام التعبيرات المنتظمة لتنظيف النص

# Initialize Flask app
app = Flask(__name__)

# تحديد عدد الأنوية المتاحة في النظام بشكل تلقائي
max_workers = os.cpu_count() * 2  # مضاعفة عدد الأنوية للحصول على عدد أكبر من العمال


# دالة لتنظيف المقالة من الإعلانات والرعاية والروابط الخارجية
def remove_unwanted_content(text):
    # قائمة التعبيرات المنتظمة لإزالة الفقرات غير المرغوبة
    unwanted_patterns = [
        r'\bSponsored\b',  # حذف الفقرات التي تحتوي على كلمة "Sponsored"
        r'Advertisement',  # حذف الفقرات التي تحتوي على "Advertisement"
        r'https?://[^\s]+',  # حذف الروابط الخارجية
    ]

    # تطبيق الفلترة باستخدام التعبيرات المنتظمة
    for pattern in unwanted_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return text


# معالجة المقالة أو استخدام SmartScraperGraph مع الخيوط المتعددة
def process_input(input_data: str, input_type: str) -> tuple:
    if input_type == "smart_scraper":
        # إعداد SmartScraperGraph
        graph_config = {
            "llm": {
                "api_key": "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",
                # استبدل بمفتاح API الخاص بك
                "model": "openai/gpt-4o-mini",
            },
            "verbose": False,
            "headless": True,
        }

        # استخدم SmartScraperGraph لاستخراج المعلومات
        smart_scraper_graph = SmartScraperGraph(
            prompt="""Extract the **Title** and the **Content** of the article. 
            Ignore metadata like author, date, and other unnecessary information.""",
            source=input_data,  # URL المدخل من المستخدم
            config=graph_config
        )

        start_time = time.time()  # قياس زمن تشغيل SmartScraperGraph
        result = smart_scraper_graph.run()
        print(f"Time taken for SmartScraperGraph: {time.time() - start_time} seconds")

        # استخراج الحقول المطلوبة من JSON (الـ Title و Content مثلاً)
        if result and "Content" in result:
            extracted_text = result["Content"]  # استخراج المحتوى كـنص
            title = result.get("Title", "")  # استخراج العنوان إذا كان متاحاً
            extracted_text = f"{title}\n\n{extracted_text}"  # دمج العنوان والمحتوى كنص مع سطر جديد بينهما
        else:
            extracted_text = ""  # إذا لم يتم العثور على محتوى

    else:
        # إذا كان المدخل نصًا، نستخدمه مباشرة
        extracted_text = input_data

    # إزالة الفقرات غير المرغوبة من النص
    cleaned_text = remove_unwanted_content(extracted_text)

    # التأكد من أن النص المستخرج أو المدخل ليس فارغًا
    if not cleaned_text.strip():
        raise ValueError("The extracted text or article content is empty after cleaning. Please provide a valid input.")

    # تنفيذ المهام المعقدة بشكل متوازي باستخدام ThreadPoolExecutor مع max_workers
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # إرسال المهام بشكل متوازي للتنفيذ
        key_info_future = executor.submit(extract_key_info, cleaned_text)
        summary_future = executor.submit(generate_summary, cleaned_text, key_info_future.result())
        arabic_summary_future = executor.submit(translate_to_arabic, summary_future.result())

        # استرجاع النتائج بعد انتهاء المهام
        key_info = key_info_future.result()
        summary = summary_future.result()
        arabic_summary = arabic_summary_future.result()

    # قياس الزمن لدالة match_summary_with_article
    start_time = time.time()
    matched_sentences = match_summary_with_article(cleaned_text, summary)
    print(f"Time taken for match_summary_with_article: {time.time() - start_time} seconds")

    return arabic_summary, summary, cleaned_text, matched_sentences


# تمييز المقالة والخلاصة
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


# عرض الواجهة
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_type = request.form.get('input_type')  # تحديد نوع المدخل (url, text, smart_scraper)
        input_data = request.form.get('article') if input_type != "smart_scraper" else request.form.get('article_url')

        if input_data:
            try:
                # معالجة المدخل النصي أو URL
                arabic_summary, summary, article, matched_sentences = process_input(input_data, input_type)

                # تعديل النص لإضافة سطر جديد بشكل صحيح في HTML
                arabic_summary = arabic_summary.replace('\n', '<br>')
                summary = summary.replace('\n', '<br>')

                # تمييز المقالة والخلاصة
                highlighted_summary, highlighted_article = highlight_summary_and_article(article, summary,
                                                                                         matched_sentences)

                # عرض النتائج باستخدام |safe في قالب HTML
                return render_template('result.html', arabic_summary=arabic_summary, summary=summary,
                                       highlighted_article=highlighted_article, highlighted_summary=highlighted_summary)
            except ValueError as e:
                return render_template('form.html', error_message=str(e))

    return render_template('form.html')


# تشغيل التطبيق
if __name__ == "__main__":
    app.run(debug=True, port=5009)