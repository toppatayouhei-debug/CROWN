import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import base64
import time

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

# --- 音声生成関数 ---
def play_audio(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    st.audio(fp, format='audio/mp3', autoplay=True)

# --- タイトル ---
st.title("🔊 CROWN音読ツール")

# --- モード選択（ボタンを大きく） ---
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

# --- メイン表示エリア ---
# オートモードの時はここを動的に書き換えるためのプレースホルダー
placeholder = st.empty()

def display_card(idx):
    eng = str(df.iloc[idx, 0])
    jp = str(df.iloc[idx, 1])
    with placeholder.container():
        st.write(f"📍 {idx + 1} / {len(df)} 枚目")
        st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 30px; border-radius: 15px; border-left: 10px solid #005088; text-align: center; margin-bottom: 20px;">
                <div style="font-size: 26px; font-weight: bold; color: #333;">{eng}</div>
                <hr style="margin: 20px 0;">
                <div style="font-size: 18px; color: #666;">{jp}</div>
            </div>
            """, unsafe_allow_html=True)
        # 音声再生
        play_audio(eng)

# --- モード別実行ロジック ---

if st.session_state.mode == "手動":
    display_card(st.session_state.index)
    
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("⬅️ 前へ", use_container_width=True):
            st.session_state.index = (st.session_state.index - 1) % len(df)
            st.rerun()
    with col_nav2:
        if st.button("次へ ➡️", use_container_width=True):
            st.session_state.index = (st.session_state.index + 1) % len(df)
            st.rerun()
    
    if st.button("⏮️ 先頭に戻る", use_container_width=True):
        st.session_state.index = 0
        st.rerun()

else:
    # --- オートモード（ここが確実な切り替えロジック） ---
    # 停止ボタンを先に配置
    if st.button("⏹️ オートを停止して手動に戻る", use_container_width=True, type="primary"):
        st.session_state.mode = "手動"
        st.rerun()
    
    st.info("🤖 5秒間隔で自動再生中...")
    
    # Pythonのループで1枚ずつ表示・待機
    # セッション状態のindexからスタートして最後まで行く
    for i in range(st.session_state.index, len(df)):
        st.session_state.index = i
        display_card(i)
        time.sleep(5)  # 5秒固定
        
        # 最後のカードが終わったら先頭に戻る
        if i == len(df) - 1:
            st.session_state.index = 0
            st.rerun()
