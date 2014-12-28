import os

def return_parse(content, lvl, nxt, parse):
    '''
    '''
    actorDict = {}
    parsed = str()
    key = str()
    value = str()
    values = list()

    for line in range(lvl, nxt):
        if content[line].startswith(parse):
            parseLine = content[line].strip(parse + ' = ')

            item = 0
            actorDict = {}
            actorDict[(parse + str(item))] = {}
            for i in range(len(parseLine)):
                if parseLine[i].isalnum() or parseLine[i] == ('-') or parseLine[i] == ('.'):
                    parsed += parseLine[i]
                elif parseLine[i] == (':'):
                    key = parsed
                    parsed = str()
                elif parseLine[i] == (',') or parseLine[i] == (' ') or parseLine[i] == ('}'):
                    try:
                        values.append(float(parsed))
                    except:
                        values.append(parsed)
                    parsed = str()
                    if parseLine[i] == (' ') or parseLine[i] == ('}'):
                        if len(values) == 1:
                            value = values[0]
                        else:
                            value = values
                        values = []
                        actorDict[(parse + str(item))][key] = value
                        key == str()
                        value == str()
                        if parseLine[i] == ('}'):
                            item += 1
                            actorDict[(parse + str(item))] = {}
    for key,value in actorDict.items():
        if value == {}:
            actorDict.pop(key)
    if parse == 'Variables':
        actorDict = actorDict[parse + str(0)]
        #actorDict.pop(parse + str(0))
    return actorDict

'''
Flan = {flav:vla}{flav:vla}{flav:chl size:w,h stab:45,45,75}
Floor = {cent:x,y size:w,h rotation:# mat:XXX}{cent:x,y size:w,h rotation:# mat:XXX alt:start}

Flan0 = {flav: vla}
Flan1 = {flav: vla}
Flan2 = {flav: chl,
         size: (w,h),
         stab: [45,45,75]}
Floor0 = {cent: (x,y),
          size: (w,h),
          rotation: #,
          mat: XXX}
Floor1 = {cent: (x,y),
          size: (w,h),
          rotation: #,
          mat: XXX,
          alt: start}
Variables = {pEnergy: #,
             gravity: #,
             push: #
             }
'''
            
def read_level(filename, mapLvl):
    mapFile = open(os.path.join('Levels',filename+'.txt'))  # open the passed filename
    content = mapFile.readlines()
    mapFile.close()
    level = {}

    for line in range(len(content)):    # find on what line the passed level begins
        if content[line].startswith('Level '+ str(mapLvl)):
            lvl = line
        elif content[line].startswith('Level ' + str(mapLvl + 1)) or content[line].startswith('END'):
            nxt = line
            break
    
    
    level['fruitList'] = return_parse(content, lvl, nxt, 'Fruit')
    level['floorList'] = return_parse(content, lvl, nxt, 'Floor')
    level['obsticles'] = return_parse(content, lvl, nxt, 'Obsticles')
    #level['image'] = return_parse(content, lvl, nxt, 'Image')
    level['variables'] = return_parse(content, lvl, nxt, 'Variables')
    level['flanList'] = return_parse(content, lvl, nxt, 'Flan')

    #print(level)
        
    return level

def save_level(filename, mapLvl, actors, floors):
    '''
    '''
    mapFile = open((os.path.join('Levels',filename + '.txt')))
    content = mapFile.readlines()
    mapFile.close()

    #lstFloors = 
    
