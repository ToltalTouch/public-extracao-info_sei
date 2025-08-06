from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (UnexpectedAlertPresentException, NoAlertPresentException)
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import threading
import os
import sys
import time
import logging

class SeiLogin:
    def __init__(self, edgedriver_path = None):
        self.driver = None
        self.wait = None
        
        self.download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
        self.log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extracao_itens.log')
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=self.log_file,
            filemode='a'
        )        
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logging = logging.getLogger().addHandler(console_handler)
        

    def setup_webdriver(self):
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        edge_options = Options()
        edge_options.add_experimental_option("prefs", prefs)
        edge_options.add_argument("--headless")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--window-size=1920,1080")
        
        # Try multiple approaches to get EdgeDriver working
        driver_paths_to_try = []
        
        # Method 1: Try EdgeChromiumDriverManager (online download)
        try:
            logging.info("Tentando baixar EdgeDriver automaticamente...")
            service = Service(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=edge_options)
            logging.info("WebDriver configurado com sucesso via EdgeChromiumDriverManager.")
            self.driver.get("https://sei.antt.gov.br/")
            self.root = tk.Tk()
            self.root.withdraw()
            return
        except Exception as e:
            logging.warning(f"EdgeChromiumDriverManager falhou: {str(e)}")
        
        # Method 2: Try local EdgeDriver paths
        local_driver_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "edgedriver_win64", "msedgedriver.exe"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "msedgedriver.exe"),
            "msedgedriver.exe",  # If it's in PATH
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedgedriver.exe"
        ]
        
        for driver_path in local_driver_paths:
            if os.path.exists(driver_path) or driver_path == "msedgedriver.exe":
                try:
                    logging.info(f"Tentando usar EdgeDriver local: {driver_path}")
                    service = Service(driver_path)
                    self.driver = webdriver.Edge(service=service, options=edge_options)
                    logging.info(f"WebDriver configurado com sucesso usando: {driver_path}")
                    self.driver.get("https://sei.antt.gov.br/")
                    self.root = tk.Tk()
                    self.root.withdraw()
                    return
                except Exception as e:
                    logging.warning(f"Falha ao usar {driver_path}: {str(e)}")
                    continue
        
        # Method 3: Try without specifying service (let Selenium find it)
        try:
            logging.info("Tentando usar EdgeDriver do sistema...")
            self.driver = webdriver.Edge(options=edge_options)
            logging.info("WebDriver configurado com sucesso usando driver do sistema.")
            self.driver.get("https://sei.antt.gov.br/")
            self.root = tk.Tk()
            self.root.withdraw()
            return
        except Exception as e:
            logging.warning(f"Driver do sistema falhou: {str(e)}")
        
        # If all methods fail, provide helpful error message
        error_msg = """
        Não foi possível configurar o EdgeDriver. Soluções possíveis:
        
        1. Verifique sua conexão com a internet para download automático
        2. Baixe manualmente o EdgeDriver de: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
        3. Coloque o msedgedriver.exe na pasta: edgedriver_win64/
        4. Verifique se o Microsoft Edge está instalado
        5. Adicione o EdgeDriver ao PATH do sistema
        """
        logging.error(error_msg)
        raise Exception(error_msg)

    def wait_for_element(self, element=None, timer=None):
        return WebDriverWait(self.driver, timer).until(
            EC.presence_of_element_located((By.XPATH, element))
        )
        
        # Função para realizar login no sistema SIFAMA
    def login_action(self, user, password):
        try:
            # Localiza os campos de entrada
            user_field = self.driver.find_element(By.CSS_SELECTOR, '*[id*="txtUsuario"]')
            password_field = self.driver.find_element(By.CSS_SELECTOR, '*[id*="pwdSenha"]')
            login_button = self.driver.find_element(By.CSS_SELECTOR, '*[id*="sbmAcessar"]')

            # Preenche os campos de entrada
            user_field.send_keys(user)
            password_field.send_keys(password)
            login_button.click()
            
            if not user or not password:
                logging.error("Usuário ou senha não fornecidos.")
                return False

            return True
        except Exception as e:
            logging.error(f"Erro durante a execução de login_action: {e}")
            return False
    
    def login(self, user, password):
        logging.info('Acessando o SEI')
        current_url = self.driver.current_url
        self.login_action(user, password)
        time.sleep(3)
        
        logging.info(f"URL atual: {current_url}")
        try:
            # Aguarda a área principal da tela ou um erro fatal
            logging.info("Aguardando a área principal da tela ou erro fatal...")

            WebDriverWait(self.driver, 240).until(
                EC.url_changes(current_url)
            )

            try:
                logging.info
                # Verifica se o login foi bem-sucedido
                if self.driver.find_element(By.XPATH, '//*[@id="divInfraAreaTela"]').is_displayed():
                    logging.info("Login efetuado com sucesso!")
                    self.root.after(0, lambda: messagebox.showinfo("Sucesso", "Login efetuado com sucesso!"))
                    return True

            except Exception as e:    
                # Verifica se ocorreu um erro fatal
                if "Fatal error" in self.driver.page_source:
                    logging.error("Erro fatal detectado durante o login. Recarregando a página...")
                    self.driver.get("https://sei.antt.gov.br/")
                    self.driver.refresh()
                    WebDriverWait(self.driver, 240).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="divInfraAreaTela"]'))
                    )
                    logging.info("Página recarregada com sucesso. Login efetuado!")
                    self.root.after(0, lambda: messagebox.showinfo("Sucesso", "Login efetuado com sucesso após recarregar a página!"))
                    return True

        except UnexpectedAlertPresentException:
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                alert.accept()
                logging.warning(f"Alerta inesperado: {alert_text}. Tentando reiniciar o Selenium.")
                return False
            
            except NoAlertPresentException:
                user_fild = self.driver.find_element(By.CSS_SELECTOR, '*[id*="txtUsuario"]')
                self.driver.execute_script("arguments[0].value = '';", user_fild)
                self.root.after(0, lambda: messagebox.showerror("Login incorreto", f"Verifique o login e a senha."))
                logging.error("Login ou senha incorretos.")
                return False         
               
    def login_window(self):
        # Criação da interface gráfica para entrada de login e senha
        login_window = tk.Toplevel(self.root)
        login_window.title("Login SEI")
        login_window.geometry("250x125")
        login_window.resizable(False, False)

        # Labels e campos de entrada de Usuario
        tk.Label(login_window, text="Usuário:", font=("Arial", 10)).grid(row=0, column=0, padx=20, pady=10)
        login_entry = tk.Entry(login_window, bg="#DCDCDC")
        login_entry.grid(row=0, column=1, padx=5, pady=10)

        # Campo de entrada de Senha
        tk.Label(login_window, text="Senha:", font=("Arial", 10)).grid(row=1, column=0, padx=20, pady=10)
        password_entry = tk.Entry(login_window, bg="#DCDCDC", show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=10)
        password_entry.bind("<Return>", lambda event: login_submit())

        # Variável para armazenar o frame de sobreposição
        overlay_frame = None
        spinner_canvas = None
        arc = None

        def animate_spinner(angle=0):
            if spinner_canvas and arc and spinner_canvas.winfo_exists():  # Verifica se o spinner_canvas e o arco foram criados
                spinner_canvas.itemconfig(arc, start=angle)
                spinner_canvas.update()
                self.spinner_animation = login_window.after(50, animate_spinner, (angle + 10) % 360)

        def show_spinner():
            nonlocal overlay_frame, spinner_canvas, arc  # Declara as variáveis como não locais
            if overlay_frame is not None:
                overlay_frame.destroy()  # Remove o frame anterior, se existir

            overlay_frame = tk.Frame(login_window)
            overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)  # Ocupa toda a janela
            overlay_frame.grid_propagate(False)

            # Conteúdo do overlay (spinner e mensagem)
            spinner_canvas = tk.Canvas(overlay_frame, width=100, height=100, highlightthickness=0)
            spinner_canvas.place(relx=0.5, rely=0.4, anchor="center")  # Centraliza o spinner
            arc = spinner_canvas.create_arc(10, 10, 90, 90, start=0, extent=150, outline="#4682B4", width=5, style="arc")
            animate_spinner()

        def hide_spinner():
            nonlocal overlay_frame  # Permite acessar a variável overlay_frame
            if overlay_frame is not None:
                overlay_frame.destroy()  # Remove o frame de sobreposição
            if hasattr(self, 'spinner_animation'):
                login_window.after_cancel(self.spinner_animation)

        def login_submit():
            user = login_entry.get()
            password = password_entry.get()
            if user and password:
                show_spinner()
                threading.Thread(target=process_login, args=(user, password)).start()
            else:
                messagebox.showwarning("Aviso", "Por favor, preencha todos os campos")

        def process_login(user, password):
            if self.login(user, password):
                login_window.destroy()
            else:
                login_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)
            hide_spinner()

        # Botão de envio
        submit_button = tk.Button(
            login_window,
            text="Entrar",
            font=("Arial", 10),
            bg="#90EE90",
            fg="#006400",
            command=login_submit)
        submit_button.grid(row=2, column=1, pady=10)

        # Botão para fechar a janela
        close_button = tk.Button(
            login_window,
            text="Cancelar",
            command=lambda: (sys.exit()),
            font=("Arial", 9),
            bg="#800000",
            fg="#FFC0CB"
            )
        close_button.grid(row=2, column=0, columnspan=1, pady=10)

class PromptWindow:
    def __init__(self, root):
        self.root = root
    
    def prompt_window(self):
        prompt_window = tk.Toplevel(self.root)
        prompt_window.title("Log de Execução")

        prompt_window.configure(bg="white")

        output_text = scrolledtext.ScrolledText(
            prompt_window,
            height=30,
            width=130,
            bg="lightgray",
            fg="black",
            font=("Arial",12),
            insertbackground="white",
        )
        output_text.grid(row=0, column=0, padx=10, pady=10)

        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            def emit(self, record):
                log_entry = self.format(record)
                self.text_widget.insert(tk.END, log_entry + "\n")
                self.text_widget.see(tk.END)
        
        text_handler = TextHandler(output_text)
        text_handler.setFormatter(logging.Formatter("%(message)s"))
        logging.getLogger().addHandler(text_handler)

        # Botão para fechar a janela
        close_button = tk.Button(
            prompt_window,
            text="Fechar",
            command=lambda: (sys.exit()),
            font=("Arial", 10),
            bg="#800000",
            fg="#FFC0CB",
            )
        close_button.grid(row=1, column=0, pady=10)
        
if __name__ == "__main__":
    edgedriver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edgedriver_win64", "msedgedriver.exe")
    
    sei = SeiLogin(edgedriver_path)
    sei.setup_webdriver()
    prompt = PromptWindow(sei.root)
    sei.login_window()
    prompt.prompt_window()
    sei.root.mainloop()