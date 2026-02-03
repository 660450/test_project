from playwright.sync_api import sync_playwright
import pandas as pd
import time

URL = "https://acrylicosvallejo.com/en/category/hobby/model-color-en/"

def fetch_vallejo():
    print("Start script...")

    with sync_playwright() as p:
        print("Browser starten...")
        browser = p.chromium.launch(headless=False)  # headless uit → je ziet wat er gebeurt
        page = browser.new_page()

        print("Pagina openen...")
        page.goto(URL, timeout=60000)

        # Wacht even zodat je kunt zien wat er gebeurt
        time.sleep(3)

        # Probeer cookie popup weg te klikken
        try:
            print("Probeer cookie popup te sluiten...")
            page.click("button#onetrust-accept-btn-handler", timeout=3000)
            print("Cookie popup gesloten.")
        except Exception as e:
            print("Geen cookie popup:", e)

        print("Scrollen om producten te laden...")
        for i in range(15):
            page.mouse.wheel(0, 2000)
            time.sleep(0.5)

        print("Zoeken naar producten...")
        try:
            page.wait_for_selector("div.product-item", timeout=10000)
        except Exception as e:
            print("Geen producten gevonden:", e)

        items = page.query_selector_all("div.product-item")
        print(f"Aantal gevonden items: {len(items)}")

        data = []

        for item in items:
            try:
                name = item.query_selector("h3.product-title").inner_text().strip()
                number = item.query_selector("span.sku").inner_text().replace("Ref: ", "").strip()
                color_style = item.query_selector("span.color-sample").get_attribute("style")
                hex_color = "#" + color_style.split("#")[-1].replace(";", "")
                desc_el = item.query_selector("div.product-description")
                description = desc_el.inner_text().strip() if desc_el else ""
                data.append([number, name, hex_color, "", description])
            except Exception as e:
                print("Fout bij item:", e)

        if data:
            df = pd.DataFrame(data, columns=["Number", "Name", "HexColor", "RAL", "Description"])
            df.to_csv("vallejo_model_color_latest.csv", index=False)
            print("CSV opgeslagen.")
        else:
            print("Geen data om op te slaan.")

        print("Browser sluiten...")
        browser.close()

if __name__ == "__main__":
    fetch_vallejo()
