import logging
import os
import time
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException

from app.buscas import Buscas
from app.login_sei import SeiLogin
from app.config import Config
from app.salvar import Salvar

class ExtracaoItensSei:
    def __init__(self, base_dir=None, web_driver=None):
        self.config = Config()
        # Configurar base_dir primeiro
        self.atual_dir = base_dir or os.getcwd()
        
        # Configurar config com base_dir
        self.config.configure_excel(self.atual_dir)
        self.config.setup_logging()
        
        # Configurar web_driver
        self.web_driver = web_driver or SeiLogin()
        if web_driver is None:
            self.web_driver.setup_webdriver()
            
        # Inicializar outras classes
        self.busca = Buscas(self.web_driver, self.config)
        self.salvar = Salvar(self.web_driver)
        
        # Configurar caminhos do Excel
        self.excel_path = self.config.excel_path
        self.df = self.config.df
        self.process_numbers = self.config.process_numbers
    
    def wait_page_load(self):
        try:
            WebDriverWait(self.web_driver.driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == "complete"
            )
            time.sleep(2)
            
            # Buscar caixa de pesquisa
            search_input = self.busca.procurar_caixa_pesquisa()
            if search_input:
                return search_input
            else:
                logging.error("Nenhuma caixa de pesquisa foi encontrada com os XPaths configurados")
                return None
                
        except TimeoutException:
            logging.warning("Timeout aguardando carregamento da página")
            return None
        
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
        # Verificar se arquivo Excel existe, se não, criar
        if not os.path.exists(self.excel_path):
            os.makedirs(os.path.dirname(self.excel_path), exist_ok=True)
            df_cabecalho = pd.DataFrame(columns=self.config.COLUNAS)
            df_cabecalho.to_excel(self.excel_path, index=False, sheet_name='Itens Extraídos')
            logging.info(f"Arquivo Excel criado em: {self.excel_path}")

        for process_number in self.process_numbers:
            processo_itens_extraidos = []
            
            # Inicializar variáveis com valores padrão
            nome_funcionario = ""
            matricula = ""
            cargo = ""
            lotacao = ""
            data_encontrada = ""
            data_vencimento_str = ""
            
            try:
                search_input = self.wait_page_load()
                if not search_input:
                    continue
                
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
                    logging.info(f"Processando {len(termos_encontrados)} termo(s) para o processo {process_number}")

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
                                    frame_visualizacao = WebDriverWait(self.web_driver.driver, 10).until(
                                        EC.presence_of_element_located((By.ID, "ifrVisualizacao"))
                                    )
                                    self.web_driver.driver.switch_to.frame(frame_visualizacao)
                                    time.sleep(1)
                                    
                                    frame_lista = WebDriverWait(self.web_driver.driver, 10).until(
                                        EC.presence_of_element_located((By.ID, "ifrArvoreHtml")) 
                                    )
                                    self.web_driver.driver.switch_to.frame(frame_lista)
                                    time.sleep(1)

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
                                    
                                    logging.info(f"Dados extraídos - Nome: {nome_funcionario}, Matrícula: {matricula}, Cargo: {cargo}, Lotação: {lotacao}")
                                    
                                    # Chamar método correto da classe Salvar
                                    self.salvar.save_to_excel(process_number, documento_titulo, nome_funcionario, matricula, cargo, lotacao, data_encontrada, data_vencimento_str, processo_itens_extraidos)
                                    
                                    # Limpar dados do parágrafo contínuo para próxima iteração
                                    self.busca.limpar_dados_paragrafo_continuo()
                                    
                                except Exception as e:
                                    logging.error(f"Erro ao localizar dados do servidor para o processo {process_number}: {e}")
                                    # Manter valores anteriores ou vazios se primeira iteração
                                    self.salvar.save_to_excel(process_number, documento_titulo, nome_funcionario, matricula, cargo, lotacao, data_encontrada, data_vencimento_str, processo_itens_extraidos)

                        except (Exception, WebDriverException) as e:
                            logging.error(f"Erro ao processar documento {idx+1}: {e}")
                            
                            try:
                                self.web_driver.driver.switch_to.default_content()
                            except:
                                pass
                            continue
                else:
                    logging.info(f"Nenhum termo encontrado para o processo {process_number}")
                    # Mesmo sem termos encontrados, tentar salvar dados básicos se houver
                    if nome_funcionario or matricula or cargo or lotacao:
                        info_basica = {
                            'PROCESSO': process_number,
                            'NOME ARQUIVO': "Documento não encontrado",
                            'NOME': nome_funcionario,
                            'MATRICULA': matricula,
                            'CARGO': cargo,
                            'LOTACAO': lotacao,
                            'MATERIAL': "",
                            'MODELO': "",
                            'TAMANHO/GENERO': "",
                            'QUANTIDADE': "",
                            'DATA': data_encontrada,
                            'DATA VENCIMENTO': data_vencimento_str
                        }
                        processo_itens_extraidos.append(info_basica)
                        
            except (WebDriverException, TimeoutException, Exception, NoSuchElementException) as e:
                logging.error(f"Erro ao processar o número do processo {process_number}: {e}")
                continue
            
            finally:
                try:
                    self.web_driver.driver.switch_to.default_content()
                except:
                    pass
                
                # Aplicar preenchimento inteligente ANTES de salvar
                if processo_itens_extraidos:
                    logging.info(f"Aplicando preenchimento inteligente para processo {process_number}")
                    processo_itens_extraidos = self.salvar.aplicar_preenchimento_inteligente(processo_itens_extraidos)
                
                # Salvar dados no Excel se houver itens extraídos
                if processo_itens_extraidos:
                    try:
                        # Tentar ler planilha existente
                        try:
                            df_existente = pd.read_excel(self.excel_path, sheet_name='RESULTADO')
                        except (FileNotFoundError, ValueError):
                            df_existente = pd.DataFrame(columns=self.config.COLUNAS)
                            
                        df_novos = pd.DataFrame(processo_itens_extraidos)
                        df_final = pd.concat([df_existente, df_novos], ignore_index=True)
                        
                        # Garantir que todas as colunas existam
                        for col in self.config.COLUNAS:
                            if col not in df_final.columns:
                                df_final[col] = ""
                                
                        df_final = df_final[self.config.COLUNAS]
                        
                        # Salvar no Excel
                        with pd.ExcelWriter(self.excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                            df_final.to_excel(writer, index=False, sheet_name='RESULTADO')
                            
                        logging.info(f"Total de {len(processo_itens_extraidos)} itens do processo {process_number} salvos no Excel.")
                        
                    except Exception as e:
                        logging.error(f"Erro ao salvar dados no Excel para processo {process_number}: {e}")
                else:
                    logging.warning(f"Nenhum item foi extraído para o processo {process_number}")
                
                time.sleep(1)
                
        logging.info("Processamento concluído. Verifique o arquivo Excel para os resultados.")