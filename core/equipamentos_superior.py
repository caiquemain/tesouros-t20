# core/equipamentos_superior.py
import random
from .utils import rolar_em_tabela_d_porcento
from tabelas.base.tabela_8_4_data import EQUIPAMENTO_DATA  # Para obter o item base
from tabelas.base.tabela_8_5_data import ITENS_SUPERIORES_DATA, MATERIAIS_ESPECIAIS


def _determinar_categoria_e_item_base(mod_2D_ativo, log_principal):
    """
    Determina a categoria do item base (arma, armadura/escudo, esotérico)
    e rola um item base da Tabela 8-4 para essa categoria.
    Retorna: (categoria_str, nome_item_base, log_detalhado_str) ou (None, None, log_detalhado_str) em caso de erro.
    categoria_str é "armas", "armaduras_escudos", ou "esotericos".
    """
    d6_rolagens = [random.randint(1, 6)]
    log_rolagem_tipo_parcial = f"d6 para tipo de item base superior: Rolagem 1 = {d6_rolagens[0]}"

    if mod_2D_ativo:
        d6_rolagens.append(random.randint(1, 6))
        log_rolagem_tipo_parcial += f"; Rolagem 2 = {d6_rolagens[1]}"
        # Exemplo de escolha automática: maior valor
        escolha_d6 = max(d6_rolagens)
        log_rolagem_tipo_parcial += f". Modificador 2D ativo, escolhido (max): {escolha_d6}"
    else:
        escolha_d6 = d6_rolagens[0]
        log_rolagem_tipo_parcial += f". Escolhido: {escolha_d6}"

    categoria_t84_key = None
    categoria_t85_key = None  # Chave para Tabela 8-5 pode ser a mesma da Tabela 8-4
    desc_categoria_log = ""

    if 1 <= escolha_d6 <= 3:
        categoria_t84_key = "armas"
        categoria_t85_key = "armas"
        desc_categoria_log = "Arma"
    elif 4 <= escolha_d6 <= 5:
        categoria_t84_key = "armaduras_escudos"
        categoria_t85_key = "armaduras_escudos"
        desc_categoria_log = "Armadura/Escudo"
    elif escolha_d6 == 6:
        categoria_t84_key = "esotericos"
        categoria_t85_key = "esotericos"
        desc_categoria_log = "Esotérico"

    log_rolagem_tipo_completa = f"{log_rolagem_tipo_parcial} -> Categoria Base: {desc_categoria_log}"
    log_principal.append(f"  Item Superior - {log_rolagem_tipo_completa}")

    if not categoria_t84_key:
        log_principal.append(
            "    Item Superior: Erro ao determinar categoria base.")
        return None, None, log_rolagem_tipo_completa  # Retorna o log acumulado até aqui

    # Obter item base da Tabela 8-4
    tabela_base_especifica = EQUIPAMENTO_DATA.get(categoria_t84_key)
    if not tabela_base_especifica:
        log_principal.append(
            f"    Item Superior: Sub-tabela '{categoria_t84_key}' não encontrada na Tabela 8-4.")
        return None, None, log_rolagem_tipo_completa

    resultado_rolagem_t8_4 = rolar_em_tabela_d_porcento(tabela_base_especifica)
    if resultado_rolagem_t8_4 and "entrada_tabela" in resultado_rolagem_t8_4:
        item_base_info = resultado_rolagem_t8_4["entrada_tabela"]
        nome_item_base = item_base_info.get("item", "Item Base Desconhecido")
        # Quantidade do item base geralmente não é relevante para itens superiores, mas guardamos para log
        # qtd_base = item_base_info.get("quantidade")

        log_t8_4 = (f"Tabela 8-4 ({desc_categoria_log} Base): d100 base {resultado_rolagem_t8_4['d100_base']} "
                    f"(mod {resultado_rolagem_t8_4['modificador']}) -> final {resultado_rolagem_t8_4['d100_final']} -> {nome_item_base}")
        log_principal.append(f"    {log_t8_4}")
        return categoria_t85_key, nome_item_base, log_rolagem_tipo_completa + "; " + log_t8_4
    else:
        log_principal.append(
            f"    Item Superior (Tabela 8-4 {desc_categoria_log}): Falha ao rolar item base.")
        # Retorna categoria para possível log de erro
        return categoria_t85_key, None, log_rolagem_tipo_completa


def _aplicar_melhorias_da_t85(categoria_item_t85_key, num_melhorias_objetivo, log_principal):
    """
    Aplica melhorias da Tabela 8-5 a um item.
    Retorna uma lista de strings descrevendo as melhorias aplicadas e seus logs específicos.
    """
    melhorias_aplicadas_desc = []
    logs_especificos_melhorias = []
    slots_de_melhoria_usados = 0

    tabela_melhorias_superior = ITENS_SUPERIORES_DATA.get(
        categoria_item_t85_key)
    if not tabela_melhorias_superior:
        log_principal.append(
            f"    ALERTA: Categoria '{categoria_item_t85_key}' não encontrada na Tabela 8-5 de Itens Superiores.")
        return [], []

    tentativas_gerais = 0  # Para evitar loop infinito
    max_tentativas_gerais = num_melhorias_objetivo * \
        5  # Ex: 5 tentativas por slot de melhoria

    while slots_de_melhoria_usados < num_melhorias_objetivo and tentativas_gerais < max_tentativas_gerais:
        tentativas_gerais += 1
        resultado_rolagem_t8_5 = rolar_em_tabela_d_porcento(
            tabela_melhorias_superior)

        if not resultado_rolagem_t8_5 or "entrada_tabela" not in resultado_rolagem_t8_5:
            log_principal.append(
                f"      Melhoria #{slots_de_melhoria_usados+1}: Falha ao rolar na Tabela 8-5 (tentativa {tentativas_gerais}).")
            continue

        melhoria_info = resultado_rolagem_t8_5["entrada_tabela"]
        nome_melhoria_base = melhoria_info.get(
            "melhoria", "Melhoria Desconhecida")
        custo_esta_melhoria = melhoria_info.get("custo_melhorias", 1)
        reroll_se_unica = melhoria_info.get("reroll_se_unica", False)
        requer_material = melhoria_info.get("requer_rolagem_material", False)

        log_rolagem_melhoria_atual = (f"Tabela 8-5 ({categoria_item_t85_key}): d100 base {resultado_rolagem_t8_5['d100_base']} "
                                      f"(mod {resultado_rolagem_t8_5['modificador']}) -> final {resultado_rolagem_t8_5['d100_final']} -> '{nome_melhoria_base}' (Custo: {custo_esta_melhoria})")

        # Regra 1: "Conta como duas melhorias. Se o item só possuir uma, role novamente."
        if reroll_se_unica and num_melhorias_objetivo == 1 and custo_esta_melhoria == 2:
            log_principal.append(
                f"      Melhoria #{slots_de_melhoria_usados+1}: '{nome_melhoria_base}' custa 2, mas item só tem 1 slot total. Rolando novamente. [{log_rolagem_melhoria_atual}]")
            logs_especificos_melhorias.append(
                log_rolagem_melhoria_atual + " - Rerolado (custo 2 para item com 1 slot).")
            continue

        # Verifica se a melhoria cabe nos slots restantes
        if (slots_de_melhoria_usados + custo_esta_melhoria) > num_melhorias_objetivo:
            log_principal.append(
                f"      Melhoria #{slots_de_melhoria_usados+1}: '{nome_melhoria_base}' custa {custo_esta_melhoria}, mas só restam {num_melhorias_objetivo - slots_de_melhoria_usados} slots. Rolando novamente. [{log_rolagem_melhoria_atual}]")
            logs_especificos_melhorias.append(
                log_rolagem_melhoria_atual + f" - Rerolado (não cabe nos {num_melhorias_objetivo - slots_de_melhoria_usados} slots restantes).")
            continue

        # Se chegou aqui, a melhoria é válida e cabe
        nome_final_melhoria_str = nome_melhoria_base
        log_material = ""
        if requer_material:
            d6_material = random.randint(1, 6)
            material_escolhido = MATERIAIS_ESPECIAIS.get(
                d6_material, "Material Desconhecido")
            nome_final_melhoria_str = f"{nome_melhoria_base} ({material_escolhido})"
            log_material = f" Material Especial (d6={d6_material}): {material_escolhido}."

        log_principal.append(
            f"      Melhoria #{slots_de_melhoria_usados+1} aplicada: {nome_final_melhoria_str}.{log_material} [{log_rolagem_melhoria_atual}]")
        melhorias_aplicadas_desc.append(nome_final_melhoria_str)
        logs_especificos_melhorias.append(
            log_rolagem_melhoria_atual + log_material)
        slots_de_melhoria_usados += custo_esta_melhoria

    if slots_de_melhoria_usados < num_melhorias_objetivo:
        log_principal.append(
            f"    ALERTA: Não foi possível aplicar todas as {num_melhorias_objetivo} melhorias. Aplicadas: {slots_de_melhoria_usados} (slots).")
        logs_especificos_melhorias.append(
            f"ALERTA: Slots não preenchidos: {num_melhorias_objetivo - slots_de_melhoria_usados}")

    return melhorias_aplicadas_desc, logs_especificos_melhorias


def processar_item_superior_t81(obj_resultado_t81, log_principal):
    """
    Processa um resultado "Superior" da Tabela 8-1.
    Envolve determinar tipo de item base, obter item base da Tabela 8-4,
    e aplicar N melhorias da Tabela 8-5.
    """
    if obj_resultado_t81.get("tipo") != "Superior":
        log_principal.append(
            f"ALERTA em eq_superior: Tentativa de processar '{obj_resultado_t81.get('tipo')}' como 'Superior'.")
        return None

    num_melhorias_a_aplicar = obj_resultado_t81.get("melhorias", 0)
    mod_2D_tipo_base = obj_resultado_t81.get("mod_2D_tipo", False)

    log_principal.append(
        f"Processando Item Superior com {num_melhorias_a_aplicar} melhoria(s). Modificador 2D para tipo base: {mod_2D_tipo_base}.")

    if num_melhorias_a_aplicar == 0:
        log_principal.append(
            "  Item Superior: Nenhuma melhoria a aplicar (0). Retornando nada.")
        # Ou deveria retornar um item base comum? A tabela 8-1 diz "Superior (X melhorias)", X >= 1.
        # Vamos assumir que X é sempre >= 1 se o tipo for "Superior".
        return {"tipo_gerado": "item_superior_erro", "descricao": "0 melhorias indicadas", "detalhes_rolagem_especifica": ["Erro: 0 melhorias"]}

    # 1. Determinar categoria e obter item base
    categoria_chave_t85, nome_item_base, log_item_base = _determinar_categoria_e_item_base(
        mod_2D_tipo_base, log_principal)

    if not nome_item_base or not categoria_chave_t85:
        log_principal.append(
            "  Item Superior: Não foi possível determinar o item base. Interrompendo.")
        return {"tipo_gerado": "item_superior_erro", "descricao": "Falha ao obter item base", "detalhes_rolagem_especifica": [log_item_base]}

    # 2. Aplicar Melhorias
    log_principal.append(
        f"  Aplicando {num_melhorias_a_aplicar} melhoria(s) ao item base '{nome_item_base}' (categoria: {categoria_chave_t85})...")
    lista_melhorias_str, logs_das_melhorias = _aplicar_melhorias_da_t85(
        categoria_chave_t85, num_melhorias_a_aplicar, log_principal)

    return {
        "tipo_gerado": "item_superior",
        "nome_base": nome_item_base,
        # Ex: "Armas", "Armaduras Escudos"
        "categoria_base": categoria_chave_t85.replace("_", " ").title(),
        "melhorias_aplicadas": lista_melhorias_str,
        # Simplificado; o custo real foi tratado internamente
        "numero_slots_melhoria_usados": sum(1 for _ in lista_melhorias_str),
        "detalhes_rolagem_especifica": ([log_item_base] if log_item_base else []) + logs_das_melhorias
    }
