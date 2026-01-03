import os
import csv
import time
import json
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class JobScraper:
    def __init__(self):
        self.url = "https://www.elempleo.com/co/ofertas-empleo"
        self.data_dir = "datos"
        os.makedirs(self.data_dir, exist_ok=True)
        
    def setup_driver(self):
        """Setup headless Chrome for GitHub Actions"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def scrape_page(self, driver, page_url):
        """Scrape a single page"""
        driver.get(page_url)
        time.sleep(3)
        
        # Your scraping logic here
        # Return list of job data
        
    def save_to_csv(self, jobs_data):
        """Save data to CSV file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.data_dir}/jobs_{timestamp}.csv"
        
        df = pd.DataFrame(jobs_data)
        df.to_csv(filename, index=False, encoding='utf-8')
        
        # Also save as latest.csv for easy access
        df.to_csv(f"{self.data_dir}/latest.csv", index=False, encoding='utf-8')
        
        print(f"Saved {len(df)} jobs to {filename}")
        return filename
    
    def run(self):
        """Main scraping function"""
        print("Starting job scraping...")
        driver = self.setup_driver()
        
        try:
            all_jobs = []
            page = 1
            
            while True:
                print(f"Scraping page {page}...")
                page_url = f"{self.url}?page={page}"
                page_jobs = self.scrape_page(driver, page_url)
                
                if not page_jobs:
                    break
                    
                all_jobs.extend(page_jobs)
                page += 1
                time.sleep(2)
                
        finally:
            driver.quit()
            
        if all_jobs:
            self.save_to_csv(all_jobs)
            
        return len(all_jobs)

if __name__ == "__main__":
    scraper = JobScraper()
    job_count = scraper.run()
    print(f"Scraping completed. Found {job_count} jobs.")
