from fastapi import FastAPI, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from transformers import (
    TrOCRProcessor,
    VisionEncoderDecoderModel,
    DonutProcessor,
    VisionEncoderDecoderModel as DonutModel
)
from PIL import Image
import torch
import io
import cv2
import numpy as np
import easyocr
import pytesseract
import time

# === Setup ===
app = FastAPI()

# 👇 Add all possible frontend URLs here, including React dev ports
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5174",
    "http://127.0.0.1:5174"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# === Load All Models ===
trocr_processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
trocr_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten").to(device)
easyocr_reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available())
donut_processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base")
donut_model = DonutModel.from_pretrained("naver-clova-ix/donut-base").to(device)

@app.post("/api/translate")
async def translate(file: UploadFile = File(...), model: str = Query("trocr")):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    start_time = time.time()

    try:
        if model == "trocr":
            lines = preprocess_lines(image)
            results = []
            for line in lines:
                pixel_values = trocr_processor(images=line, return_tensors="pt").pixel_values.to(device)
                generated_ids = trocr_model.generate(pixel_values)
                text = trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
                results.append(text)
            final_text = "\n".join(results)

        elif model == "easyocr":
            image_np = np.array(image)
            result = easyocr_reader.readtext(image_np, detail=0)
            final_text = "\n".join(result)

        elif model == "tesseract":
            final_text = pytesseract.image_to_string(image)

        elif model == "donut":
            pixel_values = donut_processor(image, return_tensors="pt").pixel_values.to(device)
            task_prompt = "<s_docvqa>"
            decoder_input_ids = donut_processor.tokenizer(task_prompt, add_special_tokens=False, return_tensors="pt").input_ids
            outputs = donut_model.generate(pixel_values, decoder_input_ids=decoder_input_ids.to(device), max_length=512)
            final_text = donut_processor.batch_decode(outputs, skip_special_tokens=True)[0]

        elif model == "ocrvit":
            pixel_values = trocr_processor(images=image, return_tensors="pt").pixel_values.to(device)
            generated_ids = trocr_model.generate(pixel_values)
            final_text = trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        else:
            return {"error": f"Unsupported model: {model}"}

        elapsed = round(time.time() - start_time, 2)
        print(f"[{model}] Final Text Output: {final_text}")
        return {"text": final_text.strip(), "time": elapsed}

    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def root():
    return {"message": "OCR API running with TrOCR, EasyOCR, Tesseract, Donut, OCR-ViT"}

def preprocess_lines(image_pil):
    image_np = np.array(image_pil)
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (image_np.shape[1] // 2, 5))
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    lines = []
    for cnt in sorted(contours, key=lambda c: cv2.boundingRect(c)[1]):
        x, y, w, h = cv2.boundingRect(cnt)
        line_img = image_np[y:y+h, x:x+w]
        line_pil = Image.fromarray(line_img)
        lines.append(line_pil)
    return lines
