#!/usr/bin/env python

import io
import json
import sys
import os
from xml.dom import minidom


OUTPUT_FILE = 'pathway_groups.json'

SUBSYSTEMS = [
   {'name': "Central Core Carbon", 
    'maps': [{'id': "map00010", 'name': "Glycolysis / Gluconeogenesis", "rxns": []},
          {'id': "map00020", 'name': "Citrate cycle (TCA cycle)", "rxns": []},
          {'id': "map00030", 'name': "Pentose phosphate pathway", "rxns": []}],
    'rxns': []},

   {'name': "Aromatic and Branched Chain",
    'maps': [{'id': "map00290", 'name': "Valine, leucine and isoleucine biosynthesis", "rxns": []},
          {'id': "map00400", 'name': "Phenylalanine, tyrosine and tryptophan biosynthesis", "rxns": []}],
    'rxns': []},

   {'name': "Cell Wall Biosynthesis", 
    'maps': [{'id': "map00550", 'name': "Peptidoglycan biosynthesis", "rxns": []}],
    'rxns': []},

   {'name': "Quinone Biosynthesis", 
    'maps': [{'id': "map00130", 'name': "Ubiquinone and other terpenoid-quinone biosynthesis", "rxns": []}],
    'rxns': []}
]

def get_subsystems():
    for subsystem in SUBSYSTEMS:
        maps = subsystem['maps']
        print subsystem['name']
        subsystems_rxns = []
        for map_obj in maps:
            map_id = map_obj['id']
            print map_id
            json_str = open('xml/'+map_id+"_bio.json").read()
            obj = json.loads(json_str)
            map_obj['rxns'] = obj['reactions']
            #subsystem['rxns'] += obj['reactions']
        print

    with open(OUTPUT_FILE, 'w') as file:
        file.write(json.dumps(SUBSYSTEMS))

    print 'wrote to:', OUTPUT_FILE

if __name__ == "__main__":

    get_subsystems()
    print 'done.'
