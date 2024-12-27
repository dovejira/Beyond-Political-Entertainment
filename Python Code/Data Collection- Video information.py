import csv
import time
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm

API_KEYS = []
current_key_index = 0

def get_youtube_service():
    global current_key_index
    return build('youtube', 'v3', developerKey=API_KEYS[current_key_index])

def switch_api_key():
    global current_key_index
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    print(f"Switching to API key {current_key_index + 1}")

def get_video_info(video_id):
    youtube = get_youtube_service()
    try:
        video_response = youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()

        if 'items' in video_response and video_response['items']:
            video = video_response['items'][0]
            snippet = video['snippet']
            statistics = video['statistics']

            return {
                'video_id': video_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'published_at': snippet['publishedAt'],
                'channel_id': snippet['channelId'],
                'view_count': statistics.get('viewCount', 'N/A'),
                'like_count': statistics.get('likeCount', 'N/A'),
                'comment_count': statistics.get('commentCount', 'N/A')
            }
    except HttpError as e:
        if e.resp.status in [403, 429]:
            print(f"Quota exceeded for API key {current_key_index + 1}. Switching to next key.")
            switch_api_key()
            return get_video_info(video_id)
        else:
            print(f"An error occurred: {e}")
            return None

def load_progress(output_file):
    processed_videos = set()
    if os.path.exists(output_file):
        with open(output_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                processed_videos.add(row['video_id'])
    return processed_videos

def main():
    input_file = 'input.csv'
    output_file = 'video.csv'

    processed_videos = load_progress(output_file)

    fieldnames = ['video_id', 'title', 'description', 'published_at', 'channel_id',
                  'view_count', 'like_count', 'comment_count']

    total_videos = sum(1 for row in csv.DictReader(open(input_file, 'r', newline='', encoding='utf-8')))

    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()

        with open(input_file, 'r', newline='', encoding='utf-8') as input_csvfile:
            reader = csv.DictReader(input_csvfile)
            for row in tqdm(reader, total=total_videos, desc="Processing videos"):
                video_id = row['video_id']
                if video_id not in processed_videos:
                    info = get_video_info(video_id)
                    if info:
                        writer.writerow(info)
                        csvfile.flush()
                        processed_videos.add(video_id)
                    else:
                        print(f"Failed to get info for video {video_id}. Skipping...")
                    time.sleep(0.1)  # 添加延迟以避免超过 API 配额限制

    print(f"Video information has been saved to {output_file}")

if __name__ == '__main__':
    main()