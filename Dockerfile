FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/mpl

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY tests/data/weather_oldenburg_2020.csv ./data/demo_weather.csv

RUN useradd --create-home app \
    && mkdir -p /app/outputs \
    && chown -R app /app/outputs
USER app

ENTRYPOINT ["pvyield"]
CMD ["--lat", "53.14", "--lon", "8.21", \
     "--weather-csv", "/app/data/demo_weather.csv", "--out", "/app/outputs"]