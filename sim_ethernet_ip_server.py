import sys
import subprocess
import shutil
import os
import signal

from typing import Dict, Optional

import platform

'''
---------------------------------------------------------------------
-    Servidor Ethernet/IP
-   
-   Thiago Rodrigo Monteiro Salgado
-    Gledyson Cidade
-   
-    Universidade Federal do Amazonas 


Cria um servidor Ethernet/IP com base nas TAGs passadas 
como parâmetro no momento de criação da classe.

---------------------------------------------------------------------


'''

_IS_WIN = platform.system() == "Windows"

class EnipServer:
    def __init__(self, tags: Optional[Dict[str, str]] = None):
        
        if(tags == None):

            print("Impossível iniciar o servidor sem as TAGs.")
            exit(1)

        self.tags = tags
        self.proc: Optional[subprocess.Popen] = None

    def _graceful_signal(self, proc):
        try:
            if _IS_WIN:
                proc.terminate()
            else:
                proc.send_signal(signal.SIGINT)
        except Exception:
            pass

    def build_cmd(self) -> list:
        args = []
        
        args += ["-v"]
        for k, v in self.tags.items():
            args.append(f"{k}={v}")

        enip_path = shutil.which("enip_server")

        if enip_path:
            return [enip_path] + args
        return [sys.executable, "-m", "cpppo.server.enip.main"] + args

    def start(self) -> None:

        if self.proc and self.proc.poll() is None:
            return
        
        cmd = self.build_cmd()
        creationflags = 0

        if os.name == "nt":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True, creationflags=creationflags )

    def run(self) -> int:

        self.start()
        try:
            for line in self.proc.stdout:
                print(line, end="")
            return self.proc.wait()
        
        except KeyboardInterrupt:
            self.stop()
            return 0

    def stop(self) -> None:
        if not self.proc:
            return
        
        self._graceful_signal(self.proc)

        try:
            self.proc.wait(timeout=5)

        except Exception:
            try:
                self.proc.kill()
            except Exception:
                pass

        finally:
            self.proc = None

    @property
    def is_running(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self,):
        self.stop()

if __name__ == "__main__":

    tags = {
            "acceleration": "REAL",
            "speed_factor": "REAL",
            "inputs": "BOOL[8]",
            "outputs": "BOOL[8]",
        }
    
    server = EnipServer(tags)
    print("- Iniciando:", " ".join(server.build_cmd()))

    exit_code = server.run()
    print("\nEncerrado o servidor:", exit_code)
