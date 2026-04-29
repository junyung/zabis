# -*- coding: utf-8 -*-
import os
import re
import subprocess
import webbrowser

from skills.file_ops import read_file, write_file, list_directory, delete_file, search_files
from skills.browser import open_url, fetch_webpage, web_search

# 앱/웹 바로 실행 패턴
_APP_PATTERNS = [
    (r"(메모장|notepad)", lambda: subprocess.Popen("notepad.exe")),
    (r"(계산기|calculator)", lambda: subprocess.Popen("calc.exe")),
    (r"(탐색기|explorer)", lambda: subprocess.Popen("explorer.exe")),
    (r"(크롬|chrome)", lambda: subprocess.Popen("chrome.exe")),
]

# URL 패턴
_URL_RE = re.compile(r'(https?://\S+|[a-zA-Z0-9][\w.-]+\.[a-zA-Z]{2,}(?:/\S*)?)')

# 파일 경로 패턴 (드라이브 포함 또는 상대경로)
_PATH_RE = re.compile(r'([A-Za-z]:[/\\][^\s"\']+|[./][^\s"\']+|\S+\.\w{1,10})')


def _extract_url(text: str) -> str | None:
    m = _URL_RE.search(text)
    return m.group(1) if m else None


def _extract_path(text: str) -> str | None:
    m = _PATH_RE.search(text)
    return m.group(1) if m else None


def parse_command(text: str) -> tuple[bool, str]:
    """
    명령어를 파싱하여 실행.
    반환: (실행여부, 결과메시지)
    """
    t = text.strip()

    # ── 웹 페이지 내용 가져오기 ──────────────────────────────
    if re.search(r'(내용|크롤링|스크래핑|읽어줘|가져와).{0,10}$', t) and _extract_url(t):
        url = _extract_url(t)
        return True, fetch_webpage(url)

    if re.search(r'^(웹|페이지|사이트)\s', t) and re.search(r'(내용|읽어|가져)', t):
        url = _extract_url(t)
        if url:
            return True, fetch_webpage(url)

    # ── URL 브라우저로 열기 ──────────────────────────────────
    if re.search(r'(접속|열어|열기|이동)', t) and _extract_url(t):
        url = _extract_url(t)
        return True, open_url(url)

    # ── 파일 읽기 ────────────────────────────────────────────
    if re.search(r'(읽어|열어|보여)', t) and _extract_path(t):
        path = _extract_path(t)
        if os.path.isfile(path):
            return True, read_file(path)

    # ── 폴더 목록 ────────────────────────────────────────────
    if re.search(r'(폴더|디렉터리|목록|파일들?)\s*(보여|알려|나열)', t):
        path = _extract_path(t) or "."
        if not os.path.isfile(path):
            return True, list_directory(path)

    if re.search(r'(폴더|디렉터리|목록)', t) and re.search(r'(보여|알려|나열)', t):
        path = _extract_path(t) or "."
        return True, list_directory(path)

    # ── 파일 삭제 ────────────────────────────────────────────
    if re.search(r'(삭제|지워|없애)', t) and _extract_path(t):
        path = _extract_path(t)
        if os.path.exists(path):
            return True, delete_file(path)

    # ── 파일 검색 ────────────────────────────────────────────
    if re.search(r'(찾아|검색).{0,5}(파일|\.)', t):
        m = re.search(r'(\S+\.\w+|\*\.\w+)', t)
        pattern = m.group(1) if m else "*.txt"
        directory = _extract_path(t) or "."
        if os.path.isdir(directory):
            return True, search_files(pattern, directory)
        return True, search_files(pattern)

    # ── 볼륨 조절 ────────────────────────────────────────────
    if re.search(r'(볼륨|소리)', t):
        if re.search(r'(올려|크게)', t):
            subprocess.run(
                ["powershell", "-c",
                 "$obj=New-Object -ComObject WScript.Shell; $obj.SendKeys([char]175)"],
                capture_output=True
            )
            return True, "볼륨을 높였습니다."
        if re.search(r'(내려|작게)', t):
            subprocess.run(
                ["powershell", "-c",
                 "$obj=New-Object -ComObject WScript.Shell; $obj.SendKeys([char]174)"],
                capture_output=True
            )
            return True, "볼륨을 낮췄습니다."

    # ── 앱 실행 ──────────────────────────────────────────────
    for pattern, action in _APP_PATTERNS:
        if re.search(pattern, t, re.IGNORECASE):
            try:
                action()
                return True, "실행했습니다."
            except Exception as e:
                return True, f"실행 중 오류가 발생했습니다: {e}"

    # ── 웹 검색 (실제 결과 파싱) ─────────────────────────────
    if m := re.search(r'(.+?)\s*(검색해줘|검색해|찾아줘|알아봐줘)', t):
        query = m.group(1).strip()
        if not re.search(r'(파일|폴더)', query):
            return True, web_search(query)

    return False, ""
