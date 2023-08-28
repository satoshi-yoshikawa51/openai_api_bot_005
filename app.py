import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import openai

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
# openai.api_key = st.secrets.OpenAIAPI.openai_api_key  # Uncomment this line if you're using OpenAI API

# サイトマップを取得する関数
def fetch_sitemap(url, is_wordpress):
    if is_wordpress:
        sitemap_url = f"{url}/wp-json/wp/v2/posts"
        response = requests.get(sitemap_url)
        if response.status_code == 200:
            posts = response.json()
            sitemap = []
            for post in posts:
                post_url = post.get("link", "")
                og_image = post.get("_embedded", {}).get("wp:featuredmedia", [{}])[0].get("source_url", "")
                sitemap.append({"URL": post_url, "og:image": og_image})
            return sitemap
    else:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            sitemap = []
            for a_tag in soup.find_all('a', href=True):
                link = a_tag['href']
                sitemap.append({"URL": link, "og:image": ""})
            return sitemap
    return None

# ユーザーがURLを入力
user_input_url = st.text_input("URLを入力してください:")
is_wordpress = st.checkbox("WordPressサイトですか？")

# URLが入力されたらサイトマップを取得
if user_input_url:
    sitemap_data = fetch_sitemap(user_input_url, is_wordpress)
    if sitemap_data:
        # Pandas DataFrameに変換
        df = pd.DataFrame(sitemap_data)
        
        # DataFrameをExcelに出力
        excel_file = df.to_excel(index=False)
        
        # Excelファイルをダウンロードリンクとして表示
        st.download_button("Excelファイルをダウンロード", excel_file, "sitemap.xlsx")
        
        # DataFrameをStreamlitアプリに表示
        st.write(df)
    else:
        st.write("サイトマップを取得できませんでした。")

# 以下は元のコード（質問応答部分）です。
# （この部分は変更していません。）
# ...



# （新しい機能のコード）
# ...

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": system_prompt}
        ]

# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]

    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)

    st.session_state["user_input"] = ""  # 入力欄を消去

# ユーザーインターフェイスの構築
# ...

user_input = st.text_input("", key="user_input", on_change=communicate)

if st.session_state["messages"]:
    messages = st.session_state["messages"]

    for message in reversed(messages[1:]):  # 直近のメッセージを上に
        speaker = "🙂"
        if message["role"]=="assistant":
            speaker="🤖"

        st.write(speaker + ": " + message["content"])

