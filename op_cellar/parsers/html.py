from .parser import Parser
import re
from bs4 import BeautifulSoup

class HTMLParser(Parser):
    def parse(self, file, granularity='article'):
        """
        Parses the HTML content of a file at a specified level of granularity.

        Args:
        file (str): Path to the HTML file.
        granularity (str): The level of granularity for extraction, such as 'article' or 'paragraph'.

        Returns:
        dict: Extracted text organized by HTML element IDs.
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
                text = re.sub(r'\s+', ' ', text).strip()
                article_text[article['id']] = text
            return article_text
        
        elif granularity == 'paragraph':
            enacting_terms = soup.find('div', class_='eli-subdivision', id='enc_1')
            if not enacting_terms:
                raise ValueError("No enacting terms found with ID 'enc_1'.")

            paragraphs = enacting_terms.find_all(
                'div',
                id=lambda x: x and len(x.split('.')) == 2 and len(x.split('.')[0]) == 3 and len(x.split('.')[1]) == 3
            )

            paragraph_text = {}
            for paragraph in paragraphs:
                text = paragraph.get_text()
                text = text.encode('ascii', 'ignore').decode('ascii')
                text = re.sub(r'\s+', ' ', text).strip()
                paragraph_text[paragraph['id']] = text
            
            # Handle paragraphs in nested lists or other sub-divisions
            for article in soup.find_all('div', class_='eli-subdivision', id=lambda x: x and x.startswith('art_')):
                lists = article.find_all(['ul', 'ol'])
                for list_item in lists:
                    list_paragraphs = list_item.find_all('div', id=True)
                    for para in list_paragraphs:
                        text = para.get_text()
                        text = text.encode('ascii', 'ignore').decode('ascii')
                        text = re.sub(r'\s+', ' ', text).strip()
                        paragraph_text[para['id']] = text

            return paragraph_text

        else:
            raise ValueError(f"Unsupported granularity: {granularity}")
