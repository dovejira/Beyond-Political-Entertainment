import pandas as pd
import fasttext
from tqdm import tqdm

df = pd.read_csv('input.csv')

# Load fastText language classfication model
# can use the terminal with the command
# !curl -O https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
model = fasttext.load_model('lid.176.bin')

# detect_language function
def detect_language(text):
    if pd.isna(text):  # check the NaN value
        return 'unknown'
    if not isinstance(text, str):  # transform data into str if it's not
        text = str(text)
    text = text.replace('\n', ' ')  # clean data
    predictions = model.predict(text, k=1)
    return predictions[0][0].replace('__label__', '')

# tqdm module
tqdm.pandas()
df['language'] = df['text'].progress_apply(detect_language)

# save df to csv
df_ch = df[df['language'] == 'zh']
df_en = df[df['language'] == 'en']

df_ch.to_csv('output_ch.csv', index=False)
df_en.to_csv('output_en.csv', index=False)
