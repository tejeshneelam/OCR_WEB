# OCR_WEB

Web-based OCR application with a **React frontend** (`ocr-frontend/`) and a **FastAPI backend** (`ocr-pro/`) that performs text extraction from images using multiple OCR engines and models.

## Features

- Upload an image and extract text via a REST API
- Multiple OCR engines/models selectable via query parameter:
  - **TrOCR** – transformer-based handwritten OCR (default)
  - **EasyOCR** – scene text recognition
  - **Tesseract** – classic open-source OCR
  - **Donut** – document understanding transformer
  - **OCR-ViT** – single-image ViT-based OCR
- Automatic line segmentation for TrOCR (OpenCV-based pre-processing)
- CORS enabled for local frontend development
- JSON response includes extracted text and processing time
- Optional GPU acceleration via CUDA

## Setup

### Prerequisites

- **Node.js** (for the frontend)
- **Python 3.9+** (for the backend)
- *(Optional)* A CUDA-capable GPU for faster model inference

### Backend (FastAPI)

```bash
cd ocr-pro
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend starts on `http://localhost:8000` by default.

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/` | Health check |
| `POST` | `/api/translate` | Extract text from an uploaded image |

**`/api/translate` query parameters:**

| Parameter | Values | Default |
|-----------|--------|---------|
| `model` | `trocr`, `easyocr`, `tesseract`, `donut`, `ocrvit` | `trocr` |

### Frontend (React / Create React App)

```bash
cd ocr-frontend
npm install
npm start
```

The frontend starts on `http://localhost:3000` by default.

## Usage

1. Start the backend:
   ```bash
   cd ocr-pro
   uvicorn main:app --reload
   ```
2. Start the frontend:
   ```bash
   cd ocr-frontend
   npm start
   ```
3. Open `http://localhost:3000` in your browser.
4. Upload an image to extract text. The OCR model can also be selected directly via the API:
   ```http
   POST http://localhost:8000/api/translate?model=easyocr
   Content-Type: multipart/form-data

   file=<image file>
   ```

Example with `curl`:
```bash
curl -X POST "http://localhost:8000/api/translate?model=tesseract" \
  -F "file=@/path/to/image.png"
```

Response:
```json
{
  "text": "Extracted text from the image...",
  "time": 1.23
}
```

## License

MIT License
