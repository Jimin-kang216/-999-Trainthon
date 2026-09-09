import { getSpecialty } from "@/data/specialties";
import { LlmUnavailableError, generateStructured } from "@/lib/llm";
import { mergeFindings, prescan } from "@/lib/prescan";
import { checkSystemPrompt } from "@/lib/prompts";
import { checkRequestSchema, checkResultSchema, type CheckResult } from "@/lib/schemas";

export async function POST(request: Request) {
  const parsed = checkRequestSchema.safeParse(await request.json().catch(() => null));
  if (!parsed.success) {
    return Response.json({ error: "입력이 올바르지 않습니다.", issues: parsed.error.issues }, { status: 400 });
  }

  const { specialtyId, channel, text } = parsed.data;
  const specialty = getSpecialty(specialtyId);
  const ruleFindings = prescan(text, specialty);

  try {
    const llm = await generateStructured({
      system: checkSystemPrompt(specialty, channel),
      user: text,
      schema: checkResultSchema,
      schemaName: "medical_ad_check",
    });

    const result: CheckResult = {
      ...llm,
      findings: mergeFindings(llm.findings, ruleFindings),
    };
    return Response.json({ result, mode: "llm" });
  } catch (err) {
    if (err instanceof LlmUnavailableError) {
      return Response.json({ result: fallbackResult(text, ruleFindings), mode: "rules-only" });
    }
    console.error("[api/check]", err);
    return Response.json({ error: "검사 중 오류가 발생했습니다." }, { status: 500 });
  }
}

function fallbackResult(text: string, findings: CheckResult["findings"]): CheckResult {
  const hasHigh = findings.some((f) => f.severity === "high");
  return {
    overallRisk: findings.length === 0 ? "none" : hasHigh ? "high" : "medium",
    summary:
      findings.length === 0
        ? "키워드 기준으로는 위험 표현이 발견되지 않았습니다. OPENAI_API_KEY를 설정하면 문맥까지 검사합니다."
        : `키워드 기준으로 ${findings.length}건의 위험 표현이 있습니다. OPENAI_API_KEY를 설정하면 문맥 검사와 수정본 생성이 가능합니다.`,
    findings,
    needsPreReview: true,
    preReviewReason: "네이버·인스타그램 등 일평균 이용자 10만 명 이상 매체의 광고성 게시물은 사전심의 대상입니다.",
    rewritten: text,
  };
}
