import skfuzzy as fuzz
import numpy as np
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import pandas as pd

names =['S1Temp','S2Temp','S3Temp','S1Light','S2Light','S3Light','PIR1','PIR2','Persons','Overcrowded','Slope_CO2','Parts of the day']

df = pd.read_csv('data_preprocessed.csv',usecols=names)

df['AvTemp'] = (df['S1Temp'] + df['S2Temp'])/2
df['AvLight'] = (df['S1Light'] + df['S2Light'] + df['S3Light'])/3
df['AvPIR'] = (df['PIR1'] + df['PIR2'])/2
df = df.round()

print(df)
print(df['AvLight'].max())

#input
#temp_diff   = ctrl.Antecedent(np.arange(0, 101, 1), 'temp_diff')
light = ctrl.Antecedent(np.arange(0, 501, 1), 'light')
pir = ctrl.Antecedent(np.arange(0, 4.5, 0.5), 'pir')
c02_slope = ctrl.Antecedent(np.arange(0, 4.5, 0.5), 'c02_slope')

#output
overcrowded = ctrl.Consequent(np.arange(0, 2, 1), 'overcrowded')


#input membership
#temp_diff['cold'] = fuzz.trimf(temp_diff.universe, [0, 0, 50])
#temp_diff['warm'] = fuzz.trimf(temp_diff.universe, [30, 50, 70])
#temp_diff['hot'] = fuzz.trimf(temp_diff.universe,  [50, 100, 100])

light['low'] = fuzz.trapmf(light.universe, [0, 0, 90,110])
light['medium_low'] = fuzz.trapmf(light.universe, [90, 110, 190,210])
light['medium_high'] = fuzz.trapmf(light.universe, [190, 210, 340,360])
light['high'] = fuzz.trapmf(light.universe, [340, 360, 500,500])

#c02_slope['cold'] = fuzz.trimf(c02_slope.universe, [0, 0, 50])
#c02_slope['warm'] = fuzz.trimf(c02_slope.universe, [30, 50, 70])
#c02_slope['hot'] = fuzz.trimf(c02_slope.universe, [50, 100, 100])

#pir['low'] = fuzz.trimf(pir.universe, [0, 0, 50])
#pir['high'] = fuzz.trimf(pir.universe, [30, 50, 70])

#output membership
overcrowded['false'] = fuzz.trimf(overcrowded.universe, [0, 0, 1])
overcrowded['true'] = fuzz.trimf(overcrowded.universe, [0, 1, 1])



#view membership
#temp_diff.view()
#light.view()
#pir.view()
#c02_slope.view()
#overcrowded.view()
#plt.show()

############# rules
rule1 = ctrl.Rule(light['low'], overcrowded['false'])
rule2 = ctrl.Rule(light['medium_low'], overcrowded['false'])
rule3 = ctrl.Rule(light['medium_high'], overcrowded['false'])
rule4 = ctrl.Rule(light['high'], overcrowded['true'])

#rule1.view()
#plt.show()


overcrowded_ctrl = ctrl.ControlSystem([rule1, rule2, rule3,rule4])

over = ctrl.ControlSystemSimulation(overcrowded_ctrl)

# Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
# Note: if you like passing many inputs all at once, use .inputs(dict_of_data)
#over.input['temp_diff'] = 6.5

df['est_overcrowded'] = np.nan

for index,row in df.iterrows():

    over.input['light'] = row['AvLight']
    #over.input['pir'] = 6.5
    #over.input['c02_slope'] = 9.8

    #Crunch the numbers
    over.compute()
    df.iloc[index,15] = over.output['overcrowded'].round()

print(df)

#check TP fp fn tn
df['tp'] = np.where((df['Overcrowded'] == 1) & (df['est_overcrowded'] == 1), 1, 0)
df['fp'] = np.where((df['Overcrowded'] == 0) & (df['est_overcrowded'] == 1), 1, 0)
df['fn'] = np.where((df['Overcrowded'] == 1) & (df['est_overcrowded'] == 0), 1, 0)
df['tn'] = np.where((df['Overcrowded'] == 0) & (df['est_overcrowded'] == 0), 1, 0)

tp = df['tp'].sum()
fp = df['fp'].sum()
fn = df['fn'].sum()
tn = df['tn'].sum()



accuracy = (tp+tn)/(tp+fp+fn+tn)
precision = tp/(tp+fp)   
recall = tp/(tp+fn)
specificity = tn/(tn+fp)

print(f"accuracy: {accuracy}")
print(f"precision: {precision}")
print(f"recall: {recall}")
print(f"specificity: {specificity}")