# InvestPulse — 투자 지원 대시보드

암호화폐를 실시간 모니터링하고, 기술적 분석 지표(RSI, MACD, Bollinger Bands) 기반 조건 알림을 디스코드로 전송하는 투자 지원 웹 애플리케이션.

## 기술 스택 (Tech Stack)

### Backend
- **FastAPI** — REST API + WebSocket
- **SQLite** (aiosqlite) — 데이터 저장
- **APScheduler** — 주기적 알림 체크
- **pandas + ta** — 기술적 분석 지표 계산
- **httpx** — Upbit API 비동기 통신
- **Discord Webhook** — 알림 발송

### Frontend
- **Vue 3** + TypeScript (Composition API)
- **TradingView Lightweight Charts** — 캔들차트
- **vue-echarts (Apache ECharts)** — 파이차트, 라인차트
- **TanStack Vue Query** — 서버 상태 관리
- **Pinia** — 클라이언트 상태 관리
- **Tailwind CSS** — 다크 테마 스타일링

### 데이터 소스
- **Upbit API** — 암호화폐 시세 (KRW 마켓)

## 빠른 시작 (Quick Start)

### 수동 실행

#### Backend
```bash
cd investpulse/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 필요 시 DISCORD_WEBHOOK_URL 설정
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd investpulse/frontend
npm install
npm run dev
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- API Docs (Swagger): http://localhost:8000/docs

### Docker 실행
```bash
cd investpulse
docker-compose up --build
```

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/health` | 서버 상태 확인 |
| GET | `/api/market/markets` | KRW 마켓 목록 |
| GET | `/api/market/crypto/{symbol}` | 암호화폐 현재가 |
| GET | `/api/market/candles/{symbol}` | 캔들(OHLCV) 데이터 |
| GET | `/api/indicators/{symbol}` | 기술지표 (RSI, MACD, BB) |
| GET | `/api/alerts` | 알림 목록 |
| POST | `/api/alerts` | 알림 생성 |
| PUT | `/api/alerts/{id}` | 알림 수정 |
| DELETE | `/api/alerts/{id}` | 알림 삭제 |
| GET | `/api/portfolio` | 포트폴리오 요약 |
| POST | `/api/portfolio/assets` | 자산 추가 |
| DELETE | `/api/portfolio/assets/{id}` | 자산 삭제 |
| WS | `/ws/market` | 실시간 가격 스트림 |

## 프로젝트 구조

```
investpulse/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 진입점
│   │   ├── config.py         # 환경변수 설정
│   │   ├── database.py       # DB 연결
│   │   ├── routers/          # API 라우터
│   │   ├── services/         # 비즈니스 로직
│   │   ├── models/           # SQLAlchemy 모델
│   │   └── schemas/          # Pydantic 스키마
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/            # 페이지 컴포넌트
│   │   ├── components/       # UI 컴포넌트
│   │   ├── composables/      # Vue 3 Composition API
│   │   ├── stores/           # Pinia 상태관리
│   │   ├── api/              # API 클라이언트
│   │   └── types/            # TypeScript 타입
│   └── package.json
├── docker-compose.yml
└── README.md
```
