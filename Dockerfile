# Usa uma imagem base Python oficial leve com a versão mais recente
FROM python:3.13-slim-bookworm

# Define variáveis de ambiente para o Python e Flask
# Evita a criação de arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Garante que o output do Python não seja bufferizado (útil para logs em contêineres)
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV FLASK_DEBUG=1 

# Define o diretório de trabalho dentro do contêiner.
WORKDIR /app

# Copia primeiro o requirements.txt para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo o restante do código do seu projeto para /app
COPY . .

# Expõe a porta que o Flask estará rodando
EXPOSE 5000

# Define o comando padrão para iniciar a aplicação Flask
CMD ["flask", "run"]