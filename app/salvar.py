import re
import logging
from selenium.webdriver.common.by import By

from app.login_sei import SeiLogin
from app.config import Config

from app.limpar_texto import LimparMatricula, LimparTexto, LimparQuantidade
from app.processar import ProcessarGeneroTamanho, ProcessarCabecalho

    
class Salvar:
    def __init__(self, web_driver):
        self.web_driver = web_driver or SeiLogin()
        self.config = Config()
        
        self.limpar_matricula = LimparMatricula()
        self.limpar_texto = LimparTexto()
        self.limpar_quantidade = LimparQuantidade()
        
        self.processar_tamanho_genero = ProcessarGeneroTamanho()
        self.processar_cabecalhos = ProcessarCabecalho()
        
        if web_driver is None:
            self.web_driver.setup_webdriver()        
        
    def save_to_excel(self, process_number, documento_titulo, nome_funcionario, matricula, cargo, lotacao, data_encontrada, data_vencimento_str, processo_itens_extraidos):
        try:
            nome_funcionario = self.limpar_texto(nome_funcionario)
            matricula = self.limpar_matricula(matricula)
            cargo = self.limpar_texto(cargo)
            lotacao = self.limpar_texto(lotacao)
            documento_titulo = self.limpar_texto(documento_titulo)
            
            tabela_encontrada = False
            try:
                todas_tabelas = self.web_driver.driver.find_elements(By.XPATH, "//table")
                logging.info(f"Processando {len(todas_tabelas)} tabela(s) para documento: {documento_titulo}")
                
                for idx_tabela, tabela in enumerate(todas_tabelas):
                    try:
                        texto_tabela = tabela.text.lower()
                        tem_material = any(palavra in texto_tabela for palavra in self.config.MATERIAIS_INDICADORES)
                        
                        palavras_admin = ['data de emissão', 'responsável', 'assinatura', 'rubrica', 'campo', 'valor']
                        e_admin = any(palavra in texto_tabela for palavra in palavras_admin)
                        
                        if not tem_material or e_admin:
                            continue
                        
                        todas_linhas = tabela.find_elements(By.XPATH, ".//tr")
                        if len(todas_linhas) < 2:
                            continue

                        itens_tabela_extraidos = self.processar_cabecalhos(tabela, documento_titulo)

                        if itens_tabela_extraidos:
                            for item in itens_tabela_extraidos:
                                item_info = {
                                    'PROCESSO': process_number,
                                    'NOME ARQUIVO': documento_titulo,
                                    'NOME': nome_funcionario,
                                    'MATRICULA': matricula,
                                    'CARGO': cargo,
                                    'LOTACAO': lotacao,
                                    'MATERIAL': item.get('material', ''),
                                    'MODELO': item.get('modelo', ''),
                                    'TAMANHO': item.get('tamanho', ''),
                                    'GENERO': item.get('genero', ''),
                                    'QUANTIDADE': item.get('quantidade', ''),
                                    'DATA': data_encontrada,
                                    'DATA VENCIMENTO': data_vencimento_str
                                }
                                processo_itens_extraidos.append(item_info)
                            tabela_encontrada = True
                            logging.info(f"Tabela processada com sucesso: {len(itens_tabela_extraidos)} itens extraídos")
                            break
                        else:
                            logging.info(f"Tabela {idx_tabela + 1} não gerou itens válidos")
                            
                    except Exception as e:
                        logging.error(f"Erro ao processar tabela {idx_tabela + 1}: {e}")
                        continue
                        
            except Exception as e:
                logging.warning(f"Erro ao buscar tabelas: {e}")
            
            if not tabela_encontrada:
                logging.info(f"Nenhuma tabela de materiais encontrada para: {documento_titulo}")
            
            def e_dado_funcionario_valido(texto):
                if not texto:
                    return False
                texto_limpo = texto.strip()
                return (texto_limpo and 
                    texto_limpo != "-" and 
                    len(texto_limpo) >= 2 and
                    not texto_limpo.lower() in ['n/a', 'na', 'não informado'])
            
            if not tabela_encontrada:
                dados_validos = [
                    e_dado_funcionario_valido(nome_funcionario),
                    e_dado_funcionario_valido(matricula),
                    e_dado_funcionario_valido(cargo),
                    e_dado_funcionario_valido(lotacao)
                ]
                
                if any(dados_validos):
                    info_basica = {
                        'PROCESSO': process_number,
                        'NOME ARQUIVO': documento_titulo,
                        'NOME': nome_funcionario if e_dado_funcionario_valido(nome_funcionario) else "",
                        'MATRICULA': matricula if e_dado_funcionario_valido(matricula) else "",
                        'CARGO': cargo if e_dado_funcionario_valido(cargo) else "",
                        'LOTACAO': lotacao if e_dado_funcionario_valido(lotacao) else "",
                        'MATERIAL': "",
                        'MODELO': "",
                        'TAMANHO': "",
                        'GENERO': "",
                        'QUANTIDADE': "",
                        'DATA': data_encontrada,
                        'DATA VENCIMENTO': data_vencimento_str
                    }
                    processo_itens_extraidos.append(info_basica)
                    logging.info(f"Dados básicos salvos para: {nome_funcionario}")
                else:
                    logging.info(f"Processo {process_number} ignorado - nenhum dado válido encontrado")
                   
            if processo_itens_extraidos:
                processo_itens_extraidos = self.aplicar_preenchimento_inteligente(processo_itens_extraidos) 
                            
        except Exception as e:
            logging.error(f"Erro ao processar {process_number}: {e}")
            
        finally:
            try:
                self.web_driver.driver.switch_to.default_content()
            except:
                pass
    
    def aplicar_preenchimento_inteligente(self, processo_itens_extraidos):
        """Aplica preenchimento inteligente para completar dados - padroniza todos os itens do processo"""
        try:
            if not processo_itens_extraidos:
                return processo_itens_extraidos
                
            item_completo = None
            for item in processo_itens_extraidos:
                if (item.get('NOME') and item.get('MATRICULA') and 
                    item.get('CARGO') and item.get('LOTACAO')):
                    item_completo = item
                    break
            
            if not item_completo:
                logging.warning("Nenhum item completo encontrado para padronização")
                return processo_itens_extraidos
            
            logging.info(f"Item completo encontrado - padronizando {len(processo_itens_extraidos)} itens do processo")
            
            for item in processo_itens_extraidos:
                item['NOME'] = item_completo.get('NOME', '')
                item['MATRICULA'] = item_completo.get('MATRICULA', '')
                item['CARGO'] = item_completo.get('CARGO', '')
                item['LOTACAO'] = item_completo.get('LOTACAO', '')
                item['PROCESSO'] = item_completo.get('PROCESSO', '')
                            
            logging.info(f"Padronização concluída - todos os itens agora têm dados consistentes")
            return processo_itens_extraidos
            
        except Exception as e:
            logging.error(f"Erro no preenchimento inteligente: {e}")
            return processo_itens_extraidos