# CLAUDE.md — pearty 프로젝트 가이드

## 프로젝트 개요

**pearty**는 개인 투자 전략을 체계적으로 수립하고, 최종적으로 **투자 지원 대시보드**를 구축하기 위한 프로젝트입니다.

현재 단계: InvestPulse 대시보드 Phase 3 완료 (주식 통합 + 포트폴리오 리밸런싱)

## 저장소 구조

```
pearty/
├── CLAUDE.md                              ← 프로젝트 가이드 (현재 문서)
├── README.md                              ← 프로젝트 소개
├── docs/
│   ├── investment-strategy-workflow.md     ← 전체 워크플로우 및 프로세스
│   ├── 01-investment-strategies-report.md  ← 투자 전략 비교 분석 보고서
│   ├── 02-famous-investors-report.md       ← 유명 투자자 5인 분석 보고서
│   └── 03-personal-strategy-template.md   ← 개인 투자 전략 수립 템플릿
└── investpulse/                           ← 투자 지원 대시보드
    ├── backend/                           ← FastAPI 백엔드
    │   ├── app/                           ← 애플리케이션 코드
    │   │   ├── routers/                   ← API 라우터
    │   │   ├── services/                  ← 비즈니스 로직
    │   │   ├── models/                    ← SQLAlchemy 모델
    │   │   └── schemas/                   ← Pydantic 스키마
    │   └── requirements.txt
    ├── frontend/                          ← Vue 3 + TypeScript 프론트엔드
    │   └── src/
    │       ├── views/                     ← 페이지 컴포넌트
    │       ├── components/                ← UI 컴포넌트
    │       ├── composables/               ← Composition API hooks
    │       ├── stores/                    ← Pinia 상태관리
    │       └── api/                       ← API 클라이언트
    ├── docker-compose.yml
    └── README.md
```

## 프로젝트 로드맵

### InvestPulse 대시보드 개발
1. **Phase 1** (완료): MVP — 암호화폐 모니터링 + 기술지표 + 알림
   - FastAPI 백엔드 + Upbit API 연동
   - RSI, MACD, Bollinger Bands 기술지표 계산
   - Discord 웹훅 알림
   - Vue 3 대시보드 (캔들차트, 지표 패널, 포트폴리오)
2. **Phase 2** (완료): 알림 시스템 고도화
   - 알림 조건 CRUD 확장 (PRICE, CHANGE_RATE, 쿨다운, 복제, bulk 작업)
   - 조건 평가 엔진 고도화 (쿨다운, 히스토리 자동 기록)
   - 알림 히스토리 (타임라인 UI, 필터, 페이지네이션)
3. **Phase 3** (완료): 주식 통합 + 포트폴리오
   - 한국투자증권 OpenAPI 연동 (주식 현재가, 캔들, 기술지표)
   - 포트폴리오 자산군 분류 (crypto, stock, cash_bond)
   - 목표 자산배분 관리 (개인 전략 템플릿 기반)
   - 포트폴리오 리밸런싱 제안 (현재 vs 목표 비중 비교)
   - StocksView 주식 모니터링 화면
4. **Phase 4** (예정): 고도화
   - 다크모드 / 테마 커스터마이징
   - 모바일 반응형
   - 뉴스 피드 통합

## Git 컨벤션

- **기본 브랜치**: `master`
- **커밋 서명**: SSH 서명 활성화
- **언어**: 한국어 중심 (기술 용어는 영어 병기)

## AI 어시스턴트 가이드라인

- 문서는 한국어로 작성하되, 투자 용어는 한국어(영어) 형태로 병기
- `docs/` 디렉토리 내 문서 간 상호 참조 유지
- 대시보드 개발 시 `03-personal-strategy-template.md`의 JSON 데이터 구조를 참조
- 자산군 확장 시 기존 문서 구조를 유지하며 섹션 추가
