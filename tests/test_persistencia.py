"""Testes de persistencia: salvar e carregar Grupo em JSON."""

from racionador.modelos import Grupo, Pessoa, Suprimento
from racionador.persistencia import carregar_grupo, salvar_grupo


def test_salvar_e_carregar_grupo_simples(tmp_path):
    caminho = tmp_path / "grupo.json"
    grupo = Grupo(nome_grupo="Familia Teste")

    salvar_grupo(grupo, caminho)
    carregado = carregar_grupo(caminho)

    assert carregado is not None
    assert carregado.nome_grupo == "Familia Teste"
    assert carregado.pessoas == []
    assert carregado.suprimentos == []


def test_carregar_arquivo_inexistente_retorna_none(tmp_path):
    caminho = tmp_path / "nao_existe.json"
    resultado = carregar_grupo(caminho)
    assert resultado is None


def test_serializa_pessoas_e_suprimentos_corretamente(tmp_path):
    caminho = tmp_path / "grupo_completo.json"
    pessoa = Pessoa(nome="Carlos", idade=40)
    suprimento = Suprimento(
        nome="Agua", quantidade_atual=20.0, consumo_diario_padrao=2.0, unidade_medida="L"
    )
    grupo = Grupo(nome_grupo="Equipe", pessoas=[pessoa], suprimentos=[suprimento])

    salvar_grupo(grupo, caminho)
    carregado = carregar_grupo(caminho)

    assert carregado is not None
    assert len(carregado.pessoas) == 1
    assert carregado.pessoas[0].nome == "Carlos"
    assert carregado.pessoas[0].idade == 40
    assert carregado.pessoas[0].fator_consumo == 1.0

    assert len(carregado.suprimentos) == 1
    assert carregado.suprimentos[0].nome == "Agua"
    assert carregado.suprimentos[0].quantidade_atual == 20.0
    assert carregado.suprimentos[0].consumo_diario_padrao == 2.0
    assert carregado.suprimentos[0].unidade_medida == "L"
