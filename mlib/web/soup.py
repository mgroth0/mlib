from bs4 import BeautifulSoup
def soup(html):
    return BeautifulSoup(html, 'html.parser')
