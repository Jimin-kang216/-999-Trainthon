"use client";

import { useState } from "react";
import { ProfileSummary } from "@/components/profile-summary";
import { Button, Card, CopyButton, ErrorNote, Label, PageHeader, Spinner, TextArea } from "@/components/ui";
import type { ReviewReply } from "@/lib/schemas";
import { useClinicProfile } from "@/lib/use-clinic-profile";

const samples = [
  {
    rating: 5,
    text: "허리 디스크로 몇 년 고생했는데 여기 원장님이 추나 세 번 해주시고 한약 지어주셔서 통증이 거의 사라졌어요. 설명도 꼼꼼하게 해주시고 어머니도 모시고 갈 예정입니다.",
  },
  {
    rating: 2,
    text: "예약하고 갔는데 40분 기다렸습니다. 원장님은 친절하셨지만 데스크 응대가 좀 아쉬웠어요. 주차도 불편합니다.",
  },
];

export default function ReviewPage() {
  const { profile, isComplete, loaded } = useClinicProfile();
  const [review, setReview] = useState("");
  const [rating, setRating] = useState<number>(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ReviewReply | null>(null);

  async function run() {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("/api/review-reply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile, review, rating }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "답변 생성에 실패했습니다.");
      setResult(data.result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "답변 생성에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Place reviews"
        title="플레이스 리뷰 답변"
        description="환자가 리뷰에 쓴 진료 내용을 답글에서 되풀이하지 않고, 개인정보 노출과 재방문 유인(할인·증정) 없이 답글을 씁니다."
      />

      <div className="space-y-4">
        {loaded && <ProfileSummary profile={profile} isComplete={isComplete} />}

        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <div className="space-y-4">
              <div>
                <Label>별점</Label>
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((n) => (
                    <button
                      key={n}
                      type="button"
                      onClick={() => setRating(n)}
                      aria-label={`${n}점`}
                      className={`size-9 rounded-md border text-sm font-semibold transition-colors ${
                        n <= rating ? "border-brand bg-brand-soft text-brand" : "border-line bg-white text-ink-soft"
                      }`}
                    >
                      {n}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <Label hint={`${review.length} / 3000`}>리뷰 원문</Label>
                <TextArea rows={8} value={review} onChange={(e) => setReview(e.target.value)} placeholder="네이버 플레이스 리뷰를 붙여 넣으세요." />
              </div>
              <div className="flex flex-wrap gap-2">
                <Button onClick={run} disabled={loading || !isComplete || review.trim() === ""}>
                  {loading && <Spinner />}
                  {loading ? "작성 중" : "답글 생성하기"}
                </Button>
                {samples.map((s, i) => (
                  <Button
                    key={i}
                    type="button"
                    variant="ghost"
                    onClick={() => {
                      setReview(s.text);
                      setRating(s.rating);
                    }}
                  >
                    예시 {s.rating}점 리뷰
                  </Button>
                ))}
              </div>
            </div>
          </Card>

          <div className="space-y-4">
            {error && <ErrorNote>{error}</ErrorNote>}
            {!result && !error && (
              <Card className="text-sm text-ink-soft leading-relaxed">
                답글과 함께, 답글에서 의도적으로 피한 항목(진료 내용 언급, 개인정보, 유인 표현)이 표시됩니다.
              </Card>
            )}
            {result && (
              <>
                <Card>
                  <div className="flex items-center justify-between gap-3">
                    <h2 className="font-bold">답글</h2>
                    <CopyButton text={result.reply} />
                  </div>
                  <p className="mt-3 text-sm leading-relaxed whitespace-pre-wrap">{result.reply}</p>
                </Card>
                <Card>
                  <h3 className="font-bold text-sm">이 답글에서 피한 것</h3>
                  <ul className="mt-3 space-y-2 text-sm text-ink-soft leading-relaxed list-disc pl-4">
                    {result.cautions.map((c, i) => (
                      <li key={i}>{c}</li>
                    ))}
                  </ul>
                </Card>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
