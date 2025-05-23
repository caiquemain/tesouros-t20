# core/dinheiro.py
import random
# Funções de utils.py
from .utils import rolar_expressao_dados, rolar_em_tabela_d_porcento
from tabelas.base.tabela_8_2_data import RIQUEZAS_DATA  # Dados da Tabela 8-2


def _rolar_riqueza_individual(categoria_riqueza_str, aplicar_mod_20_porcento, log_principal):
    """
    Rola uma única riqueza na Tabela 8-2, calcula seu valor e retorna seus detalhes.
    Adiciona detalhes da rolagem ao log_principal.
    """
    modificador_d100_aplicado = 0
    if aplicar_mod_20_porcento:
        modificador_d100_aplicado = 20
        # A regra de cap em 100 (+20%, max 100) é tratada em rolar_em_tabela_d_porcento
        # pela forma como ele agora lida com d100_final.

    # A função rolar_em_tabela_d_porcento é genérica. A lógica de qual parte da
    # RIQUEZAS_DATA usar com base na categoria e na rolagem d100 precisa ser feita aqui.

    d100_base = random.randint(1, 100)
    d100_efetivo = d100_base + modificador_d100_aplicado
    if d100_efetivo > 100:
        d100_efetivo = 100
    if d100_efetivo < 1:
        d100_efetivo = 1

    cat_normalizada = categoria_riqueza_str.lower()
    if cat_normalizada.endswith("es"):  # ex: menores -> menor
        cat_normalizada = cat_normalizada[:-2]

    item_riqueza_encontrado_dados = None
    for entrada_tabela_riqueza in RIQUEZAS_DATA:
        # Verifica se a categoria atual tem rolagens definidas para esta entrada da RIQUEZAS_DATA
        if cat_normalizada in entrada_tabela_riqueza["rolagens"]:
            for d_min, d_max in entrada_tabela_riqueza["rolagens"][cat_normalizada]:
                if d_min <= d100_efetivo <= d_max:
                    item_riqueza_encontrado_dados = entrada_tabela_riqueza
                    break
            if item_riqueza_encontrado_dados:
                break

    log_msg_rolagem_t8_2 = (f"T8-2 Riqueza ({categoria_riqueza_str}, Mod+20%: {aplicar_mod_20_porcento}): "
                            f"d100 base {d100_base} + mod {modificador_d100_aplicado} = final {d100_efetivo}")

    if item_riqueza_encontrado_dados:
        valor_expressao_riqueza = item_riqueza_encontrado_dados["valor_expressao"]
        info_valor_rolado = rolar_expressao_dados(valor_expressao_riqueza)
        valor_calculado_ts = info_valor_rolado["valor"]
        detalhes_rolagem_valor = info_valor_rolado["detalhes_rolagem"]

        log_principal.append(
            f"  {log_msg_rolagem_t8_2} -> Encontrado: '{item_riqueza_encontrado_dados['exemplos'][:40]}...' (Valor base: {valor_expressao_riqueza} T$)")
        log_principal.append(
            f"    Rolagem do Valor da Riqueza: {detalhes_rolagem_valor} = {valor_calculado_ts} T$")

        return {
            "tipo_gerado": "riqueza_individual",  # Para diferenciar do conjunto de riquezas
            "descricao_exemplos": item_riqueza_encontrado_dados["exemplos"],
            "valor_calculado_ts": valor_calculado_ts,
            # Pode ser útil
            "valor_medio_ts": item_riqueza_encontrado_dados["valor_medio"],
            "categoria_usada": categoria_riqueza_str,
            "detalhes_rolagem_especifica": [log_msg_rolagem_t8_2, f"Rolagem Valor: {detalhes_rolagem_valor}"]
        }
    else:
        log_principal.append(
            f"  {log_msg_rolagem_t8_2} -> Nenhuma riqueza encontrada para esta rolagem (verifique a Tabela 8-2 ou a lógica).")
        return None


def processar_moedas_t81(obj_moedas_t81, mod_metade_ativo, log_principal):
    """
    Processa um resultado de "moedas" da Tabela 8-1.
    Retorna um dicionário com os detalhes das moedas ou None.
    """
    if obj_moedas_t81.get("tipo") != "moedas":
        return None

    expressao = obj_moedas_t81["expressao"]
    unidade = obj_moedas_t81["unidade"]

    info_rolagem_moedas = rolar_expressao_dados(expressao)
    quantidade_moedas = info_rolagem_moedas["valor"]

    log_base_moedas = f"Moedas ({unidade}) Expressão '{expressao}': {info_rolagem_moedas['detalhes_rolagem']}"

    if mod_metade_ativo:
        quantidade_final_moedas = quantidade_moedas // 2
        log_principal.append(
            f"{log_base_moedas}. Modificador 'Metade' aplicado. Final: {quantidade_final_moedas} {unidade}.")
    else:
        quantidade_final_moedas = quantidade_moedas
        log_principal.append(
            f"{log_base_moedas}. Quantidade final: {quantidade_final_moedas} {unidade}.")

    return {
        "tipo_gerado": "moedas",
        "unidade": unidade,
        "quantidade": quantidade_final_moedas,
        "detalhes_rolagem_especifica": [info_rolagem_moedas['detalhes_rolagem']]
    }


def processar_riquezas_t81(obj_riqueza_t81, log_principal):
    """
    Processa um resultado de "riqueza" da Tabela 8-1, rolando na Tabela 8-2 para cada item.
    Retorna um dicionário contendo uma lista de riquezas processadas.
    """
    if obj_riqueza_t81.get("tipo") != "riqueza":
        return None

    quantidade_dado_str = obj_riqueza_t81["quantidade_dado"]
    categoria_riqueza = obj_riqueza_t81["categoria"]
    aplicar_mod_20 = obj_riqueza_t81.get("mod_20_porcento", False)

    info_rolagem_qtd = rolar_expressao_dados(quantidade_dado_str)
    num_riquezas_a_gerar = info_rolagem_qtd["valor"]
    log_principal.append(
        f"Riquezas (Categoria: {categoria_riqueza}, Mod+20%: {aplicar_mod_20}): "
        f"Rolando quantidade '{quantidade_dado_str}' -> {info_rolagem_qtd['detalhes_rolagem']} = {num_riquezas_a_gerar} item(ns)."
    )

    if num_riquezas_a_gerar == 0:
        return {"tipo_gerado": "riquezas_conjunto", "itens": [], "detalhes_rolagem_conjunto": [info_rolagem_qtd['detalhes_rolagem']]}

    lista_de_itens_riqueza = []
    # Coleta os detalhes de rolagem da quantidade para o log do conjunto
    detalhes_log_conjunto = [info_rolagem_qtd['detalhes_rolagem']]

    log_principal.append(
        f"  Gerando {num_riquezas_a_gerar} item(ns) de riqueza individualmente...")
    for i in range(num_riquezas_a_gerar):
        # Cabeçalho para os logs da riqueza individual
        log_principal.append(f"    Processando Riqueza Individual #{i+1}...")
        item_riqueza_individual = _rolar_riqueza_individual(
            categoria_riqueza, aplicar_mod_20, log_principal)
        if item_riqueza_individual:
            lista_de_itens_riqueza.append(item_riqueza_individual)
            # Os detalhes da rolagem individual já foram adicionados ao log_principal.
            # Adicionamos ao log do conjunto para referência no objeto final.
            if "detalhes_rolagem_especifica" in item_riqueza_individual:
                detalhes_log_conjunto.extend(
                    item_riqueza_individual["detalhes_rolagem_especifica"])

    return {
        "tipo_gerado": "riquezas_conjunto",
        "itens": lista_de_itens_riqueza,  # Lista de dicionários, cada um sendo uma riqueza
        "detalhes_rolagem_conjunto": detalhes_log_conjunto  # Log resumido do conjunto
    }
