import click
from ghia import GHIA, PrinterObserver

@click.command('ghia')
@click.argument('reposlug', type=click.STRING, callback=parse_reposlug)
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
def cli(reposlug, strategy, dry_run, config_auth, config_rules):
    """CLI tool for automatic issue assigning of GitHub issues"""
    token = config_auth
    rules, fallback_label = config_rules
    owner, repo = reposlug
    ghia = GHIA(token, rules, fallback_label, dry_run, strategy)
    ghia.add_observer('printer', PrinterObserver)
    ghia.run(owner, repo)
