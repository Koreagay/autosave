# -*- coding: utf-8 -*-
"""
이 폴더만으로 GitHub에 업로드 (autosave 등 별도 폴더 불필요).
100MB 넘는 파일은 Git LFS로 업로드됩니다. 더블클릭으로 실행.
"""

import os
import sys
import subprocess

# 이 스크립트가 있는 폴더 = Git 레포 루트 (이 폴더 하나만 있으면 됨)
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# 업로드할 하위 폴더 (여기에 파일 넣으면 이 폴더에서 그대로 push)
UPLOAD_FOLDERS = ["apk", "windows"]

# Git LFS로 추적할 확장자 (100MB 넘어도 GitHub 업로드 가능)
LFS_EXTENSIONS = [".apk", ".xapk", ".exe", ".msi", ".zip", ".rar", ".7z", ".iso", ".dmg", ".pkg"]

# 이 폴더가 아직 Git 레포가 아닐 때 사용할 원격 URL (비어 있으면 기존 origin 사용)
# 새로 시작할 때: 여기에 GitHub 레포 URL 입력 (예: https://github.com/사용자/레포.git)
GITHUB_REPO_URL = "https://github.com/Koreagay/autosave"

# GitHub 푸시용 Personal Access Token (있으면 여기에 넣으면 로그인 없이 푸시됨)
# 만들기: GitHub → 설정 → Developer settings → Personal access tokens
GITHUB_TOKEN = ""

# Git에 "누가 커밋했는지" 표시용. 비어 있으면 이미 설정된 값 사용.
# 처음 한 번만 설정하면 됨 (이 폴더 또는 전역에 저장됨)
GIT_USER_NAME = ""
GIT_USER_EMAIL = ""


def run(cmd, cwd=None, check=True, capture=True):
    """capture=False 면 터미널에 진행률·속도 등이 실시간 출력됨."""
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        r = subprocess.run(
            cmd,
            cwd=cwd or REPO_ROOT,
            capture_output=capture,
            text=True,
            shell=False,
            creationflags=flags,
        )
    except FileNotFoundError:
        print("[오류] Git을 찾을 수 없습니다.")
        print("  1. https://git-scm.com 에서 Git 설치 (Windows용)")
        print("  2. 설치 시 'Add Git to PATH' 옵션 선택")
        print("  3. 설치 후 명령 프롬프트/터미널을 다시 연 뒤 이 스크립트 실행")
        raise SystemExit(1)
    if check and r.returncode != 0:
        msg = r.stderr or r.stdout or f"exit {r.returncode}"
        if not msg and not capture:
            msg = "명령 실패 (위 터미널 메시지 참고)"
        raise RuntimeError(msg)
    return r


def ensure_folders():
    """apk, windows 폴더가 없으면 생성."""
    for name in UPLOAD_FOLDERS:
        path = os.path.join(REPO_ROOT, name)
        os.makedirs(path, exist_ok=True)
    print("[확인] 폴더: apk, windows (여기에 넣은 파일이 올라갑니다.)")


def ensure_git_user():
    """Git 사용자 이름/이메일이 없으면 설정 (커밋 시 필요)."""
    r1 = run(["git", "config", "user.name"], check=False, capture=True)
    r2 = run(["git", "config", "user.email"], check=False, capture=True)
    name_ok = (r1.stdout or "").strip()
    email_ok = (r2.stdout or "").strip()
    if name_ok and email_ok:
        return
    if GIT_USER_NAME.strip() and GIT_USER_EMAIL.strip():
        run(["git", "config", "user.name", GIT_USER_NAME.strip()])
        run(["git", "config", "user.email", GIT_USER_EMAIL.strip()])
        print(f"[확인] 이 폴더 Git 사용자: {GIT_USER_NAME.strip()} / {GIT_USER_EMAIL.strip()}")
        return
    print("[오류] Git이 당신을 인식하려면 이름과 이메일이 필요합니다.")
    print("  방법 1: upload.py 상단에 GIT_USER_NAME, GIT_USER_EMAIL 입력 후 다시 실행")
    print("  방법 2: 명령 프롬프트에서 이 폴더로 이동 후")
    print("          git config user.name \"내이름\"")
    print("          git config user.email \"내이메일@예시.com\"")
    input("엔터를 누르면 종료합니다...")
    sys.exit(1)


def _remote_url_with_token(url):
    """원격 URL에 토큰이 있으면 푸시 시 인증에 사용되도록 URL 반환."""
    if not (GITHUB_TOKEN and url and "github.com" in url):
        return url
    # https://github.com/user/repo.git → https://TOKEN@github.com/user/repo.git
    if "://" in url:
        after_protocol = url.split("://", 1)[1]
        if "@" in after_protocol:
            after_protocol = after_protocol.split("@", 1)[1]  # user@github.com/... → github.com/...
        return "https://" + GITHUB_TOKEN.strip() + "@" + after_protocol
    return url


def ensure_git_repo():
    """이 폴더가 Git 레포가 아니면 init, 원격이 없으면 GITHUB_REPO_URL로 설정. 토큰 있으면 푸시용 URL로 설정."""
    git_dir = os.path.join(REPO_ROOT, ".git")
    if not os.path.isdir(git_dir):
        run(["git", "init"])
        print("[확인] Git 저장소를 이 폴더에 초기화했습니다.")
    try:
        r = run(["git", "remote", "get-url", "origin"], check=True, capture=True)
        current_url = (r.stdout or "").strip()
        if GITHUB_TOKEN.strip() and current_url:
            push_url = _remote_url_with_token(current_url)
            if push_url != current_url:
                run(["git", "remote", "set-url", "origin", push_url])
                print("[확인] GitHub 토큰으로 푸시 설정됨.")
    except Exception:
        if GITHUB_REPO_URL.strip():
            url = _remote_url_with_token(GITHUB_REPO_URL.strip())
            run(["git", "remote", "add", "origin", url])
            print(f"[확인] 원격 저장소 설정: {GITHUB_REPO_URL.strip()}")
            if GITHUB_TOKEN.strip():
                print("[확인] GitHub 토큰으로 푸시 설정됨.")
        else:
            print("[오류] 원격 저장소(origin)가 없습니다.")
            print("  방법 1: 이 폴더를 먼저 clone 한 뒤 사용")
            print("  방법 2: upload.py 상단 GITHUB_REPO_URL 에 GitHub 레포 URL 입력 후 다시 실행")
            input("엔터를 누르면 종료합니다...")
            sys.exit(1)


def ensure_lfs():
    """이 폴더 레포에 Git LFS 설정 (대용량 파일용)."""
    run(["git", "lfs", "install"], check=False)
    for ext in LFS_EXTENSIONS:
        run(["git", "lfs", "track", f"*{ext}"], check=False)
    run(["git", "add", ".gitattributes"], check=False)


def has_files_to_upload():
    """apk, windows 안에 올릴 파일이 있는지 확인."""
    for name in UPLOAD_FOLDERS:
        path = os.path.join(REPO_ROOT, name)
        if not os.path.isdir(path):
            continue
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)):
                return True
    return False


def format_size(n):
    """바이트를 읽기 쉬운 크기 문자열로."""
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} TB"


def list_staged_with_size():
    """스테이징된 파일 목록과 총 크기 반환 (업로드 예정 표시용)."""
    r = run(["git", "diff", "--cached", "--name-only"], capture=True)
    names = (r.stdout or "").strip().splitlines()
    total = 0
    for path in names:
        full = os.path.join(REPO_ROOT, path)
        if os.path.isfile(full):
            total += os.path.getsize(full)
    return names, total


def upload():
    """이 폴더 내용을 Git LFS 포함해 commit & push."""
    ensure_folders()
    ensure_git_repo()
    ensure_git_user()

    try:
        ensure_lfs()
    except Exception as e:
        err = str(e).lower()
        print(f"[경고] Git LFS 설정 중: {e}")
        if "git lfs" in err or "not found" in err or "not recognized" in err:
            print("\n100MB 넘는 파일을 올리려면 Git LFS 설치가 필요합니다.")
            print("1. https://git-lfs.com 접속 → 다운로드 후 설치")
            print("2. 설치 후 터미널에서 한 번 실행: git lfs install")
            print("3. upload.py 다시 실행")
            input("엔터를 누르면 종료합니다...")
            sys.exit(1)

    if not has_files_to_upload():
        print("[안내] apk, windows 폴더에 올릴 파일이 없습니다. 파일을 넣은 뒤 다시 실행하세요.")
        input("엔터를 누르면 종료합니다...")
        return

    try:
        run(["git", "add", ".gitattributes"], check=False)
        run(["git", "add", "."])
        r = run(["git", "status", "--short"], capture=True)
        if not (r.stdout and r.stdout.strip()):
            print("[안내] 변경된 파일이 없습니다 (이미 동일한 상태).")
            input("엔터를 누르면 종료합니다...")
            return
        # 업로드 예정 파일 목록·총 크기 표시
        names, total = list_staged_with_size()
        print("\n[업로드 예정]")
        for name in names:
            full = os.path.join(REPO_ROOT, name)
            sz = format_size(os.path.getsize(full)) if os.path.isfile(full) else "-"
            print(f"  {name}  ({sz})")
        print(f"  총 크기: {format_size(total)}\n")
        run(["git", "commit", "-m", "Upload apk and windows files (LFS)"])
        print("[푸시 중] 아래에 진행률·업로드 속도가 표시됩니다.\n")
        run(["git", "push", "--progress", "-u", "origin", "HEAD"], capture=False)
        print("\n[완료] GitHub에 업로드되었습니다.")
    except Exception as e:
        print(f"[오류] git 실패: {e}")
    input("엔터를 누르면 종료합니다...")


if __name__ == "__main__":
    exit_code = 0
    try:
        upload()
    except SystemExit as e:
        exit_code = e.code if isinstance(getattr(e, "code", None), int) else 1
    except Exception as e:
        import traceback
        print("\n[예기치 않은 오류]")
        traceback.print_exc()
        print("\n", e)
    finally:
        input("\n엔터를 누르면 종료합니다...")
    if exit_code != 0:
        sys.exit(exit_code)
