"""Bundle the backup demo into one self-contained HTML file (images inlined as base64).

Why: the repo folder name starts with "-", and the demo page lives on a feature
branch, so a half-finished clone easily ends up with a page whose images 404.
A single file has no relative paths to get wrong.

    python docs/build_standalone.py   ->   docs/AfterMap_demo.html
"""

from __future__ import annotations

import base64
from pathlib import Path

DOCS = Path(__file__).resolve().parent
ASSETS = DOCS / "demo_assets"


def data_uri(name: str) -> str:
    p = ASSETS / name
    mime = "image/png" if p.suffix == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>AfterMap — Eaton 산불 피해 지도 데모</title>
<style>
  :root {{ --navy:#0f2744; --gold:#e6a817; --paper:#f7f4ee; --ink:#1c2430; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:"Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic",sans-serif;
         background:var(--paper); color:var(--ink); }}
  header {{ background:var(--navy); color:#fff; padding:32px 36px; }}
  header h1 {{ margin:0 0 8px; font-size:30px; }}
  header p {{ margin:0; opacity:.85; line-height:1.6; }}
  .metrics {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
             gap:12px; padding:22px 36px; }}
  .m {{ background:#fff; border-radius:12px; padding:16px 18px; box-shadow:0 1px 4px #0001; }}
  .m b {{ display:block; font-size:28px; color:var(--navy); }}
  .m span {{ color:#667; font-size:13px; line-height:1.5; }}
  section {{ padding:10px 36px 30px; }}
  h2 {{ font-size:19px; color:var(--navy); margin:20px 0 10px;
       border-left:4px solid var(--gold); padding-left:10px; }}
  img {{ max-width:100%; border-radius:8px; display:block; }}
  .row {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
  @media (max-width:900px) {{ .row {{ grid-template-columns:1fr; }} }}
  .note {{ font-size:13px; color:#556; line-height:1.6; margin:6px 0 10px; }}
  footer {{ padding:20px 36px 48px; font-size:13px; color:#667; line-height:1.8;
           border-top:1px solid #ddd; }}
  code {{ background:#e9e5dd; padding:2px 6px; border-radius:4px; }}
</style>
</head>
<body>
<header>
  <h1>AfterMap — 재난 전·후 위성영상 자동 정합 &amp; 피해 지도</h1>
  <p>2025년 1월 로스앤젤레스 Eaton 산불 · 알타데나 타일 <code>031311103033</code><br/>
     이 파일 하나만 있으면 됩니다. 인터넷·설치 없이 열립니다.</p>
</header>

<div class="metrics">
  <div class="m"><b>9–16×</b><span>항공사진(2022)→위성(2025) 매칭에서<br/>LightGlue가 SIFT보다 찾은 대응점</span></div>
  <div class="m"><b>0.934</b><span>ROC-AUC<br/>전소 vs 무피해 판별</span></div>
  <div class="m"><b>9,115</b><span>CAL FIRE 현장조사 구조물<br/>(이 타일 안)</span></div>
  <div class="m"><b>1,125 ha</b><span>심각(severe) 등급으로<br/>분류된 격자 면적</span></div>
</div>

<section>
  <h2>1. 산불 전 · 정합된 후 · 피해 점수</h2>
  <img src="{data_uri('pre_post_damage.jpg')}" alt="pre, post, damage overlay"/>
  <p class="note">왼쪽: 산불 전 Maxar(2025-01-01) · 가운데: 자동 정합된 산불 후(2025-01-10) ·
     오른쪽: ΔNDVI + SSIM 피해 점수 오버레이. 밝을수록 변화가 크다.</p>
</section>

<section>
  <h2>2. 왜 AI가 핵심인가 — 2022 항공사진 → 2025 위성 매칭</h2>
  <div class="row">
    <div>
      <p class="note"><b>SIFT (고전 알고리즘)</b> · 대응점 60개 · 8×8 격자 중 30칸이 비었다</p>
      <img src="{data_uri('sift_naip.jpg')}" alt="SIFT matches"/>
    </div>
    <div>
      <p class="note"><b>LightGlue (학습 기반)</b> · 대응점 949개 · 빈 칸 11개</p>
      <img src="{data_uri('lightglue_naip.jpg')}" alt="LightGlue matches"/>
    </div>
  </div>
  <p class="note">초록 선이 두 영상에서 같은 지점으로 연결된 대응점이다. 같은 위성끼리는 SIFT도 충분하지만,
     실제 재난 대응에서 쓰는 “이전 영상”은 몇 년 전 항공사진이라 센서·계절·촬영각이 모두 다르다.
     이 조건에서 AI 매처를 빼면 영상이 어긋난 채로 “변화”가 피해로 잡힌다.</p>
</section>

<section>
  <h2>3. CAL FIRE 현장조사(DINS)로 검증</h2>
  <div class="row">
    <img src="{data_uri('dins_boxplot.png')}" alt="score vs DINS class"/>
    <img src="{data_uri('dins_pr.png')}" alt="precision-recall curve"/>
  </div>
  <p class="note">현장 조사 등급이 올라갈수록 우리 점수도 올라간다. severe 임계값 0.30에서 정밀도 0.781 · 재현율 0.961.
     한계: 건물 단위 분류 모델이 아니라 50 m 격자 점수라서 중간 등급(Affected/Minor/Major)은 서로 겹친다.</p>
</section>

<footer>
  <b>더 볼 것</b><br/>
  라이브 웹앱: 저장소에서 <code>streamlit run app.py</code><br/>
  발표 슬라이드 8장: <code>docs/slides/</code> · 3분 대본: <code>docs/PITCH.md</code> · 예상 질문: <code>docs/QNA.md</code><br/>
  코드: <a href="https://github.com/Jimin-kang216/-999-Trainthon/tree/cursor/aftermap-2b6e">github.com/Jimin-kang216/-999-Trainthon</a> (브랜치 <code>cursor/aftermap-2b6e</code>)
</footer>
</body>
</html>
"""

out = DOCS / "AfterMap_demo.html"
out.write_text(HTML, encoding="utf-8")
print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB, self-contained)")
