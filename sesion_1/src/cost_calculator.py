"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Calculadora de Costos LLM
Fundamentos de Arquitectura LLM — Sesión 1, Tema 3

Uso:
  python cost_calculator.py
  python cost_calculator.py --tokens-in 10000000 --tokens-out 5000000
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()


@dataclass
class LLMProvider:
    """Representación de un proveedor de LLM con su estructura de costos."""
    name: str
    model: str
    input_per_1m: float   # USD por 1M tokens de entrada
    output_per_1m: float  # USD por 1M tokens de salida
    context_window: str
    strengths: str
    latam_notes: str


# ── Base de datos de proveedores (Mayo 2025) ─────────────
PROVIDERS = [
    LLMProvider("OpenAI",     "GPT-4o",              2.50,  10.00, "128K", "Mejor calidad general",                "Disponible en Azure para compliance"),
    LLMProvider("OpenAI",     "GPT-4o mini",          0.15,   0.60, "128K", "Costo/calidad para tareas simples",    "Ideal para startups LATAM"),
    LLMProvider("OpenAI",     "GPT-4.1 nano",         0.10,   0.40,  "1M",  "Ultra-eficiente, contexto enorme",     "Muy nuevo, revisar disponibilidad"),
    LLMProvider("Anthropic",  "Claude 3.5 Haiku",     0.80,   4.00, "200K", "Seguimiento de instrucciones",         "Excelente para procesos regulados"),
    LLMProvider("Anthropic",  "Claude 3.7 Sonnet",    3.00,  15.00, "200K", "Razonamiento extendido",               "Para análisis financiero complejo"),
    LLMProvider("Google",     "Gemini 1.5 Flash",     0.075,  0.30,  "1M",  "Contexto largo, más barato",           "Integra bien con GCP LATAM"),
    LLMProvider("Google",     "Gemini 2.0 Flash",     0.10,   0.40,  "1M",  "Multimodal, velocidad",                "Google Cloud Colombia/México"),
    LLMProvider("Meta/Local", "Llama 3.1 70B (GPU)",  0.09,   0.09,  "128K","Open source, self-hosted",             "Costo = infraestructura GPU"),
    LLMProvider("Local",      "Llama 3.2:3B (Ollama)",0.00,   0.00,  "128K","Sin costo por token",                 "Laptop modesta, privacidad total"),
    LLMProvider("Local",      "Mistral 7B (Ollama)",  0.00,   0.00,  "32K", "Código y análisis local",              "CPU moderno, sin GPU requerida"),
]


def calculate_monthly_cost(
    provider: LLMProvider,
    input_tokens: int,
    output_tokens: int
) -> dict:
    """
    Calcula el costo mensual de un proveedor dado el volumen de tokens.
    
    Args:
        provider: Configuración del proveedor
        input_tokens: Tokens de entrada por mes
        output_tokens: Tokens de salida por mes
    
    Returns:
        dict con costos mensuales y anuales
    """
    monthly_input_cost  = (input_tokens  / 1_000_000) * provider.input_per_1m
    monthly_output_cost = (output_tokens / 1_000_000) * provider.output_per_1m
    monthly_total       = monthly_input_cost + monthly_output_cost
    
    return {
        "monthly_input_usd":  round(monthly_input_cost, 2),
        "monthly_output_usd": round(monthly_output_cost, 2),
        "monthly_total_usd":  round(monthly_total, 2),
        "annual_total_usd":   round(monthly_total * 12, 2),
    }


def display_cost_comparison(
    input_tokens: int = 10_000_000,
    output_tokens: int = 5_000_000,
    use_case: str = "Chatbot empresarial LATAM"
) -> None:
    """Muestra tabla comparativa de costos entre proveedores."""
    
    console.print(Panel.fit(
        f"[bold cyan]💰 Calculadora de Costos LLM[/bold cyan]\n"
        f"[white]Caso de uso: {use_case}[/white]\n"
        f"[dim]Tokens entrada/mes: {input_tokens:,} | Tokens salida/mes: {output_tokens:,}[/dim]",
        border_style="cyan"
    ))
    
    table = Table(
        title="Comparativa de Costos (Mayo 2025)",
        show_header=True,
        header_style="bold white on dark_blue",
        border_style="blue",
        row_styles=["", "dim"]
    )
    
    table.add_column("Proveedor",    style="cyan", width=12)
    table.add_column("Modelo",       style="white", width=22)
    table.add_column("$/1M in",      justify="right", style="yellow", width=9)
    table.add_column("$/1M out",     justify="right", style="yellow", width=9)
    table.add_column("Costo/Mes",    justify="right", style="bold green", width=11)
    table.add_column("Costo/Año",    justify="right", style="bold red", width=11)
    table.add_column("Contexto",     style="dim", width=8)
    table.add_column("Nota LATAM",   style="dim", width=30)
    
    results = []
    for p in PROVIDERS:
        costs = calculate_monthly_cost(p, input_tokens, output_tokens)
        results.append((p, costs))
    
    # Ordenar por costo mensual
    results.sort(key=lambda x: x[1]["monthly_total_usd"])
    
    cheapest_paid = None
    for p, costs in results:
        monthly = costs["monthly_total_usd"]
        annual  = costs["annual_total_usd"]
        
        # Marcar el más barato de pago
        if monthly > 0 and cheapest_paid is None:
            cheapest_paid = p.model
        
        # Estilo especial para opciones gratuitas
        month_str = f"[bold green]$0.00[/bold green]" if monthly == 0 else f"${monthly:,.2f}"
        year_str  = f"[bold green]$0.00[/bold green]" if annual  == 0 else f"${annual:,.2f}"
        
        table.add_row(
            p.name,
            p.model,
            f"${p.input_per_1m:.3f}",
            f"${p.output_per_1m:.3f}",
            month_str,
            year_str,
            p.context_window,
            p.latam_notes,
        )
    
    console.print(table)
    
    # Insights
    console.print()
    console.print(Panel(
        f"[bold white]💡 Insights para este caso de uso:[/bold white]\n\n"
        f"[white]• Opción más económica pagada:[/white] [cyan]{cheapest_paid}[/cyan]\n"
        f"[white]• Ahorro vs GPT-4o:[/white] [green]hasta 97% usando Gemini Flash[/green]\n"
        f"[white]• Para datos sensibles (salud/finanzas):[/white] [yellow]Ollama local = $0 + total privacidad[/yellow]\n"
        f"[white]• Decisión clave:[/white] calidad requerida vs presupuesto vs compliance regulatorio\n\n"
        f"[dim]Tip: Usa {input_tokens:,} tokens de entrada = ~{input_tokens//750:,} páginas de texto[/dim]",
        border_style="yellow",
        title="[bold yellow]Análisis[/bold yellow]"
    ))


def roi_analysis(
    current_manual_cost_monthly: float = 50000,
    llm_monthly_cost: float = 2000,
    productivity_gain_pct: float = 40,
) -> None:
    """
    Calcula el ROI de implementar un LLM vs proceso manual.
    Muy relevante para justificar inversión ante stakeholders LATAM.
    """
    console.print(Panel.fit(
        "[bold cyan]📈 Análisis de ROI — LLM vs Proceso Manual[/bold cyan]",
        border_style="cyan"
    ))
    
    monthly_savings = (current_manual_cost_monthly * productivity_gain_pct / 100) - llm_monthly_cost
    annual_savings  = monthly_savings * 12
    roi_pct         = (monthly_savings / llm_monthly_cost) * 100 if llm_monthly_cost > 0 else float('inf')
    payback_months  = llm_monthly_cost / monthly_savings if monthly_savings > 0 else float('inf')
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Métrica", style="white")
    table.add_column("Valor", style="bold yellow")
    
    table.add_row("Costo proceso manual/mes",    f"${current_manual_cost_monthly:,.2f} USD")
    table.add_row("Ganancia de productividad",   f"{productivity_gain_pct}%")
    table.add_row("Costo LLM/mes",               f"${llm_monthly_cost:,.2f} USD")
    table.add_row("─" * 30,                      "─" * 15)
    table.add_row("[bold]Ahorro mensual neto[/bold]",     f"[bold green]${monthly_savings:,.2f} USD[/bold green]")
    table.add_row("[bold]Ahorro anual neto[/bold]",       f"[bold green]${annual_savings:,.2f} USD[/bold green]")
    table.add_row("[bold]ROI mensual[/bold]",             f"[bold cyan]{roi_pct:.0f}%[/bold cyan]")
    table.add_row("[bold]Payback period[/bold]",          f"[bold]{payback_months:.1f} meses[/bold]" if payback_months != float('inf') else "Inmediato")
    
    console.print(table)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Calculadora de Costos LLM")
    parser.add_argument("--tokens-in",  type=int, default=10_000_000, help="Tokens de entrada por mes")
    parser.add_argument("--tokens-out", type=int, default=5_000_000,  help="Tokens de salida por mes")
    parser.add_argument("--use-case",   type=str, default="Chatbot empresarial LATAM")
    parser.add_argument("--roi",        action="store_true", help="Mostrar análisis de ROI")
    args = parser.parse_args()
    
    display_cost_comparison(args.tokens_in, args.tokens_out, args.use_case)
    
    if args.roi:
        console.print()
        roi_analysis()
