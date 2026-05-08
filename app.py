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

# --- 改良版：音声再生関数 ---
def play_audio(text):
    if text:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        
        # 1. 見えないオーディオプレイヤーを埋め込む
        # 2. JavaScriptで強制的に再生を開始させる（ブラウザのブロック対策）
        audio_html = f"""
            <div id="audio-container">
                <audio id="tts-audio" src="data:audio/mp3;base64,{b64}"></audio>
                <script>
                    var audio = document.getElementById('tts-audio');
                    audio.play().catch(function(error) {{
                        console.log("自動再生がブロックされました。ユーザー操作が必要です。");
                    }});
                </script>
            </div>
            """
        st.components.v1.html(audio_html, height=0)
        
        # 予備：標準のオーディオプレイヤーも小さく表示（確実に鳴らすため）
        st.audio(fp, format='audio/mp3')

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
    <div style="background-color: #f0f2f6; padding: 30px; border-radius: 15px; border-left: 10px solid #005088; text-align: center; margin-bottom: 10px;">
        <div style="font-size: 26px; font-weight: bold; color: #333;">{english_text}</div>
        <hr>
        <div style="font-size: 18px; color: #666;">{japanese_text}</div>
    </div>
    """, unsafe_allow_html=True)

# --- 実行ロジック ---
if st.session_state.mode == "手動":
    # 手動モードはボタンを押した時だけ鳴らす
    if st.button("▶️ 英語を再生", use_container_width=True):
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

else:
    # オートモードは表示された瞬間に鳴らす
    play_audio(english_text)
    
    if st.button("⏹️ 停止して手動に戻る", use_container_width=True, type="primary"):
        st.session_state.mode = "手動"
        st.rerun()
    
    wait_time = st.slider("切替間隔（秒）", 3, 15, 7)
    
    # 自動遷移JavaScript
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
    st.session_state.index = (st.session_state.index + 1) % len(df)

st.divider()
