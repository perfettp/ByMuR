__author__ = 'hades'
from lxml import etree
import bymur_db
import os
import bymur_functions as bf
import sys


class InventoryClass(object):
    def __init__(self, type='', name='', label=''):
        self._name = name
        self._label = label
        self._type = type
        pass

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, data):
        self._name = data

    @property
    def label(self):
        return self._label
    @label.setter
    def label(self, data):
        self._label = data

    @property
    def type(self):
        return self._type
    @type.setter
    def type(self, data):
        self._type = data

class InventoryGeneralClass(InventoryClass):
    pass

class InventoryAgeClass(InventoryClass):
    pass

class InventoryHouseClass(InventoryClass):
    pass

class InventoryPhenClass(InventoryClass):
    def __init__(self, phenomenon = None, **kwargs):
        self._phenomenon = phenomenon
        super(InventoryPhenClass, self).__init__(**kwargs)
        pass

    @property
    def phenomenon(self):
        return self._phenomenon
    @phenomenon.setter
    def phenomenon(self, data):
        self._phenomenon = data
    pass

class InventoryFragilityClass(InventoryPhenClass):
    pass

class InventoryCostClass(InventoryPhenClass):
    pass

class InventoryFragilityClass(InventoryPhenClass):
    pass


class InventoryAsset(object):
    def __init__(self):
        self._total = None
        self._type = None
        self._counts = dict()
        self._frag_class_prob = dict()
        self._cost_class_prob = dict()
        pass

    def dump(self):
        print "Total: %s" % self.total
        print "Type: %s" % self.type
        for k in self.counts.keys():
            print "Count[%s]: %s" %(k, self.counts[k])
        print "Fragility class Probability: %s " % self.frag_class_prob
        print "Cost class Probability: %s " % self.cost_class_prob

    @property
    def total(self):
        return self._total
    @total.setter
    def total(self, data):
        self._total = int(data)

    @property
    def type(self):
        return self._type
    @type.setter
    def type(self, data):
        self._type = data

    @property
    def counts(self):
        return self._counts
    @counts.setter
    def counts(self, data):
        self._counts = data

    @property
    def frag_class_prob(self):
        return self._frag_class_prob
    @frag_class_prob.setter
    def frag_class_prob(self, data):
        self._frag_class_prob = data

    @property
    def cost_class_prob(self):
        return self._cost_class_prob
    @cost_class_prob.setter
    def cost_class_prob(self, data):
        self._cost_class_prob = data

class InventorySection(object):
    def __init__(self):
        self._geometry = None
        self._centroid = None
        self._areaID = None
        self._sectionID = None
        self._asset = None
        pass

    def dump(self):
        print "AreaID: %s" % self.areaID
        print "SectionID: %s" % self.sectionID
        print "Centroid: %s" % self.centroid
        print "Geometry: %s" % self.geometry
        if self.asset is not None:
            self.asset.dump()

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, data):
        self._geometry = data

    @property
    def centroid(self):
        return self._centroid

    @centroid.setter
    def centroid(self, data):
        self._centroid = data

    @property
    def areaID(self):
        return self._areaID

    @areaID.setter
    def areaID(self, data):
        self._areaID = data

    @property
    def sectionID(self):
        return self._sectionID

    @sectionID.setter
    def sectionID(self, data):
        self._sectionID = data

    @property
    def asset(self):
        return self._asset

    @asset.setter
    def asset(self, data):
        self._asset = data


class  InventoryXML(object):
    def __init__(self, name = ''):
        self._name = name
        self._sections = []
        self._classes = dict()
        pass

    def dump(self):
        print "Classes: %s" % self.classes
        for sec in self.sections:
            sec.dump()

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, data):
        self._name = data

    @property
    def sections(self):
        return self._sections
    @sections.setter
    def sections(self, data):
        self._sections = data

    @property
    def classes(self):
        return self._classes
    @classes.setter
    def classes(self, data):
        self._classes = data

def parse_xml_inventory(filename):
    print "Parsing Inventory: %s" % (filename)
    try:
        context = etree.iterparse(filename, events=("start", "end"))
        for event, element in context:
            if event == "start":
                if element.tag == 'inventory':
                    inventory_xml = InventoryXML(element.get('Name'))
                elif element.tag == 'sezione':
                    section_model = InventorySection()
                    section_model.areaID = element.get('areaID')
                    section_model.sectionID = element.get('sezioneID')
                elif element.tag == 'classes':
                    classes = dict()
                    class_list = []
                    class_type = element.get('type')
                elif element.tag == 'generalClasses':
                    class_obj_type = 'InventoryGeneralClass'
                elif element.tag == 'ageClasses':
                    class_obj_type = 'InventoryAgeClass'
                elif element.tag == 'houseClasses':
                    class_obj_type = 'InventoryHouseClass'
                elif element.tag == 'fragilityClasses':
                    class_obj_type = 'InventoryFragilityClass'
                    class_obj_phen = element.get('phenomenon')
                elif element.tag == 'costClasses':
                    class_obj_type = 'InventoryCostClass'
                    class_obj_phen = element.get('phenomenon')
                elif element.tag == 'class':
                    label = element.get('label')
                    if label is None:
                        label = ''
                    new_class = eval(class_obj_type)(name = element.get('name'),
                                                label = label)
                    if issubclass(eval(class_obj_type), InventoryPhenClass):
                        new_class.phenomenon = class_obj_phen
                    class_list.append(new_class)
                elif element.tag == 'asset':
                    asset_model = InventoryAsset()
                    asset_model.total = element.get('total')
                    asset_model.type = element.get('type')
                elif element.tag == 'fragClassProb':
                    class_prob_dict = dict()
                    class_prob_phen = element.get('phenomenon')
                elif element.tag == 'costClassProb':
                    class_prob_dict = dict()
                    class_prob_phen = element.get('phenomenon')
            else:
                if element.tag == 'geometry':
                    section_model.geometry = element.text.strip().split(",")
                    element.clear()
                elif element.tag == 'centroid':
                    section_model.centroid = element.text.strip().split(" ")
                    element.clear()
                elif element.tag == 'asset':
                    section_model.asset = asset_model
                    asset_model = None
                    element.clear()
                elif element.tag == 'genClassCount':
                    asset_model.counts['genClassCount'] =\
                        element.text.strip().split(" ")
                elif element.tag == 'ageClassCount':
                    asset_model.counts['ageClassCount'] =\
                        element.text.strip().split(" ")
                elif element.tag == 'houseClassCount':
                    asset_model.counts['houseClassCount'] =\
                        element.text.strip().split(" ")
                elif element.tag == 'fragClassProb':
                    asset_model.frag_class_prob.update(
                        {class_prob_phen: class_prob_dict})
                    class_prob_phen = ''
                    class_prob_dict = dict()
                    element.clear()
                elif element.tag == 'costClassProb':
                    asset_model.cost_class_prob.update(
                        {class_prob_phen: class_prob_dict})
                    class_prob_phen = ''
                    class_prob_dict = dict()
                    element.clear()
                elif element.tag == 'fnt':
                    class_prob_dict['fnt'] = element.text.strip().split(" ")
                    element.clear()
                elif element.tag == 'fntGivenGeneralClass':
                    class_prob_dict['fntGivenGeneralClass'] = \
                        [[e for e in cs.strip().split(" ") if e is not '']
                         for cs in element.text.strip().split(",")]
                    element.clear()
                elif element.tag == 'fnc':
                    class_prob_dict['fnc'] = element.text.strip().split(" ")
                    element.clear()
                elif element.tag == 'generalClasses':
                    classes['generalClasses'] = class_list
                    class_list = []
                    element.clear()
                elif element.tag == 'ageClasses':
                    classes['ageClasses'] = class_list
                    class_list = []
                    element.clear()
                elif element.tag == 'houseClasses':
                    classes['houseClasses'] = class_list
                    class_list = []
                    element.clear()
                elif element.tag == 'fragilityClasses':
                    if 'fragilityClasses' not in classes.keys():
                            classes['fragilityClasses'] = dict()
                    classes['fragilityClasses'][class_obj_phen] = class_list
                    class_list = []
                    element.clear()
                elif element.tag == 'costClasses':
                    if 'costClasses' not in classes.keys():
                            classes['costClasses'] = dict()
                    classes['costClasses'][class_obj_phen] = class_list
                    class_list = []
                    element.clear()
                elif element.tag == 'classes':
                    inventory_xml.classes.update(classes)
                    class_list = None
                    element.clear()
                elif element.tag == 'sezione':
                    inventory_xml.sections.append(section_model)
                    section_model = None
                    element.clear()

    except Exception as e:
        print "Error parsing file " + \
              filename +  " : " + str(e)
        raise Exception(str(e))
    return inventory_xml


class  FragilityFunction(object):
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

    # @property
    # def [var](self):
    #     return self._[var]
    # @[var].setter
    # def [var](self, data):
    #     self._[var] = data
        

class  FragilityXML(object):
    def __init__(self):
        self._hazard_type = None
        self._model_name = None
        self._statistic = None
        self._quantile_value = None
        self._description = None
        self._limit_states = None
        self._iml = None
        self._imt = None
        self._areas = []
        pass

    def dump(self):
        print "Hazard type: %s " % self.hazard_type
        print "Model name: %s " % self.model_name
        print "Statistic: %s " % self.statistic
        print "Quantile value: %s " % self.quantile_value
        print "Description: %s " % self.description
        print "Limit states: %s " % self.limit_states
        print "IML: %s " % self.imt
        print "IML: %s " % self.iml
        for a in self.areas:
            a.dump()
        pass

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
    def description(self):
        return self._description
    @description.setter
    def description(self, data):
        self._description = data

    @property
    def limit_states(self):
        return self._limit_states
    @limit_states.setter
    def limit_states(self, data):
        self._limit_states = data

    @property
    def imt(self):
        return self._imt
    @imt.setter
    def imt(self, data):
        self._imt = data
        
    @property
    def iml(self):
        return self._iml
    @iml.setter
    def iml(self, data):
        self._iml = data
    
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


def parse_xml_fragility(filename):
    print "Parsing fragility: %s" % (filename)
    fragility_xml = FragilityXML()
    try:
        context = etree.iterparse(filename, events=("start", "end"))
        for event, element in context:
            if event == "start":
                if element.tag == 'arealFragilityModel':
                    fragility_xml.hazard_type = element.get('hazardType')
                    fragility_xml.model_name = element.get('modelName')
                    fragility_xml.statistic = element.get('statistics')
                    if fragility_xml.statistic == "quantile":
                        fragility_xml.quantile_value = \
                            element.get('quantileValue')
                if element.tag == 'IML':
                    fragility_xml.imt= element.get("IMT")
                if element.tag == 'ffs':
                    ffs_xml = FragilityFunction(areaID=element.get("areaID"))
                if element.tag == 'taxonomy':
                    cur_cat = element.get("categoryName")
                    if cur_cat not in ffs_xml.functions.keys():
                        ffs_xml.functions[cur_cat] = dict()
                if element.tag == 'ffd':
                    cur_ls = element.get("ls")
                    if cur_ls not in ffs_xml.functions[cur_cat].keys():
                        ffs_xml.functions[cur_cat][cur_ls] = []
            else:
                if element.tag == 'arealFragilityModel':
                    element.clear()
                if element.tag == 'description':
                    fragility_xml.description = element.text.strip()
                    element.clear()
                if element.tag == 'limitStates':
                    fragility_xml.limit_states = \
                        [ls.strip() for ls in element.text.strip().split(" ")]
                    element.clear()
                if element.tag == 'IML':
                    fragility_xml.iml = [float(i) for i in
                                         element.text.strip().split(" ")]
                    element.clear()
                if element.tag == 'ffs':
                    fragility_xml.areas.append(ffs_xml)
                    element.clear()
                if element.tag == 'taxonomy':
                    element.clear()
                if element.tag == 'ffd':
                    element.clear()
                if element.tag == 'poEs':
                    ffs_xml.functions[cur_cat][cur_ls] = [float(p) for p in
                                                element.text.strip().split(" ")]
                    element.clear()

    except Exception as e:
        print "Error parsing file " + \
              filename +  " : " + str(e)
        raise Exception(str(e))
    return fragility_xml


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

    # @property
    # def [var](self):
    #     return self._[var]
    # @[var].setter
    # def [var](self, data):
    #     self._[var] = data

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
            # elif file.startswith("arealFragilityModel"):
            #     f_xml = bf.parse_xml_fragility(
            #         os.path.relpath(os.path.join(root, file), os.getcwd()))
            #     # db.add_fragility(r_xml)


if __name__ == "__main__":
    main(*sys.argv)