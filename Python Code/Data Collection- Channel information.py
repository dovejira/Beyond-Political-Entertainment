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

def get_channel_info(channel_id):
    youtube = get_youtube_service()
    try:
        channel_response = youtube.channels().list(
            part='snippet,statistics,brandingSettings',
            id=channel_id
        ).execute()

        if 'items' in channel_response and channel_response['items']:
            channel = channel_response['items'][0]
            snippet = channel['snippet']
            statistics = channel['statistics']
            branding = channel.get('brandingSettings', {}).get('channel', {})

            return {
                'channel_id': channel_id,
                'channel_name': snippet['title'],
                'description': snippet['description'],
                'subscriber_count': statistics.get('subscriberCount', 'N/A'),
                'video_count': statistics.get('videoCount', 'N/A'),
                'view_count': statistics.get('viewCount', 'N/A'),
                'country': snippet.get('country', 'N/A'),
                'custom_url': snippet.get('customUrl', 'N/A'),
                'published_at': snippet['publishedAt'],
            }
    except HttpError as e:
        if e.resp.status in [403, 429]:
            print(f"Quota exceeded for API key {current_key_index + 1}. Switching to next key.")
            switch_api_key()
            return get_channel_info(channel_id)
        else:
            print(f"An error occurred: {e}")
            return None

def load_progress(output_file):
    processed_channels = set()
    if os.path.exists(output_file):
        with open(output_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                processed_channels.add(row['channel_id'])
    return processed_channels

def main():
    input_file = 'output_1.csv'
    output_file = 'channel_info1.csv'

    processed_channels = load_progress(output_file)

    fieldnames = ['channel_id', 'channel_name', 'description', 'subscriber_count',
                  'video_count', 'view_count', 'country', 'is_verified', 'custom_url', 'published_at']

    total_channels = sum(1 for row in csv.DictReader(open(input_file, 'r', newline='', encoding='utf-8')))

    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()

        with open(input_file, 'r', newline='', encoding='utf-8') as input_csvfile:
            reader = csv.DictReader(input_csvfile)
            for row in tqdm(reader, total=total_channels, desc="Processing channels"):
                channel_id = row['channel_id']
                if channel_id not in processed_channels:
                    info = get_channel_info(channel_id)
                    if info:
                        writer.writerow(info)
                        csvfile.flush()
                        processed_channels.add(channel_id)
                    else:
                        print(f"Failed to get info for channel {channel_id}. Skipping...")
                    time.sleep(1)

    print(f"Channel information has been saved to {output_file}")

if __name__ == '__main__':
    main()
