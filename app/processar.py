from dataclasses import dataclass
from selenium.webdriver.common.by import By
import logging
import re

from app.limpar_texto import LimparMatricula, LimparTexto, LimparQuantidade
from app.config import Config

@dataclass
class ProcessarGeneroTamanho:
    config = Config()
    def processar_tamanho_genero(self, texto_tamanho):
        if not texto_tamanho:
            return "", ""
        
        texto = texto_tamanho.strip().upper()
    
        tamanho = ""
        genero = ""
        
        partes = re.split(r'[\s/\-]+', texto)
        partes = [p.strip() for p in partes if p.strip()]
        
        if len(partes) == 1 and partes[0] == 'M':
            tamanho = 'M'
            genero = ''
            return tamanho, genero
        
        elif len(partes) == 2 and partes[0] == 'M' and partes[1] == 'M':
            tamanho = 'M'
            genero = 'MASCULINO'
            return tamanho, genero
            
        elif len(partes) == 2 and partes[0] == 'F' and partes[1] == 'F':
            tamanho = 'F'
            genero = 'FEMININO'
            return tamanho, genero
        
        ms_encontrados = 0
        fs_encontrados = 0
        
        for parte in partes:
            if parte == 'M':
                ms_encontrados += 1
            elif parte == 'F':
                fs_encontrados += 1
                
            if parte in ['MASC', 'FEM', 'MASCULINO', 'FEMININO', 'UNISSEX', 'UNI']:
                genero = self.config.CONVERCAO_GENERO[parte]
            elif parte.isdigit() and 34 <= int(parte) <= 60:
                tamanho = parte
            elif parte in ['PP', 'P', 'G', 'GG', 'XG', 'XXG', 'XXXG']:
                tamanho = parte
            elif any(g in parte for g in ['MASCULINO', 'FEMININO', 'MASC', 'FEM']) and parte not in ['M', 'F']:
                for abrev, completo in self.config.CONVERCAO_GENERO.items():
                    if abrev in parte and abrev not in ['M', 'F']:
                        genero = completo
                        break
        
        if ms_encontrados == 1 and not tamanho and not genero:
            tamanho = 'M'
        elif ms_encontrados == 2:
            tamanho = 'M'
            genero = 'MASCULINO'
        elif ms_encontrados == 1 and genero:
            tamanho = 'M'
        elif ms_encontrados == 1 and tamanho:
            genero = 'MASCULINO'
            
        if fs_encontrados == 1 and not tamanho and not genero:
            tamanho = 'F'
        elif fs_encontrados == 2:
            tamanho = 'F'
            genero = 'FEMININO'
        elif fs_encontrados == 1 and genero == '':
            genero = 'FEMININO'
        elif fs_encontrados == 1 and tamanho:
            genero = 'FEMININO'
        
        if not genero:
            texto_original = texto_tamanho.upper()
            if any(ind in texto_original for ind in ['MASCULINO', 'MASC']) and 'M' not in partes:
                genero = 'MASCULINO'
            elif any(ind in texto_original for ind in ['FEMININO', 'FEM']) and 'F' not in partes:
                genero = 'FEMININO'
        
        return tamanho, genero
    
    def __call__(self, texto_tamanho):
        return self.processar_tamanho_genero(texto_tamanho)
    
@dataclass
class ProcessarCabecalho:
    def __init__(self):
        self.config = Config()
        self.limpar_matricula = LimparMatricula()
        self.limpar_texto = LimparTexto()
        self.limpar_quantidade = LimparQuantidade()
        self.processar_tamanho_genero = ProcessarGeneroTamanho()

    def extrair_item_da_linha(self, colunas, mapeamento, secao=1):
        try:
            if secao == 1:
                idx_material = mapeamento.get('material')
                idx_quantidade = mapeamento.get('quantidade')
                idx_modelo = mapeamento.get('modelo')
                idx_tamanho = mapeamento.get('tamanho')
            else:
                idx_material = mapeamento.get('material2')
                idx_quantidade = mapeamento.get('quantidade2')
                idx_modelo = mapeamento.get('modelo')
                idx_tamanho = mapeamento.get('tamanho')

            if idx_material is None or idx_quantidade is None:
                return None
            
            quantidade_list = []
            tamanho_genero_list = []
            material = colunas[idx_material].text.strip() if idx_material < len(colunas) else ""
            modelo = colunas[idx_modelo].text.strip() if idx_modelo is not None and idx_modelo < len(colunas) else ""
            
            if idx_quantidade is not None and idx_quantidade < len(colunas):
                quantidade_td = colunas[idx_quantidade]
                quantidade_ps = quantidade_td.find_elements(By.TAG_NAME, "p")
                if quantidade_ps:
                    for p in quantidade_ps:
                        texto = p.text.strip()
                        match = re.match(r'(\d+)/(\d+)', texto)
                        if match:
                            quantidade_list.append(self.limpar_quantidade(match.group(1)))
                            tamanho = self.limpar_texto(match.group(2))
                            tamanho_genero_list.append((tamanho, ""))

            if idx_tamanho is not None and idx_tamanho < len(colunas):
                tamanho_td = colunas[idx_tamanho]
                tamanho_ps = tamanho_td.find_elements(By.TAG_NAME, "p")
                if tamanho_ps:
                    for p in tamanho_ps:
                        texto = p.text.strip()
                        # Verifica se tem padrão "quantidade/tamanho"
                        match = re.match(r'(\d+)\s*/\s*([\w]+)', texto)
                        if match:
                            quantidade_list.append(self.limpar_quantidade(match.group(1)))
                            tamanho, genero = self.processar_tamanho_genero(match.group(2))
                            tamanho_genero_list.append((tamanho, genero))
                        else:
                            tamanho, genero = self.processar_tamanho_genero(texto)
                            tamanho_genero_list.append((tamanho, genero))
                else:
                    texto = tamanho_td.text.strip()
                    match = re.match(r'(\d+)\s*/\s*([\w]+)', texto)
                    if match:
                        quantidade_list.append(self.limpar_quantidade(match.group(1)))
                        tamanho, genero = self.processar_tamanho_genero(match.group(2))
                        tamanho_genero_list.append((tamanho, genero))
                    else:
                        tamanho, genero = self.processar_tamanho_genero(texto)
                        tamanho_genero_list.append((tamanho, genero))
            else:
                tamanho_genero_list.append(("", ""))

            # Só processa quantidade separadamente se não veio junto com tamanho
            if not quantidade_list and idx_quantidade is not None and idx_quantidade < len(colunas):
                quantidade_td = colunas[idx_quantidade]
                quantidade_ps = quantidade_td.find_elements(By.TAG_NAME, "p")
                if quantidade_ps:
                    for p in quantidade_ps:
                        quantidade_list.append(self.limpar_quantidade(p.text.strip()))
                else:
                    quantidade_list.append(self.limpar_quantidade(quantidade_td.text.strip()))
            elif not quantidade_list:
                quantidade_list.append("")
            
            if any(palavra in material.upper() for palavra in ['NOME:', 'MATRÍCULA:', 'MATRICULA:', 'CARGO:', 'ASSINATURA', 'DATA']):
                return None

            items = []
            
            for i in range(max(len(tamanho_genero_list), len(quantidade_list))):
                tamanho, genero = tamanho_genero_list[i] if i < len(tamanho_genero_list) else ("", "")
                quantidade = quantidade_list[i] if i < len(quantidade_list) else ""
                
                # Validações antes de criar o item
                if not material or not quantidade:
                    continue
                    
                # Remove itens com quantidade inválida
                if quantidade in ['-', '–', 'N/A', 'NA', '0', '']:
                    continue
                
                item = {
                    'material' : self.limpar_texto(material),
                    'modelo' : self.limpar_texto(modelo) if modelo.upper() not in ["X", "U", "-", "–", "N/A", "NA"] else "",
                    'tamanho' : tamanho,
                    'genero' : genero,
                    'quantidade' : quantidade
                }
                items.append(item)

            # Só loga se realmente extraiu itens
            if items:
                logging.info(f"Itens extraídos (seção {secao}): {len(items)} para material {material}")
            return items if items else None

        except Exception as e:
            logging.error(f"Erro ao extrair item da linha: {e}")
            return None
    def processar_cabecalhos_dinamicos(self, tabela, documento_titulo):
        try:
            todas_linhas = tabela.find_elements(By.XPATH, ".//tr")
            if len(todas_linhas) < 2:
                return []

            primeira_linha = todas_linhas[0]
            cabecalho_elementos = primeira_linha.find_elements(By.XPATH, ".//th|.//td")
            
            if not cabecalho_elementos:
                return []

            mapeamento_colunas = {}
            cabecalhos = []
            
            for i, elemento in enumerate(cabecalho_elementos):
                texto_cabecalho = elemento.text.strip().upper()
                cabecalhos.append(texto_cabecalho)
                
                if any(palavra in texto_cabecalho for palavra in ['MATERIAL', 'ITEM', 'PRODUTO', 'DESCRIÇÃO', 'DESCRICAO']):
                    if 'material' not in mapeamento_colunas:
                        mapeamento_colunas['material'] = i
                    else:
                        mapeamento_colunas['material2'] = i
                elif any(palavra in texto_cabecalho for palavra in ['MODELO', 'TIPO', 'ESPECIFICAÇÃO', 'ESPECIFICACAO']):
                    mapeamento_colunas['modelo'] = i
                elif any(palavra in texto_cabecalho for palavra in ['TAMANHO', 'TAM', 'SIZE', 'GENERO', 'GÊNERO']):
                    mapeamento_colunas['tamanho'] = i
                elif any(palavra in texto_cabecalho for palavra in ['QUANTIDADE', 'QTD', 'QTDE', 'QT', 'Qtd']):
                    if 'quantidade' not in mapeamento_colunas:
                        mapeamento_colunas['quantidade'] = i
                    else:
                        mapeamento_colunas['quantidade2'] = i

            if 'material' not in mapeamento_colunas or 'quantidade' not in mapeamento_colunas:
                logging.warning("Não foi possível identificar colunas de material e quantidade")
                return []

            itens_extraidos = []

            for linha_idx in range(1, len(todas_linhas)):
                linha = todas_linhas[linha_idx]
                colunas = linha.find_elements(By.TAG_NAME, "td")
                
                if not colunas or len(colunas) < max(mapeamento_colunas.values()) + 1:
                    continue

                item = self.extrair_item_da_linha(colunas, mapeamento_colunas, secao=1)
                if item:
                    if isinstance(item, list):
                        itens_extraidos.extend(item)
                    else:
                        itens_extraidos.append(item)

                if 'material2' in mapeamento_colunas and 'quantidade2' in mapeamento_colunas:
                    item2 = self.extrair_item_da_linha(colunas, mapeamento_colunas, secao=2)
                    if item2:
                        if isinstance(item2, list):
                            itens_extraidos.extend(item2)
                        else:
                            itens_extraidos.append(item2)

            logging.info(f"Total de itens extraídos da tabela: {len(itens_extraidos)}")
            return itens_extraidos

        except Exception as e:
            logging.error(f"Erro ao processar tabela com cabeçalhos dinâmicos: {e}")
            return []
        
    def __call__(self, tabela, documento_titulo):
        return self.processar_cabecalhos_dinamicos(tabela, documento_titulo)