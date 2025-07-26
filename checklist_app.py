import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

# Configuração da página
st.set_page_config(
    page_title="Sistema de Checklist - Manutenção Preventiva",
    page_icon="🔧",
    layout="wide"
)

# Carregar dados dos checklists
@st.cache_data
def load_checklists():
    with open("checklists_structure.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Função para salvar checklist preenchido
def save_checklist(data, filename):
    os.makedirs("/home/ubuntu/checklists_salvos", exist_ok=True)
    filepath = f"/home/ubuntu/checklists_salvos/{filename}"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return filepath

# Função para gerar PDF
def create_pdf(checklist_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Checklist de Manutenção Preventiva", 0, 1, "C")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Informações Gerais:", 0, 1, "L")
    pdf.set_font("Arial", "", 10)
    for key, value in checklist_data["informacoes_gerais"].items():
        pdf.cell(0, 7, f"{key.replace('_', ' ').title()}: {value}", 0, 1, "L")
    pdf.cell(0, 7, f"Categoria: {checklist_data['categoria']}", 0, 1, "L")
    pdf.cell(0, 7, f"Periodicidade: {checklist_data['periodicidade']}", 0, 1, "L")
    pdf.cell(0, 7, f"Preenchido em: {checklist_data['data_preenchimento'][:19]}", 0, 1, "L")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Itens Verificados:", 0, 1, "L")
    pdf.set_font("Arial", "", 10)
    for code, item in checklist_data["itens"].items():
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 7, f"Item {code}: {item['description'][:80]}", 0, 1, "L")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 7, f"  Status: {item['status']}", 0, 1, "L")
        pdf.cell(0, 7, f"  Técnico: {item['tecnico']}", 0, 1, "L")
        if item["observacoes_campo"]:
            pdf.cell(0, 7, f"  Observações de Campo: {item['observacoes_campo'][:80]}", 0, 1, "L")
        if item["observation_original"] and str(item["observation_original"]) != "nan":
            pdf.cell(0, 7, f"  Observações Originais: {str(item['observation_original'])[:80]}", 0, 1, "L")
        pdf.ln(2)

    return pdf.output(dest="S").encode("latin-1")

# Título principal
st.title("🔧 Sistema de Checklist - Manutenção Preventiva")
st.markdown("**Equipamento: 930E-5 - Mina de Salobo**")

# Sidebar para informações gerais
with st.sidebar:
    st.header("📋 Informações da Inspeção")
    
    # Campos obrigatórios
    equipamento = st.text_input("Equipamento", value="930E-5")
    frota = st.text_input("Frota")
    data_inspecao = st.date_input("Data da Inspeção", value=datetime.now())
    horimetro = st.number_input("Horímetro", min_value=0, step=1)
    
    # Horários
    st.subheader("⏰ Horários")
    horario_inicio = st.time_input("Horário de Início")
    horario_termino = st.time_input("Horário de Término")
    
    # Responsáveis
    st.subheader("👥 Responsáveis")
    responsaveis = st.text_area("Responsáveis", height=100)
    turno = st.selectbox("Turno", ["Manhã", "Tarde", "Noite"])

# Carregar dados
checklists_data = load_checklists()

# Seleção de categoria e periodicidade
col1, col2 = st.columns(2)

with col1:
    categoria = st.selectbox(
        "🔧 Selecione a Categoria",
        list(checklists_data.keys())
    )

with col2:
    periodicidades = []
    if categoria in checklists_data:
        periodicidades = list(checklists_data[categoria].keys())
    periodicidade = st.selectbox(
        "📅 Selecione a Periodicidade",
        periodicidades
    )

# Exibir checklist selecionado
if categoria and periodicidade:
    st.header(f"📝 Checklist: {categoria} - {periodicidade}")
    
    # Inicializar session state para armazenar respostas
    if 'checklist_responses' not in st.session_state:
        st.session_state.checklist_responses = {}
    
    items = checklists_data[categoria][periodicidade]
    
    # Criar formulário para cada item
    with st.form(key=f"checklist_{categoria}_{periodicidade}"):
        responses = {}
        
        for i, item in enumerate(items):
            st.subheader(f"Item {item['code']}")
            
            # Descrição do item
            st.write(f"**Descrição:** {item['description']}")
            
            # Observações (se houver)
            if item['observation'] and str(item['observation']) != 'nan':
                st.info(f"**Observações:** {item['observation']}")
            
            # Campos de resposta
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                status = st.selectbox(
                    "Status",
                    ["Não Verificado", "OK", "Não OK", "N/A"],
                    key=f"status_{i}"
                )
            
            with col2:
                tecnico = st.text_input(
                    "Técnico",
                    key=f"tecnico_{i}"
                )
            
            with col3:
                observacoes_campo = st.text_area(
                    "Observações de Campo",
                    height=60,
                    key=f"obs_{i}"
                )
            
            responses[item['code']] = {
                'description': item['description'],
                'status': status,
                'tecnico': tecnico,
                'observacoes_campo': observacoes_campo,
                'observation_original': item['observation']
            }
            
            st.divider()
        
        # Botão para salvar
        submitted = st.form_submit_button("💾 Salvar Checklist", type="primary")
        
        if submitted:
            # Validar campos obrigatórios
            if not frota or not responsaveis:
                st.error("Por favor, preencha todos os campos obrigatórios na barra lateral.")
            else:
                # Preparar dados para salvamento
                checklist_data = {
                    'informacoes_gerais': {
                        'equipamento': equipamento,
                        'frota': frota,
                        'data_inspecao': str(data_inspecao),
                        'horimetro': horimetro,
                        'horario_inicio': str(horario_inicio),
                        'horario_termino': str(horario_termino),
                        'responsaveis': responsaveis,
                        'turno': turno
                    },
                    'categoria': categoria,
                    'periodicidade': periodicidade,
                    'data_preenchimento': datetime.now().isoformat(),
                    'itens': responses
                }
                
                # Gerar nome do arquivo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"checklist_{categoria}_{periodicidade}_{frota}_{timestamp}.json"
                
                # Salvar arquivo
                filepath = save_checklist(checklist_data, filename)
                
                st.success(f"✅ Checklist salvo com sucesso!")
                st.info(f"📁 Arquivo salvo: {filename}")
                
                st.session_state.last_saved_filepath = filepath
                st.session_state.last_saved_filename = filename
                st.session_state.last_saved_data = checklist_data

# Seção para visualizar checklists salvos
st.header("📂 Checklists Salvos")

# Verificar se existem checklists salvos
checklists_dir = "/home/ubuntu/checklists_salvos"
if os.path.exists(checklists_dir):
    saved_files = [f for f in os.listdir(checklists_dir) if f.endswith(".json")]
    
    if saved_files:
        selected_file = st.selectbox("Selecione um checklist salvo", saved_files)
        
        if selected_file:
            with open(os.path.join(checklists_dir, selected_file), "r", encoding="utf-8") as f:
                saved_data = json.load(f)
            
            # Exibir informações do checklist salvo
            st.subheader("📋 Informações Gerais")
            info = saved_data['informacoes_gerais']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Equipamento:** {info['equipamento']}")
                st.write(f"**Frota:** {info['frota']}")
                st.write(f"**Data:** {info['data_inspecao']}")
            
            with col2:
                st.write(f"**Horímetro:** {info['horimetro']}")
                st.write(f"**Turno:** {info['turno']}")
                st.write(f"**Categoria:** {saved_data['categoria']}")
            
            with col3:
                st.write(f"**Periodicidade:** {saved_data['periodicidade']}")
                st.write(f"**Responsáveis:** {info['responsaveis']}")
                st.write(f"**Preenchido em:** {saved_data['data_preenchimento'][:19]}")
            
            # Exibir itens do checklist
            st.subheader("📝 Itens Verificados")
            
            for code, item in saved_data['itens'].items():
                with st.expander(f"{code} - {item['status']}"):
                    st.write(f"**Descrição:** {item['description']}")
                    st.write(f"**Status:** {item['status']}")
                    st.write(f"**Técnico:** {item['tecnico']}")
                    if item['observacoes_campo']:
                        st.write(f"**Observações de Campo:** {item['observacoes_campo']}")
            
            # Botões de download
            col1, col2 = st.columns(2)
            
            with col1:
                # Botão de download do JSON (fora do formulário)
                with open(os.path.join(checklists_dir, selected_file), 'r', encoding='utf-8') as f:
                    st.download_button(
                        label="📥 Baixar Checklist (JSON)",
                        data=f.read(),
                        file_name=selected_file,
                        mime="application/json"
                    )
            
            with col2:
                # Botão de download do PDF
                try:
                    pdf_data = create_pdf(saved_data)
                    pdf_filename = selected_file.replace('.json', '.pdf')
                    st.download_button(
                        label="📄 Baixar Checklist (PDF)",
                        data=pdf_data,
                        file_name=pdf_filename,
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Erro ao gerar PDF: {str(e)}")

    else:
        st.info("Nenhum checklist salvo encontrado.")
else:
    st.info("Nenhum checklist salvo encontrado.")

# Rodapé
st.markdown("---")
st.markdown("**Sistema de Checklist - Manutenção Preventiva | Desenvolvido para uso em campo**")

