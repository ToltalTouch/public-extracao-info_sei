from config import Config

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import logging
import os
import re
from datetime import datetime, timedelta   

class Buscas:
    def __init__(self, web_driver, config: Config = None):
        self.config = config or Config()
        self.web_driver = web_driver
        self.atual_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.setup_logging()
    
    def procurar_caixa_pesquisa(self):
        for xpath in self.config.XPATH_PESQUISA:
            try:
                element = WebDriverWait(self.web_driver.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                return element
            except TimeoutException:
                continue
        
    def setup_logging(self):
        log_file = os.path.join(self.atual_dir, 'logs', 'sei_extraction.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=log_file,
            filemode='a'
        )        
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logging = logging.getLogger().addHandler(console_handler)
        
    def buscar_matricula(self):
        try:
            for xpath in self.config.XPATH_MATRICULA:
                try:
                    matricula_elemento = self.web_driver.driver.find_element(By.XPATH, xpath)
                    matricula = matricula_elemento.text.strip()
                    if matricula and matricula.isdigit() and len(matricula) >= 6:
                        logging.info(f"Matrícula encontrada: {matricula}")
                        return matricula
                except Exception:
                    continue
            return
        except Exception as e:
            logging.error(f"Erro ao buscar matrícula: {e}")
            return ""
        
    def buscar_cargo(self):
        try:
            for xpath in self.config.XPATH_CARGO:
                try:
                    cargo_elemento = self.web_driver.driver.find_element(By.XPATH, xpath)
                    texto_cargo = cargo_elemento.text.strip()
                    if "CARGO" in texto_cargo:
                        cargo = texto_cargo.replace("CARGO:", "").strip()
                    else:
                        cargo = texto_cargo
                    if cargo and len(cargo) > 3:
                        logging.info(f"Cargo encontrado: {cargo}")
                        return cargo
                except Exception:
                    continue
            return ""
        except Exception as e:
            logging.error(f"Erro ao buscar cargo: {e}")
            return ""
    
    def buscar_lotacao(self):
        try:
            for xpath in self.config.XPATH_LOTACAO:
                try:
                    lotacao_elemento = self.web_driver.driver.find_element(By.XPATH, xpath)
                    texto_lotacao = lotacao_elemento.text.strip()
                    
                    if "LOTAÇÃO" in texto_lotacao:
                        lotacao = texto_lotacao.replace("LOTAÇÃO:", "").strip()
                    else:
                        lotacao = texto_lotacao
                        
                    if lotacao and len(lotacao) > 3:
                        logging.info(f"Lotação encontrada: {lotacao}")
                        return lotacao
                except Exception:
                    continue
            return ""
        except Exception as e:
            logging.error(f"Erro ao buscar lotação: {e}")
            return ""
    
    def buscar_nome(self):
        try:
            for xpath in self.config.XPATH_NOME:
                try:
                    nome_funcionario_element = self.web_driver.driver.find_element(By.XPATH, xpath)
                    nome_funcionario = nome_funcionario_element.text.strip().replace('&nbsp;', ' ')
                    if nome_funcionario and ' ' in nome_funcionario and len(nome_funcionario.split()) >= 2:
                        return nome_funcionario
                except Exception:
                    continue
            return ""
        except Exception as e:
            logging.error(f"Erro ao buscar nome do servidor: {e}")
            return ""
    
    def buscar_data(self):
        padrao_data = re.compile(r'\d{1,2}/\d{1,2}/\d{4}')
        padrao_data_completa = re.compile(r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}:\d{2})')

    
        for xpath in self.config.XPATH_DATA:
            try:
                elementos = self.web_driver.driver.find_elements(By.XPATH, xpath)
                for elemento in elementos:
                    texto = elemento.text.strip()
                    if texto and ('em ' in texto or 'Criado por' in texto):
                        match_completa = re.search(padrao_data_completa, texto)
                        if match_completa:
                            data_encontrada = match_completa.group(1)
                            hora_encontrada = match_completa.group(2)
                            logging.info(f"Data e hora encontradas: {data_encontrada} {hora_encontrada}")
                            return data_encontrada
                        
                        match_simples = re.search(padrao_data, texto)
                        if match_simples:
                            data_encontrada = match_simples.group(0)
                            return data_encontrada
            except Exception:
                continue
    
    def calculo_data(self):
        try:
            data_encontrada = self.buscar_data()
            logging.info(f"Data encontrada: {data_encontrada}")
            if data_encontrada:
                match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', data_encontrada)
                if match:
                    dia, mes, ano = match.groups()
                    data_original = datetime(int(ano), int(mes), int(dia))
                    
                    try:
                        data_vencimento = data_original.replace(year=data_original.year + 2)
                    except ValueError:
                        data_vencimento = data_original + timedelta(days=365*2)
                        
                    data_vencimento_str = data_vencimento.strftime('%d/%m/%Y')
                    
                    logging.info(f"Data de vencimento calculada: {data_vencimento_str}")
                    return data_vencimento_str
                else:
                    logging.error("Formato de data inválido encontrado.")
                    return ""
            else:
                logging.warning("Nenhuma data encontrada.")
        except Exception as e:
            logging.error(f"Erro ao calcular data de vencimento: {e}")
            return ""