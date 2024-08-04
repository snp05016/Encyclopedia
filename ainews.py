from bs4 import BeautifulSoup
import requests
import re
import os
from transformers import pipeline

# ANSI color codes for styling the terminal output
ANSI = {
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "BLUE": "\033[34m",
    "HRED": "\033[41m",
    "HGREEN": "\033[42m",
    "HBLUE": "\033[44m",
    "HORANGE": "\033[48;5;208m",
    "HYELLOW": "\033[43m",
    "HMAGENTA": "\033[45m",
    "UNDERLINE": "\033[4m",
    "RESET": "\033[0m",
    "BRIGHT CYAN": "\033[96m",
    "CLEARLINE": "\033[0K",
    "BOLD": "\033[1m",
    "ITALIC": "\033[3m"
}

# Dictionary for specific color mappings
COLORS = {'AA': ANSI['HRED'], 'BB': ANSI['HBLUE'], 'CC': ANSI['HGREEN'],
          'DD': ANSI['HORANGE'], 'EE': ANSI['HYELLOW'], 'FF': ANSI['HMAGENTA'], 'GG': ANSI['BRIGHT CYAN'],}

# Initialize AI pipelines
summarizer = pipeline("summarization")
ner_model = pipeline("ner")

def remove_enclosed_numbers(text):
    """Remove all numbers enclosed in square brackets."""
    return re.sub(r'\[\d+\]', '', text)

def fetch_wikipedia_page(keyword):
    """Fetch and parse the Wikipedia page for the given keyword."""
    formatted_input = keyword.title().replace(" ", "_")
    wikipedia_link = f'https://en.wikipedia.org/wiki/{formatted_input}'
    
    try:
        page_content = requests.get(wikipedia_link).text
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Network error occurred: {e}")
    
    if 'Wikipedia does not have an article with this exact name' in page_content:
        raise ValueError(f"Page not found for the keyword '{keyword}'")
    
    soup = BeautifulSoup(page_content, 'lxml')
    container = soup.find('div', {'class': 'mw-content-ltr mw-parser-output'})
    
    if container is None:
        raise ValueError(f"Page content could not be found for the keyword '{keyword}'")
    
    return container

def extract_basic_information(container, keyword):
    """Extract the first paragraph containing the keyword and summarize it."""
    paragraphs = container.find_all('p')
    plist = [p for p in paragraphs if keyword.split('_')[0].lower() in p.text.lower()]

    if plist:
        required_text = remove_enclosed_numbers(plist[0].text)
        summarized_text = summarizer(required_text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
        print(f"{ANSI['BLUE']}{ANSI['BOLD']}Basic information about the page:{ANSI['RESET']}")
        print(f"{ANSI['GREEN']}{ANSI['ITALIC']}{summarized_text}{ANSI['RESET']}")
    else:
        print(f"{ANSI['RED']}No relevant paragraphs found.{ANSI['RESET']}")

def get_table_of_contents(container):
    """Get the table of contents for the wiki page."""
    contents = container.find_all('div', {'class': "mw-heading mw-heading2"})
    list_of_contents = [line.text.split('[')[0].strip().lower() for line in contents]
    print(f"{ANSI['BLUE']}{ANSI['BOLD']}\nTable of contents for wiki page:{ANSI['RESET']}")
    for item in list_of_contents:
        print(f"{ANSI['GREEN']}{item}{ANSI['RESET']}")
    return list_of_contents, contents

def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def access_section(container, list_of_contents, contents):
    """Prompt the user to select a section and print its content with named entity recognition."""
    while True:
        user_input = input(f"{ANSI['BLUE']}Enter the part you want to access: {ANSI['RESET']}").lower()
        clear()
        if user_input in list_of_contents:
            index = list_of_contents.index(user_input)
            next_tag = contents[index]
            next_sibling = next_tag.find_next_sibling()

            print(f"{ANSI['RED']}\n{ANSI['BOLD']}Content of the '{user_input}' section:{ANSI['RESET']}")
            while next_sibling:
                if next_sibling.name == 'div' and 'mw-heading' in next_sibling.get('class', []):
                    if 'mw-heading2' in next_sibling.get('class', []):
                        break
                    if 'mw-heading3' in next_sibling.get('class', []):
                        print(f"{ANSI['BLUE']}{ANSI['UNDERLINE']}{ANSI['BOLD']}{next_sibling.text.strip()}{ANSI['RESET']}")
                elif next_sibling.name == 'p':
                    text = remove_enclosed_numbers(next_sibling.text)
                    entities = ner_model(text)
                    print(f"{ANSI['GREEN']}{ANSI['ITALIC']}{text}{ANSI['RESET']}")
                    print(f"{ANSI['BLUE']}Named Entities:{ANSI['RESET']}")
                    for entity in entities:
                        print(f"{ANSI['HYELLOW']}{entity['word']} ({entity['entity']}){ANSI['RESET']}")
                next_sibling = next_sibling.find_next_sibling()
            
            continue_search = input(f"{ANSI['BLUE']}Do you want to access another section? (yes/no): {ANSI['RESET']}").strip().lower()
            if continue_search == 'yes':
                print_table_of_contents(list_of_contents)
            else:
                break
        else:
            print(f"{ANSI['RED']}No such part found.{ANSI['RESET']}")

def print_table_of_contents(list_of_contents):
    """Print the table of contents."""
    print(f"{ANSI['BLUE']}{ANSI['BOLD']}\nTable of contents for wiki page:{ANSI['RESET']}")
    for item in list_of_contents:
        print(f"{ANSI['GREEN']}{item}{ANSI['RESET']}")

def main():
    while True:
        init_user_input = input(f"{ANSI['BRIGHT CYAN']}Enter what you want to search about: {ANSI['RESET']}").lower()
        clear()
        try:
            container = fetch_wikipedia_page(init_user_input)
        except ValueError as e:
            print(f"{ANSI['RED']}{e}{ANSI['RESET']}")
            continue
        
        extract_basic_information(container, init_user_input)
        
        list_of_contents, contents = get_table_of_contents(container)
        
        access_section(container, list_of_contents, contents)
        
        continue_search = input(f"{ANSI['BLUE']}Do you want to search for something else? (yes/no): {ANSI['RESET']}").strip().lower()
        if continue_search == 'no':
            print(f"{ANSI['HRED']}Exiting the program. Goodbye!{ANSI['RESET']}")
            break

if __name__ == "__main__":
    main()
