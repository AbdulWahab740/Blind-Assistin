from PIL import Image
try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
except:
    from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image, UnidentifiedImageError
import requests
import torch
# Load the processor and model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'tesseract.exe'  # Assuming Tesseract is in the PATH
import cv2
from ai71 import AI71 

import gtts
import playsound 





image_path="E:/Python/Django/blind-assist/blindAssist/photo1.jpg"
def play(text):
    sound=gtts.gTTS(text,lang="en")
    try:
        sound.save("voice.mp3")        
    except PermissionError as e:
        print(e)
        
    playsound.playsound("voice.mp3")

def generateText(text):
    #I extracted this informtaion from image, in reply don't say image, say inside in the enviroment, please orgnize what is inside in the enviroment: "+text
    AI71_API_KEY = "ai71-api-ddbfacf9-004f-415d-8f22-edba215b5af2"
    text_content=" "
    for chunk in AI71(AI71_API_KEY).chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant like google and siri."},
            {"role": "user", "content": " I am visually impaired and have taken a picture of the environment. After extracting the information from the image, I would like to know what is described in the text. Please provide your prediction using the given text and refer to the content as being from the environment rather than mentioning the image "+text},
        ],
        stream=True,
    ):
        
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, sep="", end="", flush=True)
            text_content += chunk.choices[0].delta.content
    print(text_content)
    play(text_content)

# Save the image locally
#image_path = save_image(photo)
#image_path="files/photo1.jpg"   
text=""     
try:
    image = Image.open(image_path)
    print(image)
except:
    #print(f"Error: {e}")
    print(" OCR")
    exit()


# Process the image and generate a caption
inputs = processor(images=image, return_tensors="pt",padding=True)
out = model.generate(**inputs,
                    max_new_tokens=50)
caption=" objects in image: "
caption += processor.decode(out[0], skip_special_tokens=True)
text +=caption
print("Generated Caption:", caption)

    # Read the image using OpenCV
img = cv2.imread(image_path)
print("done 1")
# Convert to grayscale
gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply binary thresholding
_, binary_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)

# Noise removal
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
no_noise_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

# Find contours
contours, _ = cv2.findContours(no_noise_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Check if contours were found
if contours:
    # Sort contours and get the largest one
    cnt_sorted = sorted(contours, key=lambda x: cv2.contourArea(x))
    cnt = cnt_sorted[-1]
    
    # Get bounding box for the largest contour
    x, y, w, h = cv2.boundingRect(cnt)
    cropped_image = no_noise_image[y:y+h, x:x+w]
    
    # Convert the image to a PIL Image object for OCR
    pil_image = Image.fromarray(cropped_image)
    
    # Perform OCR
    try:
        ocr_result=", text inside in image: "
        ocr_result += pytesseract.image_to_string(pil_image)
        text +=ocr_result
        # Check if OCR result is empty
        if ocr_result.strip():
            print("Detected Text:")
            print(ocr_result)

        else:
            print(" ")
    except:
        print(" Error in OCR")
else:
    print("No contours found in the image.")
    text+=". there is no text inside in the image"
print(" complete text ",text)
generateText(text)

