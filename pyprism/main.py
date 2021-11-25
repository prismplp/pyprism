import os
import glob
import subprocess
import datetime as dt
import argparse
import typing as t

def run_(code, args=[]):
    prism_wd_path = './.prism_code/'
    now = dt.datetime.now()
    os.makedirs(prism_wd_path,exist_ok=True)
    filename = prism_wd_path+now.strftime('%Y%m%d-%H%M%S.psm')
    with open(filename,"w") as fp:
        fp.write(code)
    return run_file(filename,args)

def run(code, args=[]):
    r=run_(code,args)
    return r.stdout.decode("utf8")


def run_file_(filename, args=[]):
    path=os.path.dirname(__file__)
    cmd=path+"/bin/upprism"
    cmds=[cmd, filename]+args
    out=subprocess.run(cmds,timeout=None,stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    return out

def run_file(filename, args=[]):
    r=run_file_(filename,args)
    return r.stdout.decode("utf8")

def main(argv: t.Optional[t.List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
            prog='PROG', usage='%(prog)s [options]',
            description='pyprism')
    parser.add_argument('filename', help='input file')
    args, rest_argv = parser.parse_known_args(argv)
    o=run_file(args.filename, args=rest_argv)
    print("==stdout==")
    print(o.stdout.decode("utf8"))
    print("==stderr==")
    print(o.stderr.decode("utf8"))

if __name__ == "__main__":
    main()


