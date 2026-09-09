import { getSpecialty } from "@/data/specialties";
import { demoReviewReply } from "@/lib/demo";
import { LlmUnavailableError, generateStructured } from "@/lib/llm";
import { profileBlock, reviewSystemPrompt } from "@/lib/prompts";
import { reviewReplySchema, reviewRequestSchema } from "@/lib/schemas";

export async function POST(request: Request) {
  const parsed = reviewRequestSchema.safeParse(await request.json().catch(() => null));
  if (!parsed.success) {
    return Response.json({ error: "입력이 올바르지 않습니다.", issues: parsed.error.issues }, { status: 400 });
  }

  const { profile, review, rating } = parsed.data;
  const specialty = getSpecialty(profile.specialtyId);

  const user = [
    "한의원 프로필:",
    profileBlock(profile),
    "",
    rating !== undefined && `별점: ${rating}/5`,
    "환자 리뷰 원문:",
    review,
  ]
    .filter((line) => line !== false)
    .join("\n");

  try {
    const result = await generateStructured({
      system: reviewSystemPrompt(specialty),
      user,
      schema: reviewReplySchema,
      schemaName: "review_reply",
    });
    return Response.json({ result, mode: "llm" });
  } catch (err) {
    if (err instanceof LlmUnavailableError) {
      return Response.json({ result: demoReviewReply(profile, review, rating), mode: "demo" });
    }
    console.error("[api/review-reply]", err);
    return Response.json({ error: "답변 생성 중 오류가 발생했습니다." }, { status: 500 });
  }
}
