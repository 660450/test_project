from playwright.sync_api import sync_playwright
# import pandas as pd
import re
import time
import pandas as pd

BASE_URL = "https://www.scalemates.com"
LIST_URL = "https://www.scalemates.com/colors/vallejo-model-color--827"

def scrape_vallejo_model_color():
    """
    Scrape Vallejo Model Color paint information from a website and save to CSV.
    
    This function uses Playwright to automate browser interaction and web scraping.
    It performs the following steps:
    
    1. Launches a Chromium browser and navigates to the color list page
    2. Finds all color-specific links matching the Vallejo Model Color pattern
    3. Iterates through each color page and extracts:
       - HEX color code from the background style attribute
       - Paint name from the page metadata
       - Product code (70.XXX format) from the color information
    4. Compiles the extracted data into a pandas DataFrame
    5. Exports the data to a CSV file
    
    Returns:
        None
        
    Side Effects:
        - Creates/overwrites "vallejo_model_color_latest.csv" in the current directory
        - Prints progress messages to console (page load status, found colors count, 
          current URL being scraped, and completion message)
        - Launches a visible browser window during execution (headless=False)
    
    Note:
        - Includes a 0.5 second delay between page visits for stability
        - Only adds rows to the output where a product code is found
        - Requires: playwright, pandas, re, and time modules
    """
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