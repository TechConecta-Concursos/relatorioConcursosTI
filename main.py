from bs4 import BeautifulSoup
import json
import requests
from glob import glob
from md2pdf.core import md2pdf
from collections import Counter
from datetime import datetime

arquivo_dados = "links_pci.json"
titulos_cargos = set()
nome_arquivo_pdf = f"relatorio_concursos_ti_{datetime.now().strftime('%d-%m-%y')}.pdf"
nome_arquivo_md = f"relatorio_concursos_ti_{datetime.now().strftime('%d-%m-%y')}.md"

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
    if len(glob(nome_arquivo_md)) > 0:
        with open(nome_arquivo_md, "a") as f:
            f.write(conteudo)
    else:
        with open(nome_arquivo_md, "w") as f:
            f.write(conteudo)

def extrair_dados(links_concursos):
    dados_concursos = []
    for cargo in links_concursos:
        for link in cargo["links"]:
            dic = scrapy_link(cargo,link)
            dados_concursos.append(dic)
    return dados_concursos
    
def separar_links_duplicados(dados_concursos):
    lista_concurso_link = []
    for registro in dados_concursos:
        for dic in registro:
            lista_concurso_link.append(f"{dic['concurso']},;{dic['link']}")
    contador_concurso_link = Counter(lista_concurso_link)
    links_duplicados = [chave for chave,valor in contador_concurso_link.items() 
                        if valor > 1]
    return links_duplicados

def escrever_links_unicos(dados_concursos, links_duplicados):
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

def escrever_links_mais_cargo(links_duplicados):
    escrever_markdown(f"## Vários cargos")
    escrever_markdown("\n \n")
    for link in links_duplicados:
        split_dados = link.split(",;")
        escrever_markdown(f"[{split_dados[0]}]({split_dados[1]})")
        escrever_markdown("\n \n")

def escrever_relatorio_pdf():
    md2pdf(pdf_file_path=nome_arquivo_pdf, md_file_path=nome_arquivo_md)

if __name__ == '__main__':
    # Lendo os dados iniciais sobre cargos e links
    with open(arquivo_dados,"r") as f:
        links_concursos = json.load(f)
    # Extraindo os dados
    dados_concursos = extrair_dados(links_concursos)
    # Separando duplicatas
    links_duplicados = separar_links_duplicados(dados_concursos)
    # Escrevendo maior parte dos links (relatório md)
    escrever_links_unicos(dados_concursos,links_duplicados)
    # Escrevendo links que estavam duplicados (relatório md)
    escrever_links_mais_cargo(links_duplicados)
    # Escrevendo o relatório em pdf
    escrever_relatorio_pdf()