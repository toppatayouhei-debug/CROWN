import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import base64
import json

st.set_page_config(page_title="CROWN音読ツール", layout="centered")

# --- データの読み込み ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv")
        return df.values.tolist()
    except:
        return [["Error", "data.csvが見つかりません"]]

data_list = load_data()
data_json = json.dumps(data_list)

# --- セッション管理 ---
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'mode' not in st.session_state:
    st.session_state.mode = "手動"

st.title("🔊 CROWN音読ツール")

# --- PCかiPadかを判別するためのJavaScript ---
# ブラウザの情報を取得してStreamlit側に送る
is_mobile = st.components.v1.html("""
<script>
    var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    window.parent.postMessage({type: 'set_mobile', value: isMobile}, '*');
</script>
""", height=0)

# デフォルトはPC（Googleボイス）として、モバイルならJS側に任せる
use_js_engine = False
ua = st.query_params.get("ua", "pc") # 簡易的な判別用（必要に応じて）

# --- メイン画面の構成 ---
# ここからはiPad/PC共通の表示エリア
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

# 現在のカードデータ
eng = data_list[st.session_state.index][0]
jp = data_list[st.session_state.index][1]

st.write(f"📍 {st.session_state.index + 1} / {len(data_list)} 枚目")
st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 40px 20px; border-radius: 20px; border-left: 10px solid #005088; text-align: center;">
        <div style="font-size: 30px; font-weight: bold; color: #333;">{eng}</div>
        <hr style="width: 50%; margin: 20px auto; border: 0.5px solid #ccc;">
        <div style="font-size: 20px; color: #666;">{jp}</div>
    </div>
    """, unsafe_allow_html=True)

# --- モード別の出し分け ---

# PCかつ手動/オートの場合は以前のGoogleボイス(gTTS)方式
# ただしiPadの場合は「すべての処理を1つのJSコンポーネント」で行う

st.components.v1.html(f"""
    <div id="controls" style="font-family: sans-serif;">
        <div id="nav" style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 20px;">
            <button id="p-prev" style="padding: 20px; border-radius: 12px; background: white; border: 1px solid #ddd; font-size: 20px;">⬅️ 前へ</button>
            <button id="p-next" style="padding: 20px; border-radius: 12px; background: white; border: 1px solid #ddd; font-size: 20px;">次へ ➡️</button>
        </div>
        <div id="auto-stop-area" style="display: none; margin-top: 15px;">
            <button id="p-stop" style="width: 100%; padding: 15px; border-radius: 12px; background: #ff4b4b; color: white; border: none; font-weight: bold;">⏹️ オートを止める</button>
        </div>
    </div>

    <script>
        const data = {data_json};
        let index = {st.session_state.index};
        let isAuto = { "true" if st.session_state.mode == "オート" else "false" };
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
        const synth = window.speechSynthesis;
        let timer = null;

        function getVoice() {{
            const vs = synth.getVoices();
            return vs.find(v => (v.name.includes('拡張') || v.name.includes('プレミアム') || v.name.includes('Enhanced') || v.name.includes('Premium') || v.name.includes('Siri')) && v.lang.includes('en')) || vs.find(v => v.lang.startsWith('en'));
        }}

        // GoogleボイスのURL生成（PC用）
        function getGoogleAudioUrl(text) {{
            return "https://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q=" + encodeURIComponent(text);
        }}

        function play() {{
            const text = data[index][0];
            if (isMobile) {{
                // iPadなら内蔵ボイス
                synth.cancel();
                const u = new SpeechSynthesisUtterance(text);
                u.voice = getVoice();
                u.lang = 'en-US';
                u.rate = 0.9;
                u.onend = () => {{ if(isAuto) timer = setTimeout(next, 2500); }};
                synth.speak(u);
            }} else {{
                // PCならGoogleボイス
                if (window.currentAudio) window.currentAudio.pause();
                const audio = new Audio(getGoogleAudioUrl(text));
                window.currentAudio = audio;
                audio.play();
                audio.onended = () => {{ if(isAuto) timer = setTimeout(next, 2500); }};
            }}
        }}

        function next() {{
            index = (index + 1) % data.length;
            syncToStreamlit();
        }}

        function syncToStreamlit() {{
            // StreamlitのURLを叩いてindexを同期させる（手動・オート両用）
            window.parent.postMessage({{type: 'set_index', value: index}}, '*');
            // 表示更新
            location.href = "?idx=" + index + "&mode=" + (isAuto ? "auto" : "manual");
        }}

        // モードに合わせてボタン表示切替
        document.getElementById('auto-stop-area').style.display = isAuto ? 'block' : 'none';
        
        document.getElementById('p-next').onclick = () => {{ isAuto = false; next(); }};
        document.getElementById('p-prev').onclick = () => {{ isAuto = false; index = (index - 1 + data.length) % data.length; syncToStreamlit(); }};
        document.getElementById('p-stop').onclick = () => {{ isAuto = false; location.href = "?idx=" + index + "&mode=manual"; }};

        // 初回再生
        setTimeout(play, 500);
    </script>
""", height=250)

# --- URLパラメータによる同期 ---
params = st.query_params
if "idx" in params:
    new_idx = int(params["idx"])
    if new_idx != st.session_state.index:
        st.session_state.index = new_idx
        # st.rerun() すると無限ループするので注意。JS側で表示を完結させている。
