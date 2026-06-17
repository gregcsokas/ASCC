import typer

from app.accidents.commands import commands as accidents_commands

cli = typer.Typer(help="ASCC management commands.", no_args_is_help=True)
cli.add_typer(accidents_commands, name="accidents")

if __name__ == "__main__":
    cli()
