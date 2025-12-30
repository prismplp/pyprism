import pyprism

s1="i"
s2="','(i,  10, 20  )"
s3="','(j,'-' , 20 )"
s4="','(k, 15 , 15 )"
s5="a30a"
s6="','(l, 10 ,- )"
s7="','(f(10),10010,vddd)"

for s in [s1,s2,s3,s4,s5,s6,s7]:
    a=pyprism.parse_term(s)
    print(a)
    print(">>>", pyprism.serialize_term(a))



