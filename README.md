# Start and Stop EC2 from a simple script

EC2 schedule is actually pretty expensive.
I chose to let a cron on the bastion do the actual job

## Warning

This tool stops instances based on a pattern.

It's intended to be run from cronjobs. 

**It can, and will, shutdown unexpected instances if mis-used. Be careful.**

## Usage

```
Usage: stasto.py [OPTIONS] COMMAND [ARGS]...

Options:
  -c, --conf FILENAME  Path to the JSON config
  --region TEXT        AWS region to work with
  --profile TEXT       AWS profile to work with
  --help               Show this message and exit.

Commands:
  start
  status
  stop
```

## Dependancies

You will need: 
 - `python2` (obviously)
 - `click`
 - `boto3`

Install these with : `pip install [whatever]`
