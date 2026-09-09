import type { ReactNode } from "react";
import type { Severity } from "@/data/specialties";

export function PageHeader({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return (
    <div className="mb-8">
      <p className="text-xs font-semibold tracking-widest text-brand uppercase">{eyebrow}</p>
      <h1 className="mt-2 text-2xl sm:text-3xl font-bold tracking-tight">{title}</h1>
      <p className="mt-2 text-ink-soft leading-relaxed max-w-2xl">{description}</p>
    </div>
  );
}

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`bg-white border border-line rounded-xl p-5 sm:p-6 ${className}`}>{children}</section>;
}

export function Label({ children, hint }: { children: ReactNode; hint?: string }) {
  return (
    <div className="mb-1.5 flex items-baseline justify-between gap-3">
      <span className="text-sm font-semibold">{children}</span>
      {hint && <span className="text-xs text-ink-soft">{hint}</span>}
    </div>
  );
}

const fieldClass =
  "w-full rounded-lg border border-line bg-white px-3 py-2 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand-soft disabled:bg-paper";

export function TextArea(props: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea {...props} className={`${fieldClass} leading-relaxed ${props.className ?? ""}`} />;
}

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={`${fieldClass} ${props.className ?? ""}`} />;
}

export function Select(props: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return <select {...props} className={`${fieldClass} ${props.className ?? ""}`} />;
}

export function Button({
  children,
  variant = "primary",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "ghost" }) {
  const styles =
    variant === "primary"
      ? "bg-brand text-white hover:bg-blue-800 disabled:bg-blue-300"
      : "bg-white border border-line text-ink hover:bg-paper";
  return (
    <button
      {...props}
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition-colors disabled:cursor-not-allowed ${styles} ${props.className ?? ""}`}
    >
      {children}
    </button>
  );
}

export function Spinner() {
  return (
    <span
      aria-hidden
      className="inline-block size-4 rounded-full border-2 border-current border-r-transparent animate-spin"
    />
  );
}

export function ErrorNote({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-lg border border-risk-high/30 bg-risk-high-soft px-4 py-3 text-sm text-risk-high">{children}</div>
  );
}

export function InfoNote({ children }: { children: ReactNode }) {
  return <div className="rounded-lg border border-brand/20 bg-brand-soft px-4 py-3 text-sm text-ink">{children}</div>;
}

const severityStyles: Record<Severity | "none", { label: string; className: string }> = {
  high: { label: "높음", className: "bg-risk-high-soft text-risk-high" },
  medium: { label: "중간", className: "bg-risk-medium-soft text-risk-medium" },
  low: { label: "낮음", className: "bg-risk-low-soft text-risk-low" },
  none: { label: "이상 없음", className: "bg-ok-soft text-ok" },
};

export function SeverityBadge({ severity, prefix }: { severity: Severity | "none"; prefix?: string }) {
  const s = severityStyles[severity];
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${s.className}`}>
      {prefix ? `${prefix} ${s.label}` : s.label}
    </span>
  );
}

export function CopyButton({ text }: { text: string }) {
  return (
    <Button
      type="button"
      variant="ghost"
      onClick={() => navigator.clipboard.writeText(text)}
      className="!px-3 !py-1 text-xs"
    >
      복사
    </Button>
  );
}
