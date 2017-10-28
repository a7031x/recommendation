import dataset
import math

def sim_distance(prefs, p1, p2):
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1

    if len(si) is 0:
        return 0

    sum_of_squares = sum([math.pow(prefs[p1][item] - prefs[p2][item], 2) for item in si])
    return 1 / (1 + math.sqrt(sum_of_squares))


def sim_pearson(prefs, p1, p2):
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1

    n = len(si)
    if n is 0:
        return 0

    sum1 = sum([prefs[p1][x] for x in si])
    sum2 = sum([prefs[p2][x] for x in si])

    sum1_2 = sum([pow(prefs[p1][x], 2) for x in si])
    sum2_2 = sum([pow(prefs[p2][x], 2) for x in si])

    xsum = sum([prefs[p1][x] * prefs[p2][x] for x in si])

    num = xsum - sum1 * sum2 / n
    den = math.sqrt((sum1_2 - sum1 * sum1 / n) * (sum2_2 - sum2 * sum2 / n))
   
    if den == 0:
        return 0

    return num / den


def sim_tanimoto(prefs, p1, p2):
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1

    n = len(si)
    if n is 0:
        return 0

    sum1_2 = sum([pow(prefs[p1][x], 2) for x in si])
    sum2_2 = sum([pow(prefs[p2][x], 2) for x in si])

    xsum = sum([prefs[p1][x] * prefs[p2][x] for x in si])

    return xsum / (sum1_2 + sum2_2 - xsum)


#1.0 means no overlap. 0.0 means full overlap
def tanimoto(v1, v2):
    c1,c2,shr=0,0,0

    for i in range(len(v1)):
        if v1[i]!=0: c1+=1 # in v1
        if v2[i]!=0: c2+=1 # in v2
        if v1[i]!=0 and v2[i]!=0: shr+=1 # in both

    return 1.0-(float(shr)/(c1+c2-shr))


def manhattan(v1, v2):
    num = sum([abs(x - y) for x, y in zip(v1, v2)])
    den = sum([x + y for x, y in zip(v1, v2)])
    return num / den


def sim_manhatten(v1, v2)
    return 1 - manhattan(v1, v2)


def top_matches(prefs, person, n, sim_func):
    scores = [(sim_func(prefs, person, other), other) for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]


def get_recommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    sim_sums = {}

    for other in prefs:
        if other == person:
            continue

        sim = similarity(prefs, person, other)
        if 0 >= sim:
            continue

        for item in prefs[other]:
            if item not in prefs[person] or prefs[person][item] == 0:
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim

                sim_sums.setdefault(item, 0)
                sim_sums[item] += sim

    rankings = [(total / sim_sums[item], item) for item, total in totals.items()]
    rankings.sort()
    rankings.reverse()
    return rankings


def transform_prefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            result[item][person] = prefs[person][item]
    return result


def sim_items(prefs, n):
    result = {}
    item_prefs = transform_prefs(prefs)
    c = 0
    for item in item_prefs:
        c += 1
        if c % 100 == 0:
            print('{} / {}'.format(c, len(item_prefs)))

        scores = top_matches(item_prefs, item, n, sim_distance)
        result[item] = scores

    return result


def get_recommended_items(prefs, item_match, user):
    user_ratings = prefs[user]
    scores = {}
    total_sim = {}

    for item, rating in user_ratings.items():
        for similarity, item2 in item_match[item]:
            if item2 in user_ratings:
                continue

            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating

            total_sim.setdefault(item2, 0)
            total_sim[item2] += similarity

    rankings = [(score/total_sim[item], item) for item, score in scores.items()]
    rankings.sort()
    rankings.reverse()
    return rankings