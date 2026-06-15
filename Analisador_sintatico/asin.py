import sys
import os

diretorio_atual = os.path.dirname(os.path.abspath(__file__))

caminho_lexico = os.path.join(diretorio_atual, '..', 'Analisador_lexico')

sys.path.append(caminho_lexico)

import al



class TabelaSimbolos:
    def __init__(self):
        self.escopos = [{}]  # pilha de escopos; escopos[0] = escopo global

    def entrar_escopo(self):
        self.escopos.append({})

    def sair_escopo(self):
        self.escopos.pop()

    def declarar(self, nome, tipo, linha, col):
        escopo_atual = self.escopos[-1]
        if nome in escopo_atual:  # redeclaração
            return False, escopo_atual[nome]
        escopo_atual[nome] = {'tipo': tipo, 'linha': linha, 'col': col, 'inicializada': False}
        return True, None

    def buscar(self, nome):
        # Procura do escopo mais interno para o mais externo
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        return None

    def inicializar(self, nome):
        simbolo = self.buscar(nome)
        if simbolo is not None:
            simbolo['inicializada'] = True

    def exibir(self):
        print("\n" + "=" * 55)
        print("TABELA DE SÍMBOLOS (escopo global)")
        print("=" * 55)
        global_scope = self.escopos[0]
        if not global_scope:
            print("  (nenhuma variável declarada no escopo global)")
        else:
            print(f"  {'NOME':<18} {'TIPO':<6} {'LINHA':<6} {'INICIALIZADA'}")
            print(f"  {'-' * 48}")
            for nome, info in global_scope.items():
                init = "Sim" if info['inicializada'] else "Nao"
                print(f"  {nome:<18} {info['tipo']:<6} {info['linha']:<6} {init}")
        print("=" * 55)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.has_error = False
        self.tabela = TabelaSimbolos()

        # Tokens de sincronização para recuperação de erro
        self.sync_tokens = {
            al.TOKEN.tk_Semi, al.TOKEN.tk_Int, al.TOKEN.tk_If, 
            al.TOKEN.tk_While, al.TOKEN.tk_For, al.TOKEN.tk_Rbrace, al.TOKEN.tk_EOI
        }

    def current_token(self):
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        return self.tokens[-1]

    def advance(self):
        if self.index < len(self.tokens):
            self.index += 1

    def check(self, expected_type):
        return self.current_token()['type'] == expected_type

    def consume(self, expected_type, msg):
        if self.check(expected_type):
            self.advance()
            return True
        
        self.has_error = True
        curr = self.current_token()
        nome_token = al.simbolos[curr['type']]
        valor_token = curr['value'] if curr['value'] else nome_token
        
        print(f">>> [ERRO SINTÁTICO L{curr['line']}:C{curr['col']}]: {msg} (Encontrado: '{valor_token}')")
        
        # Modo Panico
        while not self.check(al.TOKEN.tk_EOI):
            if self.check(al.TOKEN.tk_Semi):
                self.advance()  
                break
            if self.current_token()['type'] in self.sync_tokens:
                break 
            self.advance()
        return False

    # Emite um erro semântico sem interromper o parser.
    def erro_semantico(self, linha, col, msg):
        self.has_error = True
        print(f">>> [ERRO SEMÂNTICO L{linha}:C{col}]: {msg}")

    def parse_program(self):
        while not self.check(al.TOKEN.tk_EOI):
            self.parse_statement()

    def parse_statement(self):
        curr_type = self.current_token()['type']
        
        if curr_type == al.TOKEN.tk_Int:
            self.parse_declaration()
        elif curr_type == al.TOKEN.tk_If:
            self.parse_if()
        elif curr_type == al.TOKEN.tk_While:
            self.parse_while()
        elif curr_type == al.TOKEN.tk_For:
            self.parse_for()
        elif curr_type == al.TOKEN.tk_Lbrace:
            self.parse_block()
        else:
            self.parse_expression_statement()

    def parse_block(self):
        self.consume(al.TOKEN.tk_Lbrace, "Esperado '{' no início do bloco.")
        self.tabela.entrar_escopo() 
        while not self.check(al.TOKEN.tk_EOI) and not self.check(al.TOKEN.tk_Rbrace):
            self.parse_statement()
        self.tabela.sair_escopo()  
        self.consume(al.TOKEN.tk_Rbrace, "Esperado '}' no fim do bloco.")

    def parse_declaration(self):
        self.consume(al.TOKEN.tk_Int, "Esperado 'int'.")

        ident = self.current_token()
        self.consume(al.TOKEN.tk_Ident, "Esperado identificador da variável.")

        # Registra a variável na tabela e detecta redeclaração no mesmo escopo
        if ident['type'] == al.TOKEN.tk_Ident:
            ok, existente = self.tabela.declarar(ident['value'], 'int', ident['line'], ident['col'])
            if not ok:
                self.erro_semantico(ident['line'], ident['col'],
                    f"Variável '{ident['value']}' já declarada neste escopo (linha {existente['linha']}).")

        if self.check(al.TOKEN.tk_Assign):
            self.advance()
            self.parse_expression()
            if ident['type'] == al.TOKEN.tk_Ident:
                self.tabela.inicializar(ident['value'])  # Declarada já com valor

        self.consume(al.TOKEN.tk_Semi, "Esperado ';' após a declaração.")

    def parse_if(self):
        self.consume(al.TOKEN.tk_If, "Esperado 'if'.")
        self.consume(al.TOKEN.tk_Lparen, "Esperado '(' após 'if'.")
        self.parse_expression()
        self.consume(al.TOKEN.tk_Rparen, "Esperado ')' após a condição do 'if'.")
        self.parse_statement()
        
        if self.check(al.TOKEN.tk_Else):
            self.advance()
            self.parse_statement()

    def parse_while(self):
        self.consume(al.TOKEN.tk_While, "Esperado 'while'.")
        self.consume(al.TOKEN.tk_Lparen, "Esperado '(' após 'while'.")
        self.parse_expression()
        self.consume(al.TOKEN.tk_Rparen, "Esperado ')' após a condição do 'while'.")
        self.parse_statement()

    def parse_for(self):
        self.consume(al.TOKEN.tk_For, "Esperado 'for'.")
        self.consume(al.TOKEN.tk_Lparen, "Esperado '(' após 'for'.")
        self.tabela.entrar_escopo()

        # Inicialização
        if self.check(al.TOKEN.tk_Int):
            self.parse_declaration()
        else:
            self.parse_expression_statement()
            
        # Condição
        self.parse_expression()
        self.consume(al.TOKEN.tk_Semi, "Esperado ';' após a condição do 'for'.")
        
        # Incremento
        self.parse_expression()
        self.consume(al.TOKEN.tk_Rparen, "Esperado ')' após os controles do 'for'.")

        self.parse_statement()
        self.tabela.sair_escopo() 

    def parse_expression_statement(self):
        self.parse_expression()
        self.consume(al.TOKEN.tk_Semi, "Esperado ';' no final do comando.")

    def parse_expression(self):
        nome = self.parse_primary()  # Devolve o nome do ident (ou None)

        if nome is not None and self.check(al.TOKEN.tk_Assign):
            self.tabela.inicializar(nome)

        operadores_binarios = {
            al.TOKEN.tk_Add, al.TOKEN.tk_Sub, al.TOKEN.tk_Mul, al.TOKEN.tk_Div, 
            al.TOKEN.tk_Mod, al.TOKEN.tk_Assign, al.TOKEN.tk_Eq, al.TOKEN.tk_Neq,
            al.TOKEN.tk_Lss, al.TOKEN.tk_Leq, al.TOKEN.tk_Gtr, al.TOKEN.tk_Geq,
            al.TOKEN.tk_And, al.TOKEN.tk_Or
        }
               
        while self.current_token()['type'] in operadores_binarios:
            self.advance() 
            self.parse_primary()
            
        if self.current_token()['type'] in {al.TOKEN.tk_Incr, al.TOKEN.tk_Decr}:
            self.advance()

    def parse_primary(self):
        curr = self.current_token()  # Guarda o token para consultar a tabela
        curr_type = curr['type']

        if curr_type == al.TOKEN.tk_Ident:
            nome = curr['value']
            self.advance()
            simbolo = self.tabela.buscar(nome)
            if simbolo is None:
                # Uso de variável que nunca foi declarada
                self.erro_semantico(curr['line'], curr['col'],
                    f"Variável '{nome}' usada sem ter sido declarada.")
            elif not simbolo['inicializada'] and not self.check(al.TOKEN.tk_Assign):
                # Leitura de variável declarada mas ainda sem valor
                print(f">>> [AVISO SEMÂNTICO L{curr['line']}:C{curr['col']}]: "
                      f"Variável '{nome}' pode ser usada sem ter sido inicializada.")
            return nome  # devolve o nome para o chamador tratar a atribuição
        # Se for um Número ou String
        elif curr_type in {al.TOKEN.tk_Integer, al.TOKEN.tk_String}:
            self.advance()
        # Se for uma expressão entre parênteses
        elif curr_type == al.TOKEN.tk_Lparen:
            self.advance()
            self.parse_expression()
            self.consume(al.TOKEN.tk_Rparen, "Esperado ')' após a expressão interna.")
        else:
            self.consume(al.TOKEN.error, "Expressão inválida (Esperado identificador, número ou '(').")

        return None


if __name__ == "__main__":
    print("Iniciando Análise Sintática...")
    
    try:
        lista_tokens = al.gera_lista_tokens()
    except Exception as e:
        print("Erro ao carregar tokens do analisador léxico. Verifique o arquivo codigo_fonte.txt")
        exit(1)
        
    parser = Parser(lista_tokens)
    parser.parse_program()

    parser.tabela.exibir() 

    print("-" * 55)
    if not parser.has_error:
        print("Sucesso: Nenhum erro encontrado.")
    else:
        print("Falha: A análise encontrou erros (veja os logs acima).")