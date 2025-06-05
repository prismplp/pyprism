import os
import glob
import subprocess
import datetime as dt
import argparse
import typing as t

class PrismEngine:
    def __init__(self,bin_path=None, wd_path='./.prism_code/'):
        if bin_path is None:
            path=os.path.dirname(os.path.abspath(__file__))
            bin_path=path+"/bin"
        
        self.bin_path=bin_path
        self.wd_path=wd_path
        self.result_stdout=None
        self.result_stderr=None
        self.db=""
    
    def set_db(self, code):
        self.db=code

    def query(self, q, args=[]):
        ### generate query
        if q.strip()[-1]==".":
            code=self.db+"\nprism_main :-"+q+"\n"
        else:
            code=self.db+"\nprism_main :-"+q+".\n"
        ### run
        out=self.run(code,args)
        if len(out)<7:
            return None, "error"
        open_msg=out[:7]
        warn_msg=[]
        load_msg=[]
        msgs=[]
        ret_msg=""
        prev=None
        for el in out[7:]:
            if el[:10]=="** Warning":
                warn_msg.append(el)
            elif el[:9]=="loading::":
                load_msg.append(el)
            else:
                msgs.append(el)
        if len(msgs)<3:
            return None, "error"
        return msgs[:-3], msgs[-2]

    def run(self, code, args=[]):
        now = dt.datetime.now()
        os.makedirs(self.wd_path,exist_ok=True)
        filename = self.wd_path+"/"+now.strftime('%Y%m%d-%H%M%S.psm')
        with open(filename,"w") as fp:
            fp.write(code)
        return self.run_file(filename,args)

    def run_file_(self,filename, args=[]):
        cmd=self.bin_path+"/upprism"
        cmds=[cmd, filename]+args
        out=subprocess.run(cmds,timeout=None,stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        return out

    def run_file(self, filename, args=[]):
        r=self.run_file_(filename,args)
        self.result_stdout=r.stdout.decode("utf8").split("\n")
        self.result_stderr=r.stderr.decode("utf8").split("\n")
        return self.result_stdout

PRISMEngine = PrismEngine # compatibility

def main():
    engine=PRISMEngine()
    print(engine.bin_path)
    o=engine.run("""prism_main([]):-format("hello world\n").""")
    print("==stdout==")
    print(o)
    print("==stderr==")
    print(engine.result_stderr)

if __name__ == "__main__":
    main()


