import sys
import boto3
import click

def validate_region(ctx, param, value):
    regs = [ 'ap-south-1', 'eu-west-2', 'eu-west-1', 'ap-northeast-2', 'ap-northeast-1', 
            'sa-east-1', 'ca-central-1', 'ap-southeast-1', 'ap-southeast-2', 'eu-central-1',
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2' ]
    if value in regs:
        return value
    else:
        click.echo(click.UsageError("Invalid region."))
        sys.exit(2)

@click.group()
@click.option('--region', help="AWS region to work with",
              type=click.STRING, callback=validate_region,
              default="eu-central-1" )
@click.option('--profile', help="AWS profile to work with",
              type=click.STRING, default="default" )
@click.pass_context
def main(ctx, region, profile):
    ctx.obj['REGION'] = region
    ctx.obj['PROFILE'] = profile

@main.command()
def start():
    click.echo('start the boxes')

@main.command()
def stop():
    click.echo('stop the boxes')

@main.command()
@click.argument('pattern', nargs=1)
def status(ctx):
    print ctx.obj['REGION']
    print pattern
    sess = boto3.session.Session(profile_name=ctx.obj['PROFILE'], region_name=ctx.obj['REGION'])
    ec2 = sess.resource(ec2)

    click.echo('status')


main.add_command(start)
main.add_command(stop)
main.add_command(status)

if __name__ == '__main__':
    main(obj = {} )
