import base64
import os
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps

# 외부 라이브러리
from st_click_detector import click_detector
from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    CompositeVideoClip,
    VideoFileClip,
    concatenate_videoclips,
    vfx,
)

# Pillow 패치 (최신 버전 호환성)
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# ==========================================
# 1. 초기 설정 및 CSS
# ==========================================
st.set_page_config(page_title="Shorts Maker", layout="centered", page_icon="📱")

def apply_custom_style():
    st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        html, body, [class*="css"] {
            font-family: 'Pretendard', sans-serif;
        }
        
        .block-container {
            max-width: 500px !important;
            padding-top: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-bottom: 5rem !important;
            margin: 0 auto !important;
        }
                
        .element-container, div[data-testid="stElementContainer"] {
            width: 100% !important;
            min-width: 100% !important;
        }
        
        /* 헤더 스타일 */
        .main-header {
            text-align: center;
            margin-bottom: 20px;
            padding: 10px;
        }
        .main-header h1 {
            font-size: 1.6rem;
            font-weight: 800;
            color: #333;
            margin: 0;
        }

        /* 토글(Expander) 디자인 */
        div[data-testid="stExpander"] {
            background-color: white;
            border-radius: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            border: 1px solid #f0f0f0;
            margin-bottom: 24px;
            overflow: hidden;
        }
        div[data-testid="stExpander"] > details > summary {
            font-weight: 700;
            font-size: 1.05rem;
            color: #333;
            padding: 18px 20px;
            border-bottom: 1px solid #f8f8f8;
        }
        div[data-testid="stExpander"] > details > div {
            padding: 20px 20px 28px 20px;
        }

        /* 구분선 UI */
        .styled-hr {
            border: 0;
            height: 1px;
            background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0));
            margin: 25px 0;
        }

        /* 섹션 제목 */
        .section-header {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 20px;
            color: #333;
            display: flex;
            align-items: center;
        }
        .section-header span {
            margin-right: 8px;
            font-size: 1.2rem;
        }
        
        /* 소제목 라벨 스타일 */
        .sub-label {
            font-size: 0.95rem;
            font-weight: 700;
            color: #444;
            margin-bottom: 12px;
            display: block;
        }
        
        /* 버튼 스타일 통합 (생성 버튼 + 다운로드 버튼) */
        div.stButton, div.stDownloadButton {
            width: 100% !important;
            padding: 0 !important;
            margin-top: 20px !important;
        }
        
        div.stButton > button, div.stDownloadButton > button {
            width: 100% !important;
            display: block !important;
            border-radius: 16px;
            height: 58px;
            background: linear-gradient(135deg, #4A00E0 0%, #8E2DE2 100%) !important;
            color: white !important;
            font-weight: 700;
            font-size: 1.15rem;
            border: none !important;
            box-shadow: 0 6px 15px rgba(74, 0, 224, 0.25) !important;
            transition: all 0.2s ease-in-out;
        }
        div.stButton > button:hover, div.stDownloadButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(74, 0, 224, 0.35) !important;
            color: white !important;
        }
        div.stButton > button:active, div.stDownloadButton > button:active {
            transform: scale(0.98);
            color: white !important;
            background: linear-gradient(135deg, #4A00E0 0%, #8E2DE2 100%) !important;
        }
        div.stDownloadButton > button:focus {
             box-shadow: 0 8px 20px rgba(74, 0, 224, 0.35) !important;
             color: white !important;
        }

        /* 입력창 디자인 */
        .stTextInput > div > div > input, .stTextArea > div > div > textarea {
            background-color: #f9f9f9;
            border-radius: 12px;
            border: 1px solid #eee;
            color: #333;
            padding: 12px;
        }
        .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
            background-color: #fff;
            border-color: #8E2DE2;
            box-shadow: 0 0 0 1px #8E2DE2;
        }
        
        /* 코드 블록 스타일 (프롬프트 복사용) */
        .stCode {
            border-radius: 10px;
        }

        /* 스트림릿 기본 툴바(깃허브/쉐어 등) 숨김 */
        [data-testid="stToolbar"] { 
            display: none !important; 
        }
        [data-testid="stDecoration"] {
            display: none !important;
        }
        [data-testid="stStatusWidget"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# 경로 설정
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
FONT_DIR = os.path.join(ROOT_DIR, "fonts")
VIDEO_DIR = os.path.join(ROOT_DIR, "video")
THUMB_DIR = os.path.join("temp", "thumbs")
DEFAULT_MUSIC = os.path.join(ROOT_DIR, "music", "just-relax-11157.mp3")

os.makedirs("temp", exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)

# 상수
VIDEO_WIDTH, VIDEO_HEIGHT = 1080, 1920
DEFAULT_LINE_DURATION = 2.5

AVAILABLE_FONTS = {
    "Gmarket Sans Bold": os.path.join(FONT_DIR, "GmarketSansTTFBold.ttf"),
    "Gmarket Sans Medium": os.path.join(FONT_DIR, "GmarketSansTTFMedium.ttf"),
    "Noto Sans KR Bold": os.path.join(FONT_DIR, "NotoSansKR-Bold.ttf"),
    "SCDream 5": os.path.join(FONT_DIR, "SCDream5.otf"),
    "Binggrae Bold": os.path.join(FONT_DIR, "BinggraeII-Bold.ttf"),
    "Noto Sans KR Regular": os.path.join(FONT_DIR, "NotoSansKR-Regular.ttf"),
    "SCDream 6": os.path.join(FONT_DIR, "SCDream6.otf"),
    "Bugaki": os.path.join(FONT_DIR, "Bugaki.ttf"),
    "온글잎 연체": os.path.join(FONT_DIR, "온글잎의연체.ttf"),
}

# ==========================================
# 2. 유틸리티 함수
# ==========================================
def _build_default_videos():
    if not os.path.exists(VIDEO_DIR): return []
    videos = []
    for f in sorted(os.listdir(VIDEO_DIR)):
        if f.lower().endswith((".mp4", ".mov")):
            v_path = os.path.join(VIDEO_DIR, f)
            t_path = os.path.join(THUMB_DIR, f"{os.path.splitext(f)[0]}.jpg")
            if not os.path.exists(t_path):
                try:
                    with VideoFileClip(v_path) as clip:
                        clip.save_frame(t_path, t=min(1.0, clip.duration/2))
                except: continue
            videos.append({"label": f, "video_path": v_path, "thumbnail": t_path})
    return videos

DEFAULT_VIDEOS = _build_default_videos()

if "is_generating" not in st.session_state:
    st.session_state["is_generating"] = False
    st.session_state["locked_style_music"] = None
IS_GEN = st.session_state.get("is_generating", False)

@st.cache_data
def _get_thumb_b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except: return ""

def hex_to_rgba(hex_color, alpha=255):
    h = hex_color.lstrip("#")
    if len(h) != 6: return (255, 255, 255, alpha)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (alpha,)

def load_font(path, size):
    try: return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

def _is_light(rgb):
    r, g, b = rgb
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.7

def make_font_preview(font_path, text, size, hex_color="#222222", bg=None):
    """Return a small preview image for a given font."""
    img_w, img_h = 640, 180
    text_rgb = hex_to_rgba(hex_color)[:3]
    bg_rgb = bg or ((20, 20, 20) if _is_light(text_rgb) else (245, 245, 245))
    img = Image.new("RGB", (img_w, img_h), bg_rgb)
    draw = ImageDraw.Draw(img)
    font = load_font(font_path, size)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pos = ((img_w - tw) // 2, (img_h - th) // 2)
    draw.text(pos, text, font=font, fill=text_rgb)
    return img

def _fit_bg_image(img):
    return ImageOps.fit(img.convert("RGBA"), (VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)

def make_video_preview_image(title, body_text, style_opt, uploaded_bg=None, default_video=None):
    """Create a preview image for the first scene."""
    bg_img = None

    # 1) 업로드된 배경
    if uploaded_bg:
        ext = uploaded_bg.name.split(".")[-1].lower()
        temp_bg = os.path.join("temp", f"preview_bg.{ext}")
        with open(temp_bg, "wb") as f: f.write(uploaded_bg.getbuffer())

        if ext in ["mp4", "mov", "avi"]:
            with VideoFileClip(temp_bg) as clip:
                frame = clip.get_frame(min(0.5, clip.duration/2))
            bg_img = _fit_bg_image(Image.fromarray(frame))
        else:
            bg_img = _fit_bg_image(Image.open(temp_bg))

    # 2) 기본 동영상
    elif default_video:
        with VideoFileClip(default_video) as clip:
            frame = clip.get_frame(min(0.5, clip.duration/2))
        bg_img = _fit_bg_image(Image.fromarray(frame))

    # 3) 아무 것도 없으면 단색 배경
    if bg_img is None:
        bg_img = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (20, 20, 20, 255))

    lines = [x.strip() for x in body_text.split("\n") if x.strip()]
    if not lines:
        lines = ["본문을 입력해주세요."]

    return create_text_overlay(title, lines, 0, **style_opt, bg_img=bg_img)

def _load_video_background(path):
    clip = VideoFileClip(path)
    resized = clip.resize(height=VIDEO_HEIGHT)
    if resized.w < VIDEO_WIDTH:
        resized = resized.resize(width=VIDEO_WIDTH)
    return resized.crop(x_center=resized.w/2, y_center=resized.h/2, width=VIDEO_WIDTH, height=VIDEO_HEIGHT)

def _wrap_title(draw, title_text, font, max_width):
    lines = []
    if " " in title_text:
        words = title_text.split()
        if not words: words = [title_text]
        current_line = []
        for word in words:
            test_tokens = current_line + [word]
            test_text = " ".join(test_tokens)
            bbox = draw.textbbox((0, 0), test_text, font=font)
            if bbox[2] - bbox[0] <= max_width or not current_line:
                current_line.append(word)
            else:
                lines.append(current_line)
                current_line = [word]
        if current_line: lines.append(current_line)
    else:
        chars = list(title_text)
        current_line = []
        for ch in chars:
            test_tokens = current_line + [ch]
            test_text = "".join(test_tokens)
            bbox = draw.textbbox((0, 0), test_text, font=font)
            if bbox[2] - bbox[0] <= max_width or not current_line:
                current_line.append(ch)
            else:
                lines.append(current_line)
                current_line = [ch]
        if current_line: lines.append(current_line)
    if len(lines) > 2:
        all_tokens = [token for line in lines for token in line]
        mid = len(all_tokens) // 2
        lines = [all_tokens[:mid], all_tokens[mid:]]
    return lines

# ==========================================
# 3. 이미지 생성 로직
# ==========================================
def create_text_overlay(title, lines, highlight_idx, **kwargs):
    cfg = kwargs
    
    W, H = VIDEO_WIDTH, VIDEO_HEIGHT
    
    TITLE_SIZE = int(cfg['title_size'] * 0.85)
    BODY_SIZE = int(cfg['body_size'] * 0.85)
    
    MARGIN_X = 60
    top_padding = int(cfg.get('top_padding', 190))
    TITLE_BOTTOM_MARGIN = 36
    DIVIDER_MARGIN = 60
    LINE_HEIGHT_RATIO = 1.9
    
    c_title = hex_to_rgba(cfg['colors']['title'])
    c_body = hex_to_rgba(cfg['colors']['body'])
    
    f_title = load_font(cfg['title_font_path'], TITLE_SIZE)
    f_body = load_font(cfg['body_font_path'], BODY_SIZE)
    try:
        f_body_bold = load_font(cfg['body_font_path'].replace("Medium", "Bold").replace("Regular", "Bold"), BODY_SIZE)
    except:
        f_body_bold = f_body

    bg_img = kwargs.get('bg_img')
    if bg_img is None:
         base = Image.new("RGBA", (W, H), (0,0,0,0))
    else:
         base = bg_img.copy().convert("RGBA")

    if cfg.get("overlay_darkness", 0) > 0:
        alpha = max(0, min(220, int(cfg["overlay_darkness"])))
        dimmer = Image.new("RGBA", (W, H), (0, 0, 0, alpha))
        base = Image.alpha_composite(base, dimmer)

    draw = ImageDraw.Draw(base)

    content_width = W - (MARGIN_X * 2)
    wrapped_title = _wrap_title(draw, title, f_title, content_width)
    
    start_y = top_padding
    cursor_y = start_y
    text_start_x = MARGIN_X

    # [제목]
    for line_tokens in wrapped_title:
        line_text = "".join(line_tokens) if " " not in title else " ".join(line_tokens)
        draw.text((text_start_x, cursor_y), line_text, font=f_title, fill=c_title)
        cursor_y += TITLE_SIZE * 1.3
    
    cursor_y += TITLE_BOTTOM_MARGIN
    cursor_y += (4 + DIVIDER_MARGIN)
    body_line_height = int(BODY_SIZE * LINE_HEIGHT_RATIO)

    # [본문]
    for i, line in enumerate(lines):
        is_highlight = (i == highlight_idx)
        cur_font = f_body_bold if is_highlight else f_body
        
        if is_highlight:
            text_color = c_body
        else:
            text_color = c_body[:3] + (100,) 

        draw.text((text_start_x, cursor_y), line, font=cur_font, fill=text_color)
        cursor_y += body_line_height

    return base

# ==========================================
# 메인 UI 구성
# ==========================================

st.markdown("""
<div class="main-header">
    <h1>🎬 Shorts Maker</h1>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# SECTION 0: AI 프롬프트 도우미 (내용 입력 바로 위)
# ----------------------------------------------------
with st.expander("🤖 AI에게 대본 요청하기 (프롬프트 복사)", expanded=True):
    st.markdown("""
    <div style="color: #555; font-size: 0.9rem; margin-bottom: 10px;">
        ChatGPT나 Gemini 등에게 아래 내용을 복사해서 물어보세요.<br>
        <b>제목 1개</b>와 <b>본문 8줄(마지막 CTA 포함)</b>을 완벽하게 뽑아줍니다.
        <br>(우측 상단 📄 아이콘을 누르면 복사됩니다)
    </div>
    """, unsafe_allow_html=True)
    
    prompt_text = """# 역할 부여
당신은 사람들의 감성을 자극하고 통찰을 주는 '인스타그램 릴스/숏폼 기획자'입니다.

# 입력 데이터
주제: [여기에 주제를 입력하세요. 예: 무기력증을 이겨내는 법]

# 작업 지시
위 주제를 바탕으로 숏폼 영상 텍스트를 작성해 주세요. 아래 규칙을 엄격히 준수하세요.

1. 썸네일 제목
   - 1초 만에 시선을 끄는 "후킹(Hooking)" 멘트 (15자 이내)
   - 의문형이나 강한 단정형 사용

2. 본문 (8줄 고정)
   - 번호 매기기(1., -) 금지, 오직 텍스트만 출력
   - 1~7줄: "~하는 것", "~하기" 등 간결한 명사형 어미로 끝낼 것 (운율감 형성)
   - 8번째 줄: "지금 바로 저장하고 잊지 마세요!" 등 강력한 행동 유도(CTA)

# 출력 예시
제목: 당신이 지금 불행한 이유
본문:
남의 시선을 너무 의식하는 것
건강을 미리 챙기지 않은 것
(중략)
지금 바로 캡처해서 저장하세요!"""
    
    st.code(prompt_text, language="text")

# ----------------------------------------------------
# SECTION 1: 내용 입력 (항상 표시)
# ----------------------------------------------------
st.markdown('<div class="section-header"><span>✍️</span> 내용 입력</div>', unsafe_allow_html=True)

title_text = st.text_input("제목", "왜 자꾸 인간관계가 힘들까", disabled=IS_GEN)
body_text = st.text_area("본문 (한 줄씩 작성해주세요, 줄바꿈 필수)", 
    "내가 책임지려는 마음 내려놓기\n거절을 미안해하지 않기\n상대의 기분까지 관리하지 않기\n말하지 않아도 알겠지 기대하지 않기\n감정소모 큰 사람과 거리 두기\n내 시간을 남에게 잠식되지 않게 하기\n내가 먼저 나를 챙기기\n지금 바로 저장하고 잊지 마세요!",
    height=200,
    disabled=IS_GEN
)
st.markdown('</div>', unsafe_allow_html=True)

bg_container = st.empty()     # 배경 선택 UI용
style_container = st.empty()  # 스타일 및 음악 설정 UI용
btn_container = st.empty()    # 생성 버튼 UI용

# ----------------------------------------------------
# SECTION 2: 배경 선택 (bg_container 안에 렌더링)
# ----------------------------------------------------
with bg_container.container():
    @st.fragment 
    def render_background_section():
        st.markdown('<div class="section-header"><span>🖼</span> 배경 선택</div>', unsafe_allow_html=True)
        
        if "selected_default_video" not in st.session_state and DEFAULT_VIDEOS:
            st.session_state["selected_default_video"] = DEFAULT_VIDEOS[0]

        bg_mode = st.radio("배경 소스", ["기본 동영상", "직접 업로드"], horizontal=True, label_visibility="collapsed", disabled=IS_GEN)
        
        if bg_mode == "기본 동영상":
            if DEFAULT_VIDEOS:
                curr_path = st.session_state["selected_default_video"]["video_path"]
                
                html_content = '<div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;">'
                for idx, video in enumerate(DEFAULT_VIDEOS):
                    b64 = _get_thumb_b64(video["thumbnail"])
                    is_sel = (video["video_path"] == curr_path)
                    border = "4px solid #8E2DE2" if is_sel else "1px solid #f0f0f0"
                    opacity = "1.0" if is_sel else "0.8"
                    
                    html_content += f"""
                    <a href='javascript:void(0);' id='{idx}' style='text-decoration: none;'>
                        <div style="
                            width: 85px; height: 125px;
                            background: url('data:image/jpeg;base64,{b64}') center/cover;
                            border-radius: 12px; border: {border}; opacity: {opacity};
                            margin-bottom: 5px;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                        "></div>
                    </a>"""
                html_content += "</div>"
                
                clicked = None if IS_GEN else click_detector(html_content)
                
                if clicked:
                    new_vid = DEFAULT_VIDEOS[int(clicked)]
                    if st.session_state["selected_default_video"] != new_vid:
                        st.session_state["selected_default_video"] = new_vid
                        st.rerun() 
            else:
                st.info("video 폴더에 영상이 없습니다.")
        else:
            st.file_uploader("이미지/영상 업로드", type=["jpg", "png", "mp4"], key="uploaded_bg_file", disabled=IS_GEN)
            
        st.markdown('</div>', unsafe_allow_html=True)

    render_background_section()

# ----------------------------------------------------
# SECTION 3: 음악 및 스타일 (style_container 안에 렌더링)
# ----------------------------------------------------
with style_container.container():
    with st.expander("🎨 스타일 & 음악 설정 (클릭하여 펼치기)", expanded=True):
        if st.session_state.get("is_generating"):
            st.info("영상 제작 중입니다. 다음 제작부터 변경사항이 적용됩니다.")

        st.markdown('<span class="sub-label">🎵 배경 음악 설정</span>', unsafe_allow_html=True)
        
        col_m1, col_m2 = st.columns([7, 3])
        with col_m1:
            music_mode = st.selectbox("배경 음악 선택", ["기본 음악", "직접 업로드", "사용 안함"], disabled=IS_GEN)
        with col_m2:
            music_vol = st.slider("배경 음량", 0.0, 1.0, 0.3, disabled=IS_GEN)

        if music_mode == "직접 업로드":
            music_file = st.file_uploader("MP3 파일", type=["mp3"], disabled=IS_GEN)
        else:
            music_file = None

        st.markdown('<div class="styled-hr"></div>', unsafe_allow_html=True)
        
        st.markdown('<span class="sub-label">✏️ 폰트 및 색상</span>', unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            t_font = st.selectbox("제목 폰트", list(AVAILABLE_FONTS.keys()), index=0, disabled=IS_GEN)
            c_title = st.color_picker("제목 색상", "#FFD600", disabled=IS_GEN)
            t_size = st.slider("제목 크기", 50, 200, 130, disabled=IS_GEN)
        with col_s2:
            b_font = st.selectbox("본문 폰트", list(AVAILABLE_FONTS.keys()), index=1, disabled=IS_GEN)
            c_body = st.color_picker("본문 색상", "#FFFFFF", disabled=IS_GEN)
            b_size = st.slider("본문 크기", 30, 150, 65, disabled=IS_GEN)

        # 폰트 미리보기
        st.markdown('<span class="sub-label">👀 폰트 미리보기</span>', unsafe_allow_html=True)
        prev_col1, prev_col2 = st.columns(2)
        with prev_col1:
            st.image(
                make_font_preview(AVAILABLE_FONTS[t_font], "제목 미리보기", int(t_size * 0.7), c_title),
                caption=f"{t_font} (제목)",
                use_container_width=True,
            )
        with prev_col2:
            st.image(
                make_font_preview(AVAILABLE_FONTS[b_font], "본문 미리보기", int(b_size * 0.7), c_body),
                caption=f"{b_font} (본문)",
                use_container_width=True,
            )

        st.markdown('<div class="styled-hr"></div>', unsafe_allow_html=True)
        
        st.markdown('<span class="sub-label">✨ 배경 효과</span>', unsafe_allow_html=True)
        dark_val = st.slider("배경 어둡기", 0, 200, 90, disabled=IS_GEN)
        top_padding = st.slider("텍스트 상단 여백", 20, 500, 190, disabled=IS_GEN)

        # 현재 선택값을 공통으로 사용하는 스타일 옵션
        style_opt = {
            "title_font_path": AVAILABLE_FONTS[t_font],
            "body_font_path": AVAILABLE_FONTS[b_font],
            "brand_font_path": AVAILABLE_FONTS[t_font],
            "title_size": t_size, 
            "body_size": b_size, 
            "colors": {"title": c_title, "body": c_body},
            "overlay_darkness": dark_val,
            "top_padding": top_padding,
        }

        st.markdown('<div class="styled-hr"></div>', unsafe_allow_html=True)

        st.markdown('<span class="sub-label">🎞️ 영상 미리보기 (첫 장면)</span>', unsafe_allow_html=True)
        preview_btn = st.button("👀 영상 미리보기", use_container_width=True, disabled=IS_GEN)
        if preview_btn:
            try:
                uploaded_bg = st.session_state.get("uploaded_bg_file")
                sel_vid = st.session_state.get("selected_default_video", DEFAULT_VIDEOS[0] if DEFAULT_VIDEOS else None)
                default_video_path = sel_vid["video_path"] if sel_vid else None
                preview_img = make_video_preview_image(title_text, body_text, style_opt, uploaded_bg=uploaded_bg, default_video=default_video_path)
                st.image(preview_img, caption="영상 미리보기 (첫 장면)", use_container_width=True)
            except Exception as e:
                st.error(f"미리보기 생성 중 오류: {str(e)}")

# ----------------------------------------------------
# SECTION 5: 생성 버튼
# ----------------------------------------------------
with btn_container.container():
    clicked_id = st.button("🎬 영상 생성하기", use_container_width=True, disabled=IS_GEN, type="primary")
    if clicked_id:
        clicked_id = "start_gen_btn"

# ==========================================
# 실행 로직 (버튼 클릭 시 처리)
# ==========================================
if clicked_id == "start_gen_btn":
    
    # 1. 빈 값 체크
    if st.session_state.get("is_generating"):
        st.warning("다른 영상이 제작 중입니다. 완료될 때까지 기다려주세요.")
    elif not body_text.strip():
        st.error("내용을 입력해주세요!")
    else:
        bg_container.empty()
        style_container.empty()
        btn_container.empty()

        # 2. 영상 생성 시작
        st.session_state["is_generating"] = True
        st.session_state["locked_style_music"] = {
            "style_opt": dict(style_opt),
            "music_mode": music_mode,
            "music_vol": music_vol,
            "music_bytes": music_file.getbuffer().tobytes() if music_mode == "직접 업로드" and music_file else None,
        }
        progress_text = "🎬 영상 제작을 시작합니다..."
        my_bar = st.progress(0, text=progress_text)
        
        try:
            # === (기존 생성 로직 시작) ===
            lines = [x.strip() for x in body_text.split('\n') if x.strip()]
            locked_cfg = st.session_state["locked_style_music"] or {}
            
            bg_clip = None
            bg_img_path = None
            uploaded_bg = st.session_state.get("uploaded_bg_file")
            
            if uploaded_bg:
                ext = uploaded_bg.name.split('.')[-1].lower()
                temp_bg = os.path.join("temp", f"upload_bg.{ext}")
                with open(temp_bg, "wb") as f: f.write(uploaded_bg.getbuffer())
                
                if ext in ['mp4', 'mov', 'avi']:
                    bg_clip = _load_video_background(temp_bg)
                else:
                    bg_img_path = temp_bg 
            elif DEFAULT_VIDEOS:
                sel_vid = st.session_state.get("selected_default_video", DEFAULT_VIDEOS[0])
                bg_clip = _load_video_background(sel_vid['video_path'])

            if not bg_clip and not bg_img_path:
                if DEFAULT_VIDEOS:
                    bg_clip = _load_video_background(DEFAULT_VIDEOS[0]['video_path'])
                else:
                    raise Exception("배경을 선택해주세요.")

            active_style_opt = locked_cfg.get("style_opt", style_opt)

            clips = []
            total_steps = len(lines) + 2 
            
            for i, line in enumerate(lines):
                percent = int((i / total_steps) * 100)
                my_bar.progress(percent, text=f"🎞️ 장면 {i+1} 생성 중...")
                
                txt_img = create_text_overlay(title_text, lines, i, **active_style_opt)
                txt_clip = ImageClip(np.array(txt_img)).set_duration(DEFAULT_LINE_DURATION)
                
                if bg_clip:
                    bg_seg = bg_clip.subclip(0, DEFAULT_LINE_DURATION)
                    bg_seg = bg_seg.fx(vfx.loop, duration=DEFAULT_LINE_DURATION)
                    clips.append(CompositeVideoClip([bg_seg, txt_clip]).set_duration(DEFAULT_LINE_DURATION))
                else:
                    bg_base = Image.open(bg_img_path).convert("RGBA")
                    bg_base = ImageOps.fit(bg_base, (VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)
                    final_scene = Image.alpha_composite(bg_base, txt_img)
                    clips.append(ImageClip(np.array(final_scene)).set_duration(DEFAULT_LINE_DURATION))

            my_bar.progress(80, text="🎼 오디오 합성 및 인코딩 중... (예상 시간 약 1분~2분)")
            final_video = concatenate_videoclips(clips, method="compose")

            audio_clip = None
            active_music_mode = locked_cfg.get("music_mode", music_mode)
            active_music_bytes = locked_cfg.get("music_bytes")
            active_music_vol = locked_cfg.get("music_vol", music_vol)
            if active_music_mode == "기본 음악" and os.path.exists(DEFAULT_MUSIC):
                audio_clip = AudioFileClip(DEFAULT_MUSIC)
            elif active_music_mode == "직접 업로드" and active_music_bytes:
                with open("temp/temp_music.mp3", "wb") as f: f.write(active_music_bytes)
                audio_clip = AudioFileClip("temp/temp_music.mp3")
            
            if audio_clip:
                if audio_clip.duration < final_video.duration:
                    audio_clip = audio_clip.loop(duration=final_video.duration)
                else:
                    audio_clip = audio_clip.subclip(0, final_video.duration)
                final_video = final_video.set_audio(audio_clip.volumex(active_music_vol))

            output_path = "output_shorts.mp4"
            final_video.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                preset="superfast",
                threads=max(1, os.cpu_count() or 1),
                logger=None,
            )
            
            if bg_clip: bg_clip.close()

            my_bar.progress(100, text="✅ 영상 제작 완료!")
            st.balloons() # 축하 효과 추가
            
            st.video(output_path)
            
            with open(output_path, "rb") as f:
                st.download_button("📥 영상 저장하기", f, file_name="shorts.mp4", type="primary")
                
        except Exception as e:
            my_bar.empty()
            st.error(f"에러 발생: {str(e)}")
        finally:
            st.session_state["is_generating"] = False
            st.session_state["locked_style_music"] = None