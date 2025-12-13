import click
import sys
from .config import load_config
from .scanner import scan_directory
from .executor import execute_files
from .formatters.markdown import MarkdownFormatter

@click.group()
def main():
    """CodeSubmit: Automate academic code submissions."""
    pass

@main.command()
@click.option('--config', '-c', default='codesubmit.yaml', help='Path to configuration file.')
@click.option('--output', '-o', default='submission.md', help='Output file path.')
@click.option('--format', '-f', default='markdown', type=click.Choice(['markdown', 'docx', 'pdf'], case_sensitive=False), help='Output format.')
def generate(config, output, format):
    """Generate the submission document."""
    click.echo(f"Loading configuration from {config}...")
    try:
        conf = load_config(config)
    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        sys.exit(1)
    
    click.echo(f"Scanning {conf.input_root}...")
    try:
        files = scan_directory(conf)
    except Exception as e:
         click.echo(f"Error scanning directory: {e}", err=True)
         sys.exit(1)

    if not files:
        click.echo("No source files found matching the criteria.")
        sys.exit(0)
    
    click.echo(f"Found {len(files)} files. Executing...")
    results = execute_files(files, conf)
    
    click.echo(f"Generating output ({format})...")
    try:
        if format == 'markdown':
            from .formatters.markdown import MarkdownFormatter
            formatter = MarkdownFormatter()
        elif format == 'docx':
            from .formatters.docx_fmt import DocxFormatter
            formatter = DocxFormatter()
            if not output.endswith('.docx'):
                output += '.docx'
                click.echo(f"Adjusted output filename to {output}")
        elif format == 'pdf':
            try:
                from .formatters.pdf_fmt import PdfFormatter
                formatter = PdfFormatter()
            except ImportError:
                 click.echo("Error: PDF export requires 'xhtml2pdf'. Install it with: pip install xhtml2pdf", err=True)
                 sys.exit(1)
            if not output.endswith('.pdf'):
                output += '.pdf'
                click.echo(f"Adjusted output filename to {output}")
        else:
            raise ValueError(f"Unknown format: {format}")

        formatter.save(results, conf, output)
        
        click.echo(f"Done! Saved to {output}")
    except Exception as e:
        click.echo(f"Error generating output: {e}", err=True)
        # import traceback
        # traceback.print_exc()
        sys.exit(1)


@main.command()
def init():
    """Create a default configuration file."""
    click.echo("Creating default codesubmit.yaml...")
    # TODO: Write default config
    pass
