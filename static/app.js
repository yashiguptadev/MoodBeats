let mood='happy';const $=id=>document.getElementById(id);
$('moods').querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{mood=b.dataset.mood;$('moods').querySelectorAll('button').forEach(x=>x.classList.toggle('active',x===b))}));
$('energy').addEventListener('input',e=>$('energyLabel').textContent=e.target.value+'%');
function card(s){const node=document.createElement('div');node.className='song';const icon=document.createElement('span');icon.className='note';icon.textContent='♫';const info=document.createElement('div');info.className='info';const title=document.createElement('strong');title.textContent=s.title;const artist=document.createElement('small');artist.textContent=s.artist+' · '+s.genre;const score=document.createElement('span');score.className='score';score.textContent=Math.round(s.score*100)+'% AI match';info.append(title,artist,score);const a=document.createElement('a');a.href='https://www.youtube.com/results?search_query='+encodeURIComponent(s.title+' '+s.artist);a.target='_blank';a.rel='noopener noreferrer';a.textContent='▶ Listen';node.append(icon,info,a);return node}
$('go').addEventListener('click',async()=>{const b=$('go');b.disabled=true;b.textContent='Finding your songs…';try{const r=await fetch('/api/recommend',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mood,genre:$('genre').value,energy:Number($('energy').value)/100})});const data=await r.json();if(!r.ok)throw Error(data.error||'Request failed');$('songs').replaceChildren(...data.recommendations.map(card));$('playlist').replaceChildren(...data.playlist.map(card));$('adversarial').textContent='Adversarial minimax choice: '+data.adversarial_choice.title+' (worst-case simulated utility '+data.minimax_utility+').';$('fitness').textContent='Genetic algorithm playlist fitness: '+data.ga_fitness+'.';$('explain').replaceChildren(...Object.entries(data.algorithm_info).map(([k,v])=>{const p=document.createElement('p');p.textContent=k.toUpperCase()+': '+v;return p}));showGaTrace(data.ga_trace);$('results').hidden=false;$('results').scrollIntoView({behavior:'smooth'});}catch(e){alert(e.message)}finally{b.disabled=false;b.textContent='✦ Recommend my songs'}});

let gaTrace=null;
const gaToggle=$('gaToggle');
function paragraph(label,value){const p=document.createElement('p');const strong=document.createElement('strong');strong.textContent=label+' ';p.append(strong,document.createTextNode(value));return p}
function playlistLine(obj){return obj.songs.join(' → ')+' (fitness '+obj.fitness.toFixed(4)+')'}
function renderGeneration(){
  if(!gaTrace)return;
  const index=Number($('gaGeneration').value)-1;
  const entry=gaTrace.history[index], ex=entry.example;
  $('gaGenerationLabel').textContent=String(entry.generation);
  $('gaGenerationDetail').replaceChildren(
    paragraph('Generation:',String(entry.generation)+' of '+gaTrace.generations),
    paragraph('Best playlist before reproduction:',playlistLine(entry.best_before)),
    paragraph('Average population fitness:',entry.average_before.toFixed(4)),
    paragraph('Selection — Parent A:',playlistLine(ex.parent_a)),
    paragraph('Selection — Parent B:',playlistLine(ex.parent_b)),
    paragraph('Crossover:', 'Cut after song '+ex.crossover_cut+'; duplicates are repaired to keep songs unique.'),
    paragraph('Child after crossover:',playlistLine(ex.after_crossover)),
    paragraph('Mutation:',ex.mutation_applied?'Yes — one song was replaced.':'No mutation for this example child.'),
    paragraph('Resulting child:',playlistLine(ex.child))
  );
}
$('gaGeneration').addEventListener('input',renderGeneration);
gaToggle.addEventListener('click',()=>{
  const opening=$('gaLab').hidden;
  $('gaLab').hidden=!opening;
  gaToggle.setAttribute('aria-expanded',String(opening));
  gaToggle.textContent=opening?'🧬 Hide Genetic Algorithm Working':'🧬 View Genetic Algorithm Working';
  if(opening)renderGeneration();
});
function showGaTrace(trace){
  gaTrace=trace;
  $('gaLab').hidden=true;
  gaToggle.setAttribute('aria-expanded','false');
  gaToggle.textContent='🧬 View Genetic Algorithm Working';
  $('gaGeneration').max=String(trace.generations);
  $('gaGeneration').value='1';
  $('gaSummary').replaceChildren(
    paragraph('Initial population:',trace.population_size+' candidate playlists'),
    paragraph('Fitness formula:',trace.fitness_formula),
    paragraph('Selection:',trace.selection),
    paragraph('Crossover:','One-point crossover with duplicate repair'),
    paragraph('Mutation probability:',Math.round(trace.mutation_probability*100)+'% per new child'),
    paragraph('Elitism:',trace.elitism+' best playlists survive unchanged'),
    paragraph('Initial best:',playlistLine(trace.initial_best)),
    paragraph('Final best:',playlistLine(trace.final_best))
  );
  $('gaStages').replaceChildren();
  renderGeneration();
}
