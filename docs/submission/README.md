# 제출용 문구 · 이미지

연세대 AI 창업캠프 999: Trainthon 제출 초안.
사이트는 본인 노트북에서 `npm run dev` 후 `http://localhost:3000` 으로 연다.

---

## 1. 본인 컴퓨터에서 사이트 열기

터미널에 한 줄씩 입력한다. 프롬프트가 `-999-Trainthon %` 로 끝나면 폴더 안에 있는 것이다.

```bash
cd ~/-999-Trainthon
git pull
npm install
npm run dev
```

마지막 줄 다음에 `Local: http://localhost:3000` 이 나오면, **Safari 또는 Chrome 주소창**에 아래를 붙여 넣는다.

```
http://localhost:3000
```

Cursor 안이 아니라 **브라우저**에서 열린다.

처음 쓸 때 순서:

1. 한의원 프로필 → 예시 프로필 불러오기 → 저장
2. 광고 문구 검사 → 위반 예시 불러오기 → 검사하기
3. 콘텐츠 생성 → 글 생성하기
4. 리뷰 답변 → 예시 리뷰 → 답글 생성하기
5. 이번 주 계획

끌 때는 터미널에서 `Ctrl + C`.

---

## 2. Submission images (최대 10장)

핵심 경험만 올린다. 추천 8장. 파일명은 GitHub `docs/submission/` 과 같다.

| # | 파일 | 찍는 화면 | 캡션 (영문 폼이면 이 문장) | 왜 넣나 |
| --- | --- | --- | --- | --- |
| 1 | `01-home.png` | `/` 히어로 + 3단계 | Problem: skilled neighborhood clinics stay invisible because medical-ad law blocks DIY marketing | 문제 한 장 |
| 2 | `02-profile.png` | `/profile` 예시 저장 후 | Clinic facts only: name, area, years, services, director’s own words | 입력이 단순하다는 것 |
| 3 | `03-check-findings.png` | `/check` 검사 결과 (조항 카드) | AI flags illegal phrases by statute (Medical Act Art. 56 / 27) | **핵심 데모** |
| 4 | `04-check-rewrite.png` | 같은 화면의 안전한 수정본 | Safe rewrite without superlatives, reviews, discounts, or inducements | 고쳐서 쓸 수 있음 |
| 5 | `05-generate.png` | `/generate` 플레이스 소개글 | Compliant Naver Place copy from clinic facts | 생성 기능 |
| 6 | `06-review.png` | `/review` 답글 | Place-review reply that never repeats clinical details or offers rewards | 일상 운영 |
| 7 | `07-plan.png` | `/plan` 키워드+7일 | Local keywords and a 7-day content plan | 다음 액션 |
| 8 | `08-rules.png` | `/` 하단 조항 목록 | 15 built-in clauses for Korean medicine clinics; other specialties = data files | 확장·신뢰 |

9~10장은 비워도 된다. 넣으면:

- 랜딩의 발표 대본 카드 (`09-pitch.png`) — 심사 스토리
- 생성 결과 오른쪽 “의도적으로 피한 것” (`10-compliance-notes.png`) — AI가 규정을 안다는 증거

찍을 때:

- 브라우저를 넓게 (1200px 이상). 개발자 도구(F12)는 끈다.
- 주소창의 `localhost` 가 보여도 제출엔 상관 없다. 가능하면 주소창을 가리거나 전체 페이지 스크롤 캡처보다 **핵심 UI만** 담는다.
- 한 장에 글자가 읽혀야 한다. 흐릿한 전체 스크롤샷은 빼다.

---

## 3. Submission description

아래 중 **중간(권장)** 을 그대로 붙여 넣고, 글자 수 제한이 있으면 짧은 버전을 쓴다.

### 짧은 버전 (약 450자)

실력 있는 동네 한의원이 검색에 안 보이는 이유는 실력이 아니라 의료광고법입니다. 후기·최고·할인·리뷰 이벤트가 위법이라 원장은 홍보를 시작하지 못하고, 대행사는 월 100만 원이 넘습니다.

「한카피」는 의료법 제56조·제27조를 아는 AI입니다. 위험한 문구를 붙이면 조항별로 짚고 고치고, 원장 말투의 프로필로 플레이스·블로그·인스타 글과 리뷰 답글을 규정에 맞게 씁니다. 첫 사용자는 2007년부터 한자리에서 진료 중인 한의원입니다. 한의원에서 시작해 1인 원장 동네 의원으로 확장합니다. 이 도구는 사전심의를 대체하지 않는 보조 도구입니다.

### 중간 버전 (권장, 약 1,100자)

**문제.** 동네 의원 환자는 대부분 “근처 한의원” 검색에서 옵니다. 그런데 의료광고는 일반 마케팅과 다릅니다. 치료 후기 인용, “최고·전문·완치”, 할인·증정, 리뷰 이벤트는 의료법 제56조·제27조 위반입니다. ChatGPT와 SNS 툴은 이 규정을 모르고 위법 문구를 만들고, 병원 대행사는 1인 원장이 쓸 수 없는 가격입니다. 결과적으로 실력 있는 동네 한의원은 홍보를 포기합니다. 첫 사용자는 2007년부터 같은 자리에서 진료해 온 한의원입니다.

**제품.** 네 가지를 한 흐름으로 붙였습니다. (1) 광고 문구 검사 — 조항별 위험 구절, 이유, 대체 문구, 사전심의 대상 여부, 수정본. (2) 콘텐츠 생성 — 프로필에 있는 사실만으로 네이버 플레이스·블로그·인스타 글을 처음부터 규정에 맞게 작성. (3) 리뷰 답변 — 진료 내용 재언급·개인정보·재방문 유인 없이 플레이스 답글. (4) 이번 주 계획 — 지역 검색 키워드와 7일 콘텐츠 일정.

**AI.** 규칙 데이터(한의원 기준 15개 조항)를 프롬프트에 넣고 구조화 출력으로 검사·생성합니다. 키가 없으면 같은 화면이 데모 모드로 동작합니다. AI 도구(Cursor)로 아이디어 검증, 조문 구조화, 구현까지 진행했습니다.

**확장.** 화면은 진료과 무관입니다. 치과·정형외과는 규칙 파일만 추가합니다. 수익은 월 구독(대행사 대비 저가)입니다. 사전심의를 대체하지 않으며, 위법 초안을 안 쓰게 하는 보조 도구입니다.

### 영문 버전이 필요할 때

Neighborhood clinics lose patients to search, not to skill. Korean medical-ad law bans testimonials, superlatives, discounts, and review rewards, so solo directors never start marketing and agencies cost too much.

This product is a compliance-aware marketing assistant for Korean medicine clinics. Paste copy to get article-level flags and a safe rewrite. Enter clinic facts to generate Naver Place, blog, and Instagram posts plus Place review replies. A weekly plan lists local keywords and seven posts. The first user is a clinic that has practiced in the same place since 2007. Other specialties are additional rule files. It does not replace association pre-review.

---

## 제출 폼에 같이 넣을 한 줄들

- **제품명:** 한카피
- **한 줄:** 올려도 되는 한의원 글만. 의료광고법을 아는 AI가 검사하고 작성합니다.
- **타깃:** 1인 원장 한의원 (확장: 동네 의원·치과)
- **핵심 AI:** 의료법 제56조·제27조 조항 데이터 + LLM 구조화 검사/생성
- **데모 하이라이트:** 위법 예시 한 장을 검사 → 조항 카드 + 수정본
- **주의 문구:** 대한한의사협회 의료광고 사전심의를 대체하지 않습니다.
