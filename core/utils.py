# core/utils.py
import random
import re


def _rolar_dados_simples_detalhado(num_dados, lados_dado):
    """
    Rola NdM e retorna um dicionário com a soma e os rolos individuais.
    Ex: _rolar_dados_simples_detalhado(2, 6) -> {"soma": 8, "rolos": [5, 3]}
    """
    if num_dados <= 0 or lados_dado <= 0:
        return {"soma": 0, "rolos": []}
    rolos = [random.randint(1, lados_dado) for _ in range(num_dados)]
    return {"soma": sum(rolos), "rolos": rolos}


def rolar_expressao_dados(expressao_original):
    """
    Rola dados com base em uma expressão string.
    Retorna um dicionário: {"valor": resultado_int, "detalhes_rolagem": "string_descritiva_das_etapas"}
    Ex: "2d6+1*100" -> {"valor": 700, "detalhes_rolagem": "2d6 (3, 2) = 5; 5+1 = 6; 6*100 = 600"}
    Também lida com 'x' como multiplicador, convertendo para '*'.
    """
    expressao_input = str(expressao_original).strip().lower()

    # >>> INÍCIO DA MUDANÇA: Padroniza 'x' para '*' ANTES de tentar os matches <<<
    expressao = expressao_input.replace('x', '*')
    # >>> FIM DA MUDANÇA <<<

    etapas_rolagem = []

    # Padrão: (NdM+K)*C  -> (\d+)d(\d+)\s*\+\s*(\d+)\s*\*\s*(\d+)
    # Ex: "2d6+1*100" (significa (2d6+1) * 100)
    m = re.fullmatch(r"(\d+)d(\d+)\s*\+\s*(\d+)\s*\*\s*(\d+)", expressao)
    if m:
        num_dados, lados_dado, k_add, k_mult = map(int, m.groups())
        dados_base_info = _rolar_dados_simples_detalhado(num_dados, lados_dado)
        etapas_rolagem.append(
            f"{num_dados}d{lados_dado} {tuple(dados_base_info['rolos'])} = {dados_base_info['soma']}")

        resultado_com_add = dados_base_info['soma'] + k_add
        etapas_rolagem.append(
            f"{dados_base_info['soma']}+{k_add} = {resultado_com_add}")

        valor_final = resultado_com_add * k_mult
        etapas_rolagem.append(f"{resultado_com_add}*{k_mult} = {valor_final}")
        return {"valor": valor_final, "detalhes_rolagem": "; ".join(etapas_rolagem)}

    # Padrão: NdM*K -> (\d+)d(\d+)\s*\*\s*(\d+)
    # Ex: "1d6*10", "2d4*1000" (após 'x' ser convertido para '*')
    m = re.fullmatch(r"(\d+)d(\d+)\s*\*\s*(\d+)", expressao)
    if m:
        num_dados, lados_dado, k_mult = map(int, m.groups())
        dados_base_info = _rolar_dados_simples_detalhado(num_dados, lados_dado)
        etapas_rolagem.append(
            f"{num_dados}d{lados_dado} {tuple(dados_base_info['rolos'])} = {dados_base_info['soma']}")

        valor_final = dados_base_info['soma'] * k_mult
        etapas_rolagem.append(
            f"{dados_base_info['soma']}*{k_mult} = {valor_final}")
        return {"valor": valor_final, "detalhes_rolagem": "; ".join(etapas_rolagem)}

    # Padrão: NdM+K -> (\d+)d(\d+)\s*\+\s*(\d+)
    # Ex: "2d8+2", "1d4+1"
    m = re.fullmatch(r"(\d+)d(\d+)\s*\+\s*(\d+)", expressao)
    if m:
        num_dados, lados_dado, k_add = map(int, m.groups())
        dados_base_info = _rolar_dados_simples_detalhado(num_dados, lados_dado)
        etapas_rolagem.append(
            f"{num_dados}d{lados_dado} {tuple(dados_base_info['rolos'])} = {dados_base_info['soma']}")

        valor_final = dados_base_info['soma'] + k_add
        etapas_rolagem.append(
            f"{dados_base_info['soma']}+{k_add} = {valor_final}")
        return {"valor": valor_final, "detalhes_rolagem": "; ".join(etapas_rolagem)}

    # Padrão: NdM -> (\d+)d(\d+)
    # Ex: "1d6", "4d12"
    m = re.fullmatch(r"(\d+)d(\d+)", expressao)
    if m:
        num_dados, lados_dado = map(int, m.groups())
        dados_base_info = _rolar_dados_simples_detalhado(num_dados, lados_dado)
        return {"valor": dados_base_info['soma'], "detalhes_rolagem": f"{num_dados}d{lados_dado} {tuple(dados_base_info['rolos'])} = {dados_base_info['soma']}"}

    # Padrão: K (apenas um número constante)
    m = re.fullmatch(r"(\d+)", expressao)
    if m:
        valor_final = int(m.group(1))
        return {"valor": valor_final, "detalhes_rolagem": f"Valor constante: {valor_final}"}

    raise ValueError(
        f"Expressão de dados não reconhecida ou inválida: '{expressao_original}' (Processada como: '{expressao}')")


def rolar_em_tabela_d_porcento(tabela_entradas, d100_roll_override=None, modificador_d100=0):
    """
    Rola 1d100 (ou usa um valor fornecido), aplica modificador, e encontra a entrada.
    O modificador_d100 é somado à rolagem base. A lógica de cap (ex: max 100 para poções/riquezas)
    deve ser tratada ANTES de passar o modificador_d100 ou ajustando o roll_final aqui se for genérico.
    Para poções/riquezas, o modificador é +20, e o resultado final do d100 é capado em 100.

    Retorna: 
        Um dicionário {"entrada_tabela": dict_da_entrada, "d100_base": int, "modificador": int, "d100_final": int_com_mod} 
        ou None se nenhuma entrada for encontrada.
    """
    if not tabela_entradas:
        return None

    d100_base = d100_roll_override if d100_roll_override is not None else random.randint(
        1, 100)
    d100_final = d100_base + modificador_d100

    # Cap genérico para d100, se necessário, ou o chamador garante que o modificador é apropriado.
    # Para a regra específica de +20% capado em 100 para riquezas/poções,
    # o ideal é que a função chamadora prepare o `modificador_d100` ou
    # esta função tenha um parâmetro extra para essa regra de cap.
    # Por agora, faremos um cap simples:
    if d100_final > 100:
        d100_final = 100
    if d100_final < 1:
        d100_final = 1

    for entrada in tabela_entradas:
        if not all(k in entrada for k in ("d_min", "d_max")):
            continue
        try:
            d_min = int(entrada["d_min"])
            d_max = int(entrada["d_max"])
        except ValueError:
            continue

        if d_min <= d100_final <= d_max:
            return {
                "entrada_tabela": entrada,
                "d100_base": d100_base,
                "modificador": modificador_d100,
                "d100_final": d100_final
            }

    print(
        f"ALERTA: Rolagem d100 final ({d100_final}) não encontrou correspondência. (Base: {d100_base}, Mod: {modificador_d100})")
    return None
