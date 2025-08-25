import re
import unicodedata
from dataclasses import dataclass

from app.config import Config

@dataclass
class LimparMatricula:
    config = Config()
    
    def limpar_matricula(self, texto):
        if not texto or not isinstance(texto, str):
            return ""      
        texto = str(texto).strip().upper()

        self.config.PREFIXOS_MATRICULA.sort(key=len, reverse=True)
        for prefixo in self.config.PREFIXOS_MATRICULA:
            if texto.startswith(prefixo):
                texto = texto[len(prefixo):].strip()
                break
            
        texto_limpo = re.sub(r'[^\d]', '', texto)
            
        return texto_limpo

    def __call__(self, texto):
        return self.limpar_matricula(texto)
    
@dataclass
class LimparTexto:
    config = Config()
    
    def limpar_texto(self, texto):
        if not texto or not isinstance(texto, str):
            return ""
        texto = str(texto).strip()
        texto = texto.upper()
        
        texto_sem_acento = unicodedata.normalize('NFD', texto)
        texto_sem_acento = ''.join(c for c in texto_sem_acento if unicodedata.category(c) != 'Mn')

        texto_limpo = re.sub(r'\s+', ' ', texto_sem_acento)
        texto_limpo = re.sub(r'[^\w\s\-/]', '', texto_limpo)
        
        return texto_limpo
    
    def __call__(self, texto):
        return self.limpar_texto(texto)
    
@dataclass
class LimparQuantidade:
    config = Config()
    
    def limpar_quantidade(self, quantidade):
        if not quantidade or not isinstance(quantidade, str):
            return ""
        quantidade_limpa = quantidade.strip().upper()
        
        valores_ignorados = ['-', '–', '—', 'X', 'N/A', 'NA', '0', 'NULL', 'VAZIO', '']
        
        if quantidade_limpa in valores_ignorados:
            return ""
        numeros = re.sub(r'[^\d]', '', quantidade_limpa)
        
        if not numeros:
            return ""
        quantidade_final = numeros.lstrip('0')
        
        if not quantidade_final:
            return ""
        
        return quantidade_final
    
    def __call__(self, quantidade):
        return self.limpar_quantidade(quantidade)