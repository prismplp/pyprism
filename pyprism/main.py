import os
import glob
import subprocess
import datetime as dt
import argparse
import typing as t

def run(code):
    now = dt.datetime.now()
    filename = now.strftime('%Y%m%d-%H%M%S.psm')
    with open(filename,"w") as fp:
        fp.write(code)
    return run_file(filename)

def run_file(filename, args=[]):
    path=os.path.dirname(__file__)
    files = glob.glob(path+"/*")
    cmd=path+"/bin/upprism"
    cmds=[cmd, filename]+args
    out=subprocess.run(cmds,timeout=None)
    return out

def main(argv: t.Optional[t.List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
            prog='PROG', usage='%(prog)s [options]',
            description='このプログラムの説明（なくてもよい）')
    parser.add_argument('filename', help='input file')
    args, rest_argv = parser.parse_known_args(argv)
    run_file(args.filename, args=rest_argv)

if __name__ == "__main__":
    main()


