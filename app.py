import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import base64
import json

st.set_page_config(page_title="CROWN Buddy", layout="centered")

# --- 1. データの読み込み（ロジック維持） ---
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

# --- 2. 音声パック（ロジック維持） ---
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

with st.spinner("✨ Buddyが準備中..."):
    text_json = json.dumps(prepare_assets(text_raw, False))
    tango_json = json.dumps(prepare_assets(tango_raw, True))

# --- シンプルなタイトル（ここを変更しました） ---
# 記号の 🤖 を使い、最も標準的な書き方にしました
st.markdown("<h1 style='text-align: center; color: #4a90e2;'>🤖 CROWN Buddy</h1>", unsafe_allow_html=True)

# --- 3. メインUI ---
st.components.v1.html(f"""
    <style>
        @keyframes glow {{
            0% {{ box-shadow: 0 10px 25px rgba(74,144,226,0.1); border-color: #f0f4f8; }}
            50% {{ box-shadow: 0 0 30px rgba(74,144,226,0.5); border-color: #4a90e2; }}
            100% {{ box-shadow: 0 10px 25px rgba(74,144,226,0.1); border-color: #f0f4f8; }}
        }}
        .playing {{
            animation: glow 1.5s infinite ease-in-out;
        }}
    </style>

    <div id="study-app" style="font-family: sans-serif; color: #444; max-width: 550px; margin: auto;">
        
        <div style="display: flex; background: #e0e6ed; padding: 6px; border-radius: 20px; margin-bottom: 20px;">
            <button id="mode-text" style="flex: 1; padding: 12px; border-radius: 16px; border: none; background: #4a90e2; color: white; font-weight: bold; cursor: pointer;">📖 本文音読</button>
            <button id="mode-tango" style="flex: 1; padding: 12px; border-radius: 16px; border: none; background: transparent; color: #555; font-weight: bold; cursor: pointer;">🗂️ 単語カード</button>
        </div>

        <div style="display: flex; gap: 8px; margin-bottom: 20px; justify-content: center;">
            <button id="btn-manual" style="padding: 10px 20px; border-radius: 20px; border: 1px solid #ddd; background: #fff; color: #555; font-size: 12px; font-weight: bold;">👆手動</button>
            <button id="btn-auto" style="padding: 10px 20px; border-radius: 20px; border: 1px solid #ddd; background: #fff; color: #555; font-size: 12px; font-weight: bold;">🤖オート</button>
            <button id="btn-random" style="padding: 10px 20px; border-radius: 20px; border: 1px solid #ddd; background: #fff; color: #555; font-size: 12px; font-weight: bold;">🔀ランダム</button>
        </div>

        <div id="card" style="background: #ffffff; padding: 40px 25px; border-radius: 30px; text-align: center; min-height: 280px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 10px 25px rgba(74,144,226,0.1); border: 2px solid #f0f4f8; position: relative; transition: 0.3s;">
            <div style="position: absolute; top: 15px; left: 15px; width: 12px; height: 12px; background: #4a90e2; border-radius: 50%;"></div>
            <div id="eng" style="font-size: 28px; font-weight: 800; margin-bottom: 15px; color: #2c3e50; line-height: 1.2;"></div>
            
            <div id="jp-container">
                <div id="jp" style="font-size: 18px; color: #7f8c8d; font-weight: bold; line-height: 1.3;"></div>
                <div id="tango-extra" style="display: none; border-top: 1px solid #eee; margin-top: 20px; padding-top: 20px;">
                    <div id="ex" style="font-size: 16px; color: #4a90e2; font-weight: 500; font-style: italic; margin-bottom: 10px;"></div>
                    <div id="ext" style="font-size: 14px; color: #95a5a6;"></div>
                </div>
            </div>

            <button id="btn-show" style="display: none; margin: 25px auto 0; padding: 12px 30px; border-radius: 25px; border: none; background: #4a90e2; color: white; font-weight: bold; cursor: pointer; font-size: 14px;">🔍 意味をチェック</button>
        </div>

        <div id="nav-controls" style="margin-top: 30px; display: flex; gap: 20px; justify-content: center;">
            <button id="btn-prev" style="width: 70px; height: 70px; border-radius: 50%; background: #fff; border: 1px solid #eee; font-size: 28px; cursor: pointer;">⬅️</button>
            <button id="btn-next" style="width: 70px; height: 70px; border-radius: 50%; background: #fff; border: 1px solid #eee; font-size: 28px; cursor: pointer;">➡️</button>
        </div>

        <div id="auto-extra" style="display: none; margin-top: 20px;">
            <button id="btn-stop" style="width: 100%; padding: 16px; border-radius: 20px; background: #ff6b6b; color: white; border: none; font-weight: bold;">⏹️ オート停止</button>
        </div>

        <div style="margin-top: 30px; text-align: center;">
            <div id="status" style="font-size: 14px; color: #bdc3c7; font-weight: bold;"></div>
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
            
            const card = document.getElementById('card');
            card.classList.add('playing');

            currentAudio.play().then(() => {{
                currentAudio.onended = () => {{
                    card.classList.remove('playing');
                    if (isAuto) {{
                        const delay = currentMode === 'text' ? 2200 : 3200;
                        timer = setTimeout(() => {{
                            if (!isAuto) return;
                            nextCard();
                        }}, delay);
                    }}
                }};
            }}).catch(e => {{
                card.classList.remove('playing');
                console.log("Play blocked");
            }});
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
        document.getElementById('btn-stop').onclick = () => {{ 
            isAuto = false; 
            currentAudio.pause(); 
            document.getElementById('card').classList.remove('playing');
            updateUI(); 
        }};

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
            btnAuto.style.background = isAuto ? '#4a90e2' : '#fff';
            btnAuto.style.color = isAuto ? '#fff' : '#555';
            btnRandom.style.background = isRandom ? '#f39c12' : '#fff';
            btnRandom.style.color = isRandom ? '#fff' : '#555';
            
            document.getElementById('auto-extra').style.display = isAuto ? 'block' : 'none';
        }}

        updateCard(false);
    </script>
""", height=720)
