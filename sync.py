#!/usr/bin/env python

import sys, os, glob, errno, subprocess
import yaml
import zipfile, zlib
from github import Github


def main():
  
  # load config file and command line options

  config = yaml.load(open("config.yml", 'r'))
  options = get_options()

  session = options.get('session', None)
  if not session:
    print "Provide a --session option."
    return

  output_dir = os.path.join(os.getcwd(), "output/bills") # absolute path
  mkdir_p(output_dir)

  zipfile_name = "bills-%s.zip" % session
  zipfile_path = os.path.join(output_dir, zipfile_name)

  if os.path.exists(zipfile_path) and options.get('cache', False):
    print "Using cached zip file..."

  else:
    print "Zipping up data.json files..."

    data_dir = config['data_directory']

    # switch working directory to input data dir for relative globs
    os.chdir(os.path.join(data_dir, "bills", session))
    files = glob.glob("*/*/data.json")

    with zipfile.ZipFile(zipfile_path, "w", zipfile.ZIP_DEFLATED) as zf:
      for f in files:
        zf.write(f)


  print "Creating download on Github..."

  username = config['github']['credentials']['username']
  password = config['github']['credentials']['password']
  client = Github(username, password)

  organization = client.get_organization(config['github']['organization'])
  repo = organization.get_repo(config['github']['repo'])

  for download in repo.get_downloads():
    if download.name == zipfile_name:
      print "Deleting existing download..."
      download.delete()

  download = repo.create_download(
    zipfile_name, os.path.getsize(zipfile_path), 
    "Bill data for Congress #%s" % session, "application/zip")

  
  print "Uploading file to S3..."

  os.chdir(output_dir)

  subprocess.call(["curl",
    '-F key=%s' % download.path,
    '-F acl=%s' % download.acl,
    '-F success_action_status=201',
    '-F Filename=%s' % download.name,
    '-F AWSAccessKeyId=%s' % download.accesskeyid,
    '-F Policy=%s' % download.policy,
    '-F Signature=%s' % download.signature,
    '-F Content-Type=%s' % download.mime_type,
    '-F file=@%s' % zipfile_name,
    download.s3_url
  ], stdout=open("/dev/null"))

  print "Uploaded %s to Github." % zipfile_name
  exit(0)


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