import time
import json
import undetected_chromedriver as uc
import mysql.connector
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -----------------------------
# Config
# -----------------------------
URL = "https://www.ivasms.com/portal/live/my_sms"
POLL_INTERVAL = 1.0  # seconds

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "admin",
    "password": "admin",  # <- your MySQL password
    "database": "sms_monitor"
}

# JS_INJECT stays the same as your provided robust snippet
JS_INJECT = r"""
(function(){
  if (window.__sms_monitor_installed) return "already_installed";
  window.__sms_monitor_installed = true;
  window.__newSmsQueue = [];

  function extractRowData(tr){
    try {
      const numberEl = tr.querySelector("p.CopyText");
      const number = numberEl ? numberEl.innerText.trim() : null;
      const countryEl = tr.querySelector("h6 a");
      const country = countryEl ? countryEl.innerText.trim() : null;
      const sidEl = tr.querySelector("td:nth-child(2) .fw-semi-bold");
      const sid = sidEl ? sidEl.innerText.trim() : null;
      const paidEl = tr.querySelector("td:nth-child(3) label");
      const paid = paidEl ? paidEl.innerText.trim() : null;
      const limitEl = tr.querySelector("td:nth-child(4) label");
      const limit = limitEl ? limitEl.innerText.trim() : null;
      const messageEl = tr.querySelector("td:nth-child(5)");
      const message = messageEl ? messageEl.innerText.trim() : null;
      return { number, country, sid, paid, limit, message, _ts: Date.now() };
    } catch(e){ return {number:null, country:null, sid:null, paid:null, limit:null, message:null, error:String(e)}; }
  }

  function observe(){
    const tbody = document.querySelector("#LiveTestSMS");
    if (!tbody) return "no_table";
    const mo = new MutationObserver(function(muts){
      muts.forEach(m => {
        if (m.addedNodes && m.addedNodes.length){
          m.addedNodes.forEach(node => {
            if (node.nodeType === 1 && node.tagName === "TR"){
              try {
                const data = extractRowData(node);
                window.__newSmsQueue.push(data);
                console.info("[SMS_MONITOR][NEW_ROW]", JSON.stringify(data));
              } catch(e){}
            }
          });
        }
      });
    });
    mo.observe(tbody, { childList: true, subtree: false });
    return "observing";
  }

  if (document.readyState === "complete" || document.readyState === "interactive"){
    const res = observe();
    if (res === "no_table") {
      const waiter = setInterval(() => {
        const t = document.querySelector("#LiveTestSMS");
        if (t) {
          clearInterval(waiter);
          observe();
        }
      }, 500);
    }
  } else {
    window.addEventListener("DOMContentLoaded", () => {
      const res = observe();
      if (res === "no_table") {
        const waiter = setInterval(() => {
          const t = document.querySelector("#LiveTestSMS");
          if (t) {
            clearInterval(waiter);
            observe();
          }
        }, 500);
      }
    });
  }

  return "injected";
})();
"""

# -----------------------------
# Helper: fetch new SMS queue from JS
# -----------------------------
def fetch_queue(driver):
    script = "return (function(){ const q = window.__newSmsQueue||[]; const out = q.splice(0,q.length); return out; })();"
    try:
        return driver.execute_script(script)
    except Exception:
        return []

# -----------------------------
# Main
# -----------------------------
def main():
    # Connect to MySQL
    db = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = db.cursor()

    # Chrome options
    options = uc.ChromeOptions()
    # options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)

    try:
        driver.get(URL)
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.ID, "LiveTestSMS")))
        print("Page loaded:", driver.title)

        # Inject JS observer
        driver.execute_script(JS_INJECT)
        print("JS injected, monitoring new SMS...")

        while True:
            try:
                new_items = fetch_queue(driver)
                if new_items:
                    for item in new_items:
                        number = item.get("number")
                        country = item.get("country")
                        sid = item.get("sid")
                        paid = item.get("paid")
                        limit_status = item.get("limit")
                        message = item.get("message")

                        # Insert into MySQL
                        try:
                            sql = """
                            INSERT IGNORE INTO live_sms
                            (number, country, sid, paid, limit_status, message)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """
                            cursor.execute(sql, (number, country, sid, paid, limit_status, message))
                            db.commit()
                            print("NEW_SMS SAVED:", number, message)
                        except Exception as e:
                            print("MySQL insert error:", e)
                time.sleep(POLL_INTERVAL)
            except KeyboardInterrupt:
                print("Monitoring stopped by user.")
                break
            except Exception as e:
                print("Loop error:", e)
                time.sleep(2)
    finally:
        try:
            driver.quit()
        except:
            pass
        try:
            cursor.close()
            db.close()
        except:
            pass

if __name__ == "__main__":
    main()
