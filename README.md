# Automated OMR Evaluation & Scoring System

## Overview
This project automates the evaluation of OMR sheets for placement readiness assessments. It replaces manual checking with an **accurate, fast, and scalable system**.

- Evaluates OMR sheets captured via mobile or scanner.
- Computes **subject-wise scores (0–20)** and **total score (0–100)**.
- Provides an **evaluator-friendly Streamlit interface**.
- Supports **sample data and template generation** for testing.

---

## Features
- Upload OMR sheet images.
- Automatic preprocessing (rotation, skew correction, perspective).
- Bubble detection and evaluation using **OpenCV**.
- Compare with answer keys and generate scores.
- Display results in Streamlit dashboard.
- Export results to CSV/Excel.
- Placeholder for ML-based ambiguous bubble classification.

---

## Project Structure
Automated-OMR-Evaluation/
├── app.py # Streamlit app
├── omr.py # OMR evaluation logic
├── template_generator.py # Generates sample OMR templates
├── requirements.txt # Python dependencies
├── README.md # Project documentation
├── sample_data/ # Sample OMR images
│ └── sample_captured.png

## Tech Stack
- Python 3, OpenCV, NumPy, Pillow
- Streamlit (frontend & dashboard)
- SQLite/PostgreSQL (optional for storage)
- Streamlit Cloud deployment


