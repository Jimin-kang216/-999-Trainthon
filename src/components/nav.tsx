"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LlmStatusChip } from "./demo-banner";

const links = [
  { href: "/check", label: "광고 문구 검사" },
  { href: "/generate", label: "콘텐츠 생성" },
  { href: "/review", label: "리뷰 답변" },
  { href: "/plan", label: "이번 주 계획" },
  { href: "/profile", label: "한의원 프로필" },
] as const;

export function Nav() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-10 border-b border-line bg-white/90 backdrop-blur">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
        <div className="flex items-center gap-2 shrink-0">
          <Link href="/" className="font-bold tracking-tight text-ink">
            한카피
          </Link>
          <LlmStatusChip />
        </div>
        <nav className="flex items-center gap-1 text-sm overflow-x-auto">
          {links.map((l) => {
            const active = pathname === l.href;
            return (
              <Link
                key={l.href}
                href={l.href}
                className={`px-3 py-1.5 rounded-md whitespace-nowrap transition-colors ${
                  active ? "bg-brand-soft text-brand font-semibold" : "text-ink-soft hover:bg-paper hover:text-ink"
                }`}
              >
                {l.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
