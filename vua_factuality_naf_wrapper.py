'''
Created on July 8, 2015

@author: antske
'''

from KafNafParserPy import *
from subprocess import call, PIPE
import sys
import time
import getopt

class CtermInfo:
    '''
    Class with all features for finding factuality from a given term
    '''
    def __init__(self, tid=''):
        
        self.sn_nr = 'NULL'
        self.tid = tid
        self.wid = 'NULL'
        self.word = 'NULL'
        self.lemma = 'NULL'
        self.pos = 'NULL'
        self.morphofeat = 'NULL'
        self.dephead = 'NULL'
        self.deplabel = 'NULL'
        self.eventTag = 'O'
        self.propbank = 'NULL'
        self.verbnet = 'NULL'
        self.framenet = 'NULL'
        self.wordnet = 'NULL'
        self.eventtype = 'NULL'
        self.eso = 'NULL'
        self.nombank = 'NULL'
        self.roleTag = 'O'

    def return_vals_as_list(self):
        '''
        Returns information needed to generate features for factuality for a given term
        '''
        mylist = [self.sn_nr,
        self.tid,
        self.wid,
        self.word,
        self.lemma,
        self.pos,
        self.morphofeat,
        self.dephead,
        self.deplabel,
        self.eventTag,
        self.propbank,
        self.verbnet,
        self.framenet,
        self.wordnet,
        self.eventtype,
        self.eso,
        self.nombank,
        self.roleTag]
        
        return mylist

class cFactValLocal:
    '''
     Class for capturing information associated with factuality
    '''
    def __init__(self, factuality=None, resource=None, confidence = None):
            
        self.factuality = factuality
        self.resource = resource
        self.confidence = confidence
        self.source = None

    def set_source(self, source):

        self.source = source

            
class cFactObject:
    '''
    Class for storing factuality information for a specific span
    '''
    
    def __init__(self, fid=None, tid=None, span=[], factVals= []):
        
        self.fid = fid
        self.tid = tid
        self.span = span
        self.factVals = factVals
        
        
    def add_factval(self, factval):
        
        self.factVals.append(factval)
            
            

def get_public_id(nafobj):
    '''
    Takes naf obj as input and returns the publicId (as string)
    '''

    myheader = nafobj.header
    return myheader.get_publicId()

def create_dep_dictionary(nafobj):
    '''
    Takes naf obj and creates a dict where each term is linked to the term of which it is a depedent
    as well as the dependency label
    '''
    my_dep_dict = {}
    for dep in nafobj.get_dependencies():
        dependent = dep.get_to()
        head = dep.get_from()
        label = dep.get_function()
        if dependent in my_dep_dict:
            print('Problem: this term has more than one head')
        else:
            my_dep_dict[dependent] = [head,label]
            
    return my_dep_dict


def create_exRefs_dict(mynode):
    '''
    Creates a dictionary that links the resources in exRefs to the highest scoring reference and the conf score
    '''
    exRefs = {}
    for exR in mynode.get_external_references():
        res = exR.get_resource()
        ref = exR.get_reference()
        conf = exR.get_confidence()
        if not conf:
            conf = 0.0
        else:
            conf = float(conf)
        if not res in exRefs:
            exRefs[res] = [ref,conf]
        elif conf > exRefs[res][1]:
            exRefs[res] = [ref,conf]
    return exRefs


def create_srl_dict(nafobj):
    '''
    Takes nafobj and retrieves information from the SRL layer: verbnet, framenet, propbank, eso
    '''
    my_srlpred_dict = {}
    srllayer = nafobj.srl_layer
    
    for pred in srllayer.get_predicates():
        
        exRefs = create_exRefs_dict(pred)
        
        pspan = pred.get_span().get_span_ids()
        for t in pspan:
            #we don't measure start and end point for the predicate: if they're events, this is done in the event layer
            my_srlpred_dict[t] = [exRefs,'O']
        for myrole in pred.get_roles():
            rspan = myrole.get_span().get_span_ids()
            rExRefs = create_exRefs_dict(myrole)
            role = myrole.get_sem_role()
            my_srlpred_dict[rspan[0]] = [exRefs, 'B' + role]
            #all other tokens get I + role
            for x in range(1, len(rspan)):   
                my_srlpred_dict[rspan[x]] = [exRefs, 'I' + role]
                
    return my_srlpred_dict


def create_event_dict(nafobj):
    '''
    Takes nafobj as input and creates a dictionary with event information
    '''
    event_dict = {}
    clayer = nafobj.coreference_layer
    for coref in clayer.get_corefs():
        coref_type = coref.get_type()
        if coref_type == 'event':
            #get external references
            exRefs = create_exRefs_dict(coref)
            #go through spans and add all terms from Span to dict
            for myspan in coref.get_spans():
                span_ids = myspan.get_span_ids()
                event_dict[span_ids[0]] = [exRefs, 'BEvent']
                for x in range(1, len(span_ids)):
                    event_dict[span_ids[x]] = [exRefs, 'IEvent']
    return event_dict

def collect_info_per_term(nafobj):
    '''
    Takes nafobj as input and returns dictionary with term id as key and collected info object as value
    where info is filled out where possible
    '''
    termsInfo = []
    for term in nafobj.get_terms():
        tId = term.get_id()
        #initiate object
        myTinfo = CtermInfo(tId)
        myspan = term.get_span().get_span_ids()
        #obtain info from token layer, starting with first token in span
        mytoken = nafobj.get_token(myspan[0])
        myTinfo.sn_nr = mytoken.get_sent()
        wid = mytoken.get_id().lstrip('w')
        token = mytoken.get_text()
        #for the rare case where the term span consists of more than one token
        #update id and token (sn_nr will be the same)
        for x in range(1, len(myspan)):
            mytoken = nafobj.get_token(myspan[0])
            wid += '_' + mytoken.get_id().lstrip('w')
            token += '_' + mytoken.get_text()
        myTinfo.wid = wid
        myTinfo.word = token
        #read off information from term
        myTinfo.lemma = term.get_lemma()
        myTinfo.pos = term.get_pos()
        myTinfo.morphofeat = term.get_morphofeat()
        #add externalRefs for as far as present on term itself
        exRefs = create_exRefs_dict(term)
        #for now: get wordnet score of It_Makes_Sense_WSD as first choice (overwrites ukb output)
        if len(exRefs) > 0:
            if 'WordNet-3.0' in exRefs:
                myTinfo.wordnet = exRefs.get('WordNet-3.0')[0]
            elif 'wn30g.bin64' in exRefs:
                myTinfo.wordnet = exRefs.get('wn30g.bin64')[0]
        
        termsInfo.append(myTinfo)
    return termsInfo


def extract_features(nafobj):
    '''
    Extract relevant features for output
    '''
    #1. features from header: docId
    docId = get_public_id(nafobj)
    #no need to create anything if no srls to get events from
    basic_info_per_term = []
    if nafobj.srl_layer:
        #2. create dict with dependent to head + label
        my_deps = create_dep_dictionary(nafobj)
        #3. create dict with srl information
        my_srl_info = create_srl_dict(nafobj)
        #4. create dict with event information
        my_event_info = create_event_dict(nafobj)
        #5. go through term layer and produce full feature set
        basic_info_per_term = collect_info_per_term(nafobj)
        #6. update term info with information from other layers
        for t in basic_info_per_term:
            tid = t.tid
            #update dep info
            if tid in my_deps:
                tdep = my_deps.get(tid)
                t.dephead = tdep[0]
                t.deplabel = tdep[1]
            #update with information from coreference(/event) layer
            if tid in my_event_info:
                newinfo = my_event_info.get(tid)
                t.eventTag = newinfo[1]
                #wsd output is prefered: only replace if this is absent
                if t.wordnet == 'NULL':
                    for k, v in newinfo[0].items():
                        if 'WordNet' in k:
                            t.wordnet = v[0]
            #update with info from srl layer
            if tid in my_srl_info:
                newinfo = my_srl_info.get(tid)
                t.roleTag = newinfo[1]
                for k, v in newinfo[0].items():
                    if 'PropBank' in k:
                        t.propbank = v[0]
                    elif 'VerbNet' in k:
                        t.propbank = v[0]
                    elif 'FrameNet' in k:
                        t.framenet = v[0]
                    elif 'WordNet' in k:
                        t.wordnet = v[0]
                    elif 'ESO' in k:
                        t.eso = v[0]
                    elif 'EvenType' in k:
                        t.eventtype = v[0]
                    elif 'NomBank' in k:
                        t.nombank = v[0]
               
    return docId, basic_info_per_term
    

def print_out_features(docId, flist, tmpdir):
    '''
    takes docId, list with feature values per term and path to directory for output file as input
    prints out all features in temporary dir file
    if for training: file will have docId as name, else it will be 'temp'
    '''
    outfname = tmpdir + 'features.tsv'
    myout = open(outfname, 'w')
    for fobj in flist:
        newline = docId
        feats = fobj.return_vals_as_list()
        for ft in feats:
            newline += '\t' + ft.encode('utf8').decode()
        myout.write(newline + '\n')
    myout.close()


def translate_values(factVal):
    '''
    Returns NWR values based on factbank value.
    Checks in order of frequency in training corpus
    '''
    if factVal == 'CT+':
        return 'CERTAIN', 'POS'
    if factVal == 'Uu':
        return 'UNDERSPECIFIED', 'UNDERSPECIFIED'
    if factVal == 'CT-':
        return 'CERTAIN', 'NEG'
    if factVal == 'PR+':
        return 'PROBABLE', 'POS'
    if factVal == 'PS+':
        return 'POSSIBLE', 'POS'
    if factVal == 'PR-':
        return 'PROBABLE', 'NEG'
    if factVal == 'NA':
        return 'UNDERSPECIFIED', 'UNDERSPECIFIED'
    if factVal == 'PS-':
        return 'POSSIBLE', 'NEG'
    if factVal == 'CTu':
        return 'CERTAIN', 'UNDERSPECIFIED'
    elif factVal == 'NONE':
        return 'CERTAIN', 'POS'
    else:
        return 'UNDERSPECIFIED', 'UNDERSPECIFIED'



def add_factvalues(value, resource, fnode, source = None):
    '''
    Adds a new factuality value to the factuality node
    '''
    
    fVal = Cfactval()
    fVal.set_resource(resource)
    fVal.set_value(value)
    if source != None:
        fVal.set_source(source)
    fnode.add_factval(fVal)
    
    
    
def add_factuality_info_from_output(fn, onto, factDict, source=''):
    '''
    Goes through machine learning output and adds information from this output to factDict
    '''
    myfactuality = open(fn, 'r')
    new_factDict = {}
    for line in myfactuality:
        parts = line.split()
        mytid = parts[2]
        if mytid in factDict:
            factObj = factDict.get(mytid)
        else:
            factObj = []
        val = parts[-1]
        if onto == 'both':
            #factBank is resource for direct value
            factVal_fb = cFactValLocal(factuality=val,resource='factbank')
            factObj.append(factVal_fb)
            ctval, polval = translate_values(val)
            fVal_ct = cFactValLocal(factuality=ctval,resource='nwr:attributionCertainty')
            fVal_pol = cFactValLocal(factuality=polval,resource='nwr:attributionPolarity')
            factObj.append(fVal_ct)
            factObj.append(fVal_pol)
            if source != '':
                factVal_fb.set_source(source)
                fVal_ct.set_source(source)
                fVal_pol.set_source(source)
        else:
            my_factval = cFactValLocalLocal(factuality=val, resource=onto)
            factObj.append(my_factval)
            if source != '':
                my_factval.set_source(source)
        #set value in new factDict
        new_factDict[mytid] = factObj
    myfactuality.close()
    return new_factDict

def update_naflayer(nafobj, factDict):
    '''
    Takes newly collected factuality information and adds this to the factuality layer
    '''
    #all factuality information from input is stored, so old layer can be removed
    if nafobj.factuality_layer != None:
        nafobj.remove_factualities_layer(False)
    myFactualityLayer = Cfactualities()
    fid = 0
    for tid in sorted(factDict):
        v = factDict.get(tid)
        fid += 1
        fnode = Cfactuality()
        fnode.set_id('f' + str(fid))
        fspan = Cspan()
        fspan.add_target_id(tid)
        fnode.set_span(fspan)
        for fval in v:
            add_factvalues(fval.factuality, fval.resource, fnode, fval.source)
            myFactualityLayer.add_factuality(fnode)

    #add factuality node to parser
    nafobj.root.append(myFactualityLayer.get_node())
    nafobj.factuality_layer = myFactualityLayer


def get_fact_info_from_naf(factVal):
    
    myFactVal = cFactValLocal(factuality=factVal.get_value(),resource=factVal.get_resource())

    return myFactVal

def initiate_fact_dict_from_previous_naf(nafobj, info_per_term):

    mysource = ''
    if nafobj.header != None:
        for lps in nafobj.header.node.findall('linguisticProcessors'):
            if lps.get('layer') == 'factualities':
                for lp in lps.getchildren():
                    mysource = lp.get('name') +  '-' + lp.get('version')


    factDictTense = {}
    for facts in nafobj.get_factualities():
        tId = facts.get_span().get_span_ids()[0]
        for factVal in facts.get_factVals():
            fVal = get_fact_info_from_naf(factVal)
            if mysource != None:
                fVal.set_source(mysource)
            if not tId in factDictTense:
                factDictTense[tId] = [fVal]
            else:
                factDictTense[tId].append(fVal)
    #We now assume we only need factDictTense if no factuality values have been found (may change in the future)
    if len(factDictTense) == 0:
        factDictTense = initiate_fact_dict_from_previous_terms(info_per_term)

    return factDictTense

def initiate_fact_dict_from_previous_terms(info_per_term):
    
    factDict = {}
    head2dep = {}
    for featobj in info_per_term:
        #FIXME: FOR NOW ONLY TAKING THE FIRST TERM IN A SPAN
        if featobj.eventTag == 'BEvent':
            mytid = featobj.tid
            factList = []
            factVal = cFactValLocal(resource='nwr:attributionTense')
            if featobj.morphofeat in ['VBD','VBP','VBZ','VBN']:
                factVal.factuality = 'NON_FUTURE'
            else:
                factVal.factuality = 'UNDERSPECIFIED'
                if not featobj.dephead in head2dep:
                    head2dep[featobj.dephead] = [mytid]
                else:
                    head2dep[featobj.dephead].append(mytid)
            factList.append(factVal)
            factDict[mytid] = factList
            
    # make events headed by a future marking modal or auxiliary future 
    for head in info_per_term:
        if head.tid in head2dep:
            deps = head2dep.get(head.tid)
            if head.lemma == 'will' or (head.lemma in ['go','become'] and not head.word in ['went', 'gone','became']):
                factVal = cFactValLocal(resource='nwr:attributionTense')
                factVal.factuality = 'FUTURE'
                for dep in deps:
                    factDict[dep] = [factVal]
            elif head.morphofeat in ['VBD','VBP','VBZ','VBN']:
                factVal = cFactValLocal(resource='nwr:attributionTense')
                factVal.factuality = 'NON_FUTURE'
                for dep in deps:
                    factDict[dep] = [factVal]         
    return factDict








def main(argv=None):

    if argv == None:
        argv = sys.argv[1:]
        optlist, argv = getopt.getopt(argv, 't:p:m:')
        #set default options for script path and timbl
        rootpath = ''
        timblcommand = 'timbl'
        model = 'timbl.factuality.model.wgt'
        versionnr='1.1'
        source = ''
        if len(optlist) > 0:
            for o, a in optlist:
                if o == '-t':
                    timblcommand = a
                elif o == '-p':
                    rootpath = a
                    if not rootpath.endswith('/'):
                        rootpath += '/'
                elif o == '-m':
                    model = a
                    versionnr += '.' + model
                    source = 'vua-perspectives_factuality-' + versionnr
    if len(argv) < 1:   
        print('Please provide path to tmp folder to store feature output,\n if you want to generate features for several files at the same time, add "T" as a second argument')
    else:    
        
        begintime = time.strftime('%Y-%m-%dT%H:%M:%S%Z')
        tmpdir = argv[0]
        if not tmpdir.endswith('/'):
            tmpdir += '/'
        nafobj = KafNafParser(sys.stdin)
        docId, info_per_term = extract_features(nafobj)
        if docId == None:
            docId = 'docId_dummy'
        if len(argv) > 1 and 'T' in argv[1]:
            print_out_features(docId, info_per_term, tmpdir, True)
        else:
            print_out_features(docId, info_per_term, tmpdir)

        #collect tense information from naf file or factuality information already present
        factDictTense = initiate_fact_dict_from_previous_naf(nafobj, info_per_term)
        #renumerate files
        my_renum_call = ['perl', rootpath + 'scripts/renumber.features.file.pl', '-d', tmpdir]
        call(my_renum_call)
        #create input for machine learning in tmpdir
        my_inst_call = ['perl', rootpath + 'scripts/generate.instances.factuality.forsystem.pl', '-d', tmpdir, '-o', tmpdir]
        call(my_inst_call)
        #call machine learner
        ml_output = tmpdir + '/myoutput.tsv'
        mytimbl_call = [timblcommand, '-mO:I1,2,3,4', '-k3', '-i', rootpath + model, '-t', tmpdir + '/features.tsv.renumbered.inst', '-o',  ml_output]
        timblout = open(tmpdir + '/timblout', 'w')
        call(mytimbl_call,stdout=timblout)
        timblout.close()
        #add output from machine learning to NAF file to factDictTense, ontology set to 'both' as default for now
        factDict = add_factuality_info_from_output(ml_output, 'both', factDictTense, source)
        #update and output nafobj
        update_naflayer(nafobj, factDict)
        
        endtime = time.strftime('%Y-%m-%dT%H:%M:%S%Z')
        lp = Clp(name="vua-perspectives_factuality",version=versionnr,btimestamp=begintime)
        nafobj.add_linguistic_processor('factualities', lp)
        #provide new naf
        nafobj.dump()



if __name__ == '__main__':
    main()
