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
        # リスト形式に変換してJavaScriptに渡せるようにする
        return df.values.tolist()
    except:
        return [["Error", "CSVが見つかりません"]]

data_list = load_data()

st.title("🔊 CROWN音読ツール")
st.write("iPad/iPhone対応版")

# --- メインロジック（JavaScriptで完結させる） ---
# Python側からはデータを流し込むだけで、めくり処理はブラウザ側に任せます

data_json = json.dumps(data_list)

st.components.v1.html(f"""
    <div id="study-app" style="font-family: sans-serif; color: #333;">
        <div style="display: flex; gap: 10px; margin-bottom: 20px;">
            <button id="btn-manual" style="flex: 1; padding: 15px; border-radius: 10px; border: none; background: #005088; color: white; font-weight: bold;">👆 手動モード</button>
            <button id="btn-auto" style="flex: 1; padding: 15px; border-radius: 10px; border: none; background: #f0f2f6; color: #333; font-weight: bold;">🤖 オートモード</button>
        </div>

        <div id="card" style="background-color: #f0f2f6; padding: 40px 20px; border-radius: 15px; border-left: 10px solid #005088; text-align: center; min-height: 150px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <div id="eng" style="font-size: 28px; font-weight: bold; margin-bottom: 20px;">読み込み中...</div>
            <hr style="width: 80%; border: 0.5px solid #ccc; margin: 20px 0;">
            <div id="jp" style="font-size: 20px; color: #666;"></div>
        </div>

        <div id="controls" style="margin-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <button id="btn-prev" style="padding: 15px; border-radius: 10px; background: white; border: 1px solid #ccc;">⬅️ 前へ</button>
            <button id="btn-next" style="padding: 15px; border-radius: 10px; background: white; border: 1px solid #ccc;">次へ ➡️</button>
        </div>
        
        <button id="btn-reset" style="width: 100%; margin-top: 10px; padding: 10px; border-radius: 10px; background: #eee; border: none;">⏮️ 先頭に戻る</button>
        
        <div id="status" style="margin-top: 15px; text-align: center; color: #999; font-size: 14px;"></div>
    </div>

    <script>
        const data = {data_json};
        let index = 0;
        let isAuto = false;
        let synth = window.speechSynthesis; // iPad標準の音声合成を使用（確実性が高い）

        const engEl = document.getElementById('eng');
        const jpEl = document.getElementById('jp');
        const statusEl = document.getElementById('status');
        const btnAuto = document.getElementById('btn-auto');
        const btnManual = document.getElementById('btn-manual');

        function updateCard() {{
            engEl.innerText = data[index][0];
            jpEl.innerText = data[index][1];
            statusEl.innerText = (index + 1) + " / " + data.length + " 枚目";
            
            // 音声再生
            speak(data[index][0]);
        }}

        function speak(text) {{
            synth.cancel(); // 前の音声を止める
            const uttr = new SpeechSynthesisUtterance(text);
            uttr.lang = 'en-US';
            uttr.rate = 0.9;
            
            uttr.onend = function() {{
                if (isAuto) {{
                    setTimeout(() => {{
                        if (!isAuto) return;
                        index = (index + 1) % data.length;
                        updateCard();
                    }}, 2000); // 読み上げ終了から2秒後に次へ
                }}
            }};
            synth.speak(uttr);
        }}

        document.getElementById('btn-next').onclick = () => {{ isAuto = false; index = (index + 1) % data.length; updateCard(); updateUI(); }};
        document.getElementById('btn-prev').onclick = () => {{ isAuto = false; index = (index - 1 + data.length) % data.length; updateCard(); updateUI(); }};
        document.getElementById('btn-reset').onclick = () => {{ isAuto = false; index = 0; updateCard(); updateUI(); }};
        
        btnManual.onclick = () => {{ isAuto = false; updateUI(); }};
        btnAuto.onclick = () => {{ 
            isAuto = true; 
            updateUI();
            updateCard(); // オート開始
        }};

        function updateUI() {{
            btnManual.style.background = isAuto ? '#f0f2f6' : '#005088';
            btnManual.style.color = isAuto ? '#333' : 'white';
            btnAuto.style.background = isAuto ? '#005088' : '#f0f2f6';
            btnAuto.style.color = isAuto ? 'white' : '#333';
            document.getElementById('controls').style.display = isAuto ? 'none' : 'grid';
        }}

        // 初回起動
        updateCard();
    </script>
""", height=600)
