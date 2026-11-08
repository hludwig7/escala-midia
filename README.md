# Escala de Mídia — IPB Central

Aplicação de linha de comando para automatizar a criação da escala da equipe
de mídia da Igreja Presbiteriana do Brasil (IPB) Central. O programa distribui
as pessoas pelas funções cadastradas, considera a disponibilidade e o histórico
de escalas e exporta o resultado para uma planilha Excel.

## Requisitos

- Python 3.10 ou superior
- `openpyxl`

## Instalação

No terminal, na pasta do projeto:

```bash
python -m venv .venv
```

Ative o ambiente virtual e instale a dependência:

```bash
# Linux ou macOS
source .venv/bin/activate
python -m pip install openpyxl
```

No Windows (PowerShell), ative o ambiente com:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install openpyxl
```

## Como usar

Execute o programa a partir da pasta do projeto:

```bash
python main.py
```

Informe a quantidade de dias para a escala quando solicitado. Os dias são
numerados sequencialmente a partir de 1; o programa não solicita datas do
calendário.

O arquivo será criado em `escala/escala_arquivo.xlsx`. Se já houver uma escala
nesse caminho, o programa a usa como histórico e então a substitui pela nova
escala.

## Cadastro da equipe

Edite a função `obter_pessoas()` em `main.py` para cadastrar as pessoas reais da
equipe. Os nomes que já estão no código são exemplos e devem ser ajustados para
a realidade da IPB Central.

Cada cadastro usa estes campos:

```python
Pessoa(
    nome="Nome da pessoa",
    funcoes={"projecao", "live"},
    disponivel_manha=True,
    indisponibilidade={2, 5},
)
```

- `nome`: nome usado para identificar a pessoa na escala.
- `funcoes`: conjunto das funções que a pessoa pode exercer.
- `disponivel_manha`: indica se a pessoa pode servir pela manhã.
- `indisponibilidade`: dias numerados em que a pessoa não pode servir; pode ser
  omitido quando não houver indisponibilidades.

As funções aceitas são:

| Identificador | Nome na planilha |
| --- | --- |
| `projecao` | Projeção |
| `live` | Live |
| `mesaDeSom` | Mesa de Som |
| `mesaDeSomLive` | Mesa de Som Live |
| `fotografia` | Fotografia |
| `auxiliar` | Auxiliar |

Cada dia da escala precisa de uma pessoa para a manhã e uma pessoa diferente
para cada uma das seis funções noturnas. Uma mesma pessoa não pode ocupar mais
de uma posição no mesmo dia. Se as disponibilidades e funções cadastradas não
permitirem completar algum dia, o programa informa que não foi possível montar
a escala.

## Como funciona a distribuição

A escala é gerada com escolhas aleatórias ponderadas: pessoas com menos
participações no histórico e na escala em construção têm maior chance de serem
escolhidas. Quem trabalhou no dia anterior recebe um peso menor para o dia
seguinte. O algoritmo também tenta combinações alternativas quando uma escolha
impede preencher todas as posições.

O histórico é lido da planilha existente, contando as participações de cada
pessoa na manhã e nas funções noturnas. Sem uma planilha anterior válida, a
geração começa sem histórico.

## Estrutura do projeto

```text
.
├── config.py       # Caminho da planilha de saída
├── escalador.py    # Lógica para distribuir as pessoas
├── main.py         # Cadastro da equipe e execução do programa
├── modelos.py      # Modelos Pessoa e EscalaDia e funções válidas
├── planilha.py     # Leitura do histórico e criação do Excel
└── escala/
    └── escala_arquivo.xlsx
```
