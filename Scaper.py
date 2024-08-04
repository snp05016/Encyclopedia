from bs4 import BeautifulSoup
import requests
import re

# Function to remove all numbers enclosed in square brackets
def remove_enclosed_numbers(text):
    """Remove all numbers enclosed in square brackets."""
    return re.sub(r'\[\d+\]', '', text)

# Fetch and parse the Wikipedia page
toi = requests.get('https://en.wikipedia.org/wiki/Dog').text
soup = BeautifulSoup(toi, 'lxml')
container = soup.find('div', {'class': 'mw-content-ltr mw-parser-output'})
para = container.find_all('p')

plist = []
# Identify paragraphs containing the keyword
for p in range(len(para)):
    if 'dog' in para[p].text.lower():
        plist.append(p)

# Extract and clean the required text
if plist:
    requiredtext = remove_enclosed_numbers(para[plist[0]].text)
    print("Basic information about the page:")
    print(requiredtext)
else:
    print("No relevant paragraphs found.")

# Get the table of contents for the wiki page
print("\nTable of contents for wiki page:")
contents = container.find_all('div', {'class': "mw-heading mw-heading2"})
list_of_contents = [line.text.split('[')[0].strip().lower() for line in contents]

for item in list_of_contents:
    print(item)

# Prompt the user to select a section
flag = True
while flag:
    user_input = input("Enter the part you want to access: ").lower()
    if user_input in list_of_contents:
        flag = False
        index = list_of_contents.index(user_input)
        next_tag = contents[index]
        next_sibling = next_tag.find_next_sibling()
        
        print(f"\nContent of the '{user_input}' section:")
        while next_sibling:
            # Print content until the next section heading is encountered
            if next_sibling.name == 'div' and 'mw-heading' in next_sibling.get('class', []):
                # Check if it's a heading with class 'mw-heading mw-heading2'
                if 'mw-heading2' in next_sibling.get('class', []):
                    break
                # Also print div with class 'mw-heading mw-heading3'
                if 'mw-heading3' in next_sibling.get('class', []):
                    print(next_sibling.text.strip())
            elif next_sibling.name == 'p':
                print(remove_enclosed_numbers(next_sibling.text))
            next_sibling = next_sibling.find_next_sibling()
    else:
        print("No such part found.")
