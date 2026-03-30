import sys


class TOKEN:
    tk_EOI, tk_Mul, tk_Div, tk_Mod, tk_Add, tk_Sub, tk_Incr, tk_Decr, tk_Not, tk_Lss, tk_Leq, tk_Gtr, \
    tk_Geq, tk_Eq, tk_Neq, tk_Assign, tk_And, tk_Or, tk_If, tk_Else, tk_While, tk_For,       \
    tk_Int, tk_Lparen, tk_Rparen, tk_Lbrace, tk_Rbrace, tk_Semi, tk_Comma, tk_Ident,          \
    tk_Integer, tk_String, error = range(33)

simbolos = ["EOI", "Op_multiply", "Op_divide", "Op_mod", "Op_add", "Op_subtract", 
            "Op_increment", "Op_decrement",
            "Op_not", "Op_less", "Op_lessequal", "Op_greater", "Op_greaterequal",
            "Op_equal", "Op_notequal", "Op_assign", "Op_and", "Op_or", "Keyword_if",
            "Keyword_else", "Keyword_while", "Keyword_for", "Keyword_int", "LeftParen",
            "RightParen", "LeftBrace", "RightBrace", "Semicolon", "Comma", "Identifier",
            "Integer", "String", "ERROR"]

separadores = { '{': TOKEN.tk_Lbrace, '}': TOKEN.tk_Rbrace, '(': TOKEN.tk_Lparen,
                ')': TOKEN.tk_Rparen, '+': TOKEN.tk_Add, '-': TOKEN.tk_Sub,
                '*': TOKEN.tk_Mul, '%': TOKEN.tk_Mod, ';': TOKEN.tk_Semi, ',': TOKEN.tk_Comma,
                '=': TOKEN.tk_Assign, '>': TOKEN.tk_Gtr, '<': TOKEN.tk_Lss,
                '!': TOKEN.tk_Not}

letras = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', \
          'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', \
          'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', \
          'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '_']

digito = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

linha = 1
coluna = 0
char_atual = ' '
entrada = None

def error(linha_ini, coluna_ini, msg):
    return(TOKEN.error, linha_ini, coluna_ini, msg)

def proximo_char():
    global char_atual, linha, coluna
    char_atual = entrada.read(1)
    coluna += 1
    if char_atual == '\n':
        linha += 1
        coluna =  0
    return char_atual

def eh_operador_composto(Op, linha_atual, coluna_atual):
    if Op == "=":
        if proximo_char() == "=": 
            if proximo_char().isspace():
                return TOKEN.tk_Eq, linha_atual, coluna_atual
            else:
                return error(linha_atual, coluna_atual, "operador não existe")
        else: 
            return TOKEN.tk_Assign, linha_atual, coluna_atual
    elif Op == ">":
        if proximo_char() == "=":
            if proximo_char().isspace():
                return TOKEN.tk_Geq, linha_atual, coluna_atual
            else:
                return error(linha_atual, coluna_atual, "operador não existe")
        else: return TOKEN.tk_Gtr, linha_atual, coluna_atual
    elif Op == "<":
        if proximo_char() == "=": 
            if proximo_char().isspace():
                return TOKEN.tk_Leq, linha_atual, coluna_atual
            else:
                return error(linha_atual, coluna_atual, "operador não existe")
        else: return TOKEN.tk_Lss, linha_atual, coluna_atual
    elif Op == "!":
        if proximo_char() == "=": 
            if proximo_char().isspace():
                return TOKEN.tk_Neq, linha_atual, coluna_atual
            else:
                return error(linha_atual, coluna_atual, "operador não existe")
        else: return TOKEN.tk_Not, linha_atual, coluna_atual
    elif Op == "&":
        if proximo_char() == "&": 
            if proximo_char().isspace():
                return TOKEN.tk_And, linha_atual, coluna_atual
            else:
                return error(linha_atual, coluna_atual, "operador não existe")
        else: return error(linha_atual, coluna_atual, "operador não existe")
    elif Op == "|":
        if proximo_char() == "|": 
            if proximo_char().isspace():
                return TOKEN.tk_Or, linha_atual, coluna_atual
            else:
                return error(linha_atual, coluna_atual, "operador não existe")
        else: return error(linha_atual, coluna_atual, "operador não existe")

    elif Op == "+":
        if proximo_char() == "+": 
            if proximo_char().isspace():
                return TOKEN.tk_Incr, linha_atual, coluna_atual
            else:
                return error(linha_atual, coluna_atual, "operador não existe")
        else: return TOKEN.tk_Add, linha_atual, coluna_atual
    
    elif Op == "-":
        if proximo_char() == "-": 
            if proximo_char().isspace():
                return TOKEN.tk_Decr, linha_atual, coluna_atual
            else:
                return error(linha_atual, coluna_atual, "operador não existe")
        else: return TOKEN.tk_Sub, linha_atual, coluna_atual


def eh_literal(linha_ini, coluna_ini):
    literal = ""
    while(True):
        proximo_char()
        if char_atual == '\"':
            proximo_char()
            return TOKEN.tk_String, linha_ini, coluna_ini, literal
        elif(len(char_atual)== 0):
            return error(linha_ini, coluna_ini, "faltou fechar as aspas")
        else:
            literal += char_atual
        
def eh_cmt_ou_div(linha_ini, coluna_ini):
    proximo_char()
    if char_atual == '/':
        while(len(proximo_char()) != 0):
            if char_atual == '\n':
                proximo_char()
                return "coment", linha_ini, coluna_ini
            elif len(char_atual) == 0:
                return pega_token()
        return error(linha_ini, coluna_ini, "erro no comentario")
    elif char_atual == '*':
        while(len(proximo_char()) != 0):
            if char_atual == '*':
                if proximo_char() == '/':
                    proximo_char()
                    return "coment", linha_ini, coluna_ini
        return error(linha_ini, coluna_ini, "nao fechou o comentario")
    elif char_atual.isspace():
        return TOKEN.tk_Div, linha_ini, coluna_ini
    

def eh_nume_ou_iden(linha_ini, coluna_ini):
    text = char_atual
    proximo_char()
    if char_atual in letras:
        text += char_atual
        while True:
            proximo_char()
            if char_atual.isspace():
                if text == "if":
                    return TOKEN.tk_If, linha_ini, coluna_ini
                elif text == "while":
                    return TOKEN.tk_While, linha_ini, coluna_ini
                elif text == "for":
                    return TOKEN.tk_For, linha_ini, coluna_ini
                elif text == "int":
                    return TOKEN.tk_Int, linha_ini, coluna_ini
                else:
                    return TOKEN.tk_Ident, linha_ini, coluna_ini, text
            elif char_atual in separadores:
                if text == "if":
                    return TOKEN.tk_If, linha_ini, coluna_ini
                elif text == "while":
                    return TOKEN.tk_While, linha_ini, coluna_ini
                elif text == "for":
                    return TOKEN.tk_For, linha_ini, coluna_ini
                elif text == "int":
                    return TOKEN.tk_Int, linha_ini, coluna_ini
                else:
                    return TOKEN.tk_Ident, linha_ini, coluna_ini, text
            elif char_atual.isalnum():
                text += char_atual
            elif char_atual == "_":
                text += char_atual
            else:
                return error(linha_ini, coluna_ini, "caracter invalido no identificador")
            
    elif char_atual.isdigit():
        text += char_atual
        while True:
            proximo_char()
            if char_atual.isdigit():
                text += char_atual
            elif char_atual.isspace():
                return TOKEN.tk_Integer, linha_ini, coluna_ini, int(text)
            elif char_atual in separadores:
                return TOKEN.tk_Integer, linha_ini, coluna_ini, int(text)
            else:
                return error(linha_ini, coluna_ini, "caracter invalido no inteiro")
    else: return error(linha_ini, coluna_ini, "identificador com caracteres invalidos")


def pega_token():
    while char_atual.isspace():
        proximo_char()

    linha_atual = linha
    coluna_atual = coluna

    if len(char_atual) == 0:    return TOKEN.tk_EOI, linha_atual, coluna_atual
    elif char_atual == '/':     return eh_cmt_ou_div(linha_atual, coluna_atual)
    elif char_atual == '"':     return eh_literal(linha_atual, coluna_atual)
    elif char_atual == '>':     return eh_operador_composto(char_atual, linha_atual, coluna_atual)
    elif char_atual == '<':     return eh_operador_composto(char_atual, linha_atual, coluna_atual)
    elif char_atual == '&':     return eh_operador_composto(char_atual, linha_atual, coluna_atual)
    elif char_atual == '|':     return eh_operador_composto(char_atual, linha_atual, coluna_atual)
    elif char_atual == '!':     return eh_operador_composto(char_atual, linha_atual, coluna_atual)
    elif char_atual == '=':     return eh_operador_composto(char_atual, linha_atual, coluna_atual)
    elif char_atual == '+':     return eh_operador_composto(char_atual, linha_atual, coluna_atual)
    elif char_atual == '-':     return eh_operador_composto(char_atual, linha_atual, coluna_atual)
    elif char_atual in separadores:
        sepa = separadores[char_atual]
        proximo_char()
        return sepa, linha_atual, coluna_atual
    else: return eh_nume_ou_iden(linha_atual, coluna_atual)


entrada = sys.stdin
if len(sys.argv) > 1:
    try:
        entrada = open(sys.argv[1], "r", 4096)
    except IOError as e:
        error(0, 0, "Can't open %s" % sys.argv[1])

while True:
    t = pega_token()
    tok = t[0]
    lin = t[1]
    col= t[2]
    
    if tok == "coment":
        continue

    print("%5d %5d  %5d   %-14s" % (tok, lin, col, simbolos[tok]), end='')

    if tok == TOKEN.tk_Integer:  print("   %5d" % (t[3]))
    elif tok == TOKEN.error:     print("  %s" %   (t[3]))
    elif tok == TOKEN.tk_Ident:  print("  %s" %   (t[3]))
    elif tok == TOKEN.tk_String: print('  "%s"' % (t[3]))
    else:                  print("")

    if tok == TOKEN.tk_EOI:
        break
