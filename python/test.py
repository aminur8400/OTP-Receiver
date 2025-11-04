import time
import json
import undetected_chromedriver as uc
import mysql.connector
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

# -----------------------------
# Config
# -----------------------------
URL = "https://www.ivasms.com/portal/live/my_sms"
POLL_INTERVAL = 1.0  # seconds

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "admin",
    "password": "admin",
    "database": "otp_api_services"
}

# -----------------------------
# JS Observer (Option B)
# -----------------------------
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
# Helper: fetch new SMS queue
# -----------------------------
def fetch_queue(driver):
    script = "return (function(){ const q = window.__newSmsQueue||[]; const out = q.splice(0,q.length); return out; })();"
    try:
        return driver.execute_script(script)
    except Exception:
        return []

# -----------------------------
# Helper: Insert SMS into Laravel DB
# -----------------------------
def insert_sms(number, country, sid, paid, limit_status, message):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()

    # 1️⃣ Find or create number
    cursor.execute("SELECT id FROM numbers WHERE number=%s", (number,))
    row = cursor.fetchone()
    if row:
        number_id = row[0]
    else:
        cursor.execute(
            "INSERT INTO numbers (number, country, sid, paid, limit_status, created_at, updated_at) VALUES (%s,%s,%s,%s,%s,NOW(),NOW())",
            (number, country, sid, paid, limit_status)
        )
        conn.commit()
        number_id = cursor.lastrowid

    # 2️⃣ Check active assignment (expire_at > NOW())
    cursor.execute("""
        SELECT user_id FROM number_assignments
        WHERE number_id=%s AND active=1 AND expire_at > NOW()
        ORDER BY id DESC LIMIT 1
    """, (number_id,))
    res = cursor.fetchone()
    user_id = res[0] if res else None

    # 3️⃣ Insert SMS
    cursor.execute("""
        INSERT INTO sms_messages (number_id, user_id, sender_number, message, received_at, created_at, updated_at)
        VALUES (%s, %s, %s, %s, NOW(), NOW(), NOW())
    """, (number_id, user_id, number, message))
    conn.commit()

    # 4️⃣ Add point to user
    if user_id:
        cursor.execute("UPDATE users SET points = points + 1 WHERE id=%s", (user_id,))
        conn.commit()

    cursor.close()
    conn.close()

    print(f"✅ SMS stored: {number} → {message[:50]}{'...' if len(message)>50 else ''}")

# -----------------------------
# Main Loop
# -----------------------------
def main():
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)

    try:
        driver.get(URL)
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.ID, "LiveTestSMS")))
        print("Page loaded:", driver.title)

        driver.execute_script(JS_INJECT)
        print("JS injected, monitoring new SMS...")

        while True:
            try:
                new_items = fetch_queue(driver)
                for item in new_items:
                    number = item.get("number")
                    country = item.get("country")
                    sid = item.get("sid")
                    paid = item.get("paid")
                    limit_status = item.get("limit")
                    message = item.get("message")

                    if number and message:
                        insert_sms(number, country, sid, paid, limit_status, message)
                time.sleep(POLL_INTERVAL)
            except KeyboardInterrupt:
                print("Stopped by user.")
                break
            except Exception as e:
                print("Loop error:", e)
                time.sleep(2)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
