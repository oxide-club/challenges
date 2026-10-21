"""Lexer inicial: apenas classificação; parsing e limites cabem ao participante."""
def tokens(text):
    i = 0
    while i < len(text):
        if text[i] in " \t\r\n\v\f":
            i += 1
        elif "0" <= text[i] <= "9":
            start = i
            while i < len(text) and "0" <= text[i] <= "9":
                i += 1
            yield ("INTEGER", text[start:i])
        elif text[i] in "+-*()":
            yield (text[i], text[i])
            i += 1
        else:
            raise ValueError(f"caractere inválido na posição {i}")
