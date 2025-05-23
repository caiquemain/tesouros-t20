from tabelas.base.tabela_8_1_data import TABELA_8_1
from core.tesouros import gerar_tesouro_completo_por_nd
from flask import Flask, render_template, request, url_for
import os  # Para garantir que os caminhos de importação funcionem corretamente

# Adiciona o diretório raiz ao sys.path para garantir que os módulos de 'core' e 'tabelas' sejam encontrados
# Isso é útil se você estiver executando o app de um subdiretório ou se a estrutura for mais complexa.
# Se 'core' e 'tabelas' já estiverem no PYTHONPATH ou no mesmo diretório, isso pode não ser estritamente necessário.
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importa a função principal de geração de tesouros do seu módulo 'core'

# Importa os dados da Tabela 8-1 para obter as chaves de ND disponíveis
# (Assumindo que o __init__.py nas pastas 'tabelas' e 'tabelas/base' permite esses imports)

app = Flask(__name__)
# Necessário para 'flash messages', embora não estejamos usando flash aqui, é uma boa prática.
app.secret_key = os.urandom(24)


def get_select_options():
    """
    Prepara os dados para os menus <select> no HTML.
    """
    # Obtém as chaves de ND da TABELA_8_1 e as ordena.
    # A ordenação tenta lidar com frações (ex: "1/4", "1/2") corretamente.
    nd_keys_raw = list(TABELA_8_1.keys())
    try:
        # Tenta ordenar numericamente, convertendo frações para float
        nd_keys_sorted = sorted(
            nd_keys_raw, key=lambda x: float(x.replace("/", ".")))
    except ValueError:
        # Fallback para ordenação alfabética se houver chaves não numéricas/fracionárias inesperadas
        nd_keys_sorted = sorted(nd_keys_raw)

    tipos_tesouro = ["Padrão", "Metade", "Dobro", "Nenhum"]
    return nd_keys_sorted, tipos_tesouro


# Definindo a rota principal como o rolador de tesouro
@app.route('/', methods=['GET', 'POST'])
def rolar_tesouro_page():
    """
    Rota principal para exibir a página de rolagem de tesouros e processar as solicitações.
    """
    nd_keys, tipos_tesouro = get_select_options()

    # Contexto inicial para o template
    contexto = {
        "nd_keys_disponiveis": nd_keys,
        "tipos_tesouro_disponiveis": tipos_tesouro,
        # Lista para armazenar os resultados de cada rolagem de tesouro
        "tesouros_processados": [],
        "erro": None  # Para mensagens de erro
    }

    if request.method == 'POST':
        try:
            # O JavaScript envia os dados como JSON
            if not request.is_json:
                contexto["erro"] = "Formato de requisição inválido. Esperado JSON."
                # Retorna o template com a mensagem de erro.
                # O JavaScript no HTML tentará atualizar a página com este conteúdo.
                # Bad Request
                return render_template('rolar_tesouro.html', **contexto), 400

            data = request.get_json()
            # 'solicitacoes_tesouro' é a chave usada no JS
            solicitacoes = data.get('solicitacoes_tesouro', [])

            if not solicitacoes:
                contexto["erro"] = "Nenhuma solicitação de tesouro recebida."
            else:
                todos_os_tesouros_gerados_para_template = []
                for i, solicitacao in enumerate(solicitacoes):
                    nd_chave = solicitacao.get('nd_chave')
                    try:
                        # Garante que a quantidade é um inteiro positivo
                        quantidade = int(solicitacao.get('quantidade', 1))
                        if quantidade < 1:
                            quantidade = 1  # Default para 1 se for inválido
                    except ValueError:
                        quantidade = 1  # Default para 1 se não for um número

                    tipo_tesouro_mod = solicitacao.get(
                        'tipo_tesouro', 'Padrão')

                    if not nd_chave or nd_chave not in nd_keys:
                        # Log de erro no servidor e informação para o usuário
                        app.logger.error(
                            f"ND inválido ou não fornecido na solicitação #{i+1}: {nd_chave}")
                        # Adiciona um resultado de erro placeholder para esta solicitação específica
                        todos_os_tesouros_gerados_para_template.append({
                            "nd_processado": nd_chave or "Desconhecido",
                            "modificador_tesouro": tipo_tesouro_mod,
                            "sumario": f"Erro: ND '{nd_chave}' inválido ou não encontrado.",
                            "moedas_e_riquezas": [],
                            "itens_encontrados": [],
                            "log_completo_rolagens": [f"Solicitação #{i+1}: ND '{nd_chave}' é inválido ou não foi encontrado nas opções disponíveis."]
                        })
                        continue  # Pula para a próxima solicitação

                    # Chama a função de gerar tesouro para cada unidade da quantidade
                    for j in range(quantidade):
                        app.logger.info(
                            f"Processando solicitação #{i+1}, Tesouro #{j+1}: ND={nd_chave}, Mod={tipo_tesouro_mod}")
                        # Cada chamada a gerar_tesouro_completo_por_nd retorna um dicionário completo
                        # que o template 'rolar_tesouro.html' espera em 'tesouros_processados'
                        tesouro_individual_gerado = gerar_tesouro_completo_por_nd(
                            nd_chave, tipo_tesouro_mod)

                        # Adiciona um identificador para o log, se útil
                        if "log_completo_rolagens" in tesouro_individual_gerado:
                            tesouro_individual_gerado["log_completo_rolagens"].insert(
                                0, f"--- Tesouro para ND {nd_chave} (Rolagem {j+1}/{quantidade} da Solicitação #{i+1}) ---")

                        todos_os_tesouros_gerados_para_template.append(
                            tesouro_individual_gerado)

                contexto["tesouros_processados"] = todos_os_tesouros_gerados_para_template

            # Retorna o template renderizado com os resultados (ou erros de validação)
            # O JavaScript no lado do cliente irá usar este HTML para atualizar a página.
            return render_template('rolar_tesouro.html', **contexto)

        except Exception as e:
            # Log detalhado do erro no servidor
            app.logger.error(
                f"Erro crítico ao processar tesouros: {e}", exc_info=True)
            contexto["erro"] = f"Ocorreu um erro interno grave no servidor ao processar sua solicitação."
            # Em caso de erro grave, ainda retorna o template para o JS atualizar a UI com a mensagem.
            # Internal Server Error
            return render_template('rolar_tesouro.html', **contexto), 500

    # Para requisições GET, apenas renderiza a página com as opções iniciais
    return render_template('rolar_tesouro.html', **contexto)


if __name__ == '__main__':
    # Configura um logger básico para debug
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s')
    # app.run(debug=True) # debug=True é ótimo para desenvolvimento
    # Para produção, use um servidor WSGI como Gunicorn ou Waitress.
    # Exemplo: app.run(host='0.0.0.0', port=5000, debug=False)
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
