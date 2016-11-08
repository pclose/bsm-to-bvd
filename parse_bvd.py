#!/usr/bin/python
# Parses SVG looking for the BVD hooks -pete 2016-10-09

from lxml import etree
import sys,getpass,re

FMT_VISIO = "VT4(eum <> Application Availability <> {})"
FMT_BVD = "eum <> Application Availability <> {}"
#channel_regex = "VT4\(eum <> Application Availability <> (.*?)\)"
CHAN_REGEX = "VT4\(eum <> Application Availability <> (.*?)\)"
CI_MAX_CHAR = 26

NS  = { 'svg': 'http://www.w3.org/2000/svg',
        'v': 'http://schemas.microsoft.com/visio/2003/SVGExtensions/'}
        
BVD_ATTR = {
    "opr_channel":         FMT_BVD,
    "opr_dashboard_item":  "1",
    "opr_switch_default":  "No Data",
    "opr_channel_vars":    "",
    "opr_item_type":       "opr_update_images",
    "opr_status":          "status",
}

def mod_svg(username, password, svg_title, bsm_url, infileh, outfileh):
    
    import get_bvd
    new_data = get_bvd.get_ci_info(username, password, bsm_url, CI_MAX_CHAR)
    
    if len(new_data) == 0: 
        raise Exception("ERROR: No application information found")
        return
    
    counter = 0
    title_found = False
    
    e = etree.parse(infileh)
    
    # Loop through every SVG element
    start = e.find('./svg:g', NS)
    for i in start:
    
        # Find title element
        if not title_found:
            title = i.find(".//*[@v:lbl='istitle']", NS)
            if title is not None: 
                i.find(".//v:tabList", NS).tail = svg_title.upper() + " BSM Application Status Page"
            
        # Find elements with opr_channel attribute (v:nameU="opr_channel")
        prop = i.find(".//*[@v:nameU='opr_channel']", NS)
        if prop is not None:
            
            # Set channel variables
            for ii in BVD_ATTR:
                if ii == "opr_channel":
                    i.set("{%s}%s" % (NS['svg'], BVD_ATTR[ii][0]), BVD_ATTR[ii][1].format(new_data[counter][0]))
                else:
                    i.set("{%s}%s" % (NS['svg'], ii), BVD_ATTR[ii])    
            
            # Set value to unique CI id (v:val="VT4(<id>)")
            prop.set("{%s}val" % NS['v'], FMT_VISIO.format(new_data[counter][0]))
            #prop.set("{%s}val" % NS['v'], "VT4()")
            
            # Set text element to CI name
            i.find(".//v:tabList", NS).tail = new_data[counter][1]
            
            if counter < len(new_data)-1: counter+=1
    
    # Save modified xml document to file
    e.write(outfileh)
    
def parse_svg(inputfh, outfileh):
        
    _re = re.compile(CHAN_REGEX)
    e = etree.parse(inputfh)
    start = e.find('./svg:g', NS)
    for i in start:
        prop = i.find(".//*[@v:nameU='opr_channel']", NS)
        if prop is not None:
            ciid = _re.match(prop.get("{%s}val" % NS['v'])).groups()[0]
            name = i.find(".//v:tabList", NS).tail
            print >>outfileh, ciid, name
    
if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] != "": username = sys.argv[2]
    else: username = raw_input("Username: ")
    if len(sys.argv) > 3 and sys.argv[3] != "": password = sys.argv[3]
    else: password = getpass.getpass("Password for {}: ".format(username))
    if len(sys.argv) > 4: mod_svg(username, password, sys.argv[4])
    else: mod_svg(username, password, "intg")
    