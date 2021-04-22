# coding: utf-8

# ===== DEFINITIONS =====

from IPython.kernel.zmq.kernelbase import Kernel
from pexpect import replwrap, EOF
from subprocess import check_output

import re
import signal
import uuid
import os

__version__ = '0.0.1'

version_pat = re.compile(r'(\d+(\.\d+)+)')
crlf_pat = re.compile(r'[\r\n]+')
space_pat = re.compile(r'[\r\n\s ]+')
prism_wd_path = './.prism_code/'

class PRISMKernel(Kernel):
    implementation = 'prism_kernel'
    implementation_version = __version__

    _language_version = None

    @property
    def language_version(self):
        if self._language_version is None:
            #m = version_pat.search(check_output(['prism', '--version']).decode('utf-8'))
            self._language_version = "1"#m.group(1)
        return self._language_version


    @property
    def banner(self):
        return u'Simple PRISM Kernel (PRISM v%s)' % self.language_version


    language_info = {'name': 'prism',
                     'codemirror_mode': 'scheme',
                     'mimetype': 'text/plain',
                     'file_extension': '.psm'}


    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self._start_prism()


    def _start_prism(self):
        # Signal handlers are inherited by forked processes, and we can't easily
        # reset it from the subprocess. Since kernelapp ignores SIGINT except in
        # message handlers, we need to temporarily reset the SIGINT handler here
        # so that PRISM is interruptible.
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        prompt = "| ?-"
        try:
            self.prismwrapper = replwrap.REPLWrapper("prism", prompt, None)
        finally:
            signal.signal(signal.SIGINT, sig)


    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        #code = crlf_pat.sub(' ', code.strip())
        code_list = re.split(crlf_pat,code.strip())
        new_code_list=[]
        file_block_code=[]
        for line in code_list:
            line=line.strip()
            if line[:2]=="#!":
                file_block_code=re.split(space_pat,line)
            else:
                new_code_list.append(line)
        code=" ".join(new_code_list)
        if len(file_block_code)>1:
            if file_block_code[1]=="prism-code":
                if len(file_block_code)>2:
                    name=os.path.basename(file_block_code[2])
                    filename=prism_wd_path+name+".psm"
                    with open(filename,"w") as fp:
                        for line in new_code_list:
                            fp.write(line)
                            fp.write("\n")
                    message = {'name': 'stdout', 'text': "[SAVE] "+name}
                else:
                    message = {'name': 'stdout', 'text': "unknown name"}
                self.send_response(self.iopub_socket, 'stream', message)
                return {'status': 'ok', 'execution_count': self.execution_count,
                        'payload': [], 'user_expressions': {}}
            else:
                message = {'name': 'stdout', 'text': "unknown command"+file_block_code[1]}
                self.send_response(self.iopub_socket, 'stream', message)
                return {'status': 'abort', 'execution_count': self.execution_count}
        if not code:
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}

        interrupted = False
        try:
            output = self.prismwrapper.run_command(code, timeout=None)
        except KeyboardInterrupt:
            self.prismwrapper.child.sendintr()
            interrupted = True
            self.prismwrapper._expect_prompt()
            output = self.prismwrapper.child.before
        except EOF:
            output = self.prismwrapper.child.before + 'Restarting PRISM'
            self._start_prism()

        if not silent:
            # Send standard output
            stream_content = {'name': 'stdout', 'text': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        if interrupted:
            return {'status': 'abort', 'execution_count': self.execution_count}

        return {'status': 'ok', 'execution_count': self.execution_count,
                'payload': [], 'user_expressions': {}}


# ===== MAIN =====
if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    os.makedirs(prism_wd_path,exist_ok=True)
    #os.chdir(prism_wd_path)
    IPKernelApp.launch_instance(kernel_class=PRISMKernel)
