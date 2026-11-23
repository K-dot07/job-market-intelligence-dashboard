import requests
from bs4 import BeautifulSoup


def scrape_quotes():

    url = "https://quotes.toscrape.com/"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    quotes = []
    quote_cards = soup.select(".quote")

    for quote_card in quote_cards:

        quote_text = quote_card.select_one(".text")
        author = quote_card.select_one(".author")

        if quote_text and author:

            text = quote_text.get_text(strip=True)
            author_name = author.get_text(strip=True)

            if text and author_name:

                quote = {
                    "text": text,
                    "author": author_name
                }

                quotes.append(quote)

    return quotes


def main():
    quotes = scrape_quotes()

    print("Total quotes collected:", len(quotes))
    print("First quote:", quotes[0] if quotes else "No quotes found")


if __name__ == "__main__":
    main()