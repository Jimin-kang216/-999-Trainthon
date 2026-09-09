import { z } from "zod";

export const severitySchema = z.enum(["high", "medium", "low"]);

export const clinicProfileSchema = z.object({
  specialtyId: z.string().default("hanbang"),
  name: z.string().min(1, "한의원 이름을 입력하세요"),
  region: z.string().min(1, "지역(예: 성북구 정릉동)을 입력하세요"),
  nearby: z.string().default(""),
  since: z.string().default(""),
  directorName: z.string().default(""),
  services: z.array(z.string()).default([]),
  philosophy: z.string().default(""),
  strengths: z.string().default(""),
});
export type ClinicProfile = z.infer<typeof clinicProfileSchema>;

export const channelSchema = z.enum(["place", "blog", "instagram"]);
export type Channel = z.infer<typeof channelSchema>;

export const channelLabels: Record<Channel, string> = {
  place: "네이버 플레이스 소개글",
  blog: "네이버 블로그 글",
  instagram: "인스타그램 게시물",
};

/** 검사 결과 (LLM 구조화 출력 + 규칙 기반 사전 검사 공용) */
export const findingSchema = z.object({
  ruleId: z.string(),
  quote: z.string().describe("문제가 되는 원문 구절을 그대로 인용"),
  reason: z.string().describe("왜 해당 조항에 걸리는지 한두 문장"),
  severity: severitySchema,
  suggestion: z.string().describe("같은 의도를 유지하면서 안전하게 바꾼 문구"),
});
export type Finding = z.infer<typeof findingSchema>;

export const checkResultSchema = z.object({
  overallRisk: z.enum(["high", "medium", "low", "none"]),
  summary: z.string().describe("전체 판정을 두 문장 이내로"),
  findings: z.array(findingSchema),
  needsPreReview: z
    .boolean()
    .describe("게시 예정 매체 기준으로 의료광고 사전심의 대상인지"),
  preReviewReason: z.string(),
  rewritten: z.string().describe("지적 사항을 모두 반영한 전체 수정본"),
});
export type CheckResult = z.infer<typeof checkResultSchema>;

export const checkRequestSchema = z.object({
  specialtyId: z.string().default("hanbang"),
  channel: channelSchema.default("instagram"),
  text: z.string().min(1).max(6000),
});

/** 콘텐츠 생성 */
export const generateResultSchema = z.object({
  title: z.string().describe("제목 또는 첫 줄. 플레이스 소개글은 빈 문자열"),
  body: z.string(),
  hashtags: z.array(z.string()).describe("인스타그램이 아니면 빈 배열"),
  complianceNotes: z
    .array(z.string())
    .describe("이 글에서 의도적으로 피한 표현과 그 이유"),
});
export type GenerateResult = z.infer<typeof generateResultSchema>;

export const generateRequestSchema = z.object({
  profile: clinicProfileSchema,
  channel: channelSchema,
  topic: z.string().max(300).default(""),
});

/** 리뷰 답변 */
export const reviewReplySchema = z.object({
  reply: z.string(),
  cautions: z
    .array(z.string())
    .describe("답변 작성 시 피한 것: 진료 내용 언급, 개인정보, 재방문 유도 대가 등"),
});
export type ReviewReply = z.infer<typeof reviewReplySchema>;

export const reviewRequestSchema = z.object({
  profile: clinicProfileSchema,
  review: z.string().min(1).max(3000),
  rating: z.number().int().min(1).max(5).optional(),
});
