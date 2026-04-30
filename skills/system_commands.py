# -*- coding: utf-8 -*-
import os
import re
import subprocess
import webbrowser

from skills.file_ops import read_file, write_file, list_directory, delete_file, search_files
from skills.browser import open_url, fetch_webpage, web_search
from skills.parenting import (
    add_baby, get_babies, log_feed, log_sleep, log_diaper,
    add_growth, today_summary, get_last_feed,
    vaccination_schedule, development_milestones,
)

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
    # 명시적 검색 요청
    if m := re.search(r'(.+?)\s*(검색해줘|검색해|찾아줘|알아봐줘|알려줘|찾아봐)', t):
        query = m.group(1).strip()
        if not re.search(r'(파일|폴더)', query):
            return True, web_search(query)

    # 가격/쇼핑 관련 자연어 쿼리 → 자동으로 검색
    if re.search(r'(싼\s*곳|저렴한\s*곳|최저가|가격\s*비교|어디서\s*사|파는\s*곳|구매처|살\s*수\s*있)', t):
        query = re.sub(r'(싼\s*곳|저렴한\s*곳|최저가|가격\s*비교|어디서\s*사.*|파는\s*곳.*|구매처.*|살\s*수\s*있.*)', '', t).strip()
        query = re.sub(r'\s*(은|는|이|가|을|를|의|에서|에)\s*$', '', query).strip()
        if query:
            return True, web_search(query + ' 최저가')

    # ── 육아 명령 ────────────────────────────────────────────

    # 아기 등록: "아기 등록 이름 2024-03-15"
    if m := re.search(r'아기\s*등록\s+(\S+)\s+(\d{4}-\d{2}-\d{2})', t):
        return True, add_baby(m.group(1), m.group(2))

    # 등록된 아기 목록
    if re.search(r'(아기\s*(목록|리스트|명단)|등록된\s*아기)', t):
        babies = get_babies()
        if not babies:
            return True, "등록된 아기가 없습니다. '아기 등록 [이름] [YYYY-MM-DD]' 명령을 사용해 주세요."
        lines = ["👶 등록된 아기 목록:"]
        for b in babies:
            lines.append(f"  [{b['id']}] {b['name']} — {b['birthdate']}")
        return True, "\n".join(lines)

    # 수유 기록: "수유", "분유", "모유", "젖 먹였어"
    if re.search(r'(수유|분유|모유|젖\s*(먹|줬|먹였))', t):
        note_m = re.search(r'(ml|cc|\d+분)', t, re.IGNORECASE)
        note = note_m.group(0) if note_m else ""
        return True, log_feed(note)

    # 수면 시작: "잠들었어", "재웠어", "수면 시작"
    if re.search(r'(잠\s*들었|재웠|수면\s*시작|낮잠\s*시작|자기\s*시작)', t):
        return True, log_sleep(start=True)

    # 기상: "일어났어", "깼어", "수면 끝"
    if re.search(r'(일어났|깼어|기상|수면\s*끝|낮잠\s*끝|잠\s*깼)', t):
        return True, log_sleep(start=False)

    # 기저귀: "기저귀 갈았어", "기저귀 교체"
    if re.search(r'(기저귀\s*(갈았|교체|바꿨|갈아))', t):
        note_m = re.search(r'(대변|소변|응가|쉬|똥)', t)
        note = note_m.group(0) if note_m else ""
        return True, log_diaper(note)

    # 성장 기록: "키 75cm 몸무게 9.5kg"
    if re.search(r'(성장\s*기록|키\s*\d|몸무게\s*\d)', t):
        h = w = None
        hm = re.search(r'키\s*([\d.]+)\s*cm', t)
        wm = re.search(r'몸무게\s*([\d.]+)\s*kg', t)
        if hm:
            h = float(hm.group(1))
        if wm:
            w = float(wm.group(1))
        if h or w:
            return True, add_growth(h, w)

    # 마지막 수유 확인
    if re.search(r'(마지막\s*수유|언제\s*(수유|먹였|먹었)|수유\s*언제)', t):
        return True, get_last_feed()

    # 오늘 육아 요약
    if re.search(r'(오늘\s*(육아\s*)?(요약|정리|현황)|하루\s*(육아\s*)?(요약|정리))', t):
        return True, today_summary()

    # 예방접종 일정
    if re.search(r'(예방\s*접종|접종\s*일정|백신\s*일정)', t):
        return True, vaccination_schedule()

    # 발달 단계 / 이정표
    if re.search(r'(발달\s*(단계|이정표|현황|상태)|성장\s*단계)', t):
        return True, development_milestones()

    return False, ""
