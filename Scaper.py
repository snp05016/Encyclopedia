from bs4 import BeautifulSoup
import requests
import re

def remove_enclosed_numbers(text):
    """Remove all numbers enclosed in square brackets."""
    return re.sub(r'\[\d+\]', '', text)

def fetch_wikipedia_page(topic):
    """Fetch the Wikipedia page for the given topic."""
    wikipedia_link = f'https://en.wikipedia.org/wiki/{topic}'
    response = requests.get(wikipedia_link)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch the Wikipedia page for {topic}")

def parse_page_content(html_content):
    """Parse the HTML content of the Wikipedia page."""
    soup = BeautifulSoup(html_content, 'lxml')
    container = soup.find('div', {'class': 'mw-content-ltr mw-parser-output'})
    paragraphs = container.find_all('p')
    contents = container.find_all('div', {'class': "mw-heading mw-heading2"})
    return paragraphs, contents

def extract_basic_info(paragraphs, keyword):
    """Extract basic information containing the keyword."""
    plist = [p for p in range(len(paragraphs)) if keyword.lower() in paragraphs[p].text.lower()]
    if plist:
        required_text = remove_enclosed_numbers(paragraphs[plist[0]].text)
        return required_text
    else:
        return "No relevant paragraphs found."

def extract_table_of_contents(contents):
    """Extract the table of contents from the Wikipedia page."""
    return [line.text.split('[')[0].strip().lower() for line in contents]

def display_content_section(contents, section_name):
    """Display the content of the specified section."""
    index = contents.index(section_name)
    next_tag = contents[index]
    next_sibling = next_tag.find_next_sibling()

    section_content = []
    while next_sibling:
        if next_sibling.name == 'div' and 'mw-heading' in next_sibling.get('class', []):
            if 'mw-heading2' in next_sibling.get('class', []):
                break
            if 'mw-heading3' in next_sibling.get('class', []):
                section_content.append(next_sibling.text.strip())
        elif next_sibling.name == 'p':
            section_content.append(remove_enclosed_numbers(next_sibling.text))
        next_sibling = next_sibling.find_next_sibling()
    return section_content

def main():
    topic = input('Enter what you want to search about: ').lower()
    formatted_topic = topic.title().replace(" ", "_")
    keyword = formatted_topic.split('_')[0]

    try:
        html_content = fetch_wikipedia_page(formatted_topic)
    except Exception as e:
        print(e)
        return

    paragraphs, contents = parse_page_content(html_content)

    basic_info = extract_basic_info(paragraphs, keyword)
    print("Basic information about the page:")
    print(basic_info)

    table_of_contents = extract_table_of_contents(contents)
    print("\nTable of contents for wiki page:")
    for item in table_of_contents:
        print(item)

    flag = True
    while flag:
        user_input = input("Enter the part you want to access: ").lower()
        if user_input in table_of_contents:
            flag = False
            section_content = display_content_section(contents, user_input)
            print(f"\nContent of the '{user_input}' section:")
            for line in section_content:
                print(line)
        else:
            print("No such part found.")

if __name__ == "__main__":
    main()
