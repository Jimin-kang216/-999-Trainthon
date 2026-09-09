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

const steps = [
  { n: "1", href: "/profile", title: "한의원 프로필", body: "이름·지역만 있어도 됩니다. 예시 불러오기로 바로 데모할 수 있습니다." },
  { n: "2", href: "/check", title: "위법 문구 검사", body: "위반 예시를 불러와 검사합니다. 조항별로 왜 안 되는지 보여 주는 게 핵심 데모입니다." },
  { n: "3", href: "/generate", title: "안전한 글 생성", body: "같은 한의원 정보로 플레이스 소개글을 만듭니다. API 키가 없어도 데모 모드로 동작합니다." },
];

const pitch = [
  {
    t: "문제 30초",
    body: "아버지 한의원은 2007년부터 한자리에서 진료하시는데, 위치가 불리하고 홍보를 못 하셔서 환자가 적습니다. 원인은 실력이 아니라 의료광고법입니다. 후기·최고·할인이 전부 위법이라 시작조차 못 합니다.",
  },
  {
    t: "제품 60초",
    body: "이 도구에 위험한 문구를 넣으면 조항별로 짚고 고칩니다. 원장 말투로 프로필을 적으면 규정을 지킨 플레이스·블로그·인스타 글과 리뷰 답글을 씁니다.",
  },
  {
    t: "시장 30초",
    body: "첫 고객은 한의원입니다. 같은 문제는 1인 원장 동네 의원 전체입니다. 대행사는 월 100만 원이고, 우리는 월 구독입니다. 진료과 확장은 규칙 파일 추가입니다.",
  },
  {
    t: "Q&A 방어",
    body: "이 도구는 사전심의를 대체하지 않습니다. 광고성 게시물은 한의사협회 심의를 받아야 합니다. 우리는 위법 초안을 안 쓰게 하는 보조 도구입니다.",
  },
];

export default function HomePage() {
  const specialty = specialties[0];

  return (
    <div className="space-y-12">
      <section className="max-w-3xl">
        <p className="text-xs font-semibold tracking-widest text-brand uppercase">한의원 홍보</p>
        <h1 className="mt-3 text-3xl sm:text-4xl font-bold tracking-tight leading-tight">
          올려도 되는
          <br />
          한의원 글만
        </h1>
        <p className="mt-4 text-ink-soft leading-relaxed max-w-xl">
          후기·최고·할인은 의료광고법 위반입니다. 한카피가 조항별로 걸러 주고, 네이버 플레이스·블로그·인스타 글을 규정에
          맞게 씁니다.
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

      <section>
        <h2 className="text-lg font-bold">지금 이 순서로 돌려 보세요</h2>
        <ol className="mt-4 grid gap-3 sm:grid-cols-3">
          {steps.map((s) => (
            <li key={s.n}>
              <Link href={s.href} className="block h-full">
                <Card className="h-full hover:border-brand transition-colors">
                  <span className="text-xs font-bold text-brand">STEP {s.n}</span>
                  <h3 className="mt-1 font-bold">{s.title}</h3>
                  <p className="mt-2 text-sm text-ink-soft leading-relaxed">{s.body}</p>
                </Card>
              </Link>
            </li>
          ))}
        </ol>
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
        <h2 className="text-lg font-bold">발표 대본 (약 2분)</h2>
        <p className="mt-1 text-sm text-ink-soft">2차 심사 발표·Q&amp;A용. 감성 도입은 30초만, 나머지는 데모와 시장입니다.</p>
        <ol className="mt-4 grid gap-3 sm:grid-cols-2">
          {pitch.map((p) => (
            <li key={p.t} className="rounded-xl border border-line bg-white p-5">
              <h3 className="text-sm font-bold text-brand">{p.t}</h3>
              <p className="mt-2 text-sm leading-relaxed">{p.body}</p>
            </li>
          ))}
        </ol>
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
