import streamlit as st
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from fpdf import FPDF
import urllib.parse
import warnings

warnings.filterwarnings('ignore')

# --- 설정값 (A5 사이즈) ---
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
    pdf = FPDF('P', 'mm', 'A5')
    pdf.add_page()
    
    img = Image.open(BytesIO(img_bytes))
    img_path = "temp_cover.png"
    img.save(img_path)
    
    margin = 10
    draw_width = A5_WIDTH_MM - (margin * 2)
    img_ratio = img.height / img.width
    draw_height = draw_width * img_ratio
    
    if draw_height > (A5_HEIGHT_MM - margin * 2):
        draw_height = A5_HEIGHT_MM - margin * 2
        draw_width = draw_height / img_ratio

    pdf.image(img_path, x=margin, y=margin, w=draw_width)
    
    # .encode('latin-1')를 삭제하여 오류를 해결했습니다.
    return pdf.output()

# --- UI ---
st.set_page_config(page_title="알라딘 A5 표지 추출기", page_icon="📖")
st.title("📖 표지 추출기 (A4 절반 사이즈)")
st.write("A4 용지의 절반인 **A5 크기**로 인쇄 가능한 PDF를 만듭니다.")

title_input = st.text_input("책 제목을 정확히 입력하세요:", "")

if st.button("표지 생성 및 PDF 만들기"):
    if title_input:
        with st.spinner('표지를 찾아서 PDF로 변환 중...'):
            img_url = get_high_res_cover(title_input)
            if img_url:
                resp = requests.get(img_url)
                st.image(resp.content, caption="찾은 이미지 (미리보기)", width=300)
                
                try:
                    pdf_data = create_pdf(resp.content, title_input)
                    st.download_button(
                        label="🖨️ A5 사이즈 PDF 다운로드",
                        data=bytes(pdf_data), # bytes 타입으로 명시적 변환
                        file_name=f"{title_input}_A5.pdf",
                        mime="application/pdf"
                    )
                    st.success("PDF 생성이 완료되었습니다!")
                except Exception as e:
                    st.error(f"PDF 생성 중 오류가 발생했습니다: {str(e)}")
            else:
                st.error("책을 찾을 수 없습니다. 제목을 확인해 주세요.")
    else:
        st.warning("책 제목을 입력해 주세요.")
