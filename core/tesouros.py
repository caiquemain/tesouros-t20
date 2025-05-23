# core/tesouros.py
import random  # Usado por rolar_em_tabela_d_porcento se não houver override
from tabelas.base.tabela_8_1_data import TABELA_8_1
from .utils import rolar_em_tabela_d_porcento, rolar_expressao_dados

# Imports para os módulos do core
from . import dinheiro as core_dinheiro
from . import itens_mundanos as core_itens_mundanos
from . import equipamentos_superior as core_equipamentos_superior
from . import pocoes as core_pocoes
from . import itens_magicos as core_itens_magicos

# --- Funções de Despacho para Processamento Detalhado ---


def _processar_resultado_dinheiro_t81(obj_resultado_t81, mod_metade_ativo=False, log_principal=None):
    if log_principal is None:
        log_principal = []
    tipo_principal = obj_resultado_t81.get("tipo")

    if tipo_principal == "moedas":
        return core_dinheiro.processar_moedas_t81(obj_resultado_t81, mod_metade_ativo, log_principal)
    elif tipo_principal == "riqueza":
        return core_dinheiro.processar_riquezas_t81(obj_resultado_t81, log_principal)
    elif tipo_principal == "nada":
        return None
    else:
        log_principal.append(
            f"ALERTA: Tipo de dinheiro/riqueza desconhecido ('{tipo_principal}') da T8-1: {obj_resultado_t81}")
        return {"tipo_gerado": "dinheiro_desconhecido_t81", "dados_brutos": obj_resultado_t81}


def _processar_item_da_t81(obj_resultado_t81, log_principal=None):
    if log_principal is None:
        log_principal = []
    tipo_principal = obj_resultado_t81.get("tipo")

    if tipo_principal == "nada":
        return None
    elif tipo_principal == "Diverso":
        return core_itens_mundanos.processar_item_diverso_t81(obj_resultado_t81, log_principal)
    elif tipo_principal == "Equipamento":
        return core_itens_mundanos.processar_equipamento_t81(obj_resultado_t81, log_principal)
    elif tipo_principal == "Superior":
        return core_equipamentos_superior.processar_item_superior_t81(obj_resultado_t81, log_principal)
    elif tipo_principal == "poção":
        return core_pocoes.processar_pocoes_t81(obj_resultado_t81_pocao=obj_resultado_t81, log_principal=log_principal)
    elif tipo_principal == "Mágico":
        return core_itens_magicos.processar_item_magico_t81(obj_resultado_t81_magico=obj_resultado_t81, log_principal=log_principal)
    else:
        log_principal.append(
            f"ALERTA: Tipo de item ('{tipo_principal}') desconhecido da T8-1: {obj_resultado_t81}")
        return {"tipo_gerado": "item_desconhecido_t81", "dados_brutos": obj_resultado_t81, "detalhes_rolagem_especifica": ["Tipo de item desconhecido da T8-1."]}

# --- Função Principal de Geração de Tesouro ---


def gerar_tesouro_completo_por_nd(nd_chave_str, tipo_tesouro_modificador="Padrão"):
    log_geral_rolagens = [
        f"Iniciando geração de tesouro para ND: {nd_chave_str}, Modificador: {tipo_tesouro_modificador}"]

    if tipo_tesouro_modificador == "Nenhum":
        log_geral_rolagens.append(
            "Nenhum tesouro gerado conforme modificador.")
        return {
            "sumario": "Nenhum tesouro para este encontro (modificador 'Nenhum').",
            "moedas_e_riquezas": [{"tipo_gerado": "info_rolagem_dinheiro", "mensagem": "Nenhum dinheiro encontrado (modificador 'Nenhum')."}],
            "itens_encontrados": [{"tipo_gerado": "info_rolagem_item", "mensagem": "Nenhum item encontrado (modificador 'Nenhum')."}],
            "log_completo_rolagens": log_geral_rolagens
        }

    if nd_chave_str not in TABELA_8_1:
        log_geral_rolagens.append(
            f"ERRO: ND '{nd_chave_str}' não é uma chave válida na Tabela 8-1.")
        return {"erro": f"ND '{nd_chave_str}' não é uma chave válida na Tabela 8-1.", "log_completo_rolagens": log_geral_rolagens}

    config_nd_tabela = TABELA_8_1[nd_chave_str]

    tesouro_gerado = {
        "nd_processado": nd_chave_str,
        "modificador_tesouro": tipo_tesouro_modificador,
        "moedas_e_riquezas": [],
        "itens_encontrados": [],
        "log_completo_rolagens": log_geral_rolagens
    }

    num_rolagens_dinheiro = 1
    num_rolagens_itens = 1
    aplicar_mod_metade_dinheiro = (tipo_tesouro_modificador == "Metade")

    if tipo_tesouro_modificador == "Dobro":
        num_rolagens_dinheiro = 2
        num_rolagens_itens = 2
        log_geral_rolagens.append(
            "Modificador 'Dobro' ativo: 2 rolagens para Dinheiro e 2 para Itens.")
    elif aplicar_mod_metade_dinheiro:
        log_geral_rolagens.append(
            "Modificador 'Metade' ativo: valor do dinheiro (moedas) será dividido por 2.")

    # Processar coluna "Dinheiro"
    log_geral_rolagens.append(
        f"Processando {num_rolagens_dinheiro}x coluna 'Dinheiro'...")
    for i in range(num_rolagens_dinheiro):
        resultado_d100_dinheiro = rolar_em_tabela_d_porcento(
            config_nd_tabela["dinheiro"], modificador_d100=0)
        if resultado_d100_dinheiro:
            entrada_tabela = resultado_d100_dinheiro["entrada_tabela"]
            obj_resultado_bruto = entrada_tabela["resultado"]
            log_rolagem_t81 = (
                f"  Rolagem Dinheiro #{i+1} (d100: {resultado_d100_dinheiro['d100_base']} -> Final: {resultado_d100_dinheiro['d100_final']}): "
                f"Resultado T8-1: {obj_resultado_bruto.get('tipo', 'desconhecido') if isinstance(obj_resultado_bruto, dict) else obj_resultado_bruto}"
            )
            log_geral_rolagens.append(log_rolagem_t81)

            if isinstance(obj_resultado_bruto, dict) and obj_resultado_bruto.get("tipo") == "nada":
                tesouro_gerado["moedas_e_riquezas"].append({
                    "tipo_gerado": "info_rolagem_dinheiro",
                    "mensagem": f"Rolagem de Dinheiro #{i+1}: Nenhum dinheiro encontrado.",
                    "detalhes_rolagem_especifica": [log_rolagem_t81]
                })
            elif isinstance(obj_resultado_bruto, dict):
                dinheiro_processado = _processar_resultado_dinheiro_t81(
                    obj_resultado_bruto,
                    aplicar_mod_metade_dinheiro,
                    log_geral_rolagens
                )
                if dinheiro_processado:
                    tesouro_gerado["moedas_e_riquezas"].append(
                        dinheiro_processado)
        else:
            log_geral_rolagens.append(
                f"  Rolagem Dinheiro #{i+1}: Falha ao obter resultado da Tabela 8-1 (Dinheiro).")

    # Processar coluna "Itens"
    log_geral_rolagens.append(
        f"Processando {num_rolagens_itens}x coluna 'Itens'...")
    for i in range(num_rolagens_itens):
        resultado_d100_itens = rolar_em_tabela_d_porcento(
            config_nd_tabela["itens"], modificador_d100=0)
        if resultado_d100_itens:
            entrada_tabela = resultado_d100_itens["entrada_tabela"]
            obj_resultado_bruto = entrada_tabela["resultado"]
            log_rolagem_t81_item = (
                f"  Rolagem Itens #{i+1} (d100: {resultado_d100_itens['d100_base']} -> Final: {resultado_d100_itens['d100_final']}): "
                f"Resultado T8-1: {obj_resultado_bruto.get('tipo', 'desconhecido') if isinstance(obj_resultado_bruto, dict) else obj_resultado_bruto}"
            )
            log_geral_rolagens.append(log_rolagem_t81_item)

            if isinstance(obj_resultado_bruto, dict) and obj_resultado_bruto.get("tipo") == "nada":
                tesouro_gerado["itens_encontrados"].append({
                    "tipo_gerado": "info_rolagem_item",
                    "mensagem": f"Rolagem de Item #{i+1}: Nenhum item encontrado.",
                    "detalhes_rolagem_especifica": [log_rolagem_t81_item]
                })
            elif isinstance(obj_resultado_bruto, dict):
                item_processado = _processar_item_da_t81(
                    obj_resultado_bruto,
                    log_geral_rolagens
                )
                if item_processado:
                    tesouro_gerado["itens_encontrados"].append(item_processado)
        else:
            log_geral_rolagens.append(
                f"  Rolagem Itens #{i+1}: Falha ao obter resultado da Tabela 8-1 (Itens).")

    return tesouro_gerado
