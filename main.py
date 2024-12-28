import json
from collections import Counter
from time import perf_counter
from concurso_area_nlp import ConcursoAreaClassificador
import const
from relatorio import Relatorio
from scraper import Scraper
from parser_estados_regioes import ParserEstadosRegioes


titulos_cargos = set()
concursos_set = set()


def separar_links_duplicados(dados_concursos):
    lista_concurso_link = []
    for registro in dados_concursos:
        for dic in registro:
            lista_concurso_link.append(f"{dic['concurso']},;{dic['link']}")
    contador_concurso_link = Counter(lista_concurso_link)
    links_duplicados = [chave for chave,valor in contador_concurso_link.items() 
                        if valor > 1]
    return links_duplicados


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


def ordenar_concursos(dados_concursos):
    dados_concursos_ordenado = []
    map_cargo_lista = dict()
    for titulo_cargo in titulos_cargos:
        map_cargo_lista[titulo_cargo] = list()
    for registro in dados_concursos:
        for dic in registro:
            map_cargo_lista[dic["cargo"]].append(dic)
    map_cargo_lista = sorted(map_cargo_lista.items(), key=lambda item:item[0])
    map_cargo_lista = dict(map_cargo_lista)
    dados_concursos_ordenado = [map_cargo_lista[chave] for chave in map_cargo_lista]
    for registro in dados_concursos_ordenado:
        registro.sort(key=lambda concurso: concurso["concurso"])
    return dados_concursos_ordenado


def gerar_titulos_cargos_unicos(dados_concursos):
    for registro in dados_concursos:
        for dic in  registro:
            titulos_cargos.add(dic["cargo"])


def retornar_concursos_cargo(dados_concursos,links_duplicados):
    concursos_cargos = []
    for _ in links_duplicados:
        concursos_cargos.append("Vários cargos")
    for registro in dados_concursos:
        for dic in registro:
            combinacao_concurso_link = f"{dic['concurso']},;{dic['link']}"
            if combinacao_concurso_link not in links_duplicados:
                concursos_cargos.append(dic["cargo"])
    return concursos_cargos


if __name__ == '__main__':
    tempo_inicio = perf_counter()
    # Lendo os dados iniciais sobre cargos e links
    with open(const.ARQUIVO_DADOS,"r") as f:
        links_concursos = json.load(f)
    # Lendo os dados dos estados
    with open(const.ARQUIVO_ESTADOS_REGIOES, "r") as f:
        info_estados_regioes = json.load(f)
    scraper = Scraper(links_concursos)
    dados_concursos = scraper.extrair_dados(concursos_set)
    # Gerar títulos de cargos únicos
    gerar_titulos_cargos_unicos(dados_concursos)
    # Ordenando os dados por cargo
    dados_concursos = ordenar_concursos(dados_concursos)
    # Separando duplicatas
    links_duplicados = separar_links_duplicados(dados_concursos)
    parser_estados_regioes = ParserEstadosRegioes(info_estados_regioes,
                                                  dados_concursos,links_duplicados)
    estados, regioes = parser_estados_regioes.separar_estados_regioes()
    areas = retornar_areas_concursos(dados_concursos,links_duplicados)
    concursos_cargos = retornar_concursos_cargo(dados_concursos,links_duplicados)
    contador_estados = Counter(estados)
    contador_regioes = Counter(regioes)
    contador_areas = Counter(areas)
    contador_cargos = Counter(concursos_cargos)
    contadores = {
        "estados": contador_estados,
        "regioes": contador_regioes,
        "areas": contador_areas,
        "cargos": contador_cargos
    }
    total_concursos = sum(contador_cargos.values())
    relatorio = Relatorio(dados_concursos,links_duplicados,contadores,total_concursos)
    relatorio.escrever_md(titulos_cargos)
    relatorio.escrever_pdf()
    relatorio.escrever_html()
    # Desempenho do script
    tempo_fim = perf_counter()
    print(f"O script rodou em {tempo_fim - tempo_inicio:.2f} segundos")
    