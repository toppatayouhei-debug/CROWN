import streamlit as st
import pandas as pd
from gtts import gTTS
import io

# ページの設定：タイトルを「CROWN読み上げアプリ」に変更
st.set_page_config(page_title="CROWN読み上げアプリ", layout="wide", page_icon="🔊")

# デザインの調整（CSSで文字サイズなどを微調整）
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #005088;
        color: white;
    }
    </style>
    """, unsafe_allow_stdio=True)

st.title("🔊 CROWN読み上げアプリ")
st.write("スプレッドシートを更新すると、自動で最新の英文リストが表示されます。")

# --- 設定：スプレッドシートのURL ---
# 末尾が /export?format=csv になっているか確認してください
SHEET_URL = "https://docs.google.com/spreadsheets/d/1qyQham1gCOYqnQSeIZwLWYyf8guYTeECxXNC1hTEhwY/export?format=csv"

@st.cache_data(ttl=600) # 10分間キャッシュを保持
def load_data(url):
    try:
        return pd.read_csv(url)
    except Exception as e:
        return pd.DataFrame([
            {"English": "Welcome to CROWN Reading App!", "Japanese": "アプリへようこそ！スプレッドシートを接続してください。"}
        ])

# データの読み込み
df = load_data(SHEET_URL)

# リストの表示
for i, row in df.iterrows():
    with st.container():
        # 枠のデザインを適用
        st.markdown(f"### Section {i+1}")
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.info(f"**{row['English']}**")
            st.write(f"*{row['Japanese']}*")
        
        with col2:
            if st.button(f"再生", key=f"btn_{i}"):
                tts = gTTS(text=row['English'], lang='en')
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                st.audio(audio_fp, format='audio/mp3', autoplay=True)
        st.divider()

st.caption("Developed with Streamlit & gTTS")
