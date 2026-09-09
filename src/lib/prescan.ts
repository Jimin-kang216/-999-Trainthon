import type { Specialty } from "@/data/specialties";
import type { Finding } from "./schemas";

/**
 * 규칙 데이터의 키워드만으로 하는 결정적 사전 검사.
 * LLM 호출 전에 즉시 결과를 보여주고, API 키가 없어도 검사기가 동작하도록 한다.
 * LLM 결과와 병합할 때 같은 인용 구절은 LLM 판단을 우선한다.
 */
export function prescan(text: string, specialty: Specialty): Finding[] {
  const findings: Finding[] = [];
  const lower = text.toLowerCase();

  for (const rule of specialty.rules) {
    for (const keyword of rule.keywords) {
      const idx = lower.indexOf(keyword.toLowerCase());
      if (idx === -1) continue;

      findings.push({
        ruleId: rule.id,
        quote: extractSentence(text, idx, keyword.length),
        reason: `'${keyword}' 표현은 ${rule.title}(${rule.article})에 해당할 가능성이 있습니다.`,
        severity: rule.severity,
        suggestion: rule.safeDirection,
      });
      break;
    }
  }

  return findings;
}

function extractSentence(text: string, idx: number, len: number): string {
  const boundaries = /[.!?\n。]/;
  let start = idx;
  while (start > 0 && !boundaries.test(text[start - 1])) start--;
  let end = idx + len;
  while (end < text.length && !boundaries.test(text[end])) end++;
  return text.slice(start, end).trim();
}

export function mergeFindings(llm: Finding[], rule: Finding[]): Finding[] {
  const seen = new Set(llm.map((f) => `${f.ruleId}::${normalize(f.quote)}`));
  const extra = rule.filter((f) => {
    const key = `${f.ruleId}::${normalize(f.quote)}`;
    if (seen.has(key)) return false;
    // LLM이 같은 조항을 이미 지적했으면 규칙 기반 중복은 버린다.
    return !llm.some((l) => l.ruleId === f.ruleId);
  });
  return [...llm, ...extra];
}

function normalize(s: string) {
  return s.replace(/\s+/g, " ").trim().toLowerCase();
}
