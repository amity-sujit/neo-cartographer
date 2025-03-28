import requests
from bs4 import BeautifulSoup
import json
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

def extract_details_from_div(html_content):
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Dictionary to store the extracted details
    details = {}
    
    # Mapping of field names as they appear in the HTML to the desired JSON keys
    field_mapping = {
        "Author:": "author_name",
        "Date:": "date_of_creation",
        "Short Title:": "short_title",
        "Publisher:": "publisher",
        "Publisher Location:": "publisher_location",
        "Type:": "type_of_image",
        "Obj Height cm:": "object_height_cm",
        "Obj Width cm:": "object_width_cm",
        "Note:": "note",
        "Reference:": "references",
        "City:": "city",
        "Full Title:": "full_title",
        "List No:": "list_number",
        "Page No:": "page_number",
        "Series No:": "series_no",
        "Engraver or Printer:": "engraver_or_printer",
        "Publication Author:": "publication_author",
        "Pub Date:": "pub_date",
        "Pub Title:": "pub_title",
        "Pub Note:": "pub_note",
        "Pub Type:": "pub_type",
        "Pub Maps:": "pub_maps",
        "Pub Height cm:": "pub_height_cm",
        "Pub Width cm:": "pub_width_cm",
        "Image No:": "image_number",
        "Authors:": "authors"
    }
    
    # Find all divs with class 'valueFieldDisplayNameTD'
    field_divs = soup.find_all('div', class_='valueFieldDisplayNameTD')
    
    for field_div in field_divs:
        # Get the field name (text content of the div, stripped of extra whitespace)
        field_name = field_div.get_text(strip=True)
        
        # Check if this field is one we want to extract
        if field_name in field_mapping:
            # Find the sibling div with class 'valueValueTD' that contains the value
            value_div = field_div.find_next_sibling('div', class_='valueValueTD')
            if value_div:
                # Extract the value from the 'singleValueValue' div
                value = value_div.find('div', class_='singleValueValue')
                if value:
                    # Get the raw HTML content of the value (to preserve links if present)
                    details[field_mapping[field_name]] = str(value.decode_contents()).strip()
    
    return details



def fetch_download_filename(html_content, search_string,out_filename):
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
                filename = href.split('/')[-1]
                filename = filename.split('.')[0]
                filename = out_filename+filename + '.json'
                return filename
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
                fileoutDir = f"data/"
                filename=fetch_download_filename(cleaned_text, search_string,fileoutDir)
                print(filename)
                if filename:
                    # Extract details
                    extracted_details = extract_details_from_div(cleaned_text)

                    # Convert to JSON
                    json_output = json.dumps(extracted_details, indent=2, ensure_ascii=False)                
    
                    # Optionally, save to a file
                    with open(filename, 'w', encoding='utf-8') as jsonf:
                        jsonf.write(json_output)
               
        except requests.RequestException as e:
            log_file.write(f"Requested: {title}, URL: {url}, Status: Error - {str(e)}\n")