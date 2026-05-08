import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import base64

# ページの設定
st.set_page_config(page_title="CROWN音読ツール", layout="centered")

# --- データの読み込み ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv("data.csv")
    except:
        return pd.DataFrame([["Error", "data.csvが見つかりません"]])

df = load_data()

# --- セッション状態の初期化 ---
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'mode' not in st.session_state:
    st.session_state.mode = "手動"

# --- 音声再生用関数 ---
def play_audio(text):
    if text:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        audio_html = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}"></audio>'
        st.components.v1.html(audio_html, height=0)

# --- タイトルの表示 ---
st.title("🔊 CROWN音読ツール")

# --- モード選択ボタン ---
st.subheader("学習モードを選択")
col_m1, col_m2 = st.columns(2)
with col_m1:
    if st.button("👆 手動モード", use_container_width=True, type="primary" if st.session_state.mode == "手動" else "secondary"):
        st.session_state.mode = "手動"
        st.rerun()
with col_m2:
    if st.button("🤖 オートモード", use_container_width=True, type="primary" if st.session_state.mode == "オート" else "secondary"):
        st.session_state.mode = "オート"
        st.rerun()

st.divider()

# --- カード操作ボタン（「先頭に戻る」を特等席に配置） ---
col_nav1, col_nav2 = st.columns([1, 3])
with col_nav1:
    # どのモードでも使えるリセットボタン
    if st.button("⏮️ 先頭に戻る", use_container_width=True):
        st.session_state.index = 0
        st.rerun()
with col_nav2:
    st.caption(f"現在の位置: {st.session_state.index + 1} / {len(df)} 枚目")

# --- 現在のカードデータ取得 ---
english_text = str(df.iloc[st.session_state.index, 0])
japanese_text = str(df.iloc[st.session_state.index, 1])

# カードの表示
st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 30px; border-radius: 15px; border-left: 10px solid #005088; text-align: center; margin-bottom: 20px;">
        <div style="font-size: 28px; font-weight: bold; color: #333; margin-bottom: 10px;">{english_text}</div>
        <div style="font-size: 20px; color: #666; border-top: 1px solid #ccc; padding-top: 10px;">{japanese_text}</div>
    </div>
    """, unsafe_allow_html=True)

# --- モード別実行ロジック ---

if st.session_state.mode == "手動":
    # 再生ボタン
    if st.button("▶️ 英語を再生", use_container_width=True):
        play_audio(english_text)
    
    # 前後移動
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 前へ", use_container_width=True):
            st.session_state.index = (st.session_state.index - 1) % len(df)
            st.rerun()
    with col2:
        if st.button("次へ ➡️", use_container_width=True):
            st.session_state.index = (st.session_state.index + 1) % len(df)
            st.rerun()

else:
    # --- オートモード ---
    st.info("🤖 オート再生中...")
    play_audio(english_text)
    
    if st.button("⏹️ オートを停止して手動に戻る", use_container_width=True, type="primary"):
        st.session_state.mode = "手動"
        st.rerun()
    
    wait_time = st.slider("間隔（秒）", 3, 12, 6)
    
    # JavaScriptによる自動遷移
    st.components.v1.html(
        f"""
        <script>
        setTimeout(function() {{
            window.parent.document.dispatchEvent(new CustomEvent("streamlit:render"));
        }}, {wait_time * 1000});
        </script>
        """,
        height=0
    )
    # インデックスを次に進める（自動でループする設定）
    st.session_state.index = (st.session_state.index + 1) % len(df)

st.divider()
