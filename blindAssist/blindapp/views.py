from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import base64
import io
import json
import os
from PIL import Image, UnidentifiedImageError
from transformers import BlipProcessor, BlipForConditionalGeneration
import pytesseract
import cv2
import numpy as np
from ai71 import AI71 
import pyttsx3

# Load the processor and model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
pytesseract.pytesseract.tesseract_cmd = r'tesseract.exe'  # Update this path if needed

def play(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def generateText(text):
    AI71_API_KEY = "ai71-api-ddbfacf9-004f-415d-8f22-edba215b5af2"
    text_content = " "
    for chunk in AI71(AI71_API_KEY).chat.completions.create(
        model="tiiuae/falcon-180b-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant like google and siri."},
            {"role": "user", "content": f"I am visually impaired and have taken a picture of the environment. After extracting the information from the image, I would like to know what is described in the text. Please provide your prediction using the given text and refer to the content as being from the environment rather than mentioning the image: {text}"},
        ],
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, sep="", end="", flush=True)
            text_content += chunk.choices[0].delta.content
    print(text_content)
    play(text_content)

def mainCode(image):
    text = ""

    try:
        print(image)
    except UnidentifiedImageError as e:
        print(f"Error: {e}")
        return "Error: Unable to identify image."

    # Process the image and generate a caption
    inputs = processor(images=image, return_tensors="pt", padding=True)
    out = model.generate(**inputs, max_new_tokens=50)
    caption = "objects in image: " + processor.decode(out[0], skip_special_tokens=True)
    text += caption
    print("Generated Caption:", caption)

    # Read the image using OpenCV
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    no_noise_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(no_noise_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        cnt_sorted = sorted(contours, key=lambda x: cv2.contourArea(x))
        cnt = cnt_sorted[-1]
        x, y, w, h = cv2.boundingRect(cnt)
        cropped_image = no_noise_image[y:y+h, x:x+w]
        pil_image = Image.fromarray(cropped_image)
        try:
            ocr_result = ", text inside in image: " + pytesseract.image_to_string(pil_image)
            text += ocr_result
            if ocr_result.strip():
                print("Detected Text:", ocr_result)
            else:
                print("No text detected.")
        except Exception as e:
            print(f"Error in OCR: {e}")
    else:
        text += ". There is no text inside in the image."
    
    print("Complete text:", text)
    generateText(text)

def home(request):
    return render(request, 'index.html')

@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            if 'image' not in data:
                return JsonResponse({"status": "error", "message": "Image data missing"}, status=400)

            image_data = data['image']
            if not image_data:
                return JsonResponse({"status": "error", "message": "Empty image data"}, status=400)

            format, imgstr = image_data.split(';base64,')
            image_data = base64.b64decode(imgstr)
            image = Image.open(io.BytesIO(image_data))

            if image.mode == 'RGBA':
                image = image.convert('RGB')

            mainCode(image)
            return JsonResponse({"status": "success", "message": "Image processed successfully"})
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)
        except ValueError as e:
            return JsonResponse({"status": "error", "message": f"Error processing image data: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)
