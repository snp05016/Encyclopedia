from bs4 import BeautifulSoup
import requests

toi = requests.get('https://en.wikipedia.org/wiki/Shikhar_Dhawan').text
soup = BeautifulSoup(toi, 'lxml')
container = soup.find('div',{'class':'mw-content-ltr mw-parser-output'})
para = container.find_all('p')

plist = []

for p in range(0,len(para)-1):
    plist.append(p) if 'Shikhar Dhawan' in para[p].text else None

# Print the first paragraph with 'dog' in it
requiredtext = para[plist[0]].text
print(requiredtext)

