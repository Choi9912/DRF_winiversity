# Python 3.12 이미지를 기반으로 합니다
FROM python:3.12

# 작업 디렉토리를 설정합니다
WORKDIR /app

# 환경 변수를 설정합니다
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 시스템 의존성을 설치합니다
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN pip install poetry

# Poetry 설정: 가상 환경 생성하지 않음
RUN poetry config virtualenvs.create false

# 프로젝트 의존성 파일을 복사합니다
COPY pyproject.toml poetry.lock* ./

# Poetry를 사용하여 의존성 설치
RUN poetry install --no-root

# 프로젝트 파일을 복사합니다
COPY . .

# Django 서버를 실행합니다
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]