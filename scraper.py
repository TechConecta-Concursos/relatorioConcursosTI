import requests
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self,links_concursos):
        self.__links_concursos = links_concursos
    
    
    def __scrapy_link(self,link,concursos_set):
        try:
            req = requests.get(link)
            if req.status_code == 200:
                doc_html = req.content
                soup_html = BeautifulSoup(doc_html, 'lxml')
                vagas_html = soup_html.find_all("ul",{'class':['link-d', 'link-i']})
                dics_concursos = []
                info_concurso_skipped = False
                info_cargo_add = False
                dic_concurso = dict(cargo="",concurso="",link="")
                for vaga in vagas_html:
                    if vaga["class"][0] == "link-d":
                        if vaga.li is not None:
                            if not vaga.li.a["title"].startswith("Concursos"):
                                dic_concurso["concurso"] = vaga.li.a.text
                                dic_concurso["link"] = vaga.li.a["href"]
                                info_concurso_skipped = False
                        else:
                            info_concurso_skipped = True
                    elif vaga["class"][0] == "link-i":
                        if not info_concurso_skipped and not info_cargo_add:
                            cargo = (vaga.li.a.text).split(" ")[0].capitalize()
                            if "-" in cargo:
                                cargo = cargo.split("-")[0]
                            dic_concurso["cargo"] = cargo
                            info_cargo_add = True
                    if info_cargo_add:
                        combinacao_concurso = f"{dic_concurso['cargo']},;{dic_concurso['concurso']},;{dic_concurso['link']}"
                        copy_concurso = dic_concurso.copy()
                        if combinacao_concurso not in concursos_set:
                            dics_concursos.append(copy_concurso)
                            concursos_set.add(combinacao_concurso)
                        info_cargo_add = False
            else:
                print("Requisição ao site PCI Concursos mal-sucedida, status diferente de 200")
        except Exception as e:
            print(f"Erro ao abrir a conexão com o site PCI Concursos {e}")
        return dics_concursos
    

    def extrair_dados(self,concursos_set):
        dados_concursos = []
        for cargo in self.__links_concursos:
            for link in cargo["links"]:
                dic = self.__scrapy_link(link,concursos_set)
                dados_concursos.append(dic)
        return dados_concursos