"""Render TrainThon pitch slides as 1920x1080 PNGs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib import font_manager as fm

plt.rcParams["font.family"] = ["WenQuanYi Micro Hei", "Droid Sans Fallback", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
RESULTS = ROOT / "results"
W, H = 19.2, 10.8
NAVY = "#0f2744"
TEAL = "#1a7a6d"
GOLD = "#e6a817"
WHITE = "#f7f4ee"
MUTED = "#8aa0b5"


def canvas(bg=NAVY):
    fig = plt.figure(figsize=(W, H), facecolor=bg)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor(bg)
    return fig, ax


def save(fig, name: str):
    p = OUT / name
    fig.savefig(p, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("wrote", p)


def card(ax, x, y, w, h, fc="#173353", ec=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor=fc, edgecolor=ec or fc, linewidth=1.2, mutation_aspect=0.6))


# --------------------------------------------------------------------------- #
fig, ax = canvas()
ax.text(0.07, 0.78, "TRAINTHON  ·  2026.09", color=GOLD, fontsize=18, fontweight="bold")
ax.text(0.07, 0.58, "AfterMap", color=WHITE, fontsize=72, fontweight="bold")
ax.text(0.07, 0.42, "재난 전·후 위성영상을 자동으로 맞추고\n건물·식생 피해를 48시간 안에 지도로 만든다.",
        color="#d5deea", fontsize=26)
ax.text(0.07, 0.18, "학습 기반 영상 매칭  ·  ΔNDVI + SSIM  ·  CAL FIRE 현장조사로 검증",
        color=MUTED, fontsize=16)
ax.text(0.07, 0.08, "연세대학교 건설환경공학  ·  GRS Lab 관심  ·  matching / remote sensing / GIS",
        color=MUTED, fontsize=14)
save(fig, "01_title.png")

# --------------------------------------------------------------------------- #
fig, ax = canvas()
ax.text(0.07, 0.88, "01  문제", color=GOLD, fontsize=18, fontweight="bold")
ax.text(0.07, 0.76, "영상은 있다. 겹치면 어긋나고, 사람이 본다.", color=WHITE, fontsize=32, fontweight="bold")
for i, (t, s) in enumerate([
    ("12,300+", "구조물이 2025 LA 산불에서\n소실·피해 (Maxar Open Data)"),
    ("수 주", "CAL FIRE DINS 현장 조사가\n피해 등급을 확정하는 시간"),
    ("이종 소스", "실제 ‘이전 영상’은 위성 짝이 아니라\n몇 년 전 항공사진 기본도"),
]):
    card(ax, 0.07 + i * 0.30, 0.22, 0.27, 0.42)
    ax.text(0.09 + i * 0.30, 0.50, t, color=GOLD, fontsize=28, fontweight="bold")
    ax.text(0.09 + i * 0.30, 0.32, s, color="#d5deea", fontsize=16)
ax.text(0.07, 0.10, "심사 기준의 ‘문제 정의’: 대상은 지자체·보험 손해사정·인도적 지원. 필요성은 현장 방문이 병목이라는 점.",
        color=MUTED, fontsize=14)
save(fig, "02_problem.png")

# --------------------------------------------------------------------------- #
fig, ax = canvas()
ax.text(0.07, 0.88, "02  왜 AI가 핵심인가", color=GOLD, fontsize=18, fontweight="bold")
ax.text(0.07, 0.74, "같은 위성 전·후는 SIFT로도 된다.\n항공사진 → 위성이면 SIFT가 무너진다.", color=WHITE, fontsize=26, fontweight="bold")
rows = [
    ("Maxar → Maxar", "SIFT 1,100–4,400   LightGlue 1,700–2,800", "둘 다 성공"),
    ("NAIP 2022 → Maxar 2025", "SIFT 49–124   LightGlue 808–1,110", "9–16배"),
    ("알타데나 빈 셀 /64", "SIFT 30   LightGlue 11", "소실 지역에서 갈림"),
]
for i, (a, b, c) in enumerate(rows):
    card(ax, 0.07, 0.48 - i * 0.15, 0.86, 0.13)
    ax.text(0.10, 0.54 - i * 0.15, a, color=GOLD, fontsize=18, fontweight="bold")
    ax.text(0.38, 0.54 - i * 0.15, b, color=WHITE, fontsize=18)
    ax.text(0.78, 0.54 - i * 0.15, c, color="#d5deea", fontsize=16)
save(fig, "03_ai_core.png")

# --------------------------------------------------------------------------- #
fig, ax = canvas()
ax.text(0.07, 0.88, "03  파이프라인", color=GOLD, fontsize=18, fontweight="bold")
steps = [
    ("1. 수집", "Maxar STAC\nquadkey 전·후 쌍"),
    ("2. 정합", "DISK + LightGlue\nMAGSAC 호모그래피"),
    ("3. 점수", "ΔNDVI + SSIM\n50 m 격자"),
    ("4. 검증", "CAL FIRE DINS\n구조물 단위"),
]
for i, (t, s) in enumerate(steps):
    card(ax, 0.06 + i * 0.235, 0.28, 0.21, 0.42)
    ax.text(0.08 + i * 0.235, 0.58, t, color=GOLD, fontsize=20, fontweight="bold")
    ax.text(0.08 + i * 0.235, 0.40, s, color="#d5deea", fontsize=16)
    if i < 3:
        ax.annotate("", xy=(0.055 + (i + 1) * 0.235, 0.49), xytext=(0.27 + i * 0.235, 0.49),
                    arrowprops=dict(arrowstyle="->", color=GOLD, lw=2))
ax.text(0.07, 0.12, "AI를 빼면 2단계가 이종 소스에서 실패한다. 지도는 그려지지만 어긋난 채로 변화가 ‘피해’로 잡힌다.",
        color=MUTED, fontsize=16)
save(fig, "04_pipeline.png")

# --------------------------------------------------------------------------- #
fig, ax = canvas()
ax.text(0.07, 0.88, "04  검증 — CAL FIRE DINS", color=GOLD, fontsize=18, fontweight="bold")
ax.text(0.07, 0.76, "Eaton 알타데나 타일, 현장 조사 9,115개 구조물", color=WHITE, fontsize=24)
metrics = [("0.934", "ROC-AUC\nDestroyed vs No Damage"),
           ("0.922", "Average Precision"),
           ("0.78 / 0.96", "severe 정밀도 / 재현율")]
for i, (n, lab) in enumerate(metrics):
    card(ax, 0.07 + i * 0.30, 0.28, 0.27, 0.38)
    ax.text(0.09 + i * 0.30, 0.50, n, color=GOLD, fontsize=36, fontweight="bold")
    ax.text(0.09 + i * 0.30, 0.36, lab, color="#d5deea", fontsize=16)
ax.text(0.07, 0.12, "점수는 학습된 피해 분류기가 아니다. ΔNDVI+SSIM 가중 합. 산지 식생 소실에 강하고, 콘크리트 지붕은 SSIM에 의존한다.",
        color=MUTED, fontsize=14)
save(fig, "05_validation.png")

# --------------------------------------------------------------------------- #
fig, ax = canvas()
ax.text(0.07, 0.88, "05  제품", color=GOLD, fontsize=18, fontweight="bold")
ax.text(0.07, 0.74, "Streamlit 데모  ·  GeoJSON 다운로드  ·  3개 탭", color=WHITE, fontsize=26, fontweight="bold")
for i, (t, s) in enumerate([
    ("Damage map", "히트맵 + 50 m 격자\n보험·지자체가 바로 쓰는 파일"),
    ("Registration", "SIFT vs LightGlue\n인라이어·RMSE·매칭선"),
    ("Validation", "DINS 박스플롯\nPR 곡선, AUC"),
]):
    card(ax, 0.07 + i * 0.30, 0.22, 0.27, 0.42)
    ax.text(0.09 + i * 0.30, 0.50, t, color=GOLD, fontsize=22, fontweight="bold")
    ax.text(0.09 + i * 0.30, 0.34, s, color="#d5deea", fontsize=16)
ax.text(0.07, 0.08, "실행:  streamlit run app.py    백업:  docs/demo_eaton.html", color=MUTED, fontsize=16)
save(fig, "06_product.png")

# --------------------------------------------------------------------------- #
fig, ax = canvas()
ax.text(0.07, 0.88, "06  사업화 · 확장", color=GOLD, fontsize=18, fontweight="bold")
items = [
    ("지금", "공개 데이터 MVP. 고객은 아직 없다. 지불 가설: 보험 손해사정 트리아지(건당), 지자체 재난 부서(연간)."),
    ("한국", "산불 항공영상(산림청), 집중호우 전·후, 국토위성. 방법론은 그대로 옮긴다."),
    ("다음 연구", "SAR–광학 매칭, 위성–드론 스케일, 텍스처 소실 지역 강건성. GRS Lab 예비실험이 이 저장소다."),
]
for i, (h, b) in enumerate(items):
    card(ax, 0.07, 0.62 - i * 0.22, 0.86, 0.18)
    ax.text(0.10, 0.72 - i * 0.22, h, color=GOLD, fontsize=18, fontweight="bold")
    ax.text(0.22, 0.70 - i * 0.22, b, color="#d5deea", fontsize=16)
save(fig, "07_business.png")

# --------------------------------------------------------------------------- #
fig, ax = canvas()
ax.text(0.07, 0.72, "Ask", color=GOLD, fontsize=20, fontweight="bold")
ax.text(0.07, 0.52, "이종 소스 정합이 필요한\n재난 한 건을 같이 돌려보자.", color=WHITE, fontsize=36, fontweight="bold")
ax.text(0.07, 0.22, "데모  ·  GeoJSON  ·  DINS 대비 표  ·  코드 github.com/Jimin-kang216/-999-Trainthon",
        color=MUTED, fontsize=16)
ax.text(0.07, 0.10, "AfterMap  ·  matching / remote sensing / GIS", color=MUTED, fontsize=14)
save(fig, "08_ask.png")
