"""Command-line interface for AICodeGen."""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
import yaml

from .core.config import Config
from .core.generator import CodeGenerator
from .utils.code_analyzer import CodeAnalyzer


console = Console()


@click.group()
@click.version_option(version="0.1.0")
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file path")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.pass_context
def main(ctx, config, debug):
    """AICodeGen - AI-Powered Software Engineering and Code Generation Platform."""
    ctx.ensure_object(dict)
    
    if config:
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        ctx.obj['config'] = Config(**config_data)
    else:
        ctx.obj['config'] = Config.from_env()
    
    if debug:
        ctx.obj['config'].debug = True


@main.command()
@click.argument("prompt", type=str)
@click.option("--output", "-o", type=str, help="Output file path")
@click.option("--template", "-t", type=str, help="Template to use")
@click.option("--language", "-l", type=str, help="Target programming language")
@click.pass_context
def generate(ctx, prompt, output, template, language):
    """Generate code based on a natural language prompt."""
    config = ctx.obj['config']
    
    if language:
        config.code_gen.language = language
    
    generator = CodeGenerator(config)
    
    try:
        code = generator.generate_code(
            prompt=prompt,
            template_name=template,
            output_file=output
        )
        
        if not output:
            console.print("\n[bold green]Generated Code:[/bold green]")
            console.print(f"```{config.code_gen.language}\n{code}\n```")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@main.command()
@click.argument("description", type=str)
@click.argument("project_name", type=str)
@click.option("--components", "-c", multiple=True, help="Components to generate")
@click.option("--output-dir", "-o", type=str, help="Output directory")
@click.pass_context
def project(ctx, description, project_name, components, output_dir):
    """Generate a complete project structure."""
    config = ctx.obj['config']
    
    if output_dir:
        config.code_gen.output_directory = output_dir
    
    generator = CodeGenerator(config)
    
    try:
        components_list = list(components) if components else None
        project_files = generator.generate_project(
            project_description=description,
            project_name=project_name,
            components=components_list
        )
        
        console.print(f"\n[bold green]Generated {len(project_files)} files:[/bold green]")
        for filename in project_files.keys():
            console.print(f"  ✅ {filename}")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def analyze(ctx, file_path):
    """Analyze code structure and complexity."""
    analyzer = CodeAnalyzer()
    
    with open(file_path, 'r') as f:
        code = f.read()
    
    # Determine language from file extension
    ext = Path(file_path).suffix.lower()
    language = {
        '.py': 'python',
        '.js': 'javascript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cs': 'csharp'
    }.get(ext, 'unknown')
    
    if language == 'python':
        analysis = analyzer.analyze_python_code(code)
        
        if 'error' in analysis:
            console.print(f"[bold red]Error:[/bold red] {analysis['error']}")
            return
        
        # Display analysis results
        table = Table(title=f"Code Analysis: {file_path}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Lines of Code", str(analysis['lines_of_code']))
        table.add_row("Functions", str(len(analysis['functions'])))
        table.add_row("Classes", str(len(analysis['classes'])))
        table.add_row("Imports", str(len(analysis['imports'])))
        table.add_row("Complexity", str(analysis['complexity']))
        
        console.print(table)
        
        if analysis['functions']:
            func_table = Table(title="Functions")
            func_table.add_column("Name")
            func_table.add_column("Line")
            func_table.add_column("Arguments")
            
            for func in analysis['functions']:
                func_table.add_row(
                    func['name'],
                    str(func['line']),
                    ', '.join(func['args'])
                )
            
            console.print(func_table)
    else:
        console.print(f"[yellow]Analysis for {language} files not fully supported yet.[/yellow]")
        
        # Basic line counting
        line_counts = analyzer.count_lines(code)
        table = Table(title=f"Basic Analysis: {file_path}")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green")
        
        for metric, count in line_counts.items():
            table.add_row(metric.title(), str(count))
        
        console.print(table)


@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def explain(ctx, file_path):
    """Explain code using AI."""
    config = ctx.obj['config']
    generator = CodeGenerator(config)
    
    with open(file_path, 'r') as f:
        code = f.read()
    
    try:
        explanation = generator.ai_model.explain_code(code)
        
        console.print(f"\n[bold blue]Code Explanation for {file_path}:[/bold blue]")
        console.print(explanation)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def review(ctx, file_path):
    """Review code using AI."""
    config = ctx.obj['config']
    generator = CodeGenerator(config)
    
    with open(file_path, 'r') as f:
        code = f.read()
    
    try:
        review = generator.ai_model.review_code(code)
        
        console.print(f"\n[bold blue]Code Review for {file_path}:[/bold blue]")
        console.print(review['suggestions'])
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@main.command()
@click.pass_context
def config_show(ctx):
    """Show current configuration."""
    config = ctx.obj['config']
    
    table = Table(title="AICodeGen Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    config_dict = config.to_dict()
    
    def add_config_rows(data, prefix=""):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                add_config_rows(value, full_key)
            else:
                table.add_row(full_key, str(value))
    
    add_config_rows(config_dict)
    console.print(table)


if __name__ == "__main__":
    main()