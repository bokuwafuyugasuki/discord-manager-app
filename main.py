import discord
import os
import csv # 追加：CSVファイルを扱う
from datetime import datetime # 追加：時間を扱う
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

ai_client = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# --- ここから追加関数 ---
def save_to_csv(author, content, channel):
    """メッセージをCSVファイルに保存する関数"""
    filename = 'chat_log.csv'
    
    # ファイルがない場合はヘッダー（見出し）を作る
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Time', 'Channel', 'User', 'Content']) # 見出し
        
        # 時間を取得
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 書き込み
        writer.writerow([now, channel, author, content])
# --- ここまで追加関数 ---

@client.event
async def on_ready():
    print(f'{client.user} がログ収集を開始しました！')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # ★ここでメッセージを記録する！ 
    save_to_csv(message.author.name, message.content, message.channel.name)

    # メンションされた時のAI返信機能（さっきのまま）
    if client.user in message.mentions:
        input_text = message.content.replace(f'<@{client.user.id}>', '').strip()
        if not input_text:
            return
        
        async with message.channel.typing():
            try:
                response = ai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "あなたは優秀なDiscordコミュニティのマネージャーです。"},
                        {"role": "user", "content": input_text}
                    ]
                )
                ai_reply = response.choices[0].message.content
                await message.channel.send(ai_reply)
            except Exception as e:
                print(f"Error: {e}")

client.run(DISCORD_TOKEN)