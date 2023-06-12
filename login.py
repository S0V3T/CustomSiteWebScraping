
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import random
import os
import requests
from bs4 import BeautifulSoup

load_dotenv()

def random_num():
    # The smallest 14-digit number is 10**13 and the largest is 10**14 - 1.
    min_value = 10 ** 13
    max_value = 10 ** 14 - 1

    random_number = random.randint(min_value, max_value)
    return random_number




def login(cookie, captcha):
    pass

def get_verification_token(cookie):
    

def request_captcha(cookie):
    captcha_url = os.getenv("captcha_url")
    captcha_url = captcha_url & "?0." & random_num()
    headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', 
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': f'{cookie}',
    'Dnt': '1',
    'Host': 'www.mynags.com.au',
    'Pragma': 'no-cache',
    'Sec-Ch-Ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': "Windows",
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    response = requests.get(captcha_url, headers=headers, stream=True)
    response.raise_for_status()

    image_path = "captcha_image.png"
    if os.path.exists(image_path):
        os.remove(image_path)
    with open(image_path, "wb") as image_file:
        image_file.write(response.content)

    # Load the captcha image
    captcha_image = Image.open(image_path)

    # Preprocess the image (if necessary)
    # You can apply various preprocessing techniques such as resizing, filtering, etc., depending on the captcha image characteristics.

    # Perform OCR on the captcha image
    captcha_text = pytesseract.image_to_string(captcha_image)

    return captcha_text
    
def get_basic_cookies():
    url = os.getenv("base_url")
    headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', 
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Dnt': '1',
    'Host': 'www.mynags.com.au',
    'Pragma': 'no-cache',
    'Sec-Ch-Ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': "Windows",
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    print(response.status_code)
    if response.status_code == 200:
        cookies = response.cookies
        cookie_string = '; '.join([f'{cookie.name}={cookie.value}' for cookie in cookies])
        return cookie_string
    else:
        return False



if __name__ == '__main__':
    anti_forg = get_basic_cookies()
    print(anti_forg)