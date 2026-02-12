# autosave 레포에 자동 백업 설정하기

## 1. 한 번만 할 일 (Git 설정)

### 1-1. autosave 레포 클론하기

**방법 A: 아직 GitHub에 autosave 레포를 안 만들었다면**

1. GitHub에서 새 저장소 생성: 이름 `autosave`, **Public 또는 Private** (아래 "프라이빗 레포 쓰기" 참고)
2. 아래처럼 **상위 폴더**에서 클론 (게이섹스 폴더와 같은 위치에 두기):

```powershell
cd "C:\Users\codelounge\Desktop"
git clone https://github.com/Koreagay/autosave.git
cd autosave
```

**방법 B: 이미 만든 레포가 있다면**

```powershell
cd "C:\Users\codelounge\Desktop"
git clone https://github.com/Koreagay/autosave.git
cd autosave
```

### 1-2. backup 폴더 만들고 첫 커밋

```powershell
# autosave 폴더 안에서
mkdir backup
echo. > backup\.gitkeep
git add backup
git commit -m "Add backup folder"
git branch -M main
git remote add origin https://github.com/Koreagay/autosave.git
# 이미 origin이 있으면: git remote set-url origin https://github.com/Koreagay/autosave.git
git push -u origin main
```

이후 백업 스크립트가 `autosave/backup` 안에 이 프로젝트 파일들을 복사하고, 여기서 `git add` → `commit` → `push` 하면 됩니다.

---

## 2. 자동 백업 사용법

### 2-1. 패키지 설치 (최초 1회)

Python 자동 백업 스크립트는 `watchdog` 패키지를 사용합니다.

```bash
pip install watchdog
```

또는 프로젝트 의존성 설치:

```bash
pip install -r requirements.txt
```

### 2-2. 경로 설정

`autobackup.py`는 **이 스크립트가 있는 폴더**를 프로젝트 루트로 보고,  
그 **상위 폴더 안의 `autosave`** 를 백업 레포로 사용합니다.

- **백업 대상:** `autobackup.py`가 있는 폴더 (실제 사용 경로: `C:\Users\codelounge\Desktop\게이섹스`)
- **백업 위치:** `autosave\backup` (게이섹스와 같은 위치의 `autosave` 폴더 안 → `C:\Users\codelounge\Desktop\autosave\backup`)

autosave를 다른 경로에 두었다면 `autobackup.py` 안의 `AUTOSAVE_ROOT` 를 수정하세요.

### 2-3. 자동 백업 실행

**방법 1: 더블클릭**  
`autobackup.py` 파일을 더블클릭하면 자동 백업이 켜집니다.

**방법 2: 터미널에서**

```bash
cd "C:\Users\codelounge\Desktop\게이섹스"
python autobackup.py
```

실행하면 파일 감시가 켜지고, 저장할 때마다 약 3초 후 백업 → 커밋 → 푸시까지 진행됩니다.  
종료하려면 콘솔에서 `Ctrl+C` 를 누르세요.

### 2-4. GitHub 인증 (프라이빗 레포는 필수)

`git push`가 되려면 GitHub 인증이 필요합니다. **프라이빗 레포**는 반드시 아래 중 하나를 설정해야 합니다.

- **HTTPS + Personal Access Token (PAT):**  
  GitHub → Settings → Developer settings → Personal access tokens 에서 토큰 생성 후,  
  push 할 때 비밀번호 대신 토큰 입력. Windows에서는 자격 증명 관리자에 저장되면 다음부터 자동 입력됩니다.
- **SSH:**  
  `git remote set-url origin git@github.com:Koreagay/autosave.git` 로 바꾼 뒤,  
  GitHub에 SSH 키 등록해 두면 별도 비밀번호 없이 push 가능합니다.

한 번만 설정해 두면 이후에는 스크립트가 자동으로 push까지 합니다.

---

## 3. 프라이빗(Private) 레포로 쓰기

백업을 남에게 보이지 않게 하려면 **autosave 레포를 Private**으로 두면 됩니다.

### 3-1. 레포를 프라이빗으로 설정

1. GitHub에서 **autosave** 저장소 페이지로 이동
2. **Settings** 탭 클릭
3. 맨 아래 **Danger Zone** → **Change repository visibility** → **Change to private** 선택 후 확인

이미 만든 레포를 나중에 Public ↔ Private 으로 바꿔도 되고, 새로 만들 때 **Private**으로 생성해도 됩니다.

### 3-2. 프라이빗일 때 꼭 할 일: 인증

프라이빗 레포는 **본인 계정으로 인증**해야만 push 할 수 있습니다.

- **HTTPS 사용 중이면:**  
  `git push` 할 때 GitHub **사용자명 + 비밀번호** 대신 **Personal Access Token(PAT)** 을 비밀번호 자리에 입력해야 합니다.  
  (일반 비밀번호는 2021년부터 사용 불가.)
- **SSH 사용 중이면:**  
  SSH 키를 GitHub 계정에 등록해 두면 별도 설정 없이 push 가능합니다.

자동 백업 스크립트(`autobackup.py`)는 그대로 두고, 위 인증만 맞춰 주면 프라이빗 레포에도 정상적으로 백업됩니다.

---

## 4. 방법 A: HTTPS + Personal Access Token (PAT) 자세히

프라이빗 레포에 push하려면 **비밀번호 대신 토큰**을 써야 합니다. 아래 순서대로 하면 됩니다.

### 4-1. GitHub에서 토큰 만들기

1. **GitHub 웹사이트 로그인** 후, 우측 상단 **프로필 사진** 클릭  
   → **Settings** 클릭 (계정 설정 페이지로 이동).

2. 왼쪽 맨 아래 **Developer settings** 클릭.

3. 왼쪽 메뉴에서 **Personal access tokens** → **Tokens (classic)** 선택.  
   (Fine-grained tokens 말고 **Classic** 쪽 사용.)

4. **Generate new token** → **Generate new token (classic)** 클릭.

5. **Note**에 아무 이름 입력 (예: `autosave backup`).  
   **Expiration**은 원하는 기간 선택 (예: 90 days, No expiration 등).

6. **Select scopes**에서 **repo** 하나만 체크.  
   (체크하면 하위 항목이 전부 선택됩니다. 이걸로 push 가능.)

7. 맨 아래 **Generate token** 클릭.

8. **생성된 토큰이 한 번만 표시**됩니다.  
   초록색 문자열 `ghp_xxxxxxxxxxxx` 를 **복사**해 두세요.  
   나중에 다시 볼 수 없으니 메모장 등에 잠깐 붙여넣어 두거나, 바로 다음 단계에서 쓸 준비를 하세요.

---

### 4-2. 토큰으로 한 번 push 해 보기 (자격 증명 저장)

한 번이라도 **토큰을 비밀번호 자리에 입력**해 두면, Windows는 보통 **자격 증명 관리자**에 저장해서 다음부터는 자동으로 씁니다. 그래서 autobackup.py가 push할 때도 그대로 동작합니다.

1. **PowerShell** 또는 **명령 프롬프트**를 연다.

2. autosave 폴더로 이동한 뒤 push를 시도한다.

   ```powershell
   cd "C:\Users\codelounge\Desktop\autosave"
   git push
   ```

3. **Username for 'https://github.com':**  
   → GitHub **아이디** 입력 후 Enter.

4. **Password for 'https://아이디@github.com':**  
   → **GitHub 비밀번호가 아니라**, 아까 복사한 **토큰(ghp_xxxx...)** 을 붙여넣기 후 Enter.  
   (입력해도 화면에 안 보이는 게 정상입니다.)

5. 이때 **자격 증명 관리자에 저장**하겠냐고 나오면 **예** 하면, 다음부터는 `git push` 할 때마다 (autobackup.py 포함) 자동으로 인증됩니다.

6. `git push` 가 성공하면 설정 끝입니다.  
   이제 `autobackup.py` 더블클릭해서 자동 백업해도 push가 됩니다.

---

### 4-3. 이미 비밀번호를 저장해 둔 경우 (push가 안 될 때)

예전에 GitHub **비밀번호**를 저장해 두었다면, 그걸 쓰다가 push가 거절될 수 있습니다. 그때는 저장된 자격 증명을 **토큰으로 바꿔 주면** 됩니다.

1. **Windows 검색**에서 **자격 증명 관리자** (Credential Manager) 검색 후 실행.

2. **Windows 자격 증명** 탭 클릭.

3. 목록에서 **git:https://github.com** 항목 찾기  
   → 클릭 후 **편집** (또는 **제거** 후 다음 push 때 다시 입력).

4. **편집**이면:  
   **암호** 칸에 GitHub 비밀번호를 지우고, 새로 만든 **토큰(ghp_xxxx...)** 을 붙여넣고 저장.

5. **제거**했으면:  
   터미널에서 `cd autosave` 후 `git push` 한 번 더 실행해서,  
   Username에는 GitHub 아이디, Password에는 **토큰** 입력해 주면 다시 저장됩니다.

---

### 4-4. 정리

| 단계 | 할 일 |
|------|--------|
| 1 | GitHub → Settings → Developer settings → Personal access tokens (classic) |
| 2 | Generate new token (classic) → Note 입력, **repo** 체크 → Generate token |
| 3 | 토큰(`ghp_...`) 복사 |
| 4 | 터미널에서 `autosave` 폴더로 가서 `git push` → Username: GitHub 아이디, Password: **토큰** 입력 |
| 5 | 자격 증명 저장하면, 이후 autobackup.py가 push할 때도 자동 인증 |

토큰은 **비밀번호처럼 다루기**: 남에게 보여 주지 말고, 공개된 곳에 붙여넣지 마세요.

---

## 요약 체크리스트

**프로젝트 위치:** `C:\Users\codelounge\Desktop\게이섹스`

- [ ] `C:\Users\codelounge\Desktop` 에 `autosave` 레포 클론
- [ ] `autosave` 안에 `backup` 폴더 만들고 커밋 후 `git push`
- [ ] `pip install watchdog` (또는 `pip install -r requirements.txt`)
- [ ] `게이섹스` 폴더에서 `autobackup.py` 더블클릭 또는 `python autobackup.py` 로 자동 백업 시작
