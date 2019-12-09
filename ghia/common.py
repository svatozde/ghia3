import configparser
import click
import re

from ghia.github import GitHub


class PrinterObserver:

    @staticmethod
    def issue(owner, repo, issue):
        number, url = issue['number'], issue['html_url']
        identifier = click.style(f'{owner}/{repo}#{number}', bold=True)
        click.echo(f'-> {identifier} ({url})')

    @staticmethod
    def assignees(old, new):
        mi = click.style('-', fg='red', bold=True)
        pl = click.style('+', fg='green', bold=True)
        eq = click.style('=', fg='blue', bold=True)
        assignees = list(set(old).union(set(new)))
        assignees.sort(key=lambda a: a.lower())
        for assignee in assignees:
            sign = eq
            if assignee not in old:
                sign = pl
            elif assignee not in new:
                sign = mi
            click.echo(f'   {sign} {assignee}')

    @staticmethod
    def fallbacked(label, added=True):
        prefix = click.style('FALLBACK', fg='yellow', bold=True)
        click.echo('   ', nl=False)
        message = 'added label' if added else 'already has label'
        click.echo(f'{prefix}: {message} "{label}"')

    @staticmethod
    def error(message, of_issue=False):
        prefix = click.style('ERROR', bold=True, fg='red')
        if of_issue:
            click.echo('   ', nl=False, err=True)
        click.echo(f'{prefix}: {message}', err=True)


def _strategy_append(found, old):
    return old + [a for a in found if a not in old]


def _strategy_set(found, old):
    return found if len(old) == 0 else old


def _strategy_change(found, old):
    return found


def _match_title(pattern, issue):
    """
       :param pattern:
       :param issue:
       :return: [True] if issue contains the pattern

       >>> _match_text('aaa',{'title': 'aaa','body': "bbb"})

       >>> _match_text('aaa',{'title': 'bbb','body': "bbb"})

       """
    return re.search(pattern, issue['title'], re.IGNORECASE)


def _match_text(pattern, issue):
    """
    :param pattern:
    :param issue:
    :return: [True] if issue contains the pattern

    >>> _match_text('.*',{'body': 'aaa'})
    <re.Match object; span=(0, 3), match='aaa'>

    >>> _match_text('aaa',{'body': "bbb"})

    """
    return re.search(pattern, issue['body'], re.IGNORECASE)


def _match_label(pattern, issue):
    """
        :param pattern:
        :param issue:
        :return: [True] if issue contains the pattern

        >>> _match_label('aaa', {'labels': [{'name': 'aaa'}]})
        True

        >>> _match_label('aaa', {'labels': [{'name': 'bbb'}]})
        False
    """
    return any(re.search(pattern, label['name'], re.IGNORECASE)
               for label in issue['labels'])


def _match_any(*args):
    """
            :param pattern:
            :param issue:
            :return: [True] if issue contains the pattern

            >>> _match_any('aaa',{'labels': [{'name': 'aaa'}],'body': 'bbb','title': 'bbb'})
            True

            >>> _match_any('aa',{'labels': [{'name': 'bbb'}],'body': 'bbb','title': 'bbb'})
            False

            >>> _match_any('aa',{'labels': [{'name': 'bbb'}],'body': 'aa','title': 'bbb'})
            <re.Match object; span=(0, 2), match='aa'>

            >>> _match_any('aa',{'labels': [{'name': 'bbb'}],'body': 'bb','title': 'aa'})
            <re.Match object; span=(0, 2), match='aa'>
        """
    return _match_title(*args) or _match_text(*args) or _match_label(*args)

class GHIA:

    STRATEGIES = {
        'append': _strategy_append,
        'set': _strategy_set,
        'change': _strategy_change
    }
    DEFAULT_STRATEGY = 'append'

    ENVVAR_STRATEGY = 'GHIA_STRATEGY'
    ENVVAR_DRYRUN = 'GHIA_DRYRUN'
    ENVVAR_CONFIG = 'GHIA_CONFIG'

    MATCHERS = {
        'any': _match_any,
        'text': _match_text,
        'title': _match_title,
        'label': _match_label
    }

    def __init__(self, token, rules, fallback_label, dry_run, ghia_strategy):
        self.github = GitHub(token)
        self.rules = rules
        self.fallback_label = fallback_label
        self.real_run = not dry_run
        self.strategy = self.STRATEGIES[ghia_strategy]
        self.observers = dict()

    def add_observer(self, name, observer):
        self.observers[name] = observer

    def remove_observer(self, name):
        del self.observers[name]

    def call_observers(self, method, *args, **kwargs):
        for observer in self.observers.values():
            getattr(observer, method)(*args, **kwargs)

    @classmethod
    def _matches_pattern(cls, pattern, issue):
        t, p = pattern.split(':', 1)
        return cls.MATCHERS[t](p, issue)

    @classmethod
    def _matches(cls, patterns, issue):
        return any(cls._matches_pattern(pattern, issue)
                   for pattern in patterns)

    def _find_assignees(self, issue):
        return [username
                for username, patterns in self.rules.items()
                if self._matches(patterns, issue)
                ]

    def _make_new_assignees(self, found, old):
        return self.strategy(found, old)

    def _update_assignees(self, owner, repo, issue, assignees):
        if self.real_run:
            self.github.set_issue_assignees(owner, repo, issue['number'], assignees)

    def _update_labels(self, owner, repo, issue, labels):
        if self.real_run:
            self.github.set_issue_labels(owner, repo, issue['number'], labels)

    def _create_fallback_label(self, owner, repo, issue):
        if self.fallback_label is None:
            return  # no fallback
        labels = [label['name'] for label in issue['labels']]
        if self.fallback_label not in labels:
            self.call_observers('fallbacked', self.fallback_label, True)
            labels.append(self.fallback_label)
            self._update_labels(owner, repo, issue, labels)
        else:
            self.call_observers('fallbacked', self.fallback_label, False)

    def run_issue(self, owner, repo, issue):
        self.call_observers('issue', owner, repo, issue)
        found_assignees = self._find_assignees(issue)
        old_assignees = [assignee['login'] for assignee in issue['assignees']]
        new_assignees = self.strategy(found_assignees, old_assignees)
        if old_assignees != new_assignees:  # there is a change
            self._update_assignees(owner, repo, issue, new_assignees)
        self.call_observers('assignees', old_assignees, new_assignees)
        if len(new_assignees) == 0:  # noone is assigned now
            self._create_fallback_label(owner, repo, issue)

    def run(self, owner, repo):
        try:
            issues = self.github.issues(owner, repo)
        except Exception:
            self.call_observers('error', f'Could not list issues '
                                         f'for repository {owner}/{repo}')
            exit(10)
            return

        for issue in issues:
            try:
                self.run_issue(owner, repo, issue)
            except Exception:
                number = issue['number']
                self.call_observers('error', f'Could not update issue '
                                             f'{owner}/{repo}#{number}', True)


def parse_rules(cfg):
    """
    Parse labels to dict where label is key and list
    of patterns is corresponding value
    cfg: ConfigParser with loaded configuration of labels
    """
    patterns = {
        username: list(filter(None, cfg['patterns'][username].splitlines()))
        for username in cfg['patterns']
    }
    fallback = cfg.get('fallback', 'label', fallback=None)
    for user_patterns in patterns.values():
        for pattern in user_patterns:
            t, p = pattern.split(':', 1)
            assert t in GHIA.MATCHERS.keys()
    return patterns, fallback


def get_rules(ctx, param, config_rules):
    """
    Extract labels from labels config and do the checks
    config_rules: ConfigParser with loaded configuration of labels
    """
    try:
        cfg_rules = configparser.ConfigParser()
        cfg_rules.optionxform = str
        cfg_rules.read_file(config_rules)
        return parse_rules(cfg_rules)
    except Exception:
        raise click.BadParameter('incorrect configuration format')


def get_token(ctx, param, config_auth):
    """
    Extract token from auth config and do the checks
    config_auth: ConfigParser with loaded configuration of auth
    """
    try:
        cfg_auth = configparser.ConfigParser()
        cfg_auth.read_file(config_auth)
        return cfg_auth.get('github', 'token')
    except Exception:
        raise click.BadParameter('incorrect configuration format')

