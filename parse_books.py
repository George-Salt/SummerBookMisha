import os
import json

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import unquote, urljoin, urlsplit


def parse_book_page(id, book_url, template_url):
    response = requests.get(book_url.format(id=id))
    response.raise_for_status()
    page_code = BeautifulSoup(response.text, "lxml")

    header_tag = page_code.find("h1").text
    book_name, author_name = header_tag.split(" :: ")

    img_url = page_code.find("div", class_="bookimage").find("img")["src"]
    full_img_url = urljoin(template_url, img_url)

    book_genre_tags = page_code.find("span", class_="d_book").find_all("a")
    book_genres = [genre_tag.text for genre_tag in book_genre_tags]

    book_parameters = {
        "name": book_name.strip(),
        "author": author_name.strip(),
        "img_url": full_img_url,
        "img_path": 0,
        "genre": book_genres
    }
    return book_parameters


def download_image(img_url, folder = "./media/images/"):
    response = requests.get(img_url)
    response.raise_for_status()

    filename = urlsplit(img_url).path.split("/")[-1]
    filepath = os.path.join(folder, filename)
    with open(unquote(filepath), "wb") as file:
        file.write(response.content)
    return filepath


def save_book(id, download_url, filename, folder = "./media/books/"):
    params = {"id": id}
    response = requests.get(download_url, params=params)
    response.raise_for_status()

    filepath = os.path.join(folder, f"{sanitize_filename(filename)}.txt")
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(response.text)
    return filepath


if __name__ == "__main__":
    template_img_url = "http://tululu.org/images/nopic.gif"
    download_url = "https://tululu.org/txt.php"

    urls = ["https://tululu.org/b10362/", "https://tululu.org/b9239/", "https://tululu.org/b12620/", "https://tululu.org/b9551/", "https://tululu.org/b9182/", "https://tululu.org/b11978/", "https://tululu.org/b10235/", "https://tululu.org/b11866/", "https://tululu.org/b11858/", "https://tululu.org/b11737/", "https://tululu.org/b13014/", "https://tululu.org/b9589/", "https://tululu.org/b9067/", "https://tululu.org/b12449/"]

    os.makedirs("./media/images", exist_ok = True)
    os.makedirs("./media/books", exist_ok = True)

    books_parameters = []
    for url in urls:
        id = url.split("https://tululu.org/b")[1].split("/")[0]
        book_page = parse_book_page(id, url, template_img_url)
        save_book(id, download_url, book_page["name"])
        book_page["img_path"] = download_image(book_page["img_url"])
        books_parameters.append(book_page)

        with open(f"./media/books.json", "w", encoding="utf-8") as file:
            json.dump(books_parameters, file, ensure_ascii=False)
