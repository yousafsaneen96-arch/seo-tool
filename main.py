from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
return """ <style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

```
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

h1 {
  margin-bottom: 5px;
}

.brand {
  color: #94a3b8;
  font-size: 13px;
  margin-bottom: 25px;
  letter-spacing: 1px;
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
  transition: 0.3s;
}

button:hover {
  transform: scale(1.05);
}

.result {
  margin-top: 25px;
  text-align: left;
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

  <div id='out' class='result'></div>
</div>

<script>
async function run(){
  let url = document.getElementById('url').value;
  let res = await fetch(`/analyze?url=${url}`);
  let data = await res.json();

  if(data.error){
    document.getElementById('out').innerHTML = `<div class="card">${data.error}</div>`;
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
    ${data.internal_links.slice(0,10).map(l => `<div>• ${l}</div>`).join("")}
    </div>

    <div class="card">
    <b>External Links:</b><br>
    ${data.external_links.slice(0,10).map(l => `<div>• ${l}</div>`).join("")}
    </div>

    <div class="card"><b>Issues:</b> ${
      data.issues.length ? data.issues.join(", ") : "No major issues"
    }</div>
  `;
}
</script>
"""
```

@app.get("/analyze")
def analyze(url: str):
try:
headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

```
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    # Remove unwanted elements
    for script in soup(["script", "style", "noscript"]):
        script.extract()

    # Title
    title = soup.title.string.strip() if soup.title and soup.title.string else "No title"

    # Meta
    meta = soup.find("meta", attrs={"name": "description"})
    meta_desc = meta["content"].strip() if meta and meta.get("content") else "No meta description"

    # H1
    h1_tags = soup.find_all("h1")
    h1_text = h1_tags[0].get_text(strip=True) if h1_tags else "No H1"

    # Word count (cleaned)
    text = soup.get_text(separator=" ")
    words = [w for w in text.split() if len(w) > 2]
    word_count = len(words)

    # Images
    images = soup.find_all("img")
    missing_alt = []
    for img in images:
        if not img.get("alt"):
            src = img.get("src")
            if src:
                missing_alt.append(urljoin(url, src))

    # Links
    links = soup.find_all("a", href=True)
    internal_links = []
    external_links = []

    for l in links:
        href = l["href"]

        if href.startswith("/") or url in href:
            internal_links.append(urljoin(url, href))
        elif href.startswith("http"):
            external_links.append(href)

    # Issues
    issues = []

    if len(title) < 30:
        issues.append("Title too short")

    if meta_desc == "No meta description":
        issues.append("Missing meta description")

    if not h1_tags:
        issues.append("Missing H1")

    if len(missing_alt) > 0:
        issues.append("Images missing alt text")

    # Score
    score = max(0, 100 - (len(issues) * 10))

    return {
        "title": title,
        "meta_description": meta_desc,
        "h1": h1_text,
        "word_count": word_count,
        "images": len(images),
        "missing_alt_count": len(missing_alt),
        "missing_alt_images": missing_alt,
        "internal_links": internal_links,
        "external_links": external_links,
        "score": score,
        "issues": issues
    }

except Exception as e:
    return {"error": str(e)}
```
