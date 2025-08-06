class Config:
    def __init__(self):
        self.COLUNAS = ["PROCESSO", "NOME ARQUIVO", "NOME", "MATRICULA", "CARGO", "LOTACAO", "MATERIAL", "MODELO", "TAMANHO/GENERO", "QUANTIDADE", "DATA", "DATA VENCIMENTO"]
        
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
            "//p[@class='Tabela_Texto_Centralizado']//span[contains(@style, 'font-family:Calibri')]//span[normalize-space(text()) and string-length(normalize-space(text())) > 5]",
            "//td[contains(@style, 'border') and contains(@style, 'width')]//p[@class='Tabela_Texto_Alinhado_Esquerda']//span[contains(@style, 'font-family:Calibri') and normalize-space(text()) and string-length(normalize-space(text())) > 3]",
            "//td[contains(@style, 'width')]//p[@class='Texto_Justificado' and normalize-space(text()) and string-length(normalize-space(text())) > 5]",
            "//p[@class='Texto_Justificado' and normalize-space(text()) and string-length(normalize-space(text())) > 10]",
            "//p[@class='Tabela_Texto_Alinhado_Esquerda' and normalize-space(text()) and string-length(normalize-space(text())) > 10]",
            "//p[@class='Tabela_Texto_Centralizado' and normalize-space(text()) and string-length(normalize-space(text())) > 10]",
            "//span[contains(@style, 'font-family:Calibri') and normalize-space(text()) and string-length(normalize-space(text())) > 10]",
            "//span[contains(@style, 'font-family') and normalize-space(text()) and string-length(normalize-space(text())) > 10]",
            "//span[normalize-space(text()) and string-length(normalize-space(text())) > 15 and contains(normalize-space(text()), ' ')]",
            "//td[contains(@style, 'width')]//p[normalize-space(text()) and string-length(normalize-space(text())) > 10]",
            "//td[contains(@style, 'border')]//p[normalize-space(text()) and string-length(normalize-space(text())) > 10]",
            "//td//p[@class='Texto_Justificado' and contains(normalize-space(text()), ' ') and string-length(normalize-space(text())) > 8]",
            "//td[contains(normalize-space(.), 'NOME:')]/following-sibling::td[1]//p",
            "//td[contains(normalize-space(.), 'NOME:')]/following-sibling::td//span",
            "//p[contains(normalize-space(.), 'NOME:')]/following-sibling::p[1]",
            "//span[contains(normalize-space(.), 'NOME:')]/following-sibling::span[1]",
            "//td[position() > 1]//p[@class='Texto_Justificado' and normalize-space(text()) and string-length(normalize-space(text())) > 8]",
            "//tr//td[2]//p[normalize-space(text()) and string-length(normalize-space(text())) > 10]",
            "//tr//td[last()]//p[normalize-space(text()) and string-length(normalize-space(text())) > 10]",
            "//p[contains(normalize-space(text()), ' ') and string-length(normalize-space(text())) > 15]",
            "//span[contains(normalize-space(text()), ' ') and string-length(normalize-space(text())) > 15]",
            "//td//text()[contains(., ' ') and string-length(normalize-space(.)) > 15]/parent::*",
            "//table//td[2]//p[normalize-space(text()) and string-length(normalize-space(text())) > 8]",
            "//table//tr[1]//td[2]//p",
            "//table//tr[2]//td[1]//p",
            "//td//p//span[normalize-space(text()) and string-length(normalize-space(text())) > 10]",
            "//p//span//text()[string-length(normalize-space(.)) > 15]/parent::*",
            "//td[contains(@style, 'width') or contains(@style, 'border')]//p[normalize-space(text())]",
            "//p[contains(@style, 'text-align') and normalize-space(text()) and string-length(normalize-space(text())) > 8]",
            "//*[self::p or self::span][normalize-space(text()) and string-length(normalize-space(text())) > 20 and contains(normalize-space(text()), ' ')]",
            "//*[normalize-space(text()) and string-length(normalize-space(text())) > 25 and not(contains(normalize-space(text()), ':'))]",
            "//form//p[@class='Texto_Justificado' and normalize-space(text())]",
            "//div//p[@class='Texto_Justificado' and normalize-space(text()) and string-length(normalize-space(text())) > 8]",
            "//body//p[contains(@class, 'Texto') and normalize-space(text()) and string-length(normalize-space(text())) > 10]",
            "//div[contains(@class, 'content') or contains(@class, 'main')]//p[normalize-space(text()) and string-length(normalize-space(text())) > 12]"
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
            "//tr[td[contains(., 'MATRÍCULA')]]/td[last()]//span"
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
            "//*[contains(text(), 'CARGO:')]"
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
            "//*[contains(text(), 'LOTACAO:')]"
        ]