"use client";

import { useState } from "react";
import { getSpecialty } from "@/data/specialties";
import {
  Button,
  Card,
  InfoNote,
  Input,
  Label,
  PageHeader,
  TextArea,
} from "@/components/ui";
import type { ClinicProfile } from "@/lib/schemas";
import {
  emptyProfile,
  sampleProfile,
  useClinicProfile,
} from "@/lib/use-clinic-profile";

export default function ProfilePage() {
  const { profile, save, reset, loaded } = useClinicProfile();

  return (
    <div>
      <PageHeader
        eyebrow="Clinic profile"
        title="한의원 프로필"
        description="콘텐츠 생성과 리뷰 답변이 이 정보를 근거로 씁니다. 여기에 없는 사실은 AI가 만들어 넣지 않으므로, 증명 가능한 내용만 원장의 말투로 적어 주세요. 이 브라우저에만 저장됩니다."
      />

      {/* localStorage 로드가 끝난 뒤에 마운트해서 초기값을 한 번만 주입한다. */}
      {loaded && (
        <ProfileForm initial={profile} onSave={save} onReset={reset} />
      )}

      <div className="mt-6">
        <InfoNote>
          &ldquo;최고&rdquo;, &ldquo;전문&rdquo;, &ldquo;완치&rdquo; 같은 표현은
          여기 적어도 생성 단계에서 자동으로 제외됩니다. 강점은 형용사가 아니라
          사실(연도, 시간, 방식)로 적을수록 좋은 글이 나옵니다.
        </InfoNote>
      </div>
    </div>
  );
}

function ProfileForm({
  initial,
  onSave,
  onReset,
}: {
  initial: ClinicProfile;
  onSave: (p: ClinicProfile) => void;
  onReset: () => void;
}) {
  const [draft, setDraft] = useState<ClinicProfile>(initial);
  const [savedAt, setSavedAt] = useState<number | null>(null);
  const specialty = getSpecialty(draft.specialtyId);

  function update<K extends keyof ClinicProfile>(
    key: K,
    value: ClinicProfile[K],
  ) {
    setDraft((d) => ({ ...d, [key]: value }));
  }

  function toggleService(s: string) {
    update(
      "services",
      draft.services.includes(s)
        ? draft.services.filter((x) => x !== s)
        : [...draft.services, s],
    );
  }

  function handleSave() {
    onSave(draft);
    setSavedAt(Date.now());
  }

  return (
    <Card>
      <div className="grid gap-5 sm:grid-cols-2">
        <div>
          <Label>한의원 이름</Label>
          <Input
            value={draft.name}
            onChange={(e) => update("name", e.target.value)}
            placeholder="예: 정릉 바른몸 한의원"
          />
        </div>
        <div>
          <Label hint="검색 노출의 핵심">지역</Label>
          <Input
            value={draft.region}
            onChange={(e) => update("region", e.target.value)}
            placeholder="예: 서울 성북구 정릉동"
          />
        </div>
        <div>
          <Label hint="선택">근처 랜드마크</Label>
          <Input
            value={draft.nearby}
            onChange={(e) => update("nearby", e.target.value)}
            placeholder="예: 정릉시장, ○○역 2번 출구"
          />
        </div>
        <div>
          <Label hint="선택">개원 연도</Label>
          <Input
            value={draft.since}
            onChange={(e) => update("since", e.target.value)}
            placeholder="예: 2007"
            inputMode="numeric"
          />
        </div>
        <div className="sm:col-span-2">
          <Label hint="선택">원장 이름</Label>
          <Input
            value={draft.directorName}
            onChange={(e) => update("directorName", e.target.value)}
            placeholder="예: 김○○"
          />
        </div>

        <div className="sm:col-span-2">
          <Label hint="실제로 하는 진료만 선택">주요 진료 항목</Label>
          <div className="flex flex-wrap gap-2">
            {specialty.commonServices.map((s) => {
              const on = draft.services.includes(s);
              return (
                <button
                  key={s}
                  type="button"
                  onClick={() => toggleService(s)}
                  className={`rounded-full border px-3 py-1 text-sm transition-colors ${
                    on
                      ? "border-brand bg-brand-soft text-brand font-semibold"
                      : "border-line bg-white hover:bg-paper"
                  }`}
                >
                  {s}
                </button>
              );
            })}
          </div>
        </div>

        <div className="sm:col-span-2">
          <Label hint="원장이 말한 그대로">진료 철학</Label>
          <TextArea
            rows={3}
            value={draft.philosophy}
            onChange={(e) => update("philosophy", e.target.value)}
            placeholder="예: 검사보다 문진에 시간을 씁니다. 환자가 본인 몸 상태를 설명할 수 있을 때까지 듣습니다."
          />
        </div>
        <div className="sm:col-span-2">
          <Label hint="증명 가능한 사실만">우리 한의원의 강점</Label>
          <TextArea
            rows={3}
            value={draft.strengths}
            onChange={(e) => update("strengths", e.target.value)}
            placeholder="예: 2007년부터 같은 자리에서 진료. 초진 상담 20분 이상. 어르신 환자에게 천천히 설명."
          />
        </div>
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-2">
        <Button
          onClick={handleSave}
          disabled={draft.name.trim() === "" || draft.region.trim() === ""}
        >
          저장
        </Button>
        <Button
          type="button"
          variant="ghost"
          onClick={() => setDraft(sampleProfile)}
        >
          예시 프로필 불러오기
        </Button>
        <Button
          type="button"
          variant="ghost"
          onClick={() => {
            onReset();
            setDraft(emptyProfile);
            setSavedAt(null);
          }}
        >
          초기화
        </Button>
        {savedAt && (
          <span className="text-sm text-ok font-semibold">저장했습니다.</span>
        )}
      </div>
    </Card>
  );
}
