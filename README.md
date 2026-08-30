# SiteCheck

A lightweight Flask web app that checks a website's core on-page SEO health: title tag, meta description, image alt texts, mobile viewport tag, HTTPS, canonical tag, and page load time.

## Features

- Fetches and parses any public URL with `requests` and `BeautifulSoup`
- Scores the page out of 100 based on five essential SEO checks
- Simple, responsive single-page interface with no build step

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000` in your browser.

## How it works

1. The frontend sends the entered URL to `POST /api/analyze`.
2. The Flask backend fetches the page, parses the HTML, and runs five checks.
3. Results (score, load time, and per-check status) are returned as JSON and rendered on the page.

## Tech stack

Python, Flask, BeautifulSoup, vanilla HTML/CSS/JS.

## Possible next steps

- Add more checks (heading structure, canonical tags, structured data)
- Store analysis history per user
- Add a Lighthouse-style performance breakdown
