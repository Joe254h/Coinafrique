---
title: Coinafrique
emoji: 🏠
colorFrom: yellow
colorTo: green
sdk: docker
app_file: coinafrique.py
pinned: false
---

# CoinAfrique Real Estate Dashboard

Interactive Flask web application for scraping, cleaning, uploading, visualizing, and downloading CoinAfrique Senegal real estate data.

## Features

- Scrape villas, terrains, and apartments from CoinAfrique Senegal.
- Upload CSV datasets collected from other scraping tools.
- Store raw and cleaned records in SQLite.
- Explore price, room, surface, and location trends with Plotly charts.
- Download collected datasets as CSV files.
- Switch between light and dark themes with custom CSS and browser local storage.
- Collect user feedback through KoboToolbox and Google Forms.

## Run Locally

```bash
pip install -r requirements.txt
python coinafrique.py
```

## Hugging Face Space

This repository is configured for a Hugging Face Docker Space that runs the Flask app from `coinafrique.py` on port `7860`.

Live app URL:

https://huggingface.co/spaces/joe254h/coinafrique
