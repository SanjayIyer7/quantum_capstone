from pathlib import Path
import subprocess, sys
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
app = FastAPI(title='Quantum Correlation Detection API', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173','http://127.0.0.1:5173'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.mount('/results', StaticFiles(directory=str(RESULTS)), name='results')

class RunConfig(BaseModel):
    eta_values: list[float] = Field(default=[0.1, 0.2, 0.4, 0.6], min_length=1, max_length=8)
    epsilon_values: list[float] = Field(default=[0.0, 0.05, 0.1, 0.2], min_length=1, max_length=8)
    trials: int = Field(default=100, ge=2, le=500)
    shots: int = Field(default=256, ge=16, le=2048)
    seed: int = 20260912

@app.get('/api/health')
def health(): return {'status':'ok','project':'Quantum Correlation Simulation Platform'}

@app.get('/api/results')
def get_results():
    summary_path = RESULTS / 'summary.csv'
    if not summary_path.exists():
        summary_path = RESULTS / 'final_results_table.csv'
    try:
        summary = pd.read_csv(summary_path).replace({float('nan'): None}).to_dict(orient='records')
        auc_path = RESULTS / 'final_auc_summary.csv'
        auc = pd.read_csv(auc_path).replace({float('nan'): None}).to_dict(orient='records') if auc_path.exists() else []
        return {'summary': summary, 'auc_summary': auc, 'source': summary_path.name}
    except Exception as exc: raise HTTPException(500, str(exc))

@app.post('/api/run')
def run_experiment(config: RunConfig):
    if any(not 0 <= v <= 1 for v in config.eta_values): raise HTTPException(400, 'eta values must be between 0 and 1')
    if any(not 0 <= v <= 0.5 for v in config.epsilon_values): raise HTTPException(400, 'epsilon values must be between 0 and 0.5')
    command = [sys.executable, str(ROOT/'experiments'/'main.py'), '--eta-values', ','.join(map(str, config.eta_values)), '--epsilon-values', ','.join(map(str, config.epsilon_values)), '--trials', str(config.trials), '--quantum-shots', str(config.shots), '--classical-samples', str(config.shots), '--seed', str(config.seed), '--output-dir', str(RESULTS)]
    try:
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=600)
        if proc.returncode != 0: raise HTTPException(500, (proc.stderr or proc.stdout)[-3000:])
        return {'status':'completed', 'message':'Experiment completed and result CSVs/plots refreshed.', 'output':proc.stdout[-5000:]}
    except subprocess.TimeoutExpired: raise HTTPException(504, 'Simulation exceeded the 10-minute limit.')

@app.get('/api/figures')
def figures():
    names = ['auc_comparison.png','roc_best_condition.png','final_auc_vs_eta.png','final_auc_vs_noise.png','final_roc_difficult_condition.png','final_correlation_separation.png','presentation_overall.png']
    return {'figures':[{'name':n,'url':f'/results/{n}'} for n in names if (RESULTS/n).exists()]}
