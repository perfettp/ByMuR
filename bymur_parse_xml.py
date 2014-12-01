import bymur_db
import os
import bymur_functions as bf
import sys


def main(*args):
    if (len(args)<2):
        print "Root dir is needed"
        exit(-1)

    dbDetails = {'db_host': '127.0.0.1',
                 'db_port': '3306',
                 'db_user': '***REMOVED***',
                 'db_password': '***REMOVED***',
                 'db_name': '***REMOVED***'
    }
    db=bymur_db.BymurDB(**dbDetails)

    rootdir = args[1]
    print "Scanning directory %s for files" % rootdir

    for root, dirs, files in os.walk(rootdir):
        for file in files:
            if file.startswith("arealRiskModel"):
                r_xml = bf.parse_xml_risk(
                    os.path.relpath(os.path.join(root,file), os.getcwd()))
                db.add_risk(r_xml)
            elif file.startswith("arealLossModel"):
                l_xml = bf.parse_xml_loss(
                    os.path.relpath(os.path.join(root, file), os.getcwd()))
                db.add_loss(l_xml)

            elif file.startswith("arealFragilityModel"):
                f_xml = bf.parse_xml_fragility(
                    os.path.relpath(os.path.join(root, file), os.getcwd()))
                db.add_fragility(f_xml)


if __name__ == "__main__":
    main(*sys.argv)