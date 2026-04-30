# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime, date
from config import DB_PATH


VACCINATION_SCHEDULE = [
    ("BCG (결핵)",                      [0],            "생후 4주 이내"),
    ("B형간염",                          [0, 1, 6],      "0, 1, 6개월"),
    ("DTaP (디프테리아·파상풍·백일해)",   [2, 4, 6, 15],  "2, 4, 6, 15-18개월"),
    ("IPV (소아마비)",                   [2, 4, 6, 18],  "2, 4, 6, 18개월"),
    ("Hib (뇌수막염)",                   [2, 4, 6, 12],  "2, 4, 6, 12-15개월"),
    ("PCV (폐렴구균)",                   [2, 4, 6, 12],  "2, 4, 6, 12-15개월"),
    ("RV (로타바이러스)",                [2, 4, 6],      "2, 4개월 또는 2, 4, 6개월"),
    ("MMR (홍역·유행성이하선염·풍진)",   [12, 48],       "12-15개월, 4-6세"),
    ("VAR (수두)",                       [12],           "12-15개월"),
    ("HepA (A형간염)",                   [12, 18],       "12-23개월, 이후 6개월 후"),
    ("Flu (인플루엔자)",                 [],             "매년 (생후 6개월 이상)"),
]

MILESTONES = [
    (1,  "얼굴 쪽으로 고개 돌리기, 빛에 반응, 소리에 놀람"),
    (2,  "사회적 미소, 소리 내기 시작, 고개 잠시 들기"),
    (3,  "목 가누기, 손 발견, 까르르 웃기"),
    (4,  "뒤집기 시도, 물체 잡기, 옹알이"),
    (6,  "혼자 앉기 시도, 이유식 시작, 낯가림 시작"),
    (9,  "기어다니기, 물건 집기·놓기, '엄마' '아빠' 소리"),
    (12, "혼자 서기·걷기 시도, 첫 단어, 컵으로 마시기"),
    (18, "혼자 걷기, 10단어 이상, 그림책 보기"),
    (24, "두 단어 연결, 뛰기, 계단 오르기"),
    (36, "세 단어 이상 문장, 세발자전거 타기, 혼자 옷 입기 시도"),
]


def init_baby_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS baby_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birthdate TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS baby_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            baby_id INTEGER NOT NULL,
            log_type TEXT NOT NULL,
            note TEXT,
            logged_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS growth_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            baby_id INTEGER NOT NULL,
            height_cm REAL,
            weight_kg REAL,
            recorded_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.commit()
    conn.close()


def _get_baby(baby_id: int = None) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    if baby_id:
        row = conn.execute(
            "SELECT id, name, birthdate FROM baby_profiles WHERE id=?", (baby_id,)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT id, name, birthdate FROM baby_profiles ORDER BY id LIMIT 1"
        ).fetchone()
    conn.close()
    return {"id": row[0], "name": row[1], "birthdate": row[2]} if row else None


def _age_months(birthdate: str) -> int:
    birth = datetime.strptime(birthdate, "%Y-%m-%d").date()
    today = date.today()
    months = (today.year - birth.year) * 12 + (today.month - birth.month)
    if today.day < birth.day:
        months -= 1
    return max(0, months)


def _age_days(birthdate: str) -> int:
    birth = datetime.strptime(birthdate, "%Y-%m-%d").date()
    return (date.today() - birth).days


def add_baby(name: str, birthdate: str) -> str:
    """아기 등록. birthdate: YYYY-MM-DD"""
    try:
        datetime.strptime(birthdate, "%Y-%m-%d")
    except ValueError:
        return "날짜 형식 오류입니다. YYYY-MM-DD 형식으로 입력해 주세요. (예: 2024-03-15)"
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO baby_profiles (name, birthdate) VALUES (?, ?)",
        (name, birthdate)
    )
    conn.commit()
    conn.close()
    days = _age_days(birthdate)
    months = _age_months(birthdate)
    return f"✅ {name} 등록 완료! (생년월일: {birthdate} / 생후 {days}일 / {months}개월)"


def get_babies() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, name, birthdate FROM baby_profiles ORDER BY id"
    ).fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "birthdate": r[2]} for r in rows]


def log_feed(note: str = "", baby_id: int = None) -> str:
    baby = _get_baby(baby_id)
    if not baby:
        return "등록된 아기가 없습니다. '아기 등록 [이름] [생년월일]' 명령을 사용해 주세요."
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO baby_logs (baby_id, log_type, note) VALUES (?, 'feed', ?)",
        (baby["id"], note or now_str)
    )
    conn.commit()
    conn.close()
    suffix = f" — {note}" if note else ""
    return f"🍼 {baby['name']} 수유 기록 완료 ({now_str}){suffix}"


def log_sleep(start: bool = True, note: str = "", baby_id: int = None) -> str:
    baby = _get_baby(baby_id)
    if not baby:
        return "등록된 아기가 없습니다."
    log_type = "sleep_start" if start else "sleep_end"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO baby_logs (baby_id, log_type, note) VALUES (?, ?, ?)",
        (baby["id"], log_type, note or now_str)
    )
    conn.commit()
    conn.close()
    label = "수면 시작" if start else "기상"
    return f"😴 {baby['name']} {label} 기록 완료 ({now_str})"


def log_diaper(note: str = "", baby_id: int = None) -> str:
    baby = _get_baby(baby_id)
    if not baby:
        return "등록된 아기가 없습니다."
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO baby_logs (baby_id, log_type, note) VALUES (?, 'diaper', ?)",
        (baby["id"], note or now_str)
    )
    conn.commit()
    conn.close()
    suffix = f" — {note}" if note else ""
    return f"🧷 {baby['name']} 기저귀 교체 기록 완료 ({now_str}){suffix}"


def add_growth(height_cm: float = None, weight_kg: float = None, baby_id: int = None) -> str:
    baby = _get_baby(baby_id)
    if not baby:
        return "등록된 아기가 없습니다."
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO growth_records (baby_id, height_cm, weight_kg) VALUES (?, ?, ?)",
        (baby["id"], height_cm, weight_kg)
    )
    conn.commit()
    conn.close()
    parts = []
    if height_cm is not None:
        parts.append(f"키 {height_cm}cm")
    if weight_kg is not None:
        parts.append(f"몸무게 {weight_kg}kg")
    return f"📏 {baby['name']} 성장 기록 완료 ({now_str}): {', '.join(parts)}"


def today_summary(baby_id: int = None) -> str:
    baby = _get_baby(baby_id)
    if not baby:
        return "등록된 아기가 없습니다."
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT log_type, note, logged_at FROM baby_logs "
        "WHERE baby_id=? AND logged_at LIKE ? ORDER BY logged_at",
        (baby["id"], today + "%")
    ).fetchall()

    growth = conn.execute(
        "SELECT height_cm, weight_kg, recorded_at FROM growth_records "
        "WHERE baby_id=? AND recorded_at LIKE ? ORDER BY id DESC LIMIT 1",
        (baby["id"], today + "%")
    ).fetchone()
    conn.close()

    age_d = _age_days(baby["birthdate"])
    age_m = _age_months(baby["birthdate"])
    lines = [f"📋 {baby['name']} 오늘의 육아 요약 (생후 {age_d}일 / {age_m}개월)"]
    lines.append(f"날짜: {today}")
    lines.append("")

    feeds = [r for r in rows if r[0] == "feed"]
    sleeps_s = [r for r in rows if r[0] == "sleep_start"]
    sleeps_e = [r for r in rows if r[0] == "sleep_end"]
    diapers = [r for r in rows if r[0] == "diaper"]

    feed_str = f"{len(feeds)}회"
    if feeds:
        feed_str += f" (마지막: {feeds[-1][2][11:16]})"
    lines.append(f"🍼 수유: {feed_str}")
    lines.append(f"😴 수면: 시작 {len(sleeps_s)}회 / 기상 {len(sleeps_e)}회")
    lines.append(f"🧷 기저귀: {len(diapers)}회")

    if growth:
        parts = []
        if growth[0]:
            parts.append(f"키 {growth[0]}cm")
        if growth[1]:
            parts.append(f"몸무게 {growth[1]}kg")
        if parts:
            lines.append(f"📏 오늘 성장 기록: {', '.join(parts)}")

    if not rows:
        lines.append("\n아직 오늘의 기록이 없습니다.")
    return "\n".join(lines)


def get_last_feed(baby_id: int = None) -> str:
    baby = _get_baby(baby_id)
    if not baby:
        return "등록된 아기가 없습니다."
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT logged_at FROM baby_logs WHERE baby_id=? AND log_type='feed' ORDER BY id DESC LIMIT 1",
        (baby["id"],)
    ).fetchone()
    conn.close()
    if not row:
        return f"{baby['name']}의 수유 기록이 없습니다."
    last_time = datetime.fromisoformat(row[0])
    elapsed = datetime.now() - last_time
    h = int(elapsed.total_seconds() // 3600)
    m = int((elapsed.total_seconds() % 3600) // 60)
    return f"🍼 {baby['name']} 마지막 수유: {row[0][11:16]} ({h}시간 {m}분 전)"


def vaccination_schedule(baby_id: int = None) -> str:
    baby = _get_baby(baby_id)
    if not baby:
        return "등록된 아기가 없습니다."
    age_m = _age_months(baby["birthdate"])
    age_d = _age_days(baby["birthdate"])
    lines = [f"💉 {baby['name']} 예방접종 일정 (현재 {age_m}개월 / 생후 {age_d}일)"]
    lines.append("")

    upcoming, done = [], []
    for vaccine, months, schedule in VACCINATION_SCHEDULE:
        if not months:
            upcoming.append(f"  📅 {vaccine}: {schedule}")
            continue
        if all(m <= age_m for m in months):
            done.append(f"  ✅ {vaccine}")
        elif months[0] <= age_m:
            remaining = [m for m in months if m > age_m]
            upcoming.append(f"  ⏳ {vaccine}: {remaining[0]}개월 차 예정")
        else:
            upcoming.append(f"  📅 {vaccine}: {months[0]}개월부터 ({schedule})")

    if upcoming:
        lines.append("▶ 예정 / 진행 중:")
        lines.extend(upcoming)
    if done:
        lines.append("\n▶ 완료 (연령 기준):")
        lines.extend(done)
    lines.append("\n⚠️ 실제 접종 일정은 반드시 소아과 의사와 확인하세요.")
    return "\n".join(lines)


def development_milestones(baby_id: int = None) -> str:
    baby = _get_baby(baby_id)
    if not baby:
        return "등록된 아기가 없습니다."
    age_m = _age_months(baby["birthdate"])
    lines = [f"🌱 {baby['name']} 발달 이정표 (현재 {age_m}개월)"]
    lines.append("")

    current = next_ms = None
    for m, desc in MILESTONES:
        if m <= age_m:
            current = (m, desc)
        elif next_ms is None:
            next_ms = (m, desc)

    if current:
        lines.append(f"✅ 현재 단계 (~{current[0]}개월):\n  {current[1]}")
    if next_ms:
        lines.append(f"\n⏭ 다음 단계 (~{next_ms[0]}개월):\n  {next_ms[1]}")

    lines.append("\n📋 전체 이정표:")
    for m, desc in MILESTONES:
        marker = "✅" if m <= age_m else "  "
        lines.append(f"  {marker} {m:2d}개월: {desc}")
    return "\n".join(lines)
