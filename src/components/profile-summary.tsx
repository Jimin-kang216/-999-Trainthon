"use client";

import Link from "next/link";
import type { ClinicProfile } from "@/lib/schemas";
import { InfoNote } from "./ui";

export function ProfileSummary({ profile, isComplete }: { profile: ClinicProfile; isComplete: boolean }) {
  if (!isComplete) {
    return (
      <InfoNote>
        먼저{" "}
        <Link href="/profile" className="font-semibold underline">
          한의원 프로필
        </Link>
        을 입력해 주세요. 이름과 지역만 있어도 시작할 수 있습니다.
      </InfoNote>
    );
  }

  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 rounded-lg border border-line bg-white px-4 py-3 text-sm">
      <span className="font-semibold">{profile.name}</span>
      <span className="text-ink-soft">{profile.region}</span>
      {profile.since && <span className="text-ink-soft">{profile.since}년 개원</span>}
      {profile.services.length > 0 && <span className="text-ink-soft">{profile.services.join(" · ")}</span>}
      <Link href="/profile" className="ml-auto text-brand font-semibold">
        수정
      </Link>
    </div>
  );
}
