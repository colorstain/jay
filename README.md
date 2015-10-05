# Jay

`jay` is a nifty command line utility to get information and quickly ssh into
running AWS ec2 instances. The utility assumes you have your aws credentials
are stored in a config file in `~/.aws` as described in the 
[AWS documentation](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html).

To ssh into multiple servers at once make sure to install `tmux`.

## Usage

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

