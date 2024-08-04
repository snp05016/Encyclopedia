from bs4 import BeautifulSoup
import requests
import re

def remove_enclosed_numbers(text):
    """Remove all numbers enclosed in square brackets."""
    return re.sub(r'\[\d+\]', '', text)

def fetch_wikipedia_page(keyword):
    """Fetch and parse the Wikipedia page for the given keyword."""
    formatted_input = keyword.title().replace(" ","_")
    wikipedia_link = f'https://en.wikipedia.org/wiki/{formatted_input}'
    page_content = requests.get(wikipedia_link).text
    soup = BeautifulSoup(page_content, 'lxml')
    container = soup.find('div', {'class': 'mw-content-ltr mw-parser-output'})
    return container

def extract_basic_information(container, keyword):
    """Extract the first paragraph containing the keyword."""
    paragraphs = container.find_all('p')
    plist = [p for p in paragraphs if keyword.split('_')[0].lower() in p.text.lower()]

    if plist:
        required_text = remove_enclosed_numbers(plist[0].text)
        print("Basic information about the page:")
        print(required_text)
    else:
        print("No relevant paragraphs found.")

def get_table_of_contents(container):
    """Get the table of contents for the wiki page."""
    contents = container.find_all('div', {'class': "mw-heading mw-heading2"})
    list_of_contents = [line.text.split('[')[0].strip().lower() for line in contents]
    print("\nTable of contents for wiki page:")
    for item in list_of_contents:
        print(item)
    return list_of_contents, contents

def access_section(container, list_of_contents, contents):
    """Prompt the user to select a section and print its content."""
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

def main():
    init_user_input = input('Enter what you want to search about: ').lower()
    container = fetch_wikipedia_page(init_user_input)
    
    extract_basic_information(container, init_user_input)
    
    list_of_contents, contents = get_table_of_contents(container)
    
    access_section(container, list_of_contents, contents)

if __name__ == "__main__":
    main()
