import streamlit as st
import pandas as pd
from gtts import gTTS
import io

st.set_page_config(page_title="CROWN Flashcards", layout="centered")

# --- データの読み込み ---
@st.cache_data
def load_data():
    return pd.read_csv("data.csv")

df = load_data()

# --- セッション状態の初期化 ---
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'auto_play' not in st.session_state:
    st.session_state.auto_play = False

st.title("🎴 CROWN オート学習")

# --- オート再生のタイマー設定 ---
if st.session_state.auto_play:
    # 5000ミリ秒（5秒）ごとに画面を強制リフレッシュして次へ進む
    st.info("🔄 オート再生中...（5秒ごとに次へ進みます）")
    st.empty() 
    # このコンポーネントが指定秒数ごとにスクリプトを再実行させる
    st_autorefresh = st.empty()
    with st_autorefresh:
        st.write("") # 空の要素
        # インデックスを自動で進める
        st.session_state.index = (st.session_state.index + 1) % len(df)
        # JavaScript的なリフレッシュ（Streamlitの標準機能）
        st.runtime.legacy_caching.clear_cache() # キャッシュクリア
        st.rerun()

# --- カード表示 ---
english_text = str(df.iloc[st.session_state.index, 0])
japanese_text = str(df.iloc[st.session_state.index, 1])

# カードのデザイン
st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 40px; border-radius: 10px; border-left: 10px solid #005088; margin-bottom: 20px;">
        <h2 style="color: #333;">{english_text}</h2>
        <hr>
        <h3 style="color: #666;">{japanese_text}</h3>
    </div>
    """, unsafe_allow_html=True)

# --- 音声の自動再生 ---
# カードが表示されるたびに音声を生成して流す
tts = gTTS(text=english_text, lang='en')
audio_fp = io.BytesIO()
tts.write_to_fp(audio_fp)
st.audio(audio_fp, format='audio/mp3', autoplay=True)

# --- 操作ボタン ---
col1, col2 = st.columns(2)
with col1:
    if st.button("⬅️ 前のカードへ"):
        st.session_state.index = (st.session_state.index - 1) % len(df)
        st.rerun()

with col2:
    if st.button("次のカードへ ➡️"):
        st.session_state.index = (st.session_state.index + 1) % len(df)
        st.rerun()

st.divider()

# --- オート再生スイッチ ---
if not st.session_state.auto_play:
    if st.button("▶️ オート再生を開始する"):
        st.session_state.auto_play = True
        st.rerun()
else:
    if st.button("⏹️ オート再生を停止する"):
        st.session_state.auto_play = False
        st.rerun()

st.caption(f"Card {st.session_state.index + 1} / {len(df)}")
