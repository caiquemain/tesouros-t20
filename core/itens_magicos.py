# core/itens_magicos.py
import random
# rolar_expressao_dados pode ser útil para preços, etc.
from .utils import rolar_em_tabela_d_porcento, rolar_expressao_dados
# Para itens base (armas, armaduras/escudos)
from tabelas.base.tabela_8_4_data import EQUIPAMENTO_DATA
from tabelas.base.tabela_8_8_data import ARMAS_MAGICAS_ENCANTOS_DATA
from tabelas.base.tabela_8_9_data import ARMAS_ESPECIFICAS_DATA
from tabelas.base.tabela_8_10_data import ARMADURAS_ESCUDOS_MAGICOS_ENCANTOS_DATA
from tabelas.base.tabela_8_11_data import ARMADURAS_ESCUDOS_ESPECIFICOS_DATA
from tabelas.base.tabela_8_13_data import ACESSORIOS_MENORES_DATA
from tabelas.base.tabela_8_14_data import ACESSORIOS_MEDIOS_DATA
from tabelas.base.tabela_8_15_data import ACESSORIOS_MAIORES_DATA

# --- Funções Auxiliares ---


def _determinar_tipo_item_magico_d6(mod_2D_ativo, log_principal):
    """
    Rola 1d6 (ou 2d6 com escolha) para determinar o tipo de item mágico.
    Retorna: (str_tipo_item, int_d6_escolhido, str_log_d6)
    str_tipo_item: "arma", "armadura_escudo", ou "acessorio"
    """
    d6_rolagens = [random.randint(1, 6)]
    log_rolagem_d6 = f"d6 para tipo de Item Mágico: Rolagem 1 = {d6_rolagens[0]}"

    if mod_2D_ativo:
        d6_rolagens.append(random.randint(1, 6))
        log_rolagem_d6 += f"; Rolagem 2 = {d6_rolagens[1]}"
        # Escolha automática: maior valor. Em jogo, jogador escolheria.
        escolha_d6 = max(d6_rolagens)
        log_rolagem_d6 += f". Modificador 2D ativo, escolhido (max): {escolha_d6}"
    else:
        escolha_d6 = d6_rolagens[0]
        log_rolagem_d6 += f". Escolhido: {escolha_d6}"

    tipo_item_str = None
    if 1 <= escolha_d6 <= 2:
        tipo_item_str = "arma"
        log_rolagem_d6 += " -> Arma Mágica"
    elif escolha_d6 == 3:
        tipo_item_str = "armadura_escudo"
        log_rolagem_d6 += " -> Armadura/Escudo Mágico"
    elif 4 <= escolha_d6 <= 6:
        tipo_item_str = "acessorio"
        log_rolagem_d6 += " -> Acessório Mágico"

    log_principal.append(f"  Item Mágico - {log_rolagem_d6}")
    return tipo_item_str, escolha_d6, log_rolagem_d6


def _obter_item_base_t84(categoria_t84_key, log_principal, sub_log_header="    "):
    """
    Rola um item base da Tabela 8-4 para a categoria especificada.
    Retorna: {"nome": nome_item, "quantidade": qtd (opcional), "subcategoria": categoria_t84_key}
    """
    tabela_base = EQUIPAMENTO_DATA.get(categoria_t84_key)
    if not tabela_base:
        log_principal.append(
            f"{sub_log_header}ALERTA: Categoria '{categoria_t84_key}' não encontrada na Tabela 8-4 para item base.")
        return None

    resultado_rolagem_t8_4 = rolar_em_tabela_d_porcento(tabela_base)
    if resultado_rolagem_t8_4 and "entrada_tabela" in resultado_rolagem_t8_4:
        item_info = resultado_rolagem_t8_4["entrada_tabela"]
        nome_item = item_info.get("item", "Item Base Desconhecido")
        quantidade = item_info.get("quantidade")

        log_msg = (f"Item Base (Tabela 8-4 {categoria_t84_key}): d100 base {resultado_rolagem_t8_4['d100_base']} "
                   f"(mod {resultado_rolagem_t8_4['modificador']}) -> final {resultado_rolagem_t8_4['d100_final']} -> {nome_item}"
                   f"{f' (Qtd: {quantidade})' if quantidade else ''}")
        log_principal.append(f"{sub_log_header}{log_msg}")
        return {"nome": nome_item, "quantidade": quantidade, "subcategoria": categoria_t84_key, "log_rolagem_base": log_msg}

    log_principal.append(
        f"{sub_log_header}Falha ao rolar item base na Tabela 8-4 ({categoria_t84_key}).")
    return None

# --- Lógica para Armas Mágicas (T8-8, T8-9) ---


def _aplicar_encantos_arma(categoria_magica, log_principal):
    """Aplica encantos da Tabela 8-8 a uma arma."""
    if categoria_magica == "menor":
        max_custo_total = 1
    elif categoria_magica == "medio":
        max_custo_total = 2
    elif categoria_magica == "maior":
        max_custo_total = 3
    else:
        return []  # Categoria inválida

    encantos_finais = []
    custo_usado = 0
    tentativas = 0
    max_tentativas_loop = 20  # Para evitar loops infinitos

    while custo_usado < max_custo_total and tentativas < max_tentativas_loop:
        tentativas += 1
        resultado_rolagem_t8_8 = rolar_em_tabela_d_porcento(
            ARMAS_MAGICAS_ENCANTOS_DATA)
        if not resultado_rolagem_t8_8 or "entrada_tabela" not in resultado_rolagem_t8_8:
            log_principal.append(
                f"      ALERTA: Falha ao rolar encanto na Tabela 8-8.")
            continue

        encanto_info = resultado_rolagem_t8_8["entrada_tabela"]
        nome_encanto = encanto_info.get("encanto")
        custo_atual = encanto_info.get("custo_encantos", 1)
        reroll_menor = encanto_info.get("reroll_se_menor", False)
        ref_tabela = encanto_info.get("referencia_tabela")

        log_rolagem_encanto = (f"Encanto Arma (T8-8): d100 base {resultado_rolagem_t8_8['d100_base']} "
                               f"(mod {resultado_rolagem_t8_8['modificador']}) -> final {resultado_rolagem_t8_8['d100_final']} -> '{nome_encanto}' (Custo: {custo_atual})")

        if categoria_magica == "menor" and reroll_menor and custo_atual > 1:
            log_principal.append(
                f"      {log_rolagem_encanto} - Rerolado (item menor, custo > 1).")
            continue
        if (custo_usado + custo_atual) > max_custo_total:
            log_principal.append(
                f"      {log_rolagem_encanto} - Rerolado (não cabe nos slots restantes: {max_custo_total - custo_usado}).")
            continue

        # Encanto válido e cabe
        log_principal.append(f"      {log_rolagem_encanto} - Aplicado.")

        if ref_tabela == "8-9":  # Arma específica
            log_principal.append(
                f"        Resultado '{nome_encanto}', redirecionando para Tabela 8-9...")
            resultado_t8_9 = rolar_em_tabela_d_porcento(ARMAS_ESPECIFICAS_DATA)
            if resultado_t8_9 and "entrada_tabela" in resultado_t8_9:
                arma_especifica_info = resultado_t8_9["entrada_tabela"]
                nome_arma_esp = arma_especifica_info.get("nome_arma")
                log_arma_esp = (f"Arma Específica (T8-9): d100 base {resultado_t8_9['d100_base']} "
                                f"(mod {resultado_t8_9['modificador']}) -> final {resultado_t8_9['d100_final']} -> '{nome_arma_esp}'")
                log_principal.append(f"          {log_arma_esp}")
                # Arma específica geralmente substitui tudo
                return [{"nome": nome_arma_esp, "tipo_especial": "arma_especifica_t89", "preco_ts": arma_especifica_info.get("preco_ts"), "log_rolagem": [log_rolagem_encanto, log_arma_esp]}]
            else:
                log_principal.append(
                    f"          ALERTA: Falha ao rolar na Tabela 8-9.")
                # Decide se continua tentando outros encantos ou para. Por ora, para.
                return [{"nome": "Falha ao rolar Arma Específica T8-9", "log_rolagem": [log_rolagem_encanto]}]

        encantos_finais.append({"nome": nome_encanto, "efeito": encanto_info.get(
            "efeito"), "custo": custo_atual, "log_rolagem": [log_rolagem_encanto]})
        custo_usado += custo_atual
        tentativas = 0  # Reseta tentativas se um encanto válido foi adicionado

    if custo_usado < max_custo_total and tentativas == max_tentativas_loop:
        log_principal.append(
            f"      ALERTA: Atingido limite de tentativas sem preencher todos os {max_custo_total} slots de encanto para arma {categoria_magica}. Slots preenchidos: {custo_usado}.")

    return encantos_finais


def _processar_arma_magica_detalhado(categoria_magica, log_principal):
    log_principal.append(f"    Gerando Arma Mágica ({categoria_magica})...")
    item_base_arma_info = _obter_item_base_t84(
        "armas", log_principal, sub_log_header="      ")
    if not item_base_arma_info:
        return {"tipo_gerado": "arma_magica_erro", "descricao": "Falha ao obter arma base", "detalhes_rolagem_especifica": ["Erro T8-4"]}

    log_principal.append(
        f"      Aplicando encantos à base '{item_base_arma_info['nome']}'...")
    lista_encantos = _aplicar_encantos_arma(categoria_magica, log_principal)

    return {
        "tipo_gerado": "arma_magica",
        "nome_base": item_base_arma_info["nome"],
        "categoria_magica": categoria_magica,
        "encantos": lista_encantos,
        # Coleta logs
        "detalhes_rolagem_especifica": [item_base_arma_info["log_rolagem_base"]] + [e["log_rolagem"][0] for e in lista_encantos if isinstance(e, dict) and "log_rolagem" in e]
    }

# --- Lógica para Armaduras/Escudos Mágicos (T8-10, T8-11) ---


# tipo_item_base: "armadura" ou "escudo"
def _aplicar_encantos_armadura_escudo(categoria_magica, tipo_item_base, log_principal):
    if categoria_magica == "menor":
        max_custo_total = 1
    elif categoria_magica == "medio":
        max_custo_total = 2
    elif categoria_magica == "maior":
        max_custo_total = 3
    else:
        return []

    encantos_finais = []
    custo_usado = 0
    tentativas = 0
    max_tentativas_loop = 20

    while custo_usado < max_custo_total and tentativas < max_tentativas_loop:
        tentativas += 1
        resultado_rolagem_t8_10 = rolar_em_tabela_d_porcento(
            ARMADURAS_ESCUDOS_MAGICOS_ENCANTOS_DATA)
        if not resultado_rolagem_t8_10 or "entrada_tabela" not in resultado_rolagem_t8_10:
            log_principal.append(
                f"      ALERTA: Falha ao rolar encanto na Tabela 8-10.")
            continue

        encanto_info = resultado_rolagem_t8_10["entrada_tabela"]
        nome_encanto = encanto_info.get("encanto")
        custo_atual = encanto_info.get("custo_encantos", 1)
        reroll_menor = encanto_info.get("reroll_se_menor", False)
        apenas_escudos = encanto_info.get("apenas_escudos", False)
        ref_tabela = encanto_info.get("referencia_tabela")

        log_rolagem_encanto = (f"Encanto Arm/Esc (T8-10): d100 base {resultado_rolagem_t8_10['d100_base']} "
                               f"(mod {resultado_rolagem_t8_10['modificador']}) -> final {resultado_rolagem_t8_10['d100_final']} -> '{nome_encanto}' (Custo: {custo_atual})")

        if apenas_escudos and tipo_item_base == "armadura":
            log_principal.append(
                f"      {log_rolagem_encanto} - Rerolado ('{nome_encanto}' é apenas para escudos, item base é armadura).")
            continue
        if categoria_magica == "menor" and reroll_menor and custo_atual > 1:
            log_principal.append(
                f"      {log_rolagem_encanto} - Rerolado (item menor, custo > 1).")
            continue
        if (custo_usado + custo_atual) > max_custo_total:
            log_principal.append(
                f"      {log_rolagem_encanto} - Rerolado (não cabe nos slots restantes: {max_custo_total - custo_usado}).")
            continue

        log_principal.append(f"      {log_rolagem_encanto} - Aplicado.")

        if ref_tabela == "8-11":  # Item específico
            log_principal.append(
                f"        Resultado '{nome_encanto}', redirecionando para Tabela 8-11...")
            resultado_t8_11 = rolar_em_tabela_d_porcento(
                ARMADURAS_ESCUDOS_ESPECIFICOS_DATA)
            if resultado_t8_11 and "entrada_tabela" in resultado_t8_11:
                item_especifico_info = resultado_t8_11["entrada_tabela"]
                nome_item_esp = item_especifico_info.get("nome_item")
                log_item_esp = (f"Item Específico (T8-11): d100 base {resultado_t8_11['d100_base']} "
                                f"(mod {resultado_t8_11['modificador']}) -> final {resultado_t8_11['d100_final']} -> '{nome_item_esp}'")
                log_principal.append(f"          {log_item_esp}")
                return [{"nome": nome_item_esp, "tipo_especial": "arm_esc_especifico_t811", "preco_ts": item_especifico_info.get("preco_ts"), "log_rolagem": [log_rolagem_encanto, log_item_esp]}]
            else:
                log_principal.append(
                    f"          ALERTA: Falha ao rolar na Tabela 8-11.")
                return [{"nome": "Falha ao rolar Item Específico T8-11", "log_rolagem": [log_rolagem_encanto]}]

        encantos_finais.append({"nome": nome_encanto, "efeito": encanto_info.get(
            "efeito"), "custo": custo_atual, "log_rolagem": [log_rolagem_encanto]})
        custo_usado += custo_atual
        tentativas = 0

    if custo_usado < max_custo_total and tentativas == max_tentativas_loop:
        log_principal.append(
            f"      ALERTA: Atingido limite de tentativas sem preencher todos os {max_custo_total} slots de encanto para armadura/escudo {categoria_magica}. Slots preenchidos: {custo_usado}.")

    return encantos_finais


def _processar_armadura_escudo_magico_detalhado(categoria_magica, log_principal):
    log_principal.append(
        f"    Gerando Armadura/Escudo Mágico ({categoria_magica})...")
    item_base_info = _obter_item_base_t84(
        "armaduras_escudos", log_principal, sub_log_header="      ")
    if not item_base_info:
        return {"tipo_gerado": "arm_esc_magico_erro", "descricao": "Falha ao obter armadura/escudo base", "detalhes_rolagem_especifica": ["Erro T8-4"]}

    # Determinar se o item base é "armadura" ou "escudo" para a regra "apenas_escudos"
    # Isso é uma simplificação; idealmente, o nome do item base indicaria (ex: "Escudo Leve")
    tipo_base_especifico = "armadura"  # Default
    if "escudo" in item_base_info["nome"].lower():
        tipo_base_especifico = "escudo"
    log_principal.append(
        f"      Item base '{item_base_info['nome']}' considerado como '{tipo_base_especifico}' para aplicação de encantos.")

    log_principal.append(
        f"      Aplicando encantos à base '{item_base_info['nome']}'...")
    lista_encantos = _aplicar_encantos_armadura_escudo(
        categoria_magica, tipo_base_especifico, log_principal)

    return {
        "tipo_gerado": "armadura_escudo_magico",
        "nome_base": item_base_info["nome"],
        "categoria_magica": categoria_magica,
        "tipo_base": tipo_base_especifico,
        "encantos": lista_encantos,
        "detalhes_rolagem_especifica": [item_base_info["log_rolagem_base"]] + [e["log_rolagem"][0] for e in lista_encantos if isinstance(e, dict) and "log_rolagem" in e]
    }

# --- Lógica para Acessórios Mágicos (T8-13, T8-14, T8-15) ---


def _processar_acessorio_magico_detalhado(categoria_magica, log_principal):
    log_principal.append(
        f"    Gerando Acessório Mágico ({categoria_magica})...")

    tabela_acessorios = None
    nome_tabela_log = ""
    if categoria_magica == "menor":
        tabela_acessorios = ACESSORIOS_MENORES_DATA
        nome_tabela_log = "Tabela 8-13 (Acessórios Menores)"
    elif categoria_magica == "medio":
        tabela_acessorios = ACESSORIOS_MEDIOS_DATA
        nome_tabela_log = "Tabela 8-14 (Acessórios Médios)"
    elif categoria_magica == "maior":
        tabela_acessorios = ACESSORIOS_MAIORES_DATA
        nome_tabela_log = "Tabela 8-15 (Acessórios Maiores)"
    else:
        log_principal.append(
            f"      ALERTA: Categoria de acessório mágico desconhecida: {categoria_magica}")
        return {"tipo_gerado": "acessorio_magico_erro", "descricao": f"Categoria {categoria_magica} inválida"}

    resultado_rolagem_acessorio = rolar_em_tabela_d_porcento(tabela_acessorios)
    if resultado_rolagem_acessorio and "entrada_tabela" in resultado_rolagem_acessorio:
        acessorio_info = resultado_rolagem_acessorio["entrada_tabela"]
        nome_acessorio = acessorio_info.get("nome_acessorio")

        log_msg = (f"Acessório Mágico ({nome_tabela_log}): d100 base {resultado_rolagem_acessorio['d100_base']} "
                   f"(mod {resultado_rolagem_acessorio['modificador']}) -> final {resultado_rolagem_acessorio['d100_final']} -> '{nome_acessorio}'")
        log_principal.append(f"      {log_msg}")

        return {
            "tipo_gerado": "acessorio_magico",
            "nome": nome_acessorio,
            "preco_ts": acessorio_info.get("preco_ts"),
            "categoria_magica": categoria_magica,
            "detalhes_rolagem_especifica": [log_msg]
        }
    else:
        log_principal.append(
            f"      ALERTA: Falha ao rolar em {nome_tabela_log}.")
        return {"tipo_gerado": "acessorio_magico_erro", "descricao": f"Falha ao rolar em {nome_tabela_log}"}

# --- Função Principal de Despacho ---


def processar_item_magico_t81(obj_resultado_t81_magico, log_principal):
    """
    Processa um resultado "Mágico" da Tabela 8-1.
    obj_resultado_t81_magico: {"tipo": "Mágico", "categoria": "menor/medio/maior", "mod_2D_tipo": True/False}
    log_principal: Lista para adicionar logs de rolagem.
    Retorna: Dicionário com os detalhes do item mágico gerado.
    """
    if obj_resultado_t81_magico.get("tipo") != "Mágico":
        log_principal.append(
            f"ALERTA em itens_magicos: Tentativa de processar '{obj_resultado_t81_magico.get('tipo')}' como 'Mágico'.")
        return None

    categoria_magica = obj_resultado_t81_magico.get(
        "categoria", "menor")  # Default para menor se não especificado
    mod_2D_tipo_ativo = obj_resultado_t81_magico.get("mod_2D_tipo", False)

    log_principal.append(
        f"Processando Item Mágico (Categoria: {categoria_magica}, Modificador 2D para tipo: {mod_2D_tipo_ativo})...")

    # Log já adicionado por _determinar...
    tipo_item_magico_str, _, _ = _determinar_tipo_item_magico_d6(
        mod_2D_tipo_ativo, log_principal)

    if tipo_item_magico_str == "arma":
        return _processar_arma_magica_detalhado(categoria_magica, log_principal)
    elif tipo_item_magico_str == "armadura_escudo":
        return _processar_armadura_escudo_magico_detalhado(categoria_magica, log_principal)
    elif tipo_item_magico_str == "acessorio":
        return _processar_acessorio_magico_detalhado(categoria_magica, log_principal)
    else:
        log_principal.append(
            f"  ALERTA: Tipo de item mágico determinado pelo d6 ('{tipo_item_magico_str}') é inválido.")
        return {"tipo_gerado": "item_magico_erro", "descricao": "Tipo de item mágico inválido após rolagem d6"}
