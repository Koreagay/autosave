========================================
  업로드 폴더 사용법 (이 폴더만으로 GitHub 업로드)
========================================

■ 이 폴더 하나만 있으면 됩니다 (autosave 등 다른 폴더 불필요).

■ 사용 방법
  1. apk 폴더 → 올릴 .apk 파일 넣기
  2. windows 폴더 → 올릴 .exe 등 윈도우용 파일 넣기
  3. upload.py 더블클릭
  4. 이 폴더가 GitHub 레포로 push 됨 (100MB 넘는 파일도 LFS로 업로드)

■ 처음 사용할 때 (Git 레포 연결)
  방법 1: GitHub에서 레포 만든 뒤 이 폴더를 clone 해서 사용
  방법 2: 이 폴더에서 시작하려면 upload.py를 연 뒤
          상단 GITHUB_REPO_URL = "" 부분에 GitHub 레포 URL 입력
          (예: https://github.com/사용자/레포이름.git)
          저장 후 upload.py 실행 → 자동으로 git init & 원격 연결

■ 100MB 넘는 파일
  - Git LFS가 필요합니다.
  - 설치: https://git-lfs.com 에서 다운로드 후 설치
  - 한 번만: 터미널에서 git lfs install 실행

■ apk / windows 폴더가 없으면
  - upload.py 실행 시 자동으로 만들어집니다.
