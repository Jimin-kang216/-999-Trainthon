import OpenAI from "openai";
import { zodTextFormat } from "openai/helpers/zod";
import type { ZodType } from "zod";

export const DEFAULT_MODEL = "gpt-5.4-mini";

export function hasApiKey(): boolean {
  return Boolean(process.env.OPENAI_API_KEY);
}

let client: OpenAI | null = null;

function getClient(): OpenAI {
  if (!client) client = new OpenAI();
  return client;
}

export class LlmUnavailableError extends Error {
  constructor() {
    super("OPENAI_API_KEY가 설정되지 않았습니다.");
    this.name = "LlmUnavailableError";
  }
}

/**
 * 시스템 프롬프트 + 사용자 입력을 보내고 zod 스키마로 검증된 객체를 돌려준다.
 * 모든 API 라우트가 이 함수 하나만 쓰도록 해서 모델·파라미터 변경 지점을 한 곳으로 모은다.
 */
export async function generateStructured<T>(args: {
  system: string;
  user: string;
  schema: ZodType<T>;
  schemaName: string;
}): Promise<T> {
  if (!hasApiKey()) throw new LlmUnavailableError();

  const response = await getClient().responses.parse({
    model: process.env.OPENAI_MODEL ?? DEFAULT_MODEL,
    instructions: args.system,
    input: args.user,
    text: { format: zodTextFormat(args.schema, args.schemaName) },
  });

  const parsed = response.output_parsed;
  if (!parsed) throw new Error("모델이 구조화된 응답을 반환하지 않았습니다.");
  return parsed as T;
}
