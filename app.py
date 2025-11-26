import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI

# .envファイルからAPIキーを読み込む
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# AIの準備
ai_client = OpenAI(api_key=OPENAI_API_KEY)

# ページの基本設定
st.set_page_config(page_title="Discord管理ダッシュボード", layout="wide")
st.title("🤖 Discord コミュニティ管理画面")

# --- 関数エリア ---

def load_data():
    """CSVを読み込む関数"""
    try:
        # 毎回最新のCSVを読みに行く
        df = pd.read_csv('chat_log.csv')
        return df
    except FileNotFoundError:
        return None

def generate_summary(df):
    """チャット履歴をAIに要約させる関数"""
    # 最新の30件だけをテキストにする（全部送ると高いし重いから）
    recent_logs = df.tail(30)
    text_data = ""
    for index, row in recent_logs.iterrows():
        text_data += f"{row['User']}: {row['Content']}\n"

    # AIへの命令文
    prompt = f"""
    以下のチャットログはDiscordコミュニティの会話です。
    管理者のために、この会話の内容を「箇条書きで3点」に要約してください。
    また、不適切な発言やトラブルの予兆があれば警告してください。
    
    【チャットログ】
    {text_data}
    """

    try:
        response = ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"エラー: {e}"

# --- メイン処理エリア ---

# 1. データを読み込む
df = load_data()

# 2. 上部に「更新ボタン」を設置
if st.button('🔄 データを最新に更新'):
    st.rerun() # これで強制的に再読み込みさせる

if df is None:
    st.warning("まだログデータがありません。Discordで会話してください！")
else:
    # --- レイアウト ---
    # KPI表示
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("総メッセージ数", len(df))
    with col2:
        st.metric("参加ユーザー数", df['User'].nunique())
    with col3:
        st.metric("最終更新", df['Time'].iloc[-1])

    st.divider() # 区切り線

    # 左：AI要約エリア
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("🧠 AI コミュニティ日報")
        st.info("ボタンを押すと、直近30件の会話をAIが分析します。")
        
        if st.button('日報を作成する'):
            with st.spinner('AIが分析中...（数秒かかります）'):
                summary_text = generate_summary(df)
                st.success("分析完了！")
                st.markdown(summary_text)

    # 右：ログ一覧
    with col_right:
        st.subheader("📜 直近の会話ログ")
        st.dataframe(df.tail(10)) # 最新10件を表示
        
        st.caption("ユーザー別の発言数ランキング")
        st.dataframe(df['User'].value_counts())

        # --- ここから追加 ---
st.sidebar.markdown("---") # サイドバーに区切り線
auto_refresh = st.sidebar.checkbox("⚡ リアルタイム更新モード")

if auto_refresh:
    time.sleep(2) # 2秒待つ
    st.rerun()    # 画面を再読み込みする