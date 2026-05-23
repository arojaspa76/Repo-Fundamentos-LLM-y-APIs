"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Demo: Streaming de respuestas LLM con Ollama

Propósito:
  Mostrar cómo implementar streaming para mejorar la
  experiencia del usuario (respuesta progresiva, no esperar
  que el modelo termine de generar todos los tokens).

  Esto es fundamental en aplicaciones de producción donde
  el tiempo de respuesta percibido importa.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import ollama
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

console = Console()
MODEL = "llama3.2:3b"

SYSTEM_PROMPT = """Eres un experto en arquitecturas LLM para empresas LATAM. 
Respondes en español, con ejemplos concretos del contexto latinoamericano."""


def stream_response(prompt: str, model: str = MODEL) -> None:
    """
    Hace streaming de la respuesta del LLM token por token.
    
    El streaming mejora la UX porque el usuario ve la respuesta
    mientras se genera, en lugar de esperar segundos en blanco.
    """
    console.print(Panel(
        f"[yellow]{prompt}[/yellow]",
        title="[bold cyan]💬 Pregunta (con Streaming)[/bold cyan]",
        border_style="cyan"
    ))
    
    start_time = time.time()
    accumulated_text = ""
    token_count = 0
    
    # --- STREAMING: La clave es stream=True ---
    stream = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        stream=True,  # ← Aquí está la magia
        options={"temperature": 0.7, "num_predict": 400}
    )
    
    # Usar Rich Live para actualizar el panel en tiempo real
    with Live(
        Panel("", title="[bold green]🤖 Respuesta (en tiempo real)[/bold green]", border_style="green"),
        console=console,
        refresh_per_second=20
    ) as live:
        for chunk in stream:
            # Cada chunk contiene un fragmento de la respuesta
            token = chunk['message']['content']
            accumulated_text += token
            token_count += 1
            
            # Actualizar el panel con el texto acumulado
            live.update(Panel(
                Text(accumulated_text),
                title=f"[bold green]🤖 Generando... ({token_count} tokens)[/bold green]",
                border_style="green"
            ))
    
    elapsed = time.time() - start_time
    
    # Mostrar métricas finales
    console.print(
        f"[dim]⏱ Tiempo total: {elapsed:.2f}s | "
        f"⚡ ~{token_count / elapsed:.1f} tokens/seg | "
        f"💰 Costo: $0.00[/dim]"
    )


def compare_streaming_vs_sync(prompt: str, model: str = MODEL) -> None:
    """
    Compara la experiencia de respuesta síncrona vs streaming.
    Útil para demostrar en clase por qué el streaming importa en producción.
    """
    console.rule("[bold]Comparativa: Síncrono vs Streaming[/bold]")
    
    # --- Modo síncrono (esperar toda la respuesta) ---
    console.print("\n[yellow]1️⃣  Modo SÍNCRONO: Esperando respuesta completa...[/yellow]")
    t0 = time.time()
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )
    sync_time = time.time() - t0
    console.print(f"[green]✅ Respuesta recibida en {sync_time:.2f}s[/green]")
    console.print(f"[dim]{response['message']['content'][:200]}...[/dim]")
    
    console.print(f"\n[cyan]2️⃣  Modo STREAMING: Respuesta token a token...[/cyan]")
    stream_response(prompt, model)
    
    console.print(Panel(
        f"[white]En modo síncrono, el usuario esperó [red bold]{sync_time:.1f}s[/red bold] en blanco.\n"
        "En modo streaming, vio la primera respuesta en [green bold]<0.5s[/green bold].\n\n"
        "[dim]👉 Para APIs de producción, implementa siempre Server-Sent Events (SSE)\n"
        "   o WebSockets para hacer streaming al cliente final.[/dim]",
        title="[bold]💡 Conclusión",
        border_style="yellow"
    ))


if __name__ == "__main__":
    prompt = "Explica en 5 puntos cómo las empresas financieras en LATAM pueden adoptar LLMs de forma segura y cumpliendo regulaciones locales."
    
    console.print(Panel.fit(
        "[bold cyan]🌊 Demo: Streaming de Respuestas LLM[/bold cyan]\n"
        "[dim]Fundamentos de Arquitectura LLM — Sesión 1[/dim]",
        border_style="cyan"
    ))
    
    # Demo principal de streaming
    stream_response(prompt)
    
    console.print("\n[dim]Para ver comparativa síncrono vs streaming, ejecuta:[/dim]")
    console.print("[cyan]  python demo_streaming.py --compare[/cyan]")
