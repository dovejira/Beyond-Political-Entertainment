import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

data_path = "input.csv"
data = pd.read_csv(data_path)

# Load the SentenceTransformer model
embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Initialize the BERTopic model
# Do not specify the number of topics, using the default mode
model = BERTopic(embedding_model=embedding_model)

# Perform clustering on the text data
# also can be used to 'description'
texts = data['text'].tolist()
topics, probs = model.fit_transform(texts)

# Retrieve the top ten keywords and top five examples for each topic
topic_info = model.get_topic_info()

# Construct a detailed topic information table
output_topics = []
for topic_id in topic_info['Topic']:
    if topic_id == -1:  # Skip unassigned noise topics
        continue

    # Retrieve keywords
    keywords = model.get_topic(topic_id)
    top_keywords = ", ".join([keyword[0] for keyword in keywords[:10]])

    # Retrieve representative documents for the topic
    examples = model.get_representative_docs(topic_id)
    top_examples = examples[:5] if examples else []

    # Add to the output list
    output_topics.append({
        "topic_id": topic_id,
        "keywords": top_keywords,
        "examples": " | ".join(top_examples)
    })

# Convert to DataFrame and export to CSV
output_topics_df = pd.DataFrame(output_topics)
output_topics_df.to_csv("topics_details.csv", index=False, encoding="utf-8-sig")

# Add topic and probability columns to the original file
data['topic_id'] = topics
if probs is not None:
    data['topic_probability'] = probs

# Save the updated data
updated_data_path = "output.csv"
data.to_csv(updated_data_path, index=False, encoding="utf-8-sig")

print("Clustering completed! Topic details have been saved to 'topics_details.csv', and the updated data has been saved to 'output.csv'.")
