from cpppo.server.enip.get_attribute import proxy_simple
from typing import Iterable, Optional, Protocol

import threading

'''
-----------------------------------------------------------------------------
 
    Client Ethernet/IP

    Thiago Rodrigo Monteiro Salgado
    Gledyson Cidade

    Universidade Federal do Amazonas

-----------------------------------------------------------------------------

Cria um client Ethernet/IP, podendo ler ou escrever nas TAGs do 
servidor (produtor) Ethernet/IP. Este client é baseado no servidor
simulado no outro arquivo em python neste mesmo repositório 
(sim_ethernet_ip_server.py).
'''

class EthernetIPProxy:
    class _ClientProtocol(Protocol):
        def read(self, tags: list[str]) -> Iterable[tuple]: ...
        def write(self, tags: list[str]) -> Iterable[bool]: ...

    def __init__(self, host: str = "127.0.0.1", port: int = 44818, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.connection: Optional[EthernetIPProxy._ClientProtocol] = None

    def __enter__(self):
        self.connection = proxy_simple(self.host, port=self.port, timeout=self.timeout)
        self.connection.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.__exit__(exc_type, exc_val, exc_tb)

    def write(self, tag: str, value: str) -> bool:
        ok, = self.connection.write([f"{tag}={value}"])
        return ok

    def read(self, tag: str):
        value, = self.connection.read([tag])
        return value[0]

    def write_bool_array(self, tag: str, bools: list[bool]) -> bool:
        data = "(BOOL)" + ",".join("1" if b else "0" for b in bools)
        return self.write(tag, data)

    def read_bool_array(self, tag: str) -> list[bool]:
        values, = self.connection.read([tag])
        return list(values)

if __name__ == "__main__":

    with EthernetIPProxy() as plc:

        plc.read("acceleration")

        plc.write("acceleration", "350")
        plc.write("speed_factor", "80")

        # inputs = [True, False, False, True, False, False, False, False]
        # plc.write_bool_array("Flags[0-7]", flags)

        # reg = plc.read("Register1")
        temp = plc.read("acceleration")
        flags2 = plc.read_bool_array("inputs[0-7]")

        # print("Register1:", reg)
        print("Temperature:", temp)
        print("Flags[0-7]:", flags2)