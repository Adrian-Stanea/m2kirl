# m2kirl

Resources for the ADALM2000 in real life workshop

Folder structure

- /bash       - command line scripts to interact with m2k and ad5592r
- /decoder    - decoder files - ad5592r used in the workshop and min_decoder boilerplate
- /dt         - devicetree related files - config.txt, dt sources, dt binaries
- /py         - python scripts for the workshop
- /res        - various resources such as keyboard configuration

How to use:

- make_zip.sh    - create a zip file that can be copied to the target
- deploy_zip.sh  - file to be used on target to inflate the system

Warning: 
- the scripts may change the current date&time
