import streamlit as st
import pandas as pd
from gtts import gTTS
import io

st.set_page_config(page_title="CROWN Auto Flashcards", layout="centered")

# --- データの読み込み ---
@st.cache_data
def load_data():
    return pd.read_csv("data.csv") # 1行目は見出しとして無視

df = load_data()

# --- セッション状態の管理 ---
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'auto_mode' not in st.session_state:
    st.session_state.auto_mode = False

st.title("🔊 CROWN 安定版オートめくり")

# --- オート再生の心臓部（JavaScriptタイマー） ---
if st.session_state.auto_mode:
    # 5000ミリ秒（5秒）ごとに自分自身をリロードさせるJavaScript
    st.components.v1.html(
        """
        <script>
        window.parent.document.dispatchEvent(new CustomEvent("streamlit:render"));
        setTimeout(function() {
            window.parent.document.querySelector('.stButton button').click();
        }, 5000); 
        </script>
        """,
        height=0,
    )
    # 5秒経ったらインデックスを進める処理
    st.session_state.index = (st.session_state.index + 1) % len(df)

# --- カード表示 ---
english_text = str(df.iloc[st.session_state.index, 0])
japanese_text = str(df.iloc[st.session_state.index, 1])

st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 40px; border-radius: 15px; border-left: 10px solid #005088; text-align: center;">
        <h1 style="color: #333;">{english_text}</h1>
        <hr>
        <h2 style="color: #666;">{japanese_text}</h2>
    </div>
    """, unsafe_allow_html=True)

# --- 音声再生 ---
tts = gTTS(text=english_text, lang='en')
audio_fp = io.BytesIO()
tts.write_to_fp(audio_fp)
st.audio(audio_fp, format='audio/mp3', autoplay=True)

# --- 操作パネル ---
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ 前へ"):
        st.session_state.index = (st.session_state.index - 1) % len(df)
        st.session_state.auto_mode = False # 手動操作時はオートを切る
        st.rerun()

with col2:
    if not st.session_state.auto_mode:
        if st.button("▶️ オート開始"):
            st.session_state.auto_mode = True
            st.rerun()
    else:
        if st.button("⏹️ 停止"):
            st.session_state.auto_mode = False
            st.rerun()

with col3:
    if st.button("次へ ➡️"):
        st.session_state.index = (st.session_state.index + 1) % len(df)
        st.session_state.auto_mode = False
        st.rerun()

st.write(f"Card: {st.session_state.index + 1} / {len(df)}")
