"use client";

import { useCallback, useEffect, useState } from "react";
import { clinicProfileSchema, type ClinicProfile } from "./schemas";

const STORAGE_KEY = "clinic-profile:v1";

export const emptyProfile: ClinicProfile = {
  specialtyId: "hanbang",
  name: "",
  region: "",
  nearby: "",
  since: "",
  directorName: "",
  services: [],
  philosophy: "",
  strengths: "",
};

/** 데모용 예시. 발표 전에 실제 한의원 정보로 바꾼다. */
export const sampleProfile: ClinicProfile = {
  specialtyId: "hanbang",
  name: "정릉 바른몸 한의원",
  region: "서울 성북구 정릉동",
  nearby: "정릉시장, 국민대 정문 버스 정류장",
  since: "2007",
  directorName: "김○○",
  services: ["추나요법", "교통사고 후유증(자동차보험)", "침·뜸·부항", "한약(첩약)"],
  philosophy:
    "환자분이 어디가 왜 아픈지 본인 입으로 설명할 수 있을 때까지 이야기를 듣습니다. 검사보다 문진에 시간을 씁니다.",
  strengths:
    "2007년부터 같은 자리에서 진료했습니다. 처음 오신 분은 초진 상담을 20분 이상 잡습니다. 어르신 환자가 많아 설명을 천천히 합니다.",
};

/**
 * 한의원 프로필을 localStorage에 보관한다.
 * 캠프 데모에서는 로그인·DB 없이도 세 화면이 같은 프로필을 공유하면 충분하다.
 */
export function useClinicProfile() {
  const [profile, setProfile] = useState<ClinicProfile>(emptyProfile);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = clinicProfileSchema.safeParse(JSON.parse(raw));
        if (parsed.success) setProfile(parsed.data);
      }
    } finally {
      setLoaded(true);
    }
  }, []);

  const save = useCallback((next: ClinicProfile) => {
    setProfile(next);
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  }, []);

  const reset = useCallback(() => {
    setProfile(emptyProfile);
    window.localStorage.removeItem(STORAGE_KEY);
  }, []);

  const isComplete = profile.name.trim().length > 0 && profile.region.trim().length > 0;

  return { profile, save, reset, loaded, isComplete };
}
