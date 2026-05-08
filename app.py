import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import time

st.set_page_config(page_title="CROWN Study App", layout="centered")

# --- データの読み込み ---
@st.cache_data
def load_data():
    try:
        # A1, B1を見出しとして扱い、A2, B2から読み込む
        return pd.read_csv("data.csv")
    except:
        return pd.DataFrame([["File Error", "data.csvが見つかりません"]])

df = load_data()

# --- セッション状態の初期化 ---
if 'index' not in st.session_state:
    st.session_state.index = 0

st.title("🔊 CROWN 学習モード選択")

# --- モード選択スイッチ ---
mode = st.radio("学習モードを選択:", ["👆 手動でめくる (Plan A)", "🤖 オート再生 (Plan B)"], horizontal=True)

st.divider()

# --- カード表示部分 ---
english_text = str(df.iloc[st.session_state.index, 0])
japanese_text = str(df.iloc[st.session_state.index, 1])

st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 30px; border-radius: 15px; border-left: 10px dotted #005088; text-align: center;">
        <div style="font-size: 28px; font-weight: bold; color: #333; margin-bottom: 10px;">{english_text}</div>
        <div style="font-size: 20px; color: #666; border-top: 1px solid #ccc; padding-top: 10px;">{japanese_text}</div>
    </div>
    """, unsafe_allow_html=True)

# --- 音声再生関数 ---
def play_audio(text):
    tts = gTTS(text=text, lang='en')
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    st.audio(audio_fp, format='audio/mp3', autoplay=True)

# --- A: 手動モードの挙動 ---
if mode == "👆 手動でめくる (Plan A)":
    play_audio(english_text)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 前へ", use_container_width=True):
            st.session_state.index = (st.session_state.index - 1) % len(df)
            st.rerun()
    with col2:
        if st.button("次へ ➡️", use_container_width=True):
            st.session_state.index = (st.session_state.index + 1) % len(df)
            st.rerun()

# --- B: オートモードの挙動 ---
else:
    st.warning("⚠️ オート再生中... 画面を閉じずにそのままお待ちください")
    play_audio(english_text)
    
    # 再生速度の設定（秒）
    wait_time = st.slider("次のカードまでの間隔（秒）", 3, 15, 6)
    
    # ここで待機してリロード
    time.sleep(wait_time)
    st.session_state.index = (st.session_state.index + 1) % len(df)
    st.rerun()

st.divider()
st.write(f"進捗: {st.session_state.index + 1} / {len(df)}")
