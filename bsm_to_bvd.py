#!/usr/bin/python
# bsm_to_bvd.py -pete 2016-10-14


import argparse, sys, StringIO

FORMAT = "%(asctime)s-%(levelname)s: %(message)s"
DATE_FMT= "%Y-%m-%d %H:%M:%S"
MAX_BYTES=5*100*1000
BKUP_CNT=5

LOGGING_LEVELS = {
    "CRITICAL":50,
    "ERROR":40,
    "WARNING":30,
    "INFO":20,
    "DEBUG":10,
    "NOTSET":0
}

description="Pulls data from BSM and posts to BVD instance via HTTP APIs"
epilog='''

Example usage steps:
1) Parse the .svg template using the -parse option and output to file
eg:
    `./bsm_to_bvd.py -parse \\
        --input test_app_status.svg \\
        --bsm-url http://bsm.your.domain \\
        --login User \\
        --output PROD.svg \\
        --title PROD`

2) Use the -all option which will (1) parse Ids in the input SVG, then (2) get
statuses from BSM, then (3) post status to BVD
eg:
    `./bsm_to_bvd.py -all \\
        --input PROD.svg \\
        --bsm-url http://bsm.your.domain \\
        --login User \\
        --bvd-url http://bvd.your.domain \\
        --key <bvd key>`
'''

parser = argparse.ArgumentParser(
    description=description,
    epilog=epilog,
    formatter_class=argparse.RawDescriptionHelpFormatter
)

parser.add_argument('--login', '-u', default="admin")
parser.add_argument('--password', '-p', default="admin")
parser.add_argument('--svg-title', '-t', default="intg", help="Heading in SVG output")
parser.add_argument('--input', '-i', default=sys.stdin, help="input file")
parser.add_argument('--output', '-o', default=sys.stdout, help="output file")
parser.add_argument('--bsm-url', '-bsm', default="http://localhost/", help="BSM url")
parser.add_argument('--bvd-url', '-bvd', default="http://localhost:12224/", help="BVD url")
parser.add_argument('--key', '-k', default="0", help="BVD api key")
parser.add_argument('--log', help="logfile to write to. writes to stdout if left blank")
parser.add_argument('--loglevel', default="INFO", help="logfile level")


group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-statuses', '-stat', action='store_true', help='pull CI statuses')
group.add_argument('-definitions', '-def', action='store_true', help='pull CI definitions')
group.add_argument('-all', action='store_true', help='pulls statuses from BSM and posts to BVD')
group.add_argument('-parse', action='store_true', help='parse svg file and insert CI names and ids')
group.add_argument('-find', action='store_true', help='parse svg file and find the CI ids')
group.add_argument('-post', action='store_true', help='post data to BVD')

args = parser.parse_args()



# Input/Output
if hasattr(args.input, 'read'): 
    input_fileh = args.input
else: input_fileh = open(args.input, "rb")
if hasattr(args.output, 'write'): 
    output_fileh = args.output
else: output_fileh = open(args.output, "wb")



# Username/Password
if args.login!="admin" and args.password=="admin":
    import getpass
    args.password = getpass.getpass('Password:')
    
    


# Choose actions
if args.statuses:
    import get_bvd
    get_bvd.get_status(args.login, args.password, args.bsm_url, input_fileh, output_fileh)
    
elif args.definitions:
    import get_bvd
    get_bvd.get_status_definitions(args.login, args.password, args.bsm_url)
    
    
elif args.parse:
    import parse_bvd
    parse_bvd.mod_svg(args.login, args.password, args.svg_title, args.bsm_url, input_fileh, output_fileh)
    
    
elif args.find:
    import parse_bvd
    parse_bvd.parse_svg(input_fileh, output_fileh)
    

elif args.post:
    import post_bvd
    post_bvd.post_bvd(input_fileh, output_fileh, args.key, args.bvd_url)
    

elif args.all:
    import get_bvd, post_bvd, parse_bvd
    import logging
    from logging import handlers
    
    # Setup logging
    L = logging.getLogger()
    
    if args.log:
        handler = handlers.RotatingFileHandler(
            args.log,
            mode = "a",
            encoding = "UTF-8",
            maxBytes = MAX_BYTES,
            backupCount = BKUP_CNT
        )
    else:
        handler = logging.StreamHandler(output_fileh)
        
    formatter = logging.Formatter(fmt=FORMAT, datefmt=DATE_FMT)
    handler.setFormatter(formatter)
    L.setLevel(LOGGING_LEVELS.get(args.loglevel, LOGGING_LEVELS["INFO"]))
    L.addHandler(handler)
    
    
    
    L.info("Starting update with {}".format(args))
    
    try:
        # Parse Ids
        fh1 = StringIO.StringIO()
        parse_bvd.parse_svg(input_fileh, fh1)
        fh1.seek(0)
        
        # Get status
        fh2 = StringIO.StringIO()
        get_bvd.get_status(args.login, args.password, args.bsm_url, fh1, fh2)
        fh2.seek(0)
        
        # Post to BVD
        fh3 = StringIO.StringIO()
        post_bvd.post_bvd(fh2, fh3, args.key, args.bvd_url)
        fh3.seek(0)
        
        output = fh3.readlines()    
        L.info("Finished updated with {}".format(output))
    
    except Exception, e:
        L.error("Error: {}".format(e))
    

    
    