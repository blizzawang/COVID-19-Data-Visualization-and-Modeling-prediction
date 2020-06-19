"""
�༶��2019211120
ѧ�ţ�2019210628
������������
���ݣ��¹ڷ�������Ľ�ģԤ��
"""

#ʹ�õĿ�
import numpy as np
import pandas as pd
import math
import datetime
from scipy.integrate import odeint
from scipy.optimize import minimize
import matplotlib.pyplot as plt


#����Ԥ����
Updates_NC = pd.read_csv('Updates_NC.csv')
class preProcess():
    def __init__(self):
        self.wuHan = Updates_NC[Updates_NC['����'] == '�人��']
        wuHanInfection = self.wuHan.groupby('����ʱ��')['����ȷ��'].sum()
        wuHanRecovered = self.wuHan.groupby('����ʱ��')['������Ժ'].sum()
        wuHanDead = self.wuHan.groupby('����ʱ��')['��������'].sum()
        self.wuHan = {'����ʱ��':wuHanInfection.index, '����ȷ��':wuHanInfection.values, '������Ժ': wuHanRecovered.values, '��������':wuHanDead.values}
        self.wuHan = pd.DataFrame(self.wuHan, index = [i for i in range(wuHanInfection.shape[0])])
    
    def getTotal(self):
        wuHanTotalInfection = [self.wuHan.loc[0:i,'����ȷ��'].sum() for i in range(self.wuHan.shape[0])]
        wuHanTotalRecovered = [self.wuHan.loc[0:i,'������Ժ'].sum() for i in range(self.wuHan.shape[0])]
        wuHanTotalDead = [self.wuHan.loc[0:i,'��������'].sum() for i in range(self.wuHan.shape[0])]
        self.wuHan = self.wuHan.join(pd.DataFrame([wuHanTotalInfection,wuHanTotalRecovered ,wuHanTotalDead], index = ['�ۼ�ȷ��', '�ۼƳ�Ժ','�ۼ�����']).T)
        print(self.wuHan)
    
    def removeNoisyData(self):
        self.wuHan = self.wuHan[self.wuHan['����ʱ��'] >= '1��18��']
        self.wuHan.index = [i for i in range(self.wuHan.shape[0])]
        print(self.wuHan)
        
    def report(self):
        plt.plot(self.wuHan.index, self.wuHan['�ۼ�ȷ��'])
        plt.xlabel('Day')
        plt.ylabel('Number of people(Wu Han)')
        plt.show()
        
        
        
#������ʶ
class estimationInfectionProb():
    def __init__(self, estUsedTimeIndexBox, nContact, gamma):
        self.timeRange = np.array([i for i in range(estUsedTimeIndexBox[0],estUsedTimeIndexBox[1] + 1)])
        self.nContact, self.gamma = nContact, gamma
        self.dataStartTimeStep = 41
    
    def setInitSolution(self, x0):
        self.x0 = 0.04
        
    def costFunction(self, infectionProb):
        #print(infectionData.wuHan.loc[self.timeRange - self.dataStartTimeStep,'�ۼ�ȷ��'])
        #print(np.exp((infectionProb * self.nContact - self.gamma) * self.timeRange))
        res = np.array(np.exp((infectionProb * self.nContact - self.gamma) * self.timeRange) - \
                       infectionData.wuHan.loc[self.timeRange - self.dataStartTimeStep,'�ۼ�ȷ��'])
        return (res**2).sum() / self.timeRange.size
    
    def optimize(self):
        self.solution = minimize(self.costFunction, self.x0, method='nelder-mead', options={'xtol': 1e-8, 'disp': True})
        print('infection probaility: ', self.solution.x)
        return self.getSolution()
    
    def getSolution(self):
        return self.solution.x
    
    def getBasicReproductionNumber(self):
        self.basicReproductionNumber = self.nContact * self.solution.x[0] / (self.gamma)
        print("basic reproduction number:", self.basicReproductionNumber)
        return self.basicReproductionNumber
        
#����SIRģ����
class wuHanSIRModel():
    def __init__(self, N, beta, gamma):
        self.beta, self.gamma, self.N = beta, gamma, N
        self.t = np.linspace(0, 360, 361)
        self.setInitCondition()
    
    def odeModel(self, population, t):
        diff = np.zeros(3)
        s,i,r = population
        diff[0] = - self.beta * s * i / self.N
        diff[1] = self.beta * s * i / self.N - self.gamma * i
        diff[2] = self.gamma * i
        return diff
    
    def setInitCondition(self):
        self.populationInit = [self.N - 1, 1, 0]
        
    def solve(self):
        self.solution = odeint(self.odeModel,self.populationInit,self.t)
    
    def report(self):
        #plt.plot(self.solution[:,0],color = 'darkblue',label = 'Susceptible',marker = '.')
        plt.plot(self.solution[:,1],color = 'orange',label = 'Infection',marker = '.')
        plt.plot(self.solution[:,2],color = 'green',label = 'Recovery',marker = '.')
        plt.title('SIR Model' + ' infectionProb = '+ str(infectionProb))
        plt.legend()
        plt.xlabel('Day')
        plt.ylabel('Number of people')
        plt.show()

