from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os



def search_zara(product_list):
    load_dotenv()
    mail = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")


    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)


    driver.get("https://www.zara.com/tr")
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        ).click()
    except:
        pass

    # Login işlemi
    try:
        driver.find_element(By.XPATH, '//*[@id="theme-app"]/div/div/header/ul/li[2]/a').click()
        wait.until(EC.visibility_of_element_located((By.NAME, "username"))).send_keys(mail)
        wait.until(EC.visibility_of_element_located((By.NAME, "password"))).send_keys(password)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/main/div[1]/div/div/form/button'))).click()
    except Exception as e:
        print(f"Login error: {e}")

    # Ürün ekleme döngüsü
    for product_code, size in product_list:
        try:
            driver.get("https://www.zara.com/tr")

            # Arama
            search_icon = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="theme-app"]/div/div/header/ul/li[1]/a')))
            driver.execute_script("arguments[0].click();", search_icon)
            search_bar = wait.until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="search-home-form-combo-input"]')))
            search_bar.clear()
            search_bar.send_keys(product_code, Keys.ENTER)

            # İlk ürün
            first_product = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.product-link")))
            driver.execute_script("arguments[0].click();", first_product)

            # Beden seçimi
            sizes_ul = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.size-selector-sizes")))
            sizes = sizes_ul.find_elements(By.TAG_NAME, "li")
            size_found = False

            for s in sizes:
                try:
                    label = s.find_element(By.CSS_SELECTOR, "div.size-selector-sizes-size__label").text.strip()
                    if label != size:
                        continue
                    size_found = True

                    try:
                        status_elem = s.find_element(By.CSS_SELECTOR, "div.size-selector-sizes-size__action")
                        status = status_elem.text.strip()
                    except:
                        status = "Clickable"

                    if "Coming soon" in status or "Similar products" in status:
                        print(f"{product_code} - Size {label} is out of stock. ({status})")
                    else:
                        button = s.find_element(By.TAG_NAME, "button")
                        driver.execute_script("arguments[0].click();", button)
                        print(f"{product_code} - Size {label} added to cart! ({status})")
                    break
                except Exception as e:
                    print(f"{product_code} - Error processing size: {e}")

            if not size_found:
                print(f"{product_code}: Requested size ({size}) not listed on the page.")
        except Exception as e:
            print(f"{product_code}: Error during product process: {e}")

    # Tüm ürünler eklendikten sonra sepete geç
    try:
        cart_count_element = driver.find_element(By.CSS_SELECTOR, "[data-qa-id='layout-header-go-to-cart-items-count']")
        cart_count = int(cart_count_element.text.strip() or 0)
        if cart_count > 0:
            try:
                cart_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-qa-id='layout-header-go-to-cart']")))
                driver.execute_script("arguments[0].click();", cart_button)
                print("Sepete gidildi.")
            except TimeoutException:
                print("Cart button not found.")

            try:
                continue_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-qa-id='shop-continue']")))
                driver.execute_script("arguments[0].click();", continue_button)
                print("Continue butonuna tıklandı.")
            except TimeoutException:
                print("'Continue' button not found.")
        else:
            print("Sepet boş.")
    except Exception as e:
        print(f"Error during go_to_cart: {e}")