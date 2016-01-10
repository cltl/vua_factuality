# vua_factuality


This is the first version of the vua-perspectives-factuality module.
The module is currently under development.
Any questions should be directed to:

Roser Morante (r.morantevallejo@vu.nl) and/or
Antske Fokkens (antske.fokkens@vu.nl)

Basic information:

- This module is trained on factuality annotations from FactBank.
- It consists of a NAF wrapper and timbl machine learning module.
- It takes NAF with (at least):
 1. a token layer
 2. a term layer with PoS tags and (optionally) externalRefs
 3. a dependency layer 
 4. a coref layer with events
 5. a srl layer (with optionally externalRefs).
- It outputs a NAF file with an additional factualities layer. Currently this layer provides: 
  * a span
  * a factbank attribute and value
  * NWR_attribution attributes and values derived from factbank value indicating certainty and polarity
  * NWR_attribution attribute and value indicating tense deducted from tense marking and dependency structure


Dependencies:

- KafNafParserPy (latest version): https://github.com/cltl/KafNafParserPy
- timbl: http://ilk.uvt.nl/timbl/


Running the module:

cat input_naf | python vua_factuality_naf_wrapper.py [-t path_to_timbl] [-p path_to_root_dir] tmp/ > output_naf

where tmp/ is a path to a directory temporal files can be written to. 
Option [-t path_to_timbl] allows you to specify where timbl is installed (default will assume timbl can be run anywhere using command 'timbl').
E.g. if timbl can be found at /tmp/opt/bin/timbl, you specify -t /tmp/opt/bin
Option [-p path_to_root_dir] allows you to specify the path to the location of the module, where the scripts/ folder is found (with necessary perl scripts) and where the machine learning model can be found. This option should be used when running the module from another directory.

License

Apache v2. See LICENSE.txt for details.
