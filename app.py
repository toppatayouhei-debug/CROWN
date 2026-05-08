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

# --- タイトルの表示 ---
st.title("🔊 CROWN音読ツール")

# --- 学習モード選択 ---
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

# --- ナビゲーション ---
col_nav1, col_nav2 = st.columns([1, 2])
with col_nav1:
    if st.button("⏮️ 先頭に戻る", use_container_width=True):
        st.session_state.index = 0
        st.rerun()
with col_nav2:
    st.write(f"📍 {st.session_state.index + 1} / {len(df)} 枚目")

# --- 現在のデータ取得 ---
english_text = str(df.iloc[st.session_state.index, 0])
japanese_text = str(df.iloc[st.session_state.index, 1])

# カード表示
st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 30px; border-radius: 15px; border-left: 10px solid #005088; text-align: center; margin-bottom: 20px;">
        <div style="font-size: 26px; font-weight: bold; color: #333;">{english_text}</div>
        <hr>
        <div style="font-size: 18px; color: #666;">{japanese_text}</div>
    </div>
    """, unsafe_allow_html=True)

# --- 音声生成と再生バーの表示 ---
tts = gTTS(text=english_text, lang='en')
fp = io.BytesIO()
tts.write_to_fp(fp)
fp.seek(0)
b64_audio = base64.b64encode(fp.read()).decode()

# 標準のオーディオプレイヤー（これを一度クリックするとブラウザのブロックが解けます）
st.audio(fp, format='audio/mp3', autoplay=True)

# --- モード別実行ロジック ---

if st.session_state.mode == "手動":
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
    # オートモード
    wait_time = st.slider("切替間隔（秒）", 3, 15, 7)
    
    if st.button("⏹️ 停止して手動に戻る", use_container_width=True, type="primary"):
        st.session_state.mode = "手動"
        st.rerun()

    # 自動再生を補助するJavaScript
    st.components.v1.html(f"""
        <script>
            setTimeout(function() {{
                window.parent.document.dispatchEvent(new CustomEvent("streamlit:render"));
            }}, {wait_time * 1000});
        </script>
    """, height=0)
    
    st.session_state.index = (st.session_state.index + 1) % len(df)
    st.info(f"🤖 次のカードまであと {wait_time} 秒...")

st.divider()
