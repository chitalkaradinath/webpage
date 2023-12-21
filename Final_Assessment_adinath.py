import pdb
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import smtplib
from email.utils import formatdate
from email.message import EmailMessage

class Stocks:
    def __init__(self):
        self.email_sender = "adinath.pchitalkar@kp.org"
        self.mail_recipients = "adinath.p.chitalkar@kp.org"
        self.options = Options()
        self.options.add_experimental_option("detach", True)
        self.service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        with open('google_config.json') as f:
            data = json.load(f)
            self.url = str(data["url"])
            self.dir = str(data["dir"])
            self.email_username = str(data["username"])
            self.email_password = str(data["password"])
            self.stock_searches = data["stock_searches"]

    def _google_search_stock_price(self, query, stock_name, stock_xpath):
        try:
            self.driver.get(self.url)
            self.driver.maximize_window()
            search_box = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.NAME, "q"))
            )
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            # Wait for the stock price element to be present
            stock_price_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, stock_xpath))
            )
            stock_price_text = stock_price_elem.text
            stock_price = float(stock_price_text)
            print(f'HERE IS THE {stock_name.upper()} STOCK PRICE: {stock_price}')
            return stock_price

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return 0.0

    def compare_stock_prices(self, amazon_price, microsoft_price):
        if amazon_price > microsoft_price:
            return "Amazon stock has a higher price.", amazon_price, microsoft_price
        elif amazon_price < microsoft_price:
            return "Microsoft stock has a higher price.", amazon_price, microsoft_price
        else:
            return "Amazon and Microsoft stocks have the same price.", amazon_price, microsoft_price

    def send_email(self, subject, receiver_email, comparison_result, amazon_price, microsoft_price, image_cid=None):
        try:
            msg = EmailMessage()
            receiver_email = self.mail_recipients  # Recipient's email address
            msg['From'] = self.email_sender  # your email address , declared in the init function
            msg['To'] = receiver_email        # same my mail receiver
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = subject         # declared in the main function
            html_body = f'''\
                        <html>
                        <body>
                        <p>Hello, Team !</p>
                        <p>{self.stock_searches[0]} Stock Price: {amazon_price}</p>
                        <p>{self.stock_searches[1]} Stock Price: {microsoft_price}</p>
                        <p>Comparison Result: {comparison_result}</p>
                        </p>
                        </body>
                        </html>
                        '''
            if image_cid is not None:
                html_body = html_body.format(image_cid=image_cid[1:-1])
            msg.add_alternative(html_body, subtype='html')
            smtp = smtplib.SMTP('mta.kp.org', 25)
            # smtp.login(self.email_username, self.email_password)
            smtp.sendmail(self.email_sender, receiver_email.split(','), msg.as_string())
            smtp.quit()
            return "Successfully sent mail"
        except Exception as e:
            print("Error in sending an email: ", e)
            return str(e)

    def main(self, comparison_result=None):
        try:
            print("Fetching Amazon stock price...")

            stock_prices = []
            stock_price_xpath = '//*[@id="knowledge-finance-wholepage__entity-summary"]/div[3]/g-card-section/div/g-card-section/div[2]/div[1]/span[1]/span/span[1]'

            for item in self.stock_searches:
                print("Getting stock value for "+item)
                first_stock = item + " stock Price"
                stock_price = self._google_search_stock_price(first_stock, item, stock_price_xpath)
                stock_prices.append(stock_price)
            #print("\nFetching Microsoft stock price...")
            #second_stock_price = self.stock_searches[1] + " stock price"
            #microsoft_xpath = '//*[@id="knowledge-finance-wholepage__entity-summary"]/div[3]/g-card-section/div/g-card-section/div[2]/div[1]/span[1]/span/span[1]'
            # microsoft_price = self._google_search_stock_price(second_stock_price, str(self.stock_searches[1]), microsoft_xpath)
            # print(f"\nAmazon stock price: {amazon_price}")
            # print(f"Microsoft stock price: {microsoft_price}")
            comparison_result = self.compare_stock_prices(stock_prices[0], stock_prices[1])
            print(comparison_result, f"{self.stock_searches[0]} Price:", stock_prices[0], f"{self.stock_searches[1]} Price:", stock_prices[1])
            subject = "Stock Prices Comparison"
            receiver_email = "adinath.p.chitalkar@kp.org"
            self.send_email(subject, receiver_email, comparison_result, stock_prices[0], stock_prices[1], image_cid=None)
        finally:
            self.driver.quit()


# Example usage
if __name__ == "__main__":
    stocks_instance = Stocks()
    stocks_instance.main()
