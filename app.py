from flask import Flask,render_template,request,jsonify
from engine import MOODS,GENRES,recommend
app=Flask(__name__)
@app.get('/')
def home(): return render_template('index.html')
@app.post('/api/recommend')
def api_recommend():
    data=request.get_json(silent=True) or {}
    mood=data.get('mood','happy'); genre=data.get('genre','Any')
    try: energy=float(data.get('energy',.6))
    except (TypeError,ValueError): return jsonify(error='Energy must be numeric'),400
    if mood not in MOODS or genre not in ['Any']+GENRES or not 0<=energy<=1:
        return jsonify(error='Invalid mood, genre or energy'),400
    return jsonify(recommend(mood,genre,energy))
if __name__=='__main__': app.run(debug=True)
