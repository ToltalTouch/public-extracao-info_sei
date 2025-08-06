import os
import time
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from login_sei import SeiLogin, PromptWindow
from extracao_itens_sei import ExtracaoItensSei
           
if __name__ == "__main__":
    web_driver = SeiLogin()
    web_driver.setup_webdriver()
    download_sei = ExtracaoItensSei(base_dir = os.path.dirname(os.path.abspath(__file__)), web_driver=web_driver)
    prompt = PromptWindow(web_driver.root)
    
    def executar_selenium():
        prompt.prompt_window()
        time.sleep(1)
        web_driver.login_window()
        WebDriverWait(web_driver.driver, 240).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="divInfraBarraSistemaPadraoD"]/div[2]'))
        )  
        download_sei.encontrar_arquivos()
    
    selenium_thread = threading.Thread(target=executar_selenium)
    selenium_thread.start()
    web_driver.root.mainloop()