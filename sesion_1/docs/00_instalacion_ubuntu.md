# Guía de instalación · Ubuntu 24.04 LTS (o superior)

Tiempo estimado: 30–40 minutos (la mayor parte es la descarga de modelos).
**Hágalo antes de la Sesión 1.** Si usa Windows, instale primero **WSL2 con Ubuntu 24.04**
(`wsl --install -d Ubuntu-24.04` en PowerShell como administrador) y siga esta guía dentro de Ubuntu.

## Requisitos de hardware

| Recurso | Mínimo | Recomendado |
|---|---|---|
| RAM | 8 GB | 16 GB |
| Disco libre | 10 GB | 20 GB |
| GPU | No es obligatoria | NVIDIA con 6 GB+ de VRAM acelera ~5–10× |

> ¿Equipo muy limitado? Use el **Ollama simulado** (`make simulado`) para recorrer la interfaz y los
> scripts, y ejecute las partes que requieren un modelo real en el equipo de un compañero o en la nube.

---

## 1 · Paquetes base y Python 3.12

Ubuntu 24.04 ya trae Python 3.12 como `python3`.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.12 python3.12-venv python3-pip git curl build-essential make
python3.12 --version        # Python 3.12.x
```

## 2 · Node.js 22 LTS (para React 18 + Vite 6)

```bash
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install 22
node --version              # v22.x
npm --version
```

## 3 · Ollama (ejecución local de LLM)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
systemctl status ollama     # el instalador lo deja corriendo como servicio en :11434
```

Si no quedó como servicio (p. ej. en WSL2 sin systemd), ejecútelo en una terminal aparte:

```bash
ollama serve
```

### Descargar los modelos del curso

```bash
ollama pull llama3.2:3b         # ~2.0 GB · decoder-only · modelo principal del curso
ollama pull llama3.2:1b         # ~1.3 GB · decoder-only · para comparar tamaños
ollama pull nomic-embed-text    # ~0.3 GB · encoder · embeddings (Sesión 2)
ollama list
```

### Primera prueba

```bash
ollama run llama3.2:3b "Explica en una frase qué es un LLM"
```

Y la misma prueba **vía API REST** (así la consumirá nuestra aplicación):

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2:3b",
  "messages": [{"role": "user", "content": "Hola, ¿quién eres?"}],
  "stream": false
}'
```

### Comandos útiles de Ollama

| Comando | Para qué sirve |
|---|---|
| `ollama list` | Modelos descargados |
| `ollama ps` | Modelos cargados en memoria ahora mismo (y si usan CPU o GPU) |
| `ollama show llama3.2:3b` | Arquitectura, parámetros, ventana de contexto, cuantización, licencia |
| `ollama run <modelo>` | Chat interactivo en la terminal (`/bye` para salir) |
| `ollama rm <modelo>` | Liberar disco |
| `OLLAMA_HOST=0.0.0.0 ollama serve` | Exponer la API en la red local (¡cuidado: sin autenticación!) |

> Ollama también expone una API **compatible con OpenAI** en `http://localhost:11434/v1`.
> Lo usaremos en la Sesión 2 para demostrar portabilidad entre proveedores.

## 4 · Clonar el repositorio e instalar

```bash
git clone <URL-DEL-REPOSITORIO> fundamentos-arquitectura-llm
cd fundamentos-arquitectura-llm
make setup                  # crea .venv, instala backend y frontend, copia backend/.env
make test                   # las pruebas deben pasar (no requieren Ollama)
```

## 5 · Ejecutar el laboratorio

Terminal 1:
```bash
make backend                # http://localhost:8000/docs  (Swagger)
```
Terminal 2:
```bash
make frontend               # http://localhost:5173
```

El indicador verde **"Ollama · N modelos"** en la esquina superior derecha confirma que todo está conectado.

### Alternativa con Docker

```bash
# Instalar Docker Engine: https://docs.docker.com/engine/install/ubuntu/
docker compose up -d --build
docker compose exec ollama ollama pull llama3.2:3b
docker compose exec ollama ollama pull nomic-embed-text
# Abrir http://localhost:8080
```

## 6 · Google Cloud CLI (para el laboratorio de Agent Platform)

```bash
sudo apt install -y apt-transport-https ca-certificates gnupg
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
  | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt update && sudo apt install -y google-cloud-cli
gcloud init
gcloud auth application-default login
```

---

## Solución de problemas

| Síntoma | Solución |
|---|---|
| `Error: could not connect to ollama app` | `ollama serve` en otra terminal, o `sudo systemctl restart ollama` |
| La respuesta tarda más de 1 minuto | Está en CPU: use `llama3.2:1b`, cierre aplicaciones, o reduzca *max tokens* |
| `model 'llama3.2:3b' not found` | `ollama pull llama3.2:3b` |
| El frontend muestra "Backend apagado" | Verifique `make backend` y que el puerto 8000 esté libre (`ss -ltnp | grep 8000`) |
| El tokenizador dice `method: heuristic` | `tiktoken` necesita internet la primera vez para descargar su vocabulario |
| En WSL2 el frontend no abre | Use `http://localhost:5173` desde Windows; WSL2 reenvía el puerto automáticamente |
