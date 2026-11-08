FATOR_PESO_DIA_SEGUINTE = 0.5

from collections import Counter
from random import Random
from typing import Mapping, Sequence

from modelos import Pessoa, EscalaDia, FUNCOES


class EscalaImpossivelError(Exception):
    """Indica que não foi possível preencher um dia da escala."""



def _ordem_ponderada(
    candidatos: list[Pessoa],
    historico: Mapping[str, int],
    usos_atuais: Counter[str],
    trabalharam_dia_anterior: set[str],
    rng: Random,
) -> list[Pessoa]:

    restantes = list(candidatos)
    ordem = []

    while restantes:

        pesos = []

        for pessoa in restantes:

            # Peso baseado no histórico e na escala atual.
            peso = 1 / (
                1
                + historico.get(pessoa.nome, 0)
                + usos_atuais.get(pessoa.nome, 0)
            )

            # Penaliza quem trabalhou no dia anterior.
            if pessoa.nome in trabalharam_dia_anterior:
                peso *= FATOR_PESO_DIA_SEGUINTE

            pesos.append(peso)

        escolhida = rng.choices(
            restantes,
            weights=pesos,
            k=1
        )[0]

        ordem.append(escolhida)
        restantes.remove(escolhida)

    return ordem



def _buscar_atribuicoes_noturnas(
    pessoas: Sequence[Pessoa],
    dia: int,
    funcoes_restantes: tuple[str, ...],
    nomes_usados: set[str],
    historico: Mapping[str, int],
    usos_atuais: Counter[str],
    trabalharam_dia_anterior: set[str],
    rng: Random,
) -> dict[str, str] | None:
    """
    Encontra uma combinação válida para as funções da noite.

    Utiliza backtracking para tentar outras combinações
    quando uma escolha impossibilita completar a escala.
    """

    if not funcoes_restantes:
        return {}

    # Primeiro, verifica quantos candidatos existem para cada função.
    candidatos_por_funcao = {
        funcao: [
            pessoa
            for pessoa in pessoas
            if (
                pessoa.nome not in nomes_usados
                and dia not in pessoa.indisponibilidade
                and funcao in pessoa.funcoes
            )
        ]
        for funcao in funcoes_restantes
    }

    # Escolhe primeiro a função com menos candidatos.
    menor_quantidade = min(
        len(candidatos)
        for candidatos in candidatos_por_funcao.values()
    )

    funcoes_mais_restritas = [
        funcao
        for funcao, candidatos in candidatos_por_funcao.items()
        if len(candidatos) == menor_quantidade
    ]

    funcao_escolhida = rng.choice(funcoes_mais_restritas)

    candidatos = candidatos_por_funcao[funcao_escolhida]

    if not candidatos:
        return None

    # Tenta os candidatos em ordem aleatória ponderada.
    ordem = _ordem_ponderada(
        candidatos=candidatos,
        historico=historico,
        usos_atuais=usos_atuais,
        trabalharam_dia_anterior=trabalharam_dia_anterior,
        rng=rng,
    )

    for pessoa in ordem:
        novos_usos = usos_atuais.copy()
        novos_usos[pessoa.nome] += 1

        novas_funcoes = tuple(
            funcao
            for funcao in funcoes_restantes
            if funcao != funcao_escolhida
        )

        resultado = _buscar_atribuicoes_noturnas(
            pessoas=pessoas,
            dia=dia,
            funcoes_restantes=novas_funcoes,
            nomes_usados=nomes_usados | {pessoa.nome},
            historico=historico,
            usos_atuais=novos_usos,
            trabalharam_dia_anterior=trabalharam_dia_anterior,
            rng=rng,
        )

        if resultado is not None:
            resultado[funcao_escolhida] = pessoa.nome
            return resultado

    return None


def montar_escala(
    pessoas: Sequence[Pessoa],
    quantidade_dias: int,
    historico: Mapping[str, int] | None = None,
    *,
    rng: Random | None = None,
) -> list[EscalaDia]:
    """
    Monta a escala completa.

    Args:
        pessoas: pessoas disponíveis para serem escaladas.
        quantidade_dias: quantidade de dias de trabalho.
        historico: quantidade de participações anteriores por pessoa.
        rng: gerador aleatório opcional, útil para testes reproduzíveis.

    Returns:
        Lista contendo um objeto EscalaDia para cada dia.
    """

    if (
        isinstance(quantidade_dias, bool)
        or not isinstance(quantidade_dias, int)
        or quantidade_dias < 1
    ):
        raise ValueError("A quantidade de dias deve ser um inteiro positivo.")

    if not pessoas:
        raise ValueError("A lista de pessoas não pode estar vazia.")

    if not all(isinstance(pessoa, Pessoa) for pessoa in pessoas):
        raise TypeError("Todos os elementos devem ser objetos Pessoa.")

    nomes_normalizados = [
        pessoa.nome.casefold()
        for pessoa in pessoas
    ]

    if len(nomes_normalizados) != len(set(nomes_normalizados)):
        raise ValueError("Não pode haver pessoas com nomes duplicados.")

    historico = Counter(historico or {})

    if any(
        not isinstance(nome, str)
        or not isinstance(quantidade, int)
        or isinstance(quantidade, bool)
        or quantidade < 0
        for nome, quantidade in historico.items()
    ):
        raise ValueError("O histórico deve conter nomes e contagens válidas.")

    gerador = rng if rng is not None else Random()

    # Quantidade de vezes que cada pessoa já foi escolhida
    # na escala que estamos construindo.
    usos_atuais: Counter[str] = Counter()

    escala: list[EscalaDia] = []

    # Pessoas que trabalharam no dia imediatamente anterior.
    trabalharam_dia_anterior: set[str] = set()

    for dia in range(1, quantidade_dias + 1):

        # Pessoas elegíveis para o turno da manhã.
        candidatos_manha = [
            pessoa
            for pessoa in pessoas
            if (
                pessoa.disponivel_manha
                and dia not in pessoa.indisponibilidade
            )
        ]

        if not candidatos_manha:
            raise EscalaImpossivelError(
                f"Dia {dia}: não existe pessoa disponível para a manhã."
            )

        ordem_manha = _ordem_ponderada(
            candidatos=candidatos_manha,
            historico=historico,
            usos_atuais=usos_atuais,
            trabalharam_dia_anterior=trabalharam_dia_anterior,
            rng=gerador,
        )

        resultado_noite = None
        pessoa_manha_escolhida = None

        # Tenta cada candidato da manhã até encontrar uma
        # combinação possível para as seis funções noturnas.
        for pessoa_manha in ordem_manha:

            usos_com_manha = usos_atuais.copy()
            usos_com_manha[pessoa_manha.nome] += 1

            atribuicoes_noturnas = _buscar_atribuicoes_noturnas(
                pessoas=pessoas,
                dia=dia,
                funcoes_restantes=FUNCOES,
                nomes_usados={pessoa_manha.nome},
                historico=historico,
                usos_atuais=usos_com_manha,
                trabalharam_dia_anterior=trabalharam_dia_anterior,
                rng=gerador,
            )

            if atribuicoes_noturnas is not None:
                pessoa_manha_escolhida = pessoa_manha
                resultado_noite = atribuicoes_noturnas
                break

        if resultado_noite is None or pessoa_manha_escolhida is None:
            raise EscalaImpossivelError(
                f"Dia {dia}: não foi possível encontrar uma combinação "
                "válida para a manhã e as seis funções da noite. "
                "Verifique a disponibilidade e as funções das pessoas."
            )

        # Atualiza o histórico da escala atual.
        usos_atuais[pessoa_manha_escolhida.nome] += 1
        usos_atuais.update(resultado_noite.values())

        escala.append(
            EscalaDia(
                dia=dia,
                manha=pessoa_manha_escolhida.nome,
                noite=resultado_noite,
            )
        )

        # Atualiza as pessoas que trabalharam neste dia.
        # Elas terão peso reduzido no próximo dia.
        trabalharam_dia_anterior = {
            pessoa_manha_escolhida.nome,
            *resultado_noite.values()
        }

    return escala

