"""
Crawler for the IBXX-100 B3 index.

Downloads the CSV from B3, extracts tickers, and returns:
    list[str] of tickers

If *anything* goes wrong, returns DEFAULT_TICKERS.
"""

import os
import asyncio
import pandas as pd
from pathlib import Path
from playwright.async_api import async_playwright


# ---------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------

SCRAPE_B3_IBXX_URL = (
    "https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBXX?language=pt-br"
)

DOCKER_BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
]

# Fallback list (21/11/25)
DEFAULT_TICKERS = [
    'ALOS3','ABEV3','ANIM3','ASAI3','AURE3','AXIA3','AXIA6','AZZA3','B3SA3','BBSE3',
    'BBDC3','BBDC4','BRAP4','BBAS3','BRKM5','BRAV3','BPAC11','CXSE3','CEAB3','CMIG4',
    'COGN3','CSMG3','CPLE3','CPLE5','CSAN3','CPFE3','CMIN3','CURY3','CVCB3','CYRE3',
    'DIRR3','ECOR3','EMBJ3','ENGI11','ENEV3','EGIE3','EQTL3','EZTC3','FLRY3','GGBR4',
    'GOAU4','GGPS3','GMAT3','HAPV3','HYPE3','IGTI11','INTB3','IRBR3','ISAE4','ITSA4',
    'ITUB4','KLBN11','RENT3','LREN3','LWSA3','MGLU3','POMO4','MBRF3','BEEF3','MOTV3',
    'MOVI3','MRVE3','MULT3','NATU3','PCAR3','PETR3','PETR4','RECV3','PRIO3','PETZ3',
    'PSSA3','RADL3','RAIZ4','RAPT4','RDOR3','RAIL3','SBSP3','SAPR11','SANB11','SMTO3',
    'CSNA3','SLCE3','SMFT3','SUZB3','TAEE11','VIVT3','TEND3','TIMS3','TOTS3','UGPA3',
    'USIM5','VALE3','VAMO3','VBBR3','VIVA3','WEGE3','YDUQ3','BOVA11'
][::-1]


# ---------------------------------------------------------
# Download CSV using Playwright
# ---------------------------------------------------------

async def download_b3_index_csv(download_dir: str) -> str | None:
    """
    Launches a browser, downloads the CSV, returns file path.
    """
    file_path = None

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
                headless=True,
                args=DOCKER_BROWSER_ARGS
            )
            context = await browser.new_context(accept_downloads=True)
            page = await context.new_page()
            page.set_default_timeout(30000)

            await page.goto(SCRAPE_B3_IBXX_URL)

            async with page.expect_download() as download_info:
                await page.get_by_role("link", name="Download").click()

            download = await download_info.value

            file_path = os.path.join(download_dir, download.suggested_filename)
            await download.save_as(file_path)

        except Exception:
            return None

        finally:
            if 'browser' in locals() and browser:
                await browser.close()

    return file_path


# ---------------------------------------------------------
# CSV → Ticker list
# ---------------------------------------------------------

def process_csv_to_ticker_list(file_path: str) -> list[str]:
    """
    Parses the CSV and extracts tickers.
    """
    if not file_path or not os.path.exists(file_path):
        return []

    try:
        df = pd.read_csv(
            file_path,
            encoding="latin-1",
            sep=";",
            header=None,
            skiprows=2,
            skipfooter=2,
            engine="python",
        )

        tickers = df[0].astype(str).str.strip().tolist()
        return tickers

    except Exception:
        return []


# ---------------------------------------------------------
# Main return function
# ---------------------------------------------------------

async def load_ibrx100() -> list[str]:
    """
    Executes the workflow and returns the ticker list.
    Always returns DEFAULT_TICKERS on error.
    """
    download_dir = os.getcwd()

    # Step 1 — download CSV
    csv_path = await download_b3_index_csv(download_dir)
    if not csv_path:
        return DEFAULT_TICKERS

    # Step 2 — process CSV
    tickers = process_csv_to_ticker_list(csv_path)

    # Remove downloaded file
    if csv_path and os.path.exists(csv_path):
        os.remove(csv_path)

    # Validate
    if not tickers:
        return DEFAULT_TICKERS
    
    # Always including "BOVA11"
    if "BOVA11" not in tickers:
        tickers.append("BOVA11")

    return tickers


# ---------------------------------------------------------
# CLI for debugging
# ---------------------------------------------------------

if __name__ == "__main__":
    final_list = asyncio.run(load_ibrx100())
    print(f"Tickers ({len(final_list)}):")
    print(final_list)
