import re

def count_emoticons(text):
    emoticon_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002700-\U000027BF\U000024C2-\U0001F251]')
    return len(emoticon_pattern.findall(text))

def highlight_words_in_text(text, words):
    """
    Highlights each monitored word in the given text (case-insensitive),
    surrounding it with ** to make it bold in Markdown (works for both Discord and Telegram).
    """
    pattern = r'(' + '|'.join(re.escape(word) for word in words) + r')'
    
    def bold_replacement(match):
        return f"**{match.group(1)}**"

    highlighted_text = re.sub(pattern, bold_replacement, text, flags=re.IGNORECASE)
    return highlighted_text