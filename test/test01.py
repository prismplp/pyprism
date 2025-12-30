import pyprism

tokens=pyprism.TokenStream(pyprism.tokenize(":-f(-1+2*3)"))
tokens
while True:
    tok = tokens.next()
    if tok is None:
        break
    print(tok)


a=pyprism.parse_term("fff")
print(a)
print(pyprism.serialize_term(a))
a=pyprism.parse_term("f(-x, y+1)")
print(a)
print(pyprism.serialize_term(a))
a=pyprism.parse_term("[X=10,Y=f(aaa,bbb)]")
print(a)
print(pyprism.serialize_term(a))
a=pyprism.parse_term(":-f(-x=:=y+1)")
print(a)
print(pyprism.serialize_term(a))
a=pyprism.parse_term("(X=10+30,Y=f(g(x)),Z=www)")
print(a)
print(pyprism.serialize_term(a))

a=pyprism.parse_term("X=1+(2+3)*4)")
s=pyprism.serialize_term(a)
print(s)
a=pyprism.parse_term(s)
print(a)
print(pyprism.serialize_term(a))

a=pyprism.parse_output("X='10+30',Y=20+f(g(x)),Z=www")
print(a)
