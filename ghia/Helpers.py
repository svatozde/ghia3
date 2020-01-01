import re
import click

class Parser:
    @staticmethod
    def parse_reposlug(ctx, param, reposlug):
        try:
            if re.match("[^,]+?(,?([^,]+?,)*[^,]+?)?", reposlug):
                ret = []
                for r in reposlug.split(','''):
                    owner, repo = r.strip().split('/')
                    ret.append((owner,repo))
                return ret
            else:
                raise click.BadParameter("invlid format")
        except:
            raise click.BadParameter("not in owner/repository format")