# core/itens_mundanos.py
import random
from .utils import rolar_em_tabela_d_porcento  # Função de utils.py
from tabelas.base.tabela_8_3_data import ITENS_DIVERSOS_DATA
from tabelas.base.tabela_8_4_data import EQUIPAMENTO_DATA


def processar_item_diverso_t81(obj_resultado_t81, log_principal):
    """
    Processa um resultado "Diverso" da Tabela 8-1, rolando na Tabela 8-3.

    Args:
        obj_resultado_t81 (dict): O objeto resultado da Tabela 8-1 (ex: {"tipo": "Diverso"}).
        log_principal (list): Lista para adicionar logs de rolagem.

    Returns:
        dict: Dicionário com os detalhes do item diverso ou None.
    """
    if obj_resultado_t81.get("tipo") != "Diverso":
        # Log de segurança, mas tesouros.py já deve ter filtrado.
        log_principal.append(
            f"ALERTA em itens_mundanos: Tentativa de processar '{obj_resultado_t81.get('tipo')}' como 'Diverso'.")
        return None

    # A Tabela 8-3 não tem modificadores de d100 como +20%
    resultado_rolagem_t8_3 = rolar_em_tabela_d_porcento(ITENS_DIVERSOS_DATA)

    if resultado_rolagem_t8_3 and "entrada_tabela" in resultado_rolagem_t8_3:
        item_encontrado_info = resultado_rolagem_t8_3["entrada_tabela"]
        nome_item = item_encontrado_info.get(
            "item", "Item Diverso Desconhecido")  # .get com default

        log_msg = (f"Item Diverso (Tabela 8-3): d100 base {resultado_rolagem_t8_3['d100_base']} "
                   f"(mod {resultado_rolagem_t8_3['modificador']}) -> final {resultado_rolagem_t8_3['d100_final']} -> {nome_item}")
        log_principal.append(f"  {log_msg}")  # Adiciona ao log principal

        return {
            "tipo_gerado": "item_diverso",
            "nome": nome_item,
            # Log específico deste item
            "detalhes_rolagem_especifica": [log_msg]
        }
    else:
        log_principal.append(
            "  Item Diverso (Tabela 8-3): Falha ao rolar na tabela (verifique dados ou lógica).")
        return None


def processar_equipamento_t81(obj_resultado_t81, log_principal):
    """
    Processa um resultado "Equipamento" da Tabela 8-1.
    Envolve rolar 1d6 (ou 2d6 com escolha se mod_2D_tipo) para tipo,
    e depois rolar d100 na sub-tabela apropriada da Tabela 8-4.

    Args:
        obj_resultado_t81 (dict): O objeto resultado da Tabela 8-1 (ex: {"tipo": "Equipamento", "mod_2D_tipo": True}).
        log_principal (list): Lista para adicionar logs de rolagem.

    Returns:
        dict: Dicionário com os detalhes do equipamento ou None.
    """
    if obj_resultado_t81.get("tipo") != "Equipamento":
        log_principal.append(
            f"ALERTA em itens_mundanos: Tentativa de processar '{obj_resultado_t81.get('tipo')}' como 'Equipamento'.")
        return None

    mod_2D_ativo = obj_resultado_t81.get("mod_2D_tipo", False)

    # Passo 1: Determinar tipo de equipamento (1d6 ou 2d6 com escolha)
    d6_rolagens = [random.randint(1, 6)]
    log_rolagem_tipo_parcial = f"d6 para tipo de equipamento: Rolagem 1 = {d6_rolagens[0]}"

    if mod_2D_ativo:
        d6_rolagens.append(random.randint(1, 6))
        log_rolagem_tipo_parcial += f"; Rolagem 2 = {d6_rolagens[1]}"
        # Escolha automática para o gerador: usar o maior valor rolado.
        # Em um jogo real, o jogador escolheria.
        escolha_d6 = max(d6_rolagens)
        log_rolagem_tipo_parcial += f". Modificador 2D ativo, escolhido (max): {escolha_d6}"
    else:
        escolha_d6 = d6_rolagens[0]
        log_rolagem_tipo_parcial += f". Escolhido: {escolha_d6}"

    sub_tabela_key = None
    sub_tabela_desc_log = ""  # Descrição para o log
    if 1 <= escolha_d6 <= 3:
        sub_tabela_key = "armas"
        sub_tabela_desc_log = "Arma"
    elif 4 <= escolha_d6 <= 5:
        sub_tabela_key = "armaduras_escudos"
        sub_tabela_desc_log = "Armadura/Escudo"
    elif escolha_d6 == 6:
        sub_tabela_key = "esotericos"
        sub_tabela_desc_log = "Esotérico"

    log_rolagem_tipo_completa = f"{log_rolagem_tipo_parcial} -> Categoria: {sub_tabela_desc_log}"
    log_principal.append(f"  Equipamento: {log_rolagem_tipo_completa}")

    if not sub_tabela_key:
        log_principal.append(
            "    Equipamento: Erro ao determinar sub-categoria do equipamento pela rolagem d6.")
        return None

    # Passo 2: Rolar na sub-tabela apropriada da Tabela 8-4
    tabela_especifica_equip = EQUIPAMENTO_DATA.get(sub_tabela_key)
    if not tabela_especifica_equip:
        log_principal.append(
            f"    Equipamento: Sub-tabela '{sub_tabela_key}' não encontrada nos dados da Tabela 8-4.")
        return None

    resultado_rolagem_t8_4 = rolar_em_tabela_d_porcento(
        tabela_especifica_equip)

    if resultado_rolagem_t8_4 and "entrada_tabela" in resultado_rolagem_t8_4:
        item_encontrado_info = resultado_rolagem_t8_4["entrada_tabela"]
        nome_item = item_encontrado_info.get(
            "item", "Equipamento Desconhecido")
        quantidade = item_encontrado_info.get(
            "quantidade")  # Será None se não houver

        log_msg_item_t8_4 = (f"Tabela 8-4 ({sub_tabela_desc_log}): d100 base {resultado_rolagem_t8_4['d100_base']} "
                             f"(mod {resultado_rolagem_t8_4['modificador']}) -> final {resultado_rolagem_t8_4['d100_final']} -> {nome_item}")
        if quantidade:
            log_msg_item_t8_4 += f" (Quantidade: {quantidade})"
        log_principal.append(f"    {log_msg_item_t8_4}")

        return {
            "tipo_gerado": "equipamento",
            "nome": nome_item,
            "quantidade": quantidade,
            # Ex: "Arma", "Armadura/Escudo", "Esotérico"
            "subcategoria_equipamento": sub_tabela_desc_log,
            "detalhes_rolagem_especifica": [log_rolagem_tipo_completa, log_msg_item_t8_4]
        }
    else:
        log_principal.append(
            f"    Equipamento (Tabela 8-4 {sub_tabela_desc_log}): Falha ao rolar na tabela.")
        return None
