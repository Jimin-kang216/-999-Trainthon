"use client";

import { useState } from "react";
import { getSpecialty } from "@/data/specialties";
import { DemoModeBanner } from "@/components/demo-banner";
import { FindingCard } from "@/components/finding-card";
import { ProfileSummary } from "@/components/profile-summary";
import { Button, Card, CopyButton, ErrorNote, Input, Label, PageHeader, Spinner } from "@/components/ui";
import { channelLabels, type Channel, type Finding, type GenerateResult } from "@/lib/schemas";
import { useClinicProfile } from "@/lib/use-clinic-profile";

const topicHints: Record<Channel, string> = {
  place: "비워 두면 프로필 전체를 바탕으로 소개글을 씁니다.",
  blog: "예: 환절기 어르신 허리 통증, 교통사고 후 한의원 진료 절차",
  instagram: "예: 추석 연휴 진료 안내, 초진 상담은 이렇게 진행됩니다",
};

export default function GeneratePage() {
  const { profile, isComplete, loaded } = useClinicProfile();
  const [channel, setChannel] = useState<Channel>("place");
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [selfCheck, setSelfCheck] = useState<Finding[]>([]);
  const [mode, setMode] = useState<"llm" | "demo" | null>(null);

  const specialty = getSpecialty(profile.specialtyId);

  async function run() {
    setLoading(true);
    setError(null);
    setResult(null);
    setSelfCheck([]);
    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile, channel, topic }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "생성에 실패했습니다.");
      setResult(data.result);
      setSelfCheck(data.selfCheck ?? []);
      setMode(data.mode === "llm" ? "llm" : "demo");
    } catch (e) {
      setError(e instanceof Error ? e.message : "생성에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }

  const fullText = result
    ? [result.title, result.body, result.hashtags.map((h) => (h.startsWith("#") ? h : `#${h}`)).join(" ")]
        .filter(Boolean)
        .join("\n\n")
    : "";

  return (
    <div>
      <PageHeader
        eyebrow="Compliant content"
        title="콘텐츠 생성"
        description="프로필에 적힌 사실만 사용해서, 의료광고 조항을 처음부터 지킨 글을 씁니다. 생성 후 규칙 기반 자체 검사를 한 번 더 거칩니다."
      />

      <div className="space-y-4">
        {loaded && <ProfileSummary profile={profile} isComplete={isComplete} />}

        <Card>
          <div className="space-y-4">
            <div>
              <Label>채널</Label>
              <div className="grid gap-2 sm:grid-cols-3">
                {(Object.keys(channelLabels) as Channel[]).map((c) => (
                  <button
                    key={c}
                    type="button"
                    onClick={() => setChannel(c)}
                    className={`rounded-lg border px-4 py-3 text-left text-sm transition-colors ${
                      channel === c ? "border-brand bg-brand-soft font-semibold text-brand" : "border-line bg-white hover:bg-paper"
                    }`}
                  >
                    {channelLabels[c]}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <Label hint="선택">이번 글의 주제</Label>
              <Input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder={topicHints[channel]} maxLength={300} />
            </div>
            <Button onClick={run} disabled={loading || !isComplete}>
              {loading && <Spinner />}
              {loading ? "작성 중" : "글 생성하기"}
            </Button>
          </div>
        </Card>

        {error && <ErrorNote>{error}</ErrorNote>}
        {result && <DemoModeBanner mode={mode} />}

        {result && (
          <div className="grid gap-4 lg:grid-cols-[3fr_2fr]">
            <Card>
              <div className="flex items-center justify-between gap-3">
                <h2 className="font-bold">{channelLabels[channel]}</h2>
                <CopyButton text={fullText} />
              </div>
              {result.title && <p className="mt-4 text-lg font-bold leading-snug">{result.title}</p>}
              <p className="mt-3 text-sm leading-relaxed whitespace-pre-wrap">{result.body}</p>
              {result.hashtags.length > 0 && (
                <p className="mt-4 text-sm text-brand leading-relaxed">
                  {result.hashtags.map((h) => (h.startsWith("#") ? h : `#${h}`)).join(" ")}
                </p>
              )}
            </Card>

            <div className="space-y-4">
              <Card>
                <h3 className="font-bold text-sm">이 글에서 의도적으로 피한 것</h3>
                <ul className="mt-3 space-y-2 text-sm text-ink-soft leading-relaxed list-disc pl-4">
                  {result.complianceNotes.map((n, i) => (
                    <li key={i}>{n}</li>
                  ))}
                </ul>
              </Card>

              <Card>
                <h3 className="font-bold text-sm">규칙 기반 자체 검사</h3>
                {selfCheck.length === 0 ? (
                  <p className="mt-2 text-sm text-ok font-semibold">키워드 기준 위험 표현 없음</p>
                ) : (
                  <ul className="mt-3 space-y-3">
                    {selfCheck.map((f, i) => (
                      <FindingCard key={i} finding={f} specialty={specialty} />
                    ))}
                  </ul>
                )}
                <p className="mt-3 text-xs text-ink-soft leading-relaxed">
                  게시 전 &lsquo;광고 문구 검사&rsquo;에서 문맥 검사를 한 번 더 하고, 광고성 게시물은 {specialty.reviewBody} 심의를 거치세요.
                </p>
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
