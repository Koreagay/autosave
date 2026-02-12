# Premium Showcase (Flask)

Flask + SQLite 기반 프리미엄 제품 쇼케이스 앱

## 구조

- `app.py` - Flask 메인 앱
- `db.py` - SQLite DB (Python 내장)
- `static/css/main.css` - **전체 스타일 통합 파일** (이 파일만 수정하면 전역 적용)
- `static/js/loader.js` - JS 로더
- `static/js/main.js` - Vanilla JS 앱 로직
- `templates/` - Jinja2 HTML 템플릿

## 실행

```bash
# 가상환경 생성 및 활성화
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 앱 실행 (기본 포트 5000)
python app.py
```

## 기능

- 홈: 제품 그리드, 3D 카드 호버, 상세 다이얼로그
- 어드민 로그인: /admin
- 어드민 대시보드: /admin/dashboard (제품 CRUD, 이미지 드래그앤드롭/URL)
- 404 페이지

## 관리자 계정

- 아이디: `admin1234`
- 비밀번호: `xdayoungx1234`
