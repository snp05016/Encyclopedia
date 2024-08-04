from bs4 import BeautifulSoup
import requests
import re

# Function to remove all numbers enclosed in square brackets
def remove_enclosed_numbers(text):
    """Remove all numbers enclosed in square brackets."""
    return re.sub(r'\[\d+\]', '', text)

# Fetch and parse the Wikipedia page
toi = requests.get('https://en.wikipedia.org/wiki/Shikhar_Dhawan').text
soup = BeautifulSoup(toi, 'lxml')
container = soup.find('div', {'class': 'mw-content-ltr mw-parser-output'})
para = container.find_all('p')

plist = []


# Identify paragraphs containing the keyword
for p in range(len(para)):
    if 'shikhar dhawan' in para[p].text.lower():
        plist.append(p)
'''gets basic information about the wiki page.'''
# Extract and clean the required text
if plist:
    requiredtext = remove_enclosed_numbers(para[plist[0]].text)
    print(requiredtext)
else:
    print("No relevant paragraphs found.")
'''gets the table of content for the wiki page'''
contents = container.find_all('div', {'class': "mw-heading mw-heading2"})
for line in contents:
    p = line.text.split('[')
    print(p[0])