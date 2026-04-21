from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    # INDENTED HERE
    return """
    <style>
    @import url('[https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap](https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap)');

    body {
      margin: 0;
      font-family: 'Poppins', sans-serif;
      background: linear-gradient(135deg, #0f172a, #1e293b);
      color: white;
    }

    .container {
      max-width: 900px;
      margin: 60px auto;
      padding: 30px;
      background: rgba(255,255,255,0.05);
      border-radius: 16px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.3);
      text-align: center;
    }

    .brand {
      color: #94a3b8;
      font-size: 13px;
      margin-bottom: 20px;
    }

    input {
      padding: 12px;
      width: 65%;
      border-radius: 8px;
      border: none;
      margin-right: 10px;
    }

    button {
      padding: 12px 20px;
      background: linear-gradient(135deg, #3b82f6, #06b6d4);
      border: none;
      border-radius: 8px;
      color: white;
      cursor: pointer;
    }

    .card {
      margin-bottom: 10px;
      padding: 12px;
      background: rgba(255,255,255,0.05);
      border-radius: 6px;
    }

    .score {
      font-size: 22px;
      font-weight: bold;
      background: linear-gradient(135deg, #22c55e, #4ade80);
      padding: 10px;
      border-radius: 8px;
      color: #022c22;
      text-align: center;
      margin-bottom: 15px;
    }
    </style>

    <div class="container">
      <h1>SEO Analyzer <span style="color:#3b82f6;">Pro</span></h1>
      <div class="brand">Built by Yousaf Saneen</div>

      <input id='url' placeholder='Enter website URL'>
      <button onclick='run()'>Analyze</button>

      <div id='out'></div>
    </div>

    <script>
    async function run(){
      let url = document.getElementById('url').value;

      document.getElementById('out').innerHTML =
        '<div class="card">Analyzing... detecting site type</div>';

      let res = await fetch(`/analyze?url=${url}`);
      let data = await res.json();

      if (data.error) {
        document.getElementById('out').innerHTML =
          `<div class="card" style="color:red;">${data.error}</div>`;
        return;
      }

      document.getElementById('out').innerHTML = `
        <div class="score">SEO Score: ${data.score}/100</div>

        <div class="card"><b>Title:</b> ${data.title}</div>
        <div class="card"><b>Meta:</b> ${data.meta_description}</div>
        <div class="card"><b>H1:</b> ${data.h1}</div>

        <div class="card"><b>Word Count:</b> ${data.word_count}</div>

        <div class="card"><b>Images:</b> ${data.images}</div>
        <div class="card"><b>Missing ALT:</b> ${data.missing_alt_count}</div>

        ${data.missing_alt_images.length ? `
        <div class="card">
        <b>Images Missing ALT:</b><br>
        ${data.missing_alt_images.map(i => `<div>• ${i}</div>`).join("")}
        </div>` : ""}

        <div class="card">
        <b>Internal Links:</b><br>
        ${data.internal_links.map(l => `<div>• ${l}</div>`).join("")}
        </div>

        <div class="card">
        <b>External Links:</b><br>
        ${data.external_links.map(l => `<div>• ${l}</div>`).join("")}
        </div>

        <div class="card"><b>Issues:</b> ${
          data.issues.length ? data.issues.join(", ") : "No major issues"
        }</div>
      `;
    }
    </script>
    """

@app.get("/analyze")
def analyze(url: str):
    # INDENTED HERE
    try:
        # INDENTED HERE
        headers = {"User-Agent": "Mozilla/5.0"}

        # STEP 1: Normal request
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        for s in soup(["script", "style", "noscript"]):
            s.extract()

        text = soup.get_text(separator=" ")
        words = [w for w in text.split() if len(w) > 2]

        # STEP 2: AUTO SWITCH (JS DETECTION)
        if len(words) < 200:
            try:
                from playwright.sync_api import sync_playwright

                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.goto(url, timeout=60000)
                    page.wait_for_timeout(3000)

                    html = page.content()
                    browser.close()

                soup = BeautifulSoup(html, "html.parser")

                for s in soup(["script", "style", "noscript"]):
                    s.extract()

                text = soup.get_text(separator=" ")
                words = [w for w in text.split() if len(w) > 2]

            except Exception as inner_e:
                # Good practice to catch specific exceptions or log them
                print(f"Playwright fallback failed: {inner_e}")

        # Title
        title = soup.title.string.strip() if soup.title and soup.title.string else "No title"

        # Meta
        meta = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta["content"].strip() if meta and meta.get("content") else "No meta description"

        # H1
        h1_tags = soup.find_all("h1")
        h1_text = h1_tags[0].get_text(strip=True) if h1_tags else "No H1"

        word_count = len(words)

        # Images
        images = soup.find_all("img")
        missing_alt = []

        for img in images:
            src = img.get("src")

            if not src or src.startswith("data:image"):
                continue

            if not img.get("alt"):
                missing_alt.append(urljoin(url, src))

        # Links
        links = soup.find_all("a", href=True)

        internal_links = set()
        external_links = set()

        for l in links:
            href = l.get("href")

            if not href:
                continue

            if href.startswith("/") or url in href:
                internal_links.add(urljoin(url, href))
            elif href.startswith("http"):
                external_links.add(href)

        # Issues
        issues = []

        if len(title) < 30:
            issues.append("Title too short")

        if meta_desc == "No meta description":
            issues.append("Missing meta description")

        if not h1_tags:
            issues.append("Missing H1")

        if len(missing_alt) > 0:
            issues.append(f"{len(missing_alt)} images missing alt")

        if word_count < 300:
            issues.append("Thin content")

        score = max(10, 100 - len(issues) * 8)

        return {
            "title": title,
            "meta_description": meta_desc,
            "h1": h1_text,
            "word_count": word_count,
            "images": len(images),
            "missing_alt_count": len(missing_alt),
            "missing_alt_images": missing_alt[:10],
            "internal_links": list(internal_links)[:10],
            "external_links": list(external_links)[:10],
            "score": score,
            "issues": issues
        }

    except Exception as e:
        # INDENTED HERE
        return {"error": str(e)}