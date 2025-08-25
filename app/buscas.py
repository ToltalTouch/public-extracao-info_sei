from app.config import Config
from app.login_sei import SeiLogin

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
        self.web_driver = web_driver or SeiLogin()
        self.atual_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Não configurar logging aqui - será configurado na classe principal
        # self.config.setup_logging()
        
        if web_driver is None:
            self.web_driver.setup_webdriver()
    
    def procurar_caixa_pesquisa(self):
        for xpath in self.config.XPATH_PESQUISA:
            try:
                element = WebDriverWait(self.web_driver.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                return element
            except TimeoutException:
                continue

    def paragrafos_continuos(self, elemento_texto):
        try:
            if not elemento_texto or not hasattr(elemento_texto, 'text'):
                return None
                
            texto = elemento_texto.text.strip()
            
            if "Eu," not in texto:
                return None
                
            dados_extraidos = {}

            nome_match = re.search(r"Eu,\s*(.+?),\s*matrícula", texto, re.IGNORECASE)
            if nome_match:
                nome = nome_match.group(1).strip()
                nome = re.sub(r'<[^>]+>', '', nome)
                nome = nome.replace('&nbsp;', ' ').strip()
                dados_extraidos['nome'] = nome
            
            for pattern in self.config.MATRICULA_PATTERNS:
                matricula_match = re.search(pattern, texto, re.IGNORECASE)
                if matricula_match:
                    matricula = matricula_match.group(1).strip()
                    if matricula.isdigit() and len(matricula) >= 6:
                        dados_extraidos['matricula'] = matricula
                        break
            
            for pattern in self.config.CARGO_PATTERNS:
                cargo_match = re.search(pattern, texto, re.IGNORECASE)
                if cargo_match:
                    cargo = cargo_match.group(1).strip()
                    dados_extraidos['cargo'] = cargo
                    break
            
            for pattern in self.config.LOTACAO_PATTERNS:
                lotacao_match = re.search(pattern, texto, re.IGNORECASE)
                if lotacao_match:
                    lotacao = lotacao_match.group(1).strip()
                    lotacao = re.sub(r'[,\.]+$', '', lotacao).strip()
                    dados_extraidos['lotacao'] = lotacao
                    break
            
            if dados_extraidos:
                logging.info(f"Dados extraídos de parágrafo contínuo: {dados_extraidos}")
                return dados_extraidos
                
        except Exception as e:
            logging.error(f"Erro ao processar parágrafo contínuo: {e}")
        
        return None

    def buscar_nome(self):
        try:
            for xpath in self.config.XPATH_NOME:
                try:
                    nome_funcionario_element = self.web_driver.driver.find_element(By.XPATH, xpath)
                    nome_funcionario_texto = nome_funcionario_element.text.strip().replace('&nbsp;', ' ')
                    
                    dados_paragrafo = self.paragrafos_continuos(nome_funcionario_element)
                    if dados_paragrafo and 'nome' in dados_paragrafo:
                        self._dados_paragrafo_continuo = dados_paragrafo
                        return dados_paragrafo['nome']

                    if nome_funcionario_texto and ' ' in nome_funcionario_texto and len(nome_funcionario_texto.split()) >= 2:
                        nome_limpo = re.sub(r'^NOME:\s*', '', nome_funcionario_texto, flags=re.IGNORECASE).strip()
                        if nome_limpo:
                            logging.info(f"Nome encontrado: {nome_limpo}")
                            return nome_limpo
                            
                except Exception:
                    continue
            return ""
        except Exception as e:
            logging.error(f"Erro ao buscar nome do servidor: {e}")
            return ""

    def buscar_matricula(self):
        try:
            if hasattr(self, '_dados_paragrafo_continuo') and 'matricula' in self._dados_paragrafo_continuo:
                matricula = self._dados_paragrafo_continuo['matricula']
                logging.info(f"Matrícula encontrada em parágrafo contínuo: {matricula}")
                return matricula
            
            for xpath in self.config.XPATH_MATRICULA:
                try:
                    matricula_elemento = self.web_driver.driver.find_element(By.XPATH, xpath)
                    matricula = matricula_elemento.text.strip()
                
                    matricula = re.sub(r'^MATR[IÍ]CULA:\s*', '', matricula, flags=re.IGNORECASE).strip()
                    
                    if matricula and matricula.isdigit() and len(matricula) >= 6:
                        logging.info(f"Matrícula encontrada: {matricula}")
                        return matricula
                except Exception:
                    continue
            return ""
        except Exception as e:
            logging.error(f"Erro ao buscar matrícula: {e}")
            return ""

    def buscar_cargo(self):
        try:
            if hasattr(self, '_dados_paragrafo_continuo') and 'cargo' in self._dados_paragrafo_continuo:
                cargo = self._dados_paragrafo_continuo['cargo']
                logging.info(f"Cargo encontrado em parágrafo contínuo: {cargo}")
                return cargo

            for xpath in self.config.XPATH_CARGO:
                try:
                    cargo_elemento = self.web_driver.driver.find_element(By.XPATH, xpath)
                    texto_cargo = cargo_elemento.text.strip()
                    
                    cargo = re.sub(r'^CARGO:\s*', '', texto_cargo, flags=re.IGNORECASE).strip()
                    
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
            if hasattr(self, '_dados_paragrafo_continuo') and 'lotacao' in self._dados_paragrafo_continuo:
                lotacao = self._dados_paragrafo_continuo['lotacao']
                logging.info(f"Lotação encontrada em parágrafo contínuo: {lotacao}")
                return lotacao

            for xpath in self.config.XPATH_LOTACAO:
                try:
                    lotacao_elemento = self.web_driver.driver.find_element(By.XPATH, xpath)
                    texto_lotacao = lotacao_elemento.text.strip()

                    lotacao = re.sub(r'^LOTA[ÇC][ÃA]O:\s*', '', texto_lotacao, flags=re.IGNORECASE).strip()
                    
                    if lotacao and len(lotacao) > 3:
                        logging.info(f"Lotação encontrada: {lotacao}")
                        return lotacao
                except Exception:
                    continue
            return ""
        except Exception as e:
            logging.error(f"Erro ao buscar lotação: {e}")
            return ""

    def limpar_dados_paragrafo_continuo(self):
        if hasattr(self, '_dados_paragrafo_continuo'):
            delattr(self, '_dados_paragrafo_continuo')

    
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
                            return data_encontrada
                        
                        match_simples = re.search(padrao_data, texto)
                        if match_simples:
                            data_encontrada = match_simples.group(0)
                            return data_encontrada
            except Exception:
                continue
        
        logging.warning("Nenhuma data encontrada")
        return ""
    
    def calculo_data(self):
        try:
            data_encontrada = self.buscar_data()
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
                logging.warning("Nenhuma data encontrada para cálculo.")
                return ""
        except Exception as e:
            logging.error(f"Erro ao calcular data de vencimento: {e}")
            return ""