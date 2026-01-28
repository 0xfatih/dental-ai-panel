# 🦷 Dental AI Panel

An **AI-powered web platform** for automated dental X-ray analysis, built with **Django** and **deep learning–based object detection** models.

This project aims to assist dentists by providing fast, consistent, and visual AI-supported diagnostics from dental radiographs.

---

## 🚀 Features

- 🔐 Secure doctor authentication (login & register)
- 📤 Dental X-ray upload system
- 🤖 AI-based disease detection (YOLO-based inference)
- 📊 Prediction results with confidence scores
- 🖼️ Bounding box visualization on X-rays
- 🌙 Dark mode support
- 📱 Responsive admin dashboard (SB Admin)

---

## 🛠️ Tech Stack

**Backend**
- Python
- Django

**AI / Machine Learning**
- Deep Learning
- YOLO (Object Detection)
- Computer Vision

**Frontend**
- HTML
- CSS
- Bootstrap (SB Admin Template)
- JavaScript

**Database**
- SQLite (development)

---

## 📂 Project Structure

dental-ai-panel/
│
├── core/ # Core app (models, views, ML inference)
├── proje1/ # Django project settings
├── templates/ # HTML templates
├── static/ # Static files (CSS, JS, images)
├── manage.py
└── README.md

---

## 🧠 AI Inference Pipeline

1. Doctor uploads a dental X-ray
2. Image is processed by the YOLO-based detection model
3. Detected findings are returned with:
   - Class label
   - Confidence score
   - Bounding box coordinates
4. Results are visualized directly on the X-ray image

> **Note:** Trained model files are not included in this repository.

---

## ⚠️ Notes

- AI model weights (`.pt`, `.h5`, `.onnx`) are excluded from the repository
- Large media files (e.g. background videos) are intentionally ignored
- This repository focuses on **software architecture and AI integration**

---

## 📌 Future Improvements

- 📄 Automated PDF medical reports
- 📈 Model performance metrics (precision, recall, mAP)
- 🧪 Multiple model support
- 🐳 Dockerized deployment
- ☁️ Cloud deployment (AWS / Render / Railway)

