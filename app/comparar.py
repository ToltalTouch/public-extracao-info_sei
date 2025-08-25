import pandas as pd
import os
import json
import logging
from datetime import datetime

class ComparadorPlanilhas:
    def __init__(self):
        self.servidores_sheet = os.path.join(os.path.dirname(__file__), "excel", "dados_servidores.xlsx")
        self.extraidos_sheet = os.path.join(os.path.dirname(__file__), "excel", "itens_extraidos.xlsx")
        
        self.log_extratos = os.path.join(os.path.dirname(__file__), "logs", "log_extratos.txt")
        
        # Configurar logging
        self.setup_logging()
        
    def setup_logging(self):
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = os.path.join(log_dir, f"comparacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()  # Para mostrar no console também
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("=== INICIANDO COMPARAÇÃO DE PLANILHAS ===")
    
    def extrair_area_principal(self, lotacao):
        if pd.isna(lotacao) or lotacao == '' or str(lotacao).lower() == 'nan':
            return None
            
        lotacao_str = str(lotacao).strip()
        
        # Verificar se tem o padrão ANTT>
        if 'ANTT>' in lotacao_str:
            partes = lotacao_str.split('>')
            if len(partes) >= 2:
                area_principal = partes[1].strip()
                self.logger.debug(f"Lotação completa: {lotacao_str} -> Área principal: {area_principal}")
                return area_principal
        
        # Se não tem o padrão ANTT>, retorna a lotação original
        self.logger.debug(f"Lotação sem padrão ANTT>: {lotacao_str}")
        return lotacao_str
        
    def comparar_planilhas(self):
        self.logger.info("Carregando planilhas...")
        
        df_servidores = pd.read_excel(self.servidores_sheet)
        df_extraidos = pd.read_excel(self.extraidos_sheet, sheet_name="RESULTADO")
        
        self.logger.info(f"Servidores carregados: {len(df_servidores)} registros")
        self.logger.info(f"Itens extraídos: {len(df_extraidos)} registros")
        
        # Debug: Print column names to identify the correct columns
        self.logger.info(f"Colunas em dados_servidores.xlsx: {df_servidores.columns.tolist()}")
        self.logger.info(f"Colunas em itens_extraidos.xlsx (aba RESULTADO): {df_extraidos.columns.tolist()}")
        
        # Check if 'NOME' column exists, if not, try common alternatives
        nome_col_extraidos = None
        possible_nome_cols = ['NOME', 'Nome', 'nome', 'SERVIDOR', 'Servidor', 'servidor']
        
        for col in possible_nome_cols:
            if col in df_extraidos.columns:
                nome_col_extraidos = col
                break
                
        if nome_col_extraidos is None:
            raise ValueError(f"Coluna de nome não encontrada. Colunas disponíveis: {df_extraidos.columns.tolist()}")
        
        # Check for items column - incluindo MATERIAL que vejo na sua planilha
        itens_col_extraidos = None
        possible_itens_cols = ['ITENS', 'Itens', 'itens', 'ITEM', 'Item', 'item', 'MATERIAL', 'Material', 'material']
        
        for col in possible_itens_cols:
            if col in df_extraidos.columns:
                itens_col_extraidos = col
                break
                
        if itens_col_extraidos is None:
            raise ValueError(f"Coluna de itens não encontrada. Colunas disponíveis: {df_extraidos.columns.tolist()}")
        
        self.logger.info(f"Usando coluna de nome: {nome_col_extraidos}")
        self.logger.info(f"Usando coluna de itens: {itens_col_extraidos}")
        
        # Normalizar nomes para comparação
        self.logger.info("Normalizando nomes para comparação...")
        df_servidores['nome_normalizado'] = df_servidores['Nome'].fillna('').astype(str).str.strip().str.lower()
        df_extraidos['nome_normalizado'] = df_extraidos[nome_col_extraidos].fillna('').astype(str).str.strip().str.lower()
        
        # Extrair área principal da lotação
        self.logger.info("Extraindo área principal das lotações...")
        df_servidores['area_principal'] = df_servidores['Lotação'].apply(self.extrair_area_principal)
        
        # Renomear a coluna Lotação nos servidores para evitar conflito
        df_servidores_para_merge = df_servidores[['nome_normalizado', 'Lotação', 'area_principal']].copy()
        df_servidores_para_merge = df_servidores_para_merge.rename(columns={'Lotação': 'Lotacao_Servidor'})
        
        # Fazer merge para trazer a lotação de cada pessoa
        self.logger.info("Fazendo merge entre planilhas...")
        resultado = pd.merge(
            df_extraidos,
            df_servidores_para_merge,
            on='nome_normalizado',
            how='left'
        )
        
        # Carregar dados de uniformes RESTRITOS por área
        self.logger.info("Carregando dados de uniformes RESTRITOS...")
        json_path = os.path.join(os.path.dirname(__file__), "uniforme.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            uniforme_data = json.load(f)
        
        self.logger.info(f"Áreas com restrições no uniforme.json: {list(uniforme_data.keys())}")
        
        # Aplicar validação para cada linha
        self.logger.info("Iniciando validação de itens...")
        resultado['STATUS_ITEM'] = resultado.apply(
            lambda row: self.validar_item_por_area(row, uniforme_data, nome_col_extraidos, itens_col_extraidos), axis=1
        )

        # Estatísticas do resultado
        status_counts = resultado['STATUS_ITEM'].value_counts()
        self.logger.info("=== ESTATÍSTICAS DO RESULTADO ===")
        for status, count in status_counts.items():
            self.logger.info(f"{status}: {count} registros")

        # Limpar colunas temporárias
        resultado = resultado.drop(['nome_normalizado'], axis=1)
        
        # Salvar o resultado de volta na aba RESULTADO
        self.logger.info("Salvando resultado...")
        with pd.ExcelWriter(self.extraidos_sheet, mode='a', if_sheet_exists='replace') as writer:
            resultado.to_excel(writer, sheet_name='RESULTADO', index=False)
        
        self.logger.info("=== COMPARAÇÃO CONCLUÍDA COM SUCESSO ===")
        return resultado
    
    def validar_item_por_area(self, row, uniforme_data, nome_col, itens_col):
        try:
            nome = str(row[nome_col]).strip()
            lotacao_completa = row.get('Lotacao_Servidor')
            area_principal = row.get('area_principal')
            item = str(row[itens_col]).upper().strip()
            
            self.logger.debug(f"Validando: {nome} | Lotação completa: {lotacao_completa} | Área principal: {area_principal} | Item: {item}")
            
            # Verificar se a pessoa foi encontrada (tem lotação)
            if pd.isna(area_principal) or area_principal == '' or str(area_principal).lower() == 'nan':
                self.logger.warning(f"Servidor não encontrado ou área não identificada: {nome}")
                return f"❓ SERVIDOR NÃO ENCONTRADO: {nome}"
            
            # Verificar se a área principal tem restrições no uniforme.json
            if area_principal not in uniforme_data:
                # Se a área não está no JSON, significa que NÃO tem restrições, então TUDO é permitido
                self.logger.info(f"✅ AUTORIZADO: {nome} | {item} | Área: {area_principal} | Sem restrições")
                return f"✅ AUTORIZADO para {area_principal} (sem restrições)"
            
            # A área TEM restrições, vamos verificar se o item está na lista de RESTRITOS
            itens_restritos = uniforme_data[area_principal]
            self.logger.debug(f"Itens RESTRITOS para {area_principal}: {itens_restritos}")
            
            # Verificar se o item solicitado está na lista de RESTRITOS
            item_restrito = False
            item_encontrado = None
            
            if isinstance(itens_restritos, list):
                # Se for lista, verificar cada item restrito
                for item_restrito_config in itens_restritos:
                    if self.item_match(item_restrito_config, item):
                        item_restrito = True
                        item_encontrado = item_restrito_config
                        break
            else:
                # Se for string, dividir por vírgula e verificar
                for item_restrito_config in str(itens_restritos).split(','):
                    if self.item_match(item_restrito_config.strip(), item):
                        item_restrito = True
                        item_encontrado = item_restrito_config.strip()
                        break
            
            if item_restrito:
                # Item está na lista de restritos, então NÃO é permitido
                self.logger.info(f"❌ NÃO AUTORIZADO: {nome} | {item} | Área: {area_principal} | Item restrito: {item_encontrado}")
                return f"❌ NÃO AUTORIZADO para {area_principal} (item restrito)"
            else:
                # Item NÃO está na lista de restritos, então É permitido
                self.logger.info(f"✅ AUTORIZADO: {nome} | {item} | Área: {area_principal} | Item não restrito")
                return f"✅ AUTORIZADO para {area_principal}"
               
        except Exception as e:
            self.logger.error(f"Erro ao validar item para {nome}: {e}")
            return f"❓ ERRO: {str(e)}"
    
    def item_match(self, item_permitido, item_solicitado):
        item_permitido_upper = item_permitido.upper().strip()
        item_solicitado_upper = item_solicitado.upper().strip()
        
        match = (item_permitido_upper in item_solicitado_upper or 
                item_solicitado_upper in item_permitido_upper)
        
        if match:
            self.logger.debug(f"Match encontrado: '{item_permitido}' <-> '{item_solicitado}'")
        
        return match
        
if __name__ == "__main__":
    comparador = ComparadorPlanilhas()
    resultado = comparador.comparar_planilhas()