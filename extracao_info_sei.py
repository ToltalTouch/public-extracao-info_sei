import logging
import os
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException

from buscas import Buscas
from login_sei import SeiLogin
from config import Config

class ExtracaoItensSei:
    def __init__(self, base_dir=None, web_driver=None):
        self.config = Config()
        self.web_driver = web_driver or SeiLogin()
        self.busca = Buscas(self.web_driver, self.config)
        
        if web_driver is None:
            self.web_driver.setup_webdriver()

        self.atual_dir = base_dir or os.getcwd()
        self.excel_path = os.path.join(self.atual_dir ,'excel', 'itens_extraidos.xlsx')

        self.df = pd.read_excel(self.excel_path, sheet_name='PROCESSO').dropna(subset=['PROCESSO'])
        self.df = self.df[self.df['PROCESSO'].str.strip() != '']  # Remove strings vazias ou com espaços
        
        self.process_numbers = self.df['PROCESSO'].tolist()
        self.setup_logging()
        
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
    
    def debug_pagina(self):
        try:
            current_url = self.web_driver.driver.current_url
            page_tittle = self.web_driver.driver.tittle
            iframes = self.web_driver.driver.find_elements(By.TAG_NAME, 'iframe')
            inputs = self.web_driver.driver.find_elements(By.TAG_NAME, 'input')
            logging.info(f"{current_url} - {page_tittle} - {iframes} - {inputs}")
            
            for i, input_elem in enumerate(inputs[5:]):
                input_id = input_elem.get_attribute('id')
                input_name = input_elem.get_attribute('name')
                input_class = input_elem.get_attribute('class')
                logging.debug(f"Input {i+1}: ID = {input_id}, Name = {input_name}, Class = {input_class}")
                
        except Exception as e:
            logging.error(f"Erro ao debugar a página: {e}")
    
    def wait_page_load(self):
        try:
            WebDriverWait(self.web_driver.driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == "complete"
            )
            time.sleep(2)
        except TimeoutException:
            logging.warning("Timeout aguardando carregamento da página")
        
        logging.error("Nenhuma caixa de pesquisa foi encontrada com os XPaths configurados")
        return None
    
    def save_to_excel(self, process_number, documento_titulo, nome_funcionario, matricula, cargo, lotacao, data_encontrada, data_vencimento_str, processo_itens_extraidos):
        try:
            linhas_tabela = self.web_driver.driver.find_elements(By.XPATH, "//table//tr[position()>1]")
            for linha in linhas_tabela:
                celulas = linha.find_elements(By.TAG_NAME, 'td')
                if len(celulas) >= 3 and celulas[1].text.strip():
                    material = celulas[0].text.strip()
                    modelo = celulas[1].text.strip()
                    tamanho = celulas[2].text.strip()
                    quantidade = ""

                    if len(celulas) > 3:
                        quantidade = celulas[3].text.strip()
                                        
                        if modelo or tamanho or quantidade:
                            itens_info = {
                                'PROCESSO': process_number,
                                'NOME ARQUIVO': documento_titulo,
                                'NOME': nome_funcionario,
                                'MATRICULA': matricula,
                                'CARGO': cargo,
                                'LOTACAO': lotacao,
                                'MATERIAL': material,
                                'MODELO': modelo,
                                'TAMANHO/GENERO': tamanho,
                                'QUANTIDADE': quantidade,
                                'DATA': data_encontrada,
                                'DATA VENCIMENTO': data_vencimento_str
                            }
                            processo_itens_extraidos.append(itens_info)
                            
        except (Exception,WebDriverException) as e:
            logging.error(f"Erro ao extrair itens do processo {process_number}: {e}")
            self.web_driver.driver.switch_to.default_content()
    
    def filtrar_documentos(self, itens_form):
        documentos_encontrados = []
        
        for item in itens_form:
            texto_item = item.text.strip()
            if texto_item:
                for tipo in self.config.TIPO_DOCUMENTO:
                    if texto_item.lower().startswith(tipo.lower()):
                        documentos_encontrados.append(item)
                        break
        return documentos_encontrados
    
    def encontrar_arquivos(self):
        if not os.path.exists(self.excel_path):
            self.df_cabecalho = pd.DataFrame(columns=self.config.COLUNAS)
            self.df_cabecalho.to_excel(self.excel_path, index=False, sheet_name='Itens Extraídos')
            logging.info(f"Arquivo Excel criado em: {self.excel_path}")

        for process_number in self.process_numbers:
            processo_itens_extraidos = []
            try:
                self.wait_page_load()
                
                search_input = self.busca.procurar_caixa_pesquisa()
                search_input.clear()
                search_input.send_keys(process_number)
                search_input.send_keys(Keys.RETURN)
                
                time.sleep(2)
                
                frame_lista = WebDriverWait(self.web_driver.driver, 10).until(
                    lambda d: d.find_element(By.ID, "ifrArvore")
                )
                self.web_driver.driver.switch_to.frame(frame_lista)
                frm_arvore = WebDriverWait(self.web_driver.driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'frmArvore'))
                )
                itens_form = frm_arvore.find_elements(By.TAG_NAME, 'a')

                termos_encontrados = self.filtrar_documentos(itens_form)
                
                if termos_encontrados:
                    nome_funcionario = ""
                    logging.info(f"Processando termo: {len(termos_encontrados)} para o processo {process_number}")

                for idx, termo in enumerate(termos_encontrados):
                    try:
                        self.web_driver.driver.switch_to.default_content()
                        frame_lista = WebDriverWait(self.web_driver.driver, 10).until(
                            lambda d: d.find_element(By.ID, "ifrArvore")
                        )
                        self.web_driver.driver.switch_to.frame(frame_lista)
                        
                        frm_arvore = WebDriverWait(self.web_driver.driver, 10).until(
                            EC.presence_of_element_located((By.ID, 'frmArvore'))
                        )
                        itens_form_atualizados = frm_arvore.find_elements(By.TAG_NAME, 'a')
                        termos_atualizados = self.filtrar_documentos(itens_form_atualizados)
                        
                        if idx < len(termos_atualizados):
                            documento_titulo = termos_atualizados[idx].text.strip()
                            logging.info(f"Processando documento: {idx+1}/{len(termos_encontrados)} - {documento_titulo}")

                            termos_atualizados[idx].click()
                            
                            time.sleep(1)
                            
                            self.web_driver.driver.switch_to.default_content()
                            try:
                                all_iframes = self.web_driver.driver.find_elements(By.TAG_NAME, 'iframe')
                                for index, iframe_tag in enumerate(all_iframes):
                                    iframe_id = iframe_tag.get_attribute("id")
                                    iframe_name = iframe_tag.get_attribute("name")
                                    logging.debug(f"Iframe {index}: ID = {iframe_id}, Name = {iframe_name}")
                            except Exception as e:
                                logging.error(f"Erro ao listar iframes: {e}")

                            try:
                                frame_visualizacao = WebDriverWait(self.web_driver.driver, 10).until(
                                    EC.presence_of_element_located((By.ID, "ifrVisualizacao"))
                                )
                                self.web_driver.driver.switch_to.frame(frame_visualizacao)

                                frame_lista = WebDriverWait(self.web_driver.driver, 10).until(
                                    EC.presence_of_element_located((By.ID, "ifrArvoreHtml")) 
                                )
                                self.web_driver.driver.switch_to.frame(frame_lista)

                            except (TimeoutException, NoSuchElementException) as e_iframe_switch:
                                logging.error(f"Erro ao alterar frame (ifrVisualizacao ou ifrArvoreHtml): {e_iframe_switch}")
                                continue

                            try:
                                nome_funcionario = self.busca.buscar_nome()
                                matricula = self.busca.buscar_matricula()
                                cargo = self.busca.buscar_cargo()
                                data_encontrada = self.busca.buscar_data()
                                data_vencimento_str = self.busca.calculo_data()
                                lotacao = self.busca.buscar_lotacao()
                                logging.info(f"Nome do servidor encontrado: {nome_funcionario}")
                                self.df.loc[self.df['PROCESSO'] == process_number, 'NOME servidor'] = nome_funcionario
                            except Exception as e:
                                logging.error(f"Erro ao localizar nome do servidor para o processo {process_number}: {e}")

                            self.save_to_excel(process_number, documento_titulo, nome_funcionario, matricula, cargo, lotacao, data_encontrada, data_vencimento_str, processo_itens_extraidos)
                        
                    except (Exception, WebDriverException) as e:
                        logging.error(f"Erro ao processar documento {idx+1}: {e}")
                        
                        try:
                            self.web_driver.driver.switch_to.default_content()
                        except:
                            pass
                        continue
                else:
                    logging.info(f"Mais nenhum termo encontrado para o processo {process_number}")
            except (WebDriverException,TimeoutError, Exception, NoSuchElementException) as e:
                logging.error(f"Erro ao processar o número do processo {process_number}: {e}")
                continue
            
            finally:
                try:
                    self.web_driver.driver.switch_to.default_content()
                except:
                    pass
                
                if processo_itens_extraidos:
                    try:
                        df_existente = pd.read_excel(self.excel_path, sheet_name='RESULTADO')
                    except (FileNotFoundError, ValueError):
                        df_existente = pd.DataFrame(columns=self.config.COLUNAS)
                        
                    df_novos = pd.DataFrame(processo_itens_extraidos)
                    df_final = pd.concat([df_existente, df_novos], ignore_index=True)
                    
                    for col in self.config.COLUNAS:
                        if col not in df_final.columns:
                            df_final[col] = ""
                            
                    df_final = df_final[self.config.COLUNAS]
                    
                    with pd.ExcelWriter(self.excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                        df_final.to_excel(writer, index=False, sheet_name='RESULTADO')
                        
                    logging.info(f"Itens do processo {process_number} salvos no Excel.")
                
                time.sleep(1)
                
        logging.info("Processamento concluído. Verifique o arquivo Excel para os resultados.")