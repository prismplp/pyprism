# coding: utf-8

# ===== DEFINITIONS =====

from IPython.kernel.zmq.kernelbase import Kernel
from pexpect import replwrap, EOF
from subprocess import check_output

import re
import signal
import uuid

__version__ = '0.0.1'

version_pat = re.compile(r'(\d+\.\d+)')
crlf_pat = re.compile(r'[\r\n]+')

class PRISMKernel(Kernel):
    implementation = 'prism_kernel'
    implementation_version = __version__

    _language_version = None

    @property
    def language_version(self):
        if self._language_version is None:
            m = version_pat.search(check_output(['upprism', '--version']).decode('utf-8'))
            prompt = "| ?- "
            prism = replwrap.REPLWrapper("prism",prompt, None)
            o=prism.run_command('get_version(X)')
            m=version_pat.search(o)
            self._language_version = m.group(1)
        return self._language_version


    @property
    def banner(self):
        return u'Simple PRISM Kernel (PRISM v%s)' % self.language_version


    language_info = {'name': 'prism',
                     'codemirror_mode': 'prolog',
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
        prompt = "| ?- "
        try:
            self.prismwrapper = replwrap.REPLWrapper("prism", prompt, None)
        finally:
            signal.signal(signal.SIGINT, sig)


    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        code = crlf_pat.sub(' ', code.strip())
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
    IPKernelApp.launch_instance(kernel_class=PRISMKernel)
