# =============================================================================
# INFORMATION ABOUT CODE         Coding: ISO 9001:2015
# =============================================================================
# IRCTC Automation with GUI
# For booking Tatkal or General ticket with COD option.(Verified)
# Note: Please put same station name as well as date mentioned in IRCTC.
# Basic Requirement Selenium module, webdriver-manager
# =============================================================================

import time
from tkinter import Frame, Tk, Label, Entry, E, Button, LEFT
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class BookingGui(Frame):
    def __init__(self, master, labels):
        """
        For Creating interactive GUI for IRCTC automation
        :param master:
        :param labels:
        """
        super().__init__(master)
        self.label = labels
        self.passenger = ["PassengersDetail:", "Psg:One", "Psg:Two", "Psg:Three", "Psg:Four"]
        self.entry = {}
        self.values = {}

    def main_gui(self):
        """
        For creating interactive GUI for IRCTC Automation
        """
        for label_index, label_value in enumerate(self.label):
            Label(self, text=label_value).grid(row=label_index + 1, column=0)
            self.entry[label_value] = Entry(self, show="*") if label_value == "Password" else Entry(self)
            self.entry[label_value].grid(row=label_index + 1, column=1)
        
        for passenger_index, passenger_label in enumerate(self.passenger):
            Label(self, text=passenger_label).grid(row=10, column=passenger_index)
        
        for index, value in enumerate(self.label[10:], start=12):
            Label(self, text=value).grid(row=index, column=0)
            for extra_index in range(4):
                self.entry[value + str(extra_index)] = Entry(self)
                self.entry[value + str(extra_index)].grid(row=index, column=extra_index + 1)
        
        Button(self, text="Book Tatkal Ticket", command=self._login_btn_clicked).grid(row=5, column=3)

    def _login_btn_clicked(self):
        """
        It will start the portal with provided value
        """
        for label in self.label[:10]:
            self.values[label] = self.entry[label].get()
        
        for temp_index in self.label[10:]:
            for extra_index in range(4):
                self.values[temp_index + str(extra_index)] = self.entry[temp_index + str(extra_index)].get()
        
        booking = Booking(self.values)
        booking.main()

class Booking:
    def __init__(self, values):
        """
        It will hold the main class for executing Chrome Browser
        :param values:
        """
        self.browser = None
        self.values = values

    def main(self):
        """
        It will be having main script for Chrome automation
        """
        try:
            print("Initializing Chrome Webdriver...")
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            self.browser = webdriver.Chrome(service=service, options=options)
            wait = WebDriverWait(self.browser, 20)
            wait_long = WebDriverWait(self.browser, 300) # 5 minutes for captchas

            print("Opening IRCTC Portal...")
            self.browser.get("https://www.irctc.co.in/nget/train-search")
            
            # Modern IRCTC login
            print("Waiting for login button...")
            login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'LOGIN')]")))
            login_btn.click()

            print("Entering credentials...")
            username_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@formcontrolname='userid']")))
            username_field.send_keys(self.values["UserID"])
            
            password_field = self.browser.find_element(By.XPATH, "//input[@formcontrolname='password']")
            password_field.send_keys(self.values["Password"])

            print("Waiting for manual CAPTCHA entry and Login button click...")
            # Wait until the user manually solves the CAPTCHA and logs in. We detect login by the disappearance of the login modal.
            wait_long.until(EC.invisibility_of_element_located((By.XPATH, "//input[@formcontrolname='userid']")))
            print("Login successful.")

            print("Filling search details...")
            from_station = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@aria-controls='pr_id_1_list']")))
            from_station.clear()
            from_station.send_keys(self.values["FromStation"])
            # Require exact station selection wait or allow manual selection
            # wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{self.values['FromStation'].upper()}')]"))).click()

            to_station = self.browser.find_element(By.XPATH, "//input[@aria-controls='pr_id_2_list']")
            to_station.clear()
            to_station.send_keys(self.values["ToStation"])

            date_field = self.browser.find_element(By.XPATH, "//input[contains(@class, 'ui-calendar')]")
            date_field.send_keys(Keys.CONTROL, "a")
            date_field.send_keys(Keys.BACKSPACE)
            date_field.send_keys(self.values["Date"])
            
            print("Please confirm the search details, select train/class, and click 'Book Now'.")
            print("Waiting for passenger details page...")
            
            # Wait for passenger details page to load (Passenger Name field presence)
            passenger_name_field = wait_long.until(EC.presence_of_element_located((By.XPATH, "//input[@formcontrolname='passengerName']")))

            print("Filling passenger details...")
            passenger_name_field.send_keys(self.values["Name0"])
            
            age_field = self.browser.find_element(By.XPATH, "//input[@formcontrolname='passengerAge']")
            age_field.send_keys(self.values["Age0"])

            gender_dropdown = self.browser.find_element(By.XPATH, "//select[@formcontrolname='passengerGender']")
            gender_dropdown.send_keys(self.values["Gender0"])

            for index in range(1, 4):
                if self.values[f"Name{index}"]:
                    add_passenger_btn = self.browser.find_element(By.XPATH, "//span[contains(text(), '+ Add Passenger')]")
                    add_passenger_btn.click()
                    
                    names = self.browser.find_elements(By.XPATH, "//input[@formcontrolname='passengerName']")
                    ages = self.browser.find_elements(By.XPATH, "//input[@formcontrolname='passengerAge']")
                    genders = self.browser.find_elements(By.XPATH, "//select[@formcontrolname='passengerGender']")
                    
                    names[index].send_keys(self.values[f"Name{index}"])
                    ages[index].send_keys(self.values[f"Age{index}"])
                    genders[index].send_keys(self.values[f"Gender{index}"])

            try:
                mobile_field = self.browser.find_element(By.XPATH, "//input[@formcontrolname='mobileNumber']")
                mobile_field.clear()
                mobile_field.send_keys(self.values["MobileNo"])
            except Exception:
                print("Could not find mobile number field, might already be populated.")

            print("Passenger details filled.")
            print("Please manually complete the remaining process (Captchas, Payment, etc.).")
            
            # Keep browser open until the user closes it manually or script exits
            while True:
                time.sleep(1)

        except Exception as error:
            print(f"An error occurred: {error}")
            input("Press Enter to exit...")

if __name__ == '__main__':
    FIELDS = ["UserID", "Password", "TrainNo", "FromStation", "ToStation", "Date", "Class", "Quota",
              "MobileNo", "PassengersDetail:", "Name", "Age", "Gender"]
    ROOT = Tk()
    BOOKING = BookingGui(ROOT, FIELDS)
    BOOKING.main_gui()
    BOOKING.pack(side=LEFT)
    ROOT.mainloop()
