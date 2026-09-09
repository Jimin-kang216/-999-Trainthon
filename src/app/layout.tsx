import type { Metadata } from "next";
import { Nav } from "@/components/nav";
import "./globals.css";

export const metadata: Metadata = {
  title: "동네 한의원 마케팅 AI",
  description:
    "의료광고 규정을 아는 AI가 동네 한의원의 플레이스 소개글, 블로그, 인스타그램 게시물을 대신 쓰고 검수합니다.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko" className="h-full">
      <body className="min-h-full flex flex-col">
        <Nav />
        <main className="flex-1 w-full max-w-5xl mx-auto px-4 sm:px-6 py-8 sm:py-12">{children}</main>
        <footer className="border-t border-line bg-white">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 text-xs text-ink-soft leading-relaxed">
            이 서비스는 의료광고 사전심의를 대체하지 않습니다. 검사 결과는 의료법 제56조·제27조를 기준으로 한 참고 정보이며, 게시
            전 대한한의사협회 의료광고심의위원회 심의를 거쳐야 합니다.
          </div>
        </footer>
      </body>
    </html>
  );
}
