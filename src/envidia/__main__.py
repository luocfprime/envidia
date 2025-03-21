from envidia.core.cli import CLI
from envidia.core.loader import loader


def main(*args, **kwargs):
    cli = CLI(loader=loader).create_main_command()
    cli(*args, **kwargs)


if __name__ == "__main__":
    main()
