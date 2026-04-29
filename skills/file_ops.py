# -*- coding: utf-8 -*-
import os
import glob as glob_module
import shutil


def read_file(path: str) -> str:
    try:
        path = os.path.expanduser(path.strip())
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if len(content) > 4000:
            content = content[:4000] + "\n...(이하 생략, 파일이 너무 큽니다)"
        return f"[{path}] 내용:\n{content}"
    except FileNotFoundError:
        return f"파일을 찾을 수 없습니다: {path}"
    except Exception as e:
        return f"파일 읽기 실패: {e}"


def write_file(path: str, content: str) -> str:
    try:
        path = os.path.expanduser(path.strip())
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"파일을 저장했습니다: {path}"
    except Exception as e:
        return f"파일 저장 실패: {e}"


def list_directory(path: str = ".") -> str:
    try:
        path = os.path.expanduser(path.strip())
        items = sorted(os.listdir(path))
        lines = [f"[{os.path.abspath(path)}]"]
        for item in items:
            full = os.path.join(path, item)
            if os.path.isdir(full):
                lines.append(f"  DIR  {item}/")
            else:
                size = os.path.getsize(full)
                lines.append(f"  FILE {item}  ({size:,} bytes)")
        return "\n".join(lines)
    except FileNotFoundError:
        return f"폴더를 찾을 수 없습니다: {path}"
    except Exception as e:
        return f"폴더 목록 조회 실패: {e}"


def delete_file(path: str) -> str:
    try:
        path = os.path.expanduser(path.strip())
        if not os.path.exists(path):
            return f"파일을 찾을 수 없습니다: {path}"
        if os.path.isdir(path):
            return f"폴더 삭제는 지원하지 않습니다 (안전상의 이유): {path}"
        os.remove(path)
        return f"파일을 삭제했습니다: {path}"
    except Exception as e:
        return f"삭제 실패: {e}"


def search_files(pattern: str, directory: str = ".") -> str:
    try:
        directory = os.path.expanduser(directory.strip())
        matches = glob_module.glob(
            os.path.join(directory, "**", pattern), recursive=True
        )
        if not matches:
            return f"'{pattern}' 패턴과 일치하는 파일이 없습니다."
        result = f"검색 결과 ({len(matches)}개):\n"
        result += "\n".join(matches[:30])
        if len(matches) > 30:
            result += f"\n...(총 {len(matches)}개 중 30개만 표시)"
        return result
    except Exception as e:
        return f"검색 실패: {e}"
