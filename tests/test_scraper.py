from types import SimpleNamespace

from app.scraper.scraper import scrape_quotes
from app.scraper import scraper


def test_scrape_quotes(monkeypatch):

    # Sample HTML for testing
    sample_html = """
    <div class="quote">
        <span class="text">Learning Python is useful.</span>
        <small class="author">John</small>
    </div>

    <div class="quote">
        <span class="text">Practice makes progress.</span>
        <small class="author">David</small>
    </div>
    """

    # Fake website response
    def fake_get(url, timeout=10):
        return SimpleNamespace(
            text=sample_html,
            raise_for_status=lambda: None
        )

    # Replace the real HTTP request
    monkeypatch.setattr(
        "app.scraper.scraper.requests.get",
        fake_get
    )

    quotes = scrape_quotes()

    # Verify the result
    assert isinstance(quotes, list)
    assert len(quotes) == 2

    assert quotes[0]["text"] == "Learning Python is useful."
    assert quotes[0]["author"] == "John"


def test_scrape_quotes_empty_page(monkeypatch):

    # Empty HTML response
    def fake_get(url, timeout=10):
        return SimpleNamespace(
            text="<html><body></body></html>",
            raise_for_status=lambda: None
        )

    monkeypatch.setattr(
        "app.scraper.scraper.requests.get",
        fake_get
    )

    quotes = scrape_quotes()

    assert quotes == []

def test_scrape_quotes_missing_author(monkeypatch):
    html = """
    <div class="quote">
        <span class="text">Learning Python</span>
    </div>
    """

    class FakeResponse:
        text = html

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        "app.scraper.scraper.requests.get",
        lambda *args, **kwargs: FakeResponse()
    )

    result = scraper.scrape_quotes()

    assert result == []

def test_scrape_quotes_missing_text(monkeypatch):
    html = """
    <div class="quote">
        <small class="author">John</small>
    </div>
    """

    class FakeResponse:
        text = html

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        "app.scraper.scraper.requests.get",
        lambda *args, **kwargs: FakeResponse()
    )

    result = scraper.scrape_quotes()

    assert result == []

def test_scrape_quotes_empty_fields(monkeypatch):
    html = """
    <div class="quote">
        <span class="text"></span>
        <small class="author"></small>
    </div>
    """

    class FakeResponse:
        text = html

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        "app.scraper.scraper.requests.get",
        lambda *args, **kwargs: FakeResponse()
    )

    result = scraper.scrape_quotes()

    assert result == []

def test_main_with_quotes(monkeypatch, capsys):
    fake_quotes = [
        {
            "text": "Learning Python",
            "author": "John"
        },
        {
            "text": "Practice coding",
            "author": "David"
        }
    ]

    monkeypatch.setattr(
        scraper,
        "scrape_quotes",
        lambda: fake_quotes
    )

    scraper.main()

    output = capsys.readouterr().out

    assert "Total quotes collected: 2" in output
    assert "Learning Python" in output

def test_main_without_quotes(monkeypatch, capsys):
    monkeypatch.setattr(
        scraper,
        "scrape_quotes",
        lambda: []
    )

    scraper.main()

    output = capsys.readouterr().out

    assert "Total quotes collected: 0" in output
    assert "No quotes found" in output

