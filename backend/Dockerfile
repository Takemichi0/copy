FROM python:3.10-slim

WORKDIR /backend

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# for OCR
RUN apt update && apt install -y \
    poppler-utils \
    tesseract-ocr

COPY ./app /backend/app
COPY ./main.py /backend

EXPOSE 8000

CMD ["python3" , "main.py"]
