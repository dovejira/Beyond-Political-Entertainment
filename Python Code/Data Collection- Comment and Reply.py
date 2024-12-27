import csv
import time
import pandas as pd
from googleapiclient.discovery import build
from tqdm import tqdm

# Use offcial API key(s)
API_KEYS = []
api_key_index = 0
youtube = build('youtube', 'v3', developerKey=API_KEYS[api_key_index])


# Switch API key auto
def switch_api_key():
    global api_key_index, youtube
    api_key_index += 1
    if api_key_index < len(API_KEYS):
        youtube = build('youtube', 'v3', developerKey=API_KEYS[api_key_index])
        print(f"Switch to API key {api_key_index + 1}")
    else:
        print("All API key run out，end the process")
        exit()

# Check if API key is need to be changed
def check_api_error(e):
    if any(error_keyword in str(e).lower() for error_keyword in ["quota", "forbidden"]):
        print(f"API key error: {e}. switching API key...")
        switch_api_key()
        time.sleep(1)
    else:
        print(f"Not API Error: {e}. Skip the video")

# channel details
def get_channel_details(channel_id):
    try:
        results = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        ).execute()

        if results['items']:
            channel = results['items'][0]
            snippet = channel['snippet']
            stats = channel['statistics']
            return {
                "channel_title": snippet['title'],
                "subscriber_count": stats.get('subscriberCount', 0),
                "video_count": stats.get('videoCount', 0),
                "view_count": stats.get('viewCount', 0),
                "channel_country": snippet.get('country', 'N/A'),
                "is_verified": snippet.get('isVerified', False),
                "registration_date": snippet['publishedAt']
            }
    except Exception as e:
        check_api_error(e)

    return {}

# comments details
def get_comments(video_id):
    comments = []
    try:
        results = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            textFormat="plainText"
        ).execute()

        while results:
            for item in results['items']:
                comment_details = item['snippet']['topLevelComment']['snippet']
                commenter_channel_id = comment_details['authorChannelId']['value']
                comment = {
                    "comment_id": item['snippet']['topLevelComment']['id'],
                    "author_id": commenter_channel_id,
                    "author_name": comment_details['authorDisplayName'],
                    "text": comment_details['textDisplay'].replace('<br>', '\n').replace('\n', ' ').strip(),
                    "like_count": comment_details['likeCount'],
                    "published_at": comment_details['publishedAt'],
                    "commenter_channel_details": get_channel_details(commenter_channel_id)
                }
                comments.append(comment)

            if 'nextPageToken' in results:
                results = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    pageToken=results['nextPageToken'],
                    maxResults=100,
                    textFormat="plainText"
                ).execute()
            else:
                break
    except Exception as e:
        check_api_error(e)

    return comments

# replies details
def get_replies(parent_id, video_id):
    replies = []
    try:
        results = youtube.comments().list(
            part="snippet",
            parentId=parent_id,
            maxResults=100,
            textFormat="plainText"
        ).execute()

        while results:
            for item in results['items']:
                reply_details = item['snippet']
                replier_channel_id = reply_details['authorChannelId']['value']
                reply = {
                    "reply_id": item['id'],
                    "parent_comment_id": parent_id,
                    "author_id": replier_channel_id,
                    "author_name": reply_details['authorDisplayName'],
                    "text": reply_details['textDisplay'].replace('<br>', '\n').replace('\n', ' ').strip(),
                    "like_count": reply_details['likeCount'],
                    "published_at": reply_details['publishedAt'],
                    "replier_channel_details": get_channel_details(replier_channel_id)
                }
                replies.append(reply)

            if 'nextPageToken' in results:
                results = youtube.comments().list(
                    part="snippet",
                    parentId=parent_id,
                    pageToken=results['nextPageToken'],
                    maxResults=100,
                    textFormat="plainText"
                ).execute()
            else:
                break
    except Exception as e:
        check_api_error(e)

    return replies

# save to csv
def save_to_csv(video_id, comments, comments_csv, replies_csv):
    write_header = False
    # Check if files is already saved
    try:
        with open(comments_csv, 'r', newline='', encoding='utf-8') as f:
            pass
    except FileNotFoundError:
        write_header = True

    with open(comments_csv, 'a', newline='', encoding='utf-8') as c_file, \
         open(replies_csv, 'a', newline='', encoding='utf-8') as r_file:

        comments_writer = csv.writer(c_file)
        replies_writer = csv.writer(r_file)

        if write_header:
            comments_writer.writerow(["comment_id", "video_id", "author_id", "author_name", "author_country", "text",
                                      "like_count", "published_at", "subscriber_count", "video_count", "view_count",
                                      "is_verified", "registration_date"])
            replies_writer.writerow(["reply_id", "parent_comment_id", "video_id", "author_id", "author_country", "text",
                                     "like_count", "published_at", "subscriber_count", "video_count", "view_count",
                                     "is_verified", "registration_date"])

        for comment in comments:
            comments_writer.writerow([
                comment['comment_id'], video_id, comment['author_id'], comment['author_name'],
                comment['commenter_channel_details'].get('channel_country'), comment['text'],
                comment['like_count'], comment['published_at'],
                comment['commenter_channel_details'].get('subscriber_count'),
                comment['commenter_channel_details'].get('video_count'),
                comment['commenter_channel_details'].get('view_count'),
                comment['commenter_channel_details'].get('is_verified'),
                comment['commenter_channel_details'].get('registration_date')
            ])

            replies = get_replies(comment['comment_id'], video_id)
            for reply in replies:
                replies_writer.writerow([
                    reply['reply_id'], comment['comment_id'], video_id, reply['author_id'],
                    reply['replier_channel_details'].get('channel_country'), reply['text'],
                    reply['like_count'], reply['published_at'],
                    reply['replier_channel_details'].get('subscriber_count'),
                    reply['replier_channel_details'].get('video_count'),
                    reply['replier_channel_details'].get('view_count'),
                    reply['replier_channel_details'].get('is_verified'),
                    reply['replier_channel_details'].get('registration_date')
                ])

# main function
def main():
    input_file = 'input.csv'  # input CSV
    comments_csv = 'comment.csv'  # comment output CSV
    replies_csv = 'reply.csv'  # reply output CSV

    df = pd.read_csv(input_file)
    start_index = 0

    try:
        # start from the interupt
        existing_comments = pd.read_csv(comments_csv)
        last_video_id = existing_comments['video_id'].iloc[-1]
        start_index = df[df['video_id'] == last_video_id].index[0] + 1
    except (FileNotFoundError, KeyError):
        pass

    # tqdm module
    for i in tqdm(range(start_index, len(df))):
        video_id = df.iloc[i]['video_id']
        comments = get_comments(video_id)
        if comments:
            save_to_csv(video_id, comments, comments_csv, replies_csv)

if __name__ == "__main__":
    main()