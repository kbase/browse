#!/usr/bin/env python

import io
import json
import sys
import os
from xml.dom import minidom

import wsclient

# this is the kegg rxn/cpds to seed mapping json files.
with open('rxn_mapping.json') as file:
    json_str = file.read()
    rxn_mapping = json.loads(json_str)

with open('cpd_mapping.json') as file:
    json_str = file.read()
    cpd_mapping = json.loads(json_str)

MAPSJSON = []

def data_to_json(file_name):
    print 'Converting reactions/compounds from file:', file_name
    try:
        xmldoc = minidom.parse(file_name)
    except: 
        sys.stderr.write("could not parse xml file: "+file_name+'\n')
        return


    itemlist = xmldoc.getElementsByTagName('pathway')

    try:
        name = itemlist[0].attributes['title'].value
    except:
        name = "None"

    map_number = itemlist[0].attributes['number'].value
    link = itemlist[0].attributes['link'].value

    rxns = []
    cpds = []

    entries = xmldoc.getElementsByTagName('entry')

    for obj in entries :
        if (obj.attributes['type'].value == 'group'):
            continue

        if (obj.attributes['type'].value == 'enzyme'
            and obj.getElementsByTagName('graphics')):
            try:
                obj.attributes['reaction'].value
            except:
                continue

            # get list of kegg rxn ids from the entry
            kegg_rxns = obj.attributes['reaction'].value \
                           .replace('rn:','').split(' ')

            # for each kegg_rxn, get the seed rxn id, add to list
            for kegg_rxn in kegg_rxns:
                try:
                    seed_rxn = rxn_mapping[kegg_rxn]
                    rxns.append( seed_rxn )
                except:
                    sys.stderr.write("Warning: [Converting "+file_name+
                        "] Could not find seed rxn id for KEGG id: "+kegg_rxn+'\n')
                    rxns.append( kegg_rxn )

        elif (obj.attributes['type'].value == 'compound'
            and obj.getElementsByTagName('graphics') ):

            e_obj = obj.attributes

            kegg_cpds = e_obj['name'].value \
                           .replace('cpd:','').split(' ') 

            for kegg_cpd in kegg_cpds:
                try:
                    # replace this with seed mapping result in future
                    seed_cpd = cpd_mapping[kegg_cpd]
                    cpds.append( seed_cpd )
                except:
                    sys.stderr.write("Warning: [Converting "+file_name+
                        "] Could not find seed cpd id for KEGG id: "+kegg_cpd+'\n')
                    cpds.append( kegg_cpd )


    map_obj = {'name': name,
                'map':'map'+map_number,
                'link': link,
                }
    map_obj['reaction_count'] = len(rxns)
    map_obj['compound_count'] = len(cpds)
    MAPSJSON.append(map_obj)

    json_obj = {'name': name,
                'map':'map'+map_number,
                'link': link,
                }
    json_obj['reactions'] = rxns
    json_obj['compounds'] = cpds


    #print json_obj

    json_file = file_name.replace('.xml', '_bio.json')
    outfile = open(json_file, 'w')
    json.dump(json_obj, outfile)
    print "Reaction/Compound ids converted to:", json_file

    outfile = open('maps.json', 'w')
    json.dump(MAPSJSON, outfile)    


def graph_to_json(file_name):
    print 'Converting graph data from file:', file_name

    try:
        xmldoc = minidom.parse(file_name)
    except: 
        sys.stderr.write("could not parse xml file: "+file_name+'\n')
        return


    itemlist = xmldoc.getElementsByTagName('pathway')

    try:
        name = itemlist[0].attributes['title'].value
    except:
        name = "None"

    map_number = itemlist[0].attributes['number'].value


    link = itemlist[0].attributes['link'].value

    json_obj = {'id': 'map'+map_number,
                'name': name,
                'link': link,
                'source_id': 'map'+map_number,
                'source': 'KEGG',
                'reactions':[],
                'compounds':[],
                'reaction_ids': [],
                'compound_ids': [],
                'linkedmaps': []
                }

    entries = xmldoc.getElementsByTagName('entry') 
    reaction_ids = []
    compound_ids = []

    for obj in entries:
        if (obj.attributes['type'].value == 'group'):
            continue

        #<entry id="41" name="path:ec00030" type="map"
        #     link="http://www.kegg.jp/dbget-bin/www_bget?ec00030">
        #     <graphics name="Pentose phosphate pathway" fgcolor="#000000" bgcolor="#FFFFFF"
        #          type="roundrectangle" x="656" y="339" width="62" height="237"/>
        # </entry>


        #string id;
        #map_ref map_ref;
        #string name;
        #string shape;
        #string link;
        #int h;
        #int w;
        #int y;
        #int x;
        #map_id map_id;

        if (obj.attributes['type'].value == 'map'):
            e_obj = obj.attributes
            g_obj = obj.getElementsByTagName('graphics')[0].attributes

            obj = {"id": e_obj['id'].value,
                   "shape": g_obj['type'].value,
                   "name": g_obj['name'].value,
                   "h": g_obj['height'].value,
                   "w": g_obj['width'].value,
                   "x": g_obj['x'].value,
                   "y": g_obj['y'].value,
                  }
            name = e_obj['name'].value;

            if 'ec' in name:
                name = name.split('ec')[1]
            elif 'map' in name:
                name = name.split('map')[1]

            obj['map_id'] = 'map'+name
            obj['map_ref'] = name   


            json_obj['linkedmaps'].append(obj)
            continue


        if (obj.attributes['type'].value == 'enzyme'
            and obj.getElementsByTagName('graphics')):

            try:
                obj.attributes['reaction'].value
            except:
                continue

            e_obj = obj.attributes

            # get list of kegg rxn ids from the entry
            kegg_rxns = e_obj['reaction'].value \
                           .replace('rn:','').split(' ')


            reactions = xmldoc.getElementsByTagName('reaction')  # substrate and product data from kgml
            # for each kegg_rxn, get the seed rxn id, add to list
            rxns = []
            for kegg_rxn in kegg_rxns:
                try:
                    rxn_id = rxn_mapping[kegg_rxn]
                except:
                    sys.stderr.write("Warning: [Converting "+file_name+
                        "] Could not find seed rxn id for KEGG id: "+kegg_rxn+'\n')
                    rxn_id = kegg_rxn
                rxns.append(rxn_id)

                reaction_ids.append(rxn_id)

                for reaction in reactions:

                    r_obj = reaction.attributes
                    #rn_ids = r_obj['name'].value.split(' ')
                    #rn_ids = [id.split(':')[1] for id in rn_ids]
                    #print rn_ids

                    if r_obj['id'].value == e_obj['id'].value:

                        substrates = [] 
                        for substrate in reaction.getElementsByTagName('substrate'):
                            s_obj = {'id': substrate.attributes['id'].value,
                                     'cpd':  substrate.attributes['name'].value.split(':')[1] }
                            substrates.append(s_obj)

                        products = []
                        for product in reaction.getElementsByTagName('product'):
                            p_obj = {'id': product.attributes['id'].value,
                                     'cpd':  product.attributes['name'].value.split(':')[1] }
                            products.append(p_obj)

                        break     

                    #json_obj['arrows'].append(obj)


            g_obj = obj.getElementsByTagName('graphics')[0].attributes

            try:
                link = e_obj['link'].value           
            except:
                sys.stderr.write("Warning: [Converting "+file_name+
                    "] Could not find link for reaction: "+kegg_rxn+'\n')
                pass

            x = y = h = w = False
            try:
                x = int(g_obj['x'].value)
                y = int(g_obj['y'].value)
                h = int(g_obj['height'].value)
                w = int(g_obj['width'].value)
            except:
                sys.stderr.write("Warning: [Converting "+file_name+
                    "] Could not find coordinates for reaction: "+kegg_rxn+'\n')
                pass                

            obj = {"id": e_obj['id'].value,
                    "rxns": rxns,
                   "ec": e_obj['name'].value,
                   "shape": g_obj['type'].value,
                   "name": g_obj['name'].value,
                   }
            try:
                if substrates: obj['substrates'] = substrates
                if products: obj['products'] = products
            except:
                sys.stderr.write("Warning: [Converting "+file_name+
                    "] Could not find substrates and/or products for: "+kegg_rxn+'\n')                

            if link: obj['link'] = link
            if x: obj['x'] = x
            if y: obj['y'] = y
            if h: obj['h'] = h
            if w: obj['w'] = w

            json_obj['reactions'].append(obj)

        elif (obj.attributes['type'].value == 'compound'
            and obj.getElementsByTagName('graphics') ):

            e_obj = obj.attributes

            kegg_cpds = e_obj['name'].value \
                           .replace('cpd:','').split(' ')   


            # for each kegg_rxn, get the seed rxn id, add to list
            cpds = []
            for kegg_cpd in kegg_cpds:
                try:
                    # replace this with seed mapping result in future
                    cpd_id = cpd_mapping[kegg_cpd]  #  get seed_id
                except:
                    sys.stderr.write("Warning: [Converting "+file_name+
                        "] Could not find seed cpd id for KEGG id: "+kegg_cpd+'\n')
                    cpd_id = kegg_cpd

                cpds.append( cpd_id )

                compound_ids.append(cpd_id)                   

            g_obj = obj.getElementsByTagName('graphics')[0].attributes
            obj = {"id": e_obj['id'].value,
                   "name": g_obj['name'].value,            
                   "cpds": cpds,
                   "ec": e_obj['name'].value,
                   "link": e_obj['link'].value,
                   "shape": g_obj['type'].value,
                   "x": int(g_obj['x'].value),
                   "y": int(g_obj['y'].value),
                   "h": int(g_obj['height'].value),
                   "w": int(g_obj['width'].value),
                   "link_refs": []       #fixme: I don't know what this is...
                   }

            json_obj['compounds'].append(obj)

        #print json_obj
 
    
    json_obj['reaction_ids'] = reaction_ids
    json_obj['compound_ids'] = compound_ids

    #print json_obj

    json_file = file_name.replace('.xml', '_graph.json')
    outfile = open(json_file, 'w')
    json.dump(json_obj, outfile)
    print "Graph data converted to:", json_file


def save_kegg_object(map_id):
    ws = wsclient.Workspace()

    json_data=open('xml/'+map_id+'_graph.json')
    data = json.load(json_data)
    print data
    

    test= ws.save_object({'workspace': 'nconrad:paths', 
                    'data': data, 
                    'id': map_id,
                    'type': 'KBaseBiochem.MetabolicMap'
                    })
    
    print test

# this function attempts to convert all .xml files in the current directory
def convert_all_data():
    os.chdir('xml')

#    print '\n\n*** Converting reactions and compounds ***\n'
#    for name in os.listdir(os.getcwd()):
#        if name.endswith('.xml'):
#            data_to_json(name)

    print '\n\n*** Converting graph data ***\n'

    for name in os.listdir(os.getcwd()):
        if name.endswith('.xml'):
            graph_to_json(name)            
    


if __name__ == "__main__":

    #ws = wsclient.Workspace()
    # workspaces = ws.list_workspaces({})
    
    # for arr in workspaces:
    #     if str(arr[1]) != 'nconrad': continue
    
    #     print str(arr)  + '\n'

    
    if (sys.argv[1] == 'save'):
        save_kegg_object('map00010')
    elif (sys.argv[1] == 'convert'):
        convert_all_data()

    #convert_all_data()

    # use one of these to convert a single file

    #data_to_json(sys.argv[1])
    #graph_to_json(sys.argv[1])

    print 'Done.'



