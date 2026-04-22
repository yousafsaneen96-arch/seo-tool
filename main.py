from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time
import re
from collections import Counter

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    body { margin: 0; font-family: 'Poppins', sans-serif; background: linear-gradient(135deg, #0f172a, #1e293b); color: white; }
    .container { max-width: 900px; margin: 60px auto; padding: 30px; background: rgba(255,255,255,0.05); border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); text-align: center; }
    .brand { color: #94a3b8; font-size: 13px; margin-bottom: 20px; }
    input { padding: 12px; width: 65%; border-radius: 8px; border: none; margin-right: 10px; }
    button { padding: 12px 20px; background: linear-gradient(135deg, #3b82f6, #06b6d4); border: none; border-radius: 8px; color: white; cursor: pointer; font-weight: 600; }
    .card { margin-bottom: 10px; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 6px; text-align: left; }
    .score { font-size: 22px; font-weight: bold; background: linear-gradient(135deg, #22c55e, #4ade80); padding: 10px; border-radius: 8px; color: #022c22; text-align: center; margin-bottom: 15px; }
    .google-score { font-size: 18px; font-weight: bold; background: linear-gradient(135deg, #f59e0b, #fbbf24); padding: 10px; border-radius: 8px; color: #451a03; text-align: center; margin-bottom: 15px; }
    .issues-list { color: #fca5a5; }
    .keyword-badge { display: inline-block; background: rgba(59, 130, 246, 0.2); border: 1px solid #3b82f6; padding: 4px 10px; border-radius: 20px; margin: 4px; font-size: 13px; }
    .keyword-density { color: #9ca3af; font-size: 11px; margin-left: 4px; }
    </style>

    <div class="container">
      <h1>SEO Analyzer <span style="color:#3b82f6;">Pro</span></h1>
      <div class="brand">Built by Yousaf Saneen</div>

      <input id='url' placeholder='Enter website URL'>
      <button onclick='run()'>Submit</button>

      <div id='out' style='margin-top: 20px;'></div>
    </div>

    <script>
    async function run(){
      let url = document.getElementById('url').value;

      document.getElementById('out').innerHTML = 
        '<div class="card" style="text-align:center;">Analyzing site & extracting keywords... please wait.</div>';

      try {
          let res = await fetch(`/analyze?url=${url}`);
          let data = await res.json();

          if (data.error) {
            document.getElementById('out').innerHTML = `<div class="card" style="color:red; text-align:center;">Error: ${data.error}</div>`;
            return;
          }

          document.getElementById('out').innerHTML = `
            <div class="score">On-Page SEO Score: ${data.score}/100</div>
            <div class="google-score">Official Google Mobile Speed: ${data.google_speed}/100</div>
            
            <div class="card"><b>Title:</b> ${data.content.title}</div>
            <div class="card"><b>Meta Description:</b> ${data.content.meta_description}</div>
            
            <div class="card">
                <b style="color:#3b82f6;">Top Keywords & Density:</b><br>
                <div style="margin-top:10px;">
                    ${data.keywords.length ? data.keywords.map(k => `
                        <div class="keyword-badge">
                            <b>${k.word}</b> <span class="keyword-density">(${k.count} times - ${k.density}%)</span>
                        </div>
                    `).join("") : "No significant keywords found."}
                </div>
            </div>

            <div class="card">
                <b>Server Performance:</b> Load Time: ${data.performance.load_time_seconds}s | Status Code: ${data.performance.status_code}
            </div>
            
            <div class="card">
                <b>Content Structure:</b> ${data.content.word_count} words | H1 Tags: ${data.content.h1_count} | H2 Tags: ${data.content.h2_count}
            </div>
            
            <div class="card">
                <b>Images:</b> ${data.images.total} total | ${data.images.missing_alt} missing alt text
            </div>
            
            <div class="card">
                <b>Links:</b> ${data.links.internal} internal | ${data.links.external} external
            </div>

            <div class="card issues-list">
                <b>Issues Found:</b><br>
                ${data.issues.length ? data.issues.map(i => `• ${i}<br>`).join("") : "No major issues found!"}
            </div>
          `;
      } catch (err) {
          document.getElementById('out').innerHTML = 
              `<div class="card" style="color:red; text-align:center;">Failed to connect to the server.</div>`;
      }
    }
    </script>
    """

@app.get("/analyze")
def analyze(url: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
        
        start_time = time.time()
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        load_time = round(time.time() - start_time, 2)
        
        status_code = r.status_code
        final_url = r.url 
        
        soup = BeautifulSoup(r.text, "html.parser")

        # Google API Check
        google_score = "Checking..."
        try:
            google_api = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile&key=AIzaSyAJSIWD5LTnZK_yC4mKeyxw76COHxdESPU"
            google_req = requests.get(google_api, timeout=40)
            if google_req.status_code == 200:
                raw_score = google_req.json()["lighthouseResult"]["categories"]["performance"]["score"]
                google_score = int(raw_score * 100)
            else:
                google_score = "Failed"
        except Exception:
            google_score = "Timeout"

        for s in soup(["script", "style", "noscript"]):
            s.extract()

        text = soup.get_text(separator=" ")
        
        # --- NEW STEP: KEYWORD DENSITY EXTRACTOR ---
        # 1. Clean the text: convert to lowercase and grab only actual words
        raw_words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # 2. Ignore common filler words (Stopwords)
        stopwords = {"the", "and", "for", "that", "this", "with", "from", "your", "are", "have", "not", "can", "you", "all", "was", "but", "our", "out", "has", "about", "what", "how", "will", "more", "their", "any", "which", "some", "they", "get"}
        
        # 3. Filter the words
        meaningful_words = [w for w in raw_words if w not in stopwords]
        total_meaningful = len(meaningful_words)
        
        # 4. Count and calculate percentage
        word_counts = Counter(meaningful_words)
        top_keywords = []
        for word, count in word_counts.most_common(10): # Get top 10 words
            density = round((count / total_meaningful) * 100, 2) if total_meaningful > 0 else 0
            top_keywords.append({"word": word, "count": count, "density": density})
        # ---------------------------------------------

        words = [w for w in text.split() if len(w) > 2]
        
        title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_desc_tag["content"].strip() if meta_desc_tag and meta_desc_tag.get("content") else "No meta description"
        canonical_tag = soup.find("link", rel="canonical")
        canonical = canonical_tag["href"] if canonical_tag and canonical_tag.get("href") else "Missing"
        robots_tag = soup.find("meta", attrs={"name": "robots"})
        meta_robots = robots_tag["content"] if robots_tag and robots_tag.get("content") else "Index, Follow"
        
        h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1")]
        h2_tags = [h.get_text(strip=True) for h in soup.find_all("h2")]

        images = soup.find_all("img")
        missing_alt = [urljoin(url, img.get("src")) for img in images if img.get("src") and not img.get("src").startswith("data:") and not img.get("alt")]

        links = soup.find_all("a", href=True)
        internal_links = set()
        external_links = set()
        for l in links:
            href = l.get("href")
            if not href: continue
            if href.startswith("/") or url in href: internal_links.add(urljoin(url, href))
            elif href.startswith("http"): external_links.add(href)

        issues = []
        if status_code >= 400: issues.append(f"Page returned HTTP {status_code}")
        if len(h1_tags) == 0: issues.append("Missing H1 Tag")
        if canonical == "Missing": issues.append("Missing Canonical Tag")
        if "noindex" in meta_robots.lower(): issues.append("Page is blocked from indexing")
        if len(missing_alt) > 0: issues.append(f"{len(missing_alt)} images missing alt text")

        # Added keyword stuffing check to issues
        for kw in top_keywords:
            if kw["density"] > 5.0:  # If a word is over 5% of the page text
                issues.append(f"Possible keyword stuffing: '{kw['word']}' has a density of {kw['density']}%")

        score = max(0, 100 - (len(issues) * 5))

        return {
            "google_speed": google_score,
            "performance": {"status_code": status_code, "load_time_seconds": load_time},
            "indexing": {"canonical": canonical, "meta_robots": meta_robots},
            "content": {"title": title, "meta_description": meta_desc, "word_count": len(words), "h1_count": len(h1_tags), "h2_count": len(h2_tags)},
            "keywords": top_keywords,
            "images": {"total": len(images), "missing_alt": len(missing_alt)},
            "links": {"internal": len(internal_links), "external": len(external_links)},
            "score": score,
            "issues": issues
        }

    except Exception as e:
        return {"error": str(e)}