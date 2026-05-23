# Demo: LLM Local con Ollama

## Instalación Rápida

```bash
# 1. Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Descargar modelo (elige según tu RAM)
ollama pull llama3.2:3b    # 2GB  — recomendado
ollama pull mistral:7b     # 4GB  — más potente
ollama pull phi3:mini      # 2.3GB — eficiente

# 3. Demo completo
python demo_local.py

# 4. Solo un prompt específico
python demo_local.py --prompt "¿Cómo funciona la atención en un transformer?"

# 5. Modo interactivo
python demo_local.py --interactive

# 6. Demo de streaming
python demo_streaming.py
```

## Modelos Recomendados para el Curso

| Modelo | RAM requerida | Velocidad | Calidad |
|--------|--------------|-----------|---------|
| `llama3.2:3b` | 4 GB | ⚡⚡⚡ | ★★★☆ |
| `mistral:7b` | 6 GB | ⚡⚡ | ★★★★ |
| `llama3.1:8b` | 8 GB | ⚡⚡ | ★★★★ |
| `phi3:mini` | 4 GB | ⚡⚡⚡ | ★★★☆ |
