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


class MipsGenerator:
    def __init__(self):
        self.data_section = []
        self.text_section = []
        self.label_count = 0
        self.string_count = 0

    def add_data(self, var_name, initial_value=0):
        # Add to .data if not already there (avoids duplicate data definitions)
        decl = f"var_{var_name}: .word {initial_value}"
        if decl not in self.data_section:
            self.data_section.append(decl)

    def add_string(self, string_val):
        label = f"str_{self.string_count}"
        self.string_count += 1
        self.data_section.append(f'{label}: .asciiz "{string_val}"')
        return label

    def emit(self, instruction):
        self.text_section.append(f"    {instruction}")

    def emit_label(self, label):
        self.text_section.append(f"{label}:")

    def new_label(self, prefix="L"):
        self.label_count += 1
        return f"{prefix}_{self.label_count}"

    def push(self, reg):
        self.emit("subu $sp, $sp, 4")
        self.emit(f"sw {reg}, ($sp)")

    def pop(self, reg):
        self.emit(f"lw {reg}, ($sp)")
        self.emit("addu $sp, $sp, 4")

    def get_code(self):
        code = ".data\n"
        code += "\n".join(self.data_section) + "\n\n"
        code += ".text\n.globl main\nmain:\n"
        code += "\n".join(self.text_section) + "\n"
        code += "    li $v0, 10\n    syscall\n"
        return code


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.has_error = False
        self.tabela = TabelaSimbolos()
        self.mips = MipsGenerator()

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
            
        if not self.has_error:
            with open("saida.asm", "w") as f:
                f.write(self.mips.get_code())
            print(">>> Código MIPS gerado em 'saida.asm'")

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
            else:
                self.mips.add_data(ident['value'])

        if self.check(al.TOKEN.tk_Assign):
            self.advance()
            self.parse_expression()
            if ident['type'] == al.TOKEN.tk_Ident:
                self.tabela.inicializar(ident['value'])  # Declarada já com valor
                self.mips.pop("$t0")
                self.mips.emit(f"sw $t0, var_{ident['value']}")

        self.consume(al.TOKEN.tk_Semi, "Esperado ';' após a declaração.")

    def parse_if(self):
        self.consume(al.TOKEN.tk_If, "Esperado 'if'.")
        self.consume(al.TOKEN.tk_Lparen, "Esperado '(' após 'if'.")
        self.parse_expression()
        self.consume(al.TOKEN.tk_Rparen, "Esperado ')' após a condição do 'if'.")
        
        label_else = self.mips.new_label("L_ELSE")
        label_end = self.mips.new_label("L_ENDIF")
        
        self.mips.pop("$t0")
        self.mips.emit(f"beq $t0, $zero, {label_else}")
        
        self.parse_statement()
        
        self.mips.emit(f"j {label_end}")
        self.mips.emit_label(label_else)
        
        if self.check(al.TOKEN.tk_Else):
            self.advance()
            self.parse_statement()
            
        self.mips.emit_label(label_end)

    def parse_while(self):
        self.consume(al.TOKEN.tk_While, "Esperado 'while'.")
        self.consume(al.TOKEN.tk_Lparen, "Esperado '(' após 'while'.")
        
        label_start = self.mips.new_label("L_WHILE_START")
        label_end = self.mips.new_label("L_WHILE_END")
        
        self.mips.emit_label(label_start)
        
        self.parse_expression()
        self.mips.pop("$t0")
        self.mips.emit(f"beq $t0, $zero, {label_end}")
        
        self.consume(al.TOKEN.tk_Rparen, "Esperado ')' após a condição do 'while'.")
        self.parse_statement()
        
        self.mips.emit(f"j {label_start}")
        self.mips.emit_label(label_end)

    def parse_for(self):
        self.consume(al.TOKEN.tk_For, "Esperado 'for'.")
        self.consume(al.TOKEN.tk_Lparen, "Esperado '(' após 'for'.")
        self.tabela.entrar_escopo()

        # Inicialização
        if self.check(al.TOKEN.tk_Int):
            self.parse_declaration()
        else:
            self.parse_expression_statement()
            
        label_start = self.mips.new_label("L_FOR_START")
        label_inc = self.mips.new_label("L_FOR_INC")
        label_body = self.mips.new_label("L_FOR_BODY")
        label_end = self.mips.new_label("L_FOR_END")
        
        self.mips.emit_label(label_start)
        
        # Condição
        self.parse_expression()
        self.mips.pop("$t0")
        self.mips.emit(f"beq $t0, $zero, {label_end}")
        self.mips.emit(f"j {label_body}")
        
        self.consume(al.TOKEN.tk_Semi, "Esperado ';' após a condição do 'for'.")
        
        self.mips.emit_label(label_inc)
        
        # Incremento
        self.parse_expression()
        self.mips.pop("$t0") # Discard expression result
        self.mips.emit(f"j {label_start}")
        
        self.consume(al.TOKEN.tk_Rparen, "Esperado ')' após os controles do 'for'.")

        self.mips.emit_label(label_body)
        self.parse_statement()
        self.mips.emit(f"j {label_inc}")
        
        self.mips.emit_label(label_end)
        
        self.tabela.sair_escopo() 

    def parse_expression_statement(self):
        self.parse_expression()
        self.mips.pop("$t0") # Discard result of standalone expression
        self.consume(al.TOKEN.tk_Semi, "Esperado ';' no final do comando.")

    def parse_expression(self):
        tipo, nome = self.parse_primary()

        if nome is not None and self.check(al.TOKEN.tk_Assign):
            self.tabela.inicializar(nome)

        operadores_binarios = {
            al.TOKEN.tk_Add, al.TOKEN.tk_Sub, al.TOKEN.tk_Mul, al.TOKEN.tk_Div,
            al.TOKEN.tk_Mod, al.TOKEN.tk_Assign, al.TOKEN.tk_Eq, al.TOKEN.tk_Neq,
            al.TOKEN.tk_Lss, al.TOKEN.tk_Leq, al.TOKEN.tk_Gtr, al.TOKEN.tk_Geq,
            al.TOKEN.tk_And, al.TOKEN.tk_Or
        }

        while self.current_token()['type'] in operadores_binarios:
            op = self.current_token()  
            self.advance()
            tipo_dir, nome_dir = self.parse_primary()
            
            # Operandos de tipos diferentes geram erro
            if tipo != 'unknown' and tipo_dir != 'unknown' and tipo != tipo_dir:
                self.erro_semantico(op['line'], op['col'],
                    f"Operação entre tipos incompatíveis: '{tipo}' e '{tipo_dir}'.")
            tipo = tipo if tipo != 'unknown' else tipo_dir  
            
            # MIPS emit
            if op['type'] == al.TOKEN.tk_Assign:
                if nome is not None:
                    self.mips.pop("$t0") # right
                    self.mips.pop("$t1") # left (discard)
                    self.mips.emit(f"sw $t0, var_{nome}")
                    self.mips.push("$t0")
            else:
                self.mips.pop("$t1") # right
                self.mips.pop("$t0") # left
                
                if op['type'] == al.TOKEN.tk_Add:
                    self.mips.emit("add $t0, $t0, $t1")
                elif op['type'] == al.TOKEN.tk_Sub:
                    self.mips.emit("sub $t0, $t0, $t1")
                elif op['type'] == al.TOKEN.tk_Mul:
                    self.mips.emit("mul $t0, $t0, $t1")
                elif op['type'] == al.TOKEN.tk_Div:
                    self.mips.emit("div $t0, $t1")
                    self.mips.emit("mflo $t0")
                elif op['type'] == al.TOKEN.tk_Mod:
                    self.mips.emit("div $t0, $t1")
                    self.mips.emit("mfhi $t0")
                elif op['type'] == al.TOKEN.tk_Eq:
                    self.mips.emit("seq $t0, $t0, $t1")
                elif op['type'] == al.TOKEN.tk_Neq:
                    self.mips.emit("sne $t0, $t0, $t1")
                elif op['type'] == al.TOKEN.tk_Lss:
                    self.mips.emit("slt $t0, $t0, $t1")
                elif op['type'] == al.TOKEN.tk_Leq:
                    self.mips.emit("sle $t0, $t0, $t1")
                elif op['type'] == al.TOKEN.tk_Gtr:
                    self.mips.emit("sgt $t0, $t0, $t1")
                elif op['type'] == al.TOKEN.tk_Geq:
                    self.mips.emit("sge $t0, $t0, $t1")
                elif op['type'] == al.TOKEN.tk_And:
                    self.mips.emit("and $t0, $t0, $t1")
                elif op['type'] == al.TOKEN.tk_Or:
                    self.mips.emit("or $t0, $t0, $t1")
                    
                self.mips.push("$t0")
                
            nome = nome_dir

        if self.current_token()['type'] in {al.TOKEN.tk_Incr, al.TOKEN.tk_Decr}:
            op_inc = self.current_token()
            self.advance()
            if nome is not None:
                self.mips.pop("$t0")
                if op_inc['type'] == al.TOKEN.tk_Incr:
                    self.mips.emit("add $t0, $t0, 1")
                else:
                    self.mips.emit("sub $t0, $t0, 1")
                self.mips.emit(f"sw $t0, var_{nome}")
                self.mips.push("$t0")

        return tipo 

    def parse_primary(self):
        curr = self.current_token()  
        curr_type = curr['type']

        if curr_type == al.TOKEN.tk_Ident:
            nome = curr['value']
            self.advance()
            simbolo = self.tabela.buscar(nome)
            if simbolo is None:
                self.erro_semantico(curr['line'], curr['col'],
                    f"Variável '{nome}' usada sem ter sido declarada.")
                self.mips.emit("li $t0, 0")
                self.mips.push("$t0")
                return 'unknown', nome
            elif not simbolo['inicializada'] and not self.check(al.TOKEN.tk_Assign):
                print(f">>> [AVISO SEMÂNTICO L{curr['line']}:C{curr['col']}]: "
                      f"Variável '{nome}' pode ser usada sem ter sido inicializada.")
                      
            self.mips.emit(f"lw $t0, var_{nome}")
            self.mips.push("$t0")
            return simbolo['tipo'], nome 
            
        elif curr_type == al.TOKEN.tk_Integer:
            val = curr['value']
            self.advance()
            self.mips.emit(f"li $t0, {val}")
            self.mips.push("$t0")
            return 'int', None
            
        elif curr_type == al.TOKEN.tk_String:
            val = curr['value']
            self.advance()
            label = self.mips.add_string(val)
            self.mips.emit(f"la $t0, {label}")
            self.mips.push("$t0")
            return 'string', None
            
        elif curr_type == al.TOKEN.tk_Lparen:
            self.advance()
            tipo = self.parse_expression()
            self.consume(al.TOKEN.tk_Rparen, "Esperado ')' após a expressão interna.")
            return tipo, None
        else:
            self.consume(al.TOKEN.error, "Expressão inválida (Esperado identificador, número ou '(').")
            self.mips.emit("li $t0, 0")
            self.mips.push("$t0")

        return 'unknown', None


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
