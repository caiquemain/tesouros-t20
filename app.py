import os
import sys
import logging  # Adicionado para logging mais robusto
# jsonify não está sendo usado, mas pode ser útil no futuro
from flask import Flask, render_template, request, jsonify

# Adiciona o diretório raiz ao sys.path para garantir que os módulos sejam encontrados
# Útil especialmente se a estrutura do projeto for complexa ou o app for executado de um subdiretório.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from core.tesouros import gerar_tesouro_completo_por_nd
    from tabelas.base.tabela_8_1_data import TABELA_8_1
except ImportError as e:
    # Log inicial se houver problemas com os imports customizados
    # Configura logging básico se ainda não estiver
    logging.basicConfig(level=logging.ERROR)
    logging.error(
        f"Falha ao importar módulos customizados (core/tabelas): {e}")
    logging.error(
        "Verifique se os arquivos __init__.py existem nas pastas 'core' e 'tabelas/base',")
    logging.error(
        "e se o PYTHONPATH está configurado corretamente ou se app.py está na raiz do projeto.")
    # Você pode querer que a aplicação pare aqui se os módulos principais não puderem ser carregados.
    # raise # Descomente para parar a execução se os imports falharem.

app = Flask(__name__)

# Chave secreta para funcionalidades que usam sessão (boa prática, mesmo que não usemos flash messages agora)
# Para produção real, isso viria de uma variável de ambiente.
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))

# Configuração de Logging
# Se não estiver rodando via 'python app.py', o Flask pode não configurar o logger da mesma forma.
# Garantir que app.logger esteja utilizável. Gunicorn também lida com logs.
if not app.debug:  # Configura um handler mais robusto se não estiver em modo debug explícito do Flask
    if not app.logger.handlers:  # Evita adicionar handlers duplicados
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)


def get_select_options():
    """
    Prepara os dados para os menus <select> no HTML.
    """
    nd_keys_disponiveis_ordenados = []
    tipos_tesouro_disponiveis = ["Padrão", "Metade", "Dobro", "Nenhum"]

    try:
        nd_keys_raw = list(TABELA_8_1.keys())
        # Tenta ordenar numericamente, convertendo frações para float
        nd_keys_disponiveis_ordenados = sorted(
            nd_keys_raw, key=lambda x: float(x.replace("/", ".")))
    except NameError:  # Caso TABELA_8_1 não tenha sido importada
        app.logger.error(
            "ERRO: TABELA_8_1 não definida. Verifique o import de tabelas.base.tabela_8_1_data.")
    except Exception as e:
        app.logger.error(
            f"Erro ao processar chaves de ND para get_select_options: {e}")
        # Fallback para lista vazia se houver erro na ordenação ou acesso
        nd_keys_disponiveis_ordenados = []

    return nd_keys_disponiveis_ordenados, tipos_tesouro_disponiveis


@app.route('/', methods=['GET', 'POST'])
def rolar_tesouro_page():
    """
    Rota principal para exibir a página de rolagem de tesouros e processar as solicitações.
    """
    nd_keys, tipos_tesouro = get_select_options()

    contexto = {
        "nd_keys_disponiveis": nd_keys,
        "tipos_tesouro_disponiveis": tipos_tesouro,
        "tesouros_processados": [],
        "erro": None
    }

    if request.method == 'POST':
        app.logger.info(f"Requisição POST recebida em {request.path}")
        try:
            if not request.is_json:
                app.logger.warning("Requisição POST não é JSON.")
                contexto["erro"] = "Formato de requisição inválido. Esperado JSON."
                return render_template('rolar_tesouro.html', **contexto), 400

            data = request.get_json()
            app.logger.debug(f"Dados JSON recebidos: {data}")
            solicitacoes = data.get('solicitacoes_tesouro', [])

            if not solicitacoes:
                app.logger.info(
                    "Nenhuma solicitação de tesouro na requisição POST.")
                contexto["erro"] = "Nenhuma solicitação de tesouro recebida."
            else:
                todos_os_tesouros_gerados = []
                for i, solicitacao in enumerate(solicitacoes):
                    nd_chave = solicitacao.get('nd_chave')
                    quantidade_str = solicitacao.get('quantidade', '1')
                    tipo_tesouro_mod = solicitacao.get(
                        'tipo_tesouro', 'Padrão')

                    try:
                        quantidade = int(quantidade_str)
                        if quantidade < 1:
                            app.logger.warning(
                                f"Quantidade inválida '{quantidade_str}' na solicitação #{i+1}. Usando 1.")
                            quantidade = 1
                    except ValueError:
                        app.logger.warning(
                            f"Valor de quantidade não numérico '{quantidade_str}' na solicitação #{i+1}. Usando 1.")
                        quantidade = 1

                    if not nd_chave or nd_chave not in nd_keys:
                        app.logger.error(
                            f"ND inválido ('{nd_chave}') ou não fornecido na solicitação #{i+1}.")
                        # Adiciona um item de erro ao resultado para o usuário ver
                        erro_item = {
                            "nd_processado": nd_chave or "Desconhecido",
                            "modificador_tesouro": tipo_tesouro_mod,
                            "sumario": f"Erro: ND '{nd_chave}' é inválido ou não foi encontrado.",
                            "moedas_e_riquezas": [], "itens_encontrados": [],
                            "log_completo_rolagens": [f"Solicitação #{i+1}: ND '{nd_chave}' inválido."]
                        }
                        todos_os_tesouros_gerados.append(erro_item)
                        continue

                    app.logger.info(
                        f"Processando solicitação #{i+1}: {quantidade}x ND '{nd_chave}', Tipo: '{tipo_tesouro_mod}'")
                    for j in range(quantidade):
                        tesouro_individual = gerar_tesouro_completo_por_nd(
                            nd_chave, tipo_tesouro_mod)
                        if "log_completo_rolagens" in tesouro_individual and isinstance(tesouro_individual["log_completo_rolagens"], list):
                            tesouro_individual["log_completo_rolagens"].insert(
                                0, f"--- Tesouro para ND {nd_chave} (Rolagem {j+1}/{quantidade} da Solicitação #{i+1}) ---")
                        else:  # Garante que a chave existe para evitar erros no template se a função core não retornar
                            tesouro_individual["log_completo_rolagens"] = [
                                f"--- Tesouro para ND {nd_chave} (Rolagem {j+1}/{quantidade} da Solicitação #{i+1}) ---", "Log detalhado não disponível."]

                        todos_os_tesouros_gerados.append(tesouro_individual)

                contexto["tesouros_processados"] = todos_os_tesouros_gerados

            app.logger.info(
                f"Renderizando template com {len(contexto.get('tesouros_processados', []))} pacotes de tesouro.")
            return render_template('rolar_tesouro.html', **contexto)

        except Exception as e:
            app.logger.error(
                f"Erro crítico ao processar POST para / : {e}", exc_info=True)
            contexto["erro"] = "Ocorreu um erro interno grave no servidor ao processar sua solicitação."
            return render_template('rolar_tesouro.html', **contexto), 500

    # Para requisições GET
    app.logger.info(
        f"Requisição GET recebida em {request.path}. Renderizando página inicial.")
    return render_template('rolar_tesouro.html', **contexto)


if __name__ == '__main__':
    # Configura o logging básico para quando rodamos com 'python app.py'
    # Para produção com Gunicorn, o Gunicorn geralmente lida com a configuração do logger.
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s %(levelname)s: %(module)s: %(message)s')

    # Obtém configurações de ambiente ou usa padrões seguros para desenvolvimento
    # Padrão para localhost para desenvolvimento direto
    host = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")
    try:
        port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    except ValueError:
        port = 5000
    # Debug mode deve ser False em produção. Use variável de ambiente para controlar.
    # FLASK_DEBUG=1 ou FLASK_DEBUG=True para ligar.
    debug_mode = os.environ.get("FLASK_DEBUG", "1").lower() in [
        "true", "1", "t"]

    app.logger.info(
        f"Iniciando servidor de desenvolvimento Flask em http://{host}:{port}/ com debug={debug_mode}")
    app.run(host=host, port=port, debug=debug_mode)
