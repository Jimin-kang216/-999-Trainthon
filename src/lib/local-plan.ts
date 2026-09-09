import type { Channel, ClinicProfile } from "./schemas";
import { channelLabels } from "./schemas";

function lastToken(region: string): string {
  return region.trim().split(/\s+/).at(-1) || region;
}

function guToken(region: string): string {
  return region.trim().split(/\s+/).find((p) => /[구군시]$/.test(p)) || "";
}

/** 네이버 플레이스·검색에 실제로 넣는 지역 키워드. API 없이 프로필에서 조합한다. */
export function localKeywords(profile: ClinicProfile): string[] {
  const dong = lastToken(profile.region);
  const gu = guToken(profile.region);
  const services = profile.services.length > 0 ? profile.services : ["추나요법", "한약"];
  const keys = new Set<string>();

  keys.add(`${dong} 한의원`);
  keys.add(`${dong}한의원`);
  if (gu) {
    keys.add(`${gu} 한의원`);
    keys.add(`${gu} ${dong} 한의원`);
  }
  if (profile.nearby) {
    profile.nearby.split(/[,/]/).forEach((n) => {
      const t = n.trim();
      if (t) keys.add(`${t} 한의원`);
    });
  }
  for (const s of services.slice(0, 4)) {
    keys.add(`${dong} ${s}`);
    if (gu) keys.add(`${gu} ${s}`);
  }
  keys.add(`${dong} 교통사고 한의원`);
  keys.add(`${dong} 추나`);
  return [...keys];
}

export interface PlanItem {
  day: string;
  channel: Channel;
  title: string;
  why: string;
}

export function weeklyPlan(profile: ClinicProfile): PlanItem[] {
  const dong = lastToken(profile.region) || "우리 동네";
  const name = profile.name || "한의원";
  return [
    {
      day: "월",
      channel: "place",
      title: `${name} 플레이스 소개글 교체`,
      why: "검색 유입의 대부분이 플레이스에서 옵니다. 소개글만 규정에 맞게 고쳐도 노출이 달라집니다.",
    },
    {
      day: "화",
      channel: "instagram",
      title: `${dong}에서 ${profile.since || "오래"} 진료하는 이유 (개원 연도·위치만)`,
      why: "최상급 표현 없이 '한자리 진료'라는 사실만으로 신뢰를 만듭니다.",
    },
    {
      day: "수",
      channel: "blog",
      title: `${dong} 한의원 초진, 상담은 이렇게 진행합니다`,
      why: "효과 후기 대신 과정을 설명하면 제2호(치료경험담)를 피할 수 있습니다.",
    },
    {
      day: "목",
      channel: "instagram",
      title: "교통사고 후 한의원 진료, 보험 적용 안내 (절차만)",
      why: "자동차보험 절차는 정보가 필요하고, 치료 효과 단정이 아니라 행정 안내라 안전합니다.",
    },
    {
      day: "금",
      channel: "blog",
      title: `${dong}에서 오시는 길 · 주차 · 진료 시간`,
      why: "로컬 검색 키워드와 실무 정보는 광고 심의 부담이 상대적으로 낮습니다.",
    },
    {
      day: "토",
      channel: "instagram",
      title: "이번 주 남긴 플레이스 리뷰에 규정 지키는 답글 달기",
      why: "리뷰 미응답은 순위 하락 요인입니다. 답글도 유인·후기 인용이 되면 안 됩니다.",
    },
    {
      day: "일",
      channel: "place",
      title: "플레이스 사진 점검 (시술 장면 없는 외관·대기실만)",
      why: "시술 장면 노출(제6호)을 피하면서 동네 한의원처럼 보이게 합니다.",
    },
  ];
}

export { channelLabels };
