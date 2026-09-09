import { getRule, type Specialty } from "@/data/specialties";
import type { Finding } from "@/lib/schemas";
import { SeverityBadge } from "./ui";

export function FindingCard({ finding, specialty }: { finding: Finding; specialty: Specialty }) {
  const rule = getRule(specialty, finding.ruleId);

  return (
    <li className="rounded-lg border border-line bg-white p-4">
      <div className="flex flex-wrap items-center gap-2">
        <SeverityBadge severity={finding.severity} prefix="위험도" />
        <span className="text-sm font-semibold">{rule?.title ?? finding.ruleId}</span>
        {rule && <span className="text-xs text-ink-soft">{rule.article}</span>}
      </div>

      <blockquote className="mt-3 border-l-2 border-risk-high/50 pl-3 text-sm text-ink whitespace-pre-wrap">
        {finding.quote}
      </blockquote>

      <p className="mt-3 text-sm text-ink-soft leading-relaxed">{finding.reason}</p>

      <div className="mt-3 rounded-md bg-ok-soft/60 px-3 py-2 text-sm">
        <span className="font-semibold text-ok">이렇게 바꾸세요</span>
        <p className="mt-1 leading-relaxed whitespace-pre-wrap">{finding.suggestion}</p>
      </div>
    </li>
  );
}
