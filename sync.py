#!/usr/bin/env python

import sys, os, glob, errno
import yaml
import zipfile, zlib
from github import Github


def main():
  
  # load config file and command line options

  config = yaml.load(open("config.yml", 'r'))
  options = get_options()

  output_dir = os.path.join(os.getcwd(), "output/bills") # absolute path
  mkdir_p(output_dir)

  session = options.get('session', None)
  if not session:
    print "Provide a --session option."
    return


  print "Locating all data.json files on disk..."

  data_dir = config['data_directory']

  # switch working directory to input data dir for relative globs
  os.chdir(os.path.join(data_dir, "bills", session))
  files = glob.glob("*/*/data.json")


  print "Creating zip file..."

  with zipfile.ZipFile(os.path.join(output_dir, "bills-%s.zip" % session), "w", zipfile.ZIP_DEFLATED) as zf:
    for f in files:
      zf.write(f)

  
  print "Connecting to Github..."

  username = config['github']['credentials']['username']
  password = config['github']['credentials']['password']
  client = Github(username, password)

  organization = client.get_organization(config['github']['organization'])
  repo = organization.get_repo(config['github']['repo'])



def get_options():
  options = {}
  for arg in sys.argv[1:]:
    if arg.startswith("--"):
      if "=" in arg:
        key, value = arg.split('=')
      else:
        key, value = arg, True
      key = key.split("--")[1]
      options[key.lower()] = value
  return options

# mkdir -p in python, from:
# http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc: # Python >2.5
    if exc.errno == errno.EEXIST:
      pass
    else: 
      raise

if __name__ == '__main__':
  main()