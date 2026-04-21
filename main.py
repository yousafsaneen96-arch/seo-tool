from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
return """ <style>
body {
margin: 0;
font-family: Arial, sans-serif;
background: #0f172a;
color: white;
}
.container {
max-width: 900px;
margin: 60px auto;
padding: 30px;
text-align: center;
}
input {
padding: 10px;
width: 60%;
}
button {
padding: 10px;
cursor: pointer;
}
.card {
margin-top: 10px;
padding: 10px;
background: #1e293b;
} </style>

```
<div class="container">
    <h1>SEO Analyzer Pro</h1>
    <p>Built by Yousaf Saneen</p>

    <input id="url" placeholder="Enter website URL">
    <button onclick="run()">Analyze</button>

    <div id="out"></div>
</div>

<script>
async function run(){
    let url = document.getElementById('url').value;
    let res = await fetch(`/analyze?url=${url}`);
    let data = await res.json();

    document.getElementById('out').innerHTML = `
        <div class="card"><b>Score:</b> ${data.score}</div>
        <div class="card"><b>Title:</b> ${data.title}</div>
        <div class="card"><b>Meta:</b> ${data.meta_description}</div>
        <div class="card"><b>H1:</b> ${data.h1}</div>
        <div class="card"><b>Word Count:</b> ${data.word_count}</div>
    `;
}
</script>
"""
```

@app.get("/analyze")
def analyze(url: str):
try:
headers = {"User-Agent": "Mozilla/5.0"}
r = requests.get(url, headers=headers, timeout=10)

```
    soup = BeautifulSoup(r.text, "html.parser")

    for script in soup(["script", "style", "noscript"]):
        script.extract()

    title = soup.title.string.strip() if soup.title and soup.title.string else "No title"

    meta = soup.find("meta", attrs={"name": "description"})
    meta_desc = meta["content"] if meta and meta.get("content") else "No meta description"

    h1 = soup.find("h1")
    h1_text = h1.get_text(strip=True) if h1 else "No H1"

    text = soup.get_text()
    word_count = len(text.split())

    score = 100

    return {
        "title": title,
        "meta_description": meta_desc,
        "h1": h1_text,
        "word_count": word_count,
        "score": score
    }

except Exception as e:
    return {"error": str(e)}
```
