# -*- coding: utf-8 -*-
"""문항 01 그림 SVG 생성 + 답 검산

구조: 직선 위에 A, C, B 순으로 놓고, 같은 쪽에
      △ACD (CA=CD, ∠ACD=θ) 와 △CBE (CE=CB, ∠ECB=θ) 를 세운다.
      AE 와 BD 의 교점을 P 라 한다.

핵심: ∠ACE = ∠ACD + ∠DCE, ∠DCB = ∠DCE + ∠ECB 인데 ∠ACD = ∠ECB = θ 이므로
      공통인 ∠DCE 에 같은 각을 '더해서' 두 끼인각이 같아진다.
      → △ACE ≡ △DCB (SAS) → AE = DB, ∠CAE = ∠CDB
      → ∠APB = 180° − (∠CDB + ∠DBC) = ∠DCB = 180° − θ
      θ=60(정삼각형) 이면 ∠APB = 120°, ∠APD = θ = 60°

실행: python 그림생성.py
"""
from math import cos, sin, radians, degrees, atan2, hypot
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / "그림"

# 직선 위 세 점 (C는 A와 B 사이 아무 데나 — 답은 C 위치와 무관)
AX, CX, BX = 0.0, 1.5, 4.0


# ---------- 기하 ----------
def sub(p, q):
    return (p[0] - q[0], p[1] - q[1])


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


def meet(P1, P2, P3, P4):
    """직선 P1P2 와 P3P4 의 교점"""
    d = cross(sub(P2, P1), sub(P4, P3))
    t = cross(sub(P3, P1), sub(P4, P3)) / d
    return (P1[0] + t * (P2[0] - P1[0]), P1[1] + t * (P2[1] - P1[1]))


def solve(theta):
    A, C, B = (AX, 0.0), (CX, 0.0), (BX, 0.0)
    rA, rB = CX - AX, BX - CX
    # D: CD = CA, ∠ACD = θ (A 방향 180°에서 θ 만큼 위로)
    D = (C[0] + rA * cos(radians(180 - theta)), C[1] + rA * sin(radians(180 - theta)))
    # E: CE = CB, ∠ECB = θ (B 방향 0°에서 θ 만큼 위로)
    E = (C[0] + rB * cos(radians(theta)), C[1] + rB * sin(radians(theta)))
    P = meet(A, E, B, D)
    return dict(A=A, B=B, C=C, D=D, E=E, P=P)


# ---------- SVG ----------
SC = 95.0
OX, OY = 40.0, 300.0


def px(p):
    return (OX + p[0] * SC, OY - p[1] * SC)


def arc_at(V, P1, P2, rad=24):
    a1 = atan2(*reversed(sub(P1, V)))
    a2 = atan2(*reversed(sub(P2, V)))
    d = degrees(a2 - a1)
    while d <= -180:
        d += 360
    while d > 180:
        d -= 360
    sweep = 0 if d > 0 else 1  # y축 뒤집힘 보정
    s = px((V[0] + rad / SC * cos(a1), V[1] + rad / SC * sin(a1)))
    e = px((V[0] + rad / SC * cos(a2), V[1] + rad / SC * sin(a2)))
    return (f'<path d="M {s[0]:.1f} {s[1]:.1f} A {rad} {rad} 0 0 {sweep} '
            f'{e[0]:.1f} {e[1]:.1f}" fill="none" stroke="#c2410c" stroke-width="2.5"/>')


def tick(P, Q, n=1):
    """선분 PQ 중점에 등길이 표시"""
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


def make_svg(theta, mark=("A", "P", "B")):
    p = solve(theta)
    A, B, C, D, E, P = p["A"], p["B"], p["C"], p["D"], p["E"], p["P"]

    def ln(u, v, w=2.2):
        a, b = px(u), px(v)
        return (f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                f'stroke="#1b1f24" stroke-width="{w}" stroke-linecap="round"/>')

    body = []
    body += [ln(A, B)]                    # 밑변 직선 A-C-B
    body += [ln(A, D), ln(D, C)]          # △ACD
    body += [ln(C, E), ln(E, B)]          # △CBE
    body += [ln(A, E), ln(B, D)]          # 교차하는 두 선
    # 등길이 표시: CA = CD (빗금 1개), CE = CB (빗금 2개)
    body += [tick(C, A, 1), tick(C, D, 1)]
    body += [tick(C, E, 2), tick(C, B, 2)]
    # 각 표시
    body.append(arc_at(p[mark[1]], p[mark[0]], p[mark[2]]))
    # 점
    for k in ("A", "B", "C", "D", "E", "P"):
        x, y = px(p[k])
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="#1b1f24"/>')
    # 라벨
    body.append(label("A", A, -28, 22))
    body.append(label("B", B, 10, 22))
    body.append(label("C", C, -8, 26))
    body.append(label("D", D, -28, -8))
    body.append(label("E", E, 10, -8))
    body.append(label("P", P, -6, -12))

    xs = [px(p[k])[0] for k in p]
    ys = [px(p[k])[1] for k in p]
    x0, x1 = min(xs) - 45, max(xs) + 40
    y0, y1 = min(ys) - 40, max(ys) + 40
    w, h = x1 - x0, y1 - y0
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.0f} {y0:.0f} {w:.0f} {h:.0f}" '
            f'width="{w:.0f}" height="{h:.0f}" role="img">' + "".join(body) + "</svg>"), p


# ---------- 실행 ----------
CASES = [
    ("01", 60, ("A", "P", "B")),    # 본문항: 정삼각형 두 개, ∠APB = 120°
    ("01_1", 60, ("A", "P", "D")),  # 유사1: 같은 그림, ∠APD = 60°
    ("01_2", 50, ("A", "P", "B")),  # 유사2: 꼭지각 50° 이등변, ∠APB = 130°
    ("01_3", 35, ("A", "P", "B")),  # 유사3: 역방향(∠APB=145° → θ=35°)
]

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    print(f"{'id':7} {'θ':>4} {'∠APB':>7} {'예측(180-θ)':>11} {'∠APD':>7} "
          f"{'AE':>7} {'DB':>7} {'검증'}")
    for name, th, mk in CASES:
        svg, p = make_svg(th, mk)
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        A, B, C, D, E, P = p["A"], p["B"], p["C"], p["D"], p["E"], p["P"]
        apb, apd = angle(P, A, B), angle(P, A, D)
        ae, db = dist(A, E), dist(D, B)
        ok = (abs(apb - (180 - th)) < 1e-6            # ∠APB = 180° − θ
              and abs(apd - th) < 1e-6               # ∠APD = θ
              and abs(ae - db) < 1e-9                # 합동 → AE = DB
              and abs(dist(C, A) - dist(C, D)) < 1e-9        # CA = CD
              and abs(dist(C, E) - dist(C, B)) < 1e-9        # CE = CB
              and abs(angle(C, A, E) - angle(C, D, B)) < 1e-6)  # ∠ACE = ∠DCB
        print(f"{name:7} {th:4} {apb:7.2f} {180 - th:11.2f} {apd:7.2f} "
              f"{ae:7.3f} {db:7.3f}  {'OK' if ok else 'FAIL'}")
