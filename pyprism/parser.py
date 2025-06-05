import re
import json

def tokenize(s):
    token_specification = [
        ('STRING',  r'\"(\\.|[^"\\])*\"|\'(\\.|[^\'\\])*\''),
        ('NUMBER',  r'[\-e\d+\.\d]+|\d+'),  # 小数 or 整数
        ('NAME',    r'[A-Za-z_][A-Za-z_0-9]*'),
        ('COMMA',   r','),
        ('LPAREN',  r'\('),
        ('RPAREN',  r'\)'),
        ('LBRACK',  r'\['),
        ('RBRACK',  r'\]'),
        ('SKIP',    r'\s+'),
        ('OTHER',   r' '),
    ]
    tok_regex = '|'.join(f'(?P<{name}>{regex})' for name, regex in token_specification)
    for mo in re.finditer(tok_regex, s):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP':
            continue
        elif kind == 'OTHER':
            raise SyntaxError(f'Unexpected character: {value}')
        yield (kind, value)

class TokenStream:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def next(self):
        tok = self.peek()
        self.pos += 1
        return tok

def parse_expr(ts):
    tok = ts.peek()
    if tok is None:
        return None

    kind, value = tok

    if kind == 'NAME' or kind=='STRING':
        ts.next()
        next_tok = ts.peek()
        if next_tok and next_tok[0] == 'LPAREN':
            ts.next()
            args = parse_args(ts, end_kind='RPAREN')
            return {'name': value, 'args': args}
        else:
            return value

    elif kind == 'NUMBER':
        ts.next()
        return float(value) if '.' in value else int(value)

    elif kind == 'LPAREN':
        ts.next()
        return parse_args(ts, end_kind='RPAREN')

    elif kind == 'LBRACK':
        ts.next()
        return parse_args(ts, end_kind='RBRACK')

    else:
        raise SyntaxError(f'Unexpected token: {tok}')

def parse_args(ts, end_kind):
    items = []
    while True:
        tok = ts.peek()
        if tok is None:
            raise SyntaxError(f'Unclosed {end_kind}')
        if tok[0] == end_kind:
            ts.next()
            break
        elif tok[0] == 'COMMA':
            ts.next()
            continue
        else:
            items.append(parse_expr(ts))
    return items

def parse_term(s):
    tokens = TokenStream(tokenize(s))
    return parse_expr(tokens)

def serialize_term(obj):
    name_pattern=re.compile(r'^[A-Za-z_][A-Za-z_0-9]*$')
    if isinstance(obj, dict) and 'name' in obj:
        # function
        func = obj['name']
        args = ','.join(serialize_term(arg) for arg in obj['args'])
        return f"{func}({args})"
    elif isinstance(obj, list):
        return '[' + ','.join(serialize_term(item) for item in obj) + ']'
    elif isinstance(obj, str):
      if name_pattern.match(obj):
        return obj
      else:
        # 文字列はクォート（デフォルトはダブル）
        return '"' + obj.replace('"', '\\"') + '"'
    elif isinstance(obj, (int, float)):
        return str(obj)
    else:
        raise TypeError(f"Unsupported type: {type(obj)}")

def read_sw(filename):
  sw_list=[]
  for line in open(filename):
    l=line.strip()
    if len(l)>0:
      sw=parse_term(l[:-1])
      if sw["name"]=="switch":
        obj=sw["args"][0]
        s=serialize_term(obj)
        fixed_param=sw["args"][1]
        values=sw["args"][2]
        params=sw["args"][3]
        
        sw_list.append({"term":s,
                        "term_obj":obj,
                        "fixed":fixed_param,
                        "values":values,
                        "params":params})
  return sw_list
