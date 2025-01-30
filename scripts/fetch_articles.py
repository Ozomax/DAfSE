import os
import requests
import feedparser
from bs4 import BeautifulSoup

# Blog weight mapping (higher value = higher priority)
BLOG_WEIGHTS = {
    "Meta Engineering": 10,
    "Google Research": 10,
    "Google Cloud": 10,
    "AWS Architecture": 8,
    "All Things Distributed": 8,
    "Netflix Tech": 10,
    "LinkedIn Engineering": 7,
    "Uber Engineering": 7,
    "Quora Engineering": 6,
    "Pinterest Engineering": 9,
    "Lyft Engineering": 7,
    "Twitter (X) Engineering": 7,
    "Dropbox Engineering": 6,
    "Spotify Engineering": 8,
    "GitHub Engineering": 9,
    "Instagram Engineering": 9,
    "Databricks Engineering": 7,
    "Canva Engineering": 9,
    "Etsy Engineering": 6,
    "Booking.com Tech": 6,
    "Expedia Tech": 6,
    "Airbnb Tech": 8,
    "Stripe Engineering": 8,
    "eBay Tech": 6,
    "Flickr Tech": 5,
    "HubSpot Engineering": 5,
    "Heroku Engineering": 9,
    "Discord Engineering": 8,
    "Zomato Tech": 10,
    "Hotstar Tech": 9,
    "Swiggy Tech": 10,
    "Shopify Engineering": 8,
    "Microsoft Tech Blogs": 7
}

# Blog URLs with RSS or manual scraping requirement
BLOGS = {
    "Meta Engineering": "https://engineering.fb.com/",
    "Google Research": "https://research.google/blog/",
    "Google Cloud": "https://cloud.google.com/blog/",
    "AWS Architecture": "https://aws.amazon.com/blogs/architecture/",
    "All Things Distributed": "https://www.allthingsdistributed.com/",
    "Netflix Tech": "https://netflixtechblog.com/",
    "LinkedIn Engineering": "https://www.linkedin.com/blog/engineering",
    "Uber Engineering": "https://www.uber.com/en-IN/blog/chandigarh/engineering/",
    "Quora Engineering": "https://quoraengineering.quora.com/",
    "Pinterest Engineering": "https://medium.com/pinterest-engineering",
    "Lyft Engineering": "https://eng.lyft.com/",
    "Twitter (X) Engineering": "https://blog.x.com/engineering/en_us",
    "Dropbox Engineering": "https://dropbox.tech/",
    "Spotify Engineering": "https://engineering.atspotify.com/",
    "GitHub Engineering": "https://github.blog/engineering/",
    "Instagram Engineering": "https://instagram-engineering.com/",
    "Databricks Engineering": "https://www.databricks.com/blog/category/engineering",
    "Canva Engineering": "https://www.canva.dev/blog/engineering/",
    "Etsy Engineering": "https://www.etsy.com/codeascraft",
    "Booking.com Tech": "https://blog.booking.com/",
    "Expedia Tech": "https://medium.com/expedia-group-tech",
    "Airbnb Tech": "https://medium.com/airbnb-engineering",
    "Stripe Engineering": "https://stripe.com/blog/engineering",
    "eBay Tech": "https://innovation.ebayinc.com/tech/",
    "Flickr Tech": "https://code.flickr.net/",
    "HubSpot Engineering": "https://product.hubspot.com/blog/topic/engineering",
    "Heroku Engineering": "https://blog.heroku.com/engineering",
    "Discord Engineering": "https://discord.com/blog",
    "Zomato Tech": "https://blog.zomato.com/category/technology",
    "Hotstar Tech": "https://blog.hotstar.com/",
    "Swiggy Tech": "https://bytes.swiggy.com/",
    "Shopify Engineering": "https://shopify.engineering/",
    "Microsoft Tech Blogs": "https://devblogs.microsoft.com/"
}

# Read previous history
history_file = "history.txt"
if os.path.exists(history_file):
    with open(history_file, "r") as f:
        history = set(f.read().splitlines())
else:
    history = set()

new_articles = []

# Function to fetch RSS feeds
def fetch_rss_articles(blog_name, url):
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:  # Limit to 3 latest articles per blog
            title = entry.title
            link = entry.link
            if link not in history:
                new_articles.append((blog_name, title, link, BLOG_WEIGHTS.get(blog_name, 5)))
                history.add(link)
    except Exception as e:
        print(f"Error fetching {blog_name}: {e}")

# Function to scrape articles if no RSS available
def scrape_articles(blog_name, url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        
        articles = soup.find_all("h2")[:3]  # Extract first 3 headlines
        for article in articles:
            link = article.find("a")["href"] if article.find("a") else None
            title = article.text.strip()
            if link and not link.startswith("http"):
                link = url + link  # Convert relative links to absolute
            if link and link not in history:
                new_articles.append((blog_name, title, link, BLOG_WEIGHTS.get(blog_name, 5)))
                history.add(link)
    except Exception as e:
        print(f"Error scraping {blog_name}: {e}")

# Process each blog
for blog, url in BLOGS.items():
    if url.endswith("rss") or "/feed" in url:
        fetch_rss_articles(blog, url)
    else:
        scrape_articles(blog, url)

# Sort articles by weight
new_articles.sort(key=lambda x: x[3], reverse=True)

# Update README
if new_articles:
    with open("README.md", "r") as f:
        readme = f.readlines()

    index = next((i for i, line in enumerate(readme) if "## Latest Articles" in line), len(readme))
    
    new_content = ["## Latest Articles\n"]
    for blog, title, link, weight in new_articles:
        new_content.append(f"- **{blog}** ({weight}): [{title}]({link})\n")

    readme = readme[:index+1] + new_content + readme[index+1:]

    with open("README.md", "w") as f:
        f.writelines(readme)

    with open(history_file, "w") as f:
        f.write("\n".join(history))
