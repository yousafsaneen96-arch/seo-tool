from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time

app = FastAPI()

# ... [Keep your existing HTML frontend code here, but you will want to add more UI cards for the new data] ...

@app.get("/analyze")
def analyze(url: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
        
        # Track response time for basic performance metric
        start_time = time.time()
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        load_time = round(time.time() - start_time, 2)
        
        status_code = r.status_code
        final_url = r.url # Check for redirects
        
        soup = BeautifulSoup(r.text, "html.parser")

        # Extract structured data before stripping scripts
        schema_markup = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                schema_markup.append(json.loads(script.string))
            except:
                pass

        # Strip scripts and styles for text analysis
        for s in soup(["script", "style", "noscript"]):
            s.extract()

        text = soup.get_text(separator=" ")
        words = [w for w in text.split() if len(w) > 2]
        
        # Playwright fallback logic (Keep your existing Step 2 here if word count is low)
        # ... [Your Playwright Code] ...

        # --- ADVANCED SEO METRICS ---
        
        # 1. Technical Tags
        title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_desc_tag["content"].strip() if meta_desc_tag and meta_desc_tag.get("content") else "No meta description"
        
        canonical_tag = soup.find("link", rel="canonical")
        canonical = canonical_tag["href"] if canonical_tag and canonical_tag.get("href") else "Missing"
        
        robots_tag = soup.find("meta", attrs={"name": "robots"})
        meta_robots = robots_tag["content"] if robots_tag and robots_tag.get("content") else "Index, Follow (Default)"

        viewport_tag = soup.find("meta", attrs={"name": "viewport"})
        has_viewport = bool(viewport_tag)

        # 2. Heading Hierarchy
        h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1")]
        h2_tags = [h.get_text(strip=True) for h in soup.find_all("h2")]
        h3_tags = [h.get_text(strip=True) for h in soup.find_all("h3")]

        # 3. Open Graph / Social Tags
        og_title = soup.find("meta", property="og:title")
        og_image = soup.find("meta", property="og:image")
        has_open_graph = bool(og_title and og_image)

        # 4. Images & Alt Text
        images = soup.find_all("img")
        missing_alt = [urljoin(url, img.get("src")) for img in images if img.get("src") and not img.get("src").startswith("data:") and not img.get("alt")]

        # 5. Links
        links = soup.find_all("a", href=True)
        internal_links = set()
        external_links = set()
        for l in links:
            href = l.get("href")
            if href.startswith("/") or url in href:
                internal_links.add(urljoin(url, href))
            elif href.startswith("http"):
                external_links.add(href)

        # --- ADVANCED ISSUE DETECTION ---
        issues = []
        if status_code >= 400: issues.append(f"Page returned HTTP {status_code}")
        if url != final_url: issues.append(f"Page redirects to {final_url}")
        if len(h1_tags) == 0: issues.append("Missing H1 Tag")
        if len(h1_tags) > 1: issues.append("Multiple H1 Tags found (Best practice is 1)")
        if canonical == "Missing": issues.append("Missing Canonical Tag")
        if not has_viewport: issues.append("Missing Mobile Viewport Tag")
        if "noindex" in meta_robots.lower(): issues.append("Page is blocked from indexing (noindex)")
        if len(title) < 30 or len(title) > 60: issues.append("Title length is not optimal (Aim for 30-60 chars)")
        if load_time > 3.0: issues.append(f"Slow load time ({load_time}s)")
        if len(missing_alt) > 0: issues.append(f"{len(missing_alt)} images missing alt text")

        # Dynamic Scoring
        score = max(0, 100 - (len(issues) * 5))

        return {
            "performance": {"status_code": status_code, "load_time_seconds": load_time},
            "indexing": {"canonical": canonical, "meta_robots": meta_robots},
            "content": {
                "title": title,
                "meta_description": meta_desc,
                "word_count": len(words),
                "h1_count": len(h1_tags),
                "h2_count": len(h2_tags),
            },
            "social": {"has_open_graph": has_open_graph},
            "schema_detected": len(schema_markup) > 0,
            "images": {"total": len(images), "missing_alt": len(missing_alt)},
            "links": {"internal": len(internal_links), "external": len(external_links)},
            "score": score,
            "issues": issues
        }

    except Exception as e:
        return {"error": str(e)}