import click
import asyncio
from ghia.common import GHIA, PrinterObserver, get_token, get_rules
from ghia.Helpers import Parser


@click.command('ghia')
@click.argument('reposlug', type=click.STRING, callback=Parser.parse_reposlug)
@click.option('-s', '--strategy', default=GHIA.DEFAULT_STRATEGY,
              show_default=True, type=click.Choice(GHIA.STRATEGIES.keys()),
              envvar=GHIA.ENVVAR_STRATEGY,
              help='How to handle assignment collisions.')
@click.option('--dry-run', '-d', is_flag=True, envvar=GHIA.ENVVAR_DRYRUN,
              help='Run without making any changes.')
@click.option('-a', '--config-auth', type=click.File('r'), callback=get_token,
              help='File with authorization configuration.', required=True)
@click.option('-r', '--config-rules', type=click.File('r'), callback=get_rules,
              help='File with assignment rules configuration.', required=True)
@click.option('--async','-x','is_async', is_flag=True, required=False,
              default=False,
              help='Run asynchronously.', show_default=True)
def cli(reposlug, strategy, dry_run, config_auth, config_rules, is_async):
    """CLI tool for automatic issue assigning of GitHub issues"""
    token = config_auth
    rules, fallback_label = config_rules
    slugs = reposlug
    ghia = GHIA(token, rules, fallback_label, dry_run, strategy,is_async=is_async)
    ghia.add_observer('printer', PrinterObserver)
    ghia.run(slugs)




if __name__ == '__main__':
    cli()