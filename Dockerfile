FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python3 -m src.combine_datasets \
    && python3 -m src.clean_amount \
    && python3 -m src.clean_dates \
    && python3 -m src.clean_categories \
    && python3 -m src.clean_payment_mode \
    && python3 -m src.dedupe \
    && python3 -m src.anomaly_detection \
    && python3 -m src.chunking

# embed_and_store.py needs OPENAI_API_KEY, which is only available as a
# runtime secret on Render, not at build time - so embeddings are built on
# first container start instead of at image-build time (see start.sh).
COPY start.sh .
RUN chmod +x start.sh

EXPOSE 8000
CMD ["./start.sh"]
