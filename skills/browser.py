# -*- coding: utf-8 -*-
import webbrowser
import requests
import re
from html.parser import HTMLParser


class _TextExtractor(HTMLParser):
    """HTML에서 순수 텍스트만 추출하는 파서."""
    SKIP_TAGS = {'script', 'style', 'nav', 'footer', 'header', 'noscript', 'meta', 'link'}

    def __init__(self):
        super().__init__()
        self._skip = 0
        self.texts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS and self._skip > 0:
            self._skip -= 1

    def handle_data(self, data):
        if self._skip == 0:
            text = data.strip()
            if text:
                self.texts.append(text)


def _html_to_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    text = "\n".join(parser.texts)
    # 연속 빈 줄 제거
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def open_url(url: str) -> str:
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        webbrowser.open(url)
        return f"브라우저에서 열었습니다: {url}"
    except Exception as e:
        return f"URL 열기 실패: {e}"


def fetch_webpage(url: str) -> str:
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding

        text = _html_to_text(resp.text)
        if len(text) > 3000:
            text = text[:3000] + "\n...(이하 생략)"
        return f"[{url}] 페이지 내용:\n{text}"
    except requests.Timeout:
        return f"요청 시간 초과: {url}"
    except requests.HTTPError as e:
        return f"HTTP 오류 {e.response.status_code}: {url}"
    except Exception as e:
        return f"페이지 가져오기 실패: {e}"
