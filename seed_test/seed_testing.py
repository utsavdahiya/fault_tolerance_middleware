import random
import numpy as np
from collections import defaultdict, Counter
import pickle

START_SEED = 0
NUM_LOCATIONS = 4
NUM_VM_SET = 200
SET_SIZE = 3
NUM_ITERATIONS = 1
OUTPUT_FILE = './default_output.pkl'

def place_vm(seed_result, loc_result, togetherness_result):
    location_array = [i for i in range(NUM_LOCATIONS)]
    seed = START_SEED
    for i in range(NUM_ITERATIONS):
        print("Iter start------------------")
        random.seed(seed)

        #now place the sets
        for Set in range(NUM_VM_SET):
            togetherness = {}
            placement = [0] * NUM_LOCATIONS 
            for vm in range(SET_SIZE):
                loc = random.choice(location_array)
                placement[loc] += 1
            #now calc togetherness of this placement
            for loc in range(NUM_LOCATIONS):
                num = placement[loc]
                if(num == 1):
                    if(togetherness.get(0, None)):
                        togetherness[0] += 1
                    else:
                        togetherness[0] = 1
                else:
                    #if any are together
                    if togetherness.get(num, None):
                        togetherness[num] += 1
                    else:
                        togetherness[num] = 1

            #calculating score for this
            score = 0
            for key, val in togetherness.items():
                score += key * val  #a weighted sum of the togetherness

            #updating the result
            loc_result = [sum(i) for i in zip(loc_result, placement)]
            togetherness_result = Counter(togetherness_result) + Counter(togetherness)
            seed_val = {'score':score,
                        'togetherness': togetherness,
                        'placement': placement}

            seed_result.append(seed_val)
        
        seed += 1
    return seed, loc_result, togetherness_result

def main():
    seed_result = []
    loc_result = [0] * NUM_LOCATIONS
    togetherness_result = {}
    for i in range(SET_SIZE+1):
        if i==1:
            continue
        else:
            togetherness_result[i] = 0

    end_seed, loc_result, togetherness_result = place_vm(seed_result, loc_result, togetherness_result)
    print(f"ENDING at seed: {end_seed}")

    sorted(seed_result, reverse=True, key=lambda seed: seed['score'])
    store = {'seed_result':seed_result,
               'loc_result': loc_result,
               'togetherness_result': togetherness_result}
    print(f"store: \n{store}")
    #writing the results to output file
    with open(OUTPUT_FILE, '+wb') as handle:
        print("file opened")
        store = pickle.dump(store, handle)

main()