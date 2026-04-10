"""Lógica de negócio pura para cálculo de racionamento de suprimentos."""

import math

from racionador.modelos import Grupo, Suprimento


def calcular_dias_restantes(suprimento: Suprimento, grupo: Grupo) -> float:
    """Retorna quantos dias inteiros o suprimento vai durar para o grupo.

    Considera os fatores de consumo individuais de cada pessoa.
    Retorna float('inf') se o consumo total for zero.
    """
    if not grupo.pessoas:
        raise ValueError("O grupo não possui pessoas cadastradas.")

    fator_total = sum(p.fator_consumo for p in grupo.pessoas)
    consumo_total_diario = suprimento.consumo_diario_padrao * fator_total

    if consumo_total_diario == 0:
        return float("inf")

    return math.floor(suprimento.quantidade_atual / consumo_total_diario)


def suprimento_em_alerta(
    suprimento: Suprimento, grupo: Grupo, dias_minimos: int = 3
) -> bool:
    """Retorna True se o suprimento durar menos que `dias_minimos` dias."""
    return calcular_dias_restantes(suprimento, grupo) < dias_minimos


def sugerir_corte(suprimento: Suprimento, grupo: Grupo, dias_alvo: int) -> float:
    """Calcula o percentual de redução no consumo diário para o suprimento durar `dias_alvo` dias.

    Retorna 0.0 se o suprimento já dura o suficiente.
    Retorna um valor entre 0.0 e 100.0 representando a porcentagem de corte necessária.
    """
    if dias_alvo <= 0:
        raise ValueError("dias_alvo deve ser maior que zero.")
    if not grupo.pessoas:
        raise ValueError("O grupo não possui pessoas cadastradas.")

    fator_total = sum(p.fator_consumo for p in grupo.pessoas)
    consumo_atual = suprimento.consumo_diario_padrao * fator_total

    if consumo_atual == 0:
        return 0.0

    dias_atuais = suprimento.quantidade_atual / consumo_atual
    if dias_atuais >= dias_alvo:
        return 0.0

    consumo_necessario = suprimento.quantidade_atual / dias_alvo
    corte = (consumo_atual - consumo_necessario) / consumo_atual * 100
    return min(100.0, max(0.0, corte))


def relatorio_completo(grupo: Grupo) -> dict:
    """Retorna um dicionário com o resumo de cada suprimento do grupo.

    Cada entrada contém: dias_restantes, status (OK/ALERTA/CRITICO),
    quantidade_atual, unidade_medida e corte_sugerido_pct.
    """
    if not grupo.pessoas:
        raise ValueError("O grupo não possui pessoas cadastradas.")
    if not grupo.suprimentos:
        raise ValueError("O grupo não possui suprimentos cadastrados.")

    relatorio: dict = {}
    for suprimento in grupo.suprimentos:
        dias = calcular_dias_restantes(suprimento, grupo)

        if dias == float("inf"):
            status = "OK"
        elif dias < 2:
            status = "CRITICO"
        elif dias < 5:
            status = "ALERTA"
        else:
            status = "OK"

        corte = sugerir_corte(suprimento, grupo, dias_alvo=5) if status != "OK" else 0.0

        relatorio[suprimento.nome] = {
            "dias_restantes": dias,
            "status": status,
            "quantidade_atual": suprimento.quantidade_atual,
            "unidade_medida": suprimento.unidade_medida,
            "corte_sugerido_pct": round(corte, 1),
        }

    return relatorio
