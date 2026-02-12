# 🚀 Auto Backup System

> Automated GitHub Backup Pipeline  
> 로컬 데이터를 안전하게 GitHub 저장소에 자동 백업하는 시스템

---

## 📌 Overview

이 프로젝트는 로컬 파일을 자동으로 감지하고,  
변경 사항을 GitHub 저장소에 자동으로 커밋 및 푸시하는  
**완전 자동 백업 시스템**입니다.

반복적인 수동 백업 과정을 제거하고,  
데이터 무결성과 안정성을 유지하도록 설계되었습니다.

---

## ⚙️ Key Features

- 🔄 자동 변경 감지 (File Change Detection)
- 📦 자동 Git Add / Commit / Push
- 🕒 주기적 실행 (Scheduler 기반)
- 📜 자동 커밋 메시지 생성 (Timestamp 기반)
- 🛡 예외 처리 및 오류 방지 로직 포함
- 💻 경량화된 구조 (Low Overhead)

---

## 🏗 System Architecture

```text
[Local Directory]
        │
        ▼
[Change Detection Script]
        │
        ▼
[Git Staging]
        │
        ▼
[Auto Commit]
        │
        ▼
[GitHub Remote Repository]
```

---

## 🛠 Tech Stack

- Shell Script / Python (자동화 스크립트)
- Git CLI
- GitHub Repository
- Task Scheduler / Cron

---

## 🔧 How It Works

1. 로컬 디렉토리 변경 사항 감지
2. 변경 파일 자동 스테이징
3. 현재 시간 기반 커밋 메시지 생성
4. 원격 저장소로 자동 푸시

---

## ▶ Usage

```bash
# 실행
./auto_backup.sh
```

또는 (Python 기반일 경우)

```bash
python auto_backup.py
```

---

## 📅 Commit Format

```
[Auto Backup] YYYY-MM-DD HH:MM:SS
```

예시:

```
[Auto Backup] 2026-02-13 08:15:23
```

---

## 🎯 Purpose

- 로컬 데이터 영구 보존
- 버전 관리 자동화
- 휴먼 에러 최소화
- 개발 생산성 향상

---

## 📌 Future Improvements

- Slack / Discord 알림 연동
- 백업 로그 시각화
- 클라우드 다중 백업 지원
- 변경 파일 요약 자동 생성

---

## 🧠 Philosophy

> "Backup should be invisible, automatic, and reliable."

자동화는 선택이 아니라 기본입니다.

---

## 📄 License

MIT License
