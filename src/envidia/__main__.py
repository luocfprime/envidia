from envidia.core.cli import CLI
from envidia.core.loader import loader


def main():
    cli = CLI(loader=loader).create_main_command()
    cli()


if __name__ == "__main__":
    main()
