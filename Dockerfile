# build container image (blueprint)
# get base python image (slim is smaller)
FROM python:3.13-slim

# /app workdir to keep container clean
WORKDIR /app

# install deps
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# copy app into container
COPY app/ .

# run
CMD ["python", "main.py"]
