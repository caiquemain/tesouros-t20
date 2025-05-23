# core/pocoes.py
import random
from .utils import rolar_expressao_dados, rolar_em_tabela_d_porcento
from tabelas.base.pocoes_data import POCOES_DATA  # Dados da Tabela 8-12


def _rolar_pocao_individual_da_tabela(aplicar_mod_20_porcento, log_principal):
    """
    Rola uma única poção na Tabela 8-12 (POCOES_DATA).
    Aplica o modificador de +20% se necessário.
    Adiciona detalhes da rolagem ao log_principal.
    Retorna um dicionário com os detalhes da poção ou None.
    """
    modificador_d100_final = 0
    if aplicar_mod_20_porcento:
        modificador_d100_final = 20
        # A função rolar_em_tabela_d_porcento em utils.py já lida com o cap de 100.

    resultado_rolagem_t8_12 = rolar_em_tabela_d_porcento(
        POCOES_DATA,
        modificador_d100=modificador_d100_final
    )

    if resultado_rolagem_t8_12 and "entrada_tabela" in resultado_rolagem_t8_12:
        pocao_info_base = resultado_rolagem_t8_12["entrada_tabela"]

        log_msg = (f"Poção (Tabela 8-12, Mod+20% aplicado: {aplicar_mod_20_porcento}): "
                   f"d100 base {resultado_rolagem_t8_12['d100_base']} + mod {resultado_rolagem_t8_12['modificador']} = final {resultado_rolagem_t8_12['d100_final']} "
                   f"-> '{pocao_info_base.get('descricao_completa', 'Poção Desconhecida')}'")
        log_principal.append(f"    {log_msg}")  # Adiciona ao log principal

        return {
            "tipo_gerado": "pocao_individual",
            "nome": pocao_info_base.get("nome_base"),
            "descricao_completa": pocao_info_base.get("descricao_completa"),
            "preco_ts": pocao_info_base.get("preco_ts"),
            # Pode ser None
            "efeito_detalhe": pocao_info_base.get("efeito_detalhe"),
            "detalhes_rolagem_especifica": [log_msg]
        }
    else:
        log_principal.append(
            f"    Poção (Tabela 8-12): Falha ao rolar na tabela (Mod+20% aplicado: {aplicar_mod_20_porcento}). Verifique dados ou lógica.")
        return None


def processar_pocoes_t81(obj_resultado_t81_pocao, log_principal):
    """
    Processa um resultado "poção" da Tabela 8-1.
    obj_resultado_t81_pocao: Ex: {"tipo": "poção", "quantidade_str": "1d3", "mod_20_porcento_tabela_pocao": True}
    log_principal: Lista para adicionar logs de rolagem.
    Retorna: Um dicionário contendo uma lista de poções processadas.
    """
    if obj_resultado_t81_pocao.get("tipo") != "poção":
        log_principal.append(
            f"ALERTA em pocoes: Tentativa de processar '{obj_resultado_t81_pocao.get('tipo')}' como 'poção'.")
        return None

    quantidade_str = obj_resultado_t81_pocao.get(
        "quantidade_str", "1")  # Default para "1" se não especificado
    aplicar_mod_20 = obj_resultado_t81_pocao.get(
        "mod_20_porcento_tabela_pocao", False)

    # Rolar quantidade de poções
    info_rolagem_qtd = rolar_expressao_dados(quantidade_str)
    num_pocoes_a_gerar = info_rolagem_qtd["valor"]

    log_principal.append(
        f"Poções (Modificador T8-12 +20%: {aplicar_mod_20}): "
        f"Rolando quantidade '{quantidade_str}' -> {info_rolagem_qtd['detalhes_rolagem']} = {num_pocoes_a_gerar} poção(ões)."
    )

    if num_pocoes_a_gerar == 0:
        return {"tipo_gerado": "pocoes_conjunto", "itens": [], "detalhes_rolagem_conjunto": [info_rolagem_qtd['detalhes_rolagem']]}

    lista_de_pocoes_geradas = []
    detalhes_log_conjunto = [info_rolagem_qtd['detalhes_rolagem']]

    log_principal.append(
        f"  Gerando {num_pocoes_a_gerar} poção(ões) individualmente...")
    for i in range(num_pocoes_a_gerar):
        # Cabeçalho para os logs da poção individual
        log_principal.append(f"    Processando Poção Individual #{i+1}...")
        pocao_individual = _rolar_pocao_individual_da_tabela(
            aplicar_mod_20, log_principal)
        if pocao_individual:
            lista_de_pocoes_geradas.append(pocao_individual)
            if "detalhes_rolagem_especifica" in pocao_individual:
                detalhes_log_conjunto.extend(
                    pocao_individual["detalhes_rolagem_especifica"])

    return {
        "tipo_gerado": "pocoes_conjunto",
        "itens": lista_de_pocoes_geradas,  # Lista de dicionários, cada um sendo uma poção
        "detalhes_rolagem_conjunto": detalhes_log_conjunto
    }
