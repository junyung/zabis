# -*- coding: utf-8 -*-
from skills.file_ops import read_file, write_file, list_directory, delete_file, search_files
from skills.browser import open_url, fetch_webpage

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "로컬 파일의 내용을 읽습니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "읽을 파일의 경로 (예: C:/Users/me/doc.txt)"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "파일을 생성하거나 내용을 씁니다. 경로의 폴더가 없으면 자동 생성합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "저장할 파일 경로"},
                    "content": {"type": "string", "description": "파일에 쓸 내용"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "폴더의 파일과 하위 폴더 목록을 봅니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "조회할 폴더 경로 (기본값: 현재 폴더 '.')"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "파일을 삭제합니다. 폴더는 삭제하지 않습니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "삭제할 파일 경로"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "파일 이름 패턴으로 파일을 검색합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "검색 패턴 (예: *.txt, *.py, report*)"},
                    "directory": {"type": "string", "description": "검색 시작 폴더 (기본값: '.')"}
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_url",
            "description": "기본 브라우저에서 URL을 엽니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "열 URL (예: https://google.com)"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_webpage",
            "description": "웹 페이지의 텍스트 내용을 가져옵니다. 뉴스, 검색결과, 정보 조회에 사용합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "내용을 가져올 웹 페이지 URL"}
                },
                "required": ["url"]
            }
        }
    },
]

TOOL_MAP = {
    "read_file": lambda args: read_file(**args),
    "write_file": lambda args: write_file(**args),
    "list_directory": lambda args: list_directory(**args),
    "delete_file": lambda args: delete_file(**args),
    "search_files": lambda args: search_files(**args),
    "open_url": lambda args: open_url(**args),
    "fetch_webpage": lambda args: fetch_webpage(**args),
}


def dispatch_tool(name: str, args: dict) -> str:
    fn = TOOL_MAP.get(name)
    if not fn:
        return f"알 수 없는 도구: {name}"
    try:
        return fn(args)
    except Exception as e:
        return f"도구 실행 오류 ({name}): {e}"
