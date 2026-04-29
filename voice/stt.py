"""
STT 모듈 — 현재는 비활성화 상태.
마이크 사용 가능 시 listen() 함수를 활성화하세요.
"""

VOICE_ENABLED = False


def listen() -> str | None:
    """마이크에서 음성을 텍스트로 변환. 현재 비활성화."""
    if not VOICE_ENABLED:
        return None

    import speech_recognition as sr
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("듣고 있습니다...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio, language="ko-KR")
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return None
        except Exception as e:
            print(f"STT 오류: {e}")
            return None
