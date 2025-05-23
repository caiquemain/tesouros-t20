# app.py
from flask import Flask, render_template, request, redirect, url_for
import logging  # Para logs no servidor

# Importa a função principal do nosso core e a TABELA_8_1 para as chaves de ND
from core.tesouros import gerar_tesouro_completo_por_nd
# Usada para popular o dropdown de NDs
from tabelas.base.tabela_8_1_data import TABELA_8_1

app = Flask(__name__)
# Considere adicionar uma app.secret_key se for usar sessions no futuro
# app.secret_key = 'uma_chave_secreta_muito_forte_aqui!'

# Configuração básica de logging para o Flask
# Não configurar se já estiver em modo debug (que tem seu próprio logger)
if not app.debug:
    app.logger.setLevel(logging.INFO)
    # Poderia adicionar handlers para arquivos, etc., se necessário
    # Por enquanto, o output padrão do Flask (console) é suficiente.

# Obtém as chaves de ND válidas da Tabela 8-1 para o formulário
# Tenta uma ordenação que lide com frações e números
valid_nd_keys = list(TABELA_8_1.keys())
try:
    def nd_sort_key(nd_str_key):
        if '/' in nd_str_key:
            num, den = map(float, nd_str_key.split('/'))
            return num / den
        return float(nd_str_key)
    valid_nd_keys.sort(key=nd_sort_key)
except ValueError:
    valid_nd_keys.sort()  # Fallback para ordenação de string se a conversão falhar


@app.route('/')
def index():
    return redirect(url_for('rolar_tesouro_page'))


@app.route('/rolar', methods=['GET', 'POST'])
def rolar_tesouro_page():
    tesouro_resultado_completo = None
    mensagem_erro = None

    # Valores para repopular o formulário
    nd_selecionado_no_form = request.form.get('nd_chave') if request.method == 'POST' else (
        valid_nd_keys[0] if valid_nd_keys else None)
    tipo_tesouro_selecionado_no_form = request.form.get(
        'tipo_tesouro') if request.method == 'POST' else "Padrão"

    if request.method == 'POST':
        nd_chave_input = request.form.get('nd_chave')
        tipo_tesouro_input = request.form.get('tipo_tesouro')

        app.logger.info(
            f"Recebido request para /rolar: ND='{nd_chave_input}', Tipo='{tipo_tesouro_input}'")

        if not nd_chave_input:
            mensagem_erro = "Por favor, selecione um Nível de Desafio (ND)."
        elif nd_chave_input not in TABELA_8_1:  # Validação extra
            mensagem_erro = f"Nível de Desafio (ND) '{nd_chave_input}' é inválido."
        elif not tipo_tesouro_input:
            mensagem_erro = "Por favor, selecione o Tipo de Tesouro da criatura."
        else:
            try:
                # Atualiza os valores para repopular o formulário com a última submissão
                nd_selecionado_no_form = nd_chave_input
                tipo_tesouro_selecionado_no_form = tipo_tesouro_input

                app.logger.info(
                    f"Chamando gerar_tesouro_completo_por_nd(nd_chave_str='{nd_chave_input}', tipo_tesouro_modificador='{tipo_tesouro_input}')")
                tesouro_resultado_completo = gerar_tesouro_completo_por_nd(
                    nd_chave_input, tipo_tesouro_input)
                app.logger.info(
                    "Tesouro gerado com sucesso (estrutura preliminar):")
                # Para debug, pode ser útil logar partes do resultado, mas ele pode ser grande
                # app.logger.debug(tesouro_resultado_completo)

                if tesouro_resultado_completo and "erro" in tesouro_resultado_completo:
                    mensagem_erro = tesouro_resultado_completo["erro"]
                    app.logger.error(
                        f"Erro retornado pela lógica do tesouro: {mensagem_erro}")
                    # Limpa o resultado em caso de erro da lógica interna
                    tesouro_resultado_completo = None

            except ValueError as e:
                app.logger.error(
                    f"ValueError durante a geração de tesouro: {e}", exc_info=True)
                mensagem_erro = f"Erro de valor nos dados de entrada: {e}"
            except Exception as e:
                app.logger.error(
                    f"Exceção não esperada durante a geração de tesouro: {e}", exc_info=True)
                mensagem_erro = "Ocorreu um erro inesperado no servidor. Tente novamente mais tarde."

    return render_template(
        'rolar_tesouro.html',
        # Passa o dicionário completo do tesouro
        tesouro_data=tesouro_resultado_completo,
        erro=mensagem_erro,
        nd_keys_disponiveis=valid_nd_keys,  # Para o dropdown de NDs
        nd_selecionado=nd_selecionado_no_form,
        tipos_tesouro_disponiveis=["Padrão", "Metade",
                                   "Dobro", "Nenhum"],  # Para o dropdown de tipo
        tipo_tesouro_selecionado=tipo_tesouro_selecionado_no_form
    )


if __name__ == '__main__':
    # Configuração de logging para quando rodado com `python app.py`
    # Em produção com `flask run` via Docker, o logging do Flask pode ser configurado de outras formas.
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    # Para rodar com `python app.py` diretamente:
    # app.run(host='0.0.0.0', port=5000, debug=True)
    # Lembre-se que as variáveis de ambiente FLASK_DEBUG, FLASK_RUN_HOST, FLASK_RUN_PORT
    # são usadas pelo comando `flask run` (definido no Dockerfile).
    # Se não for usar `flask run`, descomente e ajuste a linha app.run() acima.
    pass
