# 투자 전략 설계 워크플로우

## 프로젝트 개요

개인 투자 전략을 체계적으로 수립하고, 향후 **투자 지원 대시보드**로 발전시키기 위한 리서치 및 설계 프로젝트입니다.

## 진행 프로세스

### Phase 1: 투자 전략 조사 및 비교 분석
- **목표**: 다양한 투자 전략의 특징, 장단점을 파악하고 비교
- **산출물**: `01-investment-strategies-report.md`
- **범위**: 주식 투자 전략 중심 (코인, 부동산은 확장 예정)
- **포함 전략**: 가치투자, 성장투자, 인덱스투자, 모멘텀, 배당투자, 퀀트, 스윙 트레이딩, 자산배분 등

### Phase 2: 유명 투자자 전략 및 성향 조사
- **목표**: 검증된 투자자들의 철학과 전략을 분석하여 벤치마크 설정
- **산출물**: `02-famous-investors-report.md`
- **대상 투자자**:
  1. 워렌 버핏 (Warren Buffett) — 가치투자
  2. 로버트 기요사키 (Robert Kiyosaki) — 자산/현금흐름
  3. 레이 달리오 (Ray Dalio) — 올웨더 포트폴리오
  4. 피터 린치 (Peter Lynch) — 성장 가치투자
  5. 존 보글 (John Bogle) — 인덱스 투자

### Phase 3: 개인 투자 전략 수립
- **목표**: 나만의 투자 전략과 원칙을 정립
- **산출물**: `03-personal-strategy-template.md`
- **활용**: 유명 투자자와의 성향 비교, 자산 배분 설계
- **연계**: 투자 지원 대시보드의 데이터 구조로 활용

## 자산군 확장 로드맵

```
[현재] 주식 (Stock)
  │
  ├── [확장 1] 암호화폐 (Cryptocurrency)
  │     └── 코인 투자 전략, DeFi, 포트폴리오 비중
  │
  └── [확장 2] 부동산 (Real Estate)
        └── 부동산 투자 전략, REITs, 실물 부동산
```

## 최종 목표: 투자 지원 대시보드

리서치 결과를 기반으로 다음 기능을 갖춘 대시보드를 구축할 예정:
- 포트폴리오 현황 시각화
- 투자 전략 기반 자산 배분 추천
- 유명 투자자 벤치마크 비교
- 자산군별 (주식/코인/부동산) 통합 관리

## 문서 구조

```
docs/
├── investment-strategy-workflow.md    ← 현재 문서 (워크플로우)
├── 01-investment-strategies-report.md ← Phase 1 산출물
├── 02-famous-investors-report.md      ← Phase 2 산출물
├── 03-personal-strategy-template.md   ← Phase 3 산출물 (작성 예시)
├── 03-personal-strategy-blank.md      ← Phase 3 빈 템플릿
└── 04-strategy-creation-guide.md      ← 전략 수립 프로세스 가이드 (Step 1-7)
```
