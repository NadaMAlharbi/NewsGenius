# Function to normalize sentences (remove trailing period)
def normalize_sentence(sentence):
    return sentence.rstrip(".")

# Function to provide a predefined set of distinct pastel colors
def generate_distinct_colors(n):
    # Fixed list of colors (LemonChiffon, MintCream, LightCyan, MistyRose, PeachPuff, LavenderBlush, Honeydew)
    colors = ['#FFFACD', '#D3F8E2', '#D4F1F4', '#FFE4E1', '#FFDAB9', '#FFF0F5', '#F0FFF0']
    # Return enough colors for `n` sentences by cycling through the list if necessary
    return [colors[i % len(colors)] for i in range(n)]

# Function to highlight matched sentences in the text
def highlight_text(text, matched_sentences, color):
    for sentence in matched_sentences:
        normalized_sentence = normalize_sentence(sentence)
        if normalized_sentence in text:
            text = text.replace(normalized_sentence, f'<mark class="highlight" style="background-color: {color};">{normalized_sentence}</mark>')
    return text
