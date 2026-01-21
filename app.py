import os
import json
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permite conexões do navegador

# Arquivos onde os dados serão salvos
LEADS_FILE = 'data_leads.json'
PROJECTS_FILE = 'data_projects.json'

# --- FUNÇÕES PARA SALVAR/CARREGAR DADOS ---
def load_data(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return []

def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- ROTAS DO SISTEMA ---

@app.route('/')
def home():
    # Esta rota entrega o seu HTML (index.html)
    return render_template('index.html')

# --- API DE LEADS ---

@app.route('/api/leads', methods=['GET'])
def get_leads():
    leads = load_data(LEADS_FILE)
    # Ordena por data de modificação (mais recente primeiro)
    leads.sort(key=lambda x: x.get('lastActionDate', ''), reverse=True)
    return jsonify(leads)

@app.route('/api/leads', methods=['POST'])
def add_lead():
    new_lead = request.json
    # Garante que tem um ID
    if 'id' not in new_lead:
        new_lead['id'] = str(int(datetime.now().timestamp() * 1000))
    
    leads = load_data(LEADS_FILE)
    leads.append(new_lead)
    save_data(LEADS_FILE, leads)
    return jsonify({"message": "Lead criado", "lead": new_lead}), 201

@app.route('/api/leads/<lead_id>', methods=['PUT'])
def update_lead(lead_id):
    updated_data = request.json
    leads = load_data(LEADS_FILE)
    
    for i, lead in enumerate(leads):
        if str(lead.get('id')) == str(lead_id):
            # Atualiza os campos mantendo os antigos que não mudaram
            leads[i].update(updated_data)
            leads[i]['lastActionDate'] = datetime.now().isoformat()
            save_data(LEADS_FILE, leads)
            return jsonify({"message": "Lead atualizado", "lead": leads[i]})
            
    return jsonify({"error": "Lead não encontrado"}), 404

# --- API DE PROJETOS ---

@app.route('/api/projects', methods=['GET'])
def get_projects():
    projects = load_data(PROJECTS_FILE)
    return jsonify(projects)

@app.route('/api/projects', methods=['POST'])
def add_project():
    new_project = request.json
    # O ID do projeto geralmente vem do ID do lead, mas garantimos aqui
    if 'id' not in new_project:
        new_project['id'] = str(int(datetime.now().timestamp() * 1000))
        
    projects = load_data(PROJECTS_FILE)
    # Verifica se já existe para não duplicar
    if not any(p['id'] == new_project['id'] for p in projects):
        projects.append(new_project)
        save_data(PROJECTS_FILE, projects)
        return jsonify({"message": "Projeto criado", "project": new_project}), 201
    return jsonify({"message": "Projeto já existe"}), 200

@app.route('/api/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    updated_data = request.json
    projects = load_data(PROJECTS_FILE)
    
    for i, project in enumerate(projects):
        if str(project.get('id')) == str(project_id):
            projects[i].update(updated_data)
            save_data(PROJECTS_FILE, projects)
            return jsonify({"message": "Projeto atualizado", "project": projects[i]})
            
    return jsonify({"error": "Projeto não encontrado"}), 404

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    projects = load_data(PROJECTS_FILE)
    initial_len = len(projects)
    projects = [p for p in projects if str(p.get('id')) != str(project_id)]
    
    if len(projects) < initial_len:
        save_data(PROJECTS_FILE, projects)
        return jsonify({"message": "Projeto deletado"})
    return jsonify({"error": "Projeto não encontrado"}), 404

if __name__ == '__main__':
    # Cria os arquivos vazios se não existirem
    if not os.path.exists(LEADS_FILE): save_data(LEADS_FILE, [])
    if not os.path.exists(PROJECTS_FILE): save_data(PROJECTS_FILE, [])
    
    # IMPORTANTE: O Render usa a variável de ambiente PORT
    port = int(os.environ.get("PORT", 5000))
    print("Sistema Bravelle Iniciado! Acesse http://127.0.0.1:5000 no navegador.")
    app.run(host='0.0.0.0', port=port)
