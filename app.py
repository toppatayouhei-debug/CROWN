import streamlit as st
import pandas as pd
from gtts import gTTS
import io

# ページの設定
st.set_page_config(page_title="CROWN読み上げアプリ", layout="wide", page_icon="🔊")

st.title("🔊 CROWN読み上げアプリ")

# --- 設定：CSVファイルを読み込む ---
# アップロードしたファイル名が「data.csv」ならこのままでOK
CSV_FILE = "data.csv"

@st.cache_data
def load_data():
    try:
        # GitHubにアップロードしたCSVファイルを読み込む
        df = pd.read_csv(CSV_FILE)
        return df
    except Exception as e:
        # エラーが出た場合のダミーデータ
        return pd.DataFrame([
            {"English": "Error: data.csv not found", "Japanese": "data.csvが見つかりません。GitHubにアップロードされているか確認してください。"}
        ])

# データの読み込み
df = load_data()

# リストの表示と読み上げ機能
for i, row in df.iterrows():
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # CSVの1行目の見出しが「English」「Japanese」である必要があります
            st.subheader(f"Sentence {i+1}")
            st.write(f"**{row['English']}**")
            st.info(row['Japanese'])
        
        with col2:
            if st.button(f"再生", key=f"btn_{i}"):
                tts = gTTS(text=str(row['English']), lang='en')
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                st.audio(audio_fp, format='audio/mp3', autoplay=True)

st.divider()
st.caption("Developed with Streamlit & gTTS")
