# tabelas/base/tabela_8_5_data.py

ITENS_SUPERIORES_DATA = {
    "armas": [
        {"d_min": 1, "d_max": 10, "melhoria": "Atroz",
            "custo_melhorias": 2, "reroll_se_unica": True},
        {"d_min": 11, "d_max": 13, "melhoria": "Banhada a ouro"},
        {"d_min": 14, "d_max": 23, "melhoria": "Certeira"},
        {"d_min": 24, "d_max": 26, "melhoria": "Cravejada de gemas"},
        {"d_min": 27, "d_max": 36, "melhoria": "Cruel"},
        {"d_min": 37, "d_max": 39, "melhoria": "Discreta"},
        {"d_min": 40, "d_max": 44, "melhoria": "Equilibrada"},
        {"d_min": 45, "d_max": 48, "melhoria": "Harmonizada"},
        {"d_min": 49, "d_max": 53, "melhoria": "Injeção alquímica"},
        {"d_min": 54, "d_max": 55, "melhoria": "Macabra"},
        {"d_min": 56, "d_max": 65, "melhoria": "Maciça"},
        {"d_min": 66, "d_max": 75, "melhoria": "Material especial",
            "requer_rolagem_material": True},
        {"d_min": 76, "d_max": 80, "melhoria": "Mira telescópica"},
        {"d_min": 81, "d_max": 90, "melhoria": "Precisa"},
        {"d_min": 91, "d_max": 100, "melhoria": "Pungente",
            "custo_melhorias": 2, "reroll_se_unica": True}
    ],
    "armaduras_escudos": [
        {"d_min": 1, "d_max": 15, "melhoria": "Ajustada"},
        {"d_min": 16, "d_max": 19, "melhoria": "Banhada a ouro"},
        {"d_min": 20, "d_max": 23, "melhoria": "Cravejada de gemas"},
        {"d_min": 24, "d_max": 28, "melhoria": "Delicada"},
        {"d_min": 29, "d_max": 32, "melhoria": "Discreta"},
        # Para armaduras ou escudos
        {"d_min": 33, "d_max": 37, "melhoria": "Espinhos"},
        {"d_min": 38, "d_max": 40, "melhoria": "Macabra"},
        {"d_min": 41, "d_max": 50, "melhoria": "Material especial",
            "requer_rolagem_material": True},
        {"d_min": 51, "d_max": 55, "melhoria": "Polida"},
        {"d_min": 56, "d_max": 80, "melhoria": "Reforçada"},
        {"d_min": 81, "d_max": 90, "melhoria": "Selada"},
        {"d_min": 91, "d_max": 100, "melhoria": "Sob medida",
            "custo_melhorias": 2, "reroll_se_unica": True}
    ],
    "esotericos": [
        # Singular para concordar com "item esotérico"
        {"d_min": 1, "d_max": 4, "melhoria": "Banhado a ouro"},
        # Nota: "Canalizador" aparece duas vezes, 05-19 e 70-85. Isso está correto conforme a tabela.
        {"d_min": 5, "d_max": 19, "melhoria": "Canalizador"},
        {"d_min": 20, "d_max": 23, "melhoria": "Cravejado de gemas"},  # Singular
        {"d_min": 24, "d_max": 27, "melhoria": "Discreto"},
        {"d_min": 28, "d_max": 42, "melhoria": "Energético"},
        {"d_min": 43, "d_max": 57, "melhoria": "Harmonizado"},
        {"d_min": 58, "d_max": 60, "melhoria": "Macabro"},
        {"d_min": 61, "d_max": 69, "melhoria": "Material especial",
            "requer_rolagem_material": True},
        {"d_min": 70, "d_max": 85, "melhoria": "Canalizador"},  # Segunda aparição
        {"d_min": 86, "d_max": 100, "melhoria": "Vigilante"}
    ]
}

# Dados para a sub-rolagem de Material Especial (nota de rodapé 2 da Tabela 8-5)
MATERIAIS_ESPECIAIS = {
    1: "aço-rubi",
    2: "adamante",
    3: "gelo eterno",
    4: "madeira Tollon",
    5: "matéria vermelha",
    6: "mitral"
}
