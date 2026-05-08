import streamlit as st
import pd
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

st.title("🔊 CROWN音読ツール")

# --- メインロジック（JavaScript） ---
st.components.v1.html(f"""
    <div id="study-app" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #333;">
        
        <div style="display: flex; gap: 10px; margin-bottom: 20px;">
            <button id="btn-manual" style="flex: 1; padding: 15px; border-radius: 12px; border: none; background: #005088; color: white; font-weight: bold;">👆 手動</button>
            <button id="btn-auto" style="flex: 1; padding: 15px; border-radius: 12px; border: none; background: #f0f2f6; color: #333; font-weight: bold;">🤖 オート</button>
        </div>

        <div id="card" style="background-color: #f0f2f6; padding: 40px 20px; border-radius: 20px; border-left: 10px solid #005088; text-align: center; min-height: 160px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
            <div id="eng" style="font-size: 28px; font-weight: bold; margin-bottom: 15px; line-height: 1.3;">読み込み中...</div>
            <hr style="width: 50%; border: 0.5px solid #ccc; margin: 15px auto;">
            <div id="jp" style="font-size: 18px; color: #666;"></div>
        </div>

        <div id="nav-controls" style="margin-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <button id="btn-prev" style="padding: 18px; border-radius: 12px; background: white; border: 1px solid #ddd; font-size: 18px; -webkit-appearance: none;">⬅️ 前へ</button>
            <button id="btn-next" style="padding: 18px; border-radius: 12px; background: white; border: 1px solid #ddd; font-size: 18px; -webkit-appearance: none;">次へ ➡️</button>
        </div>

        <div id="auto-extra" style="display: none; margin-top: 15px;">
            <button id="btn-stop" style="width: 100%; padding: 15px; border-radius: 12px; background: #ff4b4b; color: white; border: none; font-weight: bold;">⏹️ オートを止める</button>
        </div>

        <div style="margin-top: 20px; display: flex; justify-content: space-between; align-items: center; padding: 0 5px;">
            <button id="btn-reset" style="padding: 8px 15px; border-radius: 8px; background: #eee; border: none; font-size: 13px;">⏮️ 最初から</button>
            <div id="status" style="font-size: 14px; color: #888; font-weight: bold;"></div>
        </div>
    </div>

    <script>
        const data = {data_json};
        let index = 0;
        let isAuto = false;
        let timer = null;
        const synth = window.speechSynthesis;

        // 音声設定（iPadで最も綺麗な声を選ぶ）
        let selectedVoice = null;
        function loadVoices() {{
            const voices = synth.getVoices();
            // iPadの高品質ボイス（Siri, Samantha, Karen, Daniel）を優先
            selectedVoice = voices.find(v => v.name.includes('Siri') && v.lang.includes('en')) ||
                            voices.find(v => v.name.includes('Samantha') && v.lang.includes('en')) ||
                            voices.find(v => v.name.includes('Karen') && v.lang.includes('en')) ||
                            voices.find(v => v.lang.startsWith('en-US')) ||
                            voices[0];
        }}
        synth.onvoiceschanged = loadVoices;
        loadVoices();

        function updateCard(play = true) {{
            if (timer) clearTimeout(timer);
            
            document.getElementById('eng').innerText = data[index][0];
            document.getElementById('jp').innerText = data[index][1];
            document.getElementById('status').innerText = (index + 1) + " / " + data.length;
            
            if (play) speak(data[index][0]);
        }}

        function speak(text) {{
            synth.cancel();
            const uttr = new SpeechSynthesisUtterance(text);
            if (selectedVoice) uttr.voice = selectedVoice;
            uttr.lang = 'en-US';
            uttr.rate = 0.9;
            uttr.pitch = 1.0;

            uttr.onend = function() {{
                if (isAuto) {{
                    // 次のカードへ進む予約
                    timer = setTimeout(() => {{
                        if (!isAuto) return;
                        index = (index + 1) % data.length;
                        updateCard();
                    }}, 2500);
                }}
            }};
            synth.speak(uttr);
        }}

        // ボタンイベント
        document.getElementById('btn-next').onclick = () => {{
            index = (index + 1) % data.length;
            updateCard();
        }};
        document.getElementById('btn-prev').onclick = () => {{
            index = (index - 1 + data.length) % data.length;
            updateCard();
        }};
        document.getElementById('btn-reset').onclick = () => {{
            index = 0;
            updateCard();
        }};
        document.getElementById('btn-stop').onclick = () => {{
            isAuto = false;
            if (timer) clearTimeout(timer);
            synth.cancel();
            updateUI();
        }};
        
        document.getElementById('btn-manual').onclick = () => {{ isAuto = false; updateUI(); }};
        document.getElementById('btn-auto').onclick = () => {{ 
            isAuto = true; 
            updateUI(); 
            updateCard(); 
        }};

        function updateUI() {{
            const btnManual = document.getElementById('btn-manual');
            const btnAuto = document.getElementById('btn-auto');
            btnManual.style.background = isAuto ? '#f0f2f6' : '#005088';
            btnManual.style.color = isAuto ? '#333' : 'white';
            btnAuto.style.background = isAuto ? '#005088' : '#f0f2f6';
            btnAuto.style.color = isAuto ? 'white' : '#333';
            document.getElementById('auto-extra').style.display = isAuto ? 'block' : 'none';
        }}

        // 起動
        setTimeout(updateCard, 500); 
    </script>
""", height=600)
