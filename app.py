import streamlit as st
import pandas as pd
from gtts import gTTS
import io

# ページの設定
st.set_page_config(page_title="CROWN Flashcards", layout="centered")

# --- データの読み込み ---
@st.cache_data
def load_data():
    # 自分のCSVファイル名に合わせてください
    return pd.read_csv("data.csv")

df = load_data()

# --- セッション状態（データの保持）の初期化 ---
if 'index' not in st.session_state:
    st.session_state.index = 0

st.title("🎴 CROWN めくり学習")

# --- 現在のカード情報を取得 ---
# 列名ではなく「番号」で指定（0番目が英語、1番目が日本語）
english_text = str(df.iloc[st.session_state.index, 0])
japanese_text = str(df.iloc[st.session_state.index, 1])

# --- カード表示 ---
st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 40px; border-radius: 10px; border-left: 10px solid #005088; margin-bottom: 20px; text-align: center;">
        <h1 style="color: #333; font-size: 32px;">{english_text}</h1>
        <hr>
        <h2 style="color: #666; font-size: 24px;">{japanese_text}</h2>
    </div>
    """, unsafe_allow_html=True)

# --- 音声の再生 ---
# カードが切り替わるたびに自動で再生
tts = gTTS(text=english_text, lang='en')
audio_fp = io.BytesIO()
tts.write_to_fp(audio_fp)
st.audio(audio_fp, format='audio/mp3', autoplay=True)

# --- 操作ボタン ---
col1, col2 = st.columns(2)

with col1:
    if st.button("⬅️ 前のカード", use_container_width=True):
        st.session_state.index = (st.session_state.index - 1) % len(df)
        st.rerun()

with col2:
    if st.button("次のカード ➡️", use_container_width=True):
        st.session_state.index = (st.session_state.index + 1) % len(df)
        st.rerun()

st.divider()
st.write(f"進捗: {st.session_state.index + 1} / {len(df)}")

# ヒント
st.caption("「次のカード」を押すと、自動的に次の英文が読み上げられます。")
