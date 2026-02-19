# -*- coding: UTF-8 -*-
# Version 2 to convert Sigrid-3 polygon shapefiles to S411 
# Version 2.1.
#  The input can now also be a list of shapefiles, which are combined into one S411 file
#  This is intented to read in polygon,lines and point shapefiles
#  Included but newer tested with more then 1 polygonfile!!!!!!
# !!!

from datetime import datetime,timedelta
from sigrid3 import sigrid3ToS411Objects
import s411metadatanew as s411metadata
from s411 import s411ObjectsToGml,createS411DataSet,createS411ExchangeSet,zipdir
from s411 import s411_readshape
import zipfile
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile
import re

"""
     Parameters
     ----------
     Datei : full path to the Sigrid-3 File (extension will be skipped) 
         as string or Path
    
     Returns
     -------
     None.
    
     The S411 output is written in the same directory as the input file with an 
     "S411_" in front of the Sigrid-3 Filename
"""  



def s3_to_s411(Dateilist,Org='',chartcorrection=None,N411name='',OutAKT=None):
     if isinstance(Dateilist,list):
        Datei=Dateilist[0]    # we use the first shapefile as master
     else:
        Datei=Dateilist
        Dateilist=[Datei]
    # Org is the organization responsible for the chart and is used in finding the
    #  templates for the metainformation (not given tries to get is out of the sigrid3 file)
    # chartcorection can be a functin that tages a dataframe and return a corrected dataframe
    # N411name normally for the Filename of the S411 output the filename form the inputfile is used,
    #  this can be overridden by giving N411name. Nevertheless if missing also Org and
    #  date are included in the outputfilename
     if type(Datei) == str: 
         Datei=Path(Datei)
     filename = Datei.name
     ICEshape = filename.split(".")[0]
     metadatafile=Path(Datei.parent,ICEshape+'.xml')
     if N411name:
         N_411='S411_'+N411name
     else:
         N_411='S411_'+ICEshape
     
     # search for the date 
     # get metadata out of metadatafile if the file exists
     # else try differently
     # Publication date for datestamp (or root.findall('.//timeinfo/*caldate') ??)
     heute=datetime.today()

     datum1 = datetime(1900,1,1)  
     datum2 = datetime(1900,1,2)  
     if metadatafile.exists():
         try:
             tree = ET.parse(metadatafile)
             root = tree.getroot()
             q=root.findall('.//citation/*pubdate')
             datum1 = datetime.strptime(q[0].text,"%Y%m%d")
         except Exception:
             pass
     
     datum2=datetime.fromtimestamp(Datei.stat().st_ctime)
     # Sigrid3 file naming convention:
     # organization-code_region-name_yyyymmddd_feature-type_version.ext
     try: 
         JDATUM=filename.split('_')[2]
         datum2 = datetime.strptime(JDATUM[0:8],"%Y%m%d")
     except:     # we try several dates, still could throw exceptions as not 100%checked
         dumy=re.findall(r"_(\d+)",ICEshape)
         if len(dumy)<1:
             dumy=re.findall(r"(\d+)",ICEshape)
         if len(dumy)<1:
             if Datei.suffix.upper() == '.ZIP':  # perhaps the shapefile in the zip has a date
                 with ZipFile(Datei) as zf:
                     for file in zf.namelist():
                         if file.endswith('.shp'): 
                             dumy=re.findall(r"(\d+)",file)
         if len(dumy)<1:
             pass
         elif len(dumy[0])==8:
             datum2 = datetime.strptime(dumy[0],"%Y%m%d")
         elif len(dumy[0])==6:
             datum2 = datetime.strptime(dumy[0],"%y%m%d")
         elif len(dumy[0])==7:   # Year + dayofyear
             datum2=datetime.strptime(dumy[0],'%Y%j')
         elif len(dumy[0])==12: #date with hous+minutes
             datum2 = datetime.strptime(dumy[0],"%Y%m%d%H%M")
     if datum1==datum2:
        datum=datum1
     else:
         #print('Different Publication dates:',datum1,' and ',datum2)
         if datum1-heute > datum2-heute:
             datum=datum1
         else:
             datum=datum2
             #print('taking date nearest to today:',datum)
     dateStamp0=datum.strftime("%Y%m%d")
     dateStampS=datum.strftime("%Y%m%d")
     dateStampE=(datum + timedelta(days=5)).strftime("%Y%m%d")
     if 'latest' in N_411:  # put datestamp in S411-filename if only latest
        N_411=N_411.replace('latest',dateStamp0)
     dumy=re.findall(r"(\d+)",N_411) # at least 411 found
     if max([ len(item) for item in dumy])<6 : # no date found, add date at the end
         N_411=N_411+'_'+dateStamp0
     if len(Org)>1:
         if not Org in N_411:
             N_411=N_411.replace('S411_','S411_'+Org+'_')

     
     OutPath=Datei.parent   # Outputpath equals inputpath
     if (OutPath/Path(N_411+'.zip')).exists(): return  # S411 File already present
     laufzeit=datetime.now().strftime('%Y/%m/%d %H:%M ')
     print(laufzeit+' Starting S411 chart production:'+N_411)
    
     # Sigrid3 file naming convention:
     # organization-code_region-name_yyyymmddd_feature-type_version.ext
     # Get Template out of Organization if needed
     # but first place to search is in the Inputfile directory
     if len(Org)<1:
         Org=filename.split('_')[0]
     ECtemplate=Datei.with_name("ecTemplate.xml")
     if not ECtemplate.exists():
         ECtemplate=Datei.with_name("ecTemplate"+Org+".xml")
     if not ECtemplate.exists():
         ECtemplate=Datei.parent.with_name("ecTemplate"+Org+".xml")
     if not ECtemplate.exists():
         print('No ECtemplate found')
         return
     MDtemplate=Datei.with_name("mdTemplate.xml")
     if not MDtemplate.exists():
         MDtemplate=Datei.with_name("mdTemplate"+Org+".xml")
     if not MDtemplate.exists():
         MDtemplate=Datei.parent.with_name("mdTemplate"+Org+".xml")
     if not MDtemplate.exists():
         print(MDtemplate)
         print('No MDtemplate found')
         return
         
     try:
         s411FeatureList=list()
         for Datei in Dateilist:
             IArea=s411_readshape(Datei)    
             if not isinstance(chartcorrection,type(None)):
                 IArea=chartcorrection(IArea)
             # IArea=s411_readshape(Path(InPath,ICEshape+'.shp'))  # this read only shp files, but no zip-files       
             extent = IArea.WGS84extent
             S411epsg = IArea.crs.to_epsg()   # but this returns also 4326 even if using 0-360 longitudes   
    
             s411Features = sigrid3ToS411Objects(IArea)
             s411FeatureList.extend(s411Features)
     except Exception as e:
         print(sys.exc_info()[0])
         print(Datei)
         print(e)
         print(laufzeit,'error reading shapefile into S411Objectlist')
     try:             
         s411FeatureElementsList = s411ObjectsToGml(s411FeatureList,S411epsg=S411epsg)
         datasetTree = createS411DataSet(s411FeatureElementsList)
 
         metadataTree = s411metadata.getS411MetadataFromTemplate(MDtemplate, N_411, dateStamp0,
                     extent, dateStampS, dateStampE)
         # the S411 directory structure is written to the subdirectory with the icearea
         createS411ExchangeSet(OutPath, N_411, datasetTree, metadataTree)

         exchangeCatalogueTree = s411metadata.getS411ExchangeCatalogueFromTemplate(ECtemplate,
                     metadataTree, N_411, N_411 + ".gml", extent, 
                     OutPath/Path(N_411)/Path("data")/Path(N_411 + ".gml"))
         exchangeCatalogueTree.write(Path(OutPath,N_411,"catalogue.xml"), 
                     encoding ='utf-8', xml_declaration=True)
         # a S411-zipfile is written to the chartdirectory =dirPath
         dumy=Path(OutPath, N_411)
         zf = zipfile.ZipFile(dumy.with_suffix('.zip'), mode='w')
         zipdir(dumy,zf)
         zf.close()
         # special copy to another directory
         if isinstance(OutAKT,Path):    
             import shutil
             try: 
                shutil.copy(dumy.with_suffix('.zip'),OutAKT)
                shutil.rmtree(dumy,ignore_errors=True)
             except Exception:
                pass
         else:
             print("no OutAKT!!!:",dumy)
         return dumy.with_suffix('.zip')
     except:
         print(sys.exc_info()[0])
         print(N_411)
         print(laufzeit+"Error in the S411 Production")
#end of S411 production
