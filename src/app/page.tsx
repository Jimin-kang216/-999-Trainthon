import Link from "next/link";
import { specialties } from "@/data/specialties";
import { Card } from "@/components/ui";

const features = [
  {
    href: "/check",
    title: "광고 문구 검사",
    description:
      "블로그 글, 인스타 캡션, 플레이스 소개글을 붙이면 의료법 제56조·제27조 기준으로 위험 구절을 조항별로 짚고 안전한 수정본을 만들어 줍니다.",
    tag: "핵심 기능",
  },
  {
    href: "/generate",
    title: "콘텐츠 생성",
    description:
      "원장의 진료 철학과 주요 진료 항목을 넣으면 규정을 처음부터 지킨 플레이스 소개글·블로그 글·인스타 게시물을 씁니다.",
    tag: "규정 내장 생성",
  },
  {
    href: "/review",
    title: "플레이스 리뷰 답변",
    description:
      "환자 리뷰에 진료 내용을 되풀이하지 않고, 개인정보와 유인 행위 소지 없이 답글을 씁니다. 동네 의원의 유일한 유입 채널을 지킵니다.",
    tag: "일상 운영",
  },
];

export default function HomePage() {
  const specialty = specialties[0];

  return (
    <div className="space-y-12">
      <section className="max-w-3xl">
        <p className="text-xs font-semibold tracking-widest text-brand uppercase">For solo clinics</p>
        <h1 className="mt-3 text-3xl sm:text-4xl font-bold tracking-tight leading-tight">
          실력은 있는데 검색에서 안 보이는
          <br />
          동네 한의원을 위한 마케팅 AI
        </h1>
        <p className="mt-4 text-ink-soft leading-relaxed">
          의료광고는 일반 마케팅과 다릅니다. 치료 후기, &ldquo;최고&rdquo;, 할인, 리뷰 이벤트가 전부 위법이라서 1인 원장은
          홍보를 시작조차 못 하고, 대행사는 월 100만 원이 넘습니다. 이 도구는 규정을 알고 있는 AI가 글을 쓰고 검수해서, 원장이
          직접 안전하게 알릴 수 있게 합니다.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            href="/check"
            className="rounded-lg bg-brand px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-800 transition-colors"
          >
            광고 문구 검사해 보기
          </Link>
          <Link
            href="/profile"
            className="rounded-lg border border-line bg-white px-5 py-2.5 text-sm font-semibold hover:bg-paper transition-colors"
          >
            한의원 프로필 입력
          </Link>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        {features.map((f) => (
          <Link key={f.href} href={f.href} className="group">
            <Card className="h-full transition-colors group-hover:border-brand">
              <span className="text-xs font-semibold text-brand">{f.tag}</span>
              <h2 className="mt-2 text-lg font-bold">{f.title}</h2>
              <p className="mt-2 text-sm text-ink-soft leading-relaxed">{f.description}</p>
            </Card>
          </Link>
        ))}
      </section>

      <section>
        <h2 className="text-lg font-bold">검사 기준으로 쓰는 조항</h2>
        <p className="mt-1 text-sm text-ink-soft">
          현재 {specialty.name} 기준 {specialty.rules.length}개 조항. 심의 기관: {specialty.reviewBody}. 다른 진료과는 규칙
          데이터 파일만 추가하면 같은 화면으로 동작합니다.
        </p>
        <ul className="mt-4 grid gap-2 sm:grid-cols-2">
          {specialty.rules.map((r) => (
            <li key={r.id} className="rounded-lg border border-line bg-white px-4 py-3">
              <div className="flex items-baseline justify-between gap-3">
                <span className="text-sm font-semibold">{r.title}</span>
                <span className="text-xs text-ink-soft whitespace-nowrap">{r.article}</span>
              </div>
              <p className="mt-1 text-xs text-ink-soft leading-relaxed">{r.summary}</p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
