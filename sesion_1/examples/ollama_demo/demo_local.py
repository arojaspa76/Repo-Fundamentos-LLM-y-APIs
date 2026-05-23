"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fundamentos de Arquitectura LLM — Sesión 1
Tema 1 & 2: Demo LLM Local con Ollama

Propósito:
  Demostrar cómo ejecutar un LLM completamente en local,
  sin enviar datos a proveedores externos. Ideal para
  entornos regulados (salud, finanzas, gobierno LATAM).

Prerrequisitos:
  1. Instalar Ollama: https://ollama.ai/download
  2. Descargar modelo: ollama pull llama3.2:3b
  3. pip install ollama rich

Uso:
  python demo_local.py
  python demo_local.py --model mistral:7b
  python demo_local.py --prompt "Explica RAG en 2 oraciones"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import argparse
import time
import sys
import ollama
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich import print as rprint

console = Console()

# ── Configuración por defecto ──────────────────────────────
DEFAULT_MODEL = "llama3.2:3b"
SYSTEM_PROMPT = """Eres un asistente especializado en tecnología AI/LLM para 
empresas en América Latina. Respondes en español, de forma clara y concisa, 
con ejemplos relevantes para el contexto LATAM cuando sea posible."""

# ── Prompts de demostración ────────────────────────────────
DEMO_PROMPTS = [
    {
        "title": "📚 Concepto Fundamental",
        "prompt": "¿Qué es un Large Language Model (LLM) en términos simples?",
        "topic": "Tema 1"
    },
    {
        "title": "🏗️ Arquitecturas",
        "prompt": "Explica la diferencia entre modelos encoder-only, decoder-only y encoder-decoder. Da un ejemplo de cada uno.",
        "topic": "Tema 2"
    },
    {
        "title": "🌎 Caso de Uso LATAM",
        "prompt": "¿Cómo podría un banco colombiano usar un LLM para mejorar la detección de fraude?",
        "topic": "Tema 2"
    },
    {
        "title": "💰 Análisis de Costos",
        "prompt": "¿Cuáles son las principales ventajas económicas de ejecutar un LLM local vs usar una API en la nube?",
        "topic": "Tema 3"
    },
]


def check_ollama_running() -> bool:
    """Verifica que el servidor Ollama esté activo."""
    try:
        ollama.list()
        return True
    except Exception:
        return False


def get_available_models() -> list[str]:
    """Retorna la lista de modelos descargados."""
    try:
        response = ollama.list()
        return [m.model for m in response.models]
    except Exception:
        return []


def show_model_info(model: str) -> None:
    """Muestra información del modelo seleccionado."""
    table = Table(title=f"🤖 Modelo: {model}", show_header=False, border_style="cyan")
    table.add_column("Campo", style="cyan bold", width=20)
    table.add_column("Valor", style="white")
    
    try:
        info = ollama.show(model)
        # Extraer parámetros básicos del modelfile
        modelfile = info.modelfile if hasattr(info, 'modelfile') else ""
        params_line = [l for l in modelfile.split('\n') if 'PARAMETER' in l]
        
        table.add_row("Modelo", model)
        table.add_row("Ejecución", "💻 100% Local — Sin envío de datos a la nube")
        table.add_row("Privacidad", "✅ Datos permanecen en tu máquina")
        table.add_row("Costo por token", "💰 $0.00 (solo electricidad)")
        if params_line:
            table.add_row("Parámetros", "\n".join(params_line[:3]))
    except Exception:
        table.add_row("Modelo", model)
        table.add_row("Estado", "Información no disponible")
    
    console.print(table)


def chat_with_model(model: str, prompt: str, title: str = "") -> dict:
    """
    Envía un mensaje al modelo y retorna la respuesta con métricas.
    
    Args:
        model: Nombre del modelo Ollama
        prompt: Pregunta o instrucción
        title: Título descriptivo para la demo
    
    Returns:
        dict con response, tokens_used, elapsed_time
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    start_time = time.time()
    
    response = ollama.chat(
        model=model,
        messages=messages,
        options={
            "temperature": 0.7,       # Creatividad (0=determinista, 1=creativo)
            "num_predict": 512,        # Máximo tokens a generar
            "top_k": 40,              # Top-K sampling
            "top_p": 0.9,             # Nucleus sampling
        }
    )
    
    elapsed = time.time() - start_time
    
    return {
        "content": response.message.content,
        "prompt_tokens": response.prompt_eval_count or 0,
        "completion_tokens": response.eval_count or 0,
        "elapsed_seconds": round(elapsed, 2),
        "tokens_per_second": round(
            (response.eval_count or 1) / elapsed, 1
        )
    }


def display_response(result: dict, title: str, prompt: str) -> None:
    """Muestra la respuesta con formato rico."""
    # Panel con la pregunta
    console.print(Panel(
        f"[yellow]{prompt}[/yellow]",
        title=f"[bold cyan]💬 Pregunta — {title}[/bold cyan]",
        border_style="cyan"
    ))
    
    # Respuesta en Markdown
    console.print(Panel(
        Markdown(result["content"]),
        title="[bold green]🤖 Respuesta del Modelo[/bold green]",
        border_style="green"
    ))
    
    # Métricas de performance
    metrics = Table(show_header=False, box=None, padding=(0, 2))
    metrics.add_column("Métrica", style="dim")
    metrics.add_column("Valor", style="bold yellow")
    
    metrics.add_row("⏱  Tiempo de respuesta", f"{result['elapsed_seconds']}s")
    metrics.add_row("📊 Tokens del prompt", str(result['prompt_tokens']))
    metrics.add_row("📝 Tokens generados", str(result['completion_tokens']))
    metrics.add_row("⚡ Velocidad", f"{result['tokens_per_second']} tokens/seg")
    metrics.add_row("💰 Costo", "$0.00 (modelo local)")
    
    console.print(metrics)
    console.rule(style="dim")


def run_full_demo(model: str) -> None:
    """Ejecuta la demo completa con todos los prompts."""
    console.print(Panel.fit(
        "[bold cyan]🧠 Fundamentos de Arquitectura LLM[/bold cyan]\n"
        "[white]Sesión 1 — Demo: LLM Local con Ollama[/white]\n\n"
        "[dim]Esta demo ejecuta un LLM completamente en tu máquina,\n"
        "sin conexión a internet ni envío de datos a terceros.[/dim]",
        border_style="cyan"
    ))
    
    show_model_info(model)
    console.print()
    
    for i, demo in enumerate(DEMO_PROMPTS, 1):
        console.print(f"\n[bold white]Demo {i}/{len(DEMO_PROMPTS)} — {demo['topic']}[/bold white]")
        
        with console.status(f"[cyan]🔄 Procesando con {model}...[/cyan]"):
            try:
                result = chat_with_model(model, demo["prompt"], demo["title"])
            except Exception as e:
                console.print(f"[red]❌ Error: {e}[/red]")
                continue
        
        display_response(result, demo["title"], demo["prompt"])
    
    console.print(Panel.fit(
        "[bold green]✅ Demo completada[/bold green]\n\n"
        "[white]Puntos clave aprendidos:[/white]\n"
        "• Los LLM pueden ejecutarse 100% localmente con Ollama\n"
        "• Costo por token: $0.00 (solo hardware propio)\n"
        "• Ideal para datos sensibles en LATAM (salud, finanzas, gobierno)\n"
        "• Modelos 3B-7B son suficientes para muchos casos de uso empresariales\n\n"
        "[dim]Siguiente paso: Exponer el modelo como API con FastAPI →[/dim]\n"
        "[dim]  python ../fastapi_demo/main.py[/dim]",
        border_style="green"
    ))


def interactive_mode(model: str) -> None:
    """Modo interactivo para que los estudiantes hagan sus propias preguntas."""
    console.print(Panel.fit(
        "[bold cyan]💬 Modo Interactivo[/bold cyan]\n"
        f"[dim]Modelo: {model} | Escribe 'salir' para terminar[/dim]",
        border_style="cyan"
    ))
    
    while True:
        try:
            prompt = console.input("\n[bold yellow]Tu pregunta: [/bold yellow]").strip()
            
            if prompt.lower() in ("salir", "exit", "quit", "q"):
                console.print("[dim]👋 ¡Hasta pronto![/dim]")
                break
            
            if not prompt:
                continue
            
            with console.status("[cyan]🔄 Procesando...[/cyan]"):
                result = chat_with_model(model, prompt, "Interactivo")
            
            display_response(result, "Respuesta", prompt)
            
        except KeyboardInterrupt:
            console.print("\n[dim]👋 Sesión terminada.[/dim]")
            break


def main():
    parser = argparse.ArgumentParser(
        description="Demo LLM Local con Ollama — Fundamentos de Arquitectura LLM"
    )
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL,
        help=f"Modelo Ollama a usar (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--prompt", "-p",
        help="Prompt específico a ejecutar (omite la demo completa)"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Modo interactivo"
    )
    parser.add_argument(
        "--list-models", "-l",
        action="store_true",
        help="Listar modelos disponibles"
    )
    args = parser.parse_args()
    
    # Verificar Ollama
    if not check_ollama_running():
        console.print(Panel(
            "[red]❌ Ollama no está corriendo[/red]\n\n"
            "[white]Pasos para instalar:[/white]\n"
            "1. Descargar desde: https://ollama.ai/download\n"
            "2. Instalar y ejecutar Ollama\n"
            f"3. Descargar modelo: [cyan]ollama pull {args.model}[/cyan]\n"
            "4. Volver a ejecutar este script",
            title="Error de Conexión",
            border_style="red"
        ))
        sys.exit(1)
    
    # Listar modelos
    if args.list_models:
        models = get_available_models()
        table = Table(title="Modelos Ollama Disponibles")
        table.add_column("Modelo", style="cyan")
        for m in models:
            table.add_row(m)
        console.print(table)
        return
    
    # Verificar que el modelo existe
    available = get_available_models()
    if args.model not in available and available:
        console.print(f"[yellow]⚠️  Modelo '{args.model}' no encontrado.[/yellow]")
        console.print(f"[dim]Modelos disponibles: {', '.join(available)}[/dim]")
        console.print(f"[cyan]Para descargar: ollama pull {args.model}[/cyan]")
        if available:
            args.model = available[0]
            console.print(f"[green]Usando: {args.model}[/green]")
    
    # Ejecutar modo seleccionado
    if args.prompt:
        with console.status(f"[cyan]🔄 Procesando con {args.model}...[/cyan]"):
            result = chat_with_model(args.model, args.prompt, "Custom")
        display_response(result, "Custom", args.prompt)
    elif args.interactive:
        interactive_mode(args.model)
    else:
        run_full_demo(args.model)


if __name__ == "__main__":
    main()
