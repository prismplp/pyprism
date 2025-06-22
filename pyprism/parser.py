import re
import json

def tokenize(s):
    token_specification = [
        ('STRING',  r'\"(\\.|[^"\\])*\"|\'(\\.|[^\'\\])*\''),
        ('OP',      r'[\+\-\*/=><:]+'),  # 演算子
        ('NUMBER',  r'(?:\d+\.\d*|\.\d+|\d+)(?:[eE][\+\-]?\d+)?'),  # 小数 or 整数
        ('NAME',    r'[A-Za-z_][A-Za-z0-9_]*'),
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

# Priority (The higher the number, the more priority)
PRECEDENCE = {
    ':-': 0,
    '?-': 0,
    ';': 100,
    ',': 200,
    '=': 500,
    '<': 500, '>': 500,
    '=<': 500, '>=': 500,
    '==': 500, '=\=': 500,
    '=:=': 500, '\==': 500,
    '+': 700, '-': 700,
    '*': 800, '/': 800,
}

# Prefix operators (currently + and -)
PREFIX_OPS = {'+', '-', ':-'}

def parse_tuple_or_paren_expr(ts):
    items = []
    first = parse_expr(ts)
    items.append(first)

    while True:
        tok = ts.peek()
        if tok is None:
            raise SyntaxError("Unclosed ')'")
        if tok[0] == 'COMMA':
            ts.next()
            expr = parse_expr(ts)
            items.append(expr)
        elif tok[0] == 'RPAREN':
            ts.next()
            break
        else:
            raise SyntaxError(f"Unexpected token in tuple or paren: {tok}")

    if len(items) == 1:
        return items[0]
    else:
        return {'tuple': items}

def parse_expr(ts, min_prec=0):
    tok = ts.peek()
    if tok is None:
        raise SyntaxError("Unexpected end of input")

    kind, value = tok

    # Prefix unary operators
    if kind == 'OP' and value in PREFIX_OPS:
        ts.next()
        right = parse_expr(ts, PRECEDENCE[value])
        node = {'unary': value, 'expr': right}
    else:
        node = parse_atom(ts)

    # Precedence binary operators
    while True:
        tok = ts.peek()
        if tok is None or tok[0] != 'OP':
            break
        op = tok[1]
        prec = PRECEDENCE.get(op)
        if prec is None or prec < min_prec:
            break
        ts.next()
        rhs = parse_expr(ts, prec + 1)
        node = {'binop': op, 'left': node, 'right': rhs}

    return node



def parse_atom(ts):
    tok = ts.peek()
    if tok is None:
        raise SyntaxError("Unexpected end of input")

    kind, value = tok

    if kind == 'NAME' or kind == 'STRING':
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
        return float(value) if '.' in value or 'e' in value.lower() else int(value)

    elif kind == 'LPAREN':
        ts.next()
        return parse_tuple_or_paren_expr(ts)
        #expr = parse_expr(ts)
        #if ts.peek() and ts.peek()[0] == 'RPAREN':
        #    ts.next()
        #    return expr
        #else:
        #    raise SyntaxError("Expected ')'")
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

def parse_output_(obj):
    if isinstance(obj, dict) and 'binop' in obj:
        if obj['binop']=="=":
            s1=serialize_term(obj['left'])
            s2=serialize_term(obj['right'])
            return (s1, s2)
    return None

def parse_output(s):
    obj=parse_term("("+s+")")
    if isinstance(obj, dict) and 'tuple' in obj:
        return [parse_output_(o) for o in obj["tuple"]]
    else:
        if isinstance(obj, dict) and 'binop' in obj:
            return [parse_output_(obj)]

def serialize_term(obj, unary_op_paren=True, binary_op_paren=True):
    name_pattern=re.compile(r'^[A-Za-z_][A-Za-z_0-9]*$')
    if isinstance(obj, dict) and 'name' in obj:
        # function
        func = obj['name']
        args = ','.join(serialize_term(arg) for arg in obj['args'])
        return f"{func}({args})"
    if isinstance(obj, dict) and 'unary' in obj:
        # unary op
        name = obj["unary"]
        expr = serialize_term(obj["expr"])
        if unary_op_paren:
            return f"({name}{expr})"
        else:
            return f"{name}{expr}"
    if isinstance(obj, dict) and 'binop' in obj:
        # binary op
        name = obj["binop"]
        lhs = serialize_term(obj["left"])
        rhs = serialize_term(obj["right"])
        if binary_op_paren:
            return f"({lhs}{name}{rhs})"
        else:
            return f"{lhs}{name}{rhs}"
    if isinstance(obj, dict) and 'tuple' in obj:
        # tuple
        return '(' + ','.join(serialize_term(item) for item in obj["tuple"]) + ')'
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
        status=sw["args"][1]
        values=sw["args"][2]
        params=sw["args"][3]
        
        sw_list.append({"term":s,
                        "term_obj":obj,
                        "status":status,
                        "values":values,
                        "params":params})
  return sw_list

def read_sw_data(filename,use_array=False):
  sw_list=read_sw(filename)
  #[Name	Arity	Term	Status	Vals	Param	Arg1	Arg2	Arg3	Arg4	Arg5]
  data=[]
  for el in sw_list:
    name=el["term_obj"]["name"] if "name" in el["term_obj"] else str(el["term_obj"])
    arity=len(el["term_obj"]["args"]) if "name" in el["term_obj"] else 0
    args=[pyprism.serialize_term(el) for el in el["term_obj"]["args"]] if "name" in el["term_obj"] else []
    if use_array:
      l=[name,arity,el["term"],el["status"],el["values"],el["params"]]
    else:
      l=[name,arity,el["term"],el["status"],"["+",".join(map(str,el["values"]))+"]","["+",".join(map(str,el["params"]))+"]"]
    data.append((l,args))
  n_arg=max(max([len(args) for line,args in data]),5)
  return data,n_arg

def sw2tsv(filename,out_filename):
  data,m = read_sw_data(filename)
  with open(out_filename,"w") as ofp:
    h1=["Name","Arity","Term","Status","Vals","Param"]
    h2=["Arg"+str(i+1) for i in range(m)]
    ofp.write("\t".join(h1+h2))
    ofp.write("\n")
    for line,args in data:
      line_=line+args+[""]*(m-len(args))
      ofp.write("\t".join(map(str,line_)))
      ofp.write("\n")

