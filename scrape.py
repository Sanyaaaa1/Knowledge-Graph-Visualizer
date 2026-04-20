import json
import time
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
import re 

class KnowledgeGraphScraper:
    def __init__(self, seed_url, max_nodes=30, output_file="storing_project/megagraph1.json"):
        self.seed_url = seed_url
        self.max_nodes = max_nodes
        self.output_file = output_file
        self.domain = urlparse(seed_url).netloc
        
        self.url_to_id = {}
        self.id_counter = 1
        self.visited_urls = set()
        self.queue = [seed_url]
        
        self.scraped_nodes = [] 
        self.raw_edges = {}   
        
    def get_or_create_id(self, url):
        """Maps a URL to a short sequential ID without saving the URL itself."""
        if url not in self.url_to_id:
            node_id = f"N{self.id_counter}"
            self.url_to_id[url] = node_id
            self.id_counter += 1
        return self.url_to_id[url]

    def is_valid_article(self, url):
        """Strictly ensures link is a standard article and blocks edits/logins."""
        parsed = urlparse(url)
        if parsed.netloc != self.domain:
            return False
        
        path = parsed.path
        query = parsed.query.lower()
        
        if any(q in query for q in ['action=', 'veaction=', 'type=login']):
            return False
            
        if path.startswith('/w/'):
            return False

        forbidden_prefixes = [
            '/wiki/Portal:', 
            '/wiki/Special:', 
            '/wiki/Wikipedia:', 
            '/wiki/Help:', 
            '/wiki/Talk:',
            '/wiki/File:',
            '/wiki/Category:',
            '/wiki/Main_Page',
            '/wiki/List_of',  # IDK if this is necessary or even works, but it may help

        ]
        if any(path.startswith(prefix) for prefix in forbidden_prefixes):
            return False
        
        if re.match(r'/wiki/\d{4}', path):  # Exclude year-based pages like /wiki/1990 or /wiki/2001
            return False
        
        return True

    def run(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            while self.queue and len(self.scraped_nodes) < self.max_nodes:
                current_url = self.queue.pop(0)
                if current_url in self.visited_urls:
                    continue

                try:
                    page.goto(current_url, wait_until="domcontentloaded", timeout=10000)
                    self.visited_urls.add(current_url)
                    
                    title = page.locator('h1').first.inner_text().strip()
                    current_node_id = self.get_or_create_id(current_url)
                    
                    self.scraped_nodes.append({
                        "id": current_node_id,
                        "label": title
                    })
                    print(f"Scraped Node [{len(self.scraped_nodes)}/{self.max_nodes}]: {title} ({current_node_id})")

                    hrefs = page.eval_on_selector_all('a[href]', 'elements => elements.map(el => el.getAttribute("href"))')
                    
                    target_ids = set()
                    for href in hrefs:
                        full_url = urljoin(current_url, href).split('#')[0]
                        
                        if self.is_valid_article(full_url) and full_url != current_url:
                            target_id = self.get_or_create_id(full_url)
                            target_ids.add(target_id)
                            
                            if full_url not in self.visited_urls and full_url not in self.queue:
                                self.queue.append(full_url)
                    
                    self.raw_edges[current_node_id] = list(target_ids)

                    time.sleep(0.5) 

                except Exception as e:
                    print(f"Failed to scrape {current_url}: {e}")
                    continue

            browser.close()
            self.save_data()

    def save_data(self):
        """Cleans dangling connections and generates the required JSON format."""
        valid_node_ids = {node['id'] for node in self.scraped_nodes}
        
        edges_by_node = {}
        for source_id, connections in self.raw_edges.items():
            if source_id in valid_node_ids:
                edges_by_node[source_id] = [tid for tid in connections if tid in valid_node_ids]

        output = {
            "nodes": self.scraped_nodes,
            "edges_by_node": edges_by_node
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
            
        print(f"\nScraping complete! Saved to {self.output_file}")

if __name__ == "__main__":
    SEED = "https://en.wikipedia.org/wiki/The_Big_Bang_Theory" # Any Wikipedia article can be used as a seed
    
    scraper = KnowledgeGraphScraper(seed_url=SEED, max_nodes=100) # Adjust max_nodes as needed for the needed amount of connections
    scraper.run()