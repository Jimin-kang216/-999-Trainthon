import { hanbang } from "./hanbang";
import type { Rule, Specialty } from "./types";

export type { Rule, Severity, Specialty } from "./types";

/**
 * 진료과 레지스트리.
 * 새 진료과(치과, 정형외과 등)를 추가할 때는 이 배열에 데이터 파일만 더하면 된다.
 * 화면과 API는 진료과에 의존하지 않는다.
 */
export const specialties: Specialty[] = [hanbang];

export const DEFAULT_SPECIALTY_ID = hanbang.id;

export function getSpecialty(id: string | undefined | null): Specialty {
  return specialties.find((s) => s.id === id) ?? hanbang;
}

export function getRule(specialty: Specialty, ruleId: string): Rule | undefined {
  return specialty.rules.find((r) => r.id === ruleId);
}
