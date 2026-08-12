FROM python:3.12-slim
RUN groupadd -r pavelgroup && useradd -r -g pavelgroup pavel

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/tmp

RUN pip install --upgrade pip
WORKDIR /app/www/breakfast_lecture_planner
RUN mkdir -p staticfiles && chown -R pavel:pavelgroup /app/www/breakfast_lecture_planner

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chown -R pavel:pavelgroup /app/www/breakfast_lecture_planner/media/
RUN chmod -R 755 /app/www/breakfast_lecture_planner/media/
USER pavel
