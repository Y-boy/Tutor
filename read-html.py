from bs4 import BeautifulSoup

if __name__ == "__main__":
    file_path = "test.html"
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
        soup = BeautifulSoup(html_content)
        title = soup.find('h1')
        print(title)