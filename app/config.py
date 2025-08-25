import os
import logging
import pandas as pd
from datetime import datetime

class Config:
    def __init__(self):
        self.COLUNAS = ["PROCESSO", "NOME ARQUIVO", "NOME", "MATRICULA", "CARGO", "LOTACAO", "MATERIAL", "MODELO", "TAMANHO", "GENERO", "QUANTIDADE", "DATA", "DATA VENCIMENTO"]
        
        self.XPATH_PESQUISA = [
            "//input[@id='txtPesquisaRapida']",
            "//input[@name='txtPesquisaRapida']", 
            "//input[@placeholder='Pesquisar...']",
            "//input[@class='form-control' and contains(@placeholder, 'Pesquis')]",
            "//input[contains(@id, 'txtPesquisa')]",
            "//input[@type='text' and contains(@style, 'width:190px')]"
            ]
        
        self.XPATH_NOME = [
            "//td[p[@class='Texto_Justificado' and normalize-space(.) = 'NOME:']]/following-sibling::td[1]/p[@class='Texto_Justificado']",
            "//td[contains(normalize-space(.), 'NOME:')]/following-sibling::td[1]//p",
            "//td[contains(normalize-space(.), 'NOME:')]/following-sibling::td//span",
            "//p[contains(normalize-space(.), 'NOME:')]/following-sibling::p[1]",
            "//span[contains(normalize-space(.), 'NOME:')]/following-sibling::span[1]",
            "//tr[td[contains(., 'NOME:')]]/td[2]//p",
            "//tr[td[contains(., 'NOME:')]]/td[2]//span",
            "//tr[td[contains(., 'NOME:')]]/td[last()]//span",
            "//*[contains(text(), 'Eu,') and contains(text(), 'matrícula')]",
            "//*[contains(text(), 'Eu') and contains(text(), ', matrícula')]"
            ]
        
        self.XPATH_DATA = [
            "//div[@unselectable='on']",
            "//*[contains(text(), 'Criado por') and contains(text(), 'versão')]",
            "//*[contains(text(), 'em ') and contains(text(), '/')]",
            "//*[contains(text(), '/') and contains(text(), ':')]",
            "//div[.//a[@onclick]]"
            ]
        
        self.TIPO_DOCUMENTO = [
            'Termo', 'Solicitação', 'Recebimento', 'Equipamento', 'Material',
            'Termo Solicitação', 'Termo Recebimento', 'Termo Equipamento', 'Termo Material',
            'Solicitação Recebimento', 'Solicitação Equipamento', 'Solicitação Material',
            'Recebimento Equipamento', 'Recebimento Material',
            'Equipamento Material',
            'Termo Bens', 'Solicitação Bens', 'Recebimento Bens', 'Equipamento Bens', 'Material Bens',
            'Termo Solicitação Bens', 'Termo Recebimento Bens', 'Termo Equipamento Bens', 'Termo Material Bens',
            'Solicitação Recebimento Bens', 'Solicitação Equipamento Bens', 'Solicitação Material Bens',
            'Recebimento Equipamento Bens', 'Recebimento Material Bens',
            'Equipamento Material Bens',
            'Termo de Solicitação', 'Termo de Recebimento', 'Termo de Equipamento', 'Termo de Material',
            'Solicitação de Recebimento', 'Solicitação de Equipamento', 'Solicitação de Material',
            'Recebimento de Equipamento', 'Recebimento de Material',
            'Equipamento de Material',
            'Termo de Bens', 'Solicitação de Bens', 'Recebimento de Bens', 'Equipamento de Bens', 'Material de Bens',
            'Termo de Solicitação de Bens', 'Termo de Recebimento de Bens', 'Termo de Equipamento de Bens',
            'Solicitação de Recebimento de Bens', 'Solicitação de Equipamento de Bens',
            'Recebimento de Equipamento de Bens',
            'Bens', 'Uso Individual', 'Individual', 'Uniforme', 'EPI',
            'Termo Uso Individual', 'Solicitação Uso Individual', 'Recebimento Uso Individual',
            'Termo de Uso Individual', 'Solicitação de Uso Individual', 'Recebimento de Uso Individual'
            ]
        
        self.XPATH_MATRICULA = [
            "//td[p[@class='Tabela_Texto_Centralizado' and contains(normalize-space(.), 'MATRÍCULA:')]]/following-sibling::td[1]/p[@class='Tabela_Texto_Alinhado_Esquerda']",
            "//td[p[@class='Texto_Centralizado' and contains(normalize-space(.), 'MATRÍCULA:')]]/following-sibling::td[1]/p[@class='Texto_Centralizado']",
            "//td[p[@class='Tabela_Texto_Centralizado']]",
            "//td[.//span[contains(normalize-space(text()), 'MATRÍCULA:')]]/following-sibling::td[1]//span[normalize-space(text())]",
            "//td[.//p[contains(normalize-space(text()), 'MATRÍCULA:')]]/following-sibling::td[1]//span[normalize-space(text())]",
            "//td[contains(normalize-space(.), 'MATRÍCULA:')]/following-sibling::td[1]//span[normalize-space(text())]",
            "//*[contains(text(), 'MATRÍCULA:')]/following-sibling::*[1]",
            "//*[contains(text(), 'MATRICULA:')]/following-sibling::*[1]",
            "//td[contains(text(), 'MATRÍCULA:')]/following-sibling::td[1]",
            "//td[contains(text(), 'MATRICULA:')]/following-sibling::td[1]",
            "//*[contains(text(), 'MATRÍCULA')]/parent::*/following-sibling::*[1]",
            "//span[normalize-space(text()) and string-length(normalize-space(text())) >= 6 and string-length(normalize-space(text())) <= 8 and number(normalize-space(text()))]",
            "//td//span[matches(normalize-space(text()), '^[0-9]{6,8}$')]",
            "//*[text()[matches(., '^[0-9]{6,8}$')]]",
            "//tr[td[contains(., 'MATRÍCULA')]]/td[2]//span",
            "//tr[td[contains(., 'MATRICULA')]]/td[2]//span",
            "//tr[td[contains(., 'MATRÍCULA')]]/td[last()]//span",
            "//*[contains(text(), 'matrícula SIAPE') and contains(text(), 'nº')]",
            "//*[contains(text(), 'matrícula SIAPE') and contains(text(), 'n°')]",
            "//*[contains(text(), 'SIAPE nº')]",
            "//*[contains(text(), 'SIAPE n°')]",
            "//*[contains(text(), 'SIAPE -')]"
            ]
        
        self.XPATH_CARGO = [
            "//td[.//span[contains(normalize-space(text()), 'CARGO:')]]/following-sibling::td[1]//span[normalize-space(text())]",
            "//td[.//p[contains(normalize-space(text()), 'CARGO:')]]/following-sibling::td[1]//span[normalize-space(text())]",
            "//td[contains(normalize-space(.), 'CARGO:')]/following-sibling::td[1]//span[normalize-space(text())]",
            "//p[@class='Tabela_Texto_Centralizado'][.//span[contains(normalize-space(text()), 'CARGO:')]]/parent::td/following-sibling::td[1]//span",
            "//*[contains(text(), 'CARGO:')]/following-sibling::*[1]",
            "//td[contains(text(), 'CARGO:')]/following-sibling::td[1]",
            "//*[contains(text(), 'CARGO')]/parent::*/following-sibling::*[1]",
            "//tr[td[contains(., 'CARGO')]]/td[2]//span",
            "//tr[td[contains(., 'CARGO:')]]/td[2]//span",
            "//tr[td[contains(., 'CARGO')]]/td[last()]//span",
            "//td[contains(normalize-space(.), 'CARGO:')]/following-sibling::td[1]//p",
            "//td[contains(normalize-space(.), 'CARGO:')]/following-sibling::td[1]//*[normalize-space(text())]",
            "//*[contains(text(), 'CARGO:')]",
            "//*[contains(text(), 'ocupante do cargo de') and contains(text(), ', lotad')]",
            "//*[contains(text(), 'cargo de')]"
            ]
        
        self.XPATH_LOTACAO = [
            "//td[.//span[contains(normalize-space(text()), 'LOTAÇÃO:')]]/following-sibling::td[1]//span[normalize-space(text())]",
            "//td[.//p[contains(normalize-space(text()), 'LOTAÇÃO:')]]/following-sibling::td[1]//span[normalize-space(text())]",
            "//td[contains(normalize-space(.), 'LOTAÇÃO:')]/following-sibling::td[1]//span[normalize-space(text())]",
            "//td[.//span[contains(normalize-space(text()), 'LOTACAO:')]]/following-sibling::td[1]//span[normalize-space(text())]",
            "//td[.//p[contains(normalize-space(text()), 'LOTACAO:')]]/following-sibling::td[1]//span[normalize-space(text())]",
            "//td[contains(normalize-space(.), 'LOTACAO:')]/following-sibling::td[1]//span[normalize-space(text())]",
            "//p[@class='Tabela_Texto_Centralizado'][.//span[contains(normalize-space(text()), 'LOTAÇÃO:')]]/parent::td/following-sibling::td[1]//span",
            "//p[@class='Tabela_Texto_Centralizado'][.//span[contains(normalize-space(text()), 'LOTACAO:')]]/parent::td/following-sibling::td[1]//span",
            "//*[contains(text(), 'LOTAÇÃO:')]/following-sibling::*[1]",
            "//*[contains(text(), 'LOTACAO:')]/following-sibling::*[1]",
            "//td[contains(text(), 'LOTAÇÃO:')]/following-sibling::td[1]",
            "//td[contains(text(), 'LOTACAO:')]/following-sibling::td[1]",
            "//*[contains(text(), 'LOTAÇÃO')]/parent::*/following-sibling::*[1]",
            "//*[contains(text(), 'LOTACAO')]/parent::*/following-sibling::*[1]",
            "//tr[td[contains(., 'LOTAÇÃO')]]/td[2]//span",
            "//tr[td[contains(., 'LOTACAO')]]/td[2]//span",
            "//tr[td[contains(., 'LOTAÇÃO:')]]/td[2]//span",
            "//tr[td[contains(., 'LOTACAO:')]]/td[2]//span",
            "//tr[td[contains(., 'LOTAÇÃO')]]/td[last()]//span",
            "//tr[td[contains(., 'LOTACAO')]]/td[last()]//span",
            "//td[contains(normalize-space(.), 'LOTAÇÃO:')]/following-sibling::td[1]//p",
            "//td[contains(normalize-space(.), 'LOTACAO:')]/following-sibling::td[1]//p",
            "//td[contains(normalize-space(.), 'LOTAÇÃO:')]/following-sibling::td[1]//*[normalize-space(text())]",
            "//td[contains(normalize-space(.), 'LOTACAO:')]/following-sibling::td[1]//*[normalize-space(text())]",
            "//*[contains(text(), 'LOTAÇÃO:')]",
            "//*[contains(text(), 'LOTACAO:')]",
            "//*[contains(text(), 'lotad') and contains(text(), 'no ')]",
            "//*[contains(text(), 'lotada no')]",
            "//*[contains(text(), 'lotado no')]"
            ]
        
        self.MATRICULA_PATTERNS = [
                r'matrícula\s*SIAPE\s*n[°º]\s*(\d+)',
                r'matrícula\s*SIAPE\s*nº\s*(\d+)',
                r'matrícula\s*SIAPE\s*(\d+)',
                r'SIAPE\s*n[°º]\s*(\d+)',
                r'SIAPE\s*nº\s*(\d+)'
            ]
        
        self.CARGO_PATTERNS = [
                r'ocupante\s*do\s*cargo\s*de\s*(.+?),\s*lotad[oa]',
                r'cargo\s*de\s*(.+?),\s*lotad[oa]',
                r'ocupante\s*do\s*cargo\s*de\s*(.+?),'
            ]
        
        self.LOTACAO_PATTERNS = [
                r'lotad[oa]\s*n[oa]\s*(.+?),\s*atesto',
                r'lotad[oa]\s*n[oa]\s*(.+?)[\.,]',
                r'lotad[oa]\s*n[oa]\s*(.+)'
            ]
        
        # Listas de validação para dados de funcionários
        self.PALAVRAS_REJEITADAS = [
            'MATRICULA', 'CARGO', 'LOTACAO', 'NOME', 'SERVIDOR', 'QTD', 'QUANTIDADE'
        ]
        
        self.VALORES_INVALIDOS = [
            '', ' ', 'N/A', 'NA', 'NAO INFORMADO', 'VAZIO', '-', '–'
        ]
        
        # Indicadores para busca de tabelas de materiais
        self.MATERIAIS_INDICADORES = [
            'agasalho', 'bota', 'camisa', 'calça', 'boné', 'colete', 'cinto',
            'uniforme', 'material', 'equipamento'
        ]
        
        self.PREFIXOS_MATRICULA = [
            'SIAPE - ',
            'SIAPE: ',
            'SIAPE -',
            'SIAPE:',
            'SIAPE',
            'MATRÍCULA - ',
            'MATRÍCULA: ',
            'MATRICULA - ',
            'MATRICULA: ',
            'MATRÍCULA -',
            'MATRICULA -',
            'MATRÍCULA:',
            'MATRICULA:',
            'MATRÍCULA',
            'MATRICULA',
            'MATRICULA: SIAPE - ',
            'MATRICULA: SIAPE -'
            ]
        
        self.CONVERCAO_GENERO = {
            'M': 'MASCULINO',
            'F': 'FEMININO',
            'MASC': 'MASCULINO',
            'FEM': 'FEMININO',
            'MASCULINO': 'MASCULINO',
            'FEMININO': 'FEMININO',
            'UNISSEX': 'UNISSEX',
            'UNI': 'UNISSEX'
        }
        
        # XPath para busca de tabelas de materiais
        self.XPATH_TABELAS_MATERIAIS = (
            "//table[.//th[contains(translate(text(), 'ÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛ', 'AEIOUAEIOUAEIOU'), 'MATERIAL')] or " +
            ".//td[contains(translate(text(), 'ÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛ', 'AEIOUAEIOUAEIOU'), 'MATERIAL')] or " +
            ".//th[contains(translate(text(), 'ÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛ', 'AEIOUAEIOUAEIOU'), 'QTD')] or " +
            ".//td[contains(translate(text(), 'ÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛ', 'AEIOUAEIOUAEIOU'), 'QTD')] or " +
            "contains(translate(text(), 'ÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛ', 'AEIOUAEIOUAEIOU'), 'CAMISA') or " +
            "contains(translate(text(), 'ÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛ', 'AEIOUAEIOUAEIOU'), 'CALCA') or " +
            "contains(translate(text(), 'ÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛ', 'AEIOUAEIOUAEIOU'), 'BOTA') or " +
            "contains(translate(text(), 'ÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛ', 'AEIOUAEIOUAEIOU'), 'BONE') or " +
            "contains(translate(text(), 'ÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛ', 'AEIOUAEIOUAEIOU'), 'COLETE') or " +
            "contains(translate(text(), 'ÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛ', 'AEIOUAEIOUAEIOU'), 'UNIFORME')]"
        )
        
        # Configurações para validação de campos
        self.TAMANHO_MINIMO_CAMPO = 2
        self.TAMANHO_MINIMO_CAMPO_QUANTIDADE = 1
        
        # Inicializar variáveis que podem ser usadas por outras funções
        self.atual_dir = None
        self.excel_path = None
        self.log_file = None
        self.df = None
        self.process_numbers = []
       
    def configure_excel(self, base_dir=None):
        """Configura caminhos e carrega dados do Excel"""
        try:
            self.atual_dir = base_dir or os.getcwd()
            excel_dir = os.path.join(self.atual_dir, 'excel')
            
            # Criar diretório excel se não existir
            os.makedirs(excel_dir, exist_ok=True)
            
            self.excel_path = os.path.join(excel_dir, 'itens_extraidos.xlsx')
            
            # Verificar se arquivo existe antes de tentar ler
            if os.path.exists(self.excel_path):
                self.df = pd.read_excel(self.excel_path, sheet_name='PROCESSO').dropna(subset=['PROCESSO'])
                self.df = self.df[self.df['PROCESSO'].str.strip() != '']  # Remove strings vazias ou com espaços
                self.process_numbers = self.df['PROCESSO'].tolist()
            else:
                # Criar arquivo vazio se não existir
                self.df = pd.DataFrame(columns=self.COLUNAS)
                self.process_numbers = []
                logging.warning(f"Arquivo Excel não encontrado em {self.excel_path}. Será criado quando necessário.")
                
        except Exception as e:
            logging.error(f"Erro ao configurar Excel: {e}")
            self.df = pd.DataFrame(columns=self.COLUNAS)
            self.process_numbers = []
        
        
    def setup_logging(self):
        """Configura o sistema de logging"""
        try:
            # Configurar diretório de logs
            if not self.atual_dir:
                self.atual_dir = os.getcwd()
                
            log_dir = os.path.join(self.atual_dir, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            # Nome do arquivo de log com data
            self.log_file = os.path.join(log_dir, f'sei_extraction_{datetime.now().strftime("%Y%m%d")}.log')
            
            # Configurar logging básico
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                filename=self.log_file,
                filemode='a',
                encoding='utf-8'  # Adicionar encoding para caracteres especiais
            )        
            
            # Adicionar handler para console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            
            # Evitar duplicação de handlers
            logger = logging.getLogger()
            if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
                logger.addHandler(console_handler)
                
            logging.info("Sistema de logging configurado com sucesso")
            
        except Exception as e:
            print(f"Erro ao configurar logging: {e}")