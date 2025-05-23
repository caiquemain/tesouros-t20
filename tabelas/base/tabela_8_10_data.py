# tabelas/base/tabela_8_10_data.py

ARMADURAS_ESCUDOS_MAGICOS_ENCANTOS_DATA = [
    {"d_min": 1, "d_max": 6, "encanto": "Abascanto",
        "efeito": "Resistência contra magia"},
    {"d_min": 7, "d_max": 10, "encanto": "Abençoado",
        "efeito": "Resistência contra trevas"},
    {"d_min": 11, "d_max": 12, "encanto": "Acrobático",
        "efeito": "Bônus em Acrobacia"},  # Para armaduras
    {"d_min": 13, "d_max": 14, "encanto": "Alado",
        "efeito": "Deslocamento de voo 12m"},  # Para armaduras
    {"d_min": 15, "d_max": 16, "encanto": "Animado",
        "efeito": "Escudo defende sozinho", "apenas_escudos": True},
    {"d_min": 17, "d_max": 18, "encanto": "Assustador",
        "efeito": "Causa efeito de medo"},
    {"d_min": 19, "d_max": 22, "encanto": "Cáustica",
        "efeito": "Resistência contra ácido"},  # Nome da propriedade, não do item
    # Bônus de Defesa para armadura/escudo
    {"d_min": 23, "d_max": 32, "encanto": "Defensor", "efeito": "Defesa +2"},
    {"d_min": 33, "d_max": 34, "encanto": "Escorregadio",
        "efeito": "Bônus para escapar"},  # Para armaduras
    {"d_min": 35, "d_max": 36, "encanto": "Esmagador",
        "efeito": "Escudo causa mais dano", "apenas_escudos": True},
    {"d_min": 37, "d_max": 38, "encanto": "Fantasmagórico",
        "efeito": "Lança Manto de Sombras"},
    {"d_min": 39, "d_max": 40, "encanto": "Fortificado",
        "efeito": "Chance de ignorar crítico"},
    {"d_min": 41, "d_max": 44, "encanto": "Gélido",
        "efeito": "Resistência contra frio"},  # Nome da propriedade
    {"d_min": 45, "d_max": 54, "encanto": "Guardião", "efeito": "Defesa +4",
        "custo_encantos": 2, "reroll_se_menor": True},
    {"d_min": 55, "d_max": 56, "encanto": "Hipnótico", "efeito": "Fascina inimigos"},
    {"d_min": 57, "d_max": 58, "encanto": "Ilusório",
        "efeito": "Camufla-se como item comum"},
    {"d_min": 59, "d_max": 62, "encanto": "Incandescente",
        "efeito": "Resistência contra fogo"},  # Nome da propriedade
    {"d_min": 63, "d_max": 68, "encanto": "Invulnerável", "efeito": "Redução de dano"},
    {"d_min": 69, "d_max": 72, "encanto": "Opaco",
        "efeito": "Redução de energia"},  # Nome da propriedade
    {"d_min": 73, "d_max": 78, "encanto": "Protetor",
        "efeito": "Resistência +2"},  # Bônus em testes de Resistência
    {"d_min": 79, "d_max": 80, "encanto": "Refletor",
        "efeito": "Reflete magia"},  # Para escudos geralmente
    {"d_min": 81, "d_max": 84, "encanto": "Relampejante",
        "efeito": "Resistência contra eletricidade"},  # Nome da propriedade
    {"d_min": 85, "d_max": 86, "encanto": "Reluzente",
        "efeito": "Causa efeito de cegueira"},
    {"d_min": 87, "d_max": 88, "encanto": "Sombrio",
        "efeito": "Bônus em Furtividade"},  # Para armaduras
    {"d_min": 89, "d_max": 90, "encanto": "Zeloso",
        "efeito": "Atrai ataques em aliados"},  # Para escudos geralmente
    {"d_min": 91, "d_max": 100, "encanto": "Item específico",
        "efeito": "Veja a Tabela 8-11", "referencia_tabela": "8-11"}
]
