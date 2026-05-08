import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="CROWN音読ツール", layout="centered")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv")
        return df.values.tolist()
    except:
        return [["Error", "data.csvが見つかりません"]]

data_list = load_data()
data_json = json.dumps(data_list)

st.title("🔊 CROWN音読ツール")

st.components.v1.html(f"""
    <div id="study-app" style="font-family: -apple-system, sans-serif; color: #333;">
        <div style="display: flex; gap: 10px; margin-bottom: 20px;">
            <button id="btn-manual" style="flex: 1; padding: 15px; border-radius: 12px; border: none; background: #005088; color: white; font-weight: bold;">👆 手動</button>
            <button id="btn-auto" style="flex: 1; padding: 15px; border-radius: 12px; border: none; background: #f0f2f6; color: #333; font-weight: bold;">🤖 オート</button>
        </div>

        <div id="card" style="background-color: #f0f2f6; padding: 40px 20px; border-radius: 20px; border-left: 10px solid #005088; text-align: center; min-height: 160px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
            <div id="eng" style="font-size: 28px; font-weight: bold; margin-bottom: 15px; line-height: 1.3;">画面をタップして開始</div>
            <hr style="width: 50%; border: 0.5px solid #ccc; margin: 15px auto;">
            <div id="jp" style="font-size: 18px; color: #666;"></div>
        </div>

        <div id="nav-controls" style="margin-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <button id="btn-prev" style="padding: 20px; border-radius: 12px; background: white; border: 1px solid #ddd; font-size: 20px;">⬅️ 前へ</button>
            <button id="btn-next" style="padding: 20px; border-radius: 12px; background: white; border: 1px solid #ddd; font-size: 20px;">次へ ➡️</button>
        </div>

        <div id="auto-extra" style="display: none; margin-top: 15px;">
            <button id="btn-stop" style="width: 100%; padding: 15px; border-radius: 12px; background: #ff4b4b; color: white; border: none; font-weight: bold;">⏹️ オートを止める</button>
        </div>

        <div style="margin-top: 20px; text-align: center;">
            <div id="status" style="font-size: 14px; color: #888; font-weight: bold; margin-bottom:10px;"></div>
            <button id="btn-reset" style="padding: 8px 15px; border-radius: 8px; background: #eee; border: none; font-size: 13px;">⏮️ 最初から</button>
        </div>
    </div>

    <script>
        const data = {data_json};
        let index = 0;
        let isAuto = false;
        let autoTimer = null;
        const synth = window.speechSynthesis;

        // 【ここを強化】iPadの拡張音声（Premium/Enhanced）を優先的に探す
        function getBestVoice() {{
            const voices = synth.getVoices();
            
            // 1. 「Enhanced(拡張)」や「Premium(高品質)」というキーワードが含まれる英語を探す
            let premium = voices.find(v => (v.name.includes('Enhanced') || v.name.includes('Premium') || v.name.includes('Siri')) && v.lang.includes('en'));
            if (premium) return premium;

            // 2. なければ通常のSiriやSamanthaを探す
            let siri = voices.find(v => (v.name.includes('Siri') || v.name.includes('Samantha')) && v.lang.includes('en'));
            if (siri) return siri;

            // 3. それもなければ適当な英語
            return voices.find(v => v.lang.startsWith('en'));
        }}

        function speak(text) {{
            synth.cancel();
            if (autoTimer) clearTimeout(autoTimer);

            const uttr = new SpeechSynthesisUtterance(text);
            const voice = getBestVoice();
            if (voice) uttr.voice = voice;
            
            uttr.lang = 'en-US';
            uttr.rate = 0.9;

            uttr.onend = function() {{
                if (isAuto) {{
                    autoTimer = setTimeout(() => {{
                        if (!isAuto) return;
                        index = (index + 1) % data.length;
                        updateCard();
                    }}, 2500);
                }}
            }};
            synth.speak(uttr);
        }}

        function updateCard() {{
            document.getElementById('eng').innerText = data[index][0];
            document.getElementById('jp').innerText = data[index][1];
            document.getElementById('status').innerText = (index + 1) + " / " + data.length;
            speak(data[index][0]);
        }}

        // iPadでの音声リスト更新を検知
        synth.onvoiceschanged = () => {{
            console.log("Voices updated:", synth.getVoices().length);
        }};

        document.getElementById('btn-next').onclick = () => {{
            index = (index + 1) % data.length;
            updateCard();
        }};
        document.getElementById('btn-prev').onclick = () => {{
            index = (index - 1 + data.length) % data.length;
            updateCard();
        }};
        document.getElementById('btn-stop').onclick = () => {{
            isAuto = false;
            synth.cancel();
            if (autoTimer) clearTimeout(autoTimer);
            updateUI();
        }};
        document.getElementById('btn-auto').onclick = () => {{
            isAuto = true;
            updateUI();
            updateCard();
        }};
        document.getElementById('btn-manual').onclick = () => {{
            isAuto = false;
            if (autoTimer) clearTimeout(autoTimer);
            updateUI();
        }};
        document.getElementById('btn-reset').onclick = () => {{ index = 0; updateCard(); }};

        function updateUI() {{
            document.getElementById('btn-manual').style.background = isAuto ? '#f0f2f6' : '#005088';
            document.getElementById('btn-manual').style.color = isAuto ? '#333' : 'white';
            document.getElementById('btn-auto').style.background = isAuto ? '#005088' : '#f0f2f6';
            document.getElementById('btn-auto').style.color = isAuto ? 'white' : '#333';
            document.getElementById('auto-extra').style.display = isAuto ? 'block' : 'none';
        }}
    </script>
""", height=600)
