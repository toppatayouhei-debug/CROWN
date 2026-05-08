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

# --- 学習モード選択（大きなボタン） ---
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

# --- 音声再生用関数（HTML埋め込み方式） ---
def play_audio_html(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    b64 = base64.b64encode(fp.read()).decode()
    md = f"""
        <audio autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.components.v1.html(md, height=0)

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

# --- 実行ロジック ---

if st.session_state.mode == "手動":
    # 手動モード
    play_audio_html(english_text)
    
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
    st.info(f"🤖 オート再生中... ({st.session_state.index + 1} / {len(df)})")
    play_audio_html(english_text)
    
    # 停止ボタンを大きく配置
    if st.button("⏹️ オートを停止して手動に戻る", use_container_width=True, type="primary"):
        st.session_state.mode = "手動"
        st.rerun()
    
    # 再生速度の設定
    wait_time = st.slider("次のカードまでの間隔（秒）", 3, 12, 6)
    
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
    # 描画の裏側でインデックスを次に進めておく
    st.session_state.index = (st.session_state.index + 1) % len(df)

st.divider()
st.caption(f"Progress: {st.session_state.index + 1} / {len(df)}")
