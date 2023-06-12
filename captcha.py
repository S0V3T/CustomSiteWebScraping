import requests
from PIL import Image
import pytesseract


# Download the captcha image
captcha_url = "https://www.mynags.com.au/Account/Captcha?0.9553505060394103"
response = requests.get(captcha_url, stream=True)
response.raise_for_status()


# Save the image locally
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

# Clean up the extracted text (if necessary)
# You may need to remove unwanted characters or apply specific text processing steps depending on the captcha format.

# Print the extracted captcha text
print("Captcha Text:", captcha_text)
