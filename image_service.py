"""
Image fetching service with support for Unsplash and keyword-based fallbacks
"""

import os
import requests
import logging
from pathlib import Path
from urllib.parse import quote

logger = logging.getLogger(__name__)

class ImageService:
    """Fetch relevant images from various sources"""
    
    def __init__(self, unsplash_key=None, pexels_key=None, pixabay_key=None):
        """Initialize with optional API keys"""
        self.unsplash_key = unsplash_key
        self.pexels_key = pexels_key
        self.pixabay_key = pixabay_key
        self.cache_dir = Path("temp_images")
        self.cache_dir.mkdir(exist_ok=True)
        self.unsplash_disabled_until = 0
        self.pollinations_disabled_until = 0
        self.loremflickr_disabled_until = 0
        self.picsum_disabled_until = 0
        self.wikimedia_disabled_until = 0
        self.pexels_disabled_until = 0
        self.pixabay_disabled_until = 0
        self.placeholder_dir = Path("assets/placeholders")
        self.placeholder_dir.mkdir(parents=True, exist_ok=True)
    
    def _is_disabled(self, provider):
        """Check if a provider is currently in a cooldown period"""
        import time
        disabled_until = getattr(self, f"{provider}_disabled_until", 0)
        return time.time() < disabled_until

    def _disable_provider(self, provider, duration=300):
        """Disable a provider for a certain duration (default 5 minutes)"""
        import time
        setattr(self, f"{provider}_disabled_until", time.time() + duration)
        logger.warning(f"Provider {provider} disabled for {duration}s due to errors.")
    def fetch_image(self, query, width=1200, height=800):
        """
        Fetch an image based on search query
        Fetch an image based on search query
        Returns: Dictionary with 'path', 'credit', 'download_url' or None
        """
        if not query:
            return None
        
        # Clean the query
        query = query.strip()
        if not query:
            return None
        
        # 1. Try Unsplash (Primary)
        if self.unsplash_key and not self._is_disabled('unsplash'):
            result = self._fetch_from_unsplash(query, width, height)
            if result: return result
        
        # 2. Try Pexels (if key provided)
        if self.pexels_key and not self._is_disabled('pexels'):
            result = self._fetch_from_pexels(query, width, height)
            if result: return result

        # 3. Try Pixabay (if key provided)
        if self.pixabay_key and not self._is_disabled('pixabay'):
            result = self._fetch_from_pixabay(query, width, height)
            if result: return result

        # 4. Try Wikimedia Commons (Reliable, high-quality, free)
        if not self._is_disabled('wikimedia'):
            result = self._fetch_from_wikimedia(query, width, height)
            if result: return result
        
        # 5. Try Pollinations.ai (AI-generated)
        if not self._is_disabled('pollinations'):
            result = self._fetch_from_pollinations(query, width, height)
            if result: return result
        
        # 7. Try Unsplash Source (No API key, highly reliable)
        result = self._fetch_from_unsplash_source(query, width, height)
        if result: return result

        # 8. Try Local Placeholders (Guaranteed to work offline)
        result = self._fetch_from_local_placeholders()
        if result: return result

        # 9. Fallback: LoremFlickr
        if not self._is_disabled('loremflickr'):
            result = self._fetch_from_loremflickr(query, width, height)
            if result: return result
                
        # 10. Ultimate Fallback: Picsum
        return self._fetch_from_picsum(width, height)
    
    def _fetch_from_unsplash(self, query, width, height):
        """Fetch from Unsplash API"""
        try:
            url = "https://api.unsplash.com/search/photos"
            params = {
                'query': query,
                'per_page': 1,
                'orientation': 'landscape'
            }
            headers = {
                'Authorization': f'Client-ID {self.unsplash_key}'
            }
            
            # Short timeout for API calls
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 403:
                logger.warning("Unsplash API limit reached or invalid key. Disabling.")
                self._disable_provider('unsplash', duration=3600) # Disable for 1 hour
                return None
            
            if response.status_code >= 500:
                self._disable_provider('unsplash', duration=300)
                return None

            
            data = response.json()
            if data.get('results') and len(data['results']) > 0:
                img_data = data['results'][0]
                image_url = img_data['urls']['regular']
                filepath = self._download_image(image_url, query)
                
                if filepath:
                    user = img_data['user']
                    return {
                        'path': filepath,
                        'credit': {
                            'text': f"Photo by {user['name']} on Unsplash",
                            'link': f"{user['links']['html']}?utm_source=TelegramPresentationBot&utm_medium=referral",
                            'app_link': "https://unsplash.com/?utm_source=TelegramPresentationBot&utm_medium=referral"
                        },
                        'download_url': img_data['links']['download_location']
                    }
                
        except Exception as e:
            logger.warning(f"Unsplash error: {e}")
            self._disable_provider('unsplash', duration=300)
        
        return None

    def _fetch_from_pollinations(self, query, width, height):
        """Fetch AI-generated image from Pollinations.ai"""
        try:
            enhanced_query = f"professional presentation photo of {query}, high quality, clean composition"
            encoded_query = quote(enhanced_query)
            import random
            seed = random.randint(0, 10000)
            url = f"https://image.pollinations.ai/prompt/{encoded_query}?width={width}&height={height}&nologo=true&seed={seed}"
            
            # Pollinations can be slow, use longer timeout but don't hang forever
            filepath = self._download_image(url, query, timeout=30)
            if filepath:
                return {
                    'path': filepath,
                    'credit': {'text': "Generated by AI", 'link': "https://pollinations.ai"},
                    'download_url': None
                }
            return None
        except Exception as e:
            logger.error(f"Pollinations error: {e}")
            self._disable_provider('pollinations', duration=300)
            return None

    def _fetch_from_wikimedia(self, query, width, height):
        """Fetch image from Wikimedia Commons API"""
        try:
            # Wikimedia REQUIRES a specific User-Agent
            headers = {
                'User-Agent': 'TelegramPPTBot/1.0 (https://t.me/your_bot_link; contact@example.com) Requests'
            }
            search_url = "https://commons.wikimedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": f"filetype:bitmap {query}",
                "srnamespace": 6,
                "srlimit": 1
            }
            resp = requests.get(search_url, params=params, headers=headers, timeout=10)
            if resp.status_code != 200:
                logger.warning(f"Wikimedia API returned status {resp.status_code}")
                return None
            
            try:
                data = resp.json()
            except Exception as json_err:
                logger.error(f"Wikimedia JSON parse error: {json_err} - URL: {resp.url}")
                # Log a snippet of the response to see what we got
                logger.debug(f"Wikimedia response content: {resp.text[:500]}")
                return None
            
            if data.get('query', {}).get('search'):
                title = data['query']['search'][0]['title']
                # Get direct URL
                info_params = {
                    "action": "query",
                    "format": "json",
                    "prop": "imageinfo",
                    "titles": title,
                    "iiprop": "url|user|extmetadata",
                    "iiurlwidth": width
                }
                info_resp = requests.get(search_url, params=info_params, timeout=10)
                info_data = info_resp.json()
                
                pages = info_data.get('query', {}).get('pages', {})
                for page_id in pages:
                    info = pages[page_id].get('imageinfo', [None])[0]
                    if info and info.get('thumburl'):
                        image_url = info['thumburl']
                        filepath = self._download_image(image_url, query)
                        if filepath:
                            user = info.get('user', 'Wikimedia Contributor')
                            return {
                                'path': filepath,
                                'credit': {
                                    'text': f"Photo by {user} (Wikimedia Commons)",
                                    'link': info.get('descriptionurl', "https://commons.wikimedia.org")
                                },
                                'download_url': None
                            }
            return None
        except Exception as e:
            logger.error(f"Wikimedia error: {e}")
            self._disable_provider('wikimedia', duration=300)
            return None

    def _fetch_from_pexels(self, query, width, height):
        """Fetch from Pexels API"""
        try:
            url = f"https://api.pexels.com/v1/search?query={quote(query)}&per_page=1&orientation=landscape"
            headers = {"Authorization": self.pexels_key}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('photos'):
                    photo = data['photos'][0]
                    filepath = self._download_image(photo['src']['large'], query)
                    if filepath:
                        return {
                            'path': filepath,
                            'credit': {
                                'text': f"Photo by {photo['photographer']} on Pexels",
                                'link': photo['url']
                            },
                            'download_url': None
                        }
            elif resp.status_code == 403:
                self._disable_provider('pexels', duration=3600)
            return None
        except Exception as e:
            logger.error(f"Pexels error: {e}")
            return None

    def _fetch_from_pixabay(self, query, width, height):
        """Fetch from Pixabay API"""
        try:
            url = f"https://pixabay.com/api/?key={self.pixabay_key}&q={quote(query)}&image_type=photo&orientation=horizontal&per_page=3"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('hits'):
                    photo = data['hits'][0]
                    filepath = self._download_image(photo['largeImageURL'], query)
                    if filepath:
                        return {
                            'path': filepath,
                            'credit': {
                                'text': f"Photo by {photo['user']} on Pixabay",
                                'link': photo['pageURL']
                            },
                            'download_url': None
                        }
            return None
        except Exception as e:
            logger.error(f"Pixabay error: {e}")
            return None
            
    def _fetch_from_picsum(self, width, height):
        """Ultimate fallback image from Picsum"""
        try:
            url = f"https://picsum.photos/{width}/{height}"
            filepath = self._download_image(url, "picsum_fallback", provider='picsum')
            if filepath:
                return {
                    'path': filepath,
                    'credit': { 'text': "Photo from Picsum", 'link': "https://picsum.photos" },
                    'download_url': None
                }
        except Exception as e:
            logger.error(f"Picsum error: {e}")
        return None
    
    def _fetch_from_loremflickr(self, query, width, height):
        """Fetch a relevant image from LoremFlickr using keywords"""
        try:
            # Format keywords: comma-separated, no spaces
            # Extract main keywords (first 2-3 words) to improve relevance
            keywords = ",".join(query.split()[:3])
            
            # Add a random 'lock' parameter to ensure different images for same keywords
            import random
            random_lock = random.randint(1, 10000)
            url = f"https://loremflickr.com/{width}/{height}/{quote(keywords)}?lock={random_lock}"
            
            # Since LoremFlickr redirects to the actual image, we follow redirects
            filepath = self._download_image(url, query)
            if filepath:
                return {
                    'path': filepath,
                    'credit': None, # LoremFlickr doesn't provide easy attribution
                    'download_url': None
                }
            return None
            
        except Exception as e:
            logger.error(f"LoremFlickr error: {e}")
            self._disable_provider('loremflickr', duration=300)
        
        return None
    
    def _fetch_from_unsplash_source(self, query, width, height):
        """Fetch from Unsplash Source (no key required for basic redirects)"""
        try:
            # Using the featured endpoint which is still quite reliable
            url = f"https://source.unsplash.com/featured/{width}x{height}/?{quote(query)}"
            filepath = self._download_image(url, query)
            if filepath:
                return {
                    'path': filepath,
                    'credit': {'text': "Photo from Unsplash (Source)", 'link': "https://unsplash.com"},
                    'download_url': None
                }
            return None
        except Exception as e:
            logger.warning(f"Unsplash Source error: {e}")
            return None

    def _fetch_from_local_placeholders(self):
        """Pick a random high-quality local placeholder"""
        try:
            placeholders = list(self.placeholder_dir.glob("*.jpg")) + list(self.placeholder_dir.glob("*.png"))
            if not placeholders:
                return None
            
            import random
            choice = random.choice(placeholders)
            return {
                'path': str(choice.absolute()),
                'credit': {'text': "Local Placeholder", 'link': None},
                'download_url': None
            }
        except Exception as e:
            logger.error(f"Local placeholder error: {e}")
            return None

    def _download_image(self, url, query, provider=None, timeout=60):
        """Download image from URL and save locally"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            # Follow redirects
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            
            # Handle rate limits (429) with a simple retry
            if response.status_code == 429:
                logger.warning(f"Rate limited (429) for {url}. Waiting 5s and retrying...")
                import time
                time.sleep(5)
                # Retry with same timeout
                response = requests.get(url, headers=headers, timeout=60, allow_redirects=True)
            
            if response.status_code >= 500:
                logger.warning(f"Server error {response.status_code} for {url}")
                if provider:
                    self._disable_provider(provider)
                return None
                
            if response.status_code != 200:
                logger.warning(f"Download failed for {url}: Status {response.status_code}")
                return None
                
            # Create filename from query
            safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_query = safe_query.replace(' ', '_')[:50]
            # Add random hash to avoid overwriting diff images for same query
            import time
            filename = f"{safe_query}_{int(time.time()*1000) % 10000}.jpg"
            filepath = self.cache_dir / filename
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return str(filepath)
        except Exception as e:
            logger.warning(f"Download error: {e}")
            return None
    
    def cleanup(self):
        """Remove all cached images"""
        try:
            import shutil
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(exist_ok=True)
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def trigger_download(self, download_url):
        """Trigger Unsplash download endpoint for API compliance"""
        if not download_url or not self.unsplash_key:
            return
            
        try:
            headers = {
                'Authorization': f'Client-ID {self.unsplash_key}'
            }
            # Unsplash requires hitting the download_location
            requests.get(download_url, headers=headers, timeout=5)
            logger.info(f"Triggered Unsplash download: {download_url}")
        except Exception as e:
            logger.warning(f"Failed to trigger download: {e}")
