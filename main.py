from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <style>
    body {
      margin: 0;
      font-family: Arial, sans-serif;
      background: linear-gradient(135deg, #0f172a, #1e293b);
      color: white;
    }

    .container {
      max-width: 700px;
      margin: 80px auto;
      padding: 30px;
      background: rgba(255,255,255,0.05);
      border-radius: 16px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.3);
      text-align: center;
    }

    input {
      padding: 12px;
      width: 70%;
      border-radius: 8px;
      border: none;
      margin-right: 10px;
    }

    button {
      padding: 12px 20px;
      background: #3b82f6;
      border: none;
      border-radius: 8px;
      color: white;
      cursor: pointer;
    }

    .result {
      margin-top: 20px;
      text-align: left;
    }

    .card {
      margin-bottom: 10px;
      padding: 10px;
      background: rgba(255,255,255,0.05);
      border-radius: 6px;
    }
    </style>

    <div class="container">
      <h1>SEO Analyzer Pro</h1>

      <input id='url' placeholder='Enter website URL'>
      <button onclick='run()'>Analyze</button>

      <div id='out' class='result'></div>
    </div>

    <script>
    async function run(){
      let url = document.getElementById('url').value;
      let res = await fetch(`/analyze?url=${url}`);
      let data = await res.json();
      
      // Added a quick check to display errors nicely if the URL fails
      if (data.error) {
        document.getElementById('out').innerHTML = `<div class="card" style="color: #ef4444;"><b>Error:</b> ${data.error}</div>`;
        return;
      }

      document.getElementById('out').innerHTML = `
        <div class="card"><b>Score:</b> ${data.score}/100</div>
        <div class="card"><b>Title:</b> ${data.title}</div>
        <div class="card"><b>Meta:</b> ${data.meta_description}</div>
        <div class="card"><b>H1:</b> ${data.h1}</div>
        <div class="card"><b>Word Count:</b> ${data.word_count}</div>
        <div class="card"><b>Images:</b> ${data.images}</div>
        <div class="card"><b>Missing ALT:</b> ${data.missing_alt}</div>
        <div class="card"><b>Links:</b> ${data.internal_links} internal / ${data.external_links} external</div>
        <div class="card"><b>Issues:</b> ${data.issues.length ? data.issues.join(", ") : "No issues"}</div>
      `;
    }
    </script>
    """

@app.get("/analyze")
def analyze(url: str):
    # Everything below here is now properly indented!
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.string if soup.title else "No title"

        meta = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta["content"] if meta else "No meta description"

        h1_tags = soup.find_all("h1")
        h1_text = h1_tags[0].text if h1_tags else "No H1"

        # NEW FEATURES 👇
        text = soup.get_text()
        word_count = len(text.split())

        images = soup.find_all("img")
        missing_alt = [img for img in images if not img.get("alt")]

        links = soup.find_all("a", href=True)
        internal_links = [l for l in links if url in l["href"]]
        external_links = [l for l in links if url not in l["href"]]

        https = url.startswith("https")

        canonical = soup.find("link", rel="canonical")
        robots = soup.find("meta", attrs={"name": "robots"})

        # ISSUES
        issues = []

        if len(title) < 30:
            issues.append("Title too short")

        if meta_desc == "No meta description":
            issues.append("Missing meta description")

        if not h1_tags:
            issues.append("Missing H1")

        if len(missing_alt) > 0:
            issues.append("Images missing alt text")

        # SEO SCORE
        score = 100
        score -= len(issues) * 10

        return {
            "title": title,
            "meta_description": meta_desc,
            "h1": h1_text,
            "word_count": word_count,
            "images": len(images),
            "missing_alt": len(missing_alt),
            "internal_links": len(internal_links),
            "external_links": len(external_links),
            "https": https,
            "canonical": bool(canonical),
            "robots_meta": bool(robots),
            "score": score,
            "issues": issues
        }

    except Exception as e:
        # Better error handling
        return {"error": "Invalid URL or unable to fetch", "details": str(e)}