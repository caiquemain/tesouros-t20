# Use uma imagem Python oficial como base
FROM python:3.11-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Define variáveis de ambiente para Python não bufferizar stdout/stderr e não escrever pyc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala dependências do sistema se necessário (geralmente não para Flask básico)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Copia o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação para o diretório de trabalho
COPY . .

# O Netlify define a variável de ambiente PORT. Gunicorn deve escutar nela.
# Não precisamos definir EXPOSE ou PORT aqui, pois o Netlify gerencia isso.
# O Gunicorn irá escutar em 0.0.0.0 por padrão, o que é bom.
# A variável $PORT será injetada pelo Netlify no ambiente de execução.
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]