import os
import csv
import time
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Global variables
URL = "https://www.elempleo.com/co/ofertas-empleo/?Salaries=menos-1-millon:10-125-millones&PublishDate=hoy"

class GitHubScraper:
    def __init__(self):
        # Create data directory
        self.data_dir = "datos"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Generate filename with timestamp
        now = datetime.now()
        fecha = now.strftime("%Y-%m-%d")
        self.csv_file = os.path.join(self.data_dir, f"ofertas_{fecha}.csv")
        
    def setup_driver(self):
        """Setup Chrome driver for GitHub Actions"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # For GitHub Actions
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def create_csv(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file, delimiter="|")
                writer.writerow([
                    "id", "Titulo", "Salario", "Ciudad", "Fecha", "Detalle", "Cargo",
                    "Tipo de puesto", "Nivel de educación", "Sector", "Experiencia",
                    "Tipo de contrato", "Vacantes", "Areas", "Profesiones",
                    "Nombre empresa", "Descripcion empresa", "Habilidades", "Cargos"
                ])
            print(f"Created CSV file: {self.csv_file}")
    
    def scrape_simple_data(self, driver):
        """Simplified scraping function for GitHub Actions"""
        try:
            print("Navigating to URL...")
            driver.get(URL)
            time.sleep(5)
            
            # Accept cookies if present
            try:
                accept_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceptar') or contains(text(), 'Accept')]"))
                )
                accept_button.click()
                print("Cookies accepted")
                time.sleep(2)
            except:
                print("No cookie banner found")
            
            # Find job listings
            print("Looking for job listings...")
            job_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'result-item')]"))
            )
            
            print(f"Found {len(job_elements)} job listings")
            
            # Scrape basic job information
            jobs_data = []
            for i, job in enumerate(job_elements[:5]):  # Limit to 5 for testing
                try:
                    # Extract basic information
                    title = job.find_element(By.XPATH, ".//a[contains(@class, 'js-offer-title')]").text
                    company = job.find_element(By.XPATH, ".//span[contains(@class, 'company')]").text
                    location = job.find_element(By.XPATH, ".//span[contains(@class, 'city')]").text
                    
                    # Try to get salary
                    try:
                        salary = job.find_element(By.XPATH, ".//span[contains(@class, 'salary')]").text
                    except:
                        salary = "No especificado"
                    
                    # Try to get date
                    try:
                        date = job.find_element(By.XPATH, ".//span[contains(@class, 'date')]").text
                    except:
                        date = datetime.now().strftime("%Y-%m-%d")
                    
                    # Create job data dictionary
                    job_data = {
                        "id": f"job_{i+1}_{datetime.now().strftime('%H%M%S')}",
                        "Titulo": title,
                        "Salario": salary,
                        "Ciudad": location,
                        "Fecha": date,
                        "Detalle": "",  # Simplified for GitHub Actions
                        "Cargo": title.split()[0] if title else "",
                        "Tipo de puesto": "",
                        "Nivel de educación": "",
                        "Sector": "",
                        "Experiencia": "",
                        "Tipo de contrato": "",
                        "Vacantes": "1",
                        "Areas": "",
                        "Profesiones": "",
                        "Nombre empresa": company,
                        "Descripcion empresa": "",
                        "Habilidades": "",
                        "Cargos": ""
                    }
                    
                    jobs_data.append(job_data)
                    print(f"Scraped: {title[:50]}...")
                    
                except Exception as e:
                    print(f"Error scraping job {i}: {str(e)}")
                    continue
            
            return jobs_data
            
        except Exception as e:
            print(f"Error in scraping: {str(e)}")
            return []
    
    def save_to_csv(self, jobs_data):
        """Save scraped data to CSV"""
        if not jobs_data:
            print("No data to save")
            return False
        
        self.create_csv()
        
        with open(self.csv_file, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter="|")
            for job in jobs_data:
                writer.writerow([
                    job["id"],
                    job["Titulo"],
                    job["Salario"],
                    job["Ciudad"],
                    job["Fecha"],
                    job["Detalle"],
                    job["Cargo"],
                    job["Tipo de puesto"],
                    job["Nivel de educación"],
                    job["Sector"],
                    job["Experiencia"],
                    job["Tipo de contrato"],
                    job["Vacantes"],
                    job["Areas"],
                    job["Profesiones"],
                    job["Nombre empresa"],
                    job["Descripcion empresa"],
                    job["Habilidades"],
                    job["Cargos"]
                ])
        
        print(f"Saved {len(jobs_data)} jobs to {self.csv_file}")
        return True
    
    def run(self):
        """Main function to run the scraper"""
        print("Starting GitHub Actions scraper...")
        
        driver = self.setup_driver()
        
        try:
            # Scrape data
            jobs_data = self.scrape_simple_data(driver)
            
            # Save to CSV
            if jobs_data:
                saved = self.save_to_csv(jobs_data)
                if saved:
                    print("Scraping completed successfully!")
                    return True
            else:
                print("No jobs data scraped")
                return False
                
        except Exception as e:
            print(f"Error in scraper: {str(e)}")
            return False
            
        finally:
            driver.quit()
            print("Driver closed")

if __name__ == "__main__":
    scraper = GitHubScraper()
    success = scraper.run()
    sys.exit(0 if success else 1)
