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
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-color: #f4f7f6;
        --card-bg: #ffffff;
        --text-main: #1e293b;
        --text-muted: #64748b;
        --primary: #3b82f6;
        --secondary: #0ea5e9;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }

    body {
        margin: 0;
        font-family: 'Poppins', sans-serif;
        background-color: var(--bg-color);
        color: var(--text-main);
    }

    .container {
        max-width: 1100px;
        margin: 50px auto;
        padding: 0 20px;
    }

    .header-section {
        text-align: center;
        margin-bottom: 40px;
    }

    h1 {
        font-size: 2.5rem;
        margin-bottom: 5px;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .brand {
        color: var(--text-muted);
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 30px;
    }

    .search-box {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-bottom: 40px;
    }

    input {
        padding: 16px 24px;
        width: 60%;
        border-radius: 50px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        font-size: 16px;
        font-family: 'Poppins', sans-serif;
        outline: none;
        transition: all 0.3s ease;
    }

    input:focus {
        border-color: var(--primary);
        box-shadow: 0 10px 25px -3px rgba(59, 130, 246, 0.2);
    }

    button {
        padding: 16px 32px;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        background-size: 200% auto;
        border: none;
        border-radius: 50px;
        color: white;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
        transition: all 0.4s ease;
    }

    button:hover {
        background-position: right center;
        transform: translateY(-2px);
    }

    /* Cards & Fluid Layouts */
    .card {
        background: var(--card-bg);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.03);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid #f1f5f9;
    }

    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }

    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 20px;
        color: var(--text-main);
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Scores Row */
    .scores-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 25px;
        margin-bottom: 25px;
    }

    .score-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    .score-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 15px;
        position: relative;
    }
    
    .score-circle::before {
        content: "";
        position: absolute;
        inset: 10px;
        background: white;
        border-radius: 50%;
        z-index: 1;
    }
    
    .score-circle span {
        position: relative;
        z-index: 2;
    }

    .score-label {
        font-weight: 600;
        color: var(--text-muted);
    }

    /* Metrics Grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
    }

    .metric-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .metric-value { font-size: 1.5rem; font-weight: 700; color: var(--text-main); }
    .metric-name { font-size: 0.875rem; color: var(--text-muted); font-weight: 500;}

    /* Social Preview */
    .social-preview-container {
        display: flex;
        gap: 30px;
        flex-wrap: wrap;
    }
    .social-table { flex: 1; min-width: 300px; font-size: 14px;}
    .social-table div { padding: 12px 0; border-bottom: 1px solid #e2e8f0; display: flex; gap: 15px;}
    .social-table div:last-child { border-bottom: none; }
    .social-table b { min-width: 100px; color: var(--text-muted); }
    
    .social-card-wrapper {
        flex: 1;
        min-width: 300px;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
        background: #f8fafc;
    }
    .social-img { width: 100%; height: 200px; object-fit: cover; background: #cbd5e1; }
    .social-text { padding: 20px; }
    .social-text h4 { margin: 0 0 10px 0; font-size: 18px; }
    .social-text p { margin: 0; font-size: 14px; color: var(--text-muted); }

    /* Tags & Keywords */
    .tag-box {
        background: #f1f5f9; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid var(--primary); font-size: 14px;
    }
    .keyword-badge {
        display: inline-block; background: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a8a; padding: 6px 14px; border-radius: 50px; margin: 4px; font-size: 13px; font-weight: 500;
    }
    .phrase-header { margin-top: 20px; font-size: 15px; font-weight: 600; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px; margin-bottom: 12px; color: var(--text-main); }
    
    .issues-list { background: #fef2f2; border: 1px solid #fecaca; border-left: 4px solid var(--danger); }
    .issues-list li { color: #991b1b; margin-bottom: 8px; font-size: 15px;}
    </style>

    <div class="container">
      <div class="header-section">
          <h1>SEO Analyzer Pro</h1>
          <div class="brand">Built by Yousaf Saneen</div>
          
          <div class="search-box">
              <input id='url' placeholder='https://example.com/'>
              <button onclick='run()'>Analyze Website</button>
          </div>
      </div>

      <div id='out'></div>
    </div>

    <script>
    function getScoreColor(score) {
        if(score >= 90) return '#10b981'; // Green
        if(score >= 70) return '#f59e0b'; // Orange
        return '#ef4444'; // Red
    }

    const renderBadges = (arr) => {
        if (!arr || arr.length === 0) return "<span style='font-size:13px; color:#94a3b8;'>None found</span>";
        return arr.map(k => `
            <div class="keyword-badge">
                ${k.phrase} <span style="color:#64748b; font-weight:400; margin-left:4px;">(${k.density}%)</span>
            </div>
        `).join("");
    };

    async function run(){
      let url = document.getElementById('url').value;
      if(!url) return;
      if(!url.startsWith('http')) url = 'https://' + url;

      document.getElementById('out').innerHTML = `
        <div class="card" style="text-align:center; padding: 40px;">
            <div style="font-size: 18px; font-weight: 500; color: var(--text-muted);">
                <span style="display:inline-block; animation: pulse 1.5s infinite;">Scanning website architecture... this will take a moment.</span>
            </div>
        </div>
        <style>@keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }</style>
      `;

      try {
          let res = await fetch(`/analyze?url=${url}`);
          let data = await res.json();

          if (data.error) {
            document.getElementById('out').innerHTML = `<div class="card issues-list" style="text-align:center;">Error: ${data.error}</div>`;
            return;
          }

          let pageScoreColor = getScoreColor(data.score);
          let speedScoreNum = typeof data.google_speed === 'number' ? data.google_speed : 0;
          let speedScoreColor = speedScoreNum > 0 ? getScoreColor(speedScoreNum) : '#cbd5e1';

          document.getElementById('out').innerHTML = `
            
            <div class="scores-grid">
                <div class="card score-card">
                    <div class="score-circle" style="background: conic-gradient(${pageScoreColor} ${data.score}%, #e2e8f0 0);">
                        <span style="color: ${pageScoreColor}">${data.score}</span>
                    </div>
                    <div class="card-title" style="margin-bottom:0;">On-Page Score</div>
                    <div style="font-size:13px; color:var(--text-muted); margin-top:5px;">Based on technical checks</div>
                </div>
                
                <div class="card score-card">
                    <div class="score-circle" style="background: conic-gradient(${speedScoreColor} ${speedScoreNum}%, #e2e8f0 0);">
                        <span style="color: ${typeof data.google_speed === 'number' ? speedScoreColor : 'var(--text-muted)'}">
                            ${data.google_speed}
                        </span>
                    </div>
                    <div class="card-title" style="margin-bottom:0;">Google Performance</div>
                    <div style="font-size:13px; color:var(--text-muted); margin-top:5px;">Mobile Lighthouse Score</div>
                </div>
            </div>

            <div class="card">
                <div class="card-title">Page Overview</div>
                <div class="metrics-grid">
                    <div class="metric-box">
                        <div>
                            <div class="metric-value">${data.links.internal}</div>
                            <div class="metric-name">Internal Links</div>
                        </div>
                    </div>
                    <div class="metric-box">
                        <div>
                            <div class="metric-value">${data.links.external}</div>
                            <div class="metric-name">External Links</div>
                        </div>
                    </div>
                    <div class="metric-box">
                        <div>
                            <div class="metric-value">${data.images.total}</div>
                            <div class="metric-name">Images (${data.images.missing_alt} missing ALT)</div>
                        </div>
                    </div>
                    <div class="metric-box">
                        <div>
                            <div class="metric-value">${data.content.word_count}</div>
                            <div class="metric-name">Words Processed</div>
                        </div>
                    </div>
                    <div class="metric-box">
                        <div>
                            <div class="metric-value">${data.performance.load_time_seconds}s</div>
                            <div class="metric-name">Server Response</div>
                        </div>
                    </div>
                    <div class="metric-box">
                        <div>
                            <div class="metric-value">${data.performance.status_code}</div>
                            <div class="metric-name">HTTP Status</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-title">Social Media Preview</div>
                <div class="social-preview-container">
                    <div class="social-table">
                        <div><b>og:title</b> <span>${data.og_tags.title || 'Missing'}</span></div>
                        <div><b>og:desc</b> <span>${data.og_tags.description || 'Missing'}</span></div>
                        <div><b>og:image</b> <span style="word-break: break-all;">${data.og_tags.image || 'Missing'}</span></div>
                    </div>
                    <div class="social-card-wrapper">
                        ${data.og_tags.image ? `<img src="${data.og_tags.image}" class="social-img">` : '<div class="social-img" style="display:flex;align-items:center;justify-content:center;color:#94a3b8;">No Image Provided</div>'}
                        <div class="social-text">
                            <h4>${data.og_tags.title || data.content.title}</h4>
                            <p>${data.og_tags.description || data.content.meta_description}</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-title">Header Tags Architecture</div>
                
                <div style="margin-bottom: 20px;">
                    <div style="font-weight: 600; background:#2563eb; color:white; display:inline-block; padding:2px 10px; border-radius:4px; font-size:12px; margin-bottom:10px;">H1 Tags (${data.content.h1_list.length})</div>
                    ${data.content.h1_list.length ? data.content.h1_list.map((h, i) => `<div class="tag-box">${i+1}. ${h}</div>`).join('') : '<div class="tag-box" style="border-color:red;">Missing H1</div>'}
                </div>

                <div>
                    <div style="font-weight: 600; background:#3b82f6; color:white; display:inline-block; padding:2px 10px; border-radius:4px; font-size:12px; margin-bottom:10px;">H2 Tags (${data.content.h2_list.length})</div>
                    ${data.content.h2_list.length ? data.content.h2_list.map((h, i) => `<div class="tag-box">${i+1}. ${h}</div>`).join('') : '<div class="tag-box">No H2 tags found</div>'}
                </div>
            </div>

            <div class="card">
                <div class="card-title">Keyword & Phrase Extraction</div>
                
                <div class="phrase-header">Primary Keywords</div>
                <div>${renderBadges(data.keywords.top_1)}</div>

                <div class="phrase-header">2-Word Combinations</div>
                <div>${renderBadges(data.keywords.top_2)}</div>

                <div class="phrase-header">3-Word Combinations</div>
                <div>${renderBadges(data.keywords.top_3)}</div>

                <div class="phrase-header">4-Word Combinations</div>
                <div>${renderBadges(data.keywords.top_4)}</div>
            </div>

            ${data.issues.length ? `
            <div class="card issues-list">
                <div class="card-title" style="color: #991b1b;">Action Items Found</div>
                <ul style="margin:0; padding-left:20px;">
                    ${data.issues.map(i => `<li>${i}</li>`).join("")}
                </ul>
            </div>
            ` : ''}

          `;
      } catch (err) {
          document.getElementById('out').innerHTML = `<div class="card issues-list" style="text-align:center;">Failed to fetch analysis. Check server logs.</div>`;
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
            # REMEMBER TO PASTE YOUR REAL API KEY HERE!
            google_api = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile&key=AIzaSyAJSIWD5LTnZK_yC4mKeyxw76COHxdESPU"
            google_req = requests.get(google_api, timeout=40)
            if google_req.status_code == 200:
                raw_score = google_req.json()["lighthouseResult"]["categories"]["performance"]["score"]
                google_score = int(raw_score * 100)
            else:
                google_score = "Failed"
        except Exception:
            google_score = "Timeout"

        # Extract Meta & OG tags before stripping scripts
        title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_desc_tag["content"].strip() if meta_desc_tag and meta_desc_tag.get("content") else "No meta description"
        
        og_title = soup.find("meta", property="og:title")
        og_desc = soup.find("meta", property="og:description")
        og_image = soup.find("meta", property="og:image")
        
        og_tags = {
            "title": og_title["content"].strip() if og_title and og_title.get("content") else "",
            "description": og_desc["content"].strip() if og_desc and og_desc.get("content") else "",
            "image": og_image["content"].strip() if og_image and og_image.get("content") else ""
        }

        h1_list = [h.get_text(strip=True) for h in soup.find_all("h1")]
        h2_list = [h.get_text(strip=True) for h in soup.find_all("h2")]

        canonical_tag = soup.find("link", rel="canonical")
        canonical = canonical_tag["href"] if canonical_tag and canonical_tag.get("href") else "Missing"
        robots_tag = soup.find("meta", attrs={"name": "robots"})
        meta_robots = robots_tag["content"] if robots_tag and robots_tag.get("content") else "Index, Follow"

        for s in soup(["script", "style", "noscript"]):
            s.extract()

        raw_text_blocks = soup.get_text(separator="\n")
        
        stopwords = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with", "about", "by", "from", "of", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "shall", "should", "can", "could", "may", "might", "must", "it", "this", "that", "these", "those", "which", "who", "whom", "whose", "what", "how", "why", "where", "when", "we", "you", "they", "he", "she", "your", "our", "their", "my", "his", "her", "its", "not", "no", "all", "any", "some", "more", "most", "other", "such", "only", "own", "same", "so", "than", "too", "very", "one", "two", "also", "if", "then", "as", "out", "up", "down", "into", "over", "after", "us", "home", "faq", "login", "contact", "read"}

        all_words_list = re.findall(r'\b[a-z]{2,}\b', raw_text_blocks.lower())
        total_words = max(len(all_words_list), 1)

        phrase_counts = {1: Counter(), 2: Counter(), 3: Counter(), 4: Counter()}

        regional_entities = {
            "abu dhabi": "abudhabi",
            "saudi arabia": "saudiarabia",
            "new york": "newyork",
            "sri lanka": "srilanka"
        }

        for line in raw_text_blocks.split('\n'):
            clean_line = line.lower()
            
            for region, merged in regional_entities.items():
                clean_line = clean_line.replace(region, merged)
                
            words_in_line = re.findall(r'\b[a-z]{2,}\b', clean_line)
            if not words_in_line: continue
            
            for w in words_in_line:
                if w not in stopwords:
                    phrase_counts[1][w] += 1
                    
            for n in [2, 3, 4]:
                if len(words_in_line) >= n:
                    for i in range(len(words_in_line) - n + 1):
                        ngram = words_in_line[i:i+n]
                        if ngram[0] not in stopwords and ngram[-1] not in stopwords:
                            phrase_counts[n][" ".join(ngram)] += 1

        def format_phrases(counts_dict, n_length, top_k=8):
            result = []
            for phrase, count in counts_dict.most_common(top_k):
                if count > 1:
                    density = round((count * n_length / total_words) * 100, 2)
                    result.append({"phrase": phrase, "count": count, "density": density})
            return result

        top_keywords = {
            "top_1": format_phrases(phrase_counts[1], 1, 12),
            "top_2": format_phrases(phrase_counts[2], 2, 8),
            "top_3": format_phrases(phrase_counts[3], 3, 8),
            "top_4": format_phrases(phrase_counts[4], 4, 8)
        }

        words = [w for w in soup.get_text(separator=" ").split() if len(w) > 2]

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
        if len(h1_list) == 0: issues.append("Missing H1 Tag")
        if canonical == "Missing": issues.append("Missing Canonical Tag")
        if "noindex" in meta_robots.lower(): issues.append("Page is blocked from indexing")
        if len(missing_alt) > 0: issues.append(f"{len(missing_alt)} images missing alt text")

        for kw in top_keywords["top_1"]:
            if kw["density"] > 5.0:  
                issues.append(f"Possible keyword stuffing: '{kw['phrase']}' has a density of {kw['density']}%")

        score = max(0, 100 - (len(issues) * 5))

        return {
            "google_speed": google_score,
            "performance": {"status_code": status_code, "load_time_seconds": load_time},
            "indexing": {"canonical": canonical, "meta_robots": meta_robots},
            "content": {"title": title, "meta_description": meta_desc, "word_count": len(words), "h1_list": h1_list, "h2_list": h2_list},
            "og_tags": og_tags,
            "keywords": top_keywords,
            "images": {"total": len(images), "missing_alt": len(missing_alt)},
            "links": {"internal": len(internal_links), "external": len(external_links)},
            "score": score,
            "issues": issues
        }

    except Exception as e:
        return {"error": str(e)}