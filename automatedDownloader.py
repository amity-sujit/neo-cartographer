import requests
from bs4 import BeautifulSoup

def search_anchor_href(html_content, search_string):
    try:
        # Parse HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find anchor tags where href contains the search string
        matching_tags = soup.find_all('a', href=lambda href: href and search_string in href)
        
        # Process results
        results = []
        for tag in matching_tags:
            href = tag['href']
            try:
                # Make GET request to the URL
                print(f"Found: {tag}, URL: {href}")
                with requests.get(href, stream=True, timeout=1800) as response:
                    response.raise_for_status()
                    filename = href.split('/')[-1]
                    # Set chunk size to 1MB
                    chunk_size = 1024 * 1024
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                return
            except requests.RequestException as e:
                results.append({
                    'tag': str(tag),
                    'href': href,
                    'response_content': f'Failed to fetch: {str(e)}',
                    'status_code': None
                })
        
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Read HTML from a file
with open('input.html', 'r', encoding='utf-8') as file:
    html_input = file.read()

soup = BeautifulSoup(html_input, 'html.parser')
thumbnail_items = soup.select('div.thumbnailItem div.imgContainer a[href^="https"]')
titles_urls = {}
for item in thumbnail_items:
    title = item.get('title')
    url = item.get('href')
    if title and url:
        titles_urls[title] = url

# Open log file in write mode
with open('output.log', 'w', encoding='utf-8') as log_file:
    for idx, (title, url) in enumerate(titles_urls.items()):
        try:
            search_string = "download.pl?image="
            response = requests.get(url)
            log_file.write(f"Requested: {title}, URL: {url}, Status: {response.status_code}\n")
            if response.status_code == 200:
                # Remove blank lines from response text
                cleaned_text = "\n".join(line for line in response.text.splitlines() if line.strip())
                filename = f"{title.replace('/', '_').replace(':', '_')}_{idx}.tag"
                filename_full = f"{title.replace('/', '_').replace(':', '_')}_{idx}.html"
                search_anchor_href(cleaned_text, search_string)
               
        except requests.RequestException as e:
            log_file.write(f"Requested: {title}, URL: {url}, Status: Error - {str(e)}\n")