import { DEFAULT_MODEL, hasApiKey } from "@/lib/llm";

export async function GET() {
  return Response.json({
    llm: hasApiKey(),
    model: process.env.OPENAI_MODEL ?? DEFAULT_MODEL,
  });
}
