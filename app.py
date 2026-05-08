import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import time

# ページの設定
st.set_page_config(page_title="CROWN Auto Flashcards", layout="centered", page_icon="🔊")

# --- スタイルの設定（カードを綺麗に見せる） ---
st.markdown("""
    <style>
    .card-container {
        background-color: #f8f9fa;
        padding: 40px;
        border-radius: 15px;
        border-left: 10px solid #005088;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    .en-text {
        font-size: 32px;
        font-weight: bold;
        color: #333;
        margin-bottom: 10px;
    }
    .jp-text {
        font-size: 24px;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔊 CROWN 自動めくり学習")

# --- データの読み込み設定 ---
@st.cache_data
def load_data():
    try:
        # header=0 (デフォルト) で読み込むことで、1行目を無視してA2, B2からデータとして扱います
        df = pd.read_csv("data.csv")
        return df
    except Exception as e:
        return pd.DataFrame([["Error", "CSVファイル(data.csv)が見つかりません"]])

df = load_data()

# --- セッション状態の初期化 ---
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'auto_mode' not in st.session_state:
    st.session_state.auto_mode = False

# --- オート再生の制御ロジック ---
if st.session_state.auto_mode:
    # 現在のカード情報を取得
    english_text = str(df.iloc[st.session_state.index, 0])
    japanese_text = str(df.iloc[st.session_state.index, 1])

    # カード表示
    st.markdown(f"""
        <div class="card-container">
            <div class="en-text">{english_text}</div>
            <hr>
            <div class="jp-text">{japanese_text}</div>
        </div>
        """, unsafe_allow_html=True)

    # 音声再生
    tts = gTTS(text=english_text, lang='en')
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    st.audio(audio_fp, format='audio/mp3', autoplay=True)

    st.info(f"🔄 オート再生中... ({st.session_state.index + 1} / {len(df)})")
    
    # 停止ボタンを配置（オート中も止められるように）
    if st.button("⏹️ オート再生を停止"):
        st.session_state.auto_mode = False
        st.rerun()

    # 5秒待機してから次へ
    time.sleep(5)
    st.session_state.index = (st.session_state.index + 1) % len(df)
    st.rerun()

else:
    # --- 手動モードの表示 ---
    english_text = str(df.iloc[st.session_state.index, 0])
    japanese_text = str(df.iloc[st.session_state.index, 1])

    st.markdown(f"""
        <div class="card-container">
            <div class="en-text">{english_text}</div>
            <hr>
            <div class="jp-text">{japanese_text}</div>
        </div>
        """, unsafe_allow_html=True)

    # 手動再生ボタン
    tts = gTTS(text=english_text, lang='en')
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    st.audio(audio_fp, format='audio/mp3', autoplay=True)

    # 操作ボタン
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ 前へ", use_container_width=True):
            st.session_state.index = (st.session_state.index - 1) % len(df)
            st.rerun()
    with col2:
        if st.button("▶️ オート開始", use_container_width=True):
            st.session_state.auto_mode = True
            st.rerun()
    with col3:
        if st.button("次へ ➡️", use_container_width=True):
            st.session_state.index = (st.session_state.index + 1) % len(df)
            st.rerun()

st.divider()
st.write(f"カード: {st.session_state.index + 1} / {len(df)}")
