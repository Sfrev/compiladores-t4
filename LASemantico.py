from LAParser import LAParser
from LAVisitor import LAVisitor
from TabelaDeSimbolos import TabelaDeSimbolos
from LASemanticoUtils import LASemanticoUtils
from Escopo import Escopo
from typing import List


class LASemantico(LAVisitor):
    def __init__(self):
        self.escopos = Escopo(TabelaDeSimbolos.TipoLA.VOID)

    def visitPrograma(self, ctx: LAParser.ProgramaContext):
        return super().visitPrograma(ctx)

    def visitDeclaracao_constante(self, ctx: LAParser.Declaracao_constanteContext):
        escopoAtual = self.escopos.obterEscopoAtual()

        if escopoAtual.existe(ctx.IDENT().getText()):
            LASemanticoUtils.adicionarErroSemantico(token=ctx.start,
                                                    mensagem=f'constante {ctx.IDENT().getText()} ja declarado '
                                                             f'anteriormente')
        else:
            tipo = TabelaDeSimbolos.TipoLA.INTEIRO
            aux = LASemanticoUtils.getTipo(ctx.tipo_basico().getText())
            if aux is not None:
                tipo = aux

            escopoAtual.adicionarTabelaSimbolos(ctx.IDENT().getText(), tipo, TabelaDeSimbolos.Estrutura.CONSTANTE)

        return super().visitDeclaracao_constante(ctx)

    def visitDeclaracao_tipo(self, ctx: LAParser.Declaracao_tipoContext):

        escopoAtual = self.escopos.obterEscopoAtual()

        if escopoAtual.existe(ctx.IDENT().getText()):
            LASemanticoUtils.adicionarErroSemantico(token=ctx.start,
                                                    mensagem=f'tipo {ctx.IDENT().getText()} declarado duas vezes num '
                                                             f'mesmo escopo')
        else:
            tipo = LASemanticoUtils.getTipo(ctx.tipo().getText())

            if tipo is not None:
                escopoAtual.adicionarTabelaSimbolos(ctx.IDENT().getText(), tipo, TabelaDeSimbolos.Estrutura.TIPO)
            elif ctx.tipo().registro() is not None:
                varRegistros = []
                for variavel in ctx.tipo().registro().variavel():
                    tipoRegistrador = LASemanticoUtils.getTipo(variavel.tipo().getText())
                    for identificador in variavel.identificador():
                        entrada = TabelaDeSimbolos.EntradaTabelaDeSimbolos(identificador.getText(), tipoRegistrador, TabelaDeSimbolos.Estrutura.TIPO)
                        escopoAtual.adicionarEntradaTabelaSimbolos(entrada)
                        varRegistros.append(entrada)

                if escopoAtual.existe(ctx.IDENT().getText()):
                    LASemanticoUtils.adicionarErroSemantico(token=ctx.start,
                                                            mensagem=f'identificador {ctx.IDENT().getText()} ja declarado anteriormente')
                else:
                    escopoAtual.adicionarTabelaSimbolos(ctx.IDENT().getText(), TabelaDeSimbolos.TipoLA.REGISTRADOR,
                                                        TabelaDeSimbolos.Estrutura.TIPO)

                for registro in varRegistros:
                    nomeVar = ctx.IDENT().getText() + '.' + registro.nome
                    if escopoAtual.existe(nomeVar):
                        LASemanticoUtils.adicionarErroSemantico(token=ctx.start,
                                                                mensagem=f'identificador {nomeVar} ja declarado anteriormente')
                    else:
                        escopoAtual.adicionarEntradaTabelaSimbolos(registro)
                        escopoAtual.adicionarTipoNome(ctx.IDENT().getText(), registro)

            tipo = LASemanticoUtils.getTipo(ctx.tipo().getText())
            escopoAtual.adicionarTabelaSimbolos(ctx.IDENT().getText(), tipo, TabelaDeSimbolos.Estrutura.TIPO)

        return super().visitDeclaracao_tipo(ctx)

    def visitDeclaracao_variavel(self, ctx: LAParser.Declaracao_variavelContext):
        escopoAtual = self.escopos.obterEscopoAtual()

        for identificador in ctx.variavel().identificador():
            nomeId = ''
            i = 0
            for ident in identificador.IDENT():
                if i > 0:
                    nomeId += '.'
                i += 1
                nomeId += ident.getText()
            if escopoAtual.existe(nomeId):
                LASemanticoUtils.adicionarErroSemantico(identificador.start,
                                                        f'identificador {nomeId} ja declarado '
                                                        f'anteriormente')
            else:
                tipo = LASemanticoUtils.getTipo(ctx.variavel().tipo().getText())
                if tipo is not None:
                    escopoAtual.adicionarTabelaSimbolos(nomeId, tipo, TabelaDeSimbolos.Estrutura.VARIAVEL)
                else:
                    identTipo = ctx.variavel().tipo().tipo_estendido().tipo_basico_ident().IDENT() if (
                            ctx.variavel().tipo() is not None
                            and ctx.variavel().tipo().tipo_estendido() is not None
                            and ctx.variavel().tipo().tipo_estendido().tipo_basico_ident() is not None
                            and ctx.variavel().tipo().tipo_estendido().tipo_basico_ident().IDENT() is not None
                    ) else None
                    if identTipo is not None:
                        registros = None
                        for tabela in self.escopos.obterPilha():
                            if tabela.existe(identTipo.getText()):
                                registros = tabela.verificarTipo(identTipo.getText())
                        if escopoAtual.existe(nomeId):
                            LASemanticoUtils.adicionarErroSemantico(identificador.start, f"identificador {nomeId} ja declarado anteriormente")
                        else:
                            escopoAtual.adicionarTabelaSimbolos(nomeId, TabelaDeSimbolos.TipoLA.REGISTRADOR, TabelaDeSimbolos.Estrutura.VARIAVEL)
                            if registros is not None:
                                for registro in registros:
                                    escopoAtual.adicionarTabelaSimbolos(nomeId + '.' + registro.nome, registro.tipo, TabelaDeSimbolos.Estrutura.VARIAVEL)
                    elif ctx.variavel().tipo().registro() is not None:
                        registros: List[TabelaDeSimbolos.EntradaTabelaDeSimbolos] = []
                        for variavel in ctx.variavel().tipo().registro().variavel():
                            tipoRegistros = LASemanticoUtils.getTipo(variavel.tipo().getText())
                            for identificador in variavel.identificador():
                                entrada = TabelaDeSimbolos.EntradaTabelaDeSimbolos(identificador.getText(), tipoRegistros, TabelaDeSimbolos.Estrutura.VARIAVEL)
                                escopoAtual.adicionarEntradaTabelaSimbolos(entrada)
                                registros.append(entrada)
                        escopoAtual.adicionarTabelaSimbolos(nomeId, TabelaDeSimbolos.TipoLA.REGISTRADOR, TabelaDeSimbolos.Estrutura.VARIAVEL)

                        for registro in registros:
                            nomeVar = nomeId + '.' + registro.nome
                            if escopoAtual.existe(nomeVar):
                                LASemanticoUtils.adicionarErroSemantico(identificador.start, f"identificador {nomeVar} ja declarado anteriormente")
                            else:
                                escopoAtual.adicionarEntradaTabelaSimbolos(registro)
                                escopoAtual.adicionarTabelaSimbolos(nomeVar, registro.tipo, TabelaDeSimbolos.Estrutura.VARIAVEL)
                    else:
                        escopoAtual.adicionarTabelaSimbolos(identificador.getText(), TabelaDeSimbolos.TipoLA.INTEIRO, TabelaDeSimbolos.Estrutura.VARIAVEL)

        return super().visitDeclaracao_variavel(ctx)

    def visitDeclaracao_global(self, ctx: LAParser.Declaracao_globalContext):
        escopoAtual = self.escopos.obterEscopoAtual()
        ret = None

        if escopoAtual.existe(ctx.IDENT().getText()):
            LASemanticoUtils.adicionarErroSemantico(ctx.start, f'{ctx.IDENT().getText()} ja declarado anteriormente')
            ret = super().visitDeclaracao_global(ctx)
        else:
            tipoRetornoFuncao = TabelaDeSimbolos.TipoLA.VOID
            if ctx.getText().startswith("funcao"):
                tipoRetornoFuncao = LASemanticoUtils.getTipo(ctx.tipo_estendido().getText())
                escopoAtual.adicionarTabelaSimbolos(ctx.IDENT().getText(), tipoRetornoFuncao,TabelaDeSimbolos.Estrutura.FUNCAO)
            else:
                tipoRetornoFuncao = TabelaDeSimbolos.TipoLA.VOID
                escopoAtual.adicionarTabelaSimbolos(ctx.IDENT().getText(), tipoRetornoFuncao, TabelaDeSimbolos.Estrutura.PROCEDIMENTO)
            self.escopos.criarNovoEscopo(tipoRetornoFuncao)
            escopoAntigo = escopoAtual
            escopoAtual = self.escopos.obterEscopoAtual()
            if ctx.parametros() is not None:
                for param in ctx.parametros().parametro():
                    for id in param.identificador():
                        nomeId = ''
                        i = 0
                        for ident in id.IDENT():
                            if i > 0:
                                nomeId += '.'
                            i += 1
                            nomeId += ident.getText()
                        if escopoAtual.existe(nomeId):
                            LASemanticoUtils.adicionarErroSemantico(id.start, f'identificador {nomeId} ja declarado anteriormente')
                        else:
                            tipo = LASemanticoUtils.getTipo(param.tipo_estendido().getText())
                            if tipo is not None:
                                entradaTabela = TabelaDeSimbolos.EntradaTabelaDeSimbolos(nomeId, tipo, TabelaDeSimbolos.Estrutura.VARIAVEL)
                                #escopoAtual.adicionarTabelaSimbolos(nomeId, tipo, TabelaDeSimbolos.Estrutura.VARIAVEL)
                                escopoAtual.adicionarEntradaTabelaSimbolos(entradaTabela)
                                escopoAntigo.adicionarTipoNome(ctx.IDENT().getText(), entradaTabela)
                            else:
                                identTipo = param.tipo_estendido().tipo_basico_ident().IDENT() if param.tipo_estendido().tipo_basico_ident() is not None and param.tipo_estendido().tipo_basico_ident().IDENT() is not None else None
                                if identTipo is not None:
                                    regVars = None
                                    for tabela in self.escopos.obterPilha():
                                        if tabela.existe(identTipo.getText()):
                                            regVars = tabela.verificarTipo(identTipo.getText())
                                    if escopoAtual.existe(nomeId):
                                        LASemanticoUtils.adicionarErroSemantico(id.start, f"identificador {nomeId} ja declarado anteriormente")
                                    else:
                                        entradaTabela = TabelaDeSimbolos.EntradaTabelaDeSimbolos(nomeId, TabelaDeSimbolos.TipoLA.REGISTRADOR, TabelaDeSimbolos.Estrutura.VARIAVEL)
                                        #escopoAtual.adicionarTabelaSimbolos(nomeId, TabelaDeSimbolos.TipoLA.REGISTRADOR, TabelaDeSimbolos.Estrutura.VARIAVEL)
                                        escopoAtual.adicionarEntradaTabelaSimbolos(entradaTabela)
                                        escopoAntigo.adicionarTipoNome(ctx.IDENT().getText(), entradaTabela)

                                        for s in regVars:
                                            escopoAtual.adicionarTabelaSimbolos(nomeId + '.' + s.nome, s.tipo, TabelaDeSimbolos.Estrutura.VARIAVEL)
            ret = super().visitDeclaracao_global(ctx)
            self.escopos.abandonarEscopo()
        return ret

    def visitTipo_basico_ident(self, ctx: LAParser.Tipo_basico_identContext):

        if ctx.IDENT() is not None:
            existe = False
            for escopo in self.escopos.obterPilha():
                if escopo.existe(ctx.IDENT().getText()):
                    existe = True
            if not existe:
                LASemanticoUtils.adicionarErroSemantico(ctx.start, f'tipo {ctx.IDENT().getText()} nao declarado')

        return super().visitTipo_basico_ident(ctx)

    def visitIdentificador(self, ctx: LAParser.IdentificadorContext):
        nomeVar = ''
        i = 0
        for ident in ctx.IDENT():
            if i > 0:
                nomeVar += '.'
            nomeVar += ident.getText()
            i += 1
        erro = True
        for escopo in self.escopos.obterPilha():
            if escopo.existe(nomeVar):
                erro = False
                
        if erro:
            LASemanticoUtils.adicionarErroSemantico(ctx.start, f'identificador {nomeVar} nao declarado')
        return super().visitIdentificador(ctx)

    def visitCmdAtribuicao(self, ctx: LAParser.CmdAtribuicaoContext):
        tipoExpressao = LASemanticoUtils.verificarTipoExpressao(escopos=self.escopos, ctx=ctx.expressao())
        erro = False
        ponteiro = "^" if ctx.getText()[0] == '^' else ""
        nomeVar = ''
        i = 0
        for ident in ctx.identificador().IDENT():
            if i > 0:
                nomeVar += '.'
            nomeVar += ident.getText()
            i += 1
        if tipoExpressao != TabelaDeSimbolos.TipoLA.INVALIDO:
            for escopo in self.escopos.obterPilha():
                if escopo.existe(nomeVar):
                    tipoVar = LASemanticoUtils.verificarTipoNomeVar(escopos=self.escopos, nomeVar=nomeVar)
                    varNumeric = tipoVar == TabelaDeSimbolos.TipoLA.INTEIRO or tipoVar == TabelaDeSimbolos.TipoLA.REAL
                    expNumeric = tipoExpressao == TabelaDeSimbolos.TipoLA.INTEIRO or tipoExpressao == TabelaDeSimbolos.TipoLA.REAL
                    if not (
                            varNumeric and expNumeric) and tipoVar != tipoExpressao and tipoExpressao != TabelaDeSimbolos.TipoLA.INVALIDO:
                        erro = True
        else:
            erro = True

        if erro:
            nomeVar = ctx.identificador().getText()
            LASemanticoUtils.adicionarErroSemantico(ctx.identificador().start,
                                                    f'atribuicao nao compativel para {ponteiro + nomeVar}')

        return super().visitCmdAtribuicao(ctx)
    
    def visitCmdRetorne(self, ctx: LAParser.CmdRetorneContext):
        if self.escopos.obterEscopoAtual().tipo == TabelaDeSimbolos.TipoLA.VOID:
            LASemanticoUtils.adicionarErroSemantico(ctx.start, f"comando retorne nao permitido nesse escopo")

        return super().visitCmdRetorne(ctx)
    
    def visitParcela_unario(self, ctx: LAParser.Parcela_unarioContext):
        escopoAtual = self.escopos.obterEscopoAtual()
        if ctx.IDENT() is not None:
            nome = ctx.IDENT().getText()
            if escopoAtual.existe(nome):
                params = escopoAtual.verificarTipo(nome)
                erro = False
                if len(params) != len(ctx.expressao()):
                    erro = True
                else:
                    for i in range(len(params)):
                        if params[i].tipo != LASemanticoUtils.verificarTipoExpressao(escopos=self.escopos, ctx=ctx.expressao()[i]):
                            erro = True
                if erro:
                    LASemanticoUtils.adicionarErroSemantico(ctx.start, f"incompatibilidade de parametros na chamada de {nome}")
        
        return super().visitParcela_unario(ctx)
