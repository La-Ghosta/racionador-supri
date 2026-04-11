"""Testes da logica de negocio de racionamento."""

import pytest

from racionador.modelos import Grupo, Pessoa, Suprimento
from racionador.racionamento import (
    calcular_dias_restantes,
    relatorio_completo,
    sugerir_corte,
    suprimento_em_alerta,
)


def test_calcular_dias_dois_adultos_agua():
    # floor(10 / (2.0 * (1.0 + 1.0))) = floor(2.5) = 2
    agua = Suprimento(
        nome="Agua", quantidade_atual=10.0, consumo_diario_padrao=2.0, unidade_medida="L"
    )
    grupo = Grupo(
        nome_grupo="Grupo",
        pessoas=[Pessoa(nome="Ana", idade=30), Pessoa(nome="Bruno", idade=25)],
    )
    assert calcular_dias_restantes(agua, grupo) == 2


def test_calcular_dias_adulto_e_crianca_arroz():
    # floor(10 / (0.4 * (1.0 + 0.6))) = floor(15.625) = 15
    arroz = Suprimento(
        nome="Arroz", quantidade_atual=10.0, consumo_diario_padrao=0.4, unidade_medida="kg"
    )
    grupo = Grupo(
        nome_grupo="Grupo",
        pessoas=[Pessoa(nome="Ana", idade=30), Pessoa(nome="Crianca", idade=8)],
    )
    assert calcular_dias_restantes(arroz, grupo) == 15


def test_calcular_dias_consumo_zero_retorna_infinito():
    suprimento = Suprimento(
        nome="Reserva", quantidade_atual=10.0, consumo_diario_padrao=0.0, unidade_medida="un"
    )
    grupo = Grupo(nome_grupo="Grupo", pessoas=[Pessoa(nome="Ana", idade=30)])
    assert calcular_dias_restantes(suprimento, grupo) == float("inf")


def test_calcular_dias_grupo_vazio_lanca_value_error():
    suprimento = Suprimento(
        nome="Agua", quantidade_atual=10.0, consumo_diario_padrao=2.0, unidade_medida="L"
    )
    grupo = Grupo(nome_grupo="Grupo vazio")
    with pytest.raises(ValueError):
        calcular_dias_restantes(suprimento, grupo)


def test_suprimento_em_alerta_retorna_true_quando_critico():
    # floor(1.0 / 1.0) = 1 < 3 (dias_minimos padrao) → True
    suprimento = Suprimento(
        nome="Agua", quantidade_atual=1.0, consumo_diario_padrao=1.0, unidade_medida="L"
    )
    grupo = Grupo(nome_grupo="Grupo", pessoas=[Pessoa(nome="Ana", idade=30)])
    assert suprimento_em_alerta(suprimento, grupo) is True


def test_suprimento_em_alerta_retorna_false_quando_suficiente():
    # floor(10.0 / 1.0) = 10 >= 3 → False
    suprimento = Suprimento(
        nome="Agua", quantidade_atual=10.0, consumo_diario_padrao=1.0, unidade_medida="L"
    )
    grupo = Grupo(nome_grupo="Grupo", pessoas=[Pessoa(nome="Ana", idade=30)])
    assert suprimento_em_alerta(suprimento, grupo) is False


def test_sugerir_corte_retorna_zero_quando_ja_suficiente():
    # 100kg / (1kg/dia * 1.0) = 100 dias >= 5 → 0.0
    suprimento = Suprimento(
        nome="Arroz", quantidade_atual=100.0, consumo_diario_padrao=1.0, unidade_medida="kg"
    )
    grupo = Grupo(nome_grupo="Grupo", pessoas=[Pessoa(nome="Ana", idade=30)])
    assert sugerir_corte(suprimento, grupo, dias_alvo=5) == 0.0


def test_sugerir_corte_calcula_percentual_correto():
    # consumo_atual = 0.4 * 1.0 = 0.4; dias_atuais = 2/0.4 = 5.0 < 10
    # consumo_necessario = 2/10 = 0.2; corte = (0.4-0.2)/0.4*100 = 50.0
    suprimento = Suprimento(
        nome="Arroz", quantidade_atual=2.0, consumo_diario_padrao=0.4, unidade_medida="kg"
    )
    grupo = Grupo(nome_grupo="Grupo", pessoas=[Pessoa(nome="Ana", idade=30)])
    assert sugerir_corte(suprimento, grupo, dias_alvo=10) == pytest.approx(50.0)


def test_sugerir_corte_dias_alvo_zero_lanca_value_error():
    suprimento = Suprimento(
        nome="Agua", quantidade_atual=10.0, consumo_diario_padrao=2.0, unidade_medida="L"
    )
    grupo = Grupo(nome_grupo="Grupo", pessoas=[Pessoa(nome="Ana", idade=30)])
    with pytest.raises(ValueError):
        sugerir_corte(suprimento, grupo, dias_alvo=0)


def test_relatorio_completo_classifica_status_corretamente():
    # 1 adulto (fator 1.0); consumo_diario=1kg/un por suprimento
    # CRITICO: 0.5un → floor(0.5/1.0) = 0 < 2
    # ALERTA:  3.0un → floor(3.0/1.0) = 3, 2 <= 3 < 5
    # OK:     10.0un → floor(10.0/1.0) = 10 >= 5
    grupo = Grupo(
        nome_grupo="Grupo",
        pessoas=[Pessoa(nome="Ana", idade=30)],
        suprimentos=[
            Suprimento(
                nome="Critico", quantidade_atual=0.5, consumo_diario_padrao=1.0, unidade_medida="un"
            ),
            Suprimento(
                nome="Alerta", quantidade_atual=3.0, consumo_diario_padrao=1.0, unidade_medida="un"
            ),
            Suprimento(
                nome="Ok", quantidade_atual=10.0, consumo_diario_padrao=1.0, unidade_medida="un"
            ),
        ],
    )

    relatorio = relatorio_completo(grupo)

    chaves_esperadas = {
        "dias_restantes",
        "status",
        "quantidade_atual",
        "unidade_medida",
        "corte_sugerido_pct",
    }
    for nome_sup in ("Critico", "Alerta", "Ok"):
        assert nome_sup in relatorio
        assert set(relatorio[nome_sup].keys()) == chaves_esperadas

    assert relatorio["Critico"]["status"] == "CRITICO"
    assert relatorio["Alerta"]["status"] == "ALERTA"
    assert relatorio["Ok"]["status"] == "OK"


def test_relatorio_completo_grupo_sem_suprimentos_lanca_value_error():
    """Garante que gerar relatorio de grupo sem suprimentos lanca erro."""
    grupo = Grupo(
        nome_grupo="Grupo Teste",
        pessoas=[Pessoa(nome="Ana", idade=30)],
        suprimentos=[],
    )
    with pytest.raises(ValueError):
        relatorio_completo(grupo)
