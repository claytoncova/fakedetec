#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional
import art
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from colorama import init, Fore, Style
from fakedetec_lib import ImageAnalyzer

# Initialize colorama
init()

# Initialize rich console
console = Console()

def print_banner():
    """Exibe o banner ASCII art em português."""
    banner = art.text2art("FakeDetec", font="block")
    console.print(Panel(banner, style="bold blue"))
    console.print("[bold green]Ferramenta Forense de Imagens[/bold green]")
    console.print("[italic]Detectando manipulação e geração artificial em imagens[/italic]\n")

def analyze_single_image(image_path: str, analyzer: ImageAnalyzer) -> None:
    """Analisa uma única imagem e exibe os resultados."""
    console.print(f"\n[bold]Analisando:[/bold] {image_path}")
    with Progress() as progress:
        task = progress.add_task("[cyan]Analisando imagem...", total=5)
        results = analyzer.analyze_image(image_path)
        if "error" in results:
            console.print(f"[bold red]Erro ao analisar {image_path}:[/bold red] {results['error']}")
            return
        progress.update(task, advance=5)
    display_results(results)

def analyze_directory(directory_path: str, analyzer: ImageAnalyzer) -> None:
    """Analisa todas as imagens em um diretório."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    image_files = [
        f for f in Path(directory_path).glob('**/*')
        if f.suffix.lower() in image_extensions
    ]
    if not image_files:
        console.print(f"[yellow]Nenhuma imagem encontrada em {directory_path}[/yellow]")
        return
    console.print(f"\n[bold]Foram encontradas {len(image_files)} imagens para análise[/bold]")
    with Progress() as progress:
        task = progress.add_task("[cyan]Analisando imagens...", total=len(image_files))
        for image_file in image_files:
            analyze_single_image(str(image_file), analyzer)
            progress.update(task, advance=1)

def display_results(results: dict) -> None:
    """Exibe os resultados da análise em uma tabela formatada."""
    analysis = results["analysis_results"]
    tabela = Table(title="Resultados da Análise", show_header=True, header_style="bold magenta")
    tabela.add_column("Tipo de Análise", style="cyan")
    tabela.add_column("Status", style="green")
    tabela.add_column("Constatações", style="yellow")
    for analysis_type, data in analysis.items():
        status = "[red]Suspeito[/red]" if data.get("suspicious", False) else "[green]Limpo[/green]"
        findings = "\n".join(data.get("findings", ["Nenhuma constatação suspeita"]))
        tabela.add_row(
            analysis_type.replace("_", " ").title(),
            status,
            findings
        )
    console.print("\n")
    console.print(tabela)
    if "metadata" in analysis and analysis["metadata"].get("exif_data"):
        console.print("\n[bold]Informações de Metadados:[/bold]")
        meta_table = Table(show_header=True, header_style="bold blue")
        meta_table.add_column("Tag", style="cyan")
        meta_table.add_column("Valor", style="yellow")
        for tag, value in analysis["metadata"]["exif_data"].items():
            meta_table.add_row(tag, str(value))
        console.print(meta_table)
    base_name = os.path.splitext(results["filename"])[0]
    console.print(f"\n[bold]Resultados detalhados salvos em:[/bold] output/{base_name}_report.json")
    console.print(f"[bold]Visualizações salvas em:[/bold] output/{base_name}_*.jpg/png")
    console.print("\n[bold]Relatório Técnico de Constatação:[/bold]")
    for analysis_type, data in analysis.items():
        if data.get("suspicious", False) and "parecer" in data:
            console.print(Panel(data["parecer"], title=f"Parecer Técnico – {analysis_type.replace('_', ' ').title()}"))

def main():
    """Ponto de entrada principal da aplicação."""
    parser = argparse.ArgumentParser(
        description="Analisa imagens para manipulação e geração artificial"
    )
    parser.add_argument(
        "path",
        help="Caminho para o arquivo de imagem ou diretório com imagens"
    )
    parser.add_argument(
        "--output",
        default="output",
        help="Diretório de saída para os resultados da análise (padrão: output)"
    )
    args = parser.parse_args()
    print_banner()
    analyzer = ImageAnalyzer(output_dir=args.output)
    path = Path(args.path)
    if not path.exists():
        console.print(f"[bold red]Erro:[/bold red] Caminho não existe: {args.path}")
        sys.exit(1)
    try:
        if path.is_file():
            analyze_single_image(str(path), analyzer)
        elif path.is_dir():
            analyze_directory(str(path), analyzer)
        else:
            console.print(f"[bold red]Erro:[/bold red] Caminho inválido: {args.path}")
            sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Análise interrompida pelo usuário[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Erro:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 