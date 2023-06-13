
#Library to securely store and use sensitive information data
from dotenv import load_dotenv

#Libraries that I use to recognize text on the image
from super_image import ImageLoader, EdsrModel
from PIL import Image
import cv2
from scipy.ndimage import gaussian_filter
import pytesseract
import numpy


#Library used to store the session data to reuse it later
import pickle

#Time libraries for time operations
import time
from datetime import datetime

#Library for coding/decoding web stuff
import urllib

#Most basic libraries for operations
import random
import os
import logging

#Libraries used to set an internet connection and parse the content
import requests
from bs4 import BeautifulSoup
import json

#Ignore warnings (not important)
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


#Defining the name of file where we store our session information
pickle_file = 'session.pickle'
#Creating a captcha dir if it doesn't exist
captcha_dir = "captcha"
os.makedirs(captcha_dir, exist_ok=True)
# Configure the logger
logging.basicConfig(filename='app_login.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
#Setting a default session, which can be later swapped with a saved one
session = requests.Session()

#Loading the .env storage
load_dotenv()

#Defining default headers, which we'll use all the time
existing_headers = {
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

#Function to generate random nymber for captcha request
def random_num():
    # The smallest 14-digit number is 10**13 and the largest is 10**14 - 1.
    min_value = 10 ** 13
    max_value = 10 ** 14 - 1

    random_number = random.randint(min_value, max_value)
    return random_number



#Log in function, which will set a authentication cookie to our session
def login(req_ver):
    #Info about the process
    print("Starting login process")
    logging.debug("Starting login process")
    #Creating a success variable, so we only proceed if we authenticate
    success = False
    #Creating a num variable which will indicate a max amount of tries to log in
    num_tries = 7
    #Grabbing all the sensitive information from safe storage
    url = os.getenv("base_url")
    cust_id = os.getenv("cust_id")
    usrnm = os.getenv("usrnm")
    passwrd = os.getenv("secret")
    #Loop which won't stop until we log in, or limit of tries exceeds 
    while success == False and num_tries > 0:
        print("LOOPING")
        code = request_captcha()
        #Creating a content which we will POST to our website to log in
        content = {
            "CustomerID": cust_id,
            "UserName": usrnm,
            "Password": passwrd,
            "VerifyCode": code,
            "__RequestVerificationToken": req_ver
        }
        #Encoding the content to calculate the content-length
        url_encoded_content = urllib.parse.urlencode(content)
        #Updating the headers, so they are suitable for a POST Login request
        session.headers.update({'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': f"{len(url_encoded_content)}", 'Host': 'www.mynags.com.au', 'Sec-Fetch-Site': 'same-origin', 'Referer': f'{url}'})
        #Making a post request and if we get AspNetCore.Cookies in cookies then we are logged in and can proceed
        response = session.post(url, data=content, timeout=10)
        success = "AspNetCore.Cookies" in str(session.cookies)
        #After our manipulations we remove the POST headers, so they don't conflict with our future GET requests
        headers_to_delete = ['Content-Type', 'Content-Length']
        for header in headers_to_delete:
            del session.headers[header]
        #Decreasing the number of tries after the trie
        num_tries -= 1
        #Waiting for 5 seconds, maybe the issue will go away
        time.sleep(5)
    if success:
        #Info about the process success
        print(f"Successfully logged in")
        logging.debug(f"Successfully logged in")
        return response.status_code
    #Info about the process failed
    print(f"Failed to log in after 8 tries")
    logging.debug(f"Failed to log in after 8 tries")
    return False

#The hardest part, the part of solving the captcha
def request_captcha():
    #Getting the timestamp of current time
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    #Getting the link which will get us a captcha
    #We need to remember, that we need to have our Basic Cookies, which should have been requested before in order to successfully solve the captcha and log in
    captcha_url = os.getenv("captcha_url")
    #Creating a unique captcha URL
    captcha_url = f"{captcha_url}?0.{random_num()}"
    #Getting the image and saving it as captcha_image.png
    response = session.get(captcha_url, stream=True, timeout=10)
    image_path = os.path.join(captcha_dir, f"original_{timestamp}.png")
    if os.path.exists(image_path):
        os.remove(image_path)
    with open(image_path, "wb") as image_file:
        image_file.write(response.content)

    #Proccessing the image, so it is clearly seen what characters and numbers are displayed
    th1 = 140
    sig = 1.3  # the blurring sigma
    image = Image.open(image_path)
    black_and_white = image.convert("L")  # converting to black and white
    bw_path = os.path.join(captcha_dir, f"black_white_{timestamp}.png")
    black_and_white.save(bw_path)
    first_threshold = black_and_white.point(lambda p: p > th1 and 255)
    ft_path = os.path.join(captcha_dir, f"first_threshold_{timestamp}.png")
    first_threshold.save(ft_path)
    blur = numpy.array(first_threshold)  # create an image array
    blurred = gaussian_filter(blur, sigma=sig)
    blurred = Image.fromarray(blurred)
    blur_path = os.path.join(captcha_dir, f"blurred_{timestamp}.png")
    blurred.save(blur_path)
    model = EdsrModel.from_pretrained('eugenesiow/edsr-base', scale=4)
    inputs = ImageLoader.load_image(Image.open(blur_path))
    preds = model(inputs)
    scaled_path = os.path.join(captcha_dir, f"scaled_4x_{timestamp}.png")
    ImageLoader.save_image(preds, scaled_path)
    sharpen_filter=numpy.array([[-1,-1,-1],
                 [-1,9,-1],
                [-1,-1,-1]])
    # applying kernels to the input image to get the sharpened image
    original_image=cv2.imread(scaled_path)
    sharp_image=cv2.filter2D(original_image,-1,sharpen_filter)
    #Identifying characters
    captcha_text = pytesseract.image_to_string(sharp_image, lang='eng',
                                         config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789QWERTYUIOPASDFGHJKLZXCVBNM').strip()
    #Info about the process
    print(f"Got the captcha: {captcha_text}")
    logging.debug(f"Got the captcha: {captcha_text}")
    return captcha_text
    
#Function to get basic cookies for the start
def get_basic_cookies():
    #Gettin the cookie url from our vault
    url = os.getenv("base_url")
    #Setting the headers to default
    headers = existing_headers
    #Updating default session with default headers
    session.headers.update(headers)
    #Getting the response
    response = session.get(url)
    #If success - proceed
    if response.status_code == 200:
        #Getting the secret __RequestVerificationToken which is used to log in
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        # Locate the verification token input field
        verification_token_input = soup.find("input", attrs={"name": "__RequestVerificationToken"})
        if verification_token_input:
            token_value = verification_token_input["value"]
            return token_value
        else:
            return False
    else:
        return False, False

#Accepting terms and conditions
def accept_dis():
    #Accepting the terms and conditions, so we can proceed to the inner body of the website
    url = 'https://www.mynags.com.au/Account/AcceptDisclaimer'
    session.headers.update({'Referer': 'https://www.mynags.com.au/Account/Disclaimer'})
    response = session.get(url, timeout=10)
    return response.status_code

#Function used to get log in session and reuse one if already exists
def get_login_session():
    global session
    if os.path.exists(pickle_file):
        # Load session from file
        with open(pickle_file, 'rb') as f:
            session = pickle.load(f)
        #Info about the process
        print(f"Reusing the session")
        logging.debug("Reusing the session")
    else:
        # Create a new session, do some work
        req_ver = get_basic_cookies()
        if req_ver:
            code = login(req_ver)
            if code == 200:
                code_dis = accept_dis()
                if code_dis == 200:
                    with open(pickle_file, 'wb') as f:
                        pickle.dump(session, f)
                    return True
        get_login_session()



if __name__ == '__main__':
    get_login_session()
    try:
        response = session.get('https://www.mynags.com.au/Catalogue', timeout=10)
        #Info about the process
        print("Gained access to the main source")
        logging.debug("Gained access to the main source")
    except:
        #Info about the process
        print("Failed to reuse the session")
        logging.debug("Failed to reuse the session")
        if os.path.exists(pickle_file):
            os.remove(pickle_file)
        get_login_session()
    #Info about the process
    print("Ended the work of script")
    logging.debug("Ended the work of script")