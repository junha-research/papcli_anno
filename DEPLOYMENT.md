# 윈도우 PC 외부 접속 배포 가이드

## 📋 사전 준비
- 윈도우 PC (24시간 가동 가능)
- 공인 IP 주소
- Git 설치
- Python 3.9+ 설치
- Node.js 18+ 설치

## 🔧 1. 프로젝트 설치

### Git Clone
```bash
git clone https://github.com/junha-research/papcli_anno.git
cd papcli_anno
```

## 🖥️ 2. Backend 설정

### 가상환경 생성 및 패키지 설치
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 데이터베이스 초기화
```bash
python init_db.py
```

### Backend 실행 (모든 IP에서 접속 허용)
```bash
# main.py를 직접 실행하거나
python main.py

# 또는 uvicorn으로 실행
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🎨 3. Frontend 설정

### 환경 변수 설정
`frontend/.env` 파일 생성:
```
VITE_API_URL=http://YOUR_PUBLIC_IP:8000/api
```

예시:
```
VITE_API_URL=http://123.45.67.89:8000/api
```

### 패키지 설치 및 빌드
```bash
cd ..\frontend
npm install
npm run build
```

### Frontend 실행 (프로덕션 모드)
```bash
npm run preview -- --host 0.0.0.0 --port 4173
```

## 🌐 4. 공유기 포트포워딩 설정

### 공유기 관리 페이지 접속
- 주소: `192.168.0.1` 또는 `192.168.1.1` (공유기마다 다름)
- 로그인 (관리자 계정)

### 포트포워딩 규칙 추가
**설정 위치:** 고급 설정 > NAT/라우터 관리 > 포트포워딩

| 서비스 이름 | 외부 포트 | 내부 IP | 내부 포트 | 프로토콜 |
|-----------|---------|---------|---------|---------|
| Backend API | 8000 | 윈도우PC의 로컬IP | 8000 | TCP |
| Frontend | 4173 | 윈도우PC의 로컬IP | 4173 | TCP |

**윈도우 PC 로컬 IP 확인:**
```bash
ipconfig
```
예: `192.168.0.100`

## 🔒 5. 윈도우 방화벽 설정

### PowerShell 관리자 권한으로 실행
```powershell
# Backend 포트 열기
netsh advfirewall firewall add rule name="Annotation Backend" dir=in action=allow protocol=TCP localport=8000

# Frontend 포트 열기
netsh advfirewall firewall add rule name="Annotation Frontend" dir=in action=allow protocol=TCP localport=4173
```

## 🚀 6. 접속 테스트

### 공인 IP 확인
- https://www.whatismyip.com 접속
- 예: `123.45.67.89`

### 접속 주소
- **Frontend**: `http://YOUR_PUBLIC_IP:4173`
- **Backend API Docs**: `http://YOUR_PUBLIC_IP:8000/docs`

### 테스트 계정
- `annotator1` / `password123`
- `annotator2` / `password123`
- `annotator3` / `password123`
- `annotator4` / `password123`

## ⚙️ 7. 자동 시작 설정 (선택사항)

### Backend 자동 시작
1. `start_backend.bat` 파일 생성:
```batch
@echo off
cd C:\path\to\papcli_anno\backend
call venv\Scripts\activate
python main.py
```

2. 작업 스케줄러에 등록 (시스템 시작 시 실행)

### Frontend 자동 시작
1. `start_frontend.bat` 파일 생성:
```batch
@echo off
cd C:\path\to\papcli_anno\frontend
npm run preview -- --host 0.0.0.0 --port 4173
```

2. 작업 스케줄러에 등록

## 📊 8. 데이터 관리

### 데이터 위치
- SQLite 데이터베이스: `backend/annotation.db`

### 데이터 백업
```bash
# 정기적으로 annotation.db 파일 복사
copy backend\annotation.db backup\annotation_backup_20260206.db
```

### 데이터 내보내기 (Python)
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('backend/annotation.db')
annotations = pd.read_sql_query("SELECT * FROM annotations", conn)
annotations.to_csv('annotations_export.csv', index=False)
conn.close()
```

## ⚠️ 주의사항

### 보안
- 현재 HTTP 사용 중 (HTTPS 권장)
- 강력한 비밀번호 사용 권장
- 필요시 IP 화이트리스트 설정

### 전력 관리
- 윈도우 절전 모드 해제
- 디스플레이만 끄기 설정

### 네트워크
- 공인 IP가 변경될 수 있음 (DDNS 사용 권장)
- 일부 ISP는 특정 포트 차단 가능

## 🔧 문제 해결

### Backend가 실행되지 않을 때
```bash
# 포트 사용 확인
netstat -ano | findstr :8000

# 프로세스 종료
taskkill /PID <PID> /F
```

### Frontend가 Backend에 연결되지 않을 때
- `.env` 파일의 `VITE_API_URL` 확인
- CORS 설정 확인 (`main.py`)
- 방화벽 설정 확인

### 외부에서 접속되지 않을 때
- 공유기 포트포워딩 설정 확인
- 공인 IP 주소 확인
- ISP 포트 차단 여부 확인
