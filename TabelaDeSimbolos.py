from enum import Enum


class TabelaDeSimbolos:
    class TipoLA(Enum):
        INTEIRO = 1
        REAL = 2
        LITERAL = 3
        LOGICO = 4
        INVALIDO = 5
        REGISTRADOR = 6
        VOID = 7

    class Estrutura(Enum):
        VARIAVEL = 1
        CONSTANTE = 2
        PROCEDIMENTO = 3
        FUNCAO = 4
        TIPO = 5

    class EntradaTabelaDeSimbolos:
        def __init__(self, nome, tipo, estrutura):
            self.nome = nome
            self.tipo = tipo
            self.estrutura = estrutura

    def __init__(self, tipo):
        self.tabelaDeSimbolos = {}
        self.tabelaTipo = {}
        self.tipo = tipo

    def adicionarTabelaSimbolos(self, nome: str, tipo: TipoLA, estrutura: Estrutura):
        etds = TabelaDeSimbolos.EntradaTabelaDeSimbolos(nome, tipo, estrutura)
        self.tabelaDeSimbolos[nome] = etds

    def adicionarEntradaTabelaSimbolos(self, entradaTabelaSimbolos: EntradaTabelaDeSimbolos):
        self.tabelaDeSimbolos[entradaTabelaSimbolos.nome] = entradaTabelaSimbolos

    def adicionarTipoNome(self, tipoNome: str, entradaTabelaSimbolos: EntradaTabelaDeSimbolos):

        if tipoNome in self.tabelaTipo:
            self.tabelaTipo.get(tipoNome).append(entradaTabelaSimbolos)
        else:
            list = []
            list.append(entradaTabelaSimbolos)
            self.tabelaTipo[tipoNome] = list

    def existe(self, nome: str):
        return nome in self.tabelaDeSimbolos

    def verificar(self, nome: str):
        return self.tabelaDeSimbolos[nome].tipo
    
    def verificarTipo(self, nome: str):
        return self.tabelaTipo[nome] #if nome in self.tabelaTipo else None
