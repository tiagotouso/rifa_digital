# Usa uma imagem leve do Python
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos (exceto a pasta data, que será mapeada)
COPY . .

# Expõe a porta padrão do Streamlit
EXPOSE 8599

# Comando para rodar o app
CMD ["streamlit", "run", "app.py", "--server.port=8599", "--server.baseUrlPath=/rifa"]