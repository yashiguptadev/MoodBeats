# Deploy MoodTune to Render

1. Create a GitHub repository (for example `mood-recom`).
2. Upload the **contents of this moodtune folder** to the repository root (app.py, engine.py, requirements.txt, templates/, static/, etc.).
3. At https://dashboard.render.com choose New > Web Service and connect the GitHub repository.
4. Set Name to `mood-recom` (if available), Language to Python 3, Build Command to `pip install -r requirements.txt`, and Start Command to `gunicorn --bind 0.0.0.0:$PORT app:app`.
5. Because you uploaded the contents of moodtune directly, leave Render's Root Directory blank. Select Free and deploy.
6. Open the actual URL shown on the Render service page after it says Live.

Note: render.yaml is for deployments when the original outer `moodtune/` folder is retained in the repository. If you uploaded the contents directly to the repository root, use the manual settings above instead.
