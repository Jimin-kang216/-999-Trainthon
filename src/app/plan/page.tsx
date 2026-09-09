"use client";

import { ProfileSummary } from "@/components/profile-summary";
import { Card, CopyButton, PageHeader } from "@/components/ui";
import { channelLabels } from "@/lib/schemas";
import { localKeywords, weeklyPlan } from "@/lib/local-plan";
import { useClinicProfile } from "@/lib/use-clinic-profile";

export default function PlanPage() {
  const { profile, isComplete, loaded } = useClinicProfile();
  const keywords = isComplete ? localKeywords(profile) : [];
  const plan = isComplete ? weeklyPlan(profile) : [];
  const keywordText = keywords.join("\n");

  return (
    <div>
      <PageHeader
        eyebrow="This week"
        title="이번 주 계획"
        description="프로필의 지역·진료 항목으로 검색 키워드와 7일 콘텐츠 일정을 만듭니다. 네이버 광고 API 없이, 원장이 이번 주에 실제로 올릴 일만 남깁니다."
      />

      <div className="space-y-4">
        {loaded && <ProfileSummary profile={profile} isComplete={isComplete} />}

        {isComplete && (
          <>
            <Card>
              <div className="flex items-center justify-between gap-3">
                <h2 className="font-bold">지역 검색 키워드</h2>
                <CopyButton text={keywordText} />
              </div>
              <p className="mt-1 text-sm text-ink-soft">
                네이버 검색창·플레이스 키워드에 그대로 넣습니다. 효과·할인과 붙이지 마세요.
              </p>
              <ul className="mt-4 flex flex-wrap gap-2">
                {keywords.map((k) => (
                  <li key={k} className="rounded-full border border-line bg-paper px-3 py-1 text-sm">
                    {k}
                  </li>
                ))}
              </ul>
            </Card>

            <Card>
              <h2 className="font-bold">7일 콘텐츠 일정</h2>
              <p className="mt-1 text-sm text-ink-soft">각 항목은 콘텐츠 생성 화면에서 같은 채널·주제로 이어서 쓰면 됩니다.</p>
              <ol className="mt-4 divide-y divide-line">
                {plan.map((item) => (
                  <li key={item.day} className="py-4 first:pt-0 last:pb-0 grid gap-1 sm:grid-cols-[2.5rem_1fr]">
                    <span className="text-sm font-bold text-brand">{item.day}</span>
                    <div>
                      <p className="text-sm font-semibold">{item.title}</p>
                      <p className="mt-1 text-xs text-ink-soft">
                        {channelLabels[item.channel]} · {item.why}
                      </p>
                    </div>
                  </li>
                ))}
              </ol>
            </Card>
          </>
        )}
      </div>
    </div>
  );
}
