import streamlit as st
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from fpdf import FPDF
import urllib.parse
import warnings

warnings.filterwarnings('ignore')

# --- 설정값 (A5 사이즈: A4의 절반) ---
A5_WIDTH_MM = 148
A5_HEIGHT_MM = 210

def get_high_res_cover(book_title):
    try:
        encoded_title = urllib.parse.quote(book_title)
        url = f"https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=All&SearchWord={encoded_title}"
        headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.aladin.co.kr/"}
        res = requests.get(url, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        img_tag = soup.select_one("div.ss_book_box img.front_cover")
        if img_tag and 'src' in img_tag.attrs:
            img_src = img_tag['src']
            return img_src.replace("/cover/", "/cover500/").replace("/coversum/", "/cover500/")
        return None
    except:
        return None

def create_pdf(img_bytes, title):
    # A5 사이즈 PDF 생성
    pdf = FPDF('P', 'mm', 'A5')
    pdf.add_page()
    
    # 이미지 임시 저장
    img = Image.open(BytesIO(img_bytes))
    img_path = "temp_cover.png"
    img.save(img_path)
    
    # 이미지를 A5 꽉 차게 배치 (여백 10mm 제외)
    margin = 10
    draw_width = A5_WIDTH_MM - (margin * 2)
    # 이미지 비율 유지하며 높이 계산
    img_ratio = img.height / img.width
    draw_height = draw_width * img_ratio
    
    # 만약 높이가 A5를 넘어가면 높이 기준으로 재계산
    if draw_height > (A5_HEIGHT_MM - margin * 2):
        draw_height = A5_HEIGHT_MM - margin * 2
        draw_width = draw_height / img_ratio

    pdf.image(img_path, x=margin, y=margin, w=draw_width
