from bs4 import BeautifulSoup
import requests
import re
import os
import time
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

def remove_enclosed_numbers(text):
    """Remove all numbers enclosed in square brackets."""
    return re.sub(r'\[\d+\]', '', text)

def fetch_wikipedia_page(keyword):
    """Fetch and parse the Wikipedia page for the given keyword."""
    # Format the keyword to fit Wikipedia's URL structure
    formatted_input = keyword.title().replace(" ", "_")
    wikipedia_link = f'https://en.wikipedia.org/wiki/{formatted_input}'
    
    try:
        # Request the page content
        page_content = requests.get(wikipedia_link).text
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Network error occurred: {e}")
    
    # Check if the page does not exist
    if 'Wikipedia does not have an article with this exact name' in page_content:
        raise ValueError(f"Page not found for the keyword '{keyword}'")
    
    # Parse the HTML content
    soup = BeautifulSoup(page_content, 'lxml')
    container = soup.find('div', {'class': 'mw-content-ltr mw-parser-output'})
    
    # Additional check if the container is empty
    if container is None:
        raise ValueError(f"Page content could not be found for the keyword '{keyword}'")
    
    return container

def extract_basic_information(container, keyword):
    """Extract the first paragraph containing the keyword."""
    paragraphs = container.find_all('p')
    plist = [p for p in paragraphs if keyword.split('_')[0].lower() in p.text.lower()]

    if plist:
        # Remove enclosed numbers and print the required text
        required_text = remove_enclosed_numbers(plist[0].text)
        print(f"{ANSI['BLUE']}{ANSI['BOLD']}Basic information about the page:{ANSI['RESET']}")
        print(f"{ANSI['GREEN']}{ANSI['ITALIC']}{required_text}{ANSI['RESET']}")
    else:
        print(f"{ANSI['RED']}No relevant paragraphs found.{ANSI['RESET']}")

def get_table_of_contents(container):
    """Get the table of contents for the wiki page."""
    # Find all div elements with the specified class
    contents = container.find_all('div', {'class': "mw-heading mw-heading2"})
    list_of_contents = [line.text.split('[')[0].strip().lower() for line in contents]
    print(f"{ANSI['BLUE']}{ANSI['BOLD']}\nTable of contents for wiki page:{ANSI['RESET']}")
    for item in list_of_contents:
        print(f"{ANSI['GREEN']}{item}{ANSI['RESET']}")
    return list_of_contents, contents

def clear():
    """Clear the terminal screen."""
    # Try Windows clear command
    if os.name == 'nt':
        os.system('cls')
    # Otherwise, assume it's a Unix-like system and try the clear command
    else:
        os.system('clear')

# Example usage
def access_section(container, list_of_contents, contents):
    """Prompt the user to select a section and print its content."""
    while True:
        user_input = input(f"{ANSI['BLUE']}Enter the part you want to access: {ANSI['RESET']}").lower()
        clear()
        if user_input in list_of_contents:
            index = list_of_contents.index(user_input)
            next_tag = contents[index]
            next_sibling = next_tag.find_next_sibling()

            print(f"{ANSI['RED']}\n{ANSI['BOLD']}Content of the '{user_input}' section:{ANSI['RESET']}")
            while next_sibling:
                # Print content until the next section heading is encountered
                if next_sibling.name == 'div' and 'mw-heading' in next_sibling.get('class', []):
                    # Check if it's a heading with class 'mw-heading mw-heading2'
                    if 'mw-heading2' in next_sibling.get('class', []):
                        break
                    # Also print div with class 'mw-heading mw-heading3'
                    if 'mw-heading3' in next_sibling.get('class', []):
                        print(f"{ANSI['BLUE']}{ANSI['UNDERLINE']}{ANSI['BOLD']}{next_sibling.text.strip()}{ANSI['RESET']}")
                elif next_sibling.name == 'p':
                    print(f"{ANSI['GREEN']}{ANSI['ITALIC']}{remove_enclosed_numbers(next_sibling.text)}{ANSI['RESET']}")
                next_sibling = next_sibling.find_next_sibling()
            
            # Ask if the user wants to access another section
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
    """Main function to run the program."""
    clear()
    print(f"{ANSI['UNDERLINE']}Welcome to Saumya's Encyclopedia Project!")
    time.sleep(2)
    clear()
    while True:
        # Prompt user for input keyword
        init_user_input = input(f"{ANSI['BRIGHT CYAN']}Enter what you want to search about:{ANSI['RESET']}").lower()
        clear()
        try:
            container = fetch_wikipedia_page(init_user_input)
        except ValueError as e:
            print(f"{ANSI['RED']}{e}{ANSI['RESET']}")
            continue
        
        extract_basic_information(container, init_user_input)
        
        list_of_contents, contents = get_table_of_contents(container)

        access_section(container, list_of_contents, contents)
        
        # Ask if the user wants to search for something else
        continue_search = input(f"{ANSI['BLUE']}Do you want to search for something else? (yes/no):{ANSI['RESET']}").strip().lower()
        if continue_search == 'no':
            time.sleep(1)
            print(f"{ANSI['HRED']}Exiting the program. Goodbye!{ANSI['RESET']}")
            break

if __name__ == "__main__":
    main()
