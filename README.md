# Communication Protocols and Industrial Applications

## Mestrado

**Students:**

- Thiago Rodrigo Monteiro Salgado
- Gledyson Cidade

---

## Getting Started

Este repositório contém exemplos básicos de protocolos de comunicação industrial, com foco em **Ethernet/IP**.

### Requisitos

- Python 3.9+
- Biblioteca [cpppo](https://github.com/pjkundert/cpppo) instalada:
  ```bash
  pip install cpppo
  ```

### Commands

```bash
enip_server -v Register1=INT Temperature=REAL Flags=BOOL[8]
```

then you will initialize a server Ethernet/IP with:

- Variable called Register and with type INT;
- Variable called Temperature and with type Real;
- Variable called inputs and outputs with eight positions (list) each one and each one is boolean (just true or false), and we can control.
