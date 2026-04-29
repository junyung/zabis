# -*- coding: utf-8 -*-
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text

from config import ZABIS_NAME, TELEGRAM_TOKEN
from core.memory import init_db, clear_history
from core.brain import think
from voice.tts import speak
from voice.stt import listen, VOICE_ENABLED

console = Console()

COMMANDS = {
    "/clear": "대화 기록 초기화",
    "/voice": "음성 모드 전환 (마이크 필요)",
    "/quit": "종료",
}


def print_banner(mode: str = "텍스트"):
    banner = Text(f"  Z.A.B.I.S  ", style="bold cyan")
    console.print(Panel(banner, subtitle="Zeropoint AI-Based Intelligence System", border_style="cyan"))
    console.print(f"  [dim]{mode} 모드로 실행 중 | 특수 명령: {' | '.join(COMMANDS.keys())}[/dim]\n")


def run_text_mode():
    while True:
        try:
            user_input = Prompt.ask("[bold green]나[/bold green]").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        if user_input == "/quit":
            console.print(f"[dim]{ZABIS_NAME}: 종료합니다. 좋은 하루 되세요.[/dim]")
            break
        elif user_input == "/clear":
            clear_history()
            console.print("[dim]대화 기록을 초기화했습니다.[/dim]")
            continue
        elif user_input == "/voice":
            if not VOICE_ENABLED:
                console.print("[yellow]마이크를 사용할 수 없습니다. voice/stt.py에서 VOICE_ENABLED=True로 변경하세요.[/yellow]")
            continue

        with console.status("[cyan]처리 중...[/cyan]"):
            reply = think(user_input)

        console.print(f"[bold cyan]{ZABIS_NAME}[/bold cyan]: {reply}\n")
        speak(reply)


def run_telegram_mode():
    from skills.telegram_bot import run_telegram_bot
    console.print(f"[bold cyan]{ZABIS_NAME}[/bold cyan]: 텔레그램 봇으로 시작합니다.\n")
    run_telegram_bot()


def main():
    init_db()

    # --telegram 플래그 또는 TELEGRAM_TOKEN 설정 시 텔레그램 모드
    use_telegram = "--telegram" in sys.argv or (TELEGRAM_TOKEN and "--text" not in sys.argv)

    if use_telegram and TELEGRAM_TOKEN:
        print_banner("텔레그램")
        run_telegram_mode()
    else:
        print_banner("텍스트")
        run_text_mode()


if __name__ == "__main__":
    main()
