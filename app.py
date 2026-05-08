import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import time

# ページの設定
st.set_page_config(page_title="CROWN音読ツール", layout="centered")

# --- データの読み込み ---
@st.cache_data
def load_data():
    try:
        # A2, B2から読み込み（1行目はヘッダー）
        return pd.read_csv("data.csv")
    except:
        return pd.DataFrame([["Error", "CSV読み込み失敗"]])

df = load_data()

# --- セッション状態の初期化 ---
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'mode' not in st.session_state:
    st.session_state.mode = "手動"

st.title("🔊 CROWN音読ツール")

# --- モード選択 ---
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
def display_card(idx):
    eng = str(df.iloc[idx, 0])
    jp = str(df.iloc[idx, 1])
    
    st.write(f"📍 {idx + 1} / {len(df)} 枚目")
    st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 30px; border-radius: 15px; border-left: 10px solid #005088; text-align: center; margin-bottom: 20px;">
            <div style="font-size: 26px; font-weight: bold; color: #333;">{eng}</div>
            <hr style="margin: 20px 0;">
            <div style="font-size: 18px; color: #666;">{jp}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 音声を生成して再生
    tts = gTTS(text=eng, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    st.audio(fp, format='audio/mp3', autoplay=True)

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
    # --- オートモード ---
    if st.button("⏹️ オートを停止して手動に戻る", use_container_width=True, type="primary"):
        st.session_state.mode = "手動"
        st.rerun()

    # 現在のカードを表示・再生
    display_card(st.session_state.index)
    
    # 英文の長さに合わせて待機時間を調整（1秒間に3単語＋余裕2秒）
    # 固定5秒だと長い文が途切れるため、文字数で計算します
    eng_text = str(df.iloc[st.session_state.index, 0])
    wait_seconds = max(5, len(eng_text.split()) / 2 + 3) 
    
    st.info(f"⏳ 次のカードまで約 {int(wait_seconds)} 秒待機します...")
    
    # 指定時間待機してからリロードして次へ
    time.sleep(wait_seconds)
    st.session_state.index = (st.session_state.index + 1) % len(df)
    st.rerun()
