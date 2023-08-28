import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO

# og:imageを取得する関数
def fetch_og_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        og_image_tag = soup.find("meta", {"property": "og:image"})
        if og_image_tag and 'content' in og_image_tag.attrs:
            return og_image_tag['content']
    return None

# サイトマップを取得する関数
def fetch_sitemap(url, is_wordpress):
    sitemap = []
    if is_wordpress:
        sitemap_url = f"{url}/wp-json/wp/v2/posts"
        response = requests.get(sitemap_url)
        if response.status_code == 200:
            posts = response.json()
            for post in posts:
                post_url = post.get("link", "")
                og_image = fetch_og_image(post_url)
                sitemap.append({"URL": post_url, "og:image": og_image})
    else:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for a_tag in soup.find_all('a', href=True):
                link = a_tag['href']
                og_image = fetch_og_image(link)
                sitemap.append({"URL": link, "og:image": og_image})
    return sitemap if sitemap else None

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
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        excel_data = output.getvalue()
        
        # Excelファイルをダウンロードリンクとして表示
        st.download_button("Excelファイルをダウンロード", excel_data, "sitemap.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        # DataFrameをStreamlitアプリに表示
        st.write(df)
    else:
        st.write("サイトマップを取得できませんでした。")

