# CLAUDE.md — pearty 프로젝트 가이드

## 프로젝트 개요

**pearty**는 개인 투자 전략을 체계적으로 수립하고, 최종적으로 **투자 지원 대시보드**를 구축하기 위한 프로젝트입니다.

현재 단계: 투자 전략 리서치 및 분석 문서 작성 중

## 저장소 구조

```
pearty/
├── CLAUDE.md                              ← 프로젝트 가이드 (현재 문서)
├── README.md                              ← 프로젝트 소개
└── docs/
    ├── investment-strategy-workflow.md     ← 전체 워크플로우 및 프로세스
    ├── 01-investment-strategies-report.md  ← 투자 전략 비교 분석 보고서
    ├── 02-famous-investors-report.md       ← 유명 투자자 5인 분석 보고서
    ├── 03-personal-strategy-template.md   ← 개인 투자 전략 (작성 예시)
    ├── 03-personal-strategy-blank.md      ← 개인 투자 전략 (빈 템플릿)
    └── 04-strategy-creation-guide.md      ← 전략 수립 프로세스 가이드
```

## 프로젝트 로드맵

1. **Phase 1** (현재): 투자 전략 리서치 및 문서화
   - 주식 투자 전략 중심
   - 유명 투자자 분석
   - 개인 전략 수립
2. **Phase 2** (예정): 자산군 확장
   - 암호화폐 (Cryptocurrency) 전략 추가
   - 부동산 (Real Estate) 전략 추가
3. **Phase 3** (예정): 투자 지원 대시보드 개발
   - 포트폴리오 시각화
   - 자산 배분 추천
   - 벤치마크 비교

## Git 컨벤션

- **기본 브랜치**: `master`
- **커밋 서명**: SSH 서명 활성화
- **언어**: 한국어 중심 (기술 용어는 영어 병기)

## AI 어시스턴트 가이드라인

- 문서는 한국어로 작성하되, 투자 용어는 한국어(영어) 형태로 병기
- `docs/` 디렉토리 내 문서 간 상호 참조 유지
- 새 사용자의 전략 수립 시 `04-strategy-creation-guide.md`의 프로세스를 따른다
- 빈 템플릿(`03-personal-strategy-blank.md`)을 복사하여 사용자별 전략 문서를 생성한다
- 대시보드 개발 시 `03-personal-strategy-template.md`의 JSON 데이터 구조를 참조
- 자산군 확장 시 기존 문서 구조를 유지하며 섹션 추가
