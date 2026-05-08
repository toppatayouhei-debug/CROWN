import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import time

st.set_page_config(page_title="CROWN Flashcards", layout="centered", page_icon="🎴")

# --- スタイルの設定（カードっぽく見せる） ---
st.markdown("""
    <style>
    .card-box {
        background-color: white;
        padding: 50px;
        border-radius: 15px;
        border: 2px solid #005088;
        text-align: center;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎴 CROWN オートめくり学習")

# --- データの読み込み ---
@st.cache_data
def load_data():
    return pd.read_csv("data.csv")

df = load_data()

# --- 学習状態の管理 ---
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

# 現在のデータ取得
english_text = str(df.iloc[st.session_state.index, 0])
japanese_text = str(df.iloc[st.session_state.index, 1])

# --- カード表示エリア ---
if not st.session_state.show_answer:
    # 表面（英語）
    st.markdown(f'<div class="card-box">{english_text}</div>', unsafe_allow_html=True)
else:
    # 裏面（日本語）
    st.markdown(f'<div class="card-box" style="color: #d32f2f;">{japanese_text}</div>', unsafe_allow_html=True)

# --- 操作ボタン ---
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ 前へ"):
        st.session_state.index = (st.session_state.index - 1) % len(df)
        st.session_state.show_answer = False
        st.rerun()

with col2:
    if st.button("🔍 答えを見る"):
        st.session_state.show_answer = not st.session_state.show_answer
        st.rerun()

with col3:
    if st.button("次へ ➡️"):
        st.session_state.index = (st.session_state.index + 1) % len(df)
        st.session_state.show_answer = False
        st.rerun()

st.divider()

# --- オートモード ---
st.subheader("⚙️ オート再生モード")
auto_speed = st.slider("切り替え速度（秒）", 1, 10, 3)

if st.button("▶️ オート再生を開始（1周します）"):
    for i in range(st.session_state.index, len(df)):
        st.session_state.index = i
        
        # 1. 英語を表示
        st.session_state.show_answer = False
        st.rerun() # ここで画面更新
        
        # 2. 音声を再生（少し待機）
        tts = gTTS(text=str(df.iloc[i, 0]), lang='en')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        st.audio(audio_fp, format='audio/mp3', autoplay=True)
        
        time.sleep(auto_speed)
        
        # 3. 日本語を表示
        st.session_state.show_answer = True
        st.rerun()
        
        time.sleep(2) # 和訳を見せる時間
