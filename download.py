from transformers import AutoModelForSequenceClassification, AutoTokenizer
import os


MODEL_PATH = "models/unitary-toxic-bert"

os.makedirs(MODEL_PATH, exist_ok=True)

print("Скачивание модели...")
model = AutoModelForSequenceClassification.from_pretrained("unitary/toxic-bert")
tokenizer = AutoTokenizer.from_pretrained("unitary/toxic-bert")

model.save_pretrained(MODEL_PATH)
tokenizer.save_pretrained(MODEL_PATH)

print(f"Модель сохранена в {MODEL_PATH}")
