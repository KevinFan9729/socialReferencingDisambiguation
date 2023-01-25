# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 11:51:50 2022

@author: Kevin
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class AmbiguityFuzzy():
    def __init__(self):
        self.objConf = ctrl.Antecedent(np.arange(0, 1.05, 0.05), 'object confidence')
        self.objectCount = ctrl.Antecedent(np.arange(0, 7.05, 0.05), 'detected object count')
        self.ambiguity = ctrl.Consequent(np.arange(0, 1.05, 0.05), 'ambiguity level')
        self.ambiguityCtrl = None
        self.ambiguityLvl = None
        self._fuzzy_build()

    def _fuzzy_build(self):
        #object confidence membership function
        # self.objConf['vLow'] = fuzz.trimf(self.objConf.universe, [0, 0, 0.25])#left point, middle point, rigt point
        # self.objConf['low'] = fuzz.trimf(self.objConf.universe, [0, 0.25, 0.5])
        # self.objConf['med'] = fuzz.trimf(self.objConf.universe, [0.25, 0.5, 0.75])
        # self.objConf['high'] = fuzz.trimf(self.objConf.universe, [0.5, 0.75, 1])
        # self.objConf['vHigh'] = fuzz.trimf(self.objConf.universe, [0.75, 1, 1])

        #Gaussian membership
        self.objConf['vLow'] = fuzz.gaussmf(self.objConf.universe, 0, 0.1)
        self.objConf['low'] = fuzz.gaussmf(self.objConf.universe, 0.25,0.1)
        self.objConf['med'] = fuzz.gaussmf(self.objConf.universe, 0.5,0.1)
        self.objConf['high'] = fuzz.gaussmf(self.objConf.universe, 0.75,0.1)
        self.objConf['vHigh'] = fuzz.gaussmf(self.objConf.universe, 1,0.1)

        #detected object count membership function
        self.objectCount['noObj'] = fuzz.trimf(self.objectCount.universe, [0, 0, 1])
        self.objectCount['one'] = fuzz.trimf(self.objectCount.universe, [0.95, 1, 1.05])
        self.objectCount['two'] = fuzz.trimf(self.objectCount.universe, [1, 2, 3])
        self.objectCount['more'] = fuzz.trapmf(self.objectCount.universe, [2,3,7,7])

        #ambiguity level membership function
        # self.ambiguity['vLow'] = fuzz.trimf(self.ambiguity.universe, [0, 0, 0.25])
        # self.ambiguity['low'] = fuzz.trimf(self.ambiguity.universe, [0, 0.25, 0.5])
        # self.ambiguity['med'] = fuzz.trimf(self.ambiguity.universe, [0.25, 0.5, 0.75])
        # self.ambiguity['high'] = fuzz.trimf(self.ambiguity.universe, [0.5, 0.75, 1])
        # self.ambiguity['vHigh'] = fuzz.trimf(self.ambiguity.universe, [0.75, 1, 1])

        #Gaussian membership
        self.ambiguity['vLow'] = fuzz.gaussmf(self.ambiguity.universe, 0, 0.1)
        self.ambiguity['low'] = fuzz.gaussmf(self.ambiguity.universe,  0.25,0.1)
        self.ambiguity['med'] = fuzz.gaussmf(self.ambiguity.universe, 0.5,0.1)
        self.ambiguity['high'] = fuzz.gaussmf(self.ambiguity.universe, 0.75,0.1)
        self.ambiguity['vHigh'] = fuzz.gaussmf(self.ambiguity.universe, 1,0.1)

        # objectCount.view()

        #fuzzy rules
        rule1 = ctrl.Rule(((self.objConf['vLow'] | self.objConf['low']) &
                           (self.objectCount['noObj']|self.objectCount['two']|self.objectCount['more'])),
                          (self.ambiguity['vHigh'] ,self.ambiguity['high']) )

        rule2 = ctrl.Rule(((self.objConf['vLow'] | self.objConf['low']) &
                           (self.objectCount['one'])),
                          (self.ambiguity['high']))

        rule3 = ctrl.Rule(((self.objConf['low'] | self.objConf['med']) &
                           (self.objectCount['two']|self.objectCount['more'])),
                          (self.ambiguity['high']))

        rule4 = ctrl.Rule(((self.objConf['low'] | self.objConf['med']) &
                           (self.objectCount['one'])),
                          (self.ambiguity['high'], self.ambiguity['med']))

        rule5 = ctrl.Rule(((self.objConf['med'] | self.objConf['high']) &
                           (self.objectCount['two'] | self.objectCount['more'])),
                          (self.ambiguity['med']))

        rule6 = ctrl.Rule(((self.objConf['med'] | self.objConf['high']) &
                           (self.objectCount['one'])),
                          (self.ambiguity['low']))

        rule7 = ctrl.Rule(((self.objConf['high'] | self.objConf['vHigh']) &
                           (self.objectCount['two'] | self.objectCount['more'])),
                          (self.ambiguity['med']))

        rule8 = ctrl.Rule(((self.objConf['high'] | self.objConf['vHigh']) &
                           (self.objectCount['one'])),
                          (self.ambiguity['vLow']))
        self.ambiguityCtrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8])
        self.ambiguityLvl = ctrl.ControlSystemSimulation(self.ambiguityCtrl)

    def determine(self, confidence, count):
        # print("hello")
        self.ambiguityLvl.input['object confidence'] = confidence
        self.ambiguityLvl.input['detected object count'] = count
        self.ambiguityLvl.compute()
        ambiguity=self.ambiguityLvl.output['ambiguity level']
        print(ambiguity)
        return ambiguity



# ambiguityLvl.compute()
# print(ambiguityLvl.output['ambiguity level'])
# objConf.view(sim=ambiguityLvl)
# objectCount.view(sim=ambiguityLvl)
# ambiguity.view(sim=ambiguityLvl)
