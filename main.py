from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    # The code inside the function MUST be indented (usually 4 spaces)
    return """
    <h2>My SEO Tool</h2>
    <input id='url' placeholder='Enter website URL'>
    <button onclick='run()'>Analyze</button>
    <pre id='out'></pre>
    <script>
    async function run(){
      let url = document.getElementById('url').value;
      let res = await fetch(`/analyze?url=${url}`);
      let data = await res.json();
      document.getElementById('out').innerText = JSON.stringify(data,null,2);
    }
    </script>
    """

@app.get("/analyze")
def analyze(url: str):
    # This entire block needs to be indented under the function definition
    try:
        # The code inside the try block needs another level of indentation
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        
        title = soup.title.string if soup.title else "No title"

        meta = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta["content"] if meta else "No meta description"

        h1 = soup.find("h1")
        h1_text = h1.text if h1 else "No H1"

        issues = []

        if len(title) < 30:
            issues.append("Title too short")

        if meta_desc == "No meta description":
            issues.append("Missing meta description")

        if h1_text == "No H1":
            issues.append("Missing H1")

        return {
            "title": title,
            "meta_description": meta_desc,
            "h1": h1_text,
            "issues": issues
        }

    except Exception as e:
        # The except block must align with the try block
        return {"error": "Invalid URL or unable to fetch", "details": str(e)}