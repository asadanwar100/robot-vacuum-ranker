import praw
import json
from datetime import datetime
import re
import os
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class RedditVacuumScraper:
    def __init__(self, client_id, client_secret, user_agent):
        self.reddit = praw.Reddit(
            client_id = client_id,
            client_secret = client_secret,
            user_agent = user_agent
        )

    def scrape_vacuum_discussions(self,limit=100):
        #Scrape discussions from relevant subreddits

        subreddits = [
            'RobotVacuums',
            'homeautomation',
            'BuyItForLife',
            'Frugal'
        ]

        # Common robot vacuum brands/models to look for
        vacuum_keywords = [
            'roomba', 'roborock', 'shark', 'eufy', 'neato', 'bissell',
            'dreame','mova','narwal','yeedi','evovacs','lefant', 'xiaomi',
            'robot vacuum', 'robot mop', 'vacuum robot', 'mop combo'
        ]

        all_posts = []

        for sub_name in subreddits:
            print(f"Scraping subreddit {sub_name}")
            try:
                subreddit = self.reddit.subreddit(sub_name)

                #Get hot posts
                for post in subreddit.hot(limit = limit//len(subreddits)):
                    if self._is_vacuum_related(post.title.lower(), vacuum_keywords):
                        post_data = self._extract_post_data(post)
                        all_posts.append(post_data)

                #Get top posts from last month
                for post in subreddit.top(time_filter='month',limit=limit//len(subreddits)):
                    if self._is_vacuum_related(post.title.lower(), vacuum_keywords):
                        post_data = self._extract_post_data(post)
                        all_posts.append(post_data)

            except Exception as e:
                print(f"Error scraping subreddit r/{sub_name}: {e}")
                continue

        #Remove duplicates
        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            if post['id'] not in seen_ids:
                seen_ids.add(post['id'])
                unique_posts.append(post)

        return unique_posts

    def _is_vacuum_related(self, text, keywords):
        return any(keyword in text for keyword in keywords)

    def _extract_post_data(self, post):
        #Get top comments
        post.comments.replace_more(limit=5) #Expand comments threads
        top_comments = []

        for comment in post.comments[:10]: #Top 10 comments
            if len(comment.body)>20: #Skip short comments
                top_comments.append({
                    'body': comment.body,
                    'score': comment.score,
                    'created': datetime.fromtimestamp(comment.created_utc).isoformat()
                })
        return {
            'id': post.id,
            'title': post.title,
            'selftext': post.selftext,
            'score': post.score,
            'upvote_ratio': post.upvote_ratio,
            'num_comments': post.num_comments,
            'created': datetime.fromtimestamp(post.created_utc).isoformat(),
            'url': post.url,
            'subreddit': str(post.subreddit),
            'author': str(post.author) if post.author else '[deleted]',
            'flair': post.link_flair_text,
            'comments': top_comments
        }
    
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    def analyze_brand_sentiment(self, posts, brands):
        analyzer = SentimentIntensityAnalyzer()

        brand_mentions = {brand: 0 for brand in brands}
        brand_sentiment = {brand: {'positive': 0, 'negative': 0, 'neutral': 0} for brand in brands}
        
        for post in posts:
            text = (post['title'] + ' ' + post['selftext']).lower()
            
            # Add comments to text
            for comment in post['comments']:
                text += ' ' + comment['body'].lower()
            
            # Split into sentences
            sentences = text.replace('!', '.').replace('?', '.').split('.')
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 10:
                    continue
                    
                for brand in brands:
                    if brand.lower() in sentence:
                        brand_mentions[brand] += 1
                        
                        # Analyze sentiment of this sentence
                        scores = analyzer.polarity_scores(sentence)
                        
                        if scores['compound'] >= 0.05:
                            brand_sentiment[brand]['positive'] += 1
                        elif scores['compound'] <= -0.05:
                            brand_sentiment[brand]['negative'] += 1
                        else:
                            brand_sentiment[brand]['neutral'] += 1
        
        return {
            'brand_mentions': brand_mentions,
            'brand_sentiment': brand_sentiment
        }
        
    

    def save_data(self, posts, filename='vacuum_discussions.json'):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(posts)} posts to {filename}")

def main():

    load_dotenv()  # Load environment variables from .env file

    CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    USER_AGENT = os.getenv('REDDIT_USER_AGENT')

    if not CLIENT_ID or not CLIENT_SECRET:
        print("Missing Reddit API credentials!")
        print("Create a .env file with:")
        print("REDDIT_CLIENT_ID=your_client_id")
        print("REDDIT_CLIENT_SECRET=your_client_secret")
        return
    
    brands = {
            'roomba':0, 'roborock':0, 'shark':0, 'eufy':0, 'neato':0, 'bissell':0,
            'dreame':0,'mova':0,'narwal':0,'yeedi':0,'evovacs':0,'lefant':0, 'xiaomi':0,
        }


    scraper = RedditVacuumScraper(CLIENT_ID, CLIENT_SECRET, USER_AGENT)

    print("Starting Reddit Vacuum discussion scraper")

    posts = scraper.scrape_vacuum_discussions(limit=200)
    print(f"Found {len(posts)} vacuum-related posts")

    # Analyze the data
    analysis = scraper.analyze_brand_sentiment(posts, brands)

    print("\n Most mentioned brands:")
    sorted_brands = sorted(analysis['brand_mentions'].items(), key=lambda x: x[1], reverse=True)
    for brand, count in sorted_brands[:5]:
        if count > 0:
            sentiment = analysis['brand_sentiment'][brand]
            total_sentiment = sum(sentiment.values())
            pos_ratio = sentiment['positive'] / max(total_sentiment, 1) * 100
            print(f"  {brand.capitalize()}: {count} mentions ({pos_ratio:.1f}% positive)")
    # Save the data
    scraper.save_data(posts)
    
    print("\n✅ Scraping complete! Check vacuum_discussions.json for full data")


if __name__ == "__main__":
    main()