import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="CROWN音読ツール", layout="centered")

# --- データの読み込み ---
@st.cache_data
def load_data():
    try:
        # A2, B2から読み込み
        df = pd.read_csv("data.csv")
        return df.values.tolist()
    except:
        return [["Error", "data.csvが見つかりません"]]

data_list = load_data()
data_json = json.dumps(data_list)

st.title("🔊 CROWN音読ツール")
st.caption("iPad最適化・高音質モード")

# --- メインロジック（JavaScript） ---
st.components.v1.html(f"""
    <div id="study-app" style="font-family: 'Helvetica Neue', Arial, sans-serif; color: #333;">
        <div id="mode-selector" style="display: flex; gap: 10px; margin-bottom: 20px;">
            <button id="btn-manual" style="flex: 1; padding: 15px; border-radius: 12px; border: none; background: #005088; color: white; font-weight: bold; font-size: 16px;">👆 手動</button>
            <button id="btn-auto" style="flex: 1; padding: 15px; border-radius: 12px; border: none; background: #f0f2f6; color: #333; font-weight: bold; font-size: 16px;">🤖 オート</button>
        </div>

        <div id="card" style="background-color: #f0f2f6; padding: 40px 20px; border-radius: 20px; border-left: 10px solid #005088; text-align: center; min-height: 180px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <div id="eng" style="font-size: 30px; font-weight: bold; margin-bottom: 15px; line-height: 1.2;"></div>
            <hr style="width: 60%; border: 0.5px solid #ccc; margin: 20px auto;">
            <div id="jp" style="font-size: 20px; color: #666;"></div>
        </div>

        <div id="auto-controls" style="display: none; margin-top: 20px;">
            <button id="btn-stop" style="width: 100%; padding: 18px; border-radius: 12px; background: #ff4b4b; color: white; border: none; font-weight: bold; font-size: 18px; box-shadow: 0 4px 10px rgba(255,75,75,0.3);">⏹️ オートを停止する</button>
        </div>

        <div id="manual-controls" style="margin-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <button id="btn-prev" style="padding: 15px; border-radius: 12px; background: white; border: 1px solid #ccc; font-size: 18px;">⬅️ 前へ</button>
            <button id="btn-next" style="padding: 15px; border-radius: 12px; background: white; border: 1px solid #ccc; font-size: 18px;">次へ ➡️</button>
        </div>
        
        <div style="margin-top: 20px; display: flex; align-items: center; justify-content: space-between;">
            <button id="btn-reset" style="padding: 10px 20px; border-radius: 8px; background: #eee; border: none; font-size: 14px;">⏮️ 先頭に戻る</button>
            <div id="status" style="color: #999; font-size: 14px; font-weight: bold;"></div>
        </div>
    </div>

    <script>
        const data = {data_json};
        let index = 0;
        let isAuto = false;
        const synth = window.speechSynthesis;

        const engEl = document.getElementById('eng');
        const jpEl = document.getElementById('jp');
        const statusEl = document.getElementById('status');
        const autoControls = document.getElementById('auto-controls');
        const manualControls = document.getElementById('manual-controls');
        const btnAuto = document.getElementById('btn-auto');
        const btnManual = document.getElementById('btn-manual');

        function updateCard() {{
            engEl.innerText = data[index][0];
            jpEl.innerText = data[index][1];
            statusEl.innerText = (index + 1) + " / " + data.length;
            speak(data[index][0]);
        }}

        function speak(text) {{
            synth.cancel();
            const uttr = new SpeechSynthesisUtterance(text);
            
            // iPad/iOSで「より綺麗な英語」を探すロジック
            const voices = synth.getVoices();
            // Samantha, Siri, Karen あたりの高品質ボイスを優先
            const preferredVoice = voices.find(v => 
                (v.name.includes('Samantha') || v.name.includes('Siri') || v.name.includes('Karen')) && v.lang.includes('en')
            ) || voices.find(v => v.lang.startsWith('en'));
            
            if (preferredVoice) uttr.voice = preferredVoice;
            
            uttr.lang = 'en-US';
            uttr.rate = 0.9; // 読み上げ速度（少しゆっくり）
            uttr.pitch = 1.0;

            uttr.onend = function() {{
                if (isAuto) {{
                    setTimeout(() => {{
                        if (!isAuto) return;
                        index = (index + 1) % data.length;
                        updateCard();
                    }}, 2500); // 終わってから2.5秒待機
                }}
            }};
            synth.speak(uttr);
        }}

        // イベント設定
        document.getElementById('btn-next').onclick = () => {{ index = (index + 1) % data.length; updateCard(); }};
        document.getElementById('btn-prev').onclick = () => {{ index = (index - 1 + data.length) % data.length; updateCard(); }};
        document.getElementById('btn-reset').onclick = () => {{ index = 0; updateCard(); }};
        document.getElementById('btn-stop').onclick = () => {{ isAuto = false; updateUI(); synth.cancel(); }};
        
        btnManual.onclick = () => {{ isAuto = false; updateUI(); }};
        btnAuto.onclick = () => {{ isAuto = true; updateUI(); updateCard(); }};

        function updateUI() {{
            btnManual.style.background = isAuto ? '#f0f2f6' : '#005088';
            btnManual.style.color = isAuto ? '#333' : 'white';
            btnAuto.style.background = isAuto ? '#005088' : '#f0f2f6';
            btnAuto.style.color = isAuto ? 'white' : '#333';
            
            autoControls.style.display = isAuto ? 'block' : 'none';
            manualControls.style.display = isAuto ? 'none' : 'grid';
        }}

        // iPadで音声をロードするためのハック
        window.speechSynthesis.onvoiceschanged = () => {{ updateCard(); }};
        updateCard();
    </script>
""", height=600)
