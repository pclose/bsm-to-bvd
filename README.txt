usage: bsm_to_bvd.py [-h] [--login LOGIN] [--password PASSWORD]
                     [--svg-title SVG_TITLE] [--input INPUT] [--output OUTPUT]
                     [--bsm-url BSM_URL] [--bvd-url BVD_URL] [--key KEY]
                     [--log LOG] [--loglevel LOGLEVEL]
                     (-statuses | -definitions | -all | -parse | -find | -post)

Pulls data from BSM and posts to BVD instance via HTTP APIs

optional arguments:
  -h, --help            show this help message and exit
  --login LOGIN, -u LOGIN
  --password PASSWORD, -p PASSWORD
  --svg-title SVG_TITLE, -t SVG_TITLE
                        Heading in SVG output
  --input INPUT, -i INPUT
                        input file
  --output OUTPUT, -o OUTPUT
                        output file
  --bsm-url BSM_URL, -bsm BSM_URL
                        BSM url
  --bvd-url BVD_URL, -bvd BVD_URL
                        BVD url
  --key KEY, -k KEY     BVD api key
  --log LOG             logfile to write to. writes to stdout if left blank
  --loglevel LOGLEVEL   logfile level
  -statuses, -stat      pull CI statuses
  -definitions, -def    pull CI definitions
  -all                  pulls statuses from BSM and posts to BVD
  -parse                parse svg file and insert CI names and ids
  -find                 parse svg file and find the CI ids
  -post                 post data to BVD

Example usage steps:
1) Parse the .svg template using the -parse option and output to file
eg:
    `./bsm_to_bvd.py -parse \
        --input test_app_status.svg \
        --bsm-url http://bsm.your.domain \
        --login User \
        --output PROD.svg \
        --title PROD`

2) Use the -all option which will (1) parse Ids in the input SVG, then (2) get
statuses from BSM, then (3) post status to BVD
eg:
    `./bsm_to_bvd.py -all \
        --input PROD.svg \
        --bsm-url http://bsm.your.domain \
        --login User \
        --bvd-url http://bvd.your.domain \
        --key <bvd key>`
