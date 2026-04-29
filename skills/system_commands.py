import os
import subprocess
import webbrowser
import re


COMMAND_PATTERNS = [
    (r"(메모장|notepad).*열어", lambda: subprocess.Popen("notepad.exe")),
    (r"(계산기|calculator).*열어", lambda: subprocess.Popen("calc.exe")),
    (r"(탐색기|explorer).*열어", lambda: subprocess.Popen("explorer.exe")),
    (r"(크롬|chrome).*열어", lambda: subprocess.Popen("chrome.exe")),
    (r"유튜브.*열어", lambda: webbrowser.open("https://youtube.com")),
    (r"구글.*열어", lambda: webbrowser.open("https://google.com")),
]


def parse_command(text: str) -> tuple[bool, str]:
    """명령어를 파싱하여 실행. 반환: (실행여부, 결과메시지)"""
    text_lower = text.lower()

    # 웹 검색
    if m := re.search(r"(.+?)\s*(검색|찾아줘|알려줘)", text):
        query = m.group(1).strip()
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return True, f"'{query}'를 검색했습니다."

    # 앱/웹 실행
    for pattern, action in COMMAND_PATTERNS:
        if re.search(pattern, text_lower):
            try:
                action()
                return True, "실행했습니다."
            except Exception as e:
                return True, f"실행 중 오류가 발생했습니다: {e}"

    # 볼륨 조절
    if "볼륨" in text or "소리" in text:
        if "올려" in text or "크게" in text:
            subprocess.run(
                ["powershell", "-c",
                 "$obj=New-Object -ComObject WScript.Shell; $obj.SendKeys([char]175)"],
                capture_output=True
            )
            return True, "볼륨을 높였습니다."
        elif "내려" in text or "작게" in text:
            subprocess.run(
                ["powershell", "-c",
                 "$obj=New-Object -ComObject WScript.Shell; $obj.SendKeys([char]174)"],
                capture_output=True
            )
            return True, "볼륨을 낮췄습니다."

    return False, ""
