import streamlit as st
import pandas as pd
from gtts import gTTS
import io

# ページの設定
st.set_page_config(page_title="CROWN読み上げアプリ", layout="wide", page_icon="🔊")

st.title("🔊 CROWN読み上げアプリ")

# --- 設定：CSVファイルを読み込む ---
CSV_FILE = "data.csv"

@st.cache_data
def load_data():
    try:
        # header=0（1行目を見出しとして扱う）だが、番号で指定するので名前は何でも良くなる
        df = pd.read_csv(CSV_FILE)
        return df
    except Exception as e:
        return pd.DataFrame([["Error", "CSVファイルが見つかりません"]])

# データの読み込み
df = load_data()

# リストの表示と読み上げ機能
for i, row in df.iterrows():
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        
        # --- ここがポイント：iloc[0] (0番目の列) と iloc[1] (1番目の列) で指定 ---
        try:
            english_text = str(row.iloc[0])
            japanese_text = str(row.iloc[1])
        except Exception:
            continue # データが足りない行はスキップ

        with col1:
            st.subheader(f"Sentence {i+1}")
            st.write(f"**{english_text}**")  # 左側の列を表示
            st.info(japanese_text)          # 右側の列を表示
        
        with col2:
            # 読み上げボタン
            if st.button(f"再生", key=f"btn_{i}"):
                tts = gTTS(text=english_text, lang='en')
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                st.audio(audio_fp, format='audio/mp3', autoplay=True)

st.divider()
st.caption("Developed with Streamlit & gTTS")
