import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# Configurações do Supabase (Pegas do Ambiente no Render)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def home():
    return render_template('index.html')

# --- API DE LEADS ---

@app.route('/api/leads', methods=['GET'])
def get_leads():
    # Busca todos os leads do Supabase
    response = supabase.table('leads').select("*").execute()
    # Retorna apenas o conteúdo da coluna 'data' que salvamos
    leads = [item['data'] for item in response.data]
    return jsonify(leads)

@app.route('/api/leads', methods=['POST'])
def add_lead():
    new_lead = request.json
    if 'id' not in new_lead:
        new_lead['id'] = str(int(datetime.now().timestamp() * 1000))
    
    # Salva no Supabase: id e o objeto completo na coluna 'data'
    supabase.table('leads').insert({"id": new_lead['id'], "data": new_lead}).execute()
    return jsonify({"message": "Lead criado", "lead": new_lead}), 201

@app.route('/api/leads/<lead_id>', methods=['PUT'])
def update_lead(lead_id):
    updated_data = request.json
    updated_data['lastActionDate'] = datetime.now().isoformat()
    
    # Atualiza no Supabase onde o ID for igual
    supabase.table('leads').update({"data": updated_data}).eq("id", lead_id).execute()
    return jsonify({"message": "Lead atualizado", "lead": updated_data})

# --- API DE PROJETOS ---

@app.route('/api/projects', methods=['GET'])
def get_projects():
    response = supabase.table('projects').select("*").execute()
    projects = [item['data'] for item in response.data]
    return jsonify(projects)

@app.route('/api/projects', methods=['POST'])
def add_project():
    new_project = request.json
    if 'id' not in new_project:
        new_project['id'] = str(int(datetime.now().timestamp() * 1000))
        
    supabase.table('projects').insert({"id": new_project['id'], "data": new_project}).execute()
    return jsonify({"message": "Projeto criado", "project": new_project}), 201

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    supabase.table('projects').delete().eq("id", project_id).execute()
    return jsonify({"message": "Projeto deletado"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
