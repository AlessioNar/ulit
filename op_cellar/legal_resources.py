from bs4 import BeautifulSoup
import json
import os
import re
import chardet

def extract_text(file, granularity='article'):
    """
    Extracts text from HTML files at different levels of granularity.

    Args:
    file (str): The path to the HTML file.
    granularity (str): The level of granularity to extract text at. Currently supports 'article'.

    Returns:
    dict: A dictionary with the extracted text, keyed by the ID of the HTML element.
    """
    with open(file, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    if granularity == 'article':
        articles = soup.find_all('div', class_='eli-subdivision', id=lambda x: x and x.startswith('art_'))

        article_text = {}
        for article in articles:
            text = article.get_text()
            text = text.encode('ascii', 'ignore').decode('ascii')
            text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
            text = text.strip()  # Remove leading and trailing whitespace
            article_text[article['id']] = text

        return article_text
    elif granularity == 'paragraph':
        enacting_terms = soup.find('div', class_='eli-subdivision', id='enc_1')
        
        paragraphs = soup.find_all('div', id=lambda x: x and len(x.split('.')) == 2 and len(x.split('.')[0]) == 3 and len(x.split('.')[1]) == 3)
        article_text = {}
        for article in paragraphs:
            text = article.get_text()
            text = text.encode('ascii', 'ignore').decode('ascii')
            text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
            text = text.strip()  # Remove leading and trailing whitespace
            article_text[article['id']] = text
        return article_text

    else:
        raise ValueError(f"Unsupported granularity: {granularity}")

# Main function
if __name__ == "__main__":
    # Example usage:
    file_path = './downloads/0/2fa0d32a-081c-11ef-a251-01aa75ed71a1.html'
    legal_resource = extract_text(file_path, granularity='article')

    # Convert the result to a JSON string
    json_string = json.dumps(legal_resource, indent=4)

    # Save the JSON string to a file
    with open('legal_resource.json', 'w') as f:
        f.write(json_string)