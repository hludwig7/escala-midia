
import os
from collections import Counter
from pathlib import Path
from tempfile import NamedTemporaryFile

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter

from modelos import EscalaDia, FUNCOES
from config import ARQUIVO_ESCALA


NOMES_COLUNAS = {
    "projecao": "Projeção",
    "live": "Live",
    "mesaDeSom": "Mesa de Som",
    "mesaDeSomLive": "Mesa de Som Live",
    "fotografia": "Fotografia",
    "auxiliar": "Auxiliar",
}

COLUNAS_EXCEL = [
    "Dia",
    "Manhã",
    *[NOMES_COLUNAS[funcao] for funcao in FUNCOES],
]


def criar_arquivo_excel(
    escala: list[EscalaDia],
    caminho: Path = ARQUIVO_ESCALA,
) -> None:

    if not escala:
        raise ValueError("A escala está vazia.")

    # Valida os dados antes de iniciar a criação.
    for item in escala:

        if set(item.noite) != set(FUNCOES):
            raise ValueError(
                f"Dia {item.dia}: existem funções ausentes ou inválidas."
            )

        pessoas_dia = [
            item.manha,
            *item.noite.values()
        ]

        if len(pessoas_dia) != 7 or len(set(pessoas_dia)) != 7:
            raise ValueError(
                f"Dia {item.dia}: existem pessoas repetidas na escala."
            )

    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    workbook = Workbook()

    # Remove a planilha padrão e cria uma nova com tipo conhecido.
    if workbook.worksheets:
        workbook.remove(workbook.worksheets[0])

    worksheet: Worksheet = workbook.create_sheet(
        title="Escala"
    )

    # Cria o cabeçalho.
    worksheet.append(COLUNAS_EXCEL)

    # Preenche os dados.
    for item in escala:

        linha = [
            item.dia,
            item.manha,
            *[
                item.noite[funcao]
                for funcao in FUNCOES
            ],
        ]

        worksheet.append(linha)

    # Formatação do cabeçalho.
    for celula in worksheet[1]:

        celula.fill = PatternFill(
            fill_type="solid",
            fgColor="1F4E78"
        )

        celula.font = Font(
            bold=True,
            color="FFFFFF"
        )

        celula.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    worksheet.row_dimensions[1].height = 25
    worksheet.freeze_panes = "A2"
    worksheet.sheet_view.showGridLines = False

    # Formatação das células.
    for linha in worksheet.iter_rows(min_row=2):

        for celula in linha:

            celula.alignment = Alignment(
                horizontal="center",
                vertical="center"
            )

    # Ajuste automático da largura das colunas.
    for indice, nome_coluna in enumerate(
        COLUNAS_EXCEL,
        start=1
    ):

        valores = [
            str(
                worksheet.cell(
                    row=linha,
                    column=indice
                ).value or ""
            )
            for linha in range(1, worksheet.max_row + 1)
        ]

        maior_comprimento = max(
            len(valor)
            for valor in valores
        )

        letra = get_column_letter(indice)

        worksheet.column_dimensions[letra].width = min(
            maior_comprimento + 3,
            32
        )

    # Criação da tabela do Excel.
    tabela = Table(
        displayName="TabelaEscala",
        ref=worksheet.dimensions
    )

    estilo = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )

    tabela.tableStyleInfo = estilo
    worksheet.add_table(tabela)

    caminho_temporario = None

    try:

        with NamedTemporaryFile(
            prefix=".escala_",
            suffix=".xlsx",
            dir=caminho.parent,
            delete=False,
        ) as temporario:

            caminho_temporario = Path(temporario.name)

        workbook.save(caminho_temporario)

        # Substitui o arquivo anterior somente após salvar
        # completamente a nova planilha.
        os.replace(
            caminho_temporario,
            caminho
        )

    finally:

        workbook.close()

        if caminho_temporario is not None:
            caminho_temporario.unlink(missing_ok=True)


def ler_pessoas_escaladas(
    caminho: Path = ARQUIVO_ESCALA,
) -> Counter[str]:

    caminho = Path(caminho)

    if not caminho.is_file():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    if caminho.stat().st_size == 0:
        raise ValueError(
            "O arquivo Excel está vazio (0 bytes)."
        )

    workbook = load_workbook(
        caminho,
        read_only=True,
        data_only=True
    )

    try:

        if "Escala" not in workbook.sheetnames:
            raise ValueError(
                "A planilha não possui uma aba chamada 'Escala'."
            )

        worksheet = workbook["Escala"]

        cabecalho = next(
            worksheet.iter_rows(
                min_row=1,
                max_row=1,
                values_only=True
            ),
            None
        )

        if cabecalho is None:
            raise ValueError("A planilha está vazia.")

        indices_colunas = {
            nome: indice
            for indice, nome in enumerate(cabecalho)
        }

        colunas_faltantes = [
            coluna
            for coluna in COLUNAS_EXCEL
            if coluna not in indices_colunas
        ]

        if colunas_faltantes:
            raise ValueError(
                f"Colunas ausentes: {colunas_faltantes}"
            )

        historico: Counter[str] = Counter()

        for linha in worksheet.iter_rows(
            min_row=2,
            values_only=True
        ):

            for coluna in COLUNAS_EXCEL[1:]:

                indice = indices_colunas[coluna]

                nome = (
                    linha[indice]
                    if indice < len(linha)
                    else None
                )

                if isinstance(nome, str) and nome.strip():
                    historico[nome.strip()] += 1

        return historico

    finally:
        workbook.close()
