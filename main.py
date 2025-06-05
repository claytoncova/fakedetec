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
    """Print ASCII art banner."""
    banner = art.text2art("FakeDetec", font="block")
    console.print(Panel(banner, style="bold blue"))
    console.print("[bold green]Image Forensics Analysis Tool[/bold green]")
    console.print("[italic]Detecting image manipulation and AI-generated content[/italic]\n")

def analyze_single_image(image_path: str, analyzer: ImageAnalyzer) -> None:
    """Analyze a single image and display results."""
    console.print(f"\n[bold]Analyzing:[/bold] {image_path}")
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Analyzing image...", total=5)
        
        # Run analysis
        results = analyzer.analyze_image(image_path)
        
        if "error" in results:
            console.print(f"[bold red]Error analyzing {image_path}:[/bold red] {results['error']}")
            return
        
        # Update progress
        progress.update(task, advance=5)
    
    # Display results
    display_results(results)

def analyze_directory(directory_path: str, analyzer: ImageAnalyzer) -> None:
    """Analyze all images in a directory."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    image_files = [
        f for f in Path(directory_path).glob('**/*')
        if f.suffix.lower() in image_extensions
    ]
    
    if not image_files:
        console.print(f"[yellow]No image files found in {directory_path}[/yellow]")
        return
    
    console.print(f"\n[bold]Found {len(image_files)} images to analyze[/bold]")
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Analyzing images...", total=len(image_files))
        
        for image_file in image_files:
            analyze_single_image(str(image_file), analyzer)
            progress.update(task, advance=1)

def display_results(results: dict) -> None:
    """Display analysis results in a formatted table."""
    analysis = results["analysis_results"]
    
    # Create summary table
    table = Table(title="Analysis Results", show_header=True, header_style="bold magenta")
    table.add_column("Analysis Type", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Findings", style="yellow")
    
    # Add rows for each analysis type
    for analysis_type, data in analysis.items():
        status = "[red]Suspicious[/red]" if data.get("suspicious", False) else "[green]Clean[/green]"
        findings = "\n".join(data.get("findings", ["No suspicious findings"]))
        
        table.add_row(
            analysis_type.replace("_", " ").title(),
            status,
            findings
        )
    
    # Display table
    console.print("\n")
    console.print(table)
    
    # Display additional information
    if "metadata" in analysis and analysis["metadata"].get("exif_data"):
        console.print("\n[bold]Metadata Information:[/bold]")
        meta_table = Table(show_header=True, header_style="bold blue")
        meta_table.add_column("Tag", style="cyan")
        meta_table.add_column("Value", style="yellow")
        
        for tag, value in analysis["metadata"]["exif_data"].items():
            meta_table.add_row(tag, str(value))
        
        console.print(meta_table)
    
    # Display output location
    base_name = os.path.splitext(results["filename"])[0]
    console.print(f"\n[bold]Detailed results saved in:[/bold] output/{base_name}_report.json")
    console.print(f"[bold]Visualizations saved in:[/bold] output/{base_name}_*.jpg/png")

    # Display parecer técnico (se houver) de cada item suspeito
    console.print("\n")
    console.print(table)
    console.print("\n[bold]Relatório Técnico de Constatação:[/bold]")
    for analysis_type, data in analysis.items():
        if data.get("suspicious", False) and "parecer" in data:
            console.print(Panel(data["parecer"], title=f"Parecer Técnico – {analysis_type.replace('_', ' ').title()}"))

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Analyze images for manipulation and AI-generated content"
    )
    parser.add_argument(
        "path",
        help="Path to image file or directory containing images"
    )
    parser.add_argument(
        "--output",
        default="output",
        help="Output directory for analysis results (default: output)"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Initialize analyzer
    analyzer = ImageAnalyzer(output_dir=args.output)
    
    # Process input path
    path = Path(args.path)
    if not path.exists():
        console.print(f"[bold red]Error:[/bold red] Path does not exist: {args.path}")
        sys.exit(1)
    
    try:
        if path.is_file():
            analyze_single_image(str(path), analyzer)
        elif path.is_dir():
            analyze_directory(str(path), analyzer)
        else:
            console.print(f"[bold red]Error:[/bold red] Invalid path: {args.path}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 