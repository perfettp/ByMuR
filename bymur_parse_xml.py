from lxml import etree
import bymur_db
import os
import bymur_functions as bf
import sys


class  LossFunction(object):
    def __init__(self, areaID=None):
        self._areaID = areaID
        self._functions = dict()

    def dump(self):
        print "AreaID: %s" % self.areaID
        print "Functions: %s" % self.functions

    @property
    def areaID(self):
        return self._areaID
    @areaID.setter
    def areaID(self, data):
        self._areaID = data

    @property
    def functions(self):
        return self._functions
    @functions.setter
    def functions(self, data):
        self._functions = data


class  LossXML(object):
    def __init__(self):
        self._loss_type = None
        self._hazard_type = None
        self._model_name = None
        self._statistic = None
        self._quantile_value = None
        self._unit = None
        self._areas = []
        pass

    def dump(self):
        print "Loss type: %s " % self.loss_type
        print "Model name: %s " % self.model_name
        print "Statistic: %s " % self.statistic
        print "Quantile value: %s " % self.quantile_value
        print "Unit: %s " % self.unit
        for a in self.areas:
            a.dump()
        pass

    @property
    def loss_type(self):
        return self._loss_type
    @loss_type.setter
    def loss_type(self, data):
        self._loss_type = data
        
    @property
    def hazard_type(self):
        return self._hazard_type
    @hazard_type.setter
    def hazard_type(self, data):
        self._hazard_type = data

    @property
    def model_name(self):
        return self._model_name
    @model_name.setter
    def model_name(self, data):
        self._model_name = data
        
    @property
    def statistic(self):
        return self._statistic
    @statistic.setter
    def statistic(self, data):
        self._statistic = data
    
    @property
    def quantile_value(self):
        return self._quantile_value
    @quantile_value.setter
    def quantile_value(self, data):
        self._quantile_value = float(data)

    @property
    def unit(self):
        return self._unit
    @unit.setter
    def unit(self, data):
        self._unit = data

    @property
    def areas(self):
        return self._areas
    @areas.setter
    def areas(self, data):
        self._areas = data
        
    # @property
    # def [var](self):
    #     return self._[var]
    # @[var].setter
    # def [var](self, data):
    #     self._[var] = data


def parse_xml_loss(filename):
    print "Parsing loss: %s" % (filename)
    loss_xml = LossXML()
    try:
        context = etree.iterparse(filename, events=("start", "end"))
        for event, element in context:
            if event == "start":
                if element.tag == 'arealLossModel':
                    loss_xml.loss_type = element.get('lossType')
                    loss_xml.hazard_type = element.get('hazardType')
                    loss_xml.model_name = element.get('modelName')
                    loss_xml.unit = element.get('unit')
                    loss_xml.statistic = element.get('statistics')
                    if loss_xml.statistic == "quantile":
                        loss_xml.quantile_value = \
                            element.get('quantileValue')
                if element.tag == 'lossCurve':
                    lfs_xml = LossFunction(areaID=element.get("areaID"))
                if element.tag == 'limitStateCurve':
                    cur_ls = element.get("ls")
                    if cur_ls not in lfs_xml.functions.keys():
                        lfs_xml.functions[cur_ls] = dict()
                if element.tag == 'poEs':
                    lfs_xml.functions[cur_ls]['poEs'] = []
                if element.tag == 'losses':
                    lfs_xml.functions[cur_ls]['losses'] = []
            else:
                if element.tag == 'arealLossModel':
                    element.clear()
                if element.tag == 'description':
                    loss_xml.description = element.text.strip()
                    element.clear()
                if element.tag == 'lossCurve':
                    loss_xml.areas.append(lfs_xml)
                    element.clear()
                if element.tag == 'poEs':
                    lfs_xml.functions[cur_ls]['poEs'] = [float(p) for p in
                                                element.text.strip().split(" ")]
                    element.clear()
                if element.tag == 'losses':
                    lfs_xml.functions[cur_ls]['losses'] = [float(p) for p in
                                                element.text.strip().split(" ")]
                    element.clear()

    except Exception as e:
        print "Error parsing file " + \
              filename +  " : " + str(e)
        raise Exception(str(e))
    return loss_xml



# f_xml.dump()
# f_xml = parse_xml_fragility("data/examples/volcanic5yr/FCs/LOC_0001-0010"
#                     "/arealFragilityModel_quantile10.xml")
# f_xml.dump()

# l_xml = parse_xml_loss("data/examples/volcanic5yr/LMs/LOC_0001-0010"
#                      "/arealLossModel_mean.xml")
#
# l_xml.dump()
# # l_xml = parse_xml_loss("data/examples/volcanic5yr/LMs/LOC_0001-0010"
# #                     "/arealLossModel_quantile10.xml")
# l_xml = parse_xml_loss("/tmp/arealLossModel_mean.xml")
# # l_xml.dump()
# for a in l_xml.areas:
#     # print a.functions
#     if 'Severe' in a.functions.keys():
#         if len(a.functions['Severe']['losses']) !=\
#                 len(a.functions['Severe']['poEs']):
#             raise(Exception("LUNGHEZZA DIVERSA"))
#         else:
#             print "ok"
# l_xml.dump()

# r_xml = parse_xml_risk("data/examples/volcanic5yr/RISKs/LOC_0001-0010"
#                      "/arealRiskModel_mean.xml")
#
# r_xml.dump()
# r_xml = parse_xml_risk("data/examples/volcanic5yr/RISKs/LOC_0001-0010"
#                     "/arealRiskModel_quantile10.xml")
# r_xml.dump()





# print i_xml.classes

# i_xml = parse_xml_inventory("data/InventoryByMuR.xml")
# i_xml.dump()
# db.add_inventory(i_xml, 6)

# f_xml = parse_xml_fragility("/hades/dev/bymur-data/definitivi/risk/seismic50yr"
#                             "/FCs/LOC_0001-0010/arealFragilityModel_mean.xml" )
# db.add_fragility(f_xml)

# l_xml = parse_xml_loss("/hades/dev/bymur-data/definitivi/risk/volcanic50yr"
#                          "/LMs/LOC_0011-0020/arealLossModel_quantile10.xml")
# db.add_loss(l_xml)

# r_xml = parse_xml_risk("/hades/dev/bymur-data/definitivi/risk/volcanic50yr"
#                        "/RISKs/LOC_0011-0020/arealRiskModel_quantile10.xml")
# db.add_risk(r_xml)




# files_array=[]

# for root, dirs, files in os.walk(rootdir):
#     for file in files:
#         if file.startswith("arealFragilityModel"):
#             f_xml = parse_xml_fragility(os.path.relpath(os.path.join(root,file),
#                                                         os.getcwd()))
#             db.add_fragility(f_xml)

# for root, dirs, files in os.walk(rootdir):
#     for file in files:
#         if file.startswith("arealLossModel"):
#             l_xml = parse_xml_loss(os.path.relpath(os.path.join(root,file),
#                                                    os.getcwd()))
#             db.add_loss(l_xml)


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
            # elif file.startswith("arealLossModel"):
            #     l_xml = bf.parse_xml_loss(
            #         os.path.relpath(os.path.join(root, file), os.getcwd()))
            #     # db.add_loss(l_xml)
            elif file.startswith("arealFragilityModel"):
                f_xml = bf.parse_xml_fragility(
                    os.path.relpath(os.path.join(root, file), os.getcwd()))
                f_xml.dump()
                db.add_fragility(f_xml)


if __name__ == "__main__":
    main(*sys.argv)