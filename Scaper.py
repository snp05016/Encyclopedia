from bs4 import BeautifulSoup
import requests

toi = requests.get('https://en.wikipedia.org/wiki/Shubman_Gill  ').text

soup = BeautifulSoup(toi, 'lxml')
container = soup.find('div',{'class':'mw-content-ltr mw-parser-output'})
para = container.find_all('p')[2].text
print(para)
