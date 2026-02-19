
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 12:24:43 2020

some functions for S411/sigrid-3 functionality
def rgb_to_hex(rgb):
def Sig3_Conc(CT):
def Sig3_PolT(SA):
def CT_farbe(CT):
   # WMO color codes for concentration
def SA_farbe(SA):
     # WMO color codes for stage of development
def RIO_farbe(RIO):
     # color codes for Polaris RIO
def RIO_polaris(Conc,SoD,IceClass):
    # takes partial concentrations and stage of development to calculte a risk index
    # Conc is a list of Concentrations (values according to the ice objects catalog)
    # Sod is a list of Stage of development  (values according to the ice objects catalog)


    
@author: bm12eis
"""
#import matplotlib
#matplotlib.use('Agg')
# or, after importing plt use
# plt.switch_backend('agg')
# or define before python:
# export MPLBACKEND="agg"


def rgb_to_hex(rgb):
   return '%02x%02x%02x' % rgb

def Sig3_Conc(CT):
  if not isinstance(CT, str): CT=str(CT)
  CT=CT.zfill(2)
  # converts CT,CA,CB oder CB in concentration in percent coverage
  # unknown converts to 0% !!
  # range converts to mean
  # an unknown value/tag of concentration converts to 0
  if type(CT) != str: CT='{:02d}'.format(int(round(CT))) # python 3.5
  #if type(CT) != str: CT=f'{round(CT):02d}' # python 3.6 or higher
  if CT == '01':
    return 5
  elif CT == '02' :
    return 5
  elif CT == '03' :
    return 5
  elif CT == '04' :  # new traces
    return 1
  elif CT == '99' : # unknown is set to 0%
    return 0
  elif CT == '98' : # icefree
    return 0
  elif CT == '92' :
    return 100
  elif CT == '91' :
    return 95
  elif CT == '00' : # for unknown
    return 0
  elif CT == '-9' : # for unknown, not set
    return 0
  else:
      ct1=int(CT[0])
      ct2=int(CT[1])
      if ct1==0:
          print('CT error:',CT)
          return 0
      if ct2==0:
          return ct1*10
      if ct2==1:
          ct2=10
      if ct1>ct2:
          print('CT error:',CT)
          return ct1*10
      return 10*(ct1+ct2)/2

def Conc_Sig3(conc):
  if isinstance(conc, str): conc=int(conc)
  # converts concentration in percent coverage to CT/ICEACT values
  if conc>100:
      print('error, Conc>100; set to 100')
      return '92'
  elif conc<0:
      print('error, Conc<0; set to icefree')
      return '98'
  elif conc==0:
      return '98'
  elif conc==100:
      return '92'
  elif conc>90:
      return '91'
  elif conc==1:    #traces
      return '04'
  elif conc<10:  # everthing below 10% is open water excpet 1%
      return '01'
  elif (conc/10)==0:
      return str(conc)
  else: # up till now we assume only multiples of 5
      lower=int(conc/10)
      return str(lower)+str(lower+1)

def Sig3_PolT(SA):
  # converts SA,SB oder SB in Polaris thickness class
  # which goes from 0 to 11
  # unknown 99 converts to heavy multi year !!
  # brash ice and no stage converts to new ice
  # an unknown value of SA converts to 0
  if type(SA) != str: SA='{:02d}'.format(int(round(SA))) # python 3.5
  SA=SA.zfill(2)
  # if type(SA) != str: SA=f'{SA:02d}'  # python 3.6 or higher
  if SA == '01':
    return 0
  elif SA == '70' :
    return 1
  elif SA == '80' :
    return 1
  elif SA == '81' :
    return 1
  elif SA == '82' :
    return 1
  elif SA == '83' :
    return 3
  elif SA == '84' :
    return 2
  elif SA == '85' :
    return 3
  elif SA == '86' :
    return 8
  elif SA == '87' :
    return 5
  elif SA == '88' :
    return 4
  elif SA == '89' :
    return 5
  elif SA == '90' :
    return 11
  elif SA == '91' :
    return 6
  elif SA == '92' :
    return 11
  elif SA == '93' :
    return 8
  elif SA == '94' : # residual to second year
    return 9
  elif SA == '95' : # old ice to heavy muliti year
    return 11
  elif SA == '96' :
    return 9
  elif SA == '97' :
    return 10
  elif SA == '98' : # glacier to heavy multi
    return 11
  elif SA == '99' : # for unknown set to heavy multi-year
    return 11
  elif SA == '00' : # for unknown00 =icefree
    return 0
  elif SA == '-9' : # for unknown-9 =icefree
    return 0
  else:
    return 0

def CT_farbe(CT):
    # WMO color codes for concentration
    try:
        if type(CT) != str: CT='{:02d}'.format(int(round(CT))) # python 3.5
    except:
        print(CT)
        CT='-1'
    CT=CT.zfill(2)
    # if type(CT) != str: CT=f'{CT:02d}' # python 3.6 or higher
    if CT in ['01','02']:
        farbe=rgb_to_hex((150,200,255)) #open water
    elif CT in ['10','20','30','12','13','23']:
        farbe=rgb_to_hex((140,255,160))
    elif CT in ['40','50','60','34','35','45','46','56']:
        farbe=rgb_to_hex((255,255,  0))
    elif CT in ['70','80','57','67','68','78','18']:     # added 18 for US MIZ charts
        farbe=rgb_to_hex((255,125,  7))
    elif CT in ['90','91','79','81','89']:
        farbe=rgb_to_hex((255,  0,  0))
    elif CT in ['92']:
        farbe=rgb_to_hex((255,  0,  0))
    elif CT in ['100']:
        farbe=rgb_to_hex((145,  0,  0))
    elif CT in ['00']:
        farbe=rgb_to_hex((  0,100,255)) # ice free
    else:
        farbe=rgb_to_hex((235,235,235)) # undefined
     #       farbe=rgb_to_hex((150,150,150)) #fastice
    return '#'+farbe

def SA_farbe(SA):
     # WMO color codes for stage of development
     if type(SA) != str: SA='{:02d}'.format(round(SA)) # python 3.5
     SA=SA.zfill(2)
     # if type(SA) != str: SA=f'{SA:02d}'  # python 3.6 or higher
     if SA in ['80']:
        farbe=rgb_to_hex((150,200,255)) #no stage
     elif SA in ['81']:
        farbe=rgb_to_hex((240,210,250))
     elif SA in ['82']:
        farbe=rgb_to_hex((255,100,255)) # nilas <10cm
     elif SA in ['83']:
        farbe=rgb_to_hex((170, 40,240))
     elif SA in ['84']:
        farbe=rgb_to_hex((135, 60,215))
     elif SA in ['85']:
        farbe=rgb_to_hex((220, 80,235))
     elif SA in ['86']:
        farbe=rgb_to_hex((255,255,  0))
     elif SA in ['87']:
        farbe=rgb_to_hex((155,210,  0))
     elif SA in ['88']:
        farbe=rgb_to_hex((215,250,130))
     elif SA in ['89']:
        farbe=rgb_to_hex((175,250,  0))
     elif SA in ['90']:
        farbe=rgb_to_hex((255,0,255))
     elif SA in ['91']:
        farbe=rgb_to_hex((  0,200, 20))
     elif SA in ['92']:
        farbe=rgb_to_hex((255,0,255))
     elif SA in ['93']:
        farbe=rgb_to_hex((0,120,  0))
     elif SA in ['94']:
        farbe=rgb_to_hex((255,0,255))
     elif SA in ['95']:
        farbe=rgb_to_hex((180,100, 50))
     elif SA in ['96']:
        farbe=rgb_to_hex((255,120, 10))
     elif SA in ['97']:
        farbe=rgb_to_hex((200,  0,  0))
     elif SA in ['98']:
        farbe=rgb_to_hex((210,210,215)) #glacier ice, falsch
     elif SA in ['99']:
        farbe=rgb_to_hex((235,235,235))
     elif SA in ['00']:
        farbe=rgb_to_hex((  0,100,255)) # ice free
     elif SA in ['-9']:
        farbe=rgb_to_hex((  0,100,255)) # ice free
     else:
        farbe=rgb_to_hex((235,235,235)) # undefined
     #       farbe=rgb_to_hex((150,150,150)) #fastice
     return '#'+farbe

def RIO_farbe(RIO):
     # color codes for Polaris RIO
    # RIO>=10 bright green, 10>=RIO20>5 light green, 5>=yellow>=0, 0>orange>-10, red<-10
    if RIO>=10:
        farbe='#00ff00' # lime
    elif RIO>5:
        farbe='#ADFF2F' # greenyellow
    elif RIO>0:
        farbe='#FFFF00'
    elif RIO>-10:
        farbe='#FFA500'
    else:
        farbe='#FF0000'
    return farbe

def RIO_polaris(Conc,SoD,IceClass):
    # takes partial concentrations and stage of development to calculte a risk index
    # Conc is a list of Concentrations (values according to the ice objects catalog)
    # Sod is a list of Stage of development  (values according to the ice objects catalog)
    if Conc is None: return -99
    if SoD is None: return -99
    # This are the polaris weights for each Ice Class
    IC_Weight={'PC1': [ 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 1, 1] ,
        'PC2': [ 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 0] ,
        'PC3': [ 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 0,-1] ,
        'PC4': [ 3, 3, 3, 3, 2, 2, 2, 2, 1, 0,-1,-2] ,
        'PC5': [ 3, 3, 3, 3, 2, 2, 1, 1, 0,-1,-2,-2] ,
        'PC6': [ 3, 2, 2, 2, 2, 2, 2, 0,-1,-2,-3,-3] ,
        'PC7': [ 3, 2, 2, 2, 1, 1, 0,-1,-2,-3,-3,-3] ,
        'IAsuper': [ 3, 2, 2, 2, 2, 1, 0,-1,-2,-3,-4,-4] ,
        'IA': [ 3, 2, 2, 2, 1, 0,-1,-2,-3,-4,-5,-5] ,
        'IB': [ 3, 2, 2, 1, 0,-1,-2,-3,-4,-5,-6,-6] ,
        'IC': [ 3, 2, 1, 0,-1,-2,-3,-4,-5,-6,-7,-8] ,
        'NON': [ 3, 1, 0,-1,-2,-3,-4,-5,-6,-7,-8,-8]
         }
    if IceClass in IC_Weight:
        Weight=IC_Weight[IceClass]
    else:
        print('ERROR unkonwn Iceclass:'+str(IceClass)+' set to NON')
        #raise ValueError('Unknown Iceclass')
        Weight=IC_Weight['NON']

    # first we convert, if neccesary, conc and Sod into strings
    for ii in range(len(Conc)): Conc[ii]=str(Conc[ii]).zfill(2)
    for ii in range(len(SoD )):  SoD[ii]=str( SoD[ii]).zfill(2)
    try:
        if len(Conc)<len(SoD): Conc=Conc.insert(0,'02')  # S0 gets a concentration of open water=5%
        if len(Conc)<len(SoD): Conc=Conc.append('02')    # 5th partial concentration gets a concentration of open water=5%
    except:
        print(Conc)
        print(SoD)
        print('')
    CTsum=0
    for ii in range(len(Conc)): CTsum=CTsum+Sig3_Conc(Conc[ii])
    # sum of partial concentrations, should be the same
    # as CT, but perhaps differs because of open water=5%
    if CTsum>110:
        print(Conc)
        print(CTsum)
        raise ValueError('Sum of Concentration larger 110%')
    RIO=0
    for ii in range(len(Conc)):        
        if (ii>0) and (str(SoD[ii])=='99'):
            isod-=1  # if SOD unknown we set weight to one lower then previos SOD
            if isod<0: isod=0
        else:
            isod=Sig3_PolT(SoD[ii])
        RIO=RIO+(Sig3_Conc(Conc[ii])/10)*Weight[isod]
    RIO=RIO+ (10-(CTsum/10))*Weight[0]
    return RIO


