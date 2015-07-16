'''
Created on July 8, 2015

@author: antske
'''

from KafNafParserPy import *
from subprocess import call
import sys


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
            print 'Problem: this term has more than one head'
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
            newline += '\t' + ft
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



def add_factvalues(value, resource, fnode):
    '''
    Adds a new factuality value to the factuality node
    '''
    
    fVal = Cfactval()
    fVal.set_resource(resource)
    fVal.set_value(value)
    fnode.add_factval(fVal)
    
    
    
def add_factuality_info_from_output(fn, onto, factDict):
    '''
    Goes through machine learning output and adds information from this output to factDict
    '''
    myfactuality = open(fn, 'r')
    for line in myfactuality:
        parts = line.split()
        mytid = parts[2]
        if mytid in factDict:
            factObj = factDict.get(mytid)
        else:
            factObj = cFactObject(tid=mytid)
        val = parts[-1]
        if onto == 'both':
            #factBank is source of direct value
            factVal_fb = cFactValLocal(factuality=val,resource='factbank')
            factObj.add_factval(factVal_fb)
            ctval, polval = translate_values(val)
            fVal_ct = cFactValLocal(factuality=ctval,resource='nwr:attributionCertainty')
            fVal_pol = cFactValLocal(factuality=polval,resource='nwr:attributionPolarity')
            factObj.add_factval(fVal_ct)
            factObj.add_factval(fVal_pol)
        else:
            my_factval = cFactValLocalLocal(factuality=val, resource=onto)
            factObj.add_factval(my_factval)
        #set value in factDict (may be new)
        factDict[mytid] = factObj
    myfactuality.close()
    return factDict

def update_naflayer(nafobj, factDict):
    '''
    Takes newly collected factuality information and adds this to the factuality layer
    '''
    myFactualityLayer = Cfactualities()
    fid = 0
    for tid, v in factDict.items():
        fid += 1
        fnode = Cfactuality()
        fnode.set_id('f' + str(fid))
        fspan = Cspan()
        fspan.add_target_id(tid)
        fnode.set_span(fspan)
        for fval in v.factVals:
            add_factvalues(fval.factuality, fval.resource, fnode)
        myFactualityLayer.add_factuality(fnode)    
    
    nafobj.factuality_layer = myFactualityLayer

            

def initiate_fact_dict_from_previous_naf(info_per_term):
    
    factDict = {}
    head2dep = {}
    for featobj in info_per_term:
        #FIXME: FOR NOW ONLY TAKING THE FIRST TERM IN A SPAN
        if featobj.eventTag == 'IEvent':
            mytid = factobj.tid
            factObj = cFactObject(tid=mytid)
            factObj.span = [mytid]
            factVal = cFactValLocal(resource='nwr:attributionTense')
            if featobj.morphofeat in ['VBD','VBP','VBZ','VBN']:
                factVal.factuality = 'NON_FUTURE'
            else:
                factVal.factuality = 'UNDERSPECIFIED'
                if not featobj.dephead in head2dep:
                    head2dep[featobj.dephead] = [mytid]
                else:
                    head2dep[featobj.dephead].append(mytid)
            factObj.add_factval(factVal)
            factDict[mytid] = factObj
            
    # make events headed by a future marking modal or auxiliary future 
    for head, deps in head2dep.items():
        if head.lemma == 'will' or (head.lemma in ['go','become'] and not head.word in ['went', 'gone','became']):
            for dep in deps:
                factDict[dep].factuality = 'FUTURE'
        elif head.morphofeat in ['VBD','VBP','VBZ','VBN']:
            for dep in deps:
                factDict[dep].factuality = 'NON_FUTURE'
            
                
    return factDict



def main(argv=None):

    if argv == None:
        argv = sys.argv
    if len(argv) < 2:   
        print 'Please provide path to tmp folder to store feature output,\n if you want to generate features for several files at the same time, add "T" as a second argument'
    else:    
        tmpdir = argv[1]
        nafobj = KafNafParser(sys.stdin)
        docId, info_per_term = extract_features(nafobj)
        if len(argv) > 2 and 'T' in argv[2]:
            print_out_features(docId, info_per_term, tmpdir, True)
        else:
            print_out_features(docId, info_per_term, tmpdir)
        #collect tense information from naf file
        factDictTense = initiate_fact_dict_from_previous_naf(info_per_term)
        #renumerate files
        my_renum_call = ['perl', 'scripts/renumber.features.file.pl', '-d', tmpdir]
        call(my_renum_call)
        #create input for machine learning in tmpdir
        my_inst_call = ['perl', 'scripts/generate.instances.factuality.forsystem.pl', '-d', tmpdir, '-o', tmpdir]
        call(my_inst_call)
        #call machine learner
        ml_output = tmpdir + '/myoutput.tsv'
        mytimbl_call = ['timbl', '-mO:I1,2,3,4', '-k3', '-i', 'timbl.factuality.model.wgt', '-t', tmpdir + '/features.tsv.renumbered.inst', '-o',  ml_output, '>', 'tmp/timblout']
        call(mytimbl_call)
        #add output from machine learning to NAF file to factDictTense, ontology set to 'both' as default for now
        factDict = add_factuality_info_from_output(ml_output, 'both', factDictTense)
        #update and output nafobj
        update_naflayer(nafobj, factDict)
        nafobj.dump()



if __name__ == '__main__':
    main()