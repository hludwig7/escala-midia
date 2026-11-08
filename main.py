import logging
from collections import Counter
from zipfile import BadZipFile

from openpyxl.utils.exceptions import InvalidFileException
from config import ARQUIVO_ESCALA
from modelos import Pessoa
from escalador import montar_escala, EscalaImpossivelError
from planilha import (
    criar_arquivo_excel,
    ler_pessoas_escaladas,
)


logger = logging.getLogger(__name__)


def obter_pessoas() -> list[Pessoa]:
    """
    Retorna as pessoas cadastradas no sistema.

    Substitua os exemplos abaixo pelos dados reais.
    """

    return [
        Pessoa(
            nome="Davi",
            funcoes={"mesaDeSom"},
            disponivel_manha=False,
        ),
        Pessoa(
            nome="Satochi",
            funcoes={"mesaDeSom"},
            disponivel_manha=True,
        ),
        Pessoa(
            nome="Luis",
            funcoes={"mesaDeSom", "projecao", "live"},
            disponivel_manha=True,
        ),
        Pessoa(
            nome="Gabi Teles",
            funcoes={"projecao", "live"},
            disponivel_manha=False,
        ),
        Pessoa(
            nome="Alice",
            funcoes={"projecao", "live"},
            disponivel_manha=False,
        ),
        Pessoa(
            nome="Karen",
            funcoes={"projecao", "live"},
            disponivel_manha=True,
        ),
        Pessoa(
            nome="Guilherme",
            funcoes={"projecao", "live"},
            disponivel_manha=True,
        ),
        Pessoa(
            nome="Isadora",
            funcoes={"projecao", "live"},
            disponivel_manha=True,
        ),
        Pessoa(
            nome="Bruno",
            funcoes={"live", "mesaDeSomLive"},
            disponivel_manha=True,
        ),
        Pessoa(
            nome="Cezar",
            funcoes={"live", "mesaDeSomLive"},
            disponivel_manha=False,
        ),
        Pessoa(
            nome="Matheus Romeiro",
            funcoes={"live", "mesaDeSomLive"},
            disponivel_manha=True,
        ),
        Pessoa(
            nome="Miguel",
            funcoes={"auxiliar"},
            disponivel_manha=False,
        ),
        Pessoa(
            nome="Gabriel",
            funcoes={"auxiliar"},
            disponivel_manha=False,
        ),
        Pessoa(
            nome="Stephanie",
            funcoes={"projecao", "live"},
            disponivel_manha=False,
        ),
        Pessoa(
            nome="Laura",
            funcoes={"projecao", "live", "fotografia"},
            disponivel_manha=True,
        ),
        Pessoa(
            nome="Leticia",
            funcoes={"fotografia"},
            disponivel_manha=True,
        ),
        Pessoa(
            nome="Isa Duvalle",
            funcoes={"fotografia"},
            disponivel_manha=False,
        ),
        Pessoa(
            nome="Isinha",
            funcoes={"fotografia"},
            disponivel_manha=False,
        ),
        Pessoa(
            nome="Maria Gabriela",
            funcoes={"fotografia"},
            disponivel_manha=False,
        ),
    ]


def obter_quantidade_dias() -> int:
    """Solicita a quantidade de dias ao usuário."""

    while True:
        try:
            quantidade = int(
                input("Informe a quantidade de dias de trabalho: ")
            )

            if quantidade < 1:
                print("Informe um número maior que zero.")
                continue

            return quantidade

        except ValueError:
            print("Digite um número inteiro válido.")



logger = logging.getLogger(__name__)


def main() -> None:

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    # 1. Verifica o arquivo anterior.
    if ARQUIVO_ESCALA.is_file():

        logger.info("Arquivo anterior encontrado.")

        try:

            historico = ler_pessoas_escaladas(
                ARQUIVO_ESCALA
            )

            logger.info(
                "Histórico carregado: %s",
                dict(historico)
            )

        except (ValueError, BadZipFile, InvalidFileException) as erro:

            logger.warning(
                "Arquivo anterior inválido: %s",
                erro
            )

            logger.warning(
                "A nova escala será criada sem histórico anterior."
            )

            historico = Counter()

    else:

        logger.info("Nenhuma escala anterior encontrada.")

        historico = Counter()

    # 2. Obtém as pessoas.
    pessoas = obter_pessoas()

    logger.info(
        "Quantidade de pessoas cadastradas: %d",
        len(pessoas)
    )

    # 3. Obtém a quantidade de dias.
    quantidade_dias = obter_quantidade_dias()

    # 4. Monta a escala.
    try:

        escala = montar_escala(
            pessoas=pessoas,
            quantidade_dias=quantidade_dias,
            historico=historico,
        )

        logger.info(
            "Escala gerada: %d dias.",
            len(escala)
        )

    except EscalaImpossivelError:

        logger.exception(
            "Não foi possível montar a escala."
        )

        return

    # 5. Exporta para Excel.
    try:

        criar_arquivo_excel(
            escala=escala,
            caminho=ARQUIVO_ESCALA,
        )

        logger.info(
            "Arquivo criado com sucesso: %s",
            ARQUIVO_ESCALA
        )

    except (ValueError, TypeError, OSError):

        logger.exception(
            "Erro ao criar o arquivo Excel."
        )

        return


if __name__ == "__main__":
    main()
