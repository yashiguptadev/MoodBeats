"""MoodTune recommendation algorithms. All numerical features are 0..1."""
import math
import random
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

MOODS = ['happy', 'sad', 'calm', 'energetic', 'romantic']
GENRES = ['Bollywood', 'Pop', 'Rock', 'Instrumental']
# Curated demonstration metadata, not extracted from audio files.
SONGS = [
 ('Ilahi','Arijit Singh','Bollywood',.82,.86,'happy'),
 ('Love You Zindagi','Jasleen Royal','Bollywood',.72,.87,'happy'),
 ('Happy','Pharrell Williams','Pop',.94,.96,'happy'),
 ('On Top of the World','Imagine Dragons','Rock',.88,.90,'happy'),
 ('Someone Like You','Adele','Pop',.25,.14,'sad'),
 ('Agar Tum Saath Ho','Alka Yagnik & Arijit Singh','Bollywood',.35,.19,'sad'),
 ('Channa Mereya','Arijit Singh','Bollywood',.52,.22,'sad'),
 ('Fix You','Coldplay','Rock',.36,.26,'sad'),
 ('Weightless','Marconi Union','Instrumental',.12,.55,'calm'),
 ('River Flows in You','Yiruma','Instrumental',.23,.61,'calm'),
 ('Kun Faya Kun','A.R. Rahman','Bollywood',.33,.63,'calm'),
 ('Experience','Ludovico Einaudi','Instrumental',.42,.57,'calm'),
 ('Believer','Imagine Dragons','Rock',.97,.74,'energetic'),
 ('Zinda','Siddharth Mahadevan','Bollywood',.95,.77,'energetic'),
 ('Eye of the Tiger','Survivor','Rock',.94,.78,'energetic'),
 ('Titanium','David Guetta ft. Sia','Pop',.93,.72,'energetic'),
 ('Perfect','Ed Sheeran','Pop',.37,.78,'romantic'),
 ('Tum Hi Ho','Arijit Singh','Bollywood',.42,.70,'romantic'),
 ('All of Me','John Legend','Pop',.36,.72,'romantic'),
 ('Raabta','Arijit Singh','Bollywood',.58,.81,'romantic'),
]
CATALOG = [dict(id=i,title=t,artist=a,genre=g,energy=e,valence=v,mood=m) for i,(t,a,g,e,v,m) in enumerate(SONGS)]
TARGETS = {'happy':(.77,.88),'sad':(.30,.20),'calm':(.22,.58),'energetic':(.94,.76),'romantic':(.44,.76)}

def triangle(x,a,b,c):
    if x == b: return 1.0
    if x <= a or x >= c: return 0.0
    return (x-a)/(b-a) if x < b else (c-x)/(c-b)

def fuzzy_memberships(energy,valence):
    # Soft, overlapping membership functions. Mood is not treated as a medical assessment.
    return {
      'happy': min(triangle(valence,.38,.88,1.1), triangle(energy,.25,.78,1.2)),
      'sad': min(triangle(valence,-.2,.17,.62), triangle(energy,-.2,.29,.75)),
      'calm': min(triangle(energy,-.2,.22,.67), triangle(valence,.22,.59,.95)),
      'energetic': min(triangle(energy,.48,.95,1.2), triangle(valence,.35,.76,1.15)),
      'romantic': min(triangle(energy,.12,.43,.82), triangle(valence,.42,.76,1.1))
    }

def features(song):
    return [song['energy'],song['valence']] + [int(song['genre']==g) for g in GENRES]

# Demonstration supervised classifier trained on small labeled catalogue; not a pre-trained music model.
scaler = StandardScaler()
X = scaler.fit_transform([features(s) for s in CATALOG])
model = MLPClassifier(hidden_layer_sizes=(12,8),solver='lbfgs',random_state=42,max_iter=1200)
model.fit(X,[s['mood'] for s in CATALOG])

def score(song,mood,genre,energy):
    te,tv=TARGETS[mood]
    heuristic = .52*(1-abs(song['energy']-energy)) + .28*(1-abs(song['valence']-tv)) + .20*(genre=='Any' or genre==song['genre'])
    fuzzy = fuzzy_memberships(song['energy'],song['valence'])[mood]
    proba = model.predict_proba(scaler.transform([features(song)]))[0]
    neural = float(proba[list(model.classes_).index(mood)])
    total = .55*heuristic + .25*fuzzy + .20*neural
    return {'score':round(total,4),'heuristic':round(heuristic,4),'fuzzy':round(fuzzy,4),'neural':round(neural,4)}

def genetic_playlist(candidates,seed=42,size=5,generations=35,pop_size=36,with_trace=False):
    """Evolve unique-song playlists and optionally expose an authentic execution trace."""
    rng=random.Random(seed)
    ids=[s['id'] for s in candidates]
    size=min(size,len(ids))
    if not size:
        return ([],0.0,[]) if with_trace else ([],0.0)
    lookup={s['id']:s for s in candidates}
    def fitness(chrom):
        chosen=[lookup[i] for i in chrom]
        quality=sum(s['score'] for s in chosen)/len(chosen)
        variety=len({s['artist'] for s in chosen})/len(chosen)
        return quality*.90 + variety*.10
    def repair(seq):
        out=list(dict.fromkeys(seq))
        for i in rng.sample(ids,len(ids)):
            if len(out)>=size:break
            if i not in out:out.append(i)
        return out[:size]
    def snapshot(chrom):
        return {'songs':[lookup[i]['title'] for i in chrom], 'fitness':round(fitness(chrom),4)}
    population=[rng.sample(ids,size) for _ in range(pop_size)]
    trace=[]
    for generation in range(generations):
        population.sort(key=fitness,reverse=True)
        new=population[:2]
        example=None
        while len(new)<pop_size:
            a=max(rng.sample(population,min(3,len(population))),key=fitness)
            b=max(rng.sample(population,min(3,len(population))),key=fitness)
            cut=rng.randrange(1,size) if size>1 else 1
            child=repair(a[:cut]+b[cut:])
            before_mutation=child[:]
            mutated=False
            if rng.random()<.25 and len(ids)>size:
                pos=rng.randrange(size)
                replacement=rng.choice([i for i in ids if i not in child])
                child[pos]=replacement
                mutated=True
            if example is None:
                example={'parent_a':snapshot(a),'parent_b':snapshot(b),
                         'crossover_cut':cut,'after_crossover':snapshot(before_mutation),
                         'mutation_applied':mutated,'child':snapshot(child)}
            new.append(child)
        if with_trace:
            trace.append({'generation':generation+1,'best_before':snapshot(population[0]),
                          'average_before':round(sum(map(fitness,population))/len(population),4),
                          'example':example})
        population=new
    winner=max(population,key=fitness)
    if with_trace:
        return [lookup[i] for i in winner],round(fitness(winner),4),{
            'population_size':pop_size,'generations':generations,
            'initial_best':trace[0]['best_before'],'history':trace,
            'final_best':snapshot(winner),
            'fitness_formula':'0.90 × average song match + 0.10 × unique-artist ratio',
            'mutation_probability':0.25,'selection':'tournament of 3','elitism':2}
    return [lookup[i] for i in winner],round(fitness(winner),4)

def adversarial_search(candidates):
    """Depth-2 minimax demo: MAX picks song; MIN chooses a plausible listener response.
    Utility uses the recommendation score and a response-dependent penalty.
    This is a defined two-player simulation, not evidence of real user behavior.
    """
    def responses(song):
        return {'likes':song['score'], 'skips':song['score']-.12*(1-song['score']),
                'genre_mismatch':song['score']-.08*(song['genre']!='Bollywood')}
    ranked=sorted(((min(responses(s).values()),s) for s in candidates),key=lambda z:z[0],reverse=True)
    return ranked[0][1]['id'],round(ranked[0][0],4)

def recommend(mood,genre,energy):
    candidates=[]
    for s in CATALOG:
        candidates.append({**s,**score(s,mood,genre,energy)})
    ranked=sorted(candidates,key=lambda s:s['score'],reverse=True)
    playlist,fitness,ga_trace=genetic_playlist(ranked[:15],with_trace=True)
    adversarial_id,utility=adversarial_search(ranked)
    return {'recommendations':ranked[:8],'playlist':playlist,'ga_fitness':fitness,'ga_trace':ga_trace,
            'adversarial_choice':next(s for s in ranked if s['id']==adversarial_id),
            'minimax_utility':utility,'algorithm_info':{
             'heuristic':'Weighted mood/energy/genre similarity',
             'fuzzy':'Overlapping triangular fuzzy mood memberships',
             'neural':'MLPClassifier trained on demonstration song labels',
             'genetic':'Tournament selection, crossover, mutation, elitism',
             'adversarial':'Two-ply minimax with simulated listener responses'}}
