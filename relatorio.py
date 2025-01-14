from datetime import datetime
from glob import glob
from markdown import markdown
from bs4 import BeautifulSoup
from md2pdf.core import md2pdf

class Relatorio:
    __data = datetime.now().strftime('%d-%m-%y')
    __nome_base = f"relatorio_concursos_ti_{__data}"
    __nome_arquivo_pdf = f"{__nome_base}.pdf"
    __nome_arquivo_md = f"{__nome_base}.md"
    __nome_arquivo_html = f"{__nome_base}.html"
    __folha_estilos = "css/style.css"


    def __init__(self,dados_concursos,links_duplicados,contadores,total_concursos):
        self.__dados_concursos = dados_concursos
        self.__links_duplicados = links_duplicados
        self.__contadores = contadores
        self.__total_concursos = total_concursos


    def __escrever_markdown(self,conteudo):
        try:
            if len(glob(self.__nome_arquivo_md)) > 0:
                with open(self.__nome_arquivo_md, "a") as f:
                    try:
                        f.write(conteudo)
                    except (IOError, OSError):
                        print("Erro ao escrever no relatório markdown")
            else:
                with open(self.__nome_arquivo_md, "w") as f:
                    try:
                        f.write(conteudo)
                    except (IOError, OSError):
                        print("Erro ao criar o relatório markdown")
        except Exception as e:
            print(f"Erro ao abrir o relatório markdown {e}")


    def __escrever_dupla_quebra(self):
        self.__escrever_markdown("\n \n")
        self.__escrever_markdown("\n \n")


    def __escrever_unica_quebra(self):
        self.__escrever_markdown("\n \n")


    def __escrever_cabecalho(self):
        titulo = f"# Relatório de concursos de TI {self.__data}"
        self.__escrever_markdown(titulo)
        self.__escrever_dupla_quebra()
    

    def __escrever_links_unicos(self,titulos_cargos):
        for registro in self.__dados_concursos:
            for dic in registro:
                combinacao_concurso_link = f"{dic['concurso']},;{dic['link']}"
                cargos_com_links = self.__contadores["cargos"].keys()
                if dic["cargo"] in titulos_cargos and dic["cargo"] in cargos_com_links:
                    self.__escrever_markdown(f"## {dic['cargo']}")
                    self.__escrever_unica_quebra()
                    titulos_cargos.remove(dic["cargo"])
                if combinacao_concurso_link not in self.__links_duplicados:
                    self.__escrever_markdown(f"[{dic['concurso']}]({dic['link']})")
                    self.__escrever_unica_quebra()


    def __escrever_links_mais_cargo(self):
        if len(self.__links_duplicados) > 0:
            self.__escrever_markdown("## Vários cargos")
            self.__escrever_unica_quebra()
            for link in self.__links_duplicados:
                split_dados = link.split(",;")
                self.__escrever_markdown(f"[{split_dados[0]}]({split_dados[1]})")
                self.__escrever_unica_quebra()


    def __escrever_estatistica_contador(self,contador):
        contador_sorted = sorted(contador.items(), key=lambda item:item[0])
        contador_sorted = dict(contador_sorted)
        for chave,freq in contador_sorted.items():
            estatisticas = f"{chave} - {freq} concursos ({(freq/self.__total_concursos)*100:.1f}%)"
            self.__escrever_markdown(estatisticas)
            self.__escrever_unica_quebra()


    def __escrever_estatisticas(self):
        self.__escrever_markdown("## Estatísticas")
        self.__escrever_dupla_quebra()
        self.__escrever_markdown(f"Total de concursos disponíveis: {self.__total_concursos}")
        self.__escrever_unica_quebra()
        self.__escrever_markdown("## Concursos por cargo")
        self.__escrever_unica_quebra()
        self.__escrever_estatistica_contador(self.__contadores["cargos"])
        self.__escrever_markdown("## Concursos por estado")
        self.__escrever_unica_quebra()
        self.__escrever_estatistica_contador(self.__contadores["estados"])
        self.__escrever_markdown("## Concursos por região")
        self.__escrever_unica_quebra()
        self.__escrever_estatistica_contador(self.__contadores["regioes"])
        self.__escrever_markdown("## Concursos por área de atuação")
        self.__escrever_unica_quebra()
        self.__escrever_estatistica_contador(self.__contadores["areas"])
    

    def escrever_md(self, titulos_cargos):
        # Escrevendo cabeçalho
        self.__escrever_cabecalho()
        # Escrevendo maior parte dos links (relatório md)
        self.__escrever_links_unicos(titulos_cargos)
        # Escrevendo links que estavam duplicados (relatório md)
        self.__escrever_links_mais_cargo()
        # Escrevendo estatísticas
        self.__escrever_estatisticas()
    

    def escrever_html(self):
        try:
            with open(self.__nome_arquivo_md,"r") as f:
                try:
                    conteudo_md = f.read()
                except (IOError, OSError):
                    print("Erro ao ler o relatório markdown para conversão")
        except Exception as e:
            print(f"Erro ao abrir o relatório markdown {e}")
        try:
            conteudo_html = markdown(conteudo_md)
        except Exception as e:
            print(f"Erro ao criar objeto html a partir do relatório Markdown {e}")
        soup_conteudo = BeautifulSoup(conteudo_html,"lxml")
        tag_head = soup_conteudo.new_tag("head", charset="UTF-8")
        tag_link_css = soup_conteudo.new_tag("link",rel="stylesheet", 
                                            type="text/css", href=self.__folha_estilos)
        soup_conteudo.append(tag_head)
        tag_head_ref = soup_conteudo.head
        tag_head_ref.append(tag_link_css)
        with open(self.__nome_arquivo_html,"w") as f:
            try:
                f.write(str(soup_conteudo))
            except (IOError, OSError):
                print("Erro ao escrever o relatório html")

    
    def escrever_pdf(self):
        try:
            md2pdf(pdf_file_path=self.__nome_arquivo_pdf, md_file_path=self.__nome_arquivo_md, 
                css_file_path=self.__folha_estilos)
        except Exception as e:
            print(f"Erro ao converter o relatório para PDF {e}")