import os.path
import uuid
import subprocess
import click
from collections import namedtuple
from boto3.session import Session


NAME = 'jay'
Instance = namedtuple(
    'Instance', ['name', 'role', 'public_ip', 'private_ip', 'key_name'])


class InstanceMonitor(object):

    def __init__(self, tags=None, profile_name=None):
        self.session = Session(
            profile_name=profile_name)
        self.ec2 = self.session.resource('ec2')
        self.instances = self.get_instances(tags)

    def get_instances(self, tags=None):
        raw_instances = self._retrieve_running_instances(tags)
        instances = list(map(self._extract_instance_info, raw_instances))
        return instances

    def _retrieve_running_instances(self, tags=None):
        tags = tags or {}
        filters = [
            {'Name': 'tag:{}'.format(name), 'Values': val}
            for name, val in tags.items()
        ]
        filters.append({'Name': 'instance-state-name', 'Values': ['running']})
        return list(self.ec2.instances.filter(Filters=filters))

    def _get_tag(self, tags, name):
        for tag in tags:
            if tag.get('Key') == name:
                return tag.get('Value')
        return None

    def _extract_instance_info(self, raw_instance):
        return Instance(
            name=self._get_tag(raw_instance.tags, 'Name'),
            role=self._get_tag(raw_instance.tags, 'role'),
            public_ip=raw_instance.public_ip_address,
            private_ip=raw_instance.private_ip_address,
            key_name=raw_instance.key_name
        )


def table(rows, add_index=False):
    """
    Generates a table from a list of lists. The first row should contain the
    headers.
    """
    rows = [list(row) for row in rows]
    headers = rows[0]
    body = rows[1:]
    if add_index:
        headers.insert(0, '#')
        body = [[i] + row for i, row in enumerate(body)]

    # Determining the lenght of the columns
    col_lens = []
    for i in range(len(body[0])):
        col_lens.append(len(str(max([x[i] for x in body] + headers[i:i+1],
                            key=lambda x: len(str(x))))))

    formats = []
    hformats = []
    for i in range(len(body[0])):
        col_len = col_lens[i]
        if isinstance(rows[0][i], int):
            # align right
            formats.append('{{:>{}}}'.format(col_len))
        else:
            # align left
            formats.append('{{:{}}}'.format(col_len))
        hformats.append('{{:{}}}'.format(col_len))
    pattern = ' | '.join(formats)
    hpattern = ' | '.join(hformats)
    separator = '-+-'.join('-' * n for n in col_lens)
    output = []
    output.append(hpattern.format(*headers))
    output.append(separator)
    for row in body:
        output.append(pattern.format(*row))
    return '\n'.join(output)


def echo_instances(instances, add_index=False):
    out = table([instances[0]._fields] + instances, add_index)
    click.echo(out)


def _get_ssh_cmd(instance, keys_dir, ssh_user, private_ip):
    key = '{}.pem'.format(instance.key_name)
    key_path = os.path.join(keys_dir, key)
    if not os.path.isfile(key_path):
        raise click.ClickException(
            'Key {} does not exist'.format(key))
    click.echo(
        'sshing into {i.name} using {0}'.format(key, i=instance))
    ip_attr = 'private_ip' if private_ip else 'public_ip'
    ip_addr = getattr(instance, ip_attr)
    host = '{}@{}'.format(ssh_user, ip_addr)
    return ['ssh', '-i', key_path, host]


# ----------------------- commands --------------------------------------------


@click.group()
@click.option('--profile', default=None, help='Name of aws profile.')
@click.option('--region', default='')
@click.option('--tags', '-t', nargs=2,
              multiple=True, help='Instance tags as name value pairs')
@click.pass_context
def cli(ctx, tags, profile, region):
    tags = {tag[0]: [tag[1]] for tag in tags}
    ctx.obj = InstanceMonitor(tags, profile)


@cli.command()
@click.option('--tmux-all', is_flag=True,
              help='SSHs to all servers matching the filters using tmux.')
@click.option('--ssh-user', '-u', default='ubuntu')
@click.option('--keys-dir', '-k', default=os.path.expanduser('~/.ssh'),
              type=click.Path(exists=True, file_okay=False,
                              resolve_path=True),
              help='Directory where the keys are stored.')
@click.option('--private-ip', '-p',
              is_flag=True, help='Use private ip to ssh to instance.')
@click.pass_obj
def ssh(monitor, private_ip, keys_dir, ssh_user, tmux_all):
    """
    SSH into ec2 servers.
    """
    instances = monitor.instances
    if instances:
        if tmux_all:
            click.confirm(
                'Do you want to ssh to {} instances'.format(
                    len(instances)), abort=True)
            cmds = [
                ' '.join(_get_ssh_cmd(instance, keys_dir,
                                      ssh_user, private_ip))
                for instance in instances]
            uid = str(uuid.uuid4())[:6]
            session_name = '{}-{}'.format(NAME, uid)
            subprocess.call(
                ['tmux', 'new-session', '-s', session_name, '-d', cmds[0]])
            for cmd in cmds[1:]:
                subprocess.call(
                    ['tmux', 'split-window', '-t', session_name, cmd])
            subprocess.call(
                ['tmux', 'select-layout', '-t', session_name, 'even-vertical'])
            subprocess.call(['tmux', 'attach', '-t', session_name])
        else:
            echo_instances(instances, True)
            index = click.prompt(
                'Please select an instance from the list',
                type=click.IntRange(0, len(instances)), default=0)
            instance = instances[index]
            cmd = _get_ssh_cmd(instance, keys_dir, ssh_user, private_ip)
            subprocess.call(cmd)
    else:
        click.echo('No instances available!')


@cli.command()
@click.pass_obj
def ls(monitor):
    """
    List running instances.
    """
    echo_instances(monitor.instances)

