import tweepy
import json
import csv
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import re

# Twitter API credentials
consumer_key = 'your_consumer_key'
consumer_secret = 'your_consumer_secret'
access_token = 'your_access_token'
access_token_secret = 'your_access_token_secret'

# Authenticate with Twitter API
auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
api = tweepy.API(auth)

# Set up logging
logging.basicConfig(filename='twitter_scraper.log', level=logging.INFO)

def scrape_tweets(search_query, since_date, until_date, max_tweets):
    """
    Scrape tweets based on search query, start date, end date, and maximum number of tweets to retrieve.
    """
    try:
        # Scrape tweets based on search query and time frame
        tweets = tweepy.Cursor(api.search, q=search_query, since=since_date, until=until_date, tweet_mode='extended').items(max_tweets)
        return list(tweets)
    except tweepy.TweepError as e:
        logging.error(f"Error occurred while scraping tweets: {e}")
        print("An error occurred while scraping tweets. Please try again later.")
        return []

def clean_text(text, auto_clean=False, custom_characters=None):
    """
    Clean text by removing special characters, URLs, non-ASCII characters, and extra whitespaces.
    """
    if auto_clean:
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        # Remove non-ASCII characters
        text = text.encode("ascii", "ignore").decode()
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text)
    # Custom cleaning
    if custom_characters:
        for char in custom_characters:
            text = text.replace(char, '')
    # Replace newline characters with spaces
    text = text.replace('\n', ' ')
    # Remove carriage return characters
    text = text.replace('\r', '')
    return text.strip()

def validate_date(date_str):
    """
    Validate date format (YYYY-MM-DD).
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def main():
    print("Welcome to Twitter Scraper!")
    print("=================================")
    # Input parameters
    search_query = input("Enter search query (e.g., company, product, person, or topic): ").strip()
    since_date = input("Enter start date (YYYY-MM-DD): ").strip()
    until_date = input("Enter end date (YYYY-MM-DD): ").strip()
    max_tweets = input("Enter the number of tweets to scrape: ").strip()

    # Validate date inputs
    if not (validate_date(since_date) and validate_date(until_date)):
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    # Validate date range
    if since_date >= until_date:
        print("Start date must be earlier than end date.")
        return

    # Validate max_tweets
    try:
        max_tweets = int(max_tweets)
        if max_tweets <= 0:
            print("Number of tweets must be a positive integer.")
            return
    except ValueError:
        print("Invalid input for the number of tweets.")
        return

    # Ask user for text cleaning options
    auto_clean = input("Do you want to perform automatic text cleaning? (yes/no): ").strip().lower() == 'yes'
    custom_characters = input("Enter any custom characters you want to remove (leave blank for none): ").strip()

    try:
        # Scrape tweets with parallel processing
        with ThreadPoolExecutor() as executor:
            future = executor.submit(scrape_tweets, search_query, since_date, until_date, max_tweets)
            tweets = future.result()

        if tweets:
            print(f"\nScraped {len(tweets)} tweets:")
            for tweet in tweets:
                cleaned_text = clean_text(tweet.full_text, auto_clean, custom_characters)
                print(f"\n- Author: {tweet.user.screen_name}")
                print(f"  Text: {cleaned_text}")
                print(f"  Timestamp: {tweet.created_at}")
                print(f"  Likes: {tweet.favorite_count}")
                print(f"  Retweets: {tweet.retweet_count}")
                print()

            # Save data to files
            save_option = input("Do you want to save the data to files? (yes/no): ").strip().lower()
            if save_option == 'yes':
                save_format = input("Enter the format to save data (json/csv): ").strip().lower()
                if save_format == 'json':
                    save_to_json([tweet._json for tweet in tweets], 'tweets.json')
                    print("Data saved to tweets.json")
                elif save_format == 'csv':
                    save_to_csv(tweets, 'tweets.csv')
                    print("Data saved to tweets.csv")
                else:
                    print("Invalid format. Data not saved.")
        else:
            print("No tweets found matching the search criteria.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

def save_to_json(data, filename):
    """
    Save data to JSON file.
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def save_to_csv(data, filename):
    """
    Save data to CSV file.
    """
    keys = ['tweet_id', 'author', 'timestamp', 'likes', 'retweets', 'text']
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for tweet in data:
            writer.writerow({
                'tweet_id': tweet.id_str,
                'author': tweet.user.screen_name,
                'timestamp': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'likes': tweet.favorite_count,
                'retweets': tweet.retweet_count,
                'text': clean_text(tweet.full_text)
            })

if __name__ == "__main__":
    main()
