import sys
import os

diretorio_atual = os.path.dirname(os.path.abspath(__file__))

caminho_lexico = os.path.join(diretorio_atual, '..', 'Analisador_lexico')

sys.path.append(caminho_lexico)

import al

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.has_error = False
        
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
        while not self.check(al.TOKEN.tk_EOI) and not self.check(al.TOKEN.tk_Rbrace):
            self.parse_statement()
        self.consume(al.TOKEN.tk_Rbrace, "Esperado '}' no fim do bloco.")

    def parse_declaration(self):
        self.consume(al.TOKEN.tk_Int, "Esperado 'int'.")
        self.consume(al.TOKEN.tk_Ident, "Esperado identificador da variável.")
        
        if self.check(al.TOKEN.tk_Assign):
            self.advance()
            self.parse_expression()
            
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

    def parse_expression_statement(self):
        self.parse_expression()
        self.consume(al.TOKEN.tk_Semi, "Esperado ';' no final do comando.")

    def parse_expression(self):
        self.parse_primary()
        
        # Lista de operadores que conectam expressões
        operadores_binarios = {
            al.TOKEN.tk_Add, al.TOKEN.tk_Sub, al.TOKEN.tk_Mul, al.TOKEN.tk_Div, 
            al.TOKEN.tk_Mod, al.TOKEN.tk_Assign, al.TOKEN.tk_Eq, al.TOKEN.tk_Neq,
            al.TOKEN.tk_Lss, al.TOKEN.tk_Leq, al.TOKEN.tk_Gtr, al.TOKEN.tk_Geq,
            al.TOKEN.tk_And, al.TOKEN.tk_Or
        }
               
        while self.current_token()['type'] in operadores_binarios:
            self.advance()  # Consome o operador (+, =, ==, etc)
            self.parse_primary()
            
        # Operadores unários (++, --)
        if self.current_token()['type'] in {al.TOKEN.tk_Incr, al.TOKEN.tk_Decr}:
            self.advance()

    def parse_primary(self):
        curr_type = self.current_token()['type']
        
        # Se for um Identificador, Número ou String
        if curr_type in {al.TOKEN.tk_Ident, al.TOKEN.tk_Integer, al.TOKEN.tk_String}:
            self.advance()
        # Se for uma expressão entre parênteses
        elif curr_type == al.TOKEN.tk_Lparen:
            self.advance()
            self.parse_expression()
            self.consume(al.TOKEN.tk_Rparen, "Esperado ')' após a expressão interna.")
        else:
            self.consume(al.TOKEN.error, "Expressão inválida (Esperado identificador, número ou '(').")


if __name__ == "__main__":
    print("Iniciando Análise Sintática...")
    
    try:
        lista_tokens = al.gera_lista_tokens()
    except Exception as e:
        print("Erro ao carregar tokens do analisador léxico. Verifique o arquivo codigo_fonte.txt")
        exit(1)
        
    parser = Parser(lista_tokens)
    parser.parse_program()
    
    print("-" * 55)
    if not parser.has_error:
        print("Sucesso: Nenhum erro encontrado.")
    else:
        print("Falha: A análise sintática encontrou erros (veja os logs acima).")