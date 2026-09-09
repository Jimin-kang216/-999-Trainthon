"use client";

import { useEffect, useState } from "react";
import { InfoNote } from "./ui";

export function DemoModeBanner({ mode }: { mode: "llm" | "rules-only" | "demo" | null }) {
  if (mode === "llm") return null;
  if (mode === "rules-only") {
    return (
      <InfoNote>
        OPENAI_API_KEY가 없어 키워드 검사와 위험 문장 제거 수정본만 만들었습니다. `.env.local`에 키를 넣으면 문맥 검사와
        대체 문장 생성이 켜집니다.
      </InfoNote>
    );
  }
  if (mode === "demo") {
    return (
      <InfoNote>
        지금은 데모 모드입니다. 프로필에 적은 사실로 규정에 맞는 글을 템플릿에서 채웠습니다. `.env.local`에
        OPENAI_API_KEY를 넣으면 같은 화면에서 AI가 새로 씁니다.
      </InfoNote>
    );
  }
  return null;
}

export function LlmStatusChip() {
  const [llm, setLlm] = useState<boolean | null>(null);

  useEffect(() => {
    fetch("/api/status")
      .then((r) => r.json())
      .then((d: { llm: boolean }) => setLlm(d.llm))
      .catch(() => setLlm(false));
  }, []);

  if (llm === null) return null;
  return (
    <span
      className={`hidden sm:inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${
        llm ? "bg-ok-soft text-ok" : "bg-risk-medium-soft text-risk-medium"
      }`}
    >
      {llm ? "AI 연결됨" : "데모 모드"}
    </span>
  );
}
