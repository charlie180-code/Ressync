FROM python:3.9-slim

WORKDIR /user/apps

RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libgirepository1.0-dev \
    gobject-introspection \
    gir1.2-pango-1.0 \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/common.txt ./requirements/common.txt
RUN pip install --no-cache-dir -r requirements/common.txt

RUN pip install gunicorn

COPY . .

EXPOSE 5001

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "run:app"]
