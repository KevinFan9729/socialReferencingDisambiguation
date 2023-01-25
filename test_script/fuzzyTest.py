# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 11:51:50 2022

@author: Kevin
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


objConf = ctrl.Antecedent(np.arange(0, 1.05, 0.05), 'object confidence')
objectCount = ctrl.Antecedent(np.arange(0, 7.05, 0.05), 'detected object count')
ambiguity = ctrl.Consequent(np.arange(0, 1.05, 0.05), 'ambiguity level')

#object confidence membership function
objConf['vLow'] = fuzz.trimf(objConf.universe, [0, 0, 0.25])#left point, middle point, rigt point
objConf['low'] = fuzz.trimf(objConf.universe, [0, 0.25, 0.5])
objConf['med'] = fuzz.trimf(objConf.universe, [0.25, 0.5, 0.75])
objConf['high'] = fuzz.trimf(objConf.universe, [0.5, 0.75, 1])
objConf['vHigh'] = fuzz.trimf(objConf.universe, [0.75, 1, 1])

#detected object count membership function
objectCount['noObj'] = fuzz.trimf(objectCount.universe, [0, 0, 1])
objectCount['one'] = fuzz.trimf(objectCount.universe, [0.95, 1, 1.05])
objectCount['two'] = fuzz.trimf(objectCount.universe, [1, 2, 3])
objectCount['more'] = fuzz.trapmf(objectCount.universe, [2,3,7,7])

#ambiguity level membership function
ambiguity['vLow'] = fuzz.trimf(ambiguity.universe, [0, 0, 0.25])
ambiguity['low'] = fuzz.trimf(ambiguity.universe, [0, 0.25, 0.5])
ambiguity['med'] = fuzz.trimf(ambiguity.universe, [0.25, 0.5, 0.75])
ambiguity['high'] = fuzz.trimf(ambiguity.universe, [0.5, 0.75, 1])
ambiguity['vHigh'] = fuzz.trimf(ambiguity.universe, [0.75, 1, 1])

# objectCount.view()

#fuzzy rules
rule1 = ctrl.Rule(((objConf['vLow'] | objConf['low']) &
                   (objectCount['noObj']|objectCount['two']|objectCount['more'])),
                  (ambiguity['vHigh'] ,ambiguity['high']) )

rule2 = ctrl.Rule(((objConf['vLow'] | objConf['low']) &
                   (objectCount['one'])),
                  (ambiguity['high']))

rule3 = ctrl.Rule(((objConf['low'] | objConf['med']) &
                   (objectCount['two']|objectCount['more'])),
                  (ambiguity['high']))

rule4 = ctrl.Rule(((objConf['low'] | objConf['med']) &
                   (objectCount['one'])),
                  (ambiguity['high'], ambiguity['med']))

rule5 = ctrl.Rule(((objConf['med'] | objConf['high']) &
                   (objectCount['two']|objectCount['more'])),
                  (ambiguity['med']))

rule6 = ctrl.Rule(((objConf['med'] | objConf['high']) &
                   (objectCount['one'])),
                  (ambiguity['low']))

rule7 = ctrl.Rule(((objConf['high'] | objConf['vHigh']) &
                   (objectCount['two']|objectCount['more'])),
                  (ambiguity['med']))

rule8 = ctrl.Rule(((objConf['high'] | objConf['vHigh']) &
                   (objectCount['one'])),
                  (ambiguity['vLow']))

ambiguityCtrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8])

#gerenate output
ambiguityLvl = ctrl.ControlSystemSimulation(ambiguityCtrl)

ambiguityLvl.input['object confidence'] = 0.92
ambiguityLvl.input['detected object count'] = 1

ambiguityLvl.compute()
print(ambiguityLvl.output['ambiguity level'])
objConf.view(sim=ambiguityLvl)
objectCount.view(sim=ambiguityLvl)
ambiguity.view(sim=ambiguityLvl)
