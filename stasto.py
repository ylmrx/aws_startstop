#!/usr/bin/env python
import sys
import boto3
import click
import json

def validate_region(ctx, param, value):
    regs = [ 'ap-south-1', 'eu-west-3', 'eu-west-2', 'eu-west-1', 'ap-northeast-2', 'ap-northeast-1', 
            'sa-east-1', 'ca-central-1', 'ap-southeast-1', 'ap-southeast-2', 'eu-central-1',
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2' ]
    if value in regs:
        return value
    else:
        click.echo(click.UsageError("Invalid region."))
        sys.exit(2)

def validate_config(data):
    """
        Make sure we have the keys we need in the json file
    """
    if 'inhibit' in data.keys() and 'force_desinhibit' in data.keys():
        for k in ['inhibit', 'force_desinhibit']:
            if not isinstance(data[k], (list, tuple)):
                click.echo(click.UsageError("These keys are supposed to carry lists."))
                return False
        return True
    else:
        click.echo(click.UsageError("Misformed json."))
        return False

def check_json(data, name):
    """
        Check if 'name' should be inhibited according to json 'data'
        return bool True if the box should go down
    """
    for force in data['force_desinhibit']:
        if force in name:
            return True
    for inhib in data['inhibit']:
        if inhib in name:
            return False
    return True

@click.group()
@click.option('--conf', '-c', help="Path to the JSON config",
              type=click.File('r'))
@click.option('--region', help="AWS region to work with",
              type=click.STRING, callback=validate_region,
              default="eu-central-1" )
@click.option('--profile', help="AWS profile to work with",
              type=click.STRING, default="default" )
@click.pass_context
def main(ctx, region, profile, conf):
    ctx.obj['REGION'] = region
    ctx.obj['PROFILE'] = profile
    if conf:
        try:
            json_data = json.load(conf)
        except ValueError:
            click.echo(click.UsageError("Failed to decode the JSON table."))
            sys.exit(3)
            
        if(validate_config(json_data) is False):
            sys.exit(3)
    else: # no file given.
        json_data = { "inhibit": [], "force_desinhibit": [] }
    ctx.obj['JSON'] = json_data

@main.command()
@click.argument('pattern', nargs=1, type=click.STRING)
@click.pass_context
def start(ctx, pattern):
    sess = boto3.session.Session(profile_name=ctx.obj['PROFILE'], region_name=ctx.obj['REGION'])
    ec2 = sess.resource('ec2')
    for i in ec2.instances.all():
        tags = dict(map(lambda t: (t['Key'], t['Value']), i.tags))
        if pattern in tags['Name'] and i.state['Code'] == 80:
            if check_json(ctx.obj['JSON'], tags['Name']):
                i.start()
                if i.wait_until_running() is None:
                    click.secho('Startup OK: ' + i.id, fg='green')
                else:
                    click.secho('Startup too long or is failing: ' + i.id, fg='red')
            else:
                click.secho('Not starting (inhibited from config) - ' + tags['Name'], fg='blue')

@main.command()
@click.argument('pattern', nargs=1, type=click.STRING)
@click.pass_context
def stop(ctx, pattern):
    sess = boto3.session.Session(profile_name=ctx.obj['PROFILE'], region_name=ctx.obj['REGION'])
    ec2 = sess.resource('ec2')
    for i in ec2.instances.all():
        tags = dict(map(lambda t: (t['Key'], t['Value']), i.tags))
        if pattern in tags['Name'] and i.state['Code'] == 16:
            if check_json(ctx.obj['JSON'], tags['Name']):
                i.stop()
                if i.wait_until_stopped() is None:
                    click.secho('Stop OK: ' + i.id, fg='green')
                else:
                    click.secho('Stop too long or failing: ' + i.id, fg='red')
            else:
                click.secho('Not stopping (inhibited from config) - ' + tags['Name'], fg='blue')

@main.command()
@click.argument('pattern', nargs=1, type=click.STRING, default='')
@click.pass_context
def status(ctx, pattern):
    sess = boto3.session.Session(profile_name=ctx.obj['PROFILE'], region_name=ctx.obj['REGION'])
    ec2 = sess.resource('ec2')
    for i in ec2.instances.all():
        tags = dict(map(lambda t: (t['Key'], t['Value']), i.tags))
        if pattern in tags['Name']:
            if check_json(ctx.obj['JSON'], tags['Name']):
                if i.state['Code'] == 16:
                    click.secho('Running - ' + tags['Name'], fg='green')
                elif i.state['Code'] == 80:
                    click.secho('Stopped - ' + tags['Name'], fg='red')
                else:
                    click.secho('Unexpected - ' + tags['Name'], fg='yellow')
            else:
                click.secho('Not checking (inhibited from config) - ' + tags['Name'], fg='blue')

main.add_command(start)
main.add_command(stop)
main.add_command(status)

if __name__ == '__main__':
    main( obj = {} )
