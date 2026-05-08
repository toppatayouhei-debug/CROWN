import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import base64
import json

st.set_page_config(page_title="CROWN Study Hub", layout="centered")

# --- 1. データの読み込み（以前の構成を完全維持） ---
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

# --- 2. 音声パック（iPad安定版ロジックを完全継承） ---
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

with st.spinner("教材を読み込み中..."):
    text_json = json.dumps(prepare_assets(text_raw, False))
    tango_json = json.dumps(prepare_assets(tango_raw, True))

st.title("🎓 CROWN Study Hub")

# --- 3. 画面表示（本文音読の挙動を維持しつつ、テスト機能を追加） ---
st.components.v1.html(f"""
    <div id="study-app" style="font-family: -apple-system, sans-serif; color: #333;">
        
        <div style="display: flex; background: #eee; padding: 5px; border-radius: 12px; margin-bottom: 20px;">
            <button id="mode-text" style="flex: 1; padding: 12px; border-radius: 10px; border: none; background: #005088; color: white; font-weight: bold;">📖 本文音読</button>
            <button id="mode-tango" style="flex: 1; padding: 12px; border-radius: 10px; border: none; background: transparent; color: #333; font-weight: bold;">🗂️ 単語カード</button>
        </div>

        <div style="display: flex; gap: 8px; margin-bottom: 20px;">
            <button id="btn-manual" style="flex: 1; padding: 12px; border-radius: 10px; border: none; background: #333; color: white; font-weight: bold;">👆 手動</button>
            <button id="btn-auto" style="flex: 1; padding: 12px; border-radius: 10px; border: none; background: #eee; color: #333; font-weight: bold;">🤖 オート</button>
        </div>

        <div id="card" style="background: #f8f9fa; padding: 35px 20px; border-radius: 25px; border-left: 12px solid #005088; text-align: center; min-height: 280px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 6px 15px rgba(0,0,0,0.1);">
            <div id="eng" style="font-size: 28px; font-weight: 800; margin-bottom: 10px;"></div>
            
            <div id="jp-container">
                <div id="jp" style="font-size: 18px; color: #666; font-weight: bold;"></div>
                <div id="tango-extra" style="display: none; border-top: 1px solid #ddd; margin-top: 15px; padding-top: 15px;">
                    <div id="ex" style="font-size: 16px; color: #005088; font-weight: 500; font-style: italic; margin-bottom: 5px;"></div>
                    <div id="ext" style="font-size: 14px; color: #6c757d;"></div>
                </div>
            </div>

            <button id="btn-show" style="display: none; margin: 20px auto 0; padding: 10px 20px; border-radius: 20px; border: 2px solid #005088; background: white; color: #005088; font-weight: bold; cursor: pointer;">👀 答えを見る</button>
        </div>

        <div id="nav-controls" style="margin-top: 25px; display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <button id="btn-prev" style="padding: 22px; border-radius: 15px; background: white; border: 1px solid #ddd; font-size: 26px;">⬅️</button>
            <button id="btn-next" style="padding: 22px; border-radius: 15px; background: white; border: 1px solid #ddd; font-size: 26px;">➡️</button>
        </div>

        <div id="auto-extra" style="display: none; margin-top: 15px;">
            <button id="btn-stop" style="width: 100%; padding: 18px; border-radius: 15px; background: #dc3545; color: white; border: none; font-weight: bold;">⏹️ オート停止</button>
        </div>

        <div style="margin-top: 25px; text-align: center;">
            <div id="status" style="font-size: 14px; color: #adb5bd; font-weight: bold;"></div>
        </div>
    </div>

    <script>
        const textData = {text_json};
        const tangoData = {tango_json};
        let currentDataSet = textData;
        let index = 0;
        let isAuto = false;
        let timer = null;
        let currentAudio = new Audio();
        let currentMode = 'text';
        let isRevealed = false; // 答えが表示されているか

        function updateCard(shouldPlay = true) {{
            const item = currentDataSet[index];
            document.getElementById('eng').innerText = item.eng;
            document.getElementById('jp').innerText = item.jp;
            
            const extra = document.getElementById('tango-extra');
            const showBtn = document.getElementById('btn-show');
            const jpContainer = document.getElementById('jp-container');

            if (currentMode === 'tango') {{
                document.getElementById('jp').style.color = "#d63384";
                document.getElementById('ex').innerText = item.ex || "";
                document.getElementById('ext').innerText = item.ext || "";
                
                // オートモードなら最初から表示、手動なら隠す
                if (isAuto) {{
                    jpContainer.style.display = "block";
                    extra.style.display = "block";
                    showBtn.style.display = "none";
                }} else {{
                    jpContainer.style.display = "none";
                    extra.style.display = "none";
                    showBtn.style.display = "block";
                    isRevealed = false;
                }}
            }} else {{
                // 本文音読モード（以前の挙動を完全維持）
                document.getElementById('jp').style.color = "#666";
                jpContainer.style.display = "block";
                extra.style.display = "none";
                showBtn.style.display = "none";
            }}

            document.getElementById('status').innerText = (index + 1) + " / " + currentDataSet.length;
            if (shouldPlay) playAudio(item.audio);
        }}

        // 答えを表示する処理
        document.getElementById('btn-show').onclick = () => {{
            document.getElementById('jp-container').style.display = "block";
            document.getElementById('tango-extra').style.display = "block";
            document.getElementById('btn-show').style.display = "none";
            isRevealed = true;
        }};

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
                            index = (index + 1) % currentDataSet.length;
                            updateCard();
                        }}, delay);
                    }}
                }};
            }}).catch(e => console.log("Blocked"));
        }}

        document.getElementById('mode-text').onclick = () => {{
            currentMode = 'text'; currentDataSet = textData; index = 0; isAuto = false;
            updateUI(); updateCard(false);
        }};
        document.getElementById('mode-tango').onclick = () => {{
            currentMode = 'tango'; currentDataSet = tangoData; index = 0; isAuto = false;
            updateUI(); updateCard(false);
        }};

        document.getElementById('btn-next').onclick = () => {{ isAuto = false; index = (index + 1) % currentDataSet.length; updateCard(); updateUI(); }};
        document.getElementById('btn-prev').onclick = () => {{ isAuto = false; index = (index - 1 + currentDataSet.length) % currentDataSet.length; updateCard(); updateUI(); }};
        document.getElementById('btn-auto').onclick = () => {{ isAuto = true; updateUI(); updateCard(); }};
        document.getElementById('btn-manual').onclick = () => {{ isAuto = false; updateUI(); updateCard(false); }};
        document.getElementById('btn-stop').onclick = () => {{ isAuto = false; currentAudio.pause(); updateUI(); }};

        function updateUI() {{
            const isText = (currentMode === 'text');
            document.getElementById('mode-text').style.background = isText ? '#005088' : 'transparent';
            document.getElementById('mode-text').style.color = isText ? 'white' : '#333';
            document.getElementById('mode-tango').style.background = isText ? 'transparent' : '#005088';
            document.getElementById('mode-tango').style.color = isText ? '#333' : 'white';
            
            document.getElementById('btn-manual').style.background = isAuto ? '#eee' : '#333';
            document.getElementById('btn-manual').style.color = isAuto ? '#333' : 'white';
            document.getElementById('btn-auto').style.background = isAuto ? '#005088' : '#eee';
            document.getElementById('btn-auto').style.color = isAuto ? 'white' : '#333';
            document.getElementById('auto-extra').style.display = isAuto ? 'block' : 'none';
        }}

        updateCard(false);
    </script>
""", height=680)
