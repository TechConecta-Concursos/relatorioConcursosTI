from bs4 import BeautifulSoup
import json
import requests
from glob import glob
from md2pdf.core import md2pdf
from collections import Counter

arquivo_dados = "links_pci.json"
dados_concursos = []
titulos_cargos = set()

with open(arquivo_dados,"r") as f:
    links_concursos = json.load(f)

def scrapy_link(cargo,link):
    doc_html = requests.get(link).content
    soup_html = BeautifulSoup(doc_html, 'lxml')
    vagas_html = soup_html.find_all("ul", class_="link-d")
    dics_concursos = []
    for vaga in vagas_html:
        if not vaga.li.a.text.isupper():
            dic = {"cargo": cargo["cargo"], 
                    "concurso": vaga.li.a.text, 
                    "link": vaga.li.a["href"]}
            dics_concursos.append(dic)
    return dics_concursos


def escrever_markdown(conteudo):
    if len(glob("teste_markdown.md")) > 0:
        with open("teste_markdown.md", "a") as f:
            f.write(conteudo)
    else:
        with open("teste_markdown.md", "w") as f:
            f.write(conteudo)

# Extraindo os dados
for cargo in links_concursos:
    for link in cargo["links"]:
        dic = scrapy_link(cargo,link)
        dados_concursos.append(dic)

# Separando duplicatas
lista_concurso_link = []
for registro in dados_concursos:
    for dic in registro:
        lista_concurso_link.append(f"{dic['concurso']},;{dic['link']}")

contador_concurso_link = Counter(lista_concurso_link)
links_duplicados = [chave for chave,valor in contador_concurso_link.items() if valor > 1]

# Escrevendo maior parte dos links
for registro in dados_concursos:
    for dic in registro:
        combinacao_concurso_link = f"{dic['concurso']},;{dic['link']}"
        if dic["cargo"] not in titulos_cargos:
            escrever_markdown(f"## {dic['cargo']}")
            escrever_markdown("\n \n")
        if combinacao_concurso_link not in links_duplicados:
            escrever_markdown(f"[{dic['concurso']}]({dic['link']})")
            escrever_markdown("\n \n")
        titulos_cargos.add(dic["cargo"])

# Escrevendo links que estavam duplicados

escrever_markdown(f"## Vários cargos")
escrever_markdown("\n \n")
for link in links_duplicados:
    split_dados = link.split(",;")
    escrever_markdown(f"[{split_dados[0]}]({split_dados[1]})")
    escrever_markdown("\n \n")
        
        
md2pdf(pdf_file_path="teste_pdf.pdf", md_file_path="teste_markdown.md",)