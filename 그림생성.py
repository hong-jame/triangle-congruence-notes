# -*- coding: utf-8 -*-
"""문항 023 그림 SVG 생성 + 답 검산

구조: CA=CB, CD=CE, ∠ACB=∠DCE=θ. A, D, P, E는 한 직선 위(P=AE∩BC).
θ=60이면 두 정삼각형(원문항).
일반해: △ACD ≡ △BCE (SAS) → ∠BEC = ∠ADC = 180° - ∠CDE = 90° + θ/2

실행: python 그림생성.py
"""
from math import cos, sin, radians, degrees, atan2, hypot
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / "그림"


# ---------- 기하 ----------
def rot(v, d):
    r = radians(d)
    return (v[0] * cos(r) - v[1] * sin(r), v[0] * sin(r) + v[1] * cos(r))


def sub(p, q):
    return (p[0] - q[0], p[1] - q[1])


def add(p, q):
    return (p[0] + q[0], p[1] + q[1])


def cross(u, v):
    return u[0] * v[1] - u[1] * v[0]


def dot(u, v):
    return u[0] * v[0] + u[1] * v[1]


def dist(p, q):
    return hypot(p[0] - q[0], p[1] - q[1])


def angle(P, Q, R):
    """∠QPR (꼭짓점 P)"""
    u, v = sub(Q, P), sub(R, P)
    return degrees(atan2(abs(cross(u, v)), dot(u, v)))


def solve(theta, r):
    """B=(0,0), C=(1,0) 고정. A,D,P,E 일직선이 되는 D를 찾아 전체 점 반환"""
    B, C = (0.0, 0.0), (1.0, 0.0)
    A = add(C, (cos(radians(180 - theta)), sin(radians(180 - theta))))

    def pts(t):
        D = add(C, (r * cos(radians(t)), r * sin(radians(t))))
        E = add(C, rot(sub(D, C), theta))
        return D, E

    def f(t):
        D, E = pts(t)
        return cross(sub(D, A), sub(E, A))

    # 부호 변화 구간 탐색 후 이분법
    ts = [90 + i * 0.5 for i in range(221)]
    br = None
    for i in range(len(ts) - 1):
        if (f(ts[i]) < 0) != (f(ts[i + 1]) < 0):
            br = (ts[i], ts[i + 1])
            break
    if br is None:
        raise RuntimeError(f"일직선 해 없음 (theta={theta}, r={r})")
    a, b = br
    fa = f(a)
    for _ in range(200):
        m = (a + b) / 2
        fm = f(m)
        if (fa < 0) != (fm < 0):
            b = m
        else:
            a, fa = m, fm
    t = (a + b) / 2
    D, E = pts(t)
    # P = AE ∩ BC (y=0)
    s = A[1] / (A[1] - E[1])
    P = (A[0] + s * (E[0] - A[0]), 0.0)
    return dict(A=A, B=B, C=C, D=D, E=E, P=P)


# ---------- SVG ----------
SC = 300.0
OX, OY = 70.0, 330.0


def px(p):
    return (OX + p[0] * SC, OY - p[1] * SC)


def arc_at(V, P1, P2, rad=26):
    """꼭짓점 V에서 VP1 ~ VP2 사이 각을 나타내는 호"""
    a1 = atan2(*reversed(sub(P1, V)))
    a2 = atan2(*reversed(sub(P2, V)))
    d = degrees(a2 - a1)
    while d <= -180:
        d += 360
    while d > 180:
        d -= 360
    sweep = 0 if d > 0 else 1  # y축 뒤집힘 보정
    s = px(add(V, (rad / SC * cos(a1), rad / SC * sin(a1))))
    e = px(add(V, (rad / SC * cos(a2), rad / SC * sin(a2))))
    big = 1 if abs(d) > 180 else 0
    return (f'<path d="M {s[0]:.1f} {s[1]:.1f} A {rad} {rad} 0 {big} {sweep} '
            f'{e[0]:.1f} {e[1]:.1f}" fill="none" stroke="#c2410c" stroke-width="2.5"/>')


def tick(P, Q, n=1):
    """선분 PQ 중점에 등길이 표시(빗금 n개)"""
    mx, my = (P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2
    ux, uy = Q[0] - P[0], Q[1] - P[1]
    L = hypot(ux, uy)
    ux, uy = ux / L, uy / L
    nx, ny = -uy, ux
    out = []
    for k in range(n):
        off = (k - (n - 1) / 2) * 7.0 / SC
        c = (mx + ux * off, my + uy * off)
        a = px((c[0] - nx * 7 / SC, c[1] - ny * 7 / SC))
        b = px((c[0] + nx * 7 / SC, c[1] + ny * 7 / SC))
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                   f'stroke="#1b1f24" stroke-width="2"/>')
    return "".join(out)


def label(name, p, dx, dy):
    x, y = px(p)
    return (f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" font-family="Times New Roman,serif" '
            f'font-size="26" font-style="italic" fill="#1b1f24">{name}</text>')


def make_svg(theta, r, mark_angle=("B", "E", "C"), show_P=True):
    p = solve(theta, r)
    A, B, C, D, E, P = p["A"], p["B"], p["C"], p["D"], p["E"], p["P"]

    def ln(u, v, w=2.2, col="#1b1f24"):
        a, b = px(u), px(v)
        return (f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                f'stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')

    body = []
    # 변
    body += [ln(A, B), ln(B, C), ln(C, A)]      # △ABC
    body += [ln(C, D), ln(C, E)]                # △DEC (DE는 AE 직선의 일부)
    body += [ln(A, E)]                          # A-D-P-E 직선
    body += [ln(B, E)]                          # BE
    # 등길이 표시
    body += [tick(C, A, 1), tick(C, B, 1), tick(A, B, 1)]
    body += [tick(C, D, 2), tick(C, E, 2), tick(D, E, 2)]
    # 각 표시
    V, P1, P2 = (p[mark_angle[1]], p[mark_angle[0]], p[mark_angle[2]])
    body.append(arc_at(V, P1, P2))
    # 점
    for k in ("A", "B", "C", "D", "E") + (("P",) if show_P else ()):
        x, y = px(p[k])
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="#1b1f24"/>')
    # 라벨
    body.append(label("A", A, -8, -14))
    body.append(label("B", B, -30, 8))
    body.append(label("C", C, 12, 8))
    body.append(label("D", D, -30, -8))
    body.append(label("E", E, -6, 34))
    if show_P:
        body.append(label("P", P, -26, 24))

    xs = [px(p[k])[0] for k in p] + [OX]
    ys = [px(p[k])[1] for k in p]
    x0, x1 = min(xs) - 45, max(xs) + 45
    y0, y1 = min(ys) - 40, max(ys) + 50
    w, h = x1 - x0, y1 - y0
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.0f} {y0:.0f} {w:.0f} {h:.0f}" '
            f'width="{w:.0f}" height="{h:.0f}" role="img">' + "".join(body) + "</svg>"), p


# ---------- 실행 ----------
CASES = [
    ("01", 50, 0.45, ("B", "E", "C")),      # 본문항: 꼭지각 50° 이등변, ∠BEC = 115°
    ("01_1", 50, 0.45, ("B", "E", "A")),    # 유사1: 같은 그림, ∠BEA = 50°
    ("01_2", 90, 0.42, ("B", "E", "C")),    # 유사2: 직각이등변, ∠BEC = 135°
    ("01_3", 80, 0.45, ("B", "E", "C")),    # 유사3: 역방향(∠BEC=130° → ∠ACB=80° 찾기)
]

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    print(f"{'id':8} {'θ':>4} {'∠BEC':>7} {'예측(90+θ/2)':>12} {'∠ADC':>7} {'∠BEA':>7} {'검증'}")
    for name, th, r, mk in CASES:
        svg, p = make_svg(th, r, mk)
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        A, B, C, D, E = p["A"], p["B"], p["C"], p["D"], p["E"]
        bec, adc, bea = angle(E, B, C), angle(D, A, C), angle(E, B, A)
        pred = 90 + th / 2
        ok = (abs(bec - pred) < 1e-6 and abs(bec - adc) < 1e-6
              and abs(dist(C, A) - dist(C, B)) < 1e-9
              and abs(dist(C, D) - dist(C, E)) < 1e-9
              and abs(angle(C, A, D) - angle(C, B, E)) < 1e-6      # ∠ACD = ∠BCE
              and abs(cross(sub(D, A), sub(E, A))) < 1e-9)          # A,D,E 일직선
        print(f"{name:8} {th:4} {bec:7.2f} {pred:12.2f} {adc:7.2f} {bea:7.2f}  {'OK' if ok else 'FAIL'}")
