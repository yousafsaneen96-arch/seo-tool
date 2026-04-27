from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
import re
from collections import Counter
import concurrent.futures
import os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>

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
        --purple: #8b5cf6;
        --orange: #f97316;
    }

    body { margin: 0; font-family: 'Poppins', sans-serif; background-color: var(--bg-color); color: var(--text-main); }
    img { max-width: 100%; height: auto; }
    .container { max-width: 1100px; margin: 0 auto 50px auto; padding: 0 20px; }
    
    .top-nav-wrapper { position: sticky; top: 20px; z-index: 100; display: flex; justify-content: center; width: 100%; margin-bottom: 40px; pointer-events: none; }
    .nav-container { pointer-events: auto; display: inline-flex; gap: 5px; padding: 6px; background: linear-gradient(145deg, rgba(255, 255, 255, 0.85), rgba(241, 245, 249, 0.75)); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-radius: 50px; border: 1px solid rgba(255,255,255,1); box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(226, 232, 240, 0.4); }
    .nav-btn { padding: 12px 30px; border-radius: 50px; font-family: 'Poppins', sans-serif; font-size: 15px; font-weight: 600; cursor: pointer; border: none; background: transparent; color: var(--text-muted); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
    .nav-btn:hover { color: var(--text-main); background: rgba(255,255,255,0.6); }
    .nav-btn.active { background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; box-shadow: 0 6px 15px -3px rgba(59, 130, 246, 0.4); text-shadow: 0 1px 2px rgba(0,0,0,0.1); }
    .nav-btn.active.orange-grad { background: linear-gradient(135deg, var(--orange), #fb923c); box-shadow: 0 6px 15px -3px rgba(249, 115, 22, 0.4); }

    .header-section { text-align: center; margin-bottom: 40px; }
    h1 { font-size: 2.5rem; margin-bottom: 5px; background: linear-gradient(135deg, var(--primary), var(--secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; transition: all 0.3s ease; }
    .brand { color: var(--text-muted); font-size: 14px; font-weight: 500; margin-bottom: 30px; }
    .search-box { display: flex; justify-content: center; gap: 15px; margin-bottom: 40px; transition: opacity 0.3s ease; }
    input { padding: 16px 24px; width: 60%; border-radius: 50px; border: 1px solid #e2e8f0; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); font-size: 16px; font-family: 'Poppins', sans-serif; outline: none; transition: all 0.3s ease; }
    input:focus { border-color: var(--primary); box-shadow: 0 10px 25px -3px rgba(59, 130, 246, 0.2); }
    
    button.primary-btn { padding: 16px 32px; background: linear-gradient(135deg, var(--primary), var(--secondary)); background-size: 200% auto; border: none; border-radius: 50px; color: white; font-size: 16px; font-weight: 600; cursor: pointer; box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3); transition: all 0.4s ease; }
    button.primary-btn:hover { background-position: right center; transform: translateY(-2px); }
    button.primary-btn.orange-btn { background: linear-gradient(135deg, var(--orange), #fb923c); box-shadow: 0 10px 15px -3px rgba(249, 115, 22, 0.3); }
    button.pdf-btn { padding: 10px 24px; background: #1e293b; border: none; border-radius: 8px; color: white; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.3s; display: flex; align-items: center; gap: 8px; }
    button.pdf-btn:hover { background: #334155; }
    
    button.xml-btn { padding: 10px 20px; background: var(--orange); border: none; border-radius: 8px; color: white; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.3s; display: flex; align-items: center; gap: 8px; }
    button.xml-btn:hover { background: #ea580c; }
    button.xml-btn-outline { padding: 10px 20px; background: white; border: 2px solid var(--orange); border-radius: 8px; color: var(--orange); font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.3s; }
    button.xml-btn-outline:hover { background: #fff7ed; }

    .card { background: var(--card-bg); border-radius: 20px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.03); transition: transform 0.3s ease, box-shadow 0.3s ease; border: 1px solid #f1f5f9; overflow: hidden; page-break-inside: avoid; break-inside: avoid; }
    .card-title { font-size: 1.25rem; font-weight: 600; margin-bottom: 20px; color: var(--text-main); display: flex; align-items: center; gap: 10px; }

    /* Yoast-Style Sitemap Table */
    .yoast-table-wrapper { background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    .yoast-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }
    .yoast-table th { background: #3b82f6; color: white; padding: 12px 20px; font-weight: 600; }
    .yoast-table td { padding: 12px 20px; border-bottom: 1px solid #e2e8f0; color: #3b82f6; }
    .yoast-table td:last-child { color: #64748b; }
    .yoast-table tr:last-child td { border-bottom: none; }
    .yoast-table tr:hover td { background: #f8fafc; }

    .scores-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 25px; margin-bottom: 25px; }
    .score-card { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; page-break-inside: avoid; break-inside: avoid; }
    .score-circle { width: 100px; height: 100px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: 700; margin-bottom: 15px; position: relative; }
    .score-circle::before { content: ""; position: absolute; inset: 10px; background: white; border-radius: 50%; z-index: 1; }
    .score-circle span { position: relative; z-index: 2; }
    .score-label { font-size: 14px; font-weight: 600; color: var(--text-main); }
    .score-sublabel { font-size: 11px; color: var(--text-muted); margin-top: 4px; }

    .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
    .metric-box { background: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px; display: flex; align-items: center; gap: 15px; }
    .metric-value { font-size: 1.5rem; font-weight: 700; color: var(--text-main); }
    .metric-name { font-size: 0.875rem; color: var(--text-muted); font-weight: 500;}

    details.accordion { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 15px; overflow: hidden; page-break-inside: avoid; break-inside: avoid; }
    details.accordion summary { padding: 15px 20px; font-weight: 600; cursor: pointer; list-style: none; display: flex; justify-content: space-between; align-items: center; background: #f1f5f9; transition: background 0.2s; }
    details.accordion summary:hover { background: #e2e8f0; }
    details.accordion summary::after { content: '+'; font-size: 20px; font-weight: normal; color: var(--text-muted); }
    details[open].accordion summary::after { content: '-'; }
    .accordion-content { padding: 15px 20px; border-top: 1px solid #e2e8f0; max-height: 300px; overflow-y: auto; background: white; font-size: 13px; color: var(--text-muted); word-break: break-all; }
    .url-list-item { padding: 6px 0; border-bottom: 1px solid #f1f5f9; }
    .url-list-item:last-child { border-bottom: none; }

    .content-highlight { color: var(--purple); font-weight: 600; }
    .ai-placeholder { background: #fdf4ff; border: 1px solid #f0abfc; padding: 20px; border-radius: 8px; color: #701a75; font-size: 14px; line-height: 1.6; }
    .ai-placeholder h3 { color: #a21caf; margin-top: 0; display: flex; align-items: center; gap: 8px; font-size: 18px;}
    .intent-box { display: inline-block; padding: 6px 12px; background: #f3e8ff; color: #7e22ce; border-radius: 6px; font-weight: 600; font-size: 14px; border: 1px solid #e879f9; }

    .pdf-header { display: none; text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #e2e8f0; }
    .pdf-header h2 { color: var(--primary); margin: 0; font-size: 28px; }
    .pdf-header p { color: var(--text-muted); margin: 5px 0 0 0; font-size: 14px; }
    
    .serp-preview { background: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; max-width: 650px; font-family: arial, sans-serif; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 20px; word-break: break-word; }
    .serp-url { color: #202124; font-size: 14px; margin-bottom: 4px; }
    .serp-title { color: #1a0dab; font-size: 20px; line-height: 1.3; margin-bottom: 4px; }
    .serp-desc { color: #4d5156; font-size: 14px; line-height: 1.58; }
    .char-check-block { border-top: 1px solid #e2e8f0; padding-top: 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
    .char-status { padding: 15px; border-radius: 8px; font-size: 14px;}
    .char-val { font-size: 20px; font-weight: 700; margin-bottom: 5px;}
    .char-ok { background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; }
    .char-error { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }
    
    .audit-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }
    .audit-item { display: flex; align-items: flex-start; gap: 12px; background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; }
    .audit-icon { font-size: 18px; margin-top: 2px; }
    .audit-details h4 { margin: 0 0 4px 0; font-size: 15px; }
    .audit-details p { margin: 0; font-size: 13px; color: var(--text-muted); line-height: 1.4; }
    
    .issues-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 25px; }
    .issue-panel { background: #fef2f2; border: 1px solid #fecaca; border-left: 4px solid var(--danger); padding: 20px; border-radius: 8px;}
    .issue-panel h3 { margin: 0 0 15px 0; color: #991b1b; font-size: 16px; margin-bottom: 8px;}
    .issue-panel ul { margin: 0; padding-left: 20px; }
    .issue-panel li { color: #991b1b; margin-bottom: 8px; font-size: 14px; }
    
    .badge-container { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
    .keyword-badge { background: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a8a; padding: 6px 14px; border-radius: 50px; font-size: 13px; font-weight: 500; }

    /* Tools Hub Grid */
    .tools-hub-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
    .tool-card { border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; background: white; transition: all 0.3s ease; cursor: pointer; display: flex; flex-direction: column; }
    .tool-card:hover { transform: translateY(-5px); border-color: var(--orange); box-shadow: 0 10px 20px -5px rgba(249, 115, 22, 0.15); }
    .tool-icon { font-size: 32px; margin-bottom: 15px; }
    .tool-card h3 { margin: 0 0 10px 0; color: var(--text-main); font-size: 18px; }
    .tool-card p { margin: 0 0 20px 0; font-size: 13px; color: var(--text-muted); line-height: 1.5; flex-grow: 1; }
    .tool-action { font-weight: 600; font-size: 14px; color: var(--orange); display: flex; align-items: center; gap: 5px; }
    </style>

    <div class="top-nav-wrapper">
        <div class="nav-container">
            <button class="nav-btn active" id="tab-seo" onclick="switchTab('seo')">SEO Audit</button>
            <button class="nav-btn" id="tab-content" onclick="switchTab('content')">Content Checker</button>
            <button class="nav-btn" id="tab-tools" onclick="switchTab('tools')">Tools Hub</button>
        </div>
    </div>

    <div class="container">
      <div class="header-section">
          <h1 id="app-title">SEO Analyzer Pro</h1>
          <div class="brand">Built by Yousaf Saneen</div>
          <div class="search-box" id="search-container">
              <input id='url' placeholder='https://example.com/'>
              <button class="primary-btn" id="analyze-btn" onclick='run()'>Run SEO Audit</button>
          </div>
      </div>
      <div id='out'></div>
    </div>

    <script>
    let currentMode = 'seo';

    function switchTab(mode) {
        currentMode = mode;
        
        document.getElementById('tab-seo').classList.remove('active');
        document.getElementById('tab-content').classList.remove('active');
        document.getElementById('tab-tools').classList.remove('active', 'orange-grad');
        
        let titleEl = document.getElementById('app-title');
        let btnEl = document.getElementById('analyze-btn');
        let searchCont = document.getElementById('search-container');
        
        btnEl.classList.remove('orange-btn');

        if (mode === 'seo') {
            document.getElementById('tab-seo').classList.add('active');
            titleEl.innerHTML = 'SEO Analyzer <span style="color:var(--primary)">Pro</span>';
            btnEl.innerText = 'Run SEO Audit';
            searchCont.style.display = 'flex';
            document.getElementById('out').innerHTML = '';
        } 
        else if (mode === 'content') {
            document.getElementById('tab-content').classList.add('active');
            titleEl.innerHTML = 'Content <span style="color:var(--purple)">Checker</span>';
            btnEl.innerText = 'Analyze Content';
            searchCont.style.display = 'flex';
            document.getElementById('out').innerHTML = '';
        } 
        else if (mode === 'tools') {
            document.getElementById('tab-tools').classList.add('active');
            titleEl.innerHTML = 'SEO Tools <span style="color:var(--orange)">Hub</span>';
            searchCont.style.display = 'none'; 
            renderToolsDirectory();
        }
        else if (mode === 'sitemap') {
            document.getElementById('tab-tools').classList.add('active', 'orange-grad');
            titleEl.innerHTML = 'XML Sitemap <span style="color:var(--orange)">Generator</span>';
            btnEl.innerText = 'Generate Sitemap';
            btnEl.classList.add('orange-btn');
            searchCont.style.display = 'flex';
            document.getElementById('out').innerHTML = '';
        }
    }

    function renderToolsDirectory() {
        document.getElementById('out').innerHTML = `
            <div class="card" style="background: transparent; border: none; box-shadow: none; padding: 0;">
                <div class="tools-hub-grid">
                    <div class="tool-card" onclick="switchTab('sitemap')">
                        <div class="tool-icon">🗺️</div>
                        <h3>XML Sitemap Generator</h3>
                        <p>Deep hybrid crawl tool. Categorizes URLs into Posts, Pages, and Categories to generate a perfectly structured, Yoast-style XML Sitemap Index.</p>
                        <div class="tool-action">Open Tool →</div>
                    </div>
                </div>
            </div>
        `;
    }

    function getScoreColor(score) {
        if(score >= 90) return '#10b981';
        if(score >= 70) return '#f59e0b';
        return '#ef4444';
    }

    function getMetricColor(value, type) {
        if (type === 'lcp') { return value <= 2.5 ? '#10b981' : (value <= 4.0 ? '#f59e0b' : '#ef4444'); }
        if (type === 'cls') { return value <= 0.1 ? '#10b981' : (value <= 0.25 ? '#f59e0b' : '#ef4444'); }
        if (type === 'inp') { return value <= 200 ? '#10b981' : (value <= 500 ? '#f59e0b' : '#ef4444'); }
        return 'var(--text-muted)';
    }

    const renderBadges = (arr) => {
        if (!arr || arr.length === 0) return "<span style='font-size:13px; color:#94a3b8;'>None found</span>";
        return arr.map(k => `<div class="keyword-badge">${k.phrase} <span style="color:#64748b; font-weight:400; margin-left:4px;">(${k.density}%)</span></div>`).join("");
    };

    const renderList = (arr) => {
        if (!arr || arr.length === 0) return "<div style='padding:10px;'>No items found.</div>";
        return arr.map(item => `<div class="url-list-item">${item}</div>`).join("");
    };

    function downloadPDF(url) {
        const element = document.getElementById('report-container');
        const header = document.getElementById('pdf-header');
        header.style.display = 'block';
        
        let cleanUrl = url.replace('https://', '').replace('http://', '').replaceAll('/', '');
        let fileNameStr = "Report_" + currentMode + "_" + cleanUrl + ".pdf";

        const opt = {
            margin: [0.4, 0.4, 0.4, 0.4],
            filename: fileNameStr,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, useCORS: true, windowWidth: 1100 },
            jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
        };
        html2pdf().set(opt).from(element).save().then(() => { header.style.display = 'none'; });
    }

    // NEW: Yoast-style XSLT Stylesheet string
    const xsltContent = `<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9">
  <xsl:template match="/">
    <html>
      <head>
        <title>XML Sitemap</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #333; margin: 40px; }
          h1 { color: #1e293b; margin-bottom: 5px; }
          p { color: #64748b; font-size: 14px; margin-top: 0; }
          table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }
          th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #e2e8f0; }
          th { background-color: #3b82f6; color: white; font-weight: 600; }
          tr:hover { background-color: #f8fafc; }
          a { color: #3b82f6; text-decoration: none; }
          a:hover { text-decoration: underline; }
          td:last-child { color: #64748b; }
        </style>
      </head>
      <body>
        <h1>XML Sitemap</h1>
        <p>Generated by <b>SEO Analyzer Pro</b>, this is an XML Sitemap, meant for consumption by search engines.</p>
        <table>
          <tr><th>URL / Sitemap</th><th>Last Modified</th></tr>
          <xsl:for-each select="sitemap:sitemapindex/sitemap:sitemap | sitemap:urlset/sitemap:url">
            <tr>
              <td><a href="{sitemap:loc}"><xsl:value-of select="sitemap:loc"/></a></td>
              <td><xsl:value-of select="sitemap:lastmod"/></td>
            </tr>
          </xsl:for-each>
        </table>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>`;

    // Creates a single XML file string
    function createXMLString(urls, type = "urlset", baseDomain = "") {
        let dateStr = new Date().toISOString().split('T')[0] + "T12:00:00+00:00";
        let xml = '<?xml version="1.0" encoding="UTF-8"?>\\n';
        xml += '<?xml-stylesheet type="text/xsl" href="main-sitemap.xsl"?>\\n';
        
        if (type === "sitemapindex") {
            xml += '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\\n';
            urls.forEach(u => {
                xml += '  <sitemap>\\n    <loc>' + u + '</loc>\\n    <lastmod>' + dateStr + '</lastmod>\\n  </sitemap>\\n';
            });
            xml += '</sitemapindex>';
        } else {
            xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\\n';
            urls.forEach(u => {
                let priority = (u === baseDomain || u === baseDomain + '/') ? '1.0' : '0.8';
                xml += '  <url>\\n    <loc>' + u + '</loc>\\n    <lastmod>' + dateStr + '</lastmod>\\n    <priority>' + priority + '</priority>\\n  </url>\\n';
            });
            xml += '</urlset>';
        }
        return xml;
    }

    // Downloads a flat sitemap.xml (All URLs in one file)
    function downloadFlatSitemap() {
        let allUrls = [];
        Object.values(window.sitemapData).forEach(arr => { allUrls = allUrls.concat(arr); });
        
        let xml = createXMLString(allUrls, "urlset", window.sitemapDomain);
        const blob = new Blob([xml], { type: 'application/xml' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'sitemap.xml';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    // Downloads a Yoast-style ZIP package
    function downloadStructuredSitemapZip() {
        var zip = new JSZip();
        zip.file("main-sitemap.xsl", xsltContent);
        
        let indexLinks = [];
        let baseObj = new URL(window.sitemapDomain);
        let baseUrl = baseObj.origin;

        Object.keys(window.sitemapData).forEach(key => {
            let urls = window.sitemapData[key];
            if (urls.length > 0) {
                let filename = key + "-sitemap.xml";
                indexLinks.push(baseUrl + "/" + filename);
                zip.file(filename, createXMLString(urls, "urlset", baseUrl));
            }
        });

        // The main index file MUST be named sitemap.xml
        zip.file("sitemap.xml", createXMLString(indexLinks, "sitemapindex"));

        zip.generateAsync({type:"blob"}).then(function(content) {
            const a = document.createElement('a');
            a.href = URL.createObjectURL(content);
            a.download = "sitemap_package.zip";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        });
    }

    async function run(){
      let url = document.getElementById('url').value;
      if(!url) return;
      if(!url.startsWith('http')) url = 'https://' + url;

      let modeText = currentMode === 'seo' ? 'Technical SEO Audit & AI Engine' : 
                     currentMode === 'content' ? 'Deep Content Analysis' : 'Hybrid Sitemap Extraction';

      document.getElementById('out').innerHTML = `
        <div class="card" style="text-align:center; padding: 40px;">
            <div style="font-size: 18px; font-weight: 500; color: var(--text-muted);">
                <span style="display:inline-block; animation: pulse 1.5s infinite;">Running ${modeText}...</span>
            </div>
            ${currentMode === 'sitemap' ? '<div style="font-size:13px; color:#94a3b8; margin-top:10px;">Categorizing CMS databases and actively spidering the site. This may take up to 45 seconds.</div>' : ''}
        </div>
        <style>@keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }</style>
      `;

      try {
          let endpoint = currentMode === 'seo' ? '/analyze' : 
                         currentMode === 'content' ? '/analyze-content' : '/generate-sitemap';
                         
          let res = await fetch(endpoint + '?url=' + encodeURIComponent(url));
          let data = await res.json();

          if (data.error) {
            document.getElementById('out').innerHTML = `<div class="card" style="text-align:center; color:red;">Error: ${data.error}</div>`;
            return;
          }

          if (currentMode === 'seo') {
              renderSEO(data, url);
          } else if (currentMode === 'content') {
              renderContent(data, url);
          } else {
              renderSitemap(data, url);
          }
      } catch (err) {
          document.getElementById('out').innerHTML = `<div class="card" style="text-align:center; color:red;">Failed to fetch analysis. Check server logs.</div>`;
      }
    }

    function renderSitemap(data, url) {
        window.sitemapData = data.sitemaps; 
        window.sitemapDomain = url;
        
        let dateStr = new Date().toISOString().split('T')[0] + " 12:00 +00:00";
        
        let tableRows = Object.keys(data.sitemaps).map(key => {
            if(data.sitemaps[key].length === 0) return '';
            let sitemapUrl = new URL(url).origin + "/" + key + "-sitemap.xml";
            return `<tr><td>${sitemapUrl} <b>(${data.sitemaps[key].length} URLs)</b></td><td>${dateStr}</td></tr>`;
        }).join('');

        document.getElementById('out').innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
                <h2 style="margin: 0; color: var(--text-main); font-size: 1.5rem;">Sitemap Generated</h2>
                <div style="display:flex; gap:10px;">
                    <button class="xml-btn-outline" onclick="downloadFlatSitemap()">Download sitemap.xml (Flat)</button>
                    <button class="xml-btn" onclick="downloadStructuredSitemapZip()">Download Yoast ZIP Package</button>
                </div>
            </div>
            
            <div class="card" style="padding: 0; border: none; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                <div class="yoast-table-wrapper">
                    <div style="padding: 20px; background: white; border-bottom: 1px solid #e2e8f0;">
                        <h2 style="margin: 0 0 10px 0; color: #1e293b; font-size: 24px;">XML Sitemap Index</h2>
                        <p style="margin: 0; color: #64748b; font-size: 14px;">Generated by <b>SEO Analyzer Pro</b>. This XML Sitemap Index file contains <b>${data.count}</b> total URLs divided across categorized sitemaps.</p>
                    </div>
                    <table class="yoast-table">
                        <tr><th>Sitemap Name</th><th>Last Modified</th></tr>
                        ${tableRows}
                    </table>
                </div>
            </div>
        `;
    }

    function renderSEO(data, url) {
        let onPageColor = getScoreColor(data.scores.on_page);
        let techColor = getScoreColor(data.scores.technical);
        let speedScores = { 'mobile': data.performance.mobile.score || 0, 'desktop': data.performance.desktop.score || 0 };

        document.getElementById('out').innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
                <h2 style="margin: 0; color: var(--text-main); font-size: 1.5rem;">Audit Results for ${url}</h2>
                <button class="pdf-btn" onclick="downloadPDF('${url}')">Download PDF Report</button>
            </div>
            
            <div id="report-container" style="background: var(--bg-color); padding: 10px;">
                <div id="pdf-header" class="pdf-header">
                    <h2>SEO Analyzer Pro</h2>
                    <p>Comprehensive Audit Report generated for <b>${url}</b></p>
                </div>

                <div class="scores-grid">
                    <div class="card score-card" style="margin-bottom:0;">
                        <div class="score-circle" style="background: conic-gradient(${onPageColor} ${data.scores.on_page}%, #e2e8f0 0);">
                            <span style="color: ${onPageColor}">${data.scores.on_page}</span>
                        </div>
                        <div class="score-label">On-Page SEO</div>
                        <div class="score-sublabel">Content & Architecture</div>
                    </div>
                    <div class="card score-card" style="margin-bottom:0;">
                        <div class="score-circle" style="background: conic-gradient(${techColor} ${data.scores.technical}%, #e2e8f0 0);">
                            <span style="color: ${techColor}">${data.scores.technical}</span>
                        </div>
                        <div class="score-label">Technical SEO</div>
                        <div class="score-sublabel">Security & Indexing</div>
                    </div>
                    <div class="card score-card" style="margin-bottom:0;">
                        <div class="score-circle" style="background: conic-gradient(${getScoreColor(speedScores.mobile)} ${speedScores.mobile}%, #e2e8f0 0);">
                            <span style="color: ${getScoreColor(speedScores.mobile)}">${speedScores.mobile > 0 ? speedScores.mobile : 'F'}</span>
                        </div>
                        <div class="score-label">Mobile Speed</div>
                        <div class="score-sublabel">Lighthouse Score</div>
                    </div>
                    <div class="card score-card" style="margin-bottom:0;">
                        <div class="score-circle" style="background: conic-gradient(${getScoreColor(speedScores.desktop)} ${speedScores.desktop}%, #e2e8f0 0);">
                            <span style="color: ${getScoreColor(speedScores.desktop)}">${speedScores.desktop > 0 ? speedScores.desktop : 'F'}</span>
                        </div>
                        <div class="score-label">Desktop Speed</div>
                        <div class="score-sublabel">Lighthouse Score</div>
                    </div>
                </div>

                ${data.ai_suggestion ? `
                <div class="ai-placeholder" style="margin-bottom: 25px; background: linear-gradient(to right, #fdf4ff, #faf5ff);">
                    <h3>✨ AI Content Rewriter</h3>
                    <div style="white-space: pre-wrap;">${data.ai_suggestion}</div>
                </div>
                ` : ''}

                ${(data.issues.on_page.length > 0 || data.issues.technical.length > 0) ? `
                <div class="issues-list" style="margin-top: 25px;">
                    ${data.issues.on_page.length > 0 ? `
                    <div class="issue-panel">
                        <h3>⚠️ On-Page Action Items</h3>
                        <ul>${data.issues.on_page.map(i => `<li>${i}</li>`).join("")}</ul>
                    </div>
                    ` : ''}
                    ${data.issues.technical.length > 0 ? `
                    <div class="issue-panel">
                        <h3>⚙️ Technical Action Items</h3>
                        <ul>${data.issues.technical.map(i => `<li>${i}</li>`).join("")}</ul>
                    </div>
                    ` : ''}
                </div>
                ` : '<div class="card" style="background:#ecfdf5; border-color:#a7f3d0; color:#065f46; text-align:center; font-weight:600; margin-top:25px;">🎉 Perfect! No severe SEO issues detected.</div>'}

                <div class="card" style="margin-top: 25px;">
                    <div class="card-title">Core Web Vitals Status</div>
                    <div class="cwv-subgrid">
                        <div>
                            <div style="font-weight: 600; color: var(--text-muted); margin-bottom: 10px;">Mobile</div>
                            <div class="cwv-item"><b>LCP</b> <span>${data.performance.mobile.lcp || 'F'} <span class="cwv-badge" style="background: ${getMetricColor(data.performance.mobile.lcp_v, 'lcp')}"></span></span></div>
                            <div class="cwv-item"><b>CLS</b> <span>${data.performance.mobile.cls || 'F'} <span class="cwv-badge" style="background: ${getMetricColor(data.performance.mobile.cls_v, 'cls')}"></span></span></div>
                            <div class="cwv-item"><b>INP</b> <span>${data.performance.mobile.inp || 'F'} <span class="cwv-badge" style="background: ${getMetricColor(data.performance.mobile.inp_v, 'inp')}"></span></span></div>
                        </div>
                        <div>
                            <div style="font-weight: 600; color: var(--text-muted); margin-bottom: 10px;">Desktop</div>
                            <div class="cwv-item"><b>LCP</b> <span>${data.performance.desktop.lcp || 'F'} <span class="cwv-badge" style="background: ${getMetricColor(data.performance.desktop.lcp_v, 'lcp')}"></span></span></div>
                            <div class="cwv-item"><b>CLS</b> <span>${data.performance.desktop.cls || 'F'} <span class="cwv-badge" style="background: ${getMetricColor(data.performance.desktop.cls_v, 'cls')}"></span></span></div>
                            <div class="cwv-item"><b>INP</b> <span>${data.performance.desktop.inp || 'F'} <span class="cwv-badge" style="background: ${getMetricColor(data.performance.desktop.inp_v, 'inp')}"></span></span></div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">Page Overview ${data.js_rendered ? '<span style="font-size:12px; background:#f59e0b; color:white; padding:4px 8px; border-radius:4px; margin-left:10px;">JS Rendered</span>' : ''}</div>
                    <div class="metrics-grid">
                        <div class="metric-box"><div><div class="metric-value">${data.links.internal_count}</div><div class="metric-name">Internal Links</div></div></div>
                        <div class="metric-box"><div><div class="metric-value">${data.links.external_count}</div><div class="metric-name">External Links</div></div></div>
                        <div class="metric-box"><div><div class="metric-value">${data.images.total}</div><div class="metric-name">Images</div></div></div>
                        <div class="metric-box"><div><div class="metric-value">${data.content.word_count}</div><div class="metric-name">Words Processed</div></div></div>
                        <div class="metric-box"><div><div class="metric-value">${data.server.load_time_seconds}s</div><div class="metric-name">Server Response</div></div></div>
                        <div class="metric-box"><div><div class="metric-value">${data.server.status_code}</div><div class="metric-name">HTTP Status</div></div></div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">Technical & Security Audits</div>
                    <div class="audit-grid">
                        <div class="audit-item">
                            <div class="audit-icon ${data.technical.https ? 'audit-pass' : 'audit-fail'}">${data.technical.https ? '✅' : '❌'}</div>
                            <div class="audit-details"><h4>SSL Checker and HTTPS</h4><p>${data.technical.https ? 'Website is successfully using HTTPS, a secure communication protocol.' : 'Warning: Website is not using HTTPS securely.'}</p></div>
                        </div>
                        <div class="audit-item">
                            <div class="audit-icon ${data.technical.hsts ? 'audit-pass' : 'audit-fail'}">${data.technical.hsts ? '✅' : '❌'}</div>
                            <div class="audit-details"><h4>HSTS Test</h4><p>${data.technical.hsts ? 'Website is using Strict-Transport-Security to force secure connections.' : 'Website is not using the Strict-Transport-Security header.'}</p></div>
                        </div>
                        <div class="audit-item">
                            <div class="audit-icon ${data.technical.html_size_kb <= 100 ? 'audit-pass' : 'audit-fail'}">${data.technical.html_size_kb <= 100 ? '✅' : '❌'}</div>
                            <div class="audit-details"><h4>HTML Page Size Test</h4><p>The size of this HTML document is <b>${data.technical.html_size_kb} Kb</b>.</p></div>
                        </div>
                        <div class="audit-item">
                            <div class="audit-icon ${data.technical.has_schema ? 'audit-pass' : 'audit-fail'}">${data.technical.has_schema ? '✅' : '❌'}</div>
                            <div class="audit-details"><h4>Schema.org Structured Data</h4><p>${data.technical.has_schema ? 'Using JSON-LD or Microdata Schema.' : 'Missing Schema markup.'}</p></div>
                        </div>
                        <div class="audit-item">
                            <div class="audit-icon ${data.technical.has_ga ? 'audit-pass' : 'audit-fail'}">${data.technical.has_ga ? '✅' : '❌'}</div>
                            <div class="audit-details"><h4>Google Analytics Test</h4><p>${data.technical.has_ga ? 'Google tracking scripts detected.' : 'No Google Analytics scripts detected.'}</p></div>
                        </div>
                        <div class="audit-item">
                            <div class="audit-icon ${data.technical.has_favicon ? 'audit-pass' : 'audit-fail'}">${data.technical.has_favicon ? '✅' : '❌'}</div>
                            <div class="audit-details"><h4>Favicon Test</h4><p>${data.technical.has_favicon ? 'Valid favicon found.' : 'No favicon link tag found.'}</p></div>
                        </div>
                        <div class="audit-item">
                            <div class="audit-icon ${data.technical.lang_attr ? 'audit-pass' : 'audit-fail'}">${data.technical.lang_attr ? '✅' : '❌'}</div>
                            <div class="audit-details"><h4>Language Attribute</h4><p>${data.technical.lang_attr ? `Page is using the Lang Attribute (${data.technical.lang_attr}).` : 'Missing HTML lang attribute.'}</p></div>
                        </div>
                        <div class="audit-item">
                            <div class="audit-icon ${data.technical.has_hreflang ? 'audit-pass' : 'audit-fail'}">${data.technical.has_hreflang ? '✅' : '❌'}</div>
                            <div class="audit-details"><h4>Hreflang Usage</h4><p>${data.technical.has_hreflang ? 'Page makes use of Hreflang attributes.' : 'Page is not making use of Hreflang attributes.'}</p></div>
                        </div>
                        <div class="audit-item">
                            <div class="audit-icon ${data.technical.responsive_images_pass ? 'audit-pass' : 'audit-fail'}">${data.technical.responsive_images_pass ? '✅' : '❌'}</div>
                            <div class="audit-details"><h4>Responsive Image Test</h4><p>${data.technical.responsive_images_pass ? 'Images are properly sized.' : 'Warning: Serving images larger than needed.'}</p></div>
                        </div>
                        <div class="audit-item">
                            <div class="audit-icon ${data.technical.canonical_pass ? 'audit-pass' : 'audit-fail'}">${data.technical.canonical_pass ? '✅' : '❌'}</div>
                            <div class="audit-details"><h4>Canonical Tag Test</h4><p>${data.technical.canonical_pass ? 'Website is using the canonical link tag.' : 'Missing canonical link tag.'}</p></div>
                        </div>
                        <div class="audit-item">
                            <div class="audit-icon ${data.technical.noindex_pass ? 'audit-pass' : 'audit-fail'}">${data.technical.noindex_pass ? '✅' : '❌'}</div>
                            <div class="audit-details"><h4>Noindex Tag Test</h4><p>${data.technical.noindex_pass ? 'Page does not use noindex. It can be indexed.' : 'Blocked by noindex tag.'}</p></div>
                        </div>
                        <div class="audit-item">
                            <div class="audit-icon ${data.technical.www_resolve ? 'audit-pass' : 'audit-fail'}">${data.technical.www_resolve ? '✅' : '❌'}</div>
                            <div class="audit-details"><h4>URL Canonicalization</h4><p>${data.technical.www_resolve ? 'WWW and non-WWW correctly resolve.' : 'Warning: WWW/non-WWW do not redirect.'}</p></div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">Google SERP Simulator</div>
                    <div class="serp-preview">
                        <div class="serp-url">${url}</div>
                        <div class="serp-title">${data.content.title}</div>
                        <div class="serp-desc">${data.content.meta_description}</div>
                    </div>
                    <div class="char-check-block">
                        <div>
                            <div class="card-title" style="font-size: 15px; margin-bottom: 5px;">Website Used Meta Title</div>
                            <span class="meta-website-used">${data.content.title}</span>
                            <div class="char-status ${data.content.title_len > 10 && data.content.title_len <= 60 ? 'char-ok' : 'char-error'}">
                                <div class="char-val">${data.content.title_len}</div>Title Characters Used (Optimal: 50-60)
                            </div>
                        </div>
                        <div>
                            <div class="card-title" style="font-size: 15px; margin-bottom: 5px;">Website Used Meta Description</div>
                            <span class="meta-website-used">${data.content.meta_description}</span>
                            <div class="char-status ${data.content.meta_desc_len > 50 && data.content.meta_desc_len <= 160 ? 'char-ok' : 'char-error'}">
                                <div class="char-val">${data.content.meta_desc_len}</div>Description Characters Used (Optimal: 150-160)
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
                            <div><b>og:image</b> <span>${data.og_tags.image || 'Missing'}</span></div>
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
                    <div class="card-title">Core Site Files Status</div>
                    <div>
                        <div class="file-badge ${data.site_files.robots ? 'file-found' : 'file-missing'}">${data.site_files.robots ? '✓' : '✗'} robots.txt</div>
                        <div class="file-badge ${data.site_files.sitemap ? 'file-found' : 'file-missing'}">${data.site_files.sitemap ? '✓' : '✗'} sitemap.xml</div>
                        <div class="file-badge ${data.site_files.llms ? 'file-found' : 'file-missing'}">${data.site_files.llms ? '✓' : '✗'} llms.txt (AI Readiness)</div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">Deep Link & Image Extraction</div>
                    <details class="accordion">
                        <summary>Internal Links (${data.links.internal_count} found)</summary>
                        <div class="accordion-content">${renderList(data.links.internal_urls)}</div>
                    </details>
                    <details class="accordion">
                        <summary>External Links (${data.links.external_count} found)</summary>
                        <div class="accordion-content">${renderList(data.links.external_urls)}</div>
                    </details>
                    ${data.images.missing_alt_count === 0 ? `
                        <div class="file-badge file-found" style="width:100%; border-radius:8px; display:block; text-align:center; box-sizing: border-box;">✓ No missing alt text found</div>
                    ` : `
                        <details class="accordion">
                            <summary>Images Missing Alt Text (${data.images.missing_alt_count} found)</summary>
                            <div class="accordion-content">${renderList(data.images.missing_alt_urls)}</div>
                        </details>
                    `}
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
                    <div class="badge-container">${renderBadges(data.keywords.top_1)}</div>
                    <div class="phrase-header">2-Word Combinations</div>
                    <div class="badge-container">${renderBadges(data.keywords.top_2)}</div>
                    <div class="phrase-header">3-Word Combinations</div>
                    <div class="badge-container">${renderBadges(data.keywords.top_3)}</div>
                    <div class="phrase-header">4-Word Combinations</div>
                    <div class="badge-container">${renderBadges(data.keywords.top_4)}</div>
                </div>
            </div> `;
    }

    function renderContent(data, url) {
        let contentScoreColor = getScoreColor(data.content_score);
        
        document.getElementById('out').innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
                <h2 style="margin: 0; color: var(--text-main); font-size: 1.5rem;">Content Checker Results</h2>
                <button class="pdf-btn" onclick="downloadPDF('${url}')">Download PDF Report</button>
            </div>
            
            <div id="report-container" style="background: var(--bg-color); padding: 10px;">
                <div id="pdf-header" class="pdf-header">
                    <h2 style="color:var(--purple)">Content Checker</h2>
                    <p>Content Audit generated for <b>${url}</b></p>
                </div>

                <div class="scores-grid">
                    <div class="card score-card" style="margin-bottom:0;">
                        <div class="score-circle" style="background: conic-gradient(${contentScoreColor} ${data.content_score}%, #e2e8f0 0);">
                            <span style="color: ${contentScoreColor}">${data.content_score}</span>
                        </div>
                        <div class="score-label">Content Score</div>
                        <div class="score-sublabel">Overall Quality</div>
                    </div>
                    <div class="card score-card" style="margin-bottom:0;">
                        <div style="font-size: 32px; font-weight:700; color:var(--purple); margin-bottom:10px;">${data.word_count}</div>
                        <div class="score-label">Total Words</div>
                    </div>
                    <div class="card score-card" style="margin-bottom:0;">
                        <div style="font-size: 24px; font-weight:700; color:var(--secondary); margin-bottom:10px;">${data.readability.level}</div>
                        <div class="score-label">Readability Level</div>
                        <div class="score-sublabel">Flesch Score: ${data.readability.score}</div>
                    </div>
                    <div class="card score-card" style="margin-bottom:0;">
                        <div class="intent-box">${data.intent.primary_intent}</div>
                        <div class="score-label" style="margin-top:15px;">Search Intent</div>
                    </div>
                </div>

                ${data.ai_suggestion ? `
                <div class="ai-placeholder" style="margin-bottom: 25px; background: linear-gradient(to right, #fdf4ff, #faf5ff);">
                    <h3>✨ AI Content Strategy</h3>
                    <div style="white-space: pre-wrap;">${data.ai_suggestion}</div>
                </div>
                ` : ''}

                <div class="card">
                    <div class="card-title">E-E-A-T & Trust Signals</div>
                    <div class="audit-grid">
                        <div class="audit-item"><div class="audit-icon">${data.eeat.has_author ? '✅' : '⚠️'}</div><div class="audit-details"><h4>Author Entity</h4><p>${data.eeat.has_author ? 'Author tags or classes detected.' : 'No clear author identified.'}</p></div></div>
                        <div class="audit-item"><div class="audit-icon">${data.eeat.has_contact_or_about ? '✅' : '⚠️'}</div><div class="audit-details"><h4>Business Transparency</h4><p>${data.eeat.has_contact_or_about ? 'Contact/About pages linked.' : 'Missing trust pages.'}</p></div></div>
                        <div class="audit-item"><div class="audit-icon">${data.eeat.has_external_links ? '✅' : '⚠️'}</div><div class="audit-details"><h4>External Citations</h4><p>${data.eeat.has_external_links ? 'Page links to external sources.' : 'No outbound links found.'}</p></div></div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">Heading Hierarchy (H1 - H6)</div>
                    <div style="display:flex; flex-direction:column; gap:10px;">
                        ${Object.keys(data.headings).map(tag => {
                            if(data.headings[tag].length === 0) return '';
                            return `
                            <div>
                                <span style="background:var(--primary); color:white; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:bold; margin-right:10px; display:inline-block; width:25px; text-align:center;">${tag.toUpperCase()}</span>
                                <span style="font-size:14px; color:var(--text-muted);">${data.headings[tag].length} tags found</span>
                                <div style="margin-top:5px; padding-left:45px;">
                                    ${data.headings[tag].slice(0, 5).map(h => `<div style="font-size:13px; margin-bottom:3px;">• ${h}</div>`).join('')}
                                    ${data.headings[tag].length > 5 ? `<div style="font-size:12px; color:var(--primary); font-style:italic;">+ ${data.headings[tag].length - 5} more...</div>` : ''}
                                </div>
                            </div>
                            `;
                        }).join('')}
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">NLP & Keyword Density Analysis</div>
                    <div class="phrase-header">Primary Content Keywords</div>
                    <div class="badge-container">${renderBadges(data.keywords.top_1)}</div>
                    <div class="phrase-header">LSI / Contextual Phrases (2-3 Words)</div>
                    <div class="badge-container">${renderBadges(data.keywords.top_2)}</div>
                    <div class="badge-container">${renderBadges(data.keywords.top_3)}</div>
                </div>

                <div class="card">
                    <div class="card-title">Intent Optimization Tips</div>
                    <div style="background: #f8fafc; padding: 15px; border-radius: 8px; font-size: 14px; border-left: 4px solid var(--purple);">
                        Based on the primary intent (<b>${data.intent.primary_intent}</b>), ensure this page includes:
                        <ul style="margin-top: 10px; margin-bottom: 0;">
                            ${data.intent.tips.map(tip => `<li>${tip}</li>`).join('')}
                        </ul>
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">AI & Plagiarism Checks</div>
                    <div class="audit-grid">
                        <div class="audit-item">
                            <div class="audit-icon">🔍</div>
                            <div class="audit-details">
                                <h4>Heuristic Duplicate Content</h4>
                                <p>Structural repetition score: <b>${data.ai_plagiarism.heuristic_repetition_score}%</b>. (Scores over 20% suggest heavy boilerplate).</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    </script>
    """

def get_base_soup(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
    soup = BeautifulSoup(r.text, "html.parser")
    for s in soup(["script", "style", "noscript", "svg"]):
        s.extract()
    
    text = soup.get_text(separator="\n")
    words = [w for w in text.split() if len(w) > 2]
    
    js_rendered = False
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
            for s in soup(["script", "style", "noscript", "svg"]):
                s.extract()
            js_rendered = True
        except Exception:
            pass
    return r, soup, js_rendered

def get_openai_suggestion(prompt, api_key):
    if not api_key or api_key == "YOUR_OPENAI_API_KEY_HERE": return None
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "system", "content": "You are a professional SEO copywriter and analyst."},
                         {"role": "user", "content": prompt}],
            "max_tokens": 250
        }
        res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=15)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"AI Generation Failed: {str(e)}"
    return None

@app.get("/generate-sitemap")
def generate_sitemap(url: str):
    try:
        if not url.startswith("http"):
            url = "https://" + url
            
        parsed_base = urlparse(url)
        base_domain = parsed_base.netloc
        base_url = f"{parsed_base.scheme}://{base_domain}"
        
        visited = set()
        to_visit = set([url])
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        
        # --- ENTERPRISE SITEMAP SEEDING ---
        sitemap_endpoints = ['/sitemap.xml', '/sitemap_index.xml', '/post-sitemap.xml', '/page-sitemap.xml']
        for endpoint in sitemap_endpoints:
            try:
                s_res = requests.get(base_url + endpoint, headers=headers, timeout=5)
                if s_res.status_code == 200 and 'xml' in s_res.headers.get('Content-Type', '').lower():
                    s_soup = BeautifulSoup(s_res.text, "html.parser")
                    locs = s_soup.find_all("loc")
                    for loc in locs:
                        loc_text = loc.get_text(strip=True).split('#')[0]
                        if base_domain in loc_text:
                            visited.add(loc_text)
                            to_visit.add(loc_text)
            except:
                pass

        max_pages = 500 
        timeout = 45 
        start_time = time.time()
        
        ignore_exts = ('.jpg', '.jpeg', '.png', '.gif', '.pdf', '.css', '.js', '.svg', '.zip', '.mp4', '.webp', '.xml')
        
        def normalize_url(u):
            u = u.split('#')[0].split('?')[0]
            if u.endswith('/') and len(u) > len(base_url) + 1:
                u = u[:-1]
            return u

        to_visit = {normalize_url(u) for u in to_visit}
        visited = {normalize_url(u) for u in visited}
        
        while to_visit and len(visited) < max_pages and (time.time() - start_time) < timeout:
            current_url = to_visit.pop()
            
            try:
                res = requests.get(current_url, headers=headers, timeout=5)
                if res.status_code != 200 or 'text/html' not in res.headers.get('Content-Type', ''):
                    continue
                    
                soup = BeautifulSoup(res.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a['href']
                    full_url = urljoin(current_url, href)
                    norm_url = normalize_url(full_url)
                    
                    if not norm_url.startswith("http"): continue
                    parsed_full = urlparse(norm_url)
                    
                    if parsed_full.netloc == base_domain and not norm_url.lower().endswith(ignore_exts):
                        if norm_url not in visited:
                            visited.add(norm_url)
                            to_visit.add(norm_url)
            except:
                continue
                
        final_urls = sorted(list(visited))
        
        # --- URL CATEGORIZATION LOGIC ---
        categorized = {"page": [], "post": [], "category": [], "other": []}
        for u in final_urls:
            path = urlparse(u).path
            parts = [p for p in path.split('/') if p.strip()]
            
            if not parts:
                categorized["page"].append(u)
            elif any(x in parts for x in ['category', 'tag', 'author']):
                categorized["category"].append(u)
            elif len(parts) >= 2 or any(re.match(r'\d{4}', p) for p in parts):
                categorized["post"].append(u)
            else:
                categorized["page"].append(u)
                
        return {"sitemaps": categorized, "count": len(final_urls)}
    except Exception as e:
        return {"error": str(e)}

@app.get("/analyze")
def analyze(url: str):
    try:
        r, soup, js_rendered = get_base_soup(url)
        headers = {"User-Agent": "Mozilla/5.0"}
        status_code = r.status_code
        final_url = r.url 
        
        start_time = time.time()
        load_time = round(time.time() - start_time, 2)

        google_api_key = os.getenv("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY_HERE")
        openai_api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")

        html_size_kb = round(len(r.content) / 1024, 2)
        is_https = final_url.startswith("https")
        has_hsts = "strict-transport-security" in (k.lower() for k in r.headers.keys())
        
        parsed_url = urlparse(final_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        www_resolve = False
        domain = parsed_url.netloc
        alt_domain = domain[4:] if domain.startswith("www.") else "www." + domain
        alt_url = f"{parsed_url.scheme}://{alt_domain}"
        try:
            alt_res = requests.head(alt_url, headers=headers, timeout=5, allow_redirects=False)
            www_resolve = alt_res.status_code in [301, 302, 307, 308]
        except:
            www_resolve = False

        def check_file(filename):
            try:
                res = requests.head(f"{base_url}/{filename}", headers=headers, timeout=5)
                if res.status_code == 405 or res.status_code == 403:
                    res = requests.get(f"{base_url}/{filename}", headers=headers, timeout=5, stream=True)
                return res.status_code < 400
            except:
                return False

        has_robots = check_file("robots.txt")
        has_sitemap = check_file("sitemap.xml")
        has_llms = check_file("llms.txt")

        has_favicon = False
        for link in soup.find_all("link"):
            rel_attr = link.get("rel", [])
            if isinstance(rel_attr, list):
                if any("icon" in r.lower() for r in rel_attr):
                    has_favicon = True
                    break
            elif isinstance(rel_attr, str) and "icon" in rel_attr.lower():
                has_favicon = True
                break
                
        if not has_favicon:
            has_favicon = check_file("favicon.ico")

        scripts = soup.find_all("script")
        has_ga = any("google-analytics.com" in str(s) or "googletagmanager.com" in str(s) for s in scripts)
        has_schema = bool(soup.find("script", type="application/ld+json") or soup.find(attrs={"itemtype": True}))
        has_hreflang = bool(soup.find("link", hreflang=True))
        
        html_tag = soup.find("html")
        lang_attr = html_tag.get("lang") if html_tag else None

        canonical_tag = soup.find("link", rel="canonical")
        canonical = canonical_tag["href"] if canonical_tag and canonical_tag.get("href") else "Missing"
        canonical_pass = canonical != "Missing"

        robots_tag = soup.find("meta", attrs={"name": "robots"})
        meta_robots = robots_tag["content"] if robots_tag and robots_tag.get("content") else "Index, Follow"
        noindex_pass = "noindex" not in meta_robots.lower()

        def get_psi_data(target_url, strategy, key):
            try:
                api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={target_url}&strategy={strategy}&key={key}"
                api_req = requests.get(api_url, timeout=40)
                if api_req.status_code == 200:
                    data = api_req.json()
                    raw_score = data["lighthouseResult"]["categories"]["performance"]["score"]
                    score = int(raw_score * 100)
                    
                    audits = data["lighthouseResult"]["audits"]
                    lcp_v = float(audits["largest-contentful-paint"]["numericValue"]) / 1000 
                    cls_v = float(audits["cumulative-layout-shift"]["numericValue"])
                    tbt_v = float(audits["total-blocking-time"]["numericValue"])
                    
                    responsive_images_score = audits.get("uses-responsive-images", {}).get("score", 0)
                    responsive_pass = responsive_images_score >= 0.9

                    return {
                        "score": score,
                        "lcp": audits["largest-contentful-paint"]["displayValue"],
                        "lcp_v": lcp_v,
                        "cls": audits["cumulative-layout-shift"]["displayValue"],
                        "cls_v": cls_v,
                        "inp": audits["total-blocking-time"]["displayValue"], 
                        "inp_v": tbt_v,
                        "responsive_pass": responsive_pass
                    }
                else:
                    return {"score": "Failed", "lcp": "Failed", "cls": "Failed", "inp": "Failed", "responsive_pass": False}
            except Exception:
                return {"score": "Timeout", "lcp": "Timeout", "cls": "Timeout", "inp": "Timeout", "responsive_pass": False}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            mobile_future = executor.submit(get_psi_data, url, "mobile", google_api_key)
            desktop_future = executor.submit(get_psi_data, url, "desktop", google_api_key)
            mobile_psi = mobile_future.result()
            desktop_psi = desktop_future.result()
        
        responsive_images_pass = mobile_psi.get("responsive_pass", False)

        title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
        title_len = len(title) if title != "No title" else 0
        
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_desc_tag["content"].strip() if meta_desc_tag and meta_desc_tag.get("content") else "No meta description"
        meta_desc_len = len(meta_desc) if meta_desc != "No meta description" else 0

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

        raw_text_blocks = soup.get_text(separator="\n")
        
        regional_entities = {
            "abu dhabi": "abudhabi",
            "saudi arabia": "saudiarabia",
            "new york": "newyork",
            "sri lanka": "srilanka"
        }
        
        clean_text_lower = raw_text_blocks.lower()
        for region, merged in regional_entities.items():
            clean_text_lower = clean_text_lower.replace(region, merged)

        raw_words = re.findall(r'\b[a-z0-9]{2,}\b', clean_text_lower)
        total_words = len(raw_words)

        stopwords = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with", "about", "by", "from", "of", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "shall", "should", "can", "could", "may", "might", "must", "it", "this", "that", "these", "those", "which", "who", "whom", "whose", "what", "how", "why", "where", "when", "we", "you", "they", "he", "she", "your", "our", "their", "my", "his", "her", "its", "not", "no", "all", "any", "some", "more", "most", "other", "such", "only", "own", "same", "so", "than", "too", "very", "one", "two", "also", "if", "then", "as", "out", "up", "down", "into", "over", "after", "us", "home", "faq", "login", "contact", "read"}

        phrase_counts = {1: Counter(), 2: Counter(), 3: Counter(), 4: Counter()}

        for line in clean_text_lower.split('\n'):
            words_in_line = re.findall(r'\b[a-z0-9]{2,}\b', line)
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

        on_page_issues = []
        on_page_score = 100
        
        needs_rewrite = False
        if title == "No title":
            on_page_issues.append("Missing Title Tag (-15)")
            on_page_score -= 15
            needs_rewrite = True
        elif title_len < 30 or title_len > 60:
            on_page_issues.append(f"Title length is {title_len} chars (Optimal is 50-60) (-5)")
            on_page_score -= 5
            needs_rewrite = True
            
        if meta_desc == "No meta description":
            on_page_issues.append("Missing Meta Description (-15)")
            on_page_score -= 15
            needs_rewrite = True
        elif meta_desc_len < 120 or meta_desc_len > 160:
            on_page_issues.append(f"Meta Description length is {meta_desc_len} chars (Optimal is 150-160) (-5)")
            on_page_score -= 5
            needs_rewrite = True

        if len(h1_list) == 0:
            on_page_issues.append("Missing H1 Tag (-10)")
            on_page_score -= 10
        elif len(h1_list) > 1:
            on_page_issues.append("Multiple H1 Tags detected (-5)")
            on_page_score -= 5
            
        if len(h2_list) == 0:
            on_page_issues.append("Missing H2 Tags (-5)")
            on_page_score -= 5

        if len(missing_alt) > 0:
            penalty = min(len(missing_alt) * 2, 15)
            on_page_issues.append(f"{len(missing_alt)} images missing alt text (-{penalty})")
            on_page_score -= penalty

        for kw in top_keywords["top_1"]:
            if kw["density"] > 4.0:  
                on_page_issues.append(f"Keyword stuffing: '{kw['phrase']}' is heavily overused at {kw['density']}% (-10)")
                on_page_score -= 10

        technical_issues = []
        technical_score = 100
        
        if not is_https:
            technical_issues.append("Website is not using HTTPS (-20)")
            technical_score -= 20
        if not has_hsts:
            technical_issues.append("Missing HSTS Security Header (-5)")
            technical_score -= 5
        if not canonical_pass:
            technical_issues.append("Missing Canonical Tag (-10)")
            technical_score -= 10
        if not www_resolve:
            technical_issues.append("WWW and non-WWW versions do not resolve correctly (-10)")
            technical_score -= 10
        if not noindex_pass:
            technical_issues.append("FATAL: Page is blocked by a noindex tag (-20)")
            technical_score -= 20
        if not has_robots:
            technical_issues.append("Missing robots.txt (-5)")
            technical_score -= 5
        if not has_sitemap:
            technical_issues.append("Missing sitemap.xml (-5)")
            technical_score -= 5
        if not has_schema:
            technical_issues.append("Missing Schema.org Structured Data (-10)")
            technical_score -= 10
        if html_size_kb > 100:
            technical_issues.append(f"HTML size is very large ({html_size_kb} Kb) (-5)")
            technical_score -= 5

        if isinstance(mobile_psi.get("lcp_v"), float) and mobile_psi["lcp_v"] > 2.5:
            technical_issues.append(f"Mobile LCP is too slow ({mobile_psi['lcp_v']}s) (-10)")
            technical_score -= 10
        if isinstance(mobile_psi.get("cls_v"), float) and mobile_psi["cls_v"] > 0.1:
            technical_issues.append(f"Mobile CLS is too high ({mobile_psi['cls_v']}) (-10)")
            technical_score -= 10
        if isinstance(mobile_psi.get("inp_v"), float) and mobile_psi["inp_v"] > 200:
            technical_issues.append(f"Mobile INP is too slow ({mobile_psi['inp_v']}ms) (-10)")
            technical_score -= 10

        on_page_score = max(0, on_page_score)
        technical_score = max(0, technical_score)

        ai_suggestion = None
        if needs_rewrite and openai_api_key != "YOUR_OPENAI_API_KEY_HERE":
            kw_list = [k['phrase'] for k in top_keywords['top_1'][:5]]
            prompt = f"The website {url} has a bad meta title and description. Write exactly 1 perfect Meta Title (under 60 characters) and 1 compelling Meta Description (under 160 characters). Use these top keywords naturally: {kw_list}. Format clearly with bold headings."
            ai_suggestion = get_openai_suggestion(prompt, openai_api_key)

        return {
            "js_rendered": js_rendered,
            "performance": {
                "mobile": mobile_psi,
                "desktop": desktop_psi
            },
            "server": {"status_code": status_code, "load_time_seconds": load_time},
            "technical": {
                "https": is_https,
                "hsts": has_hsts,
                "html_size_kb": html_size_kb,
                "has_schema": has_schema,
                "has_ga": has_ga,
                "has_favicon": has_favicon,
                "lang_attr": lang_attr,
                "has_hreflang": has_hreflang,
                "responsive_images_pass": responsive_images_pass,
                "canonical_pass": canonical_pass,
                "noindex_pass": noindex_pass,
                "www_resolve": www_resolve
            },
            "site_files": {"robots": has_robots, "sitemap": has_sitemap, "llms": has_llms},
            "indexing": {"canonical": canonical, "meta_robots": meta_robots},
            "content": {
                "title": title, "title_len": title_len,
                "meta_description": meta_desc, "meta_desc_len": meta_desc_len,
                "word_count": total_words, "h1_list": h1_list, "h2_list": h2_list
            },
            "og_tags": og_tags,
            "keywords": top_keywords,
            "images": {"total": len(images), "missing_alt_count": len(missing_alt), "missing_alt_urls": missing_alt[:50]},
            "links": {
                "internal_count": len(internal_links), "internal_urls": list(internal_links)[:100], 
                "external_count": len(external_links), "external_urls": list(external_links)[:100]
            },
            "scores": {"on_page": on_page_score, "technical": technical_score},
            "issues": {"on_page": on_page_issues, "technical": technical_issues},
            "ai_suggestion": ai_suggestion
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/analyze-content")
def analyze_content(url: str):
    try:
        r, soup, js_rendered = get_base_soup(url)
        
        openai_api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")

        text_clean = soup.get_text(separator="\n")
        
        regional_entities = {
            "abu dhabi": "abudhabi",
            "saudi arabia": "saudiarabia",
            "new york": "newyork",
            "sri lanka": "srilanka"
        }
        
        clean_text_lower = text_clean.lower()
        for region, merged in regional_entities.items():
            clean_text_lower = clean_text_lower.replace(region, merged)

        raw_words = re.findall(r'\b[a-z0-9]{2,}\b', clean_text_lower)
        total_words = len(raw_words)
        
        if total_words == 0:
            return {"error": "No readable content found on the page."}

        headings = {
            "h1": [h.get_text(strip=True) for h in soup.find_all("h1")],
            "h2": [h.get_text(strip=True) for h in soup.find_all("h2")],
            "h3": [h.get_text(strip=True) for h in soup.find_all("h3")],
            "h4": [h.get_text(strip=True) for h in soup.find_all("h4")],
            "h5": [h.get_text(strip=True) for h in soup.find_all("h5")],
            "h6": [h.get_text(strip=True) for h in soup.find_all("h6")]
        }

        sentences = max(1, len(re.split(r'[.!?]+', text_clean)))
        def count_syllables(word):
            count = 0
            vowels = "aeiouy"
            if len(word) > 0 and word[0] in vowels: count += 1
            for index in range(1, len(word)):
                if word[index] in vowels and word[index - 1] not in vowels: count += 1
            if word.endswith("e"): count -= 1
            if count <= 0: count = 1
            return count
        
        total_syllables = sum(count_syllables(w) for w in raw_words)
        flesch_score = round(206.835 - 1.015 * (total_words / sentences) - 84.6 * (total_syllables / max(total_words, 1)), 1)
        
        read_level = "Easy (6th Grade)"
        if flesch_score < 30: read_level = "Very Hard (College Grad)"
        elif flesch_score < 50: read_level = "Hard (College)"
        elif flesch_score < 60: read_level = "Fairly Hard (10th-12th Grade)"
        elif flesch_score < 70: read_level = "Standard (8th-9th Grade)"

        info_kws = {"how", "what", "guide", "learn", "tutorial", "tips", "best"}
        trans_kws = {"buy", "price", "order", "store", "cart", "checkout", "services"}
        
        info_count = sum(1 for w in raw_words if w in info_kws)
        trans_count = sum(1 for w in raw_words if w in trans_kws)
        
        primary_intent = "Informational"
        tips = ["Use clear H2 questions (e.g., 'What is...')", "Include bulleted lists for quick answers", "Add a table of contents"]
        
        if trans_count > info_count:
            primary_intent = "Transactional"
            tips = ["Ensure strong Call-to-Action (CTA) buttons", "Include clear pricing or service breakdowns", "Highlight trust badges & reviews"]

        has_author = bool(soup.find(attrs={"rel": "author"}) or soup.find(class_=re.compile(r'author|byline', re.I)))
        links = [a.get("href", "") for a in soup.find_all("a", href=True)]
        has_contact_or_about = any("contact" in l.lower() or "about" in l.lower() for l in links)
        has_external = any(l.startswith("http") and urlparse(url).netloc not in l for l in links)

        stopwords = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with", "about", "by", "from", "of", "is", "are", "was", "were", "this", "that", "it", "not", "be", "your", "our", "you", "they", "he", "she", "his", "her", "its"}
        meaningful = [w for w in raw_words if w not in stopwords]
        
        def get_phrases(words, n, top_k):
            if len(words) < n: return []
            phrases = []
            for i in range(len(words) - n + 1):
                ngram = words[i:i+n]
                if ngram[0] not in stopwords and ngram[-1] not in stopwords:
                    phrases.append(" ".join(ngram))
            counts = Counter(phrases)
            return [{"phrase": p, "count": c, "density": round((c * n / total_words) * 100, 2)} for p, c in counts.most_common(top_k) if c > 1]

        top_1 = [{"phrase": w, "count": c, "density": round((c / total_words) * 100, 2)} for w, c in Counter(meaningful).most_common(12) if c > 1]
        top_2 = get_phrases(meaningful, 2, 8)
        top_3 = get_phrases(meaningful, 3, 8)

        c_score = 100
        if total_words < 300: c_score -= 20
        elif total_words < 600: c_score -= 10
        if not has_author: c_score -= 5
        if not has_contact_or_about: c_score -= 5
        if len(headings["h1"]) != 1: c_score -= 10
        if flesch_score < 30: c_score -= 10 
        c_score = max(0, c_score)

        tri_grams = [" ".join(raw_words[i:i+3]) for i in range(len(raw_words)-2)]
        tri_counts = Counter(tri_grams)
        repetition_score = round((sum(c for p, c in tri_counts.items() if c > 3) / max(len(tri_grams), 1)) * 100, 1)

        ai_suggestion = None
        if openai_api_key != "YOUR_OPENAI_API_KEY_HERE":
            kw_list = [k['phrase'] for k in top_1[:5]]
            prompt = f"The website {url} has a content score of {c_score}/100 and primary intent '{primary_intent}'. Write a 3-bullet-point high-level content strategy to improve this page, using these top keywords: {kw_list}."
            ai_suggestion = get_openai_suggestion(prompt, openai_api_key)

        return {
            "content_score": c_score,
            "word_count": total_words,
            "readability": {"score": flesch_score, "level": read_level},
            "headings": headings,
            "intent": {"primary_intent": primary_intent, "tips": tips},
            "eeat": {"has_author": has_author, "has_contact_or_about": has_contact_or_about, "has_external_links": has_external},
            "keywords": {"top_1": top_1, "top_2": top_2, "top_3": top_3},
            "ai_plagiarism": {"heuristic_repetition_score": repetition_score},
            "ai_suggestion": ai_suggestion
        }
    except Exception as e:
        return {"error": str(e)}