import torch
import pandas as pd
from transformers import XLMRobertaForSequenceClassification, XLMRobertaTokenizer
from tqdm import tqdm


def load_model(model_path):
    model = XLMRobertaForSequenceClassification.from_pretrained(model_path)
    tokenizer = XLMRobertaTokenizer.from_pretrained(model_path)
    return model, tokenizer


def analyze_sentiment(model, tokenizer, text, device):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits.squeeze()
    valence = logits[0].item()

    return valence


# define function to do the collocated measure
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


# if you use macbook, you can use this code to do the torch module
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using device: {device}")

model_path = "XLM-RoBERTa-large MSE"

# Loading model
model, tokenizer = load_model(model_path)
model = model.to(device)

df = pd.read_csv('input.csv')

# keyword list
china_related_words = [
    'China', 'Chinese', 'PRC', 'CCP', 'CPC', 'Beijing', 'Shanghai',
]


valence11 = []

# tqdm module
for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing"):
    text = row['text']
    context = extract_context(text)
    if context:
        valence = analyze_sentiment(model, tokenizer, context, device)
        valence11.append(valence)
    else:
        valence11.append(None)

# add the result to dataframe
df['valence11'] = valence11

df.to_csv('output.csv', index=False)

print("Results saved to output.csv")
