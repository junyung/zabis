# -*- coding: utf-8 -*-
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text

from config import ZABIS_NAME
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


def print_banner():
    banner = Text(f"  Z.A.B.I.S  ", style="bold cyan")
    console.print(Panel(banner, subtitle="Zeropoint AI-Based Intelligence System", border_style="cyan"))
    console.print(f"  [dim]텍스트 모드로 실행 중 | 특수 명령: {' | '.join(COMMANDS.keys())}[/dim]\n")


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
                console.print("[yellow]마이크를 사용할 수 없습니다. voice/stt.py에서 VOICE_ENABLED=True로 변경 후 재실행하세요.[/yellow]")
            continue

        with console.status("[cyan]처리 중...[/cyan]"):
            reply = think(user_input)

        console.print(f"[bold cyan]{ZABIS_NAME}[/bold cyan]: {reply}\n")
        speak(reply)


def main():
    init_db()
    print_banner()

    if VOICE_ENABLED:
        console.print("[cyan]음성 모드 활성화됨. '자비스'라고 말하세요.[/cyan]\n")
        # 추후 wake word 루프 추가 예정
    else:
        run_text_mode()


if __name__ == "__main__":
    main()
