from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import base64
import io
import json

import os

from PIL import Image, UnidentifiedImageError
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
import pyttsx3

import gtts
import playsound 

def mainCode(image_path):
    print("ftn call")
    #image_path="E:/Python/Django/blind-assist/blindAssist/uploaded_image.jpg"
    def play(text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
            
        # playsound.playsound("voice.mp3")

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

def home(request):
    # engine = pyttsx3.init()
    # engine.say("Hello How are you? This app is specially build for blind people. You may capture the image by clicking anywhere or by voice")
    # engine.runAndWait()
    return render(request, 'index.html')

@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        try:
            print("hello")
            # Decode the request body
            data = json.loads(request.body.decode('utf-8'))
            if 'image' not in data:
                print("Image data missing")
                return JsonResponse({"status": "error", "message": "Image data missing"}, status=400)
            
            image_data = data['image']
            
            # Check if image_data is not None and not empty
            if not image_data:
                print("Empty image data")
                return JsonResponse({"status": "error", "message": "Empty image data"}, status=400)

            # Split the data URL to get base64 encoded data
            format, imgstr = image_data.split(';base64,')
            
            # Decode the base64 string to binary data
            image_data = base64.b64decode(imgstr)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert RGBA to RGB
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            image.save('uploaded_image.jpg')
            mainCode('uploaded_image.jpg') 
            return JsonResponse({"status": "success", "message": ""})
        except json.JSONDecodeError:
            print("Invalid JSON format")
            return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)
        except ValueError as e:
            print(f"Error processing image data: {str(e)}")
            return JsonResponse({"status": "error", "message": f"Error processing image data: {str(e)}"}, status=400)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)
