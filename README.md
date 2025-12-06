# 🎬 Shorts Maker

숏폼 영상 제작을 위한 Streamlit 기반 애플리케이션입니다.

---

## � 빠른 시작 가이드

### ✅ 사용 방법

1. **VS Code, Cursor** 또는 다른 에디터에서 해당 폴더를 엽니다
2. 터미널에서 아래 **"설치 및 실행 방법"** 순서대로 명령어를 실행합니다
3. 브라우저가 자동으로 열리며, 웹 인터페이스가 나타납니다
4. 웹사이트에서 제목/본문 입력 → 배경 선택 → 스타일 설정 → 영상 생성!

> 💡 **Tip:** 첫 실행 시 패키지 설치에 1~2분 정도 소요될 수 있습니다.

---

## �📝 설치 및 실행 방법

### 1. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows)
venv\Scripts\activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. Streamlit 실행

```bash
streamlit run app.py
```

실행 후 브라우저에서 자동으로 열리며, 숏폼 영상을 제작할 수 있습니다.

---

## 📦 필요 패키지

- streamlit
- moviepy==1.0.3
- pillow
- numpy<2.0.0
- st-click-detector

---

## 🎨 주요 기능

- ✍️ 제목 및 본문 텍스트 입력
- 🖼 배경 이미지/동영상 선택
- 🎨 폰트, 색상, 크기 커스터마이징
- 🎵 배경 음악 추가
- 📱 인스타그램/유튜브 Shorts용 세로 영상 (1080x1920)
- 🎬 실시간 미리보기 및 영상 생성

---

## 💡 더 많은 자동화 기능이 필요하신가요?

이 프로젝트는 기본적인 숏폼 영상 제작 기능만 제공합니다.

**AI API 연동 + YouTube 자동 업로드 (GCP 연동) = 완전 자동화**를 원하신다면,  
**godud2604@gmail.com**으로 문의해주세요!

📧 **완전 자동화를 위한 기능:**
- AI (gpt, gemini, claude) 를 통한 자동 대본 생성 기능
- YouTube API를 통한 자동 업로드 및 스케줄링

