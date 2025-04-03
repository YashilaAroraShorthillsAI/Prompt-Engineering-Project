import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
 
class NSEStockScraper:
    def __init__(self, download_dir):
        self.download_dir = os.path.expanduser(download_dir)
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        self.driver = self._setup_driver()
 
    def _setup_driver(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)
 
    def download_nse_csv(self):
        try:
            self.driver.get("https://www.nseindia.com/market-data/live-equity-market")
            time.sleep(5)
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(3)
 
            try:
                download_button = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.ID, "dnldEquityStock"))
                )
                download_button.click()
                print("Download button clicked, waiting for the file to download...")
            except (NoSuchElementException, TimeoutException):
                print("Error: Download button not found or not clickable.")
                return
 
            time.sleep(10)
            files = [f for f in os.listdir(self.download_dir) if f.endswith(".csv")]
            if files:
                print("CSV file downloaded successfully:", files)
                return os.path.join(self.download_dir, files[0])
            else:
                print("Error: No CSV file found in the download directory.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            self.driver.quit()
            print("Browser closed.")
 
class NSEStockAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
 
    def load_data(self):
        if not os.path.exists(self.file_path):
            print(f"Error: File not found at {self.file_path}")
            return False
 
        self.data = pd.read_csv(self.file_path)
        self.data.columns = self.data.columns.str.strip()
        self.data.rename(columns={"30 D   %CHNG": "30 D %CHNG"}, inplace=True)
        self.data["%CHNG"] = pd.to_numeric(self.data.get("%CHNG"), errors="coerce")
        self.data["LTP"] = pd.to_numeric(self.data.get("LTP"), errors="coerce")
        self.data["52W H"] = pd.to_numeric(self.data.get("52W H"), errors="coerce")
        self.data["52W L"] = pd.to_numeric(self.data.get("52W L"), errors="coerce")
        if "30 D %CHNG" in self.data.columns:
            self.data["30 D %CHNG"] = pd.to_numeric(self.data["30 D %CHNG"], errors="coerce")
        return True
 
    def get_top_gainers(self, n=5):
        if self.data is None:
            print("Data not loaded.")
            return None
        return self.data.sort_values(by="%CHNG", ascending=False).head(n)[["SYMBOL", "%CHNG"]]
 
    def get_top_losers(self, n=5):
        if self.data is None:
            print("Data not loaded.")
            return None
        return self.data.sort_values(by="%CHNG", ascending=True).head(n)[["SYMBOL", "%CHNG"]]
 
    def get_stocks_30_below_high(self, n=5):
        if self.data is None:
            print("Data not loaded.")
            return None
        self.data["Below_30%_High"] = ((self.data["52W H"] - self.data["LTP"]) / self.data["52W H"]) * 100
        filtered_stocks = self.data[self.data["Below_30%_High"] >= 30]
        return filtered_stocks.sort_values(by="Below_30%_High", ascending=False).head(n)[["SYMBOL", "LTP", "52W H", "Below_30%_High"]]
 
    def get_stocks_20_above_low(self, n=5):
        self.data["Above_20%_Low"] = ((self.data["LTP"] - self.data["52W L"]) / self.data["52W L"]) * 100
        return self.data[self.data["Above_20%_Low"] >= 20].head(n)[["SYMBOL", "LTP", "52W L", "Above_20%_Low"]]
 
    def get_highest_returns_30_days(self, n=5):
        if "30 D %CHNG" not in self.data.columns:
            print("Column '30 D %CHNG' not found.")
            return None
        return self.data.sort_values(by="30 D %CHNG", ascending=False).head(n)[["SYMBOL", "30 D %CHNG"]]
 
 
if __name__ == "__main__":
    download_dir = "~/Desktop/Surprise Test"
    scraper = NSEStockScraper(download_dir)
    csv_file_path = scraper.download_nse_csv()
 
    if csv_file_path:
        analyzer = NSEStockAnalyzer(csv_file_path)
        if analyzer.load_data():
            print("\n📈 Top 5 Gainers:")
            print(analyzer.get_top_gainers())
 
            print("\n📉 Top 5 Losers:")
            print(analyzer.get_top_losers())
 
            print("\n📉 Stocks 30% below 52-Week High:")
            print(analyzer.get_stocks_30_below_high())
 
            print("\n📈 20% above 52-Week Low:")
            print(analyzer.get_stocks_20_above_low())
 
            print("\n📈 Highest returns in last 30 days:")
            print(analyzer.get_highest_returns_30_days())