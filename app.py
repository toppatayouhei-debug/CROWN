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
    st.session_state.mode = "待機"

# --- 音声生成関数 ---
def get_audio_html(text, auto_next=False):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    b64 = base64.b64encode(fp.read()).decode()
    
    if auto_next:
        # オートモード用：再生終了後に hidden_next_btn をクリック
        return f"""
            <audio id="audio-player" autoplay src="data:audio/mp3;base64,{b64}"></audio>
            <script>
                var audio = document.getElementById('audio-player');
                audio.onended = function() {{
                    setTimeout(function() {{
                        window.parent.document.getElementById('hidden_next_btn').click();
                    }}, 1000);
                }};
            </script>
        """
    else:
        # 手動モード用：再生のみ
        return f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>'

# --- メイン画面 ---
st.title("🔊 CROWN音読ツール")

# 1. 待機画面（ブラウザの音声ブロック解除用）
if st.session_state.mode == "待機":
    st.info("下のボタンを押して音読を開始してください。")
    if st.button("🚀 学習をスタートする", use_container_width=True):
        st.session_state.mode = "手動"
        st.rerun()
    st.stop()

# 2. モード切替ボタン
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

# --- モード別実行ロジック ---
if st.session_state.mode == "手動":
    st.components.v1.html(get_audio_html(eng), height=0)
    
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
    st.info("🤖 読み上げが終了すると自動で次へ進みます...")
    if st.button("⏹️ オートを停止", use_container_width=True, type="primary"):
        st.session_state.mode = "手動"
        st.rerun()

    # 自動更新用ボタン（IDを指定してJSから確実に叩く。かつ、CSSではなくStreamlitの機能で隠す）
    if st.button("NEXT", key="hidden_next"):
        st.session_state.index = (st.session_state.index + 1) % len(df)
        st.rerun()
    
    st.components.v1.html(get_audio_html(eng, auto_next=True), height=0)

# --- 最後の仕上げ：自動更新ボタンを「ID」で指定して透明にする ---
# これなら他のボタンに影響を与えません
st.markdown("""
    <script>
        // ボタンにIDを付与する（強引ですが確実です）
        var btns = window.parent.document.querySelectorAll('button');
        for (var i = 0; i < btns.length; i++) {
            if (btns[i].innerText === 'NEXT') {
                btns[i].id = 'hidden_next_btn';
                btns[i].style.display = 'none'; // 見えなくする
            }
        }
    </script>
    """, unsafe_allow_html=True)

st.divider()
if st.button("⏮️ 先頭に戻る", use_container_width=True):
    st.session_state.index = 0
    st.rerun()
