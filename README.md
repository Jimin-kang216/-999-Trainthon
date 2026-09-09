# AfterMap

TrainThon 프로젝트. 재난 **전·후 고해상도 위성영상을 학습 기반 매칭으로 정합**하고, ΔNDVI + SSIM으로 **50 m 격자 피해 지도**를 만든 뒤, CAL FIRE 현장 조사(DINS)로 점수를 검증한다.

대상 사례: **2025년 1월 로스앤젤레스 산불** (Eaton / Palisades). 데이터는 [Maxar Open Data Program](https://www.maxar.com/open-data) STAC 카탈로그에서 공개 COG를 읽는다.

```
Maxar STAC  →  DISK + LightGlue 정합  →  ΔNDVI · SSIM 점수  →  50 m GeoJSON
                  vs SIFT (대조군)         격자 집계              Streamlit 지도
                  NAIP 2022 이종 소스
```

AI를 빼면 제품이 성립하지 않는 지점은 **정합**이다. 같은 위성 전·후 쌍은 이미 정사보정돼 있어 SIFT로도 맞지만, 실제 재난 대응에서 “이전 영상”은 대개 몇 년 전 항공사진 기본도이다. 2022 USDA NAIP 항공영상 → 2025 Maxar 위성 매칭에서 LightGlue 인라이어가 SIFT 대비 **약 9~16배**다.

## 데모

```bash
pip install -r requirements.txt
# 이미 data/tiles 와 results 가 있으면:
streamlit run app.py
```

앱 탭:

1. **Damage map** — 히트맵 + GeoJSON 다운로드
2. **Registration** — LightGlue vs SIFT 매칭선, 인라이어 표, 체커보드
3. **Validation vs DINS** — 구조물 단위 ROC-AUC / precision-recall

타일 GeoTIFF는 git에 넣지 않았다 (`data/tiles/`). 클론만 한 환경에서는 아래 파이프라인을 한 번 돌리면 된다.

## 파이프라인 (처음부터)

```bash
python -m src.ingest all --n 4          # STAC 인덱스, 전/후 페어링, 2048px 다운로드
python -m src.register                  # Maxar 전·후: LightGlue vs SIFT, 워핑
python -m src.naip --qk 031311103033    # (선택) 2022 NAIP 모자이크
python -m src.register --pre-source naip
python -m src.damage                    # ΔNDVI + SSIM → 격자 GeoJSON
python -m src.validate                  # CAL FIRE DINS 다운로드 및 평가
streamlit run app.py
```

CPU만 사용한다. 타일 4쌍 정합은 분 단위.

| 모듈 | 역할 |
|---|---|
| `src/ingest.py` | Maxar STAC 인덱싱, quadkey 페어링, 유효화소 probe, COG 다운샘플 |
| `src/register.py` | DISK+LightGlue / SIFT, MAGSAC++ 호모그래피, RMSE·인라이어 격자 |
| `src/naip.py` | Planetary Computer NAIP 2022를 같은 격자로 워프 |
| `src/damage.py` | ΔNDVI + 베이스라인 보정 SSIM, 50 m 셀, GeoJSON/GeoTIFF |
| `src/validate.py` | DINS 포인트와 공간 조인, ROC-AUC / PR |
| `app.py` | Streamlit 데모 |

## 결과 요약

### 이종 소스 정합 (NAIP 2022 항공 → Maxar 2025 위성, 1024 px)

| 타일 | 화재 | SIFT 인라이어 | LightGlue 인라이어 | 배수 | SIFT 빈 셀/64 |
|---|---|---|---|---|---|
| `031311103033` | Eaton | 60 | 949 | 16× | 30 |
| `031311102212` | Palisades | 83 | 840 | 10× | 41 |
| `031311103122` | Eaton | 49 | 808 | 16× | 41 |
| `031311102210` | Palisades | 124 | 1110 | 9× | 26 |

같은 센서 Maxar 전·후 쌍에서는 두 매처 모두 성공한다 (인라이어 1,100–4,400). 학습 매처가 갈리는 조건은 **센서·계절·연도가 다른 기본도**다.

### 피해 점수 vs CAL FIRE DINS (Destroyed vs No Damage)

| 타일 | 화재 | 타일 안 구조물 | ROC-AUC | AP | severe P / R |
|---|---|---|---|---|---|
| `031311103033` | Eaton | 9,115 | 0.934 | 0.922 | 0.781 / 0.961 |
| `031311103122` | Eaton | 1,649 | 0.955 | 0.727 | 0.826 / 0.487 |
| `031311102212` | Palisades | 431 | 0.843 | 0.495 | 0.338 / 0.883 |

알타데나 Eaton 타일이 주 결과다. Palisades 타일은 소실 구조물이 적어 AP가 낮다. 점수는 감독 학습이 아니라 ΔNDVI와 SSIM의 가중 합이며, 임계값 0.30 / 0.15는 고정이다.

정합이 제거한 허위 변화(정합 전 1−SSIM 대비): Eaton 알타데나 타일에서 0.556 → 0.299.

수치 원본: `results/registration_metrics.csv`, `results/validation_summary.csv`, `results/damage_summary.csv`.

## 한계 (발표에서 먼저 말할 것)

- 피해 점수는 건물 단위 분류 모델이 아니다. 식생 소실이 강한 산지에 점수가 몰리고, 콘크리트 지붕 소실은 SSIM에 더 의존한다.
- LightGlue는 1024 px에서 키포인트를 뽑아 원 해상도로 스케일하므로 RMSE에 ~1 px 양자화가 있다.
- 타일은 2.6 m/px로 다운샘플했다. 원본 COG는 ~0.5 m.
- B2G 고객(보험·지자체) 인터뷰는 이 버전에 없다.

## 다음에 이어서 할 연구 주제

다중시기 VHR 정합에서 학습 매칭 vs 수작업 특징, 텍스처 소실 지역 강건성, SAR–광학 이종 매칭, 위성–드론 스케일 차이. 이 저장소의 `results/` 표가 그 예비실험이다.
