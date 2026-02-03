from playwright.sync_api import sync_playwright
import pandas as pd
import re
import time

BASE_URL = "https://www.scalemates.com"
LIST_URL = "https://www.scalemates.com/colors/vallejo-model-color--827"

def scrape_vallejo_model_color():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(LIST_URL)

        print("Pagina geladen, zoeken naar kleur-links...")

        # Alle links naar individuele kleuren
        links = page.query_selector_all("a.al.p8.c.pf")

        color_urls = []
        for link in links:
            href = link.get_attribute("href")
            if href and "/colors/vallejo-model-color--827/" in href:
                full_url = BASE_URL + href
                color_urls.append(full_url)

        print(f"Gevonden kleurpagina's: {len(color_urls)}")

        data = []

        # Bezoek elke kleurpagina
        for url in color_urls:
            print(f"Scrapen: {url}")
            page.goto(url)
            time.sleep(0.5)  # kleine delay voor stabiliteit

            # HEX kleur
            color_div = page.query_selector("div[style*='background']")
            style = color_div.get_attribute("style") if color_div else ""
            hex_match = re.search(r"background:\s*(#[0-9A-Fa-f]{6})", style)
            hex_color = hex_match.group(1) if hex_match else ""

            # Naam
            name_el = page.query_selector("dt.p4.bgl:text('Name:') + dd.p4")
            name = name_el.inner_text().strip() if name_el else ""

            # Code
            code_el = page.query_selector("dt.p4.bgl:text('Color:') + dd.p4")
            code_text = code_el.inner_text() if code_el else ""
            code_match = re.search(r"70\.\d{3}", code_text)
            code = code_match.group(0) if code_match else ""

            if code:
                data.append([code, name, hex_color])

        browser.close()

    df = pd.DataFrame(data, columns=["Number", "Name", "HexColor"])
    df.to_csv("vallejo_model_color_latest.csv", index=False, encoding="utf-8")

    print("Klaar! CSV opgeslagen als vallejo_model_color_latest.csv")

if __name__ == "__main__":
    scrape_vallejo_model_color()