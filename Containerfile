FROM python:slim
LABEL maintainer="Francesco Zanti"

# Imposto la direcotry di lavoro
WORKDIR /app

# Copio il file requirements.txt nella directory di lavoro
COPY requirements.txt .

# Installo le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copio il contenuto della directory locale nella directory di lavoro
COPY . .

# Avvio l'applicativo
CMD [ "python", "./main.py" ]