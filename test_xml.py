__author__ = 'hades'
from lxml import etree

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
                        [ls.strip() for ls in element.text.strip().split(",")]
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

class  RiskFunction(object):
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

class  RiskXML(object):
    def __init__(self):
        self._risk_type = None
        self._loss_model_name = None
        self._hazard_model_name = None
        self._fragility_model_name = None
        self._statistic = None
        self._quantile_value = None
        self._investigation_time = None
        self._areas = []
        pass


    def dump(self):
        print "Risk type: %s " % self.risk_type
        print "Loss model name: %s " % self.loss_model_name
        print "Hazard model name: %s " % self.hazard_model_name
        print "Fragility model name: %s " % self.fragility_model_name
        print "Investigation time: %s " % self.investigation_time
        print "Statistic: %s " % self.statistic
        print "Quantile value: %s " % self.quantile_value
        for a in self.areas:
            a.dump()
        pass

    @property
    def risk_type(self):
        return self._risk_type
    @risk_type.setter
    def risk_type(self, data):
        self._risk_type = data

    @property
    def loss_model_name(self):
        return self._loss_model_name
    @loss_model_name.setter
    def loss_model_name(self, data):
        self._loss_model_name = data
    
    @property
    def fragility_model_name(self):
        return self._fragility_model_name
    @fragility_model_name.setter
    def fragility_model_name(self, data):
        self._fragility_model_name = data
    
    @property
    def hazard_model_name(self):
        return self._hazard_model_name
    @hazard_model_name.setter
    def hazard_model_name(self, data):
        self._hazard_model_name = data

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
    def investigation_time(self):
        return self._investigation_time
    @investigation_time.setter
    def investigation_time(self, data):
        self._investigation_time = data
    

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


def parse_xml_risk(filename):
    print "Parsing risk: %s" % (filename)
    risk_xml = RiskXML()
    try:
        context = etree.iterparse(filename, events=("start", "end"))
        for event, element in context:
            if event == "start":
                if element.tag == 'arealRiskModel':
                    risk_xml.risk_type = element.get('riskType')
                    risk_xml.loss_model_name = element.get('lossModelName')
                    risk_xml.hazard_model_name = element.get('hazardModelName')
                    risk_xml.fragility_model_name = \
                        element.get('fragilityModelName')
                    risk_xml.statistic = element.get('statistics')
                    risk_xml.investigation_time = \
                        float(element.get('investigationTime'))
                    if risk_xml.statistic == "quantile":
                        risk_xml.quantile_value = \
                            element.get('quantileValue')
                if element.tag == 'riskCurve':
                    rfs_xml = RiskFunction(areaID=element.get("areaID"))
            else:
                if element.tag == 'arealRiskModel':
                    element.clear()
                if element.tag == 'description':
                    risk_xml.description = element.text.strip()
                    element.clear()
                if element.tag == 'riskCurve':
                    risk_xml.areas.append(rfs_xml)
                    element.clear()
                if element.tag == 'poEs':
                    rfs_xml.functions['poEs'] = [float(p) for p in
                                            element.text.strip().split(" ")]
                    element.clear()
                if element.tag == 'losses':
                    rfs_xml.functions['losses'] = [float(p) for p in
                                            element.text.strip().split(" ")]
                    element.clear()
                if element.tag == 'averageRisk':
                    rfs_xml.average_risk =  float(element.text.strip())
                    element.clear()
    except Exception as e:
        print "Error parsing file " + \
              filename +  " : " + str(e)
        raise Exception(str(e))
    return risk_xml





# i_xml = parse_xml_fragility("data/examples/volcanic5yr/FCs/LOC_0001-0010"
#                      "/arealFragilityModel_mean.xml")
#
# i_xml.dump()
# i_xml = parse_xml_fragility("data/examples/volcanic5yr/FCs/LOC_0001-0010"
#                     "/arealFragilityModel_quantile10.xml")
# i_xml.dump()

# l_xml = parse_xml_loss("data/examples/volcanic5yr/LMs/LOC_0001-0010"
#                      "/arealLossModel_mean.xml")
# 
# l_xml.dump()
# l_xml = parse_xml_loss("data/examples/volcanic5yr/LMs/LOC_0001-0010"
#                     "/arealLossModel_quantile10.xml")
# l_xml.dump()

r_xml = parse_xml_risk("data/examples/volcanic5yr/RISKs/LOC_0001-0010"
                     "/arealRiskModel_mean.xml")

r_xml.dump()
r_xml = parse_xml_risk("data/examples/volcanic5yr/RISKs/LOC_0001-0010"
                    "/arealRiskModel_quantile10.xml")
r_xml.dump()