import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import urllib.parse
import warnings

warnings.filterwarnings('ignore')

# --- 핵심 기능 ---
def get_high_res_cover(book_title):
    try:
        encoded_title = urllib.parse.quote(book_title)
        url = f"https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=All&SearchWord={encoded_title}"
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.aladin.co.kr/"
        }
        
        res = requests.get(url, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 첫 번째 검색 결과의 이미지 찾기
        img_tag = soup.select_one("div.ss_book_box img.front_cover")
        if img_tag and 'src' in img_tag.attrs:
            img_src = img_tag['src']
            # 고화질 변환
            high_res_url = img_src.replace("/cover/", "/cover500/").replace("/coversum/", "/cover500/")
            return high_res_url
        return None
    except Exception as e:
        return None

# --- 스트림릿 UI ---
st.set_page_config(page_title="알라딘 표지 추출기", page_icon="📚")
st.title("📚 알라딘 책 표지 추출기")
st.info("알라딘에서 검색된 첫 번째 책의 고화질 표지를 가져옵니다.")

title_input = st.text_input("책 제목을 입력하세요:", "")

if st.button("표지 찾기"):
    if title_input:
        with st.spinner('이미지를 검색 중입니다...'):
            img_url = get_high_res_cover(title_input)
            
            if img_url:
                st.success(f"'{title_input}' 표지를 찾았습니다!")
                response = requests.get(img_url)
                img = Image.open(BytesIO(response.content))
                st.image(img, caption=title_input, use_container_width=True)
                
                # 다운로드 버튼
                buf = BytesIO()
                img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                st.download_button(
                    label="이미지 저장하기", 
                    data=byte_im, 
                    file_name=f"{title_input}.png", 
                    mime="image/png"
                )
            else:
                st.error("표지 이미지를 찾을 수 없습니다. 제목을 정확히 입력해 보세요.")
    else:
        st.warning("제목을 입력해 주세요.")
