# Usa a imagem oficial e mais leve do Python 3.13
FROM python:3.13-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Impede que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala as dependências de sistema (caso precise de algo para o SQLite ou pacotes futuros)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de dependências primeiro (otimiza o cache do Docker)
COPY pyproject.toml . 
# Se você tiver um requirements.txt, use: COPY requirements.txt .

# Instala o Flask, Gunicorn e o que mais estiver no projeto
RUN pip install --no-cache-dir gunicorn flask>=3.1.3

# Copia o restante dos arquivos do projeto
COPY . .

# Cria a pasta data para o SQLite (importante para persistência)
RUN mkdir -p /app/data

# Expõe a porta 8599
EXPOSE 8599

# Comando para rodar com Gunicorn (4 workers para melhor performance)
CMD ["gunicorn", "--bind", "0.0.0.0:8599", "--workers", "4", "app:app"]