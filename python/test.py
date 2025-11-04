import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize undetected Chrome
driver = uc.Chrome()

# Open page
driver.get("https://www.ivasms.com/portal/live/my_sms")

# Wait until the table appears (adjust selector as needed)
WebDriverWait(driver, 40).until(
    EC.presence_of_element_located((By.ID, "LiveTestSMS"))
)

print("Page loaded:", driver.title)

# Now you can start scraping the table rows
rows = driver.find_elements(By.CSS_SELECTOR, "#LiveTestSMS tr")
for row in rows:
    number = row.find_element(By.CSS_SELECTOR, "p.CopyText").text
    message = row.find_element(By.CSS_SELECTOR, "td:nth-child(5)").text
    print(number, message)
