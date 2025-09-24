from flask import Flask, request, jsonify
from cpppo.server.enip.get_attribute import proxy_simple
from typing import Iterable, Optional, Protocol

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
first_time = True


app = Flask(__name__)

class EthernetIPProxy:

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


    def write_bool_array(self, tag: str, bools: list[bool]) -> bool:
        data = "(BOOL)" + ",".join("1" if b else "0" for b in bools)
        return self.write(tag, data)


    def read_bool_array(self, tag: str) -> list[bool]:
        values, = self.connection.read([tag])
        return list(values)
    
    def write(self, tag: str, value: str) -> bool:
        ok, = self.connection.write([f"{tag}={value}"])
        return ok
    
    def read(self, tag: str):
        value, = self.connection.read([tag])
        return value[0]


@app.route("/acceleration", methods=["GET"])
def get_acceleration():
    with EthernetIPProxy() as plc:
        value = plc.read('acceleration')
        return jsonify(value)


@app.route("/speed_factor", methods=["GET"])
def get_speed_factor():
    with EthernetIPProxy() as plc:
        value = plc.read('speed_factor')
        return jsonify(value)


@app.route("/acceleration", methods=["POST"])
def set_acceleration():
    value = request.json.get("value")
    if value is None:
        return jsonify({"error": "Missing 'value' in request"}), 400
    with EthernetIPProxy() as plc:
        ok = plc.write("acceleration", str(value))
        return jsonify({"success": ok})


@app.route("/speed_factor", methods=["POST"])
def set_speed_factor():
    value = request.json.get("value")
    if value is None:
        return jsonify({"error": "Missing 'value' in request"}), 400
    with EthernetIPProxy() as plc:
        ok = plc.write("speed_factor", str(value))
        return jsonify({"success": ok})


@app.route("/outputs/<int:index>", methods=["GET"])
def get_output(index):

    with EthernetIPProxy() as plc:
        outputs = plc.read_bool_array("outputs[0-7]")
        return jsonify(outputs[index])
    
@app.route("/inputs/<int:index>", methods=["GET"])
def get_input(index):

    with EthernetIPProxy() as plc:
        outputs = plc.read_bool_array("inputs[0-7]")
        return jsonify(outputs[index])


@app.route("/outputs/<int:index>", methods=["POST"])
def toggle_output(index):
    with EthernetIPProxy() as plc:
        outputs = plc.read_bool_array("outputs[0-7]")

        if index < 0 or index >= len(outputs):
            return jsonify({"error": "Index out of range"}), 400

        outputs[index] = not outputs[index]

        plc.write_bool_array("outputs[0-7]", outputs)

        return jsonify({f"outputs[{index}]": outputs[index]})
    

@app.route("/inputs/<int:index>", methods=["POST"])
def toggle_input(index):
    with EthernetIPProxy() as plc:
        inputs = plc.read_bool_array("inputs[0-7]")

        if index < 0 or index >= len(inputs):
            return jsonify({"error": "Index out of range"}), 400

        inputs[index] = not inputs[index]

        plc.write_bool_array("inputs[0-7]", inputs)

        return jsonify({f"inputs[{index}]": inputs[index]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)