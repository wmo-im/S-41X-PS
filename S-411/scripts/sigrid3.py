'''
Version 2 including S411 Rownames
 including Polygon, LineString and Point geometries  (Multi... should also be covered)
 all features/Types of Lines and ponits are included, but still no atttributes
 polygons are always iceareas (no lakeice and no iceberg area). As attributes wjust the ice egg ic covered.
'''
import s411objects
from S411func import Sig3_Conc, Conc_Sig3

def sigrid3ToS411ObjectsN(gpdf):     # compatibility reason
    return sigrid3ToS411Objects(gpdf)


def sigrid3ToS411Objects(gpdf):

    s411SeaIceFeatureList = []

    #####################################################
    # Multipart to Singlepart, because s411 does not support multigeometries
    # try to convert to single usinf explode, which seeems to work fine
    singlegpdf = gpdf.explode(index_parts=True)
    if 'AREA' in singlegpdf:
        singlegpdf.drop('AREA', axis=1, inplace=True)
    if 'PERIMETER' in singlegpdf:
        singlegpdf.drop('PERIMETER', axis=1, inplace=True)

    # see if polygons,lines or points
    # wie have to use a loop a geometry can also be none/missing
    shapetype = ''
    for geom in singlegpdf.geom_type:
        if geom == 'Polygon':
            shapetype = geom
            break
        if geom == 'LineString':
            shapetype = geom
            break
        if geom == 'Point':
            shapetype = geom
            break
    else:
        print('unknown geometry', geom)
        return
    # Polygons as seaice
    if shapetype == 'Polygon':
        not_implemented = ['DP', 'DD', 'DR', 'DO', 'WF', 'WN', 'WD', 'WW', 'WO',
                           'RN', 'RA', 'RD', 'RC', 'RF', 'RH', 'RX', 'RO',
                           'EM', 'EX', 'EI', 'EO', 'AV', 'AK', 'AM', 'AT',
                           'SN', 'SM', 'SW', 'BD', 'be', 'BN', 'BY',
                           'BO', 'TT', 'TO', 'OP', 'OS', 'OT', 'T1', 'T2']
        FABC_iceflz = {22: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11, 99: 99, 21: 21,
                       11: 20, 12: 20, 13: 20, 14: 20, 15: 20, 16: 20, 17: 20, 18: 20, 19: 20, 91: 20, 20: 20}
        # FA,FB,FC level ice=21, stripes and patches 11-20+91; but together with concentration
        # all stripes and pathes are now transfered to ICEFLZ=20 (NEW definition needed in iceobjects)
        
        CFinformation=False  # set to true if CF is set with values other then missing

        for g, row in singlegpdf.iterrows():
            if 'POLY_TYPE' in row:
                if not (row['POLY_TYPE'] == 'I' or row['POLY_TYPE'] == 'S'):
                    continue

            # Create seaice object
            # not all things are handeld up till now
            # missing CF and all optional objects
            s411SeaIceFeature = s411objects.Seaice()

            geometry = None
            ct = None
            iceapc = [99, 99, 99, 99, 99]
            icesod = iceapc.copy()
            iceflz = iceapc.copy()
            for rowname in row.keys():
                # rowname in uppercase to compare
                rowNAME = rowname.upper()

                if rowNAME == 'POLY_TYPE':
                    continue
                if rowNAME == 'GEOMETRY':
                    geometry = row[rowname]  # ['coordinates']
                    s411SeaIceFeature.set_geometry(geometry)
                elif hasattr(s411SeaIceFeature, rowname):
                    # Sigrid3 can also use S411objectts
                    # checking for ice objects (we do not check for inconsistencies like
                    # having CT and ICEACT)
                    bb=getattr(s411SeaIceFeature,'set_'+rowname)
                    bb(row[rowname])
                    continue
                elif hasattr(s411SeaIceFeature, rowname.lower()):
                        bb=getattr(s411SeaIceFeature,'set_'+rowname.lower())
                        bb(row[rowname])
                        continue
                else:
                    # Integer out of row (is used often)
                    try:
                        rowint = int(row[rowname])
                        if rowint<0: rowint=99 #  ????????? thats just to catch values of -9 for missing
                    except Exception:
                        rowint = 99
                    # feature id for gml
                    if rowNAME == 'ID':
                        fid = row[rowname]
                        if fid is not None:
                            s411SeaIceFeature.set_gml_id(fid)
    
                    # ICEACT from CT
                    elif rowNAME == 'CT':
                        ct = rowint
                        if ct < 0:
                            ct = 99
    
                    # ICEAPC from CA,CB,CC
                    elif rowNAME == 'CA':
                        iceapc[0] = rowint
                    elif rowNAME == 'CB':
                        iceapc[1] = rowint
                    elif rowNAME == 'CC':
                        iceapc[2] = rowint
                    # ICESOD from SA,SB,SC,CC,CD
                    elif rowNAME == 'SA':
                        icesod[0] = rowint
                    elif rowNAME == 'SB':
                        icesod[1] = rowint
                    elif rowNAME == 'SC':
                        icesod[2] = rowint
                    elif rowNAME == 'CN':
                        icesod[3] = rowint
                        if rowint != 99:
                            iceapc[3] = 4  # traces
                    elif rowNAME == 'CD':  # iseapc must set later
                        icesod[4] = rowint
                    # ICEFLZ from FA,FB,FC
                    elif rowNAME == 'FA':
                        if rowint in FABC_iceflz:
                            iceflz[0] = FABC_iceflz[rowint]
                    elif rowNAME == 'FB':
                        if rowint in FABC_iceflz:
                            iceflz[1] = FABC_iceflz[rowint]
                    elif rowNAME == 'FC':
                        if rowint in FABC_iceflz:
                            iceflz[2] = FABC_iceflz[rowint]
                    elif rowNAME == 'FP':  # for a first shot we set predominat equal to FA  !!!!! THIS HAS ROOM FOR IMPROVEMENT (primary and secondary)
                        if rowint in FABC_iceflz:
                            iceflz[0] = FABC_iceflz[rowint]
                    elif rowNAME == 'FS': # for a first shot we set secondary equal to FB
                        if rowint in FABC_iceflz:
                            iceflz[1] = FABC_iceflz[rowint]
                    # others
                    elif rowNAME == 'CF':  # complicated if set and most probable transfer is not correct, as it also depends on ice service
                        if rowint==99:
                            continue
                        elif rowint>99:
                            ii1=int(rowint/100)
                            ii2=rowint%100
                        elif rowint>0:
                            ii1=rowint
                            ii2=99
                        else:
                            continue   # CF set but <=0
                        if not CFinformation:
                            print('CF is used, first value=',rowint)
                            CFinformation=True
                        if (ii1 > 0) and (ii1<99):  # sometime seems as -9 given as unknown, then dont set
                            iceflz[3] = FABC_iceflz[rowint]
                        if (ii2 > 0) and (ii2<99):  # sometime seems as -9 given as unknown, then dont set
                            iceflz[4] = FABC_iceflz[rowint]
                    elif rowNAME == 'SD':  # sastrugi orientation
                        try:
                            icescn = rowint
                            if icescn > 0:  # sometime seems as -9 given as unknown, then dont set
                                s411SeaIceFeature.set_icedos(icescn)
                        except Exception:
                            pass
                    elif rowNAME == 'SO':  # observational method not transfered to S411'
                        try:
                            iceNNN = rowint
                            if iceNNN > 0:  # sometime seems as -9 given as unknown, then dont set
                                pass
                        except Exception:
                            pass
                    # now all still not implemented SIGRID-3 fields
                    elif rowname in not_implemented:
                        print('not implemented feature',
                              rowname, ' = ', row[rowname])
                    else:
                        print('totally unknown Field:', rowname)
    
                # convert Ice Egg to ice objects
            # sum of all partial concentrations
            ct2 = sum(map(Sig3_Conc, iceapc))

            if (ct is None) and (ct2 > 0):
                ct = Conc_Sig3(ct2)

            if ct is not None:   # else we do not have to set ice egg
                s411SeaIceFeature.set_iceact(ct)

                # check iceapc,icesod,iceflz
                if (iceapc[0] == 99) and (min(icesod)<99):   
                    if (iceapc[0] == 99):
                        iceapc[0]=ct
                    else:
                        iceapc[0]=Conc_Sig3(Sig3_Conc(ct)-ct2)
                if icesod[4] != 99:  #
                    iceapc[4] = Conc_Sig3(Sig3_Conc(ct)-ct2)
                    if iceapc[4] == '98':
                        iceapc[4] = '04'  # traces

                for ii in range(len(iceapc)-1, -1, -1):
                    if iceapc[ii] == 99:
                        del iceapc[ii]
                        if icesod[ii] != 99:
                            print('icesod set with iceapc unknown')
                        del icesod[ii]
                        if iceflz[ii] != 99:
                            print('iceflz set with iceapc unknown')
                        del iceflz[ii]

                if iceapc is not None:
                    s411SeaIceFeature.set_iceapc(iceapc)
                    s411SeaIceFeature.set_icesod(icesod)
                    s411SeaIceFeature.set_iceflz(iceflz)

            if geometry is not None:
                s411SeaIceFeature.set_geometry(geometry)
                s411SeaIceFeatureList.append(s411SeaIceFeature)

        return s411SeaIceFeatureList
    if shapetype == 'LineString':   # just a draft, not setting attributes
        for g, row in singlegpdf.iterrows():
            if 'LINE_TYPE' not in row:
                continue
            geometry=None
            geometry = row['GEOMETRY']  # ['coordinates']
            if row['LINE_TYPE'] == 'ICELNE':
                s411SeaIceFeature = s411objects.Icelne()
                pass
            elif row['LINE_TYPE'] == 'BRGLNE':
                s411SeaIceFeature = s411objects.Brglne()
                pass
            elif row['LINE_TYPE'] == 'OPNLNE':
                s411SeaIceFeature = s411objects.Opelne()
                pass
            elif row['LINE_TYPE'] == 'LKILNE':
                s411SeaIceFeature = s411objects.Lkilne()
                pass
            elif row['LINE_TYPE'] == 'I_RIDG':
                s411SeaIceFeature = s411objects.I_Ridg()
                pass
            elif row['LINE_TYPE'] == 'I_LEAD':
                s411SeaIceFeature = s411objects.I_Lead()
                pass
            elif row['LINE_TYPE'] == 'I_FRAL':
                s411SeaIceFeature = s411objects.I_Fral()
                pass
            elif row['LINE_TYPE'] == 'I_CRAC':
                s411SeaIceFeature = s411objects.I_Crac()
                pass
            if geometry is not None:
                s411SeaIceFeature.set_geometry(geometry)
            s411SeaIceFeatureList.append(s411SeaIceFeature)

        return s411SeaIceFeatureList
    if shapetype == 'Point':   # just a draft, not setting attributes
        for g, row in singlegpdf.iterrows():
            if 'POINT_TYPE' not in row:
                continue
            geometry=None
            geometry = row['GEOMETRY']  # ['coordinates']
            if row['POINT_TYPE'] == 'ICECOM':
                s411SeaIceFeature = s411objects.Icecom()
                pass
            elif row['POINT_TYPE'] == 'ICELEA':
                s411SeaIceFeature = s411objects.Icelea()
                pass
            elif row['POINT_TYPE'] == 'ICEBRG':
                s411SeaIceFeature = s411objects.Icebrg()
                pass
            elif row['POINT_TYPE'] == 'FLOBRG':
                s411SeaIceFeature = s411objects.Flobrg()
                pass
            elif row['POINT_TYPE'] == 'ICETHK':
                s411SeaIceFeature = s411objects.Icethk()
                pass
            elif row['POINT_TYPE'] == 'ICESHR':
                s411SeaIceFeature = s411objects.Iceshr()
                pass
            elif row['POINT_TYPE'] == 'ICEDIV':
                s411SeaIceFeature = s411objects.Icediv()
                pass
            elif row['POINT_TYPE'] == 'ICERDG':
                s411SeaIceFeature = s411objects.Icerdg()
                pass
            elif row['POINT_TYPE'] == 'ICEKEL':
                s411SeaIceFeature = s411objects.Icekel()
                pass
            elif row['POINT_TYPE'] == 'ICEDFT':
                s411SeaIceFeature = s411objects.Icedft()
                pass
            elif row['POINT_TYPE'] == 'ICEFRA':
                s411SeaIceFeature = s411objects.Icefra()
                pass
            elif row['POINT_TYPE'] == 'ICERFT':
                s411SeaIceFeature = s411objects.Icerft()
                pass
            elif row['POINT_TYPE'] == 'JMDBRR':
                s411SeaIceFeature = s411objects.Jmdbrr()
                pass
            elif row['POINT_TYPE'] == 'STGMLT':
                s411SeaIceFeature = s411objects.Stgmlt()
                pass
            elif row['POINT_TYPE'] == 'SNWCVR':
                s411SeaIceFeature = s411objects.Snwcvr()
                pass
            elif row['POINT_TYPE'] == 'STRPTC':
                s411SeaIceFeature = s411objects.Strptc()
                pass
            elif row['POINT_TYPE'] == 'I_GRHM':
                s411SeaIceFeature = s411objects.I_Grhm()
                pass
            if geometry is not None:
                s411SeaIceFeature.set_geometry(geometry)
            s411SeaIceFeatureList.append(s411SeaIceFeature)

        return s411SeaIceFeatureList
