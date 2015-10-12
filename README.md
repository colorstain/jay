# Jay

`jay` is a nifty command line utility to get information and quickly ssh into
running AWS ec2 instances. The utility assumes you have your aws credentials
are stored in a config file in `~/.aws` as described in the 
[AWS documentation](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html).

To ssh into multiple servers at once make sure to install `tmux`.

## Usage

### AWS configuration

Before using `jay`, you should setup your aws credentials. `jay` uses boto so
you can configure them using any of the allowed [boto configurations](http://boto.readthedocs.org/en/latest/boto_config_tut.html)

The easist way is to add a config file at `~/.aws/config` like this:

```
[default]
output = json
region = us-east-1
[profile prod]
output = json
region = us-west-1
```

and your credentials at `~/.aws/credentials`:

```
[default]
aws_access_key_id = ACCESS-KEY-ID
aws_secret_access_key = ACCESS-SECRET-KEY
[prod]
aws_access_key_id = ACCESS-KEY-ID
aws_secret_access_key = ACCESS-SECRET-KEY
```

### Commands
```
Usage: jay [OPTIONS] COMMAND [ARGS]...

Options:
  --profile TEXT      Name of aws profile.
  -t, --tags TEXT...  Instance tags as name value pairs
  --help              Show this message and exit.

Commands:
  ls   List running instances.
  ssh  SSH into ec2 servers.
```

### Sub commands

- `ls` List running instances
  `jay -t role web -t env dev --profile production ls`

- `ssh` SSH into one instance
  ```
  Usage: jay ssh [OPTIONS]

  SSH into ec2 servers.

  Options:
    --tmux-all                SSHs to all servers matching the filters using
                              tmux.
    -u, --ssh-user TEXT
    -k, --keys-dir DIRECTORY  Directory where the keys are stored.
    -p, --private-ip          Use private ip to ssh to instance.
    --help                    Show this message and exit.
  ```

  Example:
  `jay -t role web ssh`

