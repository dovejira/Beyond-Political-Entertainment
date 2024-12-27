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
    valence = logits[0].item()  # get the first value as valence( while the second one is arousal)

    return valence


# cuda module
device = torch.device("cuda" if torch.backends.cuda.is_available() else "cpu")
print(f"Using device: {device}")


model_path = "XLM-RoBERTa-large MSE"

# loading model
model, tokenizer = load_model(model_path)
model = model.to(device)

df = pd.read_csv('input.csv')

# add 'valence' into dataframe
df['valence'] = None

# tqdm module
for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing"):
    text = row['text']
    valence = analyze_sentiment(model, tokenizer, text, device)
    df.at[index, 'valence'] = valence

df.to_csv('output.csv', index=False)

print("Results saved to output.csv")
