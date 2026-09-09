import { getSpecialty, type Specialty } from "@/data/specialties";
import { prescan } from "./prescan";
import type { Channel, ClinicProfile, GenerateResult, ReviewReply } from "./schemas";

const COMPLIANCE_NOTES = [
  "치료 효과·완치·전후 비교를 쓰지 않았습니다 (의료법 제56조 제2항 제2호).",
  "최고·최초·유일·전문·명의 같은 최상급·자격 표방 표현을 쓰지 않았습니다 (제8호·제9호).",
  "할인·무료·증정·리뷰 이벤트를 넣지 않았습니다 (제13호, 제27조 제3항).",
  "다른 의료기관과 비교하지 않았습니다 (제4호).",
  "환자 후기를 인용하지 않았습니다 (제2호).",
];

function regionToken(region: string): string {
  const parts = region.trim().split(/\s+/);
  return parts.at(-1) || region;
}

function serviceLine(profile: ClinicProfile): string {
  return profile.services.length > 0 ? profile.services.join(", ") : "침·뜸·부항, 한약";
}

function yearsLine(profile: ClinicProfile): string {
  if (!profile.since) return "한자리에서 오래 진료하고 있습니다.";
  return `${profile.since}년부터 같은 자리에서 진료하고 있습니다.`;
}

/**
 * 키워드가 들어간 문장을 빼고, 남은 문장이 너무 짧으면 안전한 안내문으로 대체한다.
 * API 키가 없을 때 검사기의 '수정본'으로 쓴다.
 */
export function rewriteByRules(text: string, specialty: Specialty): string {
  const keywords = specialty.rules.flatMap((r) => r.keywords).filter((k) => k.length >= 2);
  const chunks = text
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);

  const kept: string[] = [];
  for (const line of chunks) {
    const sentences = line.split(/(?<=[.!?。])/).map((s) => s.trim()).filter(Boolean);
    const safe = sentences.filter(
      (s) => !keywords.some((k) => s.toLowerCase().includes(k.toLowerCase())),
    );
    if (safe.length > 0) kept.push(safe.join(" "));
  }

  if (kept.join("").length < 40) {
    return [
      "이 한의원은 지역에서 진료하고 있습니다.",
      "치료 효과나 결과를 단정하지 않고, 초진 상담에서 현재 상태를 충분히 들은 뒤 진료 계획을 안내합니다.",
      "이벤트·할인·후기 인용 없이, 진료 항목과 오시는 길만 안내하는 글로 바꿨습니다.",
      "광고 성격의 게시물은 게시 전 대한한의사협회 의료광고심의위원회 심의를 받으세요.",
    ].join("\n");
  }

  return [
    ...kept,
    "",
    "(위험 표현이 들어간 문장은 뺐습니다. 게시 전 대한한의사협회 의료광고심의위원회 심의를 받으세요.)",
  ].join("\n");
}

export function demoGenerate(profile: ClinicProfile, channel: Channel, topic: string): GenerateResult {
  const name = profile.name;
  const region = profile.region;
  const dong = regionToken(region);
  const services = serviceLine(profile);
  const years = yearsLine(profile);
  const philosophy = profile.philosophy || "초진 때는 어디가 불편한지 충분히 듣는 데 시간을 씁니다.";
  const strengths = profile.strengths || "설명을 천천히 하고, 서두르지 않고 상담합니다.";
  const nearby = profile.nearby ? `${profile.nearby}에서 오시기 좋습니다. ` : "";
  const director = profile.directorName ? `${profile.directorName} 원장이 ` : "";
  const topicLine = topic.trim();

  if (channel === "place") {
    return {
      title: "",
      body: [
        `${name}은 ${region}에서 ${years}`,
        "",
        `${director}${philosophy}`,
        "",
        `주로 ${services} 진료를 하고 있습니다. ${nearby}진료 가능 여부와 방법은 내원 후 상담에서 안내드립니다.`,
        "",
        strengths,
      ].join("\n"),
      hashtags: [],
      complianceNotes: COMPLIANCE_NOTES,
    };
  }

  if (channel === "blog") {
    const title = topicLine
      ? `${dong}에서 ${topicLine} — ${name} 안내`
      : `${dong} ${name}, 초진 상담은 이렇게 진행합니다`;
    return {
      title,
      body: [
        `${region}에 계신 분이 '근처 한의원'을 찾다가 이 글을 읽고 있을 수 있습니다. 효과를 약속하는 글이 아니라, 이 한의원이 초진을 어떻게 진행하는지 안내하는 글입니다.`,
        "",
        `## 어디에 있나요`,
        `${name}은 ${region}에 있습니다. ${years} ${nearby}`,
        "",
        `## 초진에서 하는 일`,
        philosophy,
        "",
        `## 어떤 진료를 하나요`,
        `주로 ${services} 진료를 합니다. 개인마다 상태가 다르므로 특정 결과가 나온다고 단정하지 않습니다. 필요한 검사는 상담 후 안내합니다.`,
        "",
        `## 마치며`,
        strengths,
        topicLine ? `\n이번 글은 '${topicLine}'을 주제로, 치료 후기나 할인 없이 안내만 적었습니다.` : "",
      ].join("\n"),
      hashtags: [],
      complianceNotes: COMPLIANCE_NOTES,
    };
  }

  const first = topicLine || `${dong}에서 오래 진료하는 한의원입니다`;
  return {
    title: first,
    body: [
      first,
      "",
      `${name} · ${region}`,
      years,
      "",
      philosophy,
      "",
      `진료 항목: ${services}`,
      nearby ? nearby.trim() : "",
      "",
      "치료 결과나 후기를 올리지 않습니다. 궁금한 점은 전화 또는 방문 상담으로 안내드립니다.",
    ]
      .filter((line) => line !== "")
      .join("\n"),
    hashtags: [
      dong,
      `${dong}한의원`,
      region.replace(/\s+/g, ""),
      "한의원",
      "추나",
      "동네한의원",
      "초진상담",
      name.replace(/\s+/g, ""),
    ],
    complianceNotes: COMPLIANCE_NOTES,
  };
}

export function demoReviewReply(profile: ClinicProfile, review: string, rating?: number): ReviewReply {
  const name = profile.name;
  const stars = rating ?? 3;

  if (stars <= 2) {
    return {
      reply: `${name}입니다. 불편을 드려 죄송합니다. 답글에서 방문 내용이나 개인 정보를 언급하지는 않겠습니다. 사실 확인이 필요하시면 한의원으로 직접 연락 주시면 확인하겠습니다.`,
      cautions: [
        "리뷰에 적힌 대기·주차·응대 불만을 반박하지 않았습니다.",
        "증상·병명·진료 행위를 답글에 다시 쓰지 않았습니다.",
        "할인·재방문 혜택을 제안하지 않았습니다 (환자 유인 금지).",
      ],
    };
  }

  if (stars === 3) {
    return {
      reply: `${name}입니다. 방문해 주셔서 감사합니다. 더 편하게 이용하실 수 있도록 내부에서 살펴보겠습니다. 남기고 싶은 말씀이 있으면 한의원으로 연락 주세요.`,
      cautions: [
        "리뷰 원문의 구체적 에피소드를 재언급하지 않았습니다.",
        "효과 확인 표현('좋아지셨다니')을 쓰지 않았습니다.",
        "이벤트·증정을 연결하지 않았습니다.",
      ],
    };
  }

  return {
    reply: `${name}입니다. 방문해 주셔서 감사합니다. 진료 과정은 답글에 적지 않겠습니다. 궁금한 점이 생기면 한의원으로 문의해 주세요.`,
    cautions: [
      `리뷰에 나온 증상·치료 횟수 등(${review.slice(0, 12)}…)을 답글에 반복하지 않았습니다.`,
      "완치·효과 보장 표현을 쓰지 않았습니다.",
      "재방문 시 혜택을 제안하지 않았습니다.",
    ],
  };
}

export function selfCheckText(result: GenerateResult, specialtyId: string) {
  return prescan(`${result.title}\n${result.body}\n${result.hashtags.join(" ")}`, getSpecialty(specialtyId));
}
