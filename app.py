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
        let bestVoice = null;
        const synth = window.speechSynthesis;

        // --- 声の選別（iPad専用・再試行ロジック付） ---
        function findBestVoice() {{
            const voices = synth.getVoices();
            if (voices.length === 0) return null;

            const enVoices = voices.filter(v => v.lang.includes('en'));
            
            // iPadの「プレミアム」「拡張」「Enhanced」「Premium」を探す
            let topTier = enVoices.find(v => 
                v.name.includes('拡張') || v.name.includes('プレミアム') || 
                v.name.includes('Enhanced') || v.name.includes('Premium') ||
                v.name.includes('Siri')
            );

            if (topTier) {{
                console.log("iPad Premium Voice Found:", topTier.name);
                return topTier;
            }}
            return enVoices.find(v => v.name.includes('Samantha')) || enVoices[0];
        }}

        // iPadのために「使う直前」に声を確定させる
        function speak(text) {{
            synth.cancel();
            if (autoTimer) clearTimeout(autoTimer);

            // ここがポイント：再生の瞬間に声を再検索する
            bestVoice = findBestVoice();

            const uttr = new SpeechSynthesisUtterance(text);
            if (bestVoice) uttr.voice = bestVoice;
            
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

        // iPad用：起動時とクリック時に声をロードする
        window.onload = () => {{ synth.getVoices(); }};
        if (speechSynthesis.onvoiceschanged !== undefined) {{
            speechSynthesis.onvoiceschanged = () => {{ bestVoice = findBestVoice(); }};
        }}

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
