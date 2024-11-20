from bs4 import BeautifulSoup
import json
import requests
from glob import glob
from md2pdf.core import md2pdf
from collections import Counter
from datetime import datetime
from time import perf_counter
from markdown import markdown
from concurso_area_nlp import ConcursoAreaClassificador

arquivo_dados = "links_pci.json"
arquivo_estados_regioes = "estados_regioes.json"
titulos_cargos = set()
nome_arquivo_pdf = f"relatorio_concursos_ti_{datetime.now().strftime('%d-%m-%y')}.pdf"
nome_arquivo_md = f"relatorio_concursos_ti_{datetime.now().strftime('%d-%m-%y')}.md"
nome_arquivo_html = f"relatorio_concursos_ti_{datetime.now().strftime('%d-%m-%y')}.html"
folha_estilos = "style.css"
estados = []
regioes = []

def scrapy_link(cargo,link):
    doc_html = requests.get(link).content
    soup_html = BeautifulSoup(doc_html, 'lxml')
    vagas_html = soup_html.find_all("ul", class_="link-d")
    dics_concursos = []
    for vaga in vagas_html:
        if vaga.li is not None:
            if not vaga.li.a["title"].startswith("Concursos"):
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

def escrever_dupla_quebra():
    escrever_markdown("\n \n")
    escrever_markdown("\n \n")

def escrever_unica_quebra():
     escrever_markdown("\n \n")

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
                escrever_unica_quebra()
            if combinacao_concurso_link not in links_duplicados:
                escrever_markdown(f"[{dic['concurso']}]({dic['link']})")
                escrever_unica_quebra()
            titulos_cargos.add(dic["cargo"])

def escrever_links_mais_cargo(links_duplicados):
    escrever_markdown("## Vários cargos")
    escrever_unica_quebra()
    for link in links_duplicados:
        split_dados = link.split(",;")
        escrever_markdown(f"[{split_dados[0]}]({split_dados[1]})")
        escrever_unica_quebra()

def escrever_relatorio_pdf():
    md2pdf(pdf_file_path=nome_arquivo_pdf, md_file_path=nome_arquivo_md, 
           css_file_path=folha_estilos)

def escrever_cabecalho():
    titulo = f"# Relatório de concursos de TI {datetime.now().strftime('%d-%m-%y')}"
    escrever_markdown(titulo)
    escrever_dupla_quebra()

def inicializar_siglas_estados(info_estados_regioes):
    siglas_estados = []
    for info_estado in info_estados_regioes:
        for chave in info_estado:
            if chave == "sigla":
                siglas_estados.append(info_estado["sigla"])
    return siglas_estados

def separar_estados_regioes_unicos(dados_concursos,siglas_estados,
                                   info_estados_regioes,links_duplicados):
    for registro in dados_concursos:
        for dic in registro:
            info_concurso_split = dic["concurso"].split("-")
            info_concurso_split = list(map(lambda info: info.strip(),info_concurso_split))
            combinacao_concurso_link = f"{dic['concurso']},;{dic['link']}"
            if combinacao_concurso_link not in links_duplicados:
                for info in info_concurso_split:
                    if info in siglas_estados:
                        for info_estado in info_estados_regioes:
                            for chave in info_estado:
                                if info_estado[chave] == info:
                                    estados.append(info_estado["nome"])
                                    regioes.append(info_estado["regiao"])

def separar_estados_regioes_duplicados(links_duplicados,siglas_estados,
                                       info_estados_regioes):
    for link in links_duplicados:
        info_concurso_quebra = link.split(",;")[0]
        info_concurso_split = info_concurso_quebra.split("-")
        info_concurso_split = list(map(lambda info: info.strip(),info_concurso_split))
        for info in info_concurso_split:
            if info in siglas_estados:
                for info_estado in info_estados_regioes:
                    for chave in info_estado:
                        if info_estado[chave] == info:
                            estados.append(info_estado["nome"])
                            regioes.append(info_estado["regiao"])

def separar_estados_regioes(dados_concursos,info_estados_regioes,links_duplicados):
    # https://servicodados.ibge.gov.br/api/v1/localidades/estados
    siglas_estados = inicializar_siglas_estados(info_estados_regioes)
    separar_estados_regioes_unicos(dados_concursos,siglas_estados,
                                   info_estados_regioes,links_duplicados)
    separar_estados_regioes_duplicados(links_duplicados,siglas_estados,
                                       info_estados_regioes)

def escrever_estatistica_contador(contador,total_concursos):
    contador_sorted = sorted(contador.items(), key=lambda item:item[0])
    contador_sorted = dict(contador_sorted)
    for chave,freq in contador_sorted.items():
        estatisticas = f"{chave} - {freq} concursos ({(freq/total_concursos)*100:.1f}%)"
        escrever_markdown(estatisticas)
        escrever_unica_quebra()

def escrever_estatisticas(contador_estados,contador_regioes,total_concursos):
    escrever_markdown("## Estatísticas")
    escrever_dupla_quebra()
    escrever_markdown(f"Total de concursos disponíveis: {total_concursos}")
    escrever_unica_quebra()
    escrever_markdown("## Concursos por estado")
    escrever_unica_quebra()
    escrever_estatistica_contador(contador_estados,total_concursos)
    escrever_markdown("## Concursos por região")
    escrever_unica_quebra()
    escrever_estatistica_contador(contador_regioes,total_concursos)

def escrever_estatisticas(contador_estados,contador_regioes,contador_areas,total_concursos):
    escrever_markdown("## Estatísticas")
    escrever_dupla_quebra()
    escrever_markdown(f"Total de concursos disponíveis: {total_concursos}")
    escrever_unica_quebra()
    escrever_markdown("## Concursos por estado")
    escrever_unica_quebra()
    escrever_estatistica_contador(contador_estados,total_concursos)
    escrever_markdown("## Concursos por região")
    escrever_unica_quebra()
    escrever_estatistica_contador(contador_regioes,total_concursos)
    escrever_markdown("## Concursos por área de atuação")
    escrever_unica_quebra()
    escrever_estatistica_contador(contador_areas,total_concursos)

def escrever_relatorio_md(dados_concursos,links_duplicados,contador_estados,
                          contador_regioes,contador_areas,total_concursos):
    # Escrevendo cabeçalho
    escrever_cabecalho()
    # Escrevendo maior parte dos links (relatório md)
    escrever_links_unicos(dados_concursos,links_duplicados)
    # Escrevendo links que estavam duplicados (relatório md)
    escrever_links_mais_cargo(links_duplicados)
    # Escrevendo estatísticas
    escrever_estatisticas(contador_estados,contador_regioes,contador_areas,total_concursos)

def escrever_relatorio_html():
    with open(nome_arquivo_md,"r") as f:
        conteudo_md = f.read()
    conteudo_html = markdown(conteudo_md)
    soup_conteudo = BeautifulSoup(conteudo_html,"lxml")
    tag_head = soup_conteudo.new_tag("head", charset="UTF-8")
    tag_link_css = soup_conteudo.new_tag("link",rel="stylesheet", 
                                         type="text/css", href="style.css")
    soup_conteudo.append(tag_head)
    tag_head_ref = soup_conteudo.head
    tag_head_ref.append(tag_link_css)
    with open(nome_arquivo_html,"w") as f:
        f.write(str(soup_conteudo))

def retornar_areas_concursos(dados_concursos,links_duplicados):
    classificacoes = []
    classificador = ConcursoAreaClassificador()
    for link in links_duplicados:
        classificacao = classificador.classificar(link)
        classificacoes.append(classificacao)
    for registro in dados_concursos:
        for dic in registro:
            combinacao_concurso_link = f"{dic['concurso']},;{dic['link']}"
            if combinacao_concurso_link not in links_duplicados:
                classificacao = classificador.classificar(dic["concurso"])
                classificacoes.append(classificacao)
    return classificacoes

if __name__ == '__main__':
    tempo_inicio = perf_counter()
    # Lendo os dados iniciais sobre cargos e links
    with open(arquivo_dados,"r") as f:
        links_concursos = json.load(f)
    # Lendo os dados dos estados
    with open(arquivo_estados_regioes, "r") as f:
        info_estados_regioes = json.load(f)
    # Extraindo os dados
    dados_concursos = extrair_dados(links_concursos)
    # Separando duplicatas
    links_duplicados = separar_links_duplicados(dados_concursos)
    # Separando estados e regiões dos concursos
    separar_estados_regioes(dados_concursos,info_estados_regioes,links_duplicados)
    areas = retornar_areas_concursos(dados_concursos,links_duplicados)
    contador_estados = Counter(estados)
    contador_regioes = Counter(regioes)
    contador_areas = Counter(areas)
    total_concursos = sum(contador_estados.values())
    # Escrevendo o relatório em md
    escrever_relatorio_md(dados_concursos,links_duplicados,contador_estados,
                          contador_regioes,contador_areas,total_concursos)
    # Escrevendo o relatório em pdf
    escrever_relatorio_pdf()
    # Escrevendo o relatório em HTML
    escrever_relatorio_html()
    # Desempenho do script
    tempo_fim = perf_counter()
    print(f"O script rodou em {tempo_fim - tempo_inicio:.2f} segundos")
    