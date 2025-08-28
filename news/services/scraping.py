from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse, parse_qs
import time
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from math import ceil
from datetime import datetime

from news.serializers import NewsSerializer





class NewsScraper:
    BASE_URL = "https://www.google.com/search"


    # Entidades para buscar en google

    USER_AGENTS = [
    # Windows - Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.117 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",

    # Windows - Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.91",

    # macOS - Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15",

    # macOS - Chrome
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.199 Safari/537.36",

    # Linux - Chrome
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.109 Safari/537.36",

    # Linux - Firefox
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",

    # Android - Chrome Mobile
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.80 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Mi 11 Lite) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Mobile Safari/537.36",

    # iPhone - Safari
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",

    # iPad - Safari
    "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    ]
  
    # Dominios para buscar
    financial_business_news_domains = [
        "economictimes.indiatimes.com",
        "business-standard.com"
    ]


    SELECTORS = {
        "title": "div.n0jPhd",
        "url": "a.WlydOe",
        "description": "div.GI74Re",
        "date": "div.rbYSKb",
        "source": "div.NUnG9d"
    }


    # Fominios, maximo de articulos a traer y maximo de intentos sin rechazar la peticion
    def __init__(self, financial_business_news_domains, max_articles: int = 50, max_retries: int = 3):
        """
        Initialize the scraper with configuration options.
        """
        self.article_per_pages = 100 # Articulos por pagina, osea por request
        self.max_pages = ceil(max_articles/self.article_per_pages) # maximo de paginas
        self.max_articles = max_articles
        self.max_retries = max_retries
        self.financial_business_news_domains = financial_business_news_domains
        self.proxies = [
            # {"http": "http://207.244.217.165:6712"}, # PRoxies para vitar ser ban
        ]
    

    def construct_url(
        self,
        query: str,
        start_date: datetime = None,
        end_date: datetime = None,
        page: int = 0,
        hl: str = "en",
        lr: str = "lang_en",
        num: int = None,
        sort_by_date: bool = False
    ) -> str:

        if num is None:
            num = self.article_per_pages

        if start_date is None:
            start_date = datetime.today() - timedelta(days=1)
        if end_date is None:
            end_date = datetime.today()  # Current date
            
        date_filter = (
            f"cdr:1,"
            f"cd_min:{start_date.strftime('%m/%d/%Y')},"
            f"cd_max:{end_date.strftime('%m/%d/%Y')}"
        )
        
        tbs_parts = [date_filter]
        
        if sort_by_date:
            tbs_parts.append("sbd:1")
            
        params = {
            "q": quote(query+" "+" OR ".join([f'site:{x}' for x in self.financial_business_news_domains])),
            "tbm": "nws", # Modo de busqueda news
            "tbs": ",".join(tbs_parts),
            "start": page * num,
            "hl": hl,
            "lr": lr,
            "num": str(num),
        }

        # Build URL
        return f"{self.BASE_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

    def get_random_delay(self) -> float:
        """Generate a longer random delay between requests to avoid detection."""
        return random.uniform(5, 15)
    
    def get_headers(self):
        """Return a random User-Agent."""
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
        }

    def is_captcha_page(self, html: str) -> bool:
        """Check if the response contains a CAPTCHA."""
        return "Our systems have detected unusual traffic" in html

    def parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """
        Convert relative date strings (e.g., '1 day ago', '2 weeks ago', '1 month ago')
        or absolute date strings ('24 Mar 2023', '2023-03-24') to YYYY-MM-DD format.
        """
        if not date_str:
            return None

        date_str = date_str.lower().strip()
        today = datetime.today()

        try:
            if "ago" in date_str:
                date_str = date_str.replace("ago", "").strip()

            if "hour" in date_str or "minute" in date_str or "second" in date_str:
                return today.strftime("%Y-%m-%d")
            
            if "day" in date_str:
                days = int(date_str.split()[0])
                return (today - timedelta(days=days)).strftime("%Y-%m-%d")

            if "week" in date_str:
                weeks = int(date_str.split()[0])
                return (today - timedelta(weeks=weeks)).strftime("%Y-%m-%d")

            if "month" in date_str:
                months = int(date_str.split()[0])
                return (today - relativedelta(months=months)).strftime("%Y-%m-%d")

            if "year" in date_str:
                years = int(date_str.split()[0])
                return (today - relativedelta(years=years)).strftime("%Y-%m-%d")

            try:
                return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                pass

            try:
                return datetime.strptime(date_str, "%d %b %Y").strftime("%Y-%m-%d")  # e.g., "24 Mar 2023"
            except ValueError:
                pass

            try:
                return datetime.strptime(date_str, "%d %B %Y").strftime("%Y-%m-%d")  # e.g., "24 March 2023"
            except ValueError:
                pass

        except Exception as e:
            print(f"Failed to parse date '{date_str}': {e}")

        return None


    def extract_articles(self, html: str) -> List[Dict[str, Optional[str]]]:
        """Extract article details from the HTML."""
        soup = BeautifulSoup(html, "html.parser")
        articles = []

        for container in soup.find_all("div", class_="SoaBEf"):
            article = {
                "title": self._safe_extract(container, self.SELECTORS["title"], "text"),
                "url": self._clean_url(self._safe_extract(container, self.SELECTORS["url"], "href")),
                "source": self._safe_extract(container, self.SELECTORS["source"], "text"),
                "date": self.parse_date(self._safe_extract(container, self.SELECTORS["date"], "text")),
                "description": self._safe_extract(container, self.SELECTORS["description"], "text"),
            }

            if article["url"]:
                articles.append(article)

        return articles

    def _clean_url(self, url: Optional[str]) -> Optional[str]:
        """Clean and extract the actual URL from Google's redirect links."""
        if url and url.startswith("/url?"):
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            return qs.get("q", [url])[0]
        return url

    def _safe_extract(self, parent, selector: str, attr: str) -> Optional[str]:
        """Safely extract text or attributes from an element."""
        try:
            element = parent.select_one(selector)
            if not element:
                return None
            if attr == "text":
                return element.get_text().strip()
            return element.get(attr, "")
        except Exception as e:
            print(f"Failed to extract {selector}: {e}")
            return None




    def scrape(self, query: str, start_date: datetime, end_date: datetime):
        """
        Scrape Google News articles based on the query and date range.
        """
        all_articles = []
        empty_page_count = 0

        for page in range(self.max_pages):
            if len(all_articles) >= self.max_articles:
                print(f"Reached article limit ({self.max_articles}). Stopping.")
                break

            time.sleep(random.uniform(3, 7))
            url = self.construct_url(query, start_date, end_date, page)

            retries = 0
            while retries < self.max_retries:
                try:
                    print(f"Fetching page {page + 1}: {url}")
                    response = requests.get(
                        url,
                        headers=self.get_headers(),
                        proxies=random.choice(self.proxies) if self.proxies else None,
                        timeout=30,
                    )
                    response.raise_for_status()

                    if self.is_captcha_page(response.text):
                        print("CAPTCHA detected. Stopping scraping.")
                        return all_articles

                    raw_articles = self.extract_articles(response.text)

                    if not raw_articles:
                        empty_page_count += 1
                        print(f"No articles found on page {page + 1}. Empty count: {empty_page_count}")
                        if empty_page_count >= 2:
                            print("No more articles found. Stopping.")
                            return all_articles
                    else:
                        empty_page_count = 0

                    for raw in raw_articles:

                        try:
                            article = NewsSerializer(
                                title=raw["title"],
                                url=raw["url"],
                                source= raw["source"],
                                date=raw["date"],
                                description=raw["description"],
                                category=query,
                                sentiment=None,
                                scraped_at=datetime.now()
                            )
                            all_articles.append(article.model_dump())  # JSON dict limpio
                        except Exception as e:
                            print(f"Error validating article: {e}")

                    print(f"Page {page + 1}: Added {len(raw_articles)} articles")
                    break

                except requests.exceptions.RequestException as e:
                    retries += 1
                    print(f"Request failed (attempt {retries}/{self.max_retries}): {e}")
                    if retries < self.max_retries:
                        time.sleep(2**retries)
                    else:
                        print("Max retries reached. Stopping.")
                        return all_articles

        return all_articles[:self.max_articles]
