# ===============================================================================
# API CAEPI - Certificados de Aprovação
# Dockerfile Multi-Stage para Desenvolvimento e Produção
# ===============================================================================

# -------------------------------------------------------------------------------
# ESTÁGIO BASE: Configurações comuns para dev e prod
# -------------------------------------------------------------------------------
FROM python:3.12.7-alpine AS base

# Labels para metadados da imagem
LABEL maintainer="deyvidspindola" \
      description="API CAEPI - Certificados de Aprovação" \
      version="1.0.0"

# Variáveis de ambiente para otimizar Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências de sistema necessárias
# curl é necessário para health checks
RUN apk add --no-cache curl

# -------------------------------------------------------------------------------
# ESTÁGIO BUILDER: Instala dependências Python
# -------------------------------------------------------------------------------
FROM base AS builder

# Dependências temporárias para compilação de pacotes Python
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libffi-dev \
    python3-dev \
    build-base \
    linux-headers \
    openssl-dev

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --user --no-warn-script-location -r requirements.txt

# -------------------------------------------------------------------------------
# ESTÁGIO DESENVOLVIMENTO: Para debug e hot-reload
# -------------------------------------------------------------------------------
FROM base AS development

# Copiar dependências Python do builder
COPY --from=builder /root/.local /root/.local

# Adicionar binários Python ao PATH
ENV PATH=/root/.local/bin:$PATH

# Expor portas para aplicação e debugger
EXPOSE 8000 5681

# Volume para hot-reload (será mapeado no docker-compose)
VOLUME ["/app"]

# Comando para desenvolvimento com debugpy
CMD ["python", "-Xfrozen_modules=off", "-m", "debugpy", "--listen", "0.0.0.0:5681", "--wait-for-client", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# -------------------------------------------------------------------------------
# ESTÁGIO PRODUÇÃO: Imagem otimizada e segura
# -------------------------------------------------------------------------------
FROM base AS production

# Criar usuário não-root para segurança
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Copiar dependências Python do builder para o usuário app
COPY --from=builder /root/.local /home/appuser/.local

# Copiar código da aplicação com ownership correto
COPY --chown=appuser:appgroup . .

# Configurar PATH para o usuário
ENV PATH=/home/appuser/.local/bin:$PATH

# Mudar para usuário não-root
USER appuser

# Expor apenas a porta da aplicação
EXPOSE 8000

# Health check para monitoramento
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para produção com Gunicorn
CMD ["gunicorn", "main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]