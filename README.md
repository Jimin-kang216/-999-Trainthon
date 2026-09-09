# 동네 한의원 마케팅 AI

연세대학교 AI 창업캠프 999: Trainthon 출품작.
의료광고 규정을 알고 있는 AI가 1인 원장 동네 한의원의 홍보 글을 쓰고 검수한다.

## 문제

- 동네 의원 환자의 대부분은 "근처 한의원" 검색에서 온다. 실력이 아니라 네이버 플레이스 노출이 환자 수를 결정한다.
- 의료광고는 일반 마케팅과 다르다. 치료 후기 인용, "최고·전문·완치" 같은 표현, 할인·증정, 리뷰 이벤트가 의료법 제56조·제27조 위반이다. 일반 SNS 마케팅 툴이나 ChatGPT는 이 규정을 모른 채 위법 문구를 만들어 낸다.
- 병원 마케팅 대행사는 월 100만 원 이상이라 1인 한의원은 쓰지 못한다. 결과적으로 원장들은 무엇을 해도 되는지 몰라서 홍보를 시작하지 않는다.
- 첫 사용자: 2007년부터 같은 자리에서 진료 중인 한의원. 위치가 불리하고 홍보를 하지 않아 환자가 적다.

## 제품

세 화면, 하나의 규칙 데이터.

| 화면 | 하는 일 | 규정 적용 방식 |
| --- | --- | --- |
| 광고 문구 검사 `/check` | 붙인 글을 조항별로 검사하고 위험 구절·이유·대체 문구·사전심의 대상 여부·전체 수정본을 반환 | 규칙 기반 키워드 사전 검사 + LLM 문맥 검사 병합 |
| 콘텐츠 생성 `/generate` | 프로필 사실만으로 플레이스 소개글 / 블로그 글 / 인스타 게시물 작성 | 조항을 시스템 프롬프트에 내장, 생성 후 규칙 기반 자체 검사 |
| 리뷰 답변 `/review` | 플레이스 리뷰 답글 작성 | 진료 내용 재언급·개인정보·유인 표현 금지 원칙 내장 |
| 한의원 프로필 `/profile` | 세 화면이 공유하는 사실 정보 입력 (브라우저 저장) | 프로필에 없는 사실은 생성하지 않도록 프롬프트에서 제한 |

규칙 데이터는 `src/data/specialties/hanbang.ts` 하나다. 의료법 제56조 제2항 각 호와 제27조 제3항(환자 유인)을 조항·요지·위반 예시·키워드·안전한 방향으로 정리했다.
치과·정형외과 등 다른 진료과는 같은 형식의 데이터 파일을 `src/data/specialties/index.ts`에 추가하면 화면·API 수정 없이 동작한다.

## 실행

```bash
npm install
cp .env.example .env.local   # OPENAI_API_KEY 입력
npm run dev
```

`OPENAI_API_KEY`가 없어도 실행된다. 이 경우 검사기는 키워드 기반으로만 동작하고 생성·리뷰 답변은 503을 반환한다.

```bash
npm run build && npm run start   # 프로덕션
npm run lint
```

## 구조

```
src/
  app/
    page.tsx                 랜딩 (문제 정의 + 적용 조항 목록)
    check/page.tsx           광고 문구 검사
    generate/page.tsx        콘텐츠 생성
    review/page.tsx          리뷰 답변
    profile/page.tsx         한의원 프로필
    api/check/route.ts       POST { specialtyId, channel, text } -> { result, mode }
    api/generate/route.ts    POST { profile, channel, topic } -> { result, selfCheck }
    api/review-reply/route.ts POST { profile, review, rating } -> { result }
  data/specialties/          진료과별 규칙 데이터 (현재 한의원)
  lib/
    schemas.ts               zod 스키마 (요청/응답/LLM 구조화 출력)
    prompts.ts               시스템 프롬프트 (규칙 데이터를 주입)
    prescan.ts               규칙 기반 키워드 검사, LLM 결과 병합
    llm.ts                   OpenAI Responses API + zod 구조화 출력 래퍼
    use-clinic-profile.ts    프로필 localStorage 훅
  components/                UI
```

스택: Next.js 16 (App Router) · TypeScript · Tailwind CSS 4 · OpenAI SDK (Responses API, `zodTextFormat` 구조화 출력) · zod 4.

## 심사 기준 대응

- **제품 완성도**: 외부 연동(인스타·네이버 API) 없이 텍스트 입출력만으로 완결. 키가 없어도 검사기가 동작하는 폴백.
- **AI Tool 활용도**: 검사·생성·답변 모두 LLM이 핵심. 규칙 데이터를 프롬프트에 주입하는 방식이라 "규제를 아는 AI"가 제품 자체. 개발 과정의 AI 활용은 아래 기록.
- **사업화·확장 가능성**: 한의원 약 1.4만 곳에서 시작, 동네 의원·치과 포함 7만 곳 이상으로 확장. 규칙 파일 추가만으로 진료과 확장. 월 구독(5~15만 원)으로 대행사 대비 저가.
- **문제 정의 및 사용자 가치**: 실제 사용자(원장)가 있고 캠프 기간 중 실사용 검증 가능.

## 개발 과정의 AI 도구 활용 기록

| 단계 | 도구 | 내용 |
| --- | --- | --- |
| 아이디어 검증 | Cursor (Claude) | 교환학생 준비 도구, 인플루언서 협찬 관리 등 후보를 심사 기준에 대입해 비교. 시장 규모·경쟁·규제 리스크를 냉정하게 평가받고 한의원 마케팅으로 확정 |
| 규제 조사 | Cursor (Claude) | 의료법 제56조 제2항·제27조 제3항을 조항별 데이터로 구조화, 한의원 맥락의 위반 예시·키워드·대체 방향 작성 |
| 뼈대 구현 | Cursor (Claude) | Next.js 프로젝트 생성, 스키마·프롬프트·API·화면 초안 작성 |
| 제품 내 AI | OpenAI Responses API | 구조화 출력으로 검사 결과·생성 콘텐츠·리뷰 답변 생성 |

## 한계와 주의

- 이 도구는 의료광고 사전심의를 대체하지 않는다. 광고 성격의 게시물은 게시 전 대한한의사협회 의료광고심의위원회 심의를 받아야 한다.
- 규칙 데이터의 조문 요지와 예시는 참고용이며, 최신 개정 사항은 법제처 국가법령정보센터 원문으로 확인해야 한다.
- 검사기는 놓치는 것보다 과하게 잡는 쪽으로 설계되어 있다.
