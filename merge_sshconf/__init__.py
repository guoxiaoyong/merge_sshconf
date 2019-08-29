# Copyright (c) 2018 Xiaoyong Guo

import json
import os
import sys
import pathlib
import sshconf
import glob


def get_all_files(root, pattern):
  root = pathlib.Path(os.path.expanduser(root))
  return [path for path in root.rglob(pattern) if path.is_file()]


def format_config(config):
  config = json.loads(config)
  res = []
  try:
    res.append('Host %s\n' % config.pop('Host'))
  except KeyError:
    print(config)
    raise
  for key, value in config.items():
    if key.lower() == 'identityfile' and value[0] != '~':
      value = os.path.join(ROOT_PATH, value)
      res.append('  %s %s\n' % (key, value))
    else:
      res.append('  %s %s\n' % (key, value))
  res.append('\n')
  return res


def format_proxy_config(config):
  config = json.loads(config)
  host = config.pop('Host')
  except_host = 'coin-control-01.ap-southeast-1'
  tmpl = '  ProxyCommand ssh ec2-user@coin-control-01.ap-southeast-1 nc %s %s\n'
  res = []
  try:
    res.append('Host %s\n' % host)
  except KeyError:
    print(config)
    raise
  for key, value in config.items():
    if key.lower() == 'identityfile' and value[0] != '~':
      value = os.path.join(ROOT_PATH, value)
      res.append('  %s %s\n' % (key, value))
    else:
      res.append('  %s %s\n' % (key, value))

  if host != except_host:
    hn = config.get('Hostname') or config.get('HostName')
    res.append(tmpl % (hn, 22))
  res.append('\n')
  return res


def main():
  config_file = pathlib.Path.expanduser('~/.ssh/merge_config.json')
  if not config_file.is_file():
    print(f'{config_file} does not exist!')
    return

  new_ssh_config = sshconf.empty_ssh_config()
  default_ssh_config = pathlib.Path.expanduser('~/.ssh/default_sshconfig')
  if not default_ssh_config.is_file():
    print(f'{default_ssh_config} does not exist!')
  else:
    with default_ssh_config.open() as infile:
      ssh_config = SshConfig(infile.readlines())
      for host in ssh_config.hosts():
        host_config = ssh_config.host(host)
        host_config = update_host_config_path(host_config, root)
        new_ssh_config.add(host, **host_config)

  config = json.loads(config_file.read_text())
  for root, each_config in config.items():
    if isinstance(each_config, dict):
      pattern = each_config
    else:
      pattern = each_config['pattern']

    for sshconf_file in get_all_files(root, pattern):
      with sshconf_file.open() as infile:
        ssh_config = SshConfig(infile.readlines())
        for host in ssh_config.hosts():
          host_config = ssh_config.host(host)
          host_config = update_host_config_path(host_config, root)
          new_ssh_config.add(host, **host_config)
  print(new_ssh_config.config())


if __name__ == '__main__':
  main()
