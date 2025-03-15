from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import random

#from db_connection import get_db_connection

# Connexion à la base de données
#conn = get_db_connection()
#cursor = conn.cursor()

# Configuration du navigateur
options = Options()
options.add_argument("--detach")
driver = webdriver.Chrome(options=options)
driver.get("https://amazon.fr")

time.sleep(3)

# Accepter les cookies
try:
    driver.find_element(By.ID, "sp-cc-accept").click()
except:
    print("Bouton cookies non trouvé ou déjà accepté.")

# Recherche sur Amazon
search_box = driver.find_element(By.ID, "twotabsearchtextbox")
search_box.send_keys("ordinateur portable")
search_box.send_keys(Keys.ENTER)
time.sleep(3)

# Nombre de pages à scraper
num_pages = 3


def get_specifications(driver):
    specs = {}

    try:
        rows = driver.find_elements(By.XPATH, "//table[@class='a-normal a-spacing-micro']//tr")
        for row in rows:
            try:
                label = row.find_element(By.XPATH, ".//td[@class='a-span3']/span").text.strip()
                value = row.find_element(By.XPATH, ".//td[@class='a-span9']/span").text.strip()
                specs[label] = value
            except NoSuchElementException:
                continue
    except NoSuchElementException:
        print("Tableau des spécifications non trouvé.")

    return specs


def get_price_and_reviews(driver):
    try:
        price_whole = driver.find_element(By.CSS_SELECTOR, "span.a-price-whole").text
        price_fraction = driver.find_element(By.CSS_SELECTOR, "span.a-price-fraction").text
        price = f"{price_whole},{price_fraction} €"
    except NoSuchElementException:
        price = "Prix non disponible"

    try:
        rating = driver.find_element(By.XPATH, "//span[@id='acrPopover']/span[1]/a/span").text
    except NoSuchElementException:
        rating = "Note non disponible"

    try:
        review_count = driver.find_element(By.ID, "acrCustomerReviewText").text.split()[0]
    except NoSuchElementException:
        review_count = "Nombre d'avis non disponible"

    return price, rating, review_count


for page in range(num_pages):
    print(f"\n{'=' * 10} PAGE {page + 1} {'=' * 10}\n")
    results = driver.find_elements(By.CSS_SELECTOR, 'div.s-main-slot div[data-component-type="s-search-result"]')

    for i, result in enumerate(results, 1):
        try:
            link_element = result.find_element(By.CSS_SELECTOR, "a.a-link-normal.s-no-outline")
            link = link_element.get_attribute("href")

            # Ouvrir une nouvelle fenêtre pour chaque produit
            driver.execute_script("window.open(arguments[0]);", link)
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(3)

            specs = get_specifications(driver)
            price, rating, review_count = get_price_and_reviews(driver)

            marque = specs.get("Marque", "Non disponible")
            processeur = specs.get("Modèle du CPU", "Non disponible")
            taille_ecran = specs.get("Taille de l'écran", "Non disponible")
            disque_dur = specs.get("Taille du disque dur", "Non disponible") + " " + specs.get("Description du disque dur", "")

            print(
                f"\nPC {i} :\nMarque: {marque}\nProcesseur: {processeur}\nTaille écran: {taille_ecran}\nDisque dur: {disque_dur}\nPrix: {price}\nNote: {rating}\nAvis: {review_count}\n"
            )

            # Insérer les données dans MySQL
            sql = """
            INSERT IGNORE INTO produits (marque, processeur, taille_ecran, disque_dur, prix, note, avis)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (marque, processeur, taille_ecran, disque_dur, price, rating, review_count)

            cursor.execute(sql, values)
            conn.commit()


        except Exception as e:
            print(f"Erreur lors du traitement du PC {i}: {e}")

        finally:
            # Fermer la fenêtre du produit et revenir à la liste principale
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    # Passer à la page suivante
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "a.s-pagination-next")
        driver.execute_script("arguments[0].scrollIntoView();", next_button)
        time.sleep(1)
        next_button.click()
        time.sleep(random.randint(5, 10))  # Attente aléatoire pour éviter les blocages
        driver.refresh()
        print(f" Passé à la page {page + 2}")
    except NoSuchElementException:
        print(" Pas de bouton 'Page Suivante', fin du scraping.")
        break

# Fermeture propre
driver.quit()
cursor.close()
conn.close()

print("Les données ont été enregistrées dans la base de données MySQL.")
