  ## 폴더 구조

  ```
  backend/      # FastAPI 백엔드 (Python)
  frontend/     # React 프론트엔드 (Vite + TypeScript)
  package.json  # 통합 실행 스크립트
  ```

  ## 실행 방법

  ### 1. 레포 클론

  ```bash
  git clone https://github.com/WooAhHeyoung/FULL.git
  cd FULL
  ```

  ### 2. 백엔드 환경변수 설정

  ```bash
  cp backend/.env_example backend/.env
  ```

  `backend/.env` 파일을 열어서 `UPSTAGE_API_KEY` 에 실제 키를 입력합니다.

  ```
  UPSTAGE_API_KEY=여기에_키_입력
  USE_FAKE_UPSTAGE=false
  ```

  > API 키가 없으면 `USE_FAKE_UPSTAGE=true` 로 설정하면 더미 데이터로 테스트
  가능합니다.

  ### 3. Python 패키지 설치

  ```bash
  cd backend
  python -m venv .venv
  source .venv/bin/activate    # Windows: .venv\Scripts\activate
  pip install -r requirements.txt
  cd ..
  ```

  ### 4. npm 패키지 설치

  ```bash
  npm install
  npm --prefix frontend install
  ```

  ### 5. 실행

  ```bash
  npm run dev        # 더미 데이터 모드 (API 키 불필요)
  npm run dev:real   # 실제 Upstage API 사용
  
  http://localhost:5173
  ```
  
