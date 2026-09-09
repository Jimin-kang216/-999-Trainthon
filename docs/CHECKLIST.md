# 당신이 할 일 (코드는 이미 있음)

역할 분담이 분명하다. **파이프라인·숫자·앱은 저장소에 있다.** 심사에서 점수가 갈리는 나머지 절반은 사람만 할 수 있다.

제한 시간이 10시간이면, 아래 순서대로만 하면 된다. 1 → 4가 필수, 5 이후는 시간이 남을 때.

## 필수 (발표 전까지)

1. **데모를 자기 노트북에서 한 번 띄운다.** (20분)

   가장 확실한 방법은 단일 파일이다. GitHub에서 `docs/AfterMap_demo.html` → **Download raw file** → 더블클릭.

   라이브 앱까지 보고 싶으면:
   ```bash
   git clone -b cursor/aftermap-2b6e https://github.com/Jimin-kang216/-999-Trainthon.git
   cd ./-999-Trainthon
   pip install -r requirements.txt
   streamlit run app.py
   ```
   `-b` 를 빼면 README만 있는 `main`이 받아진다. `cd` 앞의 `./` 도 빼면 안 된다(폴더명이 `-`로 시작).

   앱이 “No processed tiles”이면:
   ```bash
   python -m src.ingest all --n 4
   python -m src.register
   python -m src.damage
   python -m src.validate
   ```
   네트워크가 불안하면 `docs/AfterMap_demo.html`을 브라우저로 연다 (오프라인 백업, 단일 파일).

2. **3분 대본을 소리 내서 두 번 읽는다.** (`docs/PITCH.md`)
   슬라이드 PNG는 `docs/slides/01_title.png` … `08_ask.png`. 구글 슬라이드에 이미지로 넣으면 끝.

3. **첫 15초에 자신을 한 줄로 넣는다.** 대본에 `[여기]`로 비워 둔 자리.
   예: “연세대 건설환경공학, GRS Lab에서 matching·원격탐사 쪽으로 가고 싶어서 이 문제를 골랐다.”

4. **Q&A 다섯 개만 외운다.** (`docs/QNA.md`)
   “SIFT로도 되지 않나?” / “누가 돈 내나?” / “UNOSAT이랑 뭐가 다르나?” / “건물 단위인가?” / “한국에 어떻게 가져가나?”

## 심사 기준에 맞추는 말 (발표 중에 한 번씩)

| 기준 | 당신이 할 말 |
|---|---|
| 제품 완성도 | 라이브로 탭 3개를 클릭한다. 지도 → 매칭 비교 → AUC. |
| AI Tool 활용도 | “핵심은 챗봇이 아니라 DISK+LightGlue 정합. NAIP→Maxar에서 인라이어 9–16배. AI를 빼면 이종 소스가 안 맞는다.” 개발에 Cursor를 쓴 것은 `docs/AI_USAGE.md` 한 장. |
| 사업화·확장 | 보험 트리아지·지자체. 지금은 매출 없음. 한국 산불 항공영상이 다음 데이터. |
| 문제 정의 | 12,300 구조물, 현장조사 수 주, 이전 영상은 항공 기본도. |
| 발표 | 숫자 세 개만 반복: **9–16배**, **AUC 0.934**, **구조물 9,115**. |

## 하지 말 것

- 파이프라인 코드를 발표 전에 고치기
- 새 아이디어로 피벗하기
- World Bank 이야기를 1분 이상 하기 (심사위원 맥락이 다름)
- “대박 날 것 같다”고 말하기

## 시간이 남으면

- 구글 슬라이드에 PNG 8장을 넣고 자기 이름·팀명만 올린다.
- `docs/AI_USAGE.md`를 슬라이드 뒤에 한 장 붙인다.
- 데모 실패 리허설: HTML 백업을 북마크한다.
