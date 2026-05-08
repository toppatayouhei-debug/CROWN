import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import base64

st.set_page_config(page_title="CROWN音読ツール", layout="centered")

# --- データの読み込み ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv("data.csv")
    except:
        return pd.DataFrame([["Error", "CSV読み込み失敗"]])

df = load_data()

# --- セッション状態の初期化 ---
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'mode' not in st.session_state:
    st.session_state.mode = "待機" # 最初は待機状態にする

st.title("🔊 CROWN音読ツール")

# --- 1. 最初の起動画面 ---
if st.session_state.mode == "待機":
    st.info("下のボタンを押すと学習を開始します。")
    if st.button("🚀 学習を開始する（音声を許可）", use_container_width=True, type="primary"):
        st.session_state.mode = "手動" # 最初は手動からスタート
        st.rerun()
    st.stop() # ここで処理を止めてボタン押し待ちにする

# --- 2. 学習画面（ここから下がメイン） ---
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

# --- カード表示 ---
eng = str(df.iloc[st.session_state.index, 0])
jp = str(df.iloc[st.session_state.index, 1])

st.write(f"📍 {st.session_state.index + 1} / {len(df)} 枚目")
st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 30px; border-radius: 15px; border-left: 10px solid #005088; text-align: center; margin-bottom: 10px;">
        <div style="font-size: 26px; font-weight: bold; color: #333;">{eng}</div>
        <hr>
        <div style="font-size: 18px; color: #666;">{jp}</div>
    </div>
    """, unsafe_allow_html=True)

# 音声生成
tts = gTTS(text=eng, lang='en')
fp = io.BytesIO()
tts.write_to_fp(fp)
fp.seek(0)
b64_audio = base64.b64encode(fp.read()).decode()

# --- 実行ロジック ---
if st.session_state.mode == "手動":
    st.components.v1.html(f"""<audio autoplay src="data:audio/mp3;base64,{b64_audio}"></audio>""", height=0)
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
    if st.button("⏹️ オートを停止して手動に戻る", use_container_width=True, type="primary"):
        st.session_state.mode = "手動"
        st.rerun()
    
    # 隠しボタン
    if st.button("NEXT_STEP", key="auto_next"):
        st.session_state.index = (st.session_state.index + 1) % len(df)
        st.rerun()

    st.components.v1.html(f"""
        <audio id="tts" autoplay src="data:audio/mp3;base64,{b64_audio}"></audio>
        <script>
            var audio = document.getElementById('tts');
            audio.onended = function() {{
                setTimeout(function() {{
                    var btns = window.parent.document.querySelectorAll('button');
                    for (var i = 0; i < btns.length; i++) {{
                        if (btns[i].innerText === 'NEXT_STEP') {{ btns[i].click(); break; }}
                    }}
                }}, 1000);
            }};
        </script>
    """, height=0)

st.markdown("""<style>div[data-testid="stButton"] button:has(div:contains("NEXT_STEP")) { display: none; }</style>""", unsafe_allow_html=True)
st.divider()
if st.button("⏮️ 先頭に戻る", use_container_width=True):
    st.session_state.index = 0
    st.rerun()
