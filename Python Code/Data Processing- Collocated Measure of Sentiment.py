from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd
from tqdm import tqdm
import re

# if you use macbook, you can use this code to do the torch module
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using device: {device}")

# load model and embedding module
model_name = "cardiffnlp/twitter-xlm-roberta-base-sentiment-multilingual"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)

df = pd.read_csv('selected_eng_rep_att.csv')

# keyword list
china_related_words = [
    'China', 'Chinese', 'PRC', 'CCP', 'CPC', 'Beijing', 'Shanghai'
]


# define function to do the collocated measure
def classify_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    predicted_class = torch.argmax(logits, dim=1).item()
    # re-map the result to -1,1
    sentiment_map = {0: -1, 1: 0, 2: 1}
    return sentiment_map[predicted_class]


# extract context
def extract_context(text):
    words = text.split()
    for phrase in china_related_words:
        phrase_words = phrase.lower().split()
        phrase_len = len(phrase_words)

        for i in range(len(words) - phrase_len + 1):
            if [word.lower() for word in words[i:i + phrase_len]] == phrase_words:
                start = max(0, i - 5)
                end = min(len(words), i + phrase_len + 5)
                return ' '.join(words[start:end])

    return None


# tqdm module
sentiments11 = []
for text in tqdm(df['text'], desc="Processing texts"):
    context = extract_context(text)
    if context:
        sentiment = classify_sentiment(context)
        sentiments11.append(sentiment)
    else:
        sentiments11.append(None)

# add the result to dataframe
df['sentiment11'] = sentiments11

# 保存结果
df.to_csv('output.csv', index=False)

print("Results saved to output.csv")
