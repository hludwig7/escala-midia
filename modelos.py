
from dataclasses import dataclass, field


FUNCOES = (
    "projecao",
    "live",
    "mesaDeSom",
    "mesaDeSomLive",
    "fotografia",
    "auxiliar",
)

FUNCOES_VALIDAS = frozenset(FUNCOES)


@dataclass(slots=True)
class Pessoa:
    nome: str
    funcoes: set[str] = field(default_factory=set)
    disponivel_manha: bool = False
    indisponibilidade: set[int] = field(default_factory=set)

    def __post_init__(self) -> None:
        if not isinstance(self.nome, str) or not self.nome.strip():
            raise ValueError("O nome da pessoa não pode ser vazio.")

        self.nome = self.nome.strip()

        if not isinstance(self.disponivel_manha, bool):
            raise TypeError("disponivel_manha deve ser um booleano.")

        if isinstance(self.funcoes, str):
            raise TypeError("funcoes deve ser um conjunto de funções.")

        try:
            self.funcoes = set(self.funcoes)
        except TypeError as erro:
            raise TypeError("funcoes deve ser um conjunto válido.") from erro

        funcoes_invalidas = self.funcoes - FUNCOES_VALIDAS

        if funcoes_invalidas:
            raise ValueError(
                f"Funções inválidas para {self.nome}: {funcoes_invalidas}"
            )

        try:
            self.indisponibilidade = set(self.indisponibilidade)
        except TypeError as erro:
            raise TypeError(
                "indisponibilidade deve ser um conjunto de dias."
            ) from erro

        if any(
            type(dia) is not int or dia < 1
            for dia in self.indisponibilidade
        ):
            raise ValueError(
                "Os dias de indisponibilidade devem ser inteiros positivos."
            )


@dataclass(slots=True)
class EscalaDia:
    dia: int
    manha: str
    noite: dict[str, str]

