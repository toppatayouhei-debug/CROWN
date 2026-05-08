import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import base64
import json

st.set_page_config(page_title="CROWN Buddy", layout="centered")

# --- 1. データの読み込み ---
@st.cache_data
def load_all_data():
    try:
        df_text = pd.read_csv("data.csv").fillna("")
        text_list = df_text.values.tolist()
    except:
        text_list = [["Error", "data.csvが見つかりません"]]

    try:
        df_tango = pd.read_csv("crowntango.csv").fillna("")
        while len(df_tango.columns) < 4:
            df_tango[f'col_{len(df_tango.columns)}'] = ""
        tango_list = df_tango.values.tolist()
    except:
        tango_list = [["Error", "crowntango.csvなし", "", ""]]
        
    return text_list, tango_list

text_raw, tango_raw = load_all_data()

# --- 2. 音声パック (ロジック維持) ---
@st.cache_data
def prepare_assets(raw_data, is_tango=False):
    prepared = []
    for item in raw_data:
        eng_text = str(item[0])
        tts = gTTS(text=eng_text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        
        entry = {
            "eng": eng_text,
            "jp": str(item[1]),
            "audio": f"data:audio/mp3;base64,{b64}"
        }
        if is_tango:
            entry["ex"] = str(item[2])
            entry["ext"] = str(item[3])
        prepared.append(entry)
    return prepared

# 怖い🤖を廃止し、可愛いローディングに変更
with st.spinner("✨ Buddyが教材を可愛く準備中..."):
    text_json = json.dumps(prepare_assets(text_raw, False))
    tango_json = json.dumps(prepare_assets(tango_raw, True))

# --- 可愛いミニロボット付きタイトル ---
# SVGで小さな、角の丸い愛らしいロボットを描画
robot_svg = """
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle; margin-right: 10px;">
<rect x="2" y="6" width="20" height="15" rx="4" fill="#4a90e2"/>
<circle cx="7.5" cy="11.5" r="1.5" fill="white"/>
<circle cx="16.5" cy="11.5" r="1.5" fill="white"/>
<rect x="9" y="16" width="6" height="2" rx="1" fill="white"/>
<path d="M12 2V6" stroke="#4a90e2" stroke-width="2" stroke-linecap="round"/>
<circle cx="12" cy="2" r="1" fill="#ff6b6b"/>
</svg>
"""

st.markdown(f"""
    <div style='text-align: center; display: flex; justify-content: center; align-items: center; margin-bottom: 20px;'>
        {robot_svg}
        <h1 style='color: #4a90e2; font-family: Comic Sans MS, cursive; margin: 0; font-size: 32px;'>CROWN Buddy</h1>
    </div>
""", unsafe_allow_html=True)

# --- 3. メインUI ---
st.components.v1.html(f"""
    <div id="study-app" style="font-family: 'Hiragino Maru Gothic ProN', 'Rounded Mplus 1c', sans-serif; color: #444; max-width: 550px; margin: auto;">
        
        <div style="display: flex; background: #e0e6ed; padding: 6px; border-radius: 20px; margin-bottom: 20px; box-shadow: inset 0 2px 5px rgba(0,0,0,0.05);">
            <button id="mode-text" style="flex: 1; padding: 12px; border-radius: 16px; border: none; background: #4a90e2; color: white; font-weight: bold; font-size: 14px; cursor: pointer; transition: 0.3s; font-family: inherit;">📖 本文音読</button>
            <button id="mode-tango" style="flex: 1; padding: 12px; border-radius: 16px; border: none; background: transparent; color: #555; font-weight: bold; font-size: 14px; cursor: pointer; transition: 0.3s; font-family: inherit;">🗂️ 単語カード</button>
        </div>

        <div style="display: flex; gap: 8px; margin-bottom: 20px; justify-content: center;">
            <button id="btn-manual" style="padding: 10px 20px; border-radius: 20px; border: 1px solid #ddd; background: #fff; color: #555; font-size: 12px; font-weight: bold; cursor: pointer; transition: 0.3s;">👆手動</button>
            <button id="btn-auto" style="padding: 10px 20px; border-radius: 20px; border: 1px solid #ddd; background: #fff; color: #555; font-size: 12px; font-weight: bold; cursor: pointer; transition: 0.3s;">🤖オート</button>
            <button id="btn-random" style="padding: 10px 20px; border-radius: 20px; border: 1px solid #ddd; background: #fff; color: #555; font-size: 12px; font-weight: bold; cursor: pointer; transition: 0.3s;">🔀ランダム</button>
        </div>

        <div id="card" style="background: #ffffff; padding: 40px 25px; border-radius: 30px; text-align: center; min-height: 280px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 10px 25px rgba(74,144,226,0.1); border: 2px solid #f0f4f8; transition: 0.3s; position: relative;">
            <div style="position: absolute; top: 15px; left: 15px; width: 12px; height: 12px; background: #4a90e2; border-radius: 50%;"></div>
            <div id="eng" style="font-size: 30px; font-weight: 800; margin-bottom: 15px; color: #2c3e50; line-height: 1.2;"></div>
            
            <div id="jp-container">
                <div id="jp" style="font-size: 19px; color: #7f8c8d; font-weight: bold; line-height: 1.3;"></div>
                <div id="tango-extra" style="display: none; border-top: 1px solid #eee; margin-top: 20px; padding-top: 20px;">
                    <div id="ex" style="font-size: 16px; color: #4a90e2; font-weight: 500; font-style: italic; margin-bottom: 10px; line-height: 1.4;"></div>
                    <div id="ext" style="font-size: 14px; color: #95a5a6; line-height: 1.4;"></div>
                </div>
            </div>

            <button id="btn-show" style="display: none; margin: 25px auto 0; padding: 12px 30px; border-radius: 25px; border: none; background: #4a90e2; color: white; font-weight: bold; cursor: pointer; font-size: 14px; box-shadow: 0 4px 10px rgba(74,144,226,0.3); transition: 0.3s;">🔍 意味をチェック</button>
        </div>

        <div id="nav-controls" style="margin-top: 30px; display: flex; gap: 20px; justify-content: center;">
            <button id="btn-prev" style="width: 70px; height: 70px; border-radius: 50%; background: #fff; border: 1px solid #eee; font-size: 28px; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.05); transition: 0.2s; -webkit-tap-highlight-color: transparent;">⬅️</button>
            <button id="btn-next" style="width: 70px; height: 70px; border-radius: 50%; background: #fff; border: 1px solid #eee; font-size: 28px; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.05); transition: 0.2s; -webkit-tap-highlight-color: transparent;">➡️</button>
        </div>

        <div id="auto-extra" style="display: none; margin-top: 20px;">
            <button id="btn-stop" style="width: 100%; padding: 16px; border-radius: 20px; background: #ff6b6b; color: white; border: none; font-weight: bold; font-size: 15px; cursor: pointer; box-shadow: 0 4px 10px rgba(255,107,107,0.3);">⏹️ オート停止</button>
        </div>

        <div style="margin-top: 30px; text-align: center;">
            <div id="status" style="font-size: 14px; color: #bdc3c7; font-weight: bold; letter-spacing: 1px;"></div>
        </div>
    </div>

    <script>
        const textData = {text_json};
        const tangoData = {tango_json};
        let currentDataSet = textData;
        let index = 0;
        let isAuto = false;
        let isRandom = false;
        let currentAudio = new Audio();
        let timer = null;
        let currentMode = 'text';

        function updateCard(shouldPlay = true) {{
            const item = currentDataSet[index];
            document.getElementById('eng').innerText = item.eng;
            document.getElementById('jp').innerText = item.jp;
            
            const extra = document.getElementById('tango-extra');
            const showBtn = document.getElementById('btn-show');
            const jpContainer = document.getElementById('jp-container');

            if (currentMode === 'tango') {{
                document.getElementById('jp').style.color = "#e056fd";
                document.getElementById('ex').innerText = item.ex || "";
                document.getElementById('ext').innerText = item.ext || "";
                
                if (isAuto) {{
                    jpContainer.style.display = "block";
                    extra.style.display = "block";
                    showBtn.style.display = "none";
                }} else {{
                    jpContainer.style.display = "none";
                    extra.style.display = "none";
                    showBtn.style.display = "block";
                }}
            }} else {{
                document.getElementById('jp').style.color = "#7f8c8d";
                jpContainer.style.display = "block";
                extra.style.display = "none";
                showBtn.style.display = "none";
            }}

            document.getElementById('status').innerText = (index + 1) + " / " + currentDataSet.length;
            if (shouldPlay) playAudio(item.audio);
        }}

        function playAudio(src) {{
            if (timer) clearTimeout(timer);
            currentAudio.pause();
            currentAudio.src = src;
            currentAudio.play().then(() => {{
                currentAudio.onended = () => {{
                    if (isAuto) {{
                        const delay = currentMode === 'text' ? 2200 : 3200;
                        timer = setTimeout(() => {{
                            if (!isAuto) return;
                            nextCard();
                        }}, delay);
                    }}
                }};
            }}).catch(e => console.log("Play blocked"));
        }}

        function nextCard() {{
            if (isRandom) {{
                index = Math.floor(Math.random() * currentDataSet.length);
            }} else {{
                index = (index + 1) % currentDataSet.length;
            }}
            updateCard();
        }}

        document.getElementById('btn-show').onclick = () => {{
            document.getElementById('jp-container').style.display = "block";
            document.getElementById('tango-extra').style.display = "block";
            document.getElementById('btn-show').style.display = "none";
        }};

        document.getElementById('btn-random').onclick = () => {{
            isRandom = !isRandom;
            updateUI();
        }};

        document.getElementById('mode-text').onclick = () => {{
            currentMode = 'text'; currentDataSet = textData; index = 0; isAuto = false;
            updateUI(); updateCard(false);
        }};
        document.getElementById('mode-tango').onclick = () => {{
            currentMode = 'tango'; currentDataSet = tangoData; index = 0; isAuto = false;
            updateUI(); updateCard(false);
        }};

        document.getElementById('btn-next').onclick = () => {{ isAuto = false; nextCard(); updateUI(); }};
        document.getElementById('btn-prev').onclick = () => {{ isAuto = false; index = (index - 1 + currentDataSet.length) % currentDataSet.length; updateCard(); updateUI(); }};
        document.getElementById('btn-auto').onclick = () => {{ isAuto = true; updateUI(); updateCard(); }};
        document.getElementById('btn-manual').onclick = () => {{ isAuto = false; updateUI(); updateCard(false); }};
        document.getElementById('btn-stop').onclick = () => {{ isAuto = false; currentAudio.pause(); updateUI(); }};

        function updateUI() {{
            const isText = (currentMode === 'text');
            const modeText = document.getElementById('mode-text');
            const modeTango = document.getElementById('mode-tango');

            modeText.style.background = isText ? '#4a90e2' : 'transparent';
            modeText.style.color = isText ? 'white' : '#555';
            modeTango.style.background = isText ? 'transparent' : '#4a90e2';
            modeTango.style.color = isText ? '#555' : 'white';
            
            const btnManual = document.getElementById('btn-manual');
            const btnAuto = document.getElementById('btn-auto');
            const btnRandom = document.getElementById('btn-random');

            btnManual.style.background = isAuto ? '#fff' : '#333';
            btnManual.style.color = isAuto ? '#555' : '#fff';
            btnManual.style.border = isAuto ? '1px solid #ddd' : '1px solid #333';

            btnAuto.style.background = isAuto ? '#4a90e2' : '#fff';
            btnAuto.style.color = isAuto ? '#fff' : '#555';
            btnAuto.style.border = isAuto ? '1px solid #4a90e2' : '1px solid #ddd';

            btnRandom.style.background = isRandom ? '#f39c12' : '#fff';
            btnRandom.style.color = isRandom ? '#fff' : '#555';
            btnRandom.style.border = isRandom ? '1px solid #f39c12' : '1px solid #ddd';
            
            document.getElementById('auto-extra').style.display = isAuto ? 'block' : 'none';
        }}

        // iPadでのホバー時の色残りを防止
        const btns = document.querySelectorAll('button');
        btns.forEach(btn => {{
            btn.addEventListener('touchstart', () => {{ btn.style.transform = 'scale(0.98)'; }});
            btn.addEventListener('touchend', () => {{ btn.style.transform = 'scale(1)'; }});
        }});

        updateCard(false);
    </script>
""", height=720)
