# 에세이 평가 도구 (Annotation Tool)

학생 에세이의 언어, 구성, 내용 등 세부 항목(Trait)별로 평가를 수행하고, 평가 점수에 따른 근거 문장을 선택하는 전문 어노테이션 도구입니다.

## ✨ 주요 개선 사항 (최근 업데이트)

- **좌우 분할 레이아웃 (Split-Screen)**: 왼쪽 패널에서 에세이를 읽으며 오른쪽 패널에서 즉시 채점할 수 있도록 인터페이스를 개선했습니다.
- **인터랙티브 평가 로직**: 평가 항목(언어, 구성, 내용)을 선택하면 해당 항목에 대한 문장 선택 모드가 활성화됩니다.
- **실시간 진행률 반영**: "최종 평가 저장" 시 대시보드의 진행률(Progress)이 즉시 갱신되도록 로직을 보강했습니다.
- **새로고침 유지**: 페이지를 새로고침해도 로그인 정보와 사용자 이름이 유지됩니다.

## 🚀 로컬 실행 방법

### 1. 필수 프로그램
- **Python 3.9+**
- **Node.js 18+**

### 2. 백엔드 실행 (Terminal 1)
```bash
cd annotation-tool/backend
# 가상환경 활성화 (최초 1회만 venv 생성 필요)
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate  # Windows

# 패키지 설치 및 DB 초기화 (최초 1회)
pip install -r requirements.txt
python init_db.py

# 서버 실행
python main.py
```

### 3. 프론트엔드 실행 (Terminal 2)
```bash
cd annotation-tool/frontend
# 패키지 설치 (최초 1회)
npm install

# 개발 서버 실행
npm run dev
```

접속 주소: [http://localhost:5173](http://localhost:5173)

## 🔑 테스트 계정
- 아이디: `annotator1` ~ `annotator4`
- 비밀번호: `password123`

## 📋 사용 가이드

1. **대시보드**: 할당된 에세이 목록과 현재 진행률을 확인합니다.
2. **에세이 선택**: 평가할 에세이 카드를 클릭하여 상세 페이지로 이동합니다.
3. **평가 수행 (Annotate)**:
   - **우측 패널**에서 평가할 항목(예: 언어)을 클릭합니다.
   - **점수 선택**: 1~5점 중 점수를 선택합니다. 선택한 점수에 따라 필요한 문장 개수가 자동으로 계산됩니다.
   - **문장 선택**: **좌측 패널**의 에세이 본문에서 어색하거나 수정이 필요한 문장을 클릭하여 선택합니다.
   - **상태 확인**: 문장 개수가 충족되면 카드 색상이 초록색으로 변경됩니다.
4. **저장**: 모든 항목 평가 완료 후 "최종 평가 저장" 버튼을 클릭합니다.

## 📁 프로젝트 구조

```
annotation-tool/
├── backend/              # FastAPI 백엔드
│   ├── main.py          # API 엔드포인트 및 로직
│   ├── models.py        # SQLAlchemy DB 모델
│   ├── init_db.py       # 초기 데이터 생성 스크립트
│   └── annotation.db    # SQLite 데이터베이스 (자동 생성)
└── frontend/            # React + Vite 프론트엔드
    ├── src/
    │   ├── pages/      # 주요 화면 (Annotate, Dashboard, Login)
    │   ├── api/        # Axios API 클라이언트
    │   └── store/      # Zustand 상태 관리 (Auth)
    └── App.tsx         # 라우팅 설정
```

## ⚠️ 주의사항
- 본 프로젝트는 현재 로컬 실험 환경에 최적화되어 있습니다.
- 공인 IP를 통한 배포를 시도할 경우, `frontend/src/api/client.ts`의 `API_BASE_URL`을 서버 IP로 수정하고 빌드해야 합니다.