"use client";

import { useState } from "react";
import { getSpecialty } from "@/data/specialties";
import { FindingCard } from "@/components/finding-card";
import { DemoModeBanner } from "@/components/demo-banner";
import {
  Button,
  Card,
  CopyButton,
  ErrorNote,
  Label,
  PageHeader,
  Select,
  SeverityBadge,
  Spinner,
  TextArea,
} from "@/components/ui";
import { channelLabels, type Channel, type CheckResult } from "@/lib/schemas";

const sampleText = `정릉 최고의 척추 전문 한의원! 다른 한의원과 달리 저희는 국내 최초 신개념 추나요법으로 디스크를 완치시킵니다.
17년간 10만 명이 치료받았고 만족도 99%! 환자 후기: "3번 받고 허리 통증이 완전히 사라졌어요"
이번 달 추나 50% 할인, 리뷰 남기시면 공진단 1환 증정합니다.`;

export default function CheckPage() {
  const [text, setText] = useState("");
  const [channel, setChannel] = useState<Channel>("instagram");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CheckResult | null>(null);
  const [mode, setMode] = useState<"llm" | "rules-only" | null>(null);

  const specialty = getSpecialty("hanbang");

  async function run() {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("/api/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ specialtyId: specialty.id, channel, text }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "검사에 실패했습니다.");
      setResult(data.result);
      setMode(data.mode);
    } catch (e) {
      setError(e instanceof Error ? e.message : "검사에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Compliance check"
        title="광고 문구 검사"
        description="게시하려는 글을 붙이면 의료법 제56조 제2항과 제27조 제3항 기준으로 위험 구절을 찾고, 같은 의도를 유지한 안전한 수정본을 만들어 줍니다."
      />

      <div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
        <Card>
          <div className="space-y-4">
            <div>
              <Label hint="심의 대상 여부 판단에 사용">게시 예정 매체</Label>
              <Select value={channel} onChange={(e) => setChannel(e.target.value as Channel)}>
                {Object.entries(channelLabels).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v}
                  </option>
                ))}
              </Select>
            </div>
            <div>
              <Label hint={`${text.length} / 6000`}>검사할 문구</Label>
              <TextArea
                rows={14}
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="블로그 글, 인스타 캡션, 플레이스 소개글 등을 붙여 넣으세요."
              />
            </div>
            <div className="flex flex-wrap gap-2">
              <Button onClick={run} disabled={loading || text.trim().length === 0}>
                {loading && <Spinner />}
                {loading ? "검사 중" : "검사하기"}
              </Button>
              <Button type="button" variant="ghost" onClick={() => setText(sampleText)}>
                위반 예시 불러오기
              </Button>
            </div>
          </div>
        </Card>

        <div className="space-y-4">
          {error && <ErrorNote>{error}</ErrorNote>}

          {!result && !error && (
            <Card className="text-sm text-ink-soft leading-relaxed">
              결과가 여기에 표시됩니다. 조항별 위험 구절, 이유, 대체 문구, 사전심의 필요 여부, 전체 수정본 순서로 나옵니다.
            </Card>
          )}

          {result && (
            <>
              {mode && <DemoModeBanner mode={mode} />}

              <Card>
                <div className="flex flex-wrap items-center gap-2">
                  <SeverityBadge severity={result.overallRisk} prefix="전체 위험도" />
                  <span className="text-sm text-ink-soft">지적 {result.findings.length}건</span>
                </div>
                <p className="mt-3 text-sm leading-relaxed">{result.summary}</p>
                <div
                  className={`mt-4 rounded-md px-3 py-2 text-sm ${
                    result.needsPreReview ? "bg-risk-medium-soft text-risk-medium" : "bg-ok-soft text-ok"
                  }`}
                >
                  <span className="font-semibold">
                    {result.needsPreReview ? "사전심의 대상" : "사전심의 대상 아님"}
                  </span>
                  <p className="mt-1 leading-relaxed">{result.preReviewReason}</p>
                </div>
              </Card>

              {result.findings.length > 0 && (
                <ul className="space-y-3">
                  {result.findings.map((f, i) => (
                    <FindingCard key={`${f.ruleId}-${i}`} finding={f} specialty={specialty} />
                  ))}
                </ul>
              )}

              {result.rewritten && (
                <Card>
                  <div className="flex items-center justify-between gap-3">
                    <h2 className="font-bold">안전한 수정본</h2>
                    <CopyButton text={result.rewritten} />
                  </div>
                  <p className="mt-3 text-sm leading-relaxed whitespace-pre-wrap">{result.rewritten}</p>
                </Card>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
