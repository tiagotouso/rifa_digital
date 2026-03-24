# Usa a imagem oficial e mais leve do Python 3.13
FROM python:3.13-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Define as variáveis de ambiente necessárias para o Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8599

# Copia e instala as dependências
COPY pyproject.toml .
RUN pip install flask>=3.1.3
RUN pip install gunicorn>=21.2.0

# Copia o restante dos arquivos do projeto
COPY . .

# Expõe a porta 8599 usada pelo Gunicorn
EXPOSE 8599

# Comando para rodar a aplicação em produção utilizando o Gunicorn (servidor mais rápido e seguro)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8599", "app:app"]
