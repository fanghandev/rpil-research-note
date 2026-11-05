"""slides.html -> slides.pdf with the HTML layout: reveal.js print mode (?print-pdf), one 1600 x 900
page per slide, backgrounds kept, after MathJax has typeset. Run from quarto/ (opengate env, Playwright)."""
from pathlib import Path

from playwright.sync_api import sync_playwright

html = Path("slides.html").resolve()
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1600, "height": 900})
    page.goto(html.as_uri() + "?print-pdf", wait_until="networkidle")
    page.wait_for_function("window.MathJax === undefined || (MathJax.startup && MathJax.startup.promise)", timeout=60000)
    page.evaluate("window.MathJax && MathJax.startup ? MathJax.startup.promise : null")
    page.wait_for_selector(".pdf-page", timeout=60000)
    # reveal.js lazy-loads images (data-src): load every one and wait until all are decoded
    page.evaluate("""async () => {
        const imgs = [...document.querySelectorAll('img')];
        for (const im of imgs) { if (im.dataset.src && !im.getAttribute('src')) im.src = im.dataset.src; }
        await Promise.all(imgs.map(im => im.decode().catch(() => null)));
    }""")
    missing = page.evaluate("[...document.querySelectorAll('img')].filter(i => !i.complete || i.naturalWidth === 0).length")
    if missing:
        raise RuntimeError(f"{missing} images did not load")
    page.wait_for_timeout(2000)
    n = page.evaluate("document.querySelectorAll('.pdf-page').length")
    page.pdf(path="slides.pdf", width="1600px", height="900px", print_background=True, prefer_css_page_size=True,
             margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    browser.close()
print(f"slides.pdf: {n} pages")
