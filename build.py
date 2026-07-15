# -*- coding: utf-8 -*-
"""데이터.json + 그림/ -> 오답노트.html (그림을 base64로 박은 단일 파일)

실행:  python build.py
"""
import base64
import json
import mimetypes
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "데이터.json"
TPL = BASE / "템플릿.html"
OUT = BASE / "오답노트.html"
MARK = "/*__DATA__*/"


def to_data_uri(rel: str) -> str:
    """그림/xxx.png -> data:image/png;base64,...  (없으면 경고 후 빈 값)"""
    p = BASE / rel
    if not p.exists():
        print(f"  [경고] 그림 없음: {rel}", file=sys.stderr)
        return ""
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    print(f"  그림 삽입: {rel} ({p.stat().st_size / 1024:.0f} KB)")
    return f"data:{mime};base64,{b64}"


def main() -> int:
    for f in (DATA, TPL):
        if not f.exists():
            print(f"[오류] 파일이 없습니다: {f.name}", file=sys.stderr)
            return 1

    items = json.loads(DATA.read_text(encoding="utf-8"))
    print(f"문항 {len(items)}개 읽음")

    seen = set()
    sims = 0
    for it in items:
        pid = it.get("id", "?")
        if pid in seen:
            print(f"  [경고] 중복 id: {pid}", file=sys.stderr)
        seen.add(pid)
        if it.get("그림"):
            it["그림"] = to_data_uri(it["그림"])
        for s in it.get("유사문제", []):
            sims += 1
            if s.get("그림"):
                s["그림"] = to_data_uri(s["그림"])
    if sims:
        print(f"유사문제 {sims}개 포함")

    tpl = TPL.read_text(encoding="utf-8")
    if MARK not in tpl:
        print(f"[오류] 템플릿에 {MARK} 자리표시자가 없습니다.", file=sys.stderr)
        return 1

    payload = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    OUT.write_text(tpl.replace(MARK + "[]", payload), encoding="utf-8")
    print(f"\n완성: {OUT.name} ({OUT.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
