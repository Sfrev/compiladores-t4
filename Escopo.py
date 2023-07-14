from TabelaDeSimbolos import TabelaDeSimbolos

class Escopo:

    def __init__(self, tipo: TabelaDeSimbolos.TipoLA):
        self.pilhaDeTabelas = []
        self.criarNovoEscopo(tipo)

    def criarNovoEscopo(self, tipo: TabelaDeSimbolos.TipoLA):
        self.pilhaDeTabelas.append(TabelaDeSimbolos(tipo))

    def obterEscopoAtual(self):
        return self.pilhaDeTabelas[-1]
    
    def obterPilha(self):
        return self.pilhaDeTabelas

    def abandonarEscopo(self):
        self.pilhaDeTabelas.pop()

    def identificadorExiste(self, nome: str):
        for tabela in self.pilhaDeTabelas:
            if not tabela.existe(nome):
                return True
        return False
