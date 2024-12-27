from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd
from tqdm import tqdm

# cuda module
device = torch.device("cuda" if torch.backends.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# load the model and embedding model
model_name = "cardiffnlp/twitter-xlm-roberta-base-sentiment-multilingual"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)

df = pd.read_csv('input.csv')


# define the function
def classify_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    predicted_class = torch.argmax(logits, dim=1).item()

    # make the result to -1, 0, 1
    sentiment_map = {0: -1, 1: 0, 2: 1}
    return sentiment_map[predicted_class]


# tqdm module
df['sentiment'] = None
for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing texts"):
    sentiment = classify_sentiment(row['text'])
    df.at[index, 'sentiment'] = sentiment

df.to_csv('output.csv', index=False)

print("Results saved to output.csv")
