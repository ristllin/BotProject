#Modules:
from Scripts.casDBFile import casDB, CASletter, CASnames #Scripts.
from Scripts.seqType import *
from Scripts.seqTools import *
#Libraries
import xml.etree.ElementTree as ET
import csv
import time

DBLOCATION = "snp_resultP.xml" #SNP DB location
badParse = 0
AVERAGERSLTS = 0
totalSequances = 0

def importDB():
    """
    opens DB to extract XML data using DBLOCATION constant
    :return: XML data from file, type: xml.etree.ElementTree
    """
    with open(DBLOCATION,"r",encoding='utf-8') as f:
        dbRawData = ""
        print("loading DB")
        try:
            dbRawData = f.read()
        except MemoryError:
            print("oh no! we got a MemoryError!")#<<<>>>> splitting file and trying again...")
            exit() #<<<>>>>
        #for line in f:
        #    dbRawData += line #check if line by line is slow, if necessary split in half
        print("Finished Successfully")
        print("Parsing XML")
        dbXmlRoot = ET.fromstring(dbRawData)
        print("Finished XML Parsing")
        return dbXmlRoot


def parse(DB):
    """
    Gets XML db, returns seqType DB
    :param DB: XML elementTree root
    :return:
    """
    global badParse
    global totalSequances
    rsltDB = []
    print("Parsing DB")
    for seq in DB:
        totalSequances += 1
        try:
            orientation,mutatype,geneId,geneName,clinical,chromosome = "NA","NA","NA","NA","NA","NA"
            rsId= seq.get("rsId")
            for element in seq:
                if element.tag == "Sequence":
                    seq5 = element.find("Seq3").text.upper() #sequence
                    seq3 = element.find("Seq5").text.upper()
                    variants = element.find("Observed").text.upper().split("/") #variants
                if element.tag == "Assembly":
                    refallele = element.find("Component").find("MapLoc").get("refAllele").upper()
                    try:
                        geneId = element.find("Component").find("MapLoc").find("FxnSet").get("geneId")  # geneId
                        geneName = element.find("Component").find("MapLoc").find("FxnSet").get("symbol")  # geneName
                        clinical = seq.find("Phenotype").find("ClinicalSignificance").text  # <<<<<>>>>> add to field
                        chromosome = element.find("Component").get("chromosome")
                        orientation = element.find("Component").get("orientation")
                        for set in element.find("Component").findall("MapLoc"):
                            if set.find("FxnSet").get("fxnClass") != "reference":
                                mutatype = set.find("FxnSet").get("fxnClass")  #mutation type
                    except Exception:
                        True #skipping, non critical data
            mutations = variants.copy()
            try:
                mutations.remove(refallele)
            except ValueError: #refallele not in variants
                True
            fromto = ""
            for mutation in mutations:
                fromto += "from "+refallele+" to "+mutation+";"
            seq3 = seq3[-20:] #cutting sequences to minimum to avoid as many illegal nucs as possible
            seq5 = seq5[:20]
            if legalSeq(seq3+refallele+seq5+"".join(variants),"-AGTC") and (60 > len(seq3+refallele+seq5) > 40): #sequence size limitations
                a = seqType(rsId, geneId, geneName, seq3, seq5, refallele, mutations, chromosome, fromto, orientation, mutatype, clinical)
                rsltDB.append(a)
            else:
                #print("illegal sequence:",seq3+"<"+refallele+">"+seq5)
                badParse += 1
        except AttributeError as e:
            badParse += 1
            print(e, rsId)
    print("Parsing finished successfully")
    print("Initial parsing, ",len(rsltDB)," sequences were loaded")
    return rsltDB

def match(CAS,sequence,seq3len,rtrnLoc=False,specific=False):
    """
    gets full Sequence and CAS's PAM, returns Match if the PAM matches the Variant somewhere
    if rtrnLoc = True, returns location of the match instead of True, or False if none found
    :param CAS: String
    :param Variant: String
    :param specific: Boolean - check only the specific location given
    :return: if rtrnLoc -> list with int locations; else Boolean
    """
    # print("cas:",CAS," seq:",sequence," seq3:",seq3len)#debug
    window = len(CAS)
    movement = window
    rslt = []
    start = seq3len - window + 1
    if specific == True: #don't move
        movement = 1
        start = seq3len
    for i in range(movement): #window size options
        # print("movement: ",i)#debug
        match = True #flag
        for j in range(window): #compare single chars in window
            # print("window: ", j)  # debug
            try:
                # print(sequence[start+i+j]," vs ",CASletter[CAS[j]])  # debug
                if sequence[start+i+j] not in CASletter[CAS[j]]:
                    match = False
                    # print("false match")  # debug
                    break
            except Exception as e:
                match = False
                print("Corrupt Data, skipping variant",e)
        if match:
            if rtrnLoc:
                rslt.append(start + i)
                # print("loc found:",start+i)  # debug
            else:
                return True
    if rtrnLoc:
        return rslt
    else:
        return False

def rank(DB):
    """
    Loops on rslt DB and adds rank using external ranking module
    :param DB: seqType database
    :return: None
    """
    #for seq in DB:
    #   for var in ??? how do you know on which vars to run, which are the right results?
    #   seq.rank = ranking()
    return DB

def parseRslts(rslts):
    """
    gets seq.rslts returns string ready for csv
    :param rslts:
    :return: String
    """
    parsed = ["" for x in range(len(casDB))] #return variable for function template
    for column in range(len(casDB)):
        for rslt in rslts: #strings
            if rslt[1].find(casDB[column]) != -1:
                if rslt[1].find("comp") != -1:
                    parsed[column] += rslt[0] + " comp; "
                else:
                    parsed[column] += rslt[0] + "; " #<<<>>> not else, also! maybe else? check...apeo4 roy's
    return parsed

def export(DB):
    """
    outputs a seqTypeDB to a CSV file Using CSV module
    :param DB: {[key - string]:(seqType,[CAS1,CAS2...CASn],...)}
    :return: None, OUTput is a CSV file in the project dir
    """
    print("exporting to file")
    try:
        with open('output.csv', 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            spamwriter.writerow([",".join(["srID","geneID","geneName","Clinical Significance","WT sequance","Variants","chromosome","base replacements","clinVar","ranking score",",".join(casDB)]).replace('"','')]) #column titles
            rows = []
            print("Building rows")
            DBkeys = DB.keys()
            for key in DBkeys: #data
                seq = DB[key]
                rslts = parseRslts(seq.rslts)
                if seq.geneName == None:
                    seq.geneName = ""
                stringified = str(seq.snpID+','+seq.geneID+','+seq.geneName+','+seq.clinical+','+seq.seq3[-20:] + "<" + seq.wt + ">" + seq.seq5[:20]+','+"|".join(seq.varSeqList)+','+seq.chromo+','+seq.baseRepl+','+seq.clinVar+','+str(seq.rank)+','+",".join(rslts))
                rows.append([stringified])
            print("Creating CSV File")
            spamwriter.writerows(rows)
        print("File created successfully")
    except PermissionError as e:
        print("Writing CSV Failed, Please close file and run again")
def matchOnDB(DB):
    """

    :param DB: gets seqType DB
    :return: rsltsDB - {key-String wtSequence:[seqType,[CAS1,CAS2...CASn],...]}
    """
    print("Matching and building results DB")
    global AVERAGERSLTS
    rslt = {}
    for seq in DB: #Go over all objects in originPyDB
        currentWT = seq.seq3[-20:]+seq.wt+seq.seq5[:20] #DB keys are strings, for good hash function in dictionary instead of seqtype hash function
        tempSeq = duplicate(seq)
        for variant in seq.varSeqList: #Go over all .patho
            for CAS in casDB: #Go over all PAMseqs
                try:
                   currentVar = seq.seq3+variant+seq.seq5
                   compwt = reverseSeq(currentWT)[::-1] #on complementary we work with the reversed antisense, so the PAM remains the same, but the window starting point changes to seq5 length
                   compVar = reverseSeq(currentVar)[::-1]
                   matchPositions = match(CAS, currentVar, len(seq.seq3), rtrnLoc=True)
                   if matchPositions != []: #if there are any locations that match on variant
                       for matchIndex in matchPositions: #go over each of these locations
                           if (not (match(CAS,currentWT,matchIndex,specific=True))): #check if the wt does not match in these specific locations
                               if rslt.get(CAS) == None: #update DB - new entry
                                   rslt[CAS] = ((getCasName(CAS)+": "+CAS+" on "+str(matchIndex)))
                               else:
                                   rslt[CAS] += ", " + str(matchIndex)
                   matchPositions = match(CAS, compVar, len(seq.seq5), rtrnLoc=True) #again for complementary
                   if matchPositions != []:
                       for matchIndex in matchPositions:
                           if (not (match(CAS, compwt, matchIndex,specific=True))):
                               if rslt.get(CAS) == None: #update DB - new entry
                                   rslt[CAS] = ((getCasName(CAS)+": "+CAS+" on "+str(matchIndex)))
                               else:
                                   rslt[CAS] += ", " + str(matchIndex)
                except Exception as e:
                    print("failed to match due to an unexpected error:",e,"\n Statistics unreliable")
        AVERAGERSLTS += len(tempSeq.rslts)
    return rslt

def gRNA(seq,PAM,loc=True):
    """
    Gets a sequance, PAM and Variant location, returns calculated guideRNA
    :param loc: Variant location, if none passed, assume seq is seqType
    :param seq: seqType, or String and loc provided
    :param PAM: String
    :return:
    """
    if loc: #seqType
        loc = match(PAM, seq, len(seq.seq3), loc=True)
        return reverseSeq(seq[loc:loc + len(PAM)])
    loc = match(PAM,seq,loc,loc=True)
    return reverseSeq(seq[loc:loc+len(PAM)])

def getCasName(Cas):
    if CASnames[Cas] != None:
        return CASnames[Cas]
    else:
        return "Na"

def main():
    t0 = time.time() #for statistics
    rawDB = importDB() #*import whole XML DB and *parse to originPyDB <<<<>>>>maybe XML isnt persistant in the way it's written
    DB = parse(rawDB) #pyDB's will contain seqType objects with .seqID .original-string .patho-list of strings .workingCas list of strings)
    #<<<>>>>>ClinVar
    rsltDB = matchOnDB(DB) #results DB is a dict, by definition duplicates are not possible\allowed in a set
    #calculate guide RNA for every sequence? function gRNA is available
    #rank(DB)#For every seqType in rslyPyDB *rankCas (will show good matches, later can also use ranking system)
    export(rsltDB)#export to CSV (for every ID: the seq, which CASes work, future imp: what is the ranking between them, future imp: what is the affect of the pathogen)
    t1 = time.time() #debug
    print("---------statistics:---------")
    print("Debug, Hits found:",int(len(rsltDB))," ",int((len(rsltDB)/(totalSequances-badParse))*100),"%")
    if len(rsltDB) == 0:
        print("Average Hits per sequence: 0")
    else:
        print("Average Hits per sequence: ",AVERAGERSLTS/len(rsltDB))
    print("Debug: failed RS's:",badParse," out of: ",totalSequances," ",int((badParse/totalSequances)*100),"%")
    print("Debug, script ran in: ",t1-t0," seconds over ",totalSequances," sequences")

if __name__ == "__main__":
    main()