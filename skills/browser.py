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


_SHOPPING_KEYWORDS = re.compile(r'(싼|싸게|저렴|가격|최저가|비교|구매|살\s*곳|파는\s*곳|어디서|추천)')


def web_search(query: str, num_results: int = 5) -> str:
    """네이버 검색에서 실제 결과를 가져옵니다. 쇼핑 쿼리는 가격비교 링크를 포함합니다."""
    import urllib.parse

    is_shopping = bool(_SHOPPING_KEYWORDS.search(query))
    encoded = urllib.parse.quote(query)
    lines = [f"🔍 '{query}' 검색 결과\n"]

    # 쇼핑/가격 비교 쿼리: 주요 쇼핑 사이트 링크 먼저 제공
    if is_shopping:
        lines.append("📦 가격 비교 사이트")
        lines.append(f"  • 네이버 쇼핑: https://search.shopping.naver.com/search/all?query={encoded}")
        lines.append(f"  • 다나와: https://search.danawa.com/dsearch.php?query={encoded}")
        lines.append(f"  • 쿠팡: https://www.coupang.com/np/search?q={urllib.parse.quote(query, safe='')}")
        lines.append("")

    # 네이버 일반 검색에서 외부 링크 파싱
    try:
        naver_url = f"https://search.naver.com/search.naver?query={encoded}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'ko-KR,ko;q=0.9',
            'Referer': 'https://www.naver.com',
        }
        resp = requests.get(naver_url, headers=headers, timeout=8)
        resp.encoding = 'utf-8'

        # 외부 링크 + 주변 제목 텍스트 추출
        # Naver 검색 결과의 실제 링크는 a 태그의 href에 있고 naver 도메인이 아닌 것들
        skip = re.compile(
            r'(naver\.com|pstatic\.net|javascript|\.css|\.js|\.ico|\.png|\.svg|account\.kakao|appleid\.apple)'
        )
        raw_links = re.findall(r'href="(https?://[^"]+)"', resp.text)
        seen, results = set(), []
        for link in raw_links:
            if not skip.search(link) and link not in seen:
                seen.add(link)
                results.append(link)
            if len(results) >= num_results:
                break

        if results:
            lines.append("🌐 웹 검색 결과")
            for i, link in enumerate(results, 1):
                lines.append(f"  {i}. {link}")
        elif not is_shopping:
            lines.append(f"검색 결과 링크를 가져오지 못했습니다.")
            lines.append(f"직접 검색: {naver_url}")

    except Exception as e:
        if not is_shopping:
            lines.append(f"검색 실패: {e}")

    return "\n".join(lines)


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
