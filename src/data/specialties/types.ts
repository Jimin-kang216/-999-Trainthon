export type Severity = "high" | "medium" | "low";

export interface Rule {
  /** 조문 기반 식별자. 예: "56-2-8" */
  id: string;
  /** 사람이 읽는 조문 표기 */
  article: string;
  title: string;
  summary: string;
  severity: Severity;
  /** 위반 가능성이 높은 문구 예시 (LLM 프롬프트와 UI에 노출) */
  examples: string[];
  /** 규칙 기반 사전 검사에 쓰는 키워드. 비어 있으면 LLM 판단에만 의존 */
  keywords: string[];
  /** 안전한 대체 방향 */
  safeDirection: string;
}

export interface Specialty {
  id: string;
  name: string;
  /** 의료광고 사전심의 기관 */
  reviewBody: string;
  reviewBodyUrl: string;
  /** 온보딩과 콘텐츠 생성에서 선택지로 쓰는 대표 진료 항목 */
  commonServices: string[];
  rules: Rule[];
}
