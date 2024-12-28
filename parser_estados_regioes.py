class ParserEstadosRegioes: # https://servicodados.ibge.gov.br/api/v1/localidades/estados
    __estados = []
    __regioes = []


    def __init__(self,info_estados_regioes,dados_concursos,links_duplicados):
        self.__info_estados_regioes = info_estados_regioes
        self.__siglas_estados = self.__inicializar_siglas_estados()
        self.__dados_concursos = dados_concursos
        self.__links_duplicados = links_duplicados


    def __inicializar_siglas_estados(self):
        siglas_estados = []
        for info_estado in self.__info_estados_regioes:
            for chave in info_estado:
                if chave == "sigla":
                    siglas_estados.append(info_estado["sigla"])
        return siglas_estados
    
    
    def __separar_estados_regioes_unicos(self):
        for registro in self.__dados_concursos:
            for dic in registro:
                info_concurso_split = dic["concurso"].split("-")
                info_concurso_split = list(map(lambda info: info.strip(),info_concurso_split))
                combinacao_concurso_link = f"{dic['concurso']},;{dic['link']}"
                if combinacao_concurso_link not in self.__links_duplicados:
                    for info in info_concurso_split:
                        if info in self.__siglas_estados:
                            for info_estado in self.__info_estados_regioes:
                                for chave in info_estado:
                                    if info_estado[chave] == info:
                                        self.__estados.append(info_estado["nome"])
                                        self.__regioes.append(info_estado["regiao"])


    def __separar_estados_regioes_duplicados(self):
        for link in self.__links_duplicados:
            info_concurso_quebra = link.split(",;")[0]
            info_concurso_split = info_concurso_quebra.split("-")
            info_concurso_split = list(map(lambda info: info.strip(),info_concurso_split))
            for info in info_concurso_split:
                if info in self.__siglas_estados:
                    for info_estado in self.__info_estados_regioes:
                        for chave in info_estado:
                            if info_estado[chave] == info:
                                self.__estados.append(info_estado["nome"])
                                self.__regioes.append(info_estado["regiao"])
    

    def separar_estados_regioes(self):
        self.__separar_estados_regioes_unicos()
        self.__separar_estados_regioes_duplicados()
        return self.__estados.copy(), self.__regioes.copy()