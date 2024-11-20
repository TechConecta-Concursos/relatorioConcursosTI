class ConcursoAreaClassificador:
    def __init__(self):
        # Mapeamento de palavras-chave para categorias
        self.keyword_map = {
            "tribunal": "Tribunal",
            "juiz": "Tribunal",
            "justiça": "Tribunal",
            "universidade": "Educação",
            "instituto": "Educação",
            "escola técnica": "Educação",
            "etec": "Educação",
            "prefeitura": "Prefeitura",
            "secretaria": "Secretaria",
            "câmara": "Legislativo Municipal",
            "banco": "Bancária",
            "hospital": "Saúde",
            "saúde": "Saúde",
            "segurança": "Segurança Pública",
            "polícia": "Segurança Pública",
            "defesa": "Segurança Pública",
            "correios": "Logística",
            "transporte": "Logística",
            "infraestrutura": "Engenharia",
            "engenharia": "Engenharia",
            "ambiental": "Meio Ambiente",
            "meio ambiente": "Meio Ambiente",
            "cultura": "Cultura",
            "turismo": "Cultura",
            "ciência": "Pesquisa",
            "tecnologia": "Pesquisa",
        }
    
    def classificar(self, orgao_nome):
        """
        Classifica o concurso com base no nome do órgão.
        
        :param orgao_nome: Nome do órgão público (string)
        :return: Categoria da área (string)
        """
        orgao_nome = orgao_nome.lower()
        for keyword, area in self.keyword_map.items():
            if keyword in orgao_nome:
                return area
        return "Outros"
