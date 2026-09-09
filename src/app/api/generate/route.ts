import { getSpecialty } from "@/data/specialties";
import { demoGenerate, selfCheckText } from "@/lib/demo";
import { LlmUnavailableError, generateStructured } from "@/lib/llm";
import { prescan } from "@/lib/prescan";
import { generateSystemPrompt, profileBlock } from "@/lib/prompts";
import { channelLabels, generateRequestSchema, generateResultSchema } from "@/lib/schemas";

export async function POST(request: Request) {
  const parsed = generateRequestSchema.safeParse(await request.json().catch(() => null));
  if (!parsed.success) {
    return Response.json({ error: "입력이 올바르지 않습니다.", issues: parsed.error.issues }, { status: 400 });
  }

  const { profile, channel, topic } = parsed.data;
  const specialty = getSpecialty(profile.specialtyId);

  const user = [
    `채널: ${channelLabels[channel]}`,
    topic && `이번 글의 주제/요청: ${topic}`,
    "",
    "한의원 프로필:",
    profileBlock(profile),
  ]
    .filter(Boolean)
    .join("\n");

  try {
    const result = await generateStructured({
      system: generateSystemPrompt(specialty, channel),
      user,
      schema: generateResultSchema,
      schemaName: "clinic_content",
    });

    const selfCheck = prescan(`${result.title}\n${result.body}\n${result.hashtags.join(" ")}`, specialty);
    return Response.json({ result, selfCheck, mode: "llm" });
  } catch (err) {
    if (err instanceof LlmUnavailableError) {
      const result = demoGenerate(profile, channel, topic);
      return Response.json({
        result,
        selfCheck: selfCheckText(result, profile.specialtyId),
        mode: "demo",
      });
    }
    console.error("[api/generate]", err);
    return Response.json({ error: "생성 중 오류가 발생했습니다." }, { status: 500 });
  }
}
