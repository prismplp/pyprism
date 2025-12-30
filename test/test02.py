from pyprism import PrismEngine
import pyprism

engine=PrismEngine(bin_path="../prism/bin")
db="""
mem(N, A,B) :- member(A,[1,2,3,4,5,6,7,8,9]),member(B,[1,2,3,4,5,6,7,8,9]), N is A+B.
"""

engine.set_db(db)

query='mem(8, A, Z),mem(8, X, Y)'
engine.query(query,verbose=True, find_n=10, out=["A","Z","X","Y"])
