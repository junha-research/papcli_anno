# 에세이 평가 도구 (Annotation Tool)

학생 에세이의 언어, 구성, 내용 등 세부 항목(Trait)별로 평가를 수행하고, 평가 점수에 따른 근거 문장을 선택하는 전문 어노테이션 도구입니다.

## 🚀 로컬 실험 실행 방법 (가장 빠른 방법)

로컬에서 개발 및 실험을 위해 각 서버를 직접 실행하는 방법입니다.

### 1. 백엔드 실행 (Terminal 1)
```bash
cd annotation-tool/backend
# 가상환경 활성화 (최초 1회만 venv 생성 필요)
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate  # Windows (CMD)

# 패키지 설치 및 DB 초기화 (최초 1회)
pip install -r requirements.txt
python init_db.py

# 서버 실행
python main.py
```

### 2. 프론트엔드 실행 (Terminal 2)
```bash
cd annotation-tool/frontend
# 패키지 설치 (최초 1회)
npm install

# 개발 서버 실행
npm run dev
```

- **접속 주소**: [http://localhost:5173](http://localhost:5173)
- **테스트 계정**: `annotator1` ~ `annotator4` (비밀번호: `password123`)

---

## ✨ 주요 기능 및 특징

- **좌우 분할 레이아웃 (Split-Screen)**: 왼쪽에서 에세이를 읽고 오른쪽에서 즉시 채점하는 효율적인 UI.
- **인터랙티브 평가**: 평가 항목 선택 시 해당 항목에 대한 문장 선택 모드가 활성화됨.
- **자동 진행률 반영**: 저장 시 즉시 완료 처리되어 대시보드에 반영.
- **상태 유지**: 새로고침 시에도 로그인 정보 및 사용자 프로필 유지.

## 📋 평가 가이드

1. **대시보드**: 할당된 에세이 목록과 진행률 확인.
2. **에세이 상세**: 평가할 항목(언어/구성/내용) 카드 클릭.
3. **점수 및 문장 선택**: 점수를 매기면 필요한 문장 개수가 표시되며, 왼쪽 본문에서 해당 개수만큼 문장 클릭.
4. **저장**: 모든 카드가 초록색(완료)이 되면 "최종 평가 저장" 클릭.

## 🛠 자동화 스크립트 (Windows용)

매번 명령어를 입력하기 번거로울 경우 다음 배치 파일을 사용할 수 있습니다.

- `setup.bat`: 최초 실행 시 환경 구축 (venv 생성, 라이브러리 설치, 빌드 등).
- `start.bat`: 백엔드와 프론트엔드 서버를 동시에 실행.

## 🌐 외부 배포 및 기타 설정

윈도우 공인 IP 환경에서 외부 배포가 필요한 경우 다음 파일을 참고하십시오.
- `DEPLOYMENT.md`: 상세 배포 가이드.
- `configure_external_access.bat`: 외부 접속 IP 설정 도구.

## 📁 프로젝트 구조

```
annotation-tool/
├── backend/              # FastAPI 백엔드 (Port 8000)
│   ├── main.py          # API 엔드포인트
│   ├── init_db.py       # 초기 데이터 생성
│   └── annotation.db    # SQLite DB
└── frontend/            # React + Vite 프론트엔드 (Port 5173)
    ├── src/pages/      # 주요 화면 (Annotate, Dashboard, Login)
    └── src/api/        # API 클라이언트 설정
```
