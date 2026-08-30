import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


def normalize_url(raw_url: str) -> str:
    raw_url = raw_url.strip()
    if not raw_url.startswith(("http://", "https://")):
        raw_url = "https://" + raw_url
    return raw_url


def analyze_url(raw_url: str) -> dict:
    url = normalize_url(raw_url)
    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError("Invalid URL")

    start = time.time()
    response = requests.get(
        url,
        timeout=10,
        headers={"User-Agent": "Mozilla/5.0 (SEO-Analyzer/1.0)"},
    )
    load_time = round(time.time() - start, 2)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("title")
    has_title = bool(title_tag and title_tag.get_text(strip=True))

    meta_desc = soup.find("meta", attrs={"name": "description"})
    has_meta_desc = bool(meta_desc and meta_desc.get("content", "").strip())

    images = soup.find_all("img")
    missing_alt = [img for img in images if not img.get("alt", "").strip()]

    viewport = soup.find("meta", attrs={"name": "viewport"})
    has_viewport = bool(viewport)

    is_https = parsed.scheme == "https"

    canonical = soup.find("link", attrs={"rel": "canonical"})
    has_canonical = bool(canonical and canonical.get("href", "").strip())

    checks = [
        {
            "name": "Title tag present",
            "pass": has_title,
            "detail": title_tag.get_text(strip=True)[:60] if has_title else "No title tag found",
        },
        {
            "name": "Meta description",
            "pass": has_meta_desc,
            "detail": "Present" if has_meta_desc else "Meta description missing",
        },
        {
            "name": "Image alt texts",
            "pass": len(missing_alt) == 0,
            "detail": "All present" if not missing_alt else f"{len(missing_alt)} missing",
        },
        {
            "name": "Mobile viewport",
            "pass": has_viewport,
            "detail": "Present" if has_viewport else "Viewport meta tag missing",
        },
        {
            "name": "HTTPS enabled",
            "pass": is_https,
            "detail": "Active" if is_https else "Site is served over HTTP",
        },
        {
            "name": "Canonical tag",
            "pass": has_canonical,
            "detail": "Present" if has_canonical else "Canonical link tag missing",
        },
    ]

    passed = sum(1 for c in checks if c["pass"])
    score = round((passed / len(checks)) * 100)

    return {
        "url": url,
        "score": score,
        "load_time": load_time,
        "checks": checks,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(silent=True) or {}
    raw_url = data.get("url", "")
    if not raw_url:
        return jsonify({"error": "URL is required"}), 400
    try:
        result = analyze_url(raw_url)
        return jsonify(result)
    except requests.exceptions.RequestException:
        return jsonify({"error": "Couldn't reach that site. Check the URL and try again."}), 400
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
