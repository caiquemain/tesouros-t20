# tabelas/base/tabela_8_1_data.py
import re


def _parse_resultado_string(s_original):
    """
    Converte a string de resultado da Tabela 8-1 para uma estrutura de dicionário.
    """
    s = str(s_original).strip()  # Garante que é string e remove espaços extras

    # Tratar modificadores primeiro
    mod_20_porcento = False
    if "+%" in s or "*" in s:  # Usuário usou +% ou * para o modificador de 20%
        mod_20_porcento = True
        s = s.replace("+%", "").replace("*", "")

    mod_2D_tipo = False
    if "2D" in s:
        mod_2D_tipo = True
        s = s.replace("2D", "")

    s = s.strip()  # Remover espaços após a remoção de modificadores

    if s == "—":
        return {"tipo": "nada"}
    if s == "Diverso":
        # mod_2D_tipo seria False aqui, a menos que a string fosse "Diverso2D"
        return {"tipo": "Diverso"}

    if s.startswith("Equipamento"):  # Ex: "Equipamento", "Equipamento2D"
        return {"tipo": "Equipamento", "mod_2D_tipo": mod_2D_tipo}

    if s.startswith("Superior"):  # Ex: "Superior (1 melhoria)", "Superior (2 melhorias)2D"
        match_melhorias = re.search(r"\((\d+)\s*melhoria[s]?\)", s)
        melhorias = 0
        if match_melhorias:
            melhorias = int(match_melhorias.group(1))
        return {"tipo": "Superior", "melhorias": melhorias, "mod_2D_tipo": mod_2D_tipo}

    if s.startswith("Mágico"):  # Ex: "Mágico (menor)", "Mágico (médio)2D"
        categoria = "desconhecida"
        if "(menor)" in s:
            categoria = "menor"
        elif "(médio)" in s:
            categoria = "medio"
        elif "(maior)" in s:
            categoria = "maior"
        return {"tipo": "Mágico", "categoria": categoria, "mod_2D_tipo": mod_2D_tipo}

    # Poções: "1 poção", "1d3 poções", "1d3+1 poções+%"
    match_pocao = re.match(
        r"((?:\d+d\d+\s*\+\s*\d+)|(?:\d+d\d+)|(?:\d+))?\s*poç(?:ão|ões)", s, re.IGNORECASE)
    if match_pocao:
        quantidade_str = "1"
        if match_pocao.group(1):
            quantidade_str = match_pocao.group(1).strip()
        return {"tipo": "poção", "quantidade_str": quantidade_str, "mod_20_porcento_tabela_pocao": mod_20_porcento, "mod_2D_tipo": mod_2D_tipo}

    # Riquezas: "1 riqueza menor", "1d3 riquezas médias+%", "riqueza maior"
    match_riqueza = re.match(
        r"((?:\d+d\d+\s*\+\s*\d+)|(?:\d+d\d+)|(?:\d+))?\s*riqueza[s]?\s*(menor|média|maior|menores|médias|maiores)", s, re.IGNORECASE)
    if match_riqueza:
        quantidade_dado = "1"
        if match_riqueza.group(1):
            quantidade_dado = match_riqueza.group(1).strip()

        categoria_raw = match_riqueza.group(2).lower()
        categoria = categoria_raw
        if categoria_raw == "menores":
            categoria = "menor"
        elif categoria_raw == "médias":
            categoria = "média"
        elif categoria_raw == "maiores":
            categoria = "maior"

        return {"tipo": "riqueza", "quantidade_dado": quantidade_dado, "categoria": categoria, "mod_20_porcento": mod_20_porcento}

    # Moedas: "1d6x10 TC", "2d6+1x100 T$", "2d4x1.000 TO"
    match_moedas = re.match(
        r"([\d\w\+\s\.]+?(?:x[\d\.,]+)?)\s*([A-Z$]{1,2})", s)
    if match_moedas:
        expressao_bruta = match_moedas.group(1).strip()
        unidade = match_moedas.group(2).strip()

        expressao_final = expressao_bruta
        if "x1.000" in expressao_bruta:
            expressao_final = expressao_bruta.replace("x1.000", "*1000")
        else:
            expressao_final = expressao_bruta.replace("x", "*")

        # Mantenha esta linha de DEBUG por enquanto para confirmar a correção:
        print(
            f"DEBUG PARSER MOEDAS (CORRIGIDO): Input='{s_original}' -> Expressão Gerada='{expressao_final}', Unidade Gerada='{unidade}'")

        return {"tipo": "moedas", "expressao": expressao_final, "unidade": unidade}


_DADOS_BRUTOS_TABELA_8_1 = {
    "1/4": {
        "dinheiro": [("01", "30", "—"), ("31", "70", "1d6x10 TC"), ("71", "95", "1d4x100 TC"), ("96", "100", "1d6x10 T$")],
        "itens": [("01", "50", "—"), ("51", "75", "Diverso"), ("76", "100", "Equipamento")]
    },
    "1/2": {
        "dinheiro": [("01", "25", "—"), ("26", "70", "2d6x10 TC"), ("71", "95", "2d8x10 T$"), ("96", "100", "1d4x100 T$")],
        "itens": [("01", "45", "—"), ("46", "70", "Diverso"), ("71", "100", "Equipamento")]
    },
    "1": {
        "dinheiro": [("01", "20", "—"), ("21", "70", "3d8x10 T$"), ("71", "95", "4d12x10 T$"), ("96", "100", "1 riqueza menor")],
        "itens": [("01", "40", "—"), ("41", "65", "Diverso"), ("66", "90", "Equipamento"), ("91", "100", "1 poção")]
    },
    "2": {
        "dinheiro": [("01", "15", "—"), ("16", "55", "3d10x10 T$"), ("56", "85", "2d4x100 T$"), ("86", "95", "2d6+1x100 T$"), ("96", "100", "1 riqueza menor")],
        "itens": [("01", "30", "—"), ("31", "40", "Diverso"), ("41", "70", "Equipamento"), ("71", "90", "1 poção"), ("91", "100", "Superior (1 melhoria)")]
    },
    "3": {
        "dinheiro": [("01", "10", "—"), ("11", "20", "4d12x10 T$"), ("21", "60", "1d4x100 T$"), ("61", "90", "1d8x10 TO"), ("91", "100", "1d3 riquezas menores")],
        "itens": [("01", "25", "—"), ("26", "35", "Diverso"), ("36", "60", "Equipamento"), ("61", "85", "1 poção"), ("86", "100", "Superior (1 melhoria)")]
    },
    "4": {
        "dinheiro": [("01", "10", "—"), ("11", "50", "1d6x100 T$"), ("51", "80", "1d12x100 T$"), ("81", "90", "1 riqueza menor+%"), ("91", "100", "1d3 riquezas menores+%")],
        "itens": [("01", "20", "—"), ("21", "30", "Diverso"), ("31", "55", "Equipamento2D"), ("56", "80", "1 poção+%"), ("81", "100", "Superior (1 melhoria)2D")]
    },
    "5": {
        "dinheiro": [("01", "15", "—"), ("16", "65", "1d8x100 T$"), ("66", "95", "3d4x10 TO"), ("96", "100", "1 riqueza média")],
        "itens": [("01", "20", "—"), ("21", "70", "1 poção"), ("71", "90", "Superior (1 melhoria)"), ("91", "100", "Superior (2 melhorias)")]
    },
    "6": {
        "dinheiro": [("01", "15", "—"), ("16", "60", "2d6x100 T$"), ("61", "90", "2d10x100 T$"), ("91", "100", "1d3+1 riquezas menores")],
        "itens": [("01", "20", "—"), ("21", "65", "1 poção+%2D"), ("66", "95", "Superior (1 melhoria)2D"), ("96", "100", "Superior (2 melhorias)2D")]
    },
    "7": {
        "dinheiro": [("01", "10", "—"), ("11", "60", "2d8x100 T$"), ("61", "90", "2d12x10 TO"), ("91", "100", "1d4+1 riquezas menores")],
        "itens": [("01", "20", "—"), ("21", "60", "1d3 poções"), ("61", "90", "Superior (2 melhorias)"), ("91", "100", "Superior (3 melhorias)")]
    },
    "8": {
        "dinheiro": [("01", "10", "—"), ("11", "55", "2d10x100 T$"), ("56", "95", "1d4+1 riquezas menores"), ("96", "100", "1 riqueza média+%")],
        "itens": [("01", "20", "—"), ("21", "75", "1d3 poções"), ("76", "95", "Superior (2 melhorias)"), ("96", "100", "Superior (3 melhorias)2D")]
    },
    "9": {
        "dinheiro": [("01", "10", "—"), ("11", "35", "1 riqueza média"), ("36", "85", "4d6x100 T$"), ("86", "100", "1d3 riquezas médias")],
        "itens": [("01", "20", "—"), ("21", "70", "1 poção+%"), ("71", "95", "Superior (3 melhorias)"), ("96", "100", "Mágico (menor)")]
    },
    "10": {
        "dinheiro": [("01", "10", "—"), ("11", "30", "4d6x100 T$"), ("31", "85", "4d10x10 TO"), ("86", "100", "1d3+1 riquezas médias")],
        "itens": [("01", "50", "—"), ("51", "75", "1d3+1 poções"), ("76", "90", "Superior (3 melhorias)"), ("91", "100", "Mágico (menor)")]
    },
    "11": {
        "dinheiro": [("01", "10", "—"), ("11", "45", "2d4x1.000 T$"), ("46", "85", "1d3 riquezas médias"), ("86", "100", "2d6x100 TO")],
        "itens": [("01", "45", "—"), ("46", "70", "1d4+1 poções"), ("71", "90", "Superior (3 melhorias)"), ("91", "100", "Mágico (menor)2D")]
    },
    "12": {
        "dinheiro": [("01", "10", "—"), ("11", "45", "1 riqueza média+%"), ("46", "80", "2d6x1.000 T$"), ("81", "100", "1d4+1 riquezas médias")],
        "itens": [("01", "45", "—"), ("46", "70", "1d3+1 poções+%"), ("71", "85", "Superior (4 melhorias)"), ("86", "100", "Mágico (menor)")]
    },
    "13": {
        "dinheiro": [("01", "10", "—"), ("11", "45", "4d4x1.000 T$"), ("46", "80", "1d3+1 riquezas médias"), ("81", "100", "4d6x100 TO")],
        "itens": [("01", "40", "—"), ("41", "65", "1d4+1 poções+%"), ("66", "95", "Superior (4 melhorias)"), ("96", "100", "Mágico (médio)")]
    },
    "14": {
        "dinheiro": [("01", "10", "—"), ("11", "45", "1d3+1 riquezas médias"), ("46", "80", "3d6x1.000 T$"), ("81", "100", "1 riqueza maior")],
        "itens": [("01", "40", "—"), ("41", "65", "1d4+1 poções+%"), ("66", "90", "Superior (4 melhorias)"), ("91", "100", "Mágico (médio)")]
    },
    "15": {
        "dinheiro": [("01", "10", "—"), ("11", "45", "1 riqueza média+%"), ("46", "80", "2d10x1.000 T$"), ("81", "100", "1d4x1.000 TO")],
        "itens": [("01", "35", "—"), ("36", "45", "1d6+1 poções"), ("46", "85", "Superior (4 melhorias)2D"), ("86", "100", "Mágico (médio)")]
    },
    "16": {
        "dinheiro": [("01", "10", "—"), ("11", "40", "3d6x1.000 T$"), ("41", "75", "3d10x100 TO"), ("76", "100", "1d3 riquezas maiores")],
        "itens": [("01", "35", "—"), ("36", "45", "1d6+1 poções+%"), ("46", "80", "Superior (4 melhorias)2D"), ("81", "100", "Mágico (médio)")]
    },
    "17": {
        "dinheiro": [("01", "05", "—"), ("06", "40", "4d6x1.000 T$"), ("41", "75", "1d3 riquezas médias+%"), ("76", "100", "2d4x1.000 TO")],
        "itens": [("01", "20", "—"), ("21", "40", "Mágico (menor)"), ("41", "80", "Mágico (médio)"), ("81", "100", "Mágico (maior)")]
    },
    "18": {
        "dinheiro": [("01", "05", "—"), ("06", "40", "4d10x1.000 T$"), ("41", "75", "1 riqueza maior"), ("76", "100", "1d3+1 riquezas maiores")],
        "itens": [("01", "15", "—"), ("16", "40", "Mágico (menor)2D"), ("41", "70", "Mágico (médio)"), ("71", "100", "Mágico (maior)")]
    },
    "19": {
        "dinheiro": [("01", "05", "—"), ("06", "40", "4d12x1.000 T$"), ("41", "75", "1 riqueza maior+%"), ("76", "100", "1d12x1.000 TO")],
        "itens": [("01", "10", "—"), ("11", "40", "Mágico (menor)2D"), ("41", "60", "Mágico (médio)2D"), ("61", "100", "Mágico (maior)")]
    },
    "20": {
        "dinheiro": [("01", "05", "—"), ("06", "40", "2d4x1.000 TO"), ("41", "75", "1d3 riquezas maiores"), ("76", "100", "1d3+1 riquezas maiores+%")],
        "itens": [("01", "05", "—"), ("06", "40", "Mágico (menor)2D"), ("41", "50", "Mágico (médio)2D"), ("51", "100", "Mágico (maior)2D")]
    }
}

TABELA_8_1 = {}
for nd_key, tabelas_nd in _DADOS_BRUTOS_TABELA_8_1.items():
    TABELA_8_1[nd_key] = {}
    for tipo_tabela, entradas_brutas in tabelas_nd.items():
        TABELA_8_1[nd_key][tipo_tabela] = []
        for d_min_str, d_max_str, resultado_str in entradas_brutas:
            TABELA_8_1[nd_key][tipo_tabela].append({
                "d_min": int(d_min_str),
                "d_max": int(d_max_str),
                "resultado": _parse_resultado_string(resultado_str)
            })
