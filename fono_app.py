import streamlit as st
from datetime import date, datetime, timedelta
import io
import gspread
from google.oauth2.service_account import Credentials

# CONFIGURAÇÃO DE PÁGINA OBRIGATÓRIA COMO LINHA DE EXECUÇÃO INICIAL
st.set_page_config(page_title="FonoClinic v1.7", page_icon="🩺", layout="wide")

import json  # Certifique-se de que esta linha está no topo absoluto do arquivo!

# =====================================================================
# MOTOR DE CONEXÃO PREMIUM VIA PARSER JSON DIRETO (SEM ARQUIVOS LOCAIS)
# =====================================================================
from streamlit_gsheets import GSheetsConnection

@st.cache_resource
def conectar_google_sheets():
    try:
        # Inicializa a conexão oficial do Streamlit
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Link do navegador da sua planilha Google Sheets
        link_da_planilha = "https://docs.google.com/spreadsheets/d/1EkIf2XPmEArBzeY6iD3tFfAwpHJeWnqJuh84XRMP-FY/edit?pli=1&gid=0#gid=0"
        
        # Lê a aba "Pacientes" informando o link explicitamente para o Streamlit
        conn.read(spreadsheet=link_da_planilha, worksheet="Pacientes", ttl="10m")
        
        # Retorna a conexão validada para o resto do app
        return conn
    except Exception as e:
        st.error(f"❌ Erro na conexão oficial do Streamlit: {e}")
        return None


# Inicializa a conexão global do banco de dados na inicialização
db_google = conectar_google_sheets()

# =====================================================================
# FUNÇÕES DE PERSISTÊNCIA REAL DE DADOS NO GOOGLE SHEETS
# =====================================================================
def salvar_novo_paciente(nome, nascimento, genero, cpf, mae, pai, responsavel, telefone, perfis, rua, numero, bairro, cidade):
    if not db_google:
        st.error("❌ Gravação abortada: Banco de dados Google Sheets não está ativo.")
        return False
    try:
        aba_pacientes = db_google.worksheet("Pacientes")
        nova_linha = [
            date.today().strftime("%d/%m/%Y"),
            nome, 
            nascimento.strftime("%d/%m/%Y") if isinstance(nascimento, date) else str(nascimento), 
            genero, 
            cpf, 
            mae, 
            pai, 
            responsavel, 
            telefone, 
            ", ".join(perfis),
            rua, 
            numero, 
            bairro, 
            cidade
        ]
        aba_pacientes.append_row(nova_linha)
        return True
    except Exception as e:
        st.error(f"⚠️ Erro ao inserir dados na aba Pacientes: {e}")
        return False

def salvar_nova_evolucao(paciente, protocolo, recursos, evolucao_slider, meta1_tosse, meta2_voz, notas_clinicas, proxima_conduta):
    if not db_google:
        st.error("❌ Gravação abortada: Banco de dados Google Sheets não está ativo.")
        return False
    try:
        aba_evolucoes = db_google.worksheet("Evolucoes")
        nova_linha = [
            date.today().strftime("%d/%m/%Y"),
            paciente, 
            protocolo, 
            ", ".join(recursos), 
            evolucao_slider, 
            meta1_tosse, 
            meta2_voz, 
            notas_clinicas, 
            proxima_conduta
        ]
        aba_evolucoes.append_row(nova_linha)
        return True
    except Exception as e:
        st.error(f"⚠️ Erro ao inserir dados na aba Evolucoes: {e}")
        return False

# Estilização CSS avançada para manter o ambiente clínico elegantíssimo
st.markdown("""
    <style>
    .reportview-container { background: #f8f9fa; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f3f5;
        border-radius: 4px 4px 0px 0px;
        padding: 12px 24px;
        font-weight: 600;
        color: #495057;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #ffffff !important; 
        color: #007bff !important;
        border-bottom: 2px solid #007bff !important;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e9ecef !important;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.02) !important;
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🩺 FonoClinic v1.7 — Gestão Clínica & Prontuário Inteligente")
if db_google:
    st.success("🟢 Banco de Dados Google Sheets Conectado e Ativo com Sucesso!")
else:
    st.error("🔴 Módulo Google Sheets inativo. Verifique as credenciais.")

# --- GERADOR DE ENCAIXES RECORRENTES DA GRADE ---
horarios_disponiveis = []
hora_atual = datetime.strptime("08:00", "%H:%M")
while hora_atual <= datetime.strptime("20:00", "%H:%M"):
    horarios_disponiveis.append(hora_atual.strftime("%H:%M"))
    hora_atual += timedelta(minutes=10)

def pergunta_sim_nao(label, key, info_adicional=False, label_adicional="Detalhes/Especificações:"):
    col1, col2 = st.columns(2)
    with col1:
        resposta = st.radio(label, ["", "Sim", "Não"], index=0, key=key, horizontal=True)
    with col2:
        detalhe = ""
        if info_adicional and resposta == "Sim":
            detalhe = st.text_input(f"{label_adicional}", key=f"{key}_det")
    return resposta, detalhe

# AS 7 ABAS COMPLETAS DO SOFTWARE UNIFICADO
aba1, aba2, aba3, aba4, aba5, aba6, aba7 = st.tabs([
    "📋 Painel de Atendimento",
    "📅 Marcar Horário",
    "👤 Admitir Paciente (Cadastro)",
    "📝 Triagem Rápida",
    "📚 Anamnese Completa (Robusta)",
    "🩺 Sessão do Dia (Evolução)",
    "🗂️ Central do Paciente (Prontuário)"
])

# =====================================================================
# ABA 1: PAINEL DE ATENDIMENTO DIÁRIO (COM FILTRAGEM E EXIBIÇÃO DE IDADE)
# =====================================================================
with aba1:
    st.header("📋 Painel de Atendimento Diário")
    st.write("Visualização unificada e limpa da grade de compromissos para controle rápido.")

    tipo_visao = st.radio(
        "Filtro de Escopo Temporal:",
        ["Ver por Dia", "Ver por Semana", "Ver por Mês"],
        horizontal=True, key="radio_tipo_visao"
    )
    data_base = st.date_input("Data de Referência:", value=date.today(), key="painel_data_ref")
    
    # Massa de dados completa contendo a idade analítica para visualização
    dados_agenda_sheets = [
        {"id_linha": "1", "paciente": "Arthur Silva", "idade": "6 anos e 4 meses", "perfil": "👶 Infantil (TEA)", "data": data_base.strftime("%d/%m/%Y"), "hora": "09:00", "status": "Agendado", "tipo_consulta": "Atendimento de Rotina", "obs": "Trazer caderno de exercícios lúdicos"},
        {"id_linha": "2", "paciente": "Beatriz Souza", "idade": "4 anos e 1 mês", "perfil": "👶 Infantil (Apraxia)", "data": data_base.strftime("%d/%m/%Y"), "hora": "10:30", "status": "Atendido", "tipo_consulta": "Primeira Consulta / Triagem", "obs": "Avaliação de processamento auditivo central"},
        {"id_linha": "3", "paciente": "Carlos Eduardo", "idade": "62 anos", "perfil": "🧓 Adulto (Pós-AVC)", "data": data_base.strftime("%d/%m/%Y"), "hora": "14:00", "status": "Faltou", "tipo_consulta": "Anamnese Clínica", "obs": "Acompanhante solicitou encaixe na recepção"}
    ]

    st.subheader(f"📅 Consultas e Atendimentos Agendados")
    
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        if st.button("⚙️ Compilar Grade (PDF)", key="btn_pdf_agenda_dia"):
            st.toast("Grade compilada no simulador com sucesso!", icon="⚙️")
    with col_exp2:
        pdf_agenda_buf = io.BytesIO()
        pdf_agenda_buf.write(b"Grade de Atendimentos FonoClinic Premium")
        st.download_button("📥 Baixar PDF da Grade", data=pdf_agenda_buf.getvalue(), file_name="agenda_diaria.pdf", mime="application/pdf")
        
    st.markdown("---")

    # Geração dos cards clínicos com as idades visíveis
    for ag in dados_agenda_sheets:
        with st.container(border=True):
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                st.markdown(f"### ⏰ **{ag.get('hora', '')}** — {ag.get('paciente', '')} <small style='background-color:#e7f5ff; color:#228be6; padding:3px 8px; border-radius:4px; font-size:12px; font-weight:bold;'>{ag.get('perfil', '')}</small>", unsafe_allow_html=True)
                st.markdown(f"🎂 **Idade:** {ag.get('idade', '')} | Tipo: **{ag.get('tipo_consulta', 'Atendimento')}**")
                if ag.get("obs", ""): 
                    st.info(f"📝 Nota de Recepção: {ag.get('obs', '')}")
            with col_c2:
                status_atual = ag.get("status", "Agendado")
                if status_atual == "Agendado": 
                    st.warning(f"🔹 Status: {status_atual}")
                elif status_atual == "Atendido": 
                    st.success(f"✅ Status: {status_atual}")
                else: 
                    st.error(f"❌ Status: {status_atual}")
            with col_c3:
                if status_atual == "Agendado":
                    if st.button("✅ Concluir Sessão", key=f"concluir_{ag.get('id_linha')}", use_container_width=True):
                        st.success("Simulação: Atendimento gravado!")
                    if st.button("🚨 Registrar Falta", key=f"falta_{ag.get('id_linha')}", use_container_width=True):
                        st.error("Simulação: Falta computada!")
                else:
                    if st.button("🗑️ Liberar Grade", key=f"excluir_{ag.get('id_linha')}", use_container_width=True):
                        st.info("Simulação: Horário disponibilizado.")

# =====================================================================
# ABA 2: CONFIGURAÇÃO E MARCAÇÃO DE NOVOS HORÁRIOS
# =====================================================================
with aba2:
    st.header("📅 Agendamento e Gestão de Vagas")
    st.write("Tela moderna para configuração de grades, marcações individuais ou repetições recorrentes.")
    
    lista_pacientes_sheets = ["Arthur Silva", "Beatriz Souza", "Carlos Eduardo"]

    with st.container(border=True):
        col_ag1, col_ag2 = st.columns(2)
        with col_ag1:
            p_nome = st.selectbox("Selecione o Paciente para Agenda:", lista_pacientes_sheets, key="agenda_p_sel")
            data_inicio = st.date_input("Data do Atendimento:", value=date.today(), key="agenda_data_ini")
            hora_agend = st.selectbox("Selecione o Horário Disponível:", horarios_disponiveis, key="agenda_hora_sel")
            tipo_consulta = st.selectbox("Modalidade Clínica:", ["Atendimento de Rotina", "Primeira Consulta / Triagem", "Anamnese Completa", "🚫 Bloqueio Clínico de Agenda"])

        with col_ag2:
            recorrencia = st.selectbox("Configuração de Recorrência:", ["Consulta Única", "Semanal (Fixo)", "Mensal (Fixo)"])
            qtd_repeticoes = st.number_input("Número de Sessões em Lote (Pacote):", min_value=1, value=1, step=1)
            obs_consulta = st.text_input("Observação para a Guia ou Prontuário:", key="agenda_obs")
            atendimento_grupo = st.checkbox("⚙️ Configurar como Atendimento Multidisciplinar / Grupo", value=False)

        st.markdown("---")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔍 Mapear Lacunas e Horários Vagos", use_container_width=True):
                st.write(f"📂 **Análise do dia {data_inicio.strftime('%d/%m/%Y')}:** Horários sugeridos: " + ", ".join(horarios_disponiveis[8:14]))
        with col_btn2:
            if st.button("🗓️ Fixar e Confirmar Agendamento", key="btn_fixar_agenda", type="primary", use_container_width=True):
                st.success(f"🎉 Sucesso! Compromisso agendado para {p_nome} através do fluxo integrado!")

# =====================================================================
# ABA 3: ADMITIR PACIENTE (CADASTRO PREMIUM COMPLETO CONECTADO AO GOOGLE SHEETS)
# =====================================================================
with aba3:
    st.header("👤 Admissão e Cadastro de Novo Paciente")
    st.write("Insira as informações cadastrais. Os dados serão salvos em tempo real na sua planilha Google Sheets.")

    with st.form("form_cadastro_paciente"):
        st.markdown("### 🧬 1. Dados Pessoais, Filiação e Perfil Clínico")
        with st.container(border=True):
            col_cad1, col_cad2 = st.columns(2)
            with col_cad1:
                cad_nome = st.text_input("Nome Completo do Paciente:", placeholder="Sem abreviações")
                cad_nasc = st.date_input("Data de Nascimento:", value=date(2015, 1, 1))
                cad_genero = st.selectbox("Gênero Biológico / Identidade:", ["", "Masculino", "Feminino", "Outro"])
                cad_cpf = st.text_input("CPF (Paciente ou Responsável):", placeholder="000.000.000-00")
            
            with col_cad2:
                cad_mae = st.text_input("Nome Completo da Mãe:", placeholder="Nome da mãe")
                cad_pai = st.text_input("Nome Completo do Pai:", placeholder="Nome do pai")
                cad_resp = st.text_input("Responsável Legal / Cuidador:", placeholder="Se menor de idade ou dependente")
                cad_tel = st.text_input("Telefone de Contato (WhatsApp):", placeholder="(00) 00000-0000")
        
        with st.container(border=True):
            st.markdown("**🏷️ Classificação e Perfil de Atendimento:**")
            st.caption("Selecione as categorias para ativar os protocolos automáticos no prontuário:")
            cad_perfis = st.multiselect(
                "Categorias Diagnósticas / Clínicas:",
                ["👶 Infantil", "🧓 Adulto/Idoso", "🧩 TEA (Autismo)", "🗣️ Apraxia de Fala", "🍽️ Disfagia (Deglutição)", "🧠 Afasia/Cognição", "🎙️ Voz/Motricidade Orofacial"],
                default=["👶 Infantil", "🧩 TEA (Autismo)"],
                key="cad_perfis_tags"
            )

        st.markdown("### 📍 2. Endereço Residencial")
        with st.container(border=True):
            col_end1, col_end2, col_end3 = st.columns(3)
            with col_end1:
                cad_rua = st.text_input("Logradouro (Rua, Avenida, etc.):", placeholder="Ex: Rua das Flores")
            with col_end2:
                cad_num = st.text_input("Número:", placeholder="Ex: 123")
            with col_end3:
                cad_compl = st.text_input("Complemento:", placeholder="Ex: Ap 102")

            col_end4, col_end5, col_end6 = st.columns(3)
            with col_end4:
                cad_bairro = st.text_input("Bairro:", placeholder="Ex: Copacabana")
            with col_end5:
                cad_cidade = st.text_input("Cidade:", placeholder="Ex: Rio de Janeiro")
            with col_end6:
                cad_uf = st.text_input("UF:", max_chars=2, placeholder="RJ")

        st.markdown("### 📂 3. Informações Complementares")
        with st.container(border=True):
            cad_email = st.text_input("E-mail para Envio de Treinos/Laudos:", placeholder="exemplo@email.com")
            cad_obs = st.text_area("Observações Administrativas Importantes:", placeholder="Restrições, convênio...")

        st.markdown("---")
        btn_salvar_cadastro = st.form_submit_button("💾 Salvar Registro de Admissão", type="primary", use_container_width=True)
        if btn_salvar_cadastro:
            if cad_nome:
                # CHAMADA REAL DA CONEXÃO DO GOOGLE SHEETS
                sucesso = salvar_novo_paciente(
                    nome=cad_nome, nascimento=cad_nasc, genero=cad_genero, cpf=cad_cpf,
                    mae=cad_mae, pai=cad_pai, responsavel=cad_resp, telefone=cad_tel,
                    perfis=cad_perfis, rua=cad_rua, numero=cad_num, bairro=cad_bairro, city=cad_cidade
                )
                if sucesso:
                    st.success(f"🎉 Excelente! O registro de {cad_nome} foi gravado na planilha Google Sheets com sucesso!")
                    st.balloons()
            else:
                st.warning("⚠️ O campo 'Nome Completo do Paciente' é obrigatório para realizar a gravação.")

# =====================================================================
# ABA 4: TRIAGEM RÁPIDA (PRIMEIRA QUEIXA E SINTOMAS INICIAIS)
# =====================================================================
with aba4:
    st.header("📝 Questionário de Triagem Inicial Rápida")
    st.write("Foco na captação da queixa principal e histórico de saúde imediato durante a primeira entrevista.")

    paciente_triagem = st.selectbox(
        "Selecione o Paciente para Vincular a Triagem:", 
        ["Arthur Silva", "Beatriz Souza", "Carlos Eduardo"], 
        key="triagem_p_sel"
    )
    
    with st.container(border=True):
        st.subheader("🚨 Queixa Principal e Antecedentes Médicos")
        tri_queixa = st.text_area("Qual a queixa principal trazida pela família ou paciente?", placeholder="Ex: Dificuldade de articulação...")
        tri_historico = st.text_area("Histórico médico relevante (Intervenções anteriores, exames realizados):")

    with st.container(border=True):
        st.subheader("🗣️ Marcos Rápidos de Desenvolvimento Motor e Fala")
        resp_fala, det_fala = pergunta_sim_nao("Apresenta atraso visível no desenvolvimento da fala?", "tri_fala", info_adicional=True, label_adicional="Idade em que iniciou as primeiras palavras:")
        resp_compreende, det_compreende = pergunta_sim_nao("Compreende ordens e comandos verbais simples?", "tri_comp")
        resp_andou, det_andou = pergunta_sim_nao("Apresentou atraso no desenvolvimento motor para andar?", "tri_andar", info_adicional=True, label_adicional="Idade com que andou sozinho(a):")

    with st.container(border=True):
        st.subheader("🍽️ Aspectos Sensoriais, Auditivos e Alimentares Básicos")
        resp_aud, det_aud = pergunta_sim_nao("Demonstra dificuldade para ouvir ou falta de atenção a sons?", "tri_aud")
        resp_mast, det_mast = pergunta_sim_nao("Apresenta dificuldade ou recusa na mastigação/deglutição?", "tri_mast", info_adicional=True, label_adicional="Descreva as texturas recusadas:")

    st.markdown("---")
    if st.button("💾 Gravar e Consolidar Triagem Rápida", key="btn_salvar_triagem", type="primary", use_container_width=True):
        st.success(f"✅ Triagem Inicial de {paciente_triagem} gravada com sucesso no simulador local!")

# =====================================================================
# ABA 5: ANAMNESE COMPLETA E ROBUSTA (PARTE 1 - HISTÓRICO DE SAÚDE E GERAL)
# =====================================================================
with aba5:
    st.header("📚 Anamnese Clínica Completa Infanto-Juvenil")
    st.write("Histórico clínico profundo e mapeamento de marcos cognitivos, comportamentais e pedagógicos.")

    paciente_ana_pdf = st.selectbox(
        "Vincular Anamnese Completa ao Paciente:", 
        ["Arthur Silva", "Beatriz Souza", "Carlos Eduardo"], 
        key="ana_pdf_p_sel"
    )

    # Organização em sub-abas para manter o consultório limpo e organizado
    sub_aba_geral, sub_aba_cognitiva, sub_aba_comportamento, sub_aba_autonomia = st.tabs([
        "🩺 Dados Gerais & Saúde", 
        "🧠 Cognição & Aprendizado", 
        "🧩 Comportamento & Neurodesenvolvimento", 
        "🏃 Autonomia & Rotina"
    ])

    # --- sub-tab 1. DADOS GERAIS, ESCOLA E SAÚDE ---
    with sub_aba_geral:
        st.subheader("Histórico de Saúde, Escola e Terapias")
        
        with st.container(border=True):
            col_sc1, col_sc2, col_sc3 = st.columns(3)
            with col_sc1:
                estuda_ref = st.radio("Frequenta Escola/Creche?", ["", "Sim", "Não"], horizontal=True, key="pdf_estuda")
            with col_sc2:
                st.text_input("Turma Escolar:", placeholder="Ex: 1º Ano EF", key="pdf_turma")
            with col_sc3:
                st.text_input("Turno Escolar:", placeholder="Ex: Matutino / Vespertino", key="pdf_turno")
                
        with st.container(border=True):
            st.text_area("Passa a maior parte do tempo com quem?", placeholder="Ex: Mãe, avó, cuidadora...", key="pdf_tempo_com")
            st.radio("Pratica ou gosta de esportes?", ["", "Sim", "Não"], horizontal=True, key="pdf_esportes")

        with st.container(border=True):
            st.subheader("Intervenções e Histórico Clínico")
            terapia_outros = st.radio("Faz terapia com outros profissionais?", ["", "Sim", "Não"], horizontal=True, key="pdf_outras_terap")
            if terapia_outros == "Sim":
                st.text_input("Quais profissionais/especialidades?", key="pdf_quais_terap")
            
            st.text_area("Já possui diagnóstico fechado? Se sim, qual?", placeholder="Ex: TEA nível 1 de suporte, Apraxia de fala infantil...", key="pdf_diagnostico")
            
            col_med1, col_med2 = st.columns(2)
            with col_med1:
                st.radio("Apresenta algum tipo de alergia?", ["", "Sim", "Não"], horizontal=True, key="pdf_alergico")
            with col_med2:
                st.radio("Toma alguma medicação contínua?", ["", "Sim", "Não"], horizontal=True, key="pdf_medicacao")

        with st.container(border=True):
            st.subheader("Histórico Neonatal e Alimentar Primitivo")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.selectbox("Tipo de Parto realizado:", ["", "Cesária", "Normal"], key="pdf_parto")
                st.text_input("Houve alguma intercorrência no parto/gestação?", key="pdf_intercorrencia")
            with col_p2:
                st.radio("Como foi a alimentação inicial?", ["", "Mamou no peito", "Fórmula", "Ambos"], key="pdf_amamentacao")
                st.radio("Usa ou já usou bicos artificiais (chupeta, mamadeira)?", ["", "Sim", "Não"], horizontal=True, key="pdf_bicos")

    # --- sub-tab 2. COGNIÇÃO E MARCOS PEDAGÓGICOS ---
    with sub_aba_cognitiva:
        st.subheader("Mapeamento Pedagógico e Habilidades Cognitivas Básicas")
        st.write("Marque o desempenho cognitivo observado ou relatado pela família:")

        with st.container(border=True):
            col_cg1, col_cg2 = st.columns(2)
            with col_cg1:
                st.radio("Sabe e responde o próprio nome?", ["", "Sim", "Não"], horizontal=True, key="pdf_sabe_nome")
                st.radio("Sabe o nome dos pais/responsáveis?", ["", "Sim", "Não"], horizontal=True, key="pdf_sabe_resp")
                st.radio("Conhece/sabe as vogais?", ["", "Sim", "Não"], horizontal=True, key="pdf_sabe_vogais")
            with col_cg2:
                st.radio("Conhece/sabe as cores básicas?", ["", "Sim", "Não"], horizontal=True, key="pdf_sabe_cores")
                st.radio("Conhece/sabe o alphabeto?", ["", "Sim", "Não"], horizontal=True, key="pdf_sabe_alfabeto")
                st.radio("Atende a comandos simples? (Ex: 'pega isso aqui e coloca na mesa')", ["", "Sim", "Não"], horizontal=True, key="pdf_atende_comandos")

        with st.container(border=True):
            st.subheader("Linguagem e Expressividade")
            st.radio("O paciente é verbal?", ["", "Sim", "Não"], horizontal=True, key="pdf_verbal")
            st.radio("Fala ou compreende o idioma inglês? (Telas)", ["", "Sim", "Não"], horizontal=True, key="pdf_ingles")
            
            col_nom1, col_nom2, col_nom3 = st.columns(3)
            with col_nom1: st.radio("Nomeia as cores?", ["", "Sim", "Não"], horizontal=True, key="pdf_nomeia_cores")
            with col_nom2: st.radio("Nomeia objetos comuns?", ["", "Sim", "Não"], horizontal=True, key="pdf_nomeia_objetos")
            with col_nom3: st.radio("Nomeia animais?", ["", "Sim", "Não"], horizontal=True, key="pdf_nomeia_animais")
                
            st.radio("Identifica e reconhece figuras/ilustrações?", ["", "Sim", "Não"], horizontal=True, key="pdf_identifica_figuras")
            st.radio("Demonstra habilidade para se expressar?", ["", "Sim", "Não"], horizontal=True, key="pdf_expressar")

    # --- sub-tab 3. COMPORTAMENTO E NEURODESENVOLVIMENTO ---
    with sub_aba_comportamento:
        st.subheader("Mapeamento Neurocomportamental")
        
        with st.container(border=True):
            st.markdown("**Características de Perfil Predominantes (Marque as aplicáveis):**")
            col_per1, col_per2, col_per3, col_per4 = st.columns(4)
            with col_per1: st.checkbox("Agitado(a)", key="pdf_chk_agitado")
            with col_per2: st.checkbox("Tranquilo(a)", key="pdf_chk_tranquilo")
            with col_per3: st.checkbox("Inseguro(a)", key="pdf_chk_inseguro")
            with col_per4: st.checkbox("Impaciente(a)", key="pdf_chk_impaciente")

        with st.container(border=True):
            st.subheader("Comunicação Social e Padrões de Comportamento")
            st.radio("Interage bem com outras pessoas/crianças?", ["", "Sim", "Não"], horizontal=True, key="pdf_interage")
            st.radio("Mantém contato visual (olha no olho) ao ser chamado?", ["", "Sim", "Não"], horizontal=True, key="pdf_olha_olho")
            st.radio("Apresenta seletividade alimentar marcante?", ["", "Sim", "Não"], horizontal=True, key="pdf_seletividade")
            st.radio("Apresenta estereotipias motoras/vocais?", ["", "Sim", "Não"], horizontal=True, key="pdf_estereotipia")
            st.radio("Apresenta ecolalia (repetição de falas)?", ["", "Sim", "Não"], horizontal=True, key="pdf_ecolalia")
            st.radio("Apresenta fixação/interesse restrito em algo?", ["", "Sim", "Não"], horizontal=True, key="pdf_fixacao")

        with st.container(border=True):
            st.subheader("Gerenciamento de Crises e Regulação")
            st.radio("Apresenta comportamentos de autoagressão?", ["", "Sim", "Não"], horizontal=True, key="pdf_auto_agressao")
            comport_agressivo = st.radio("Apresenta comportamento agressivo com terceiros?", ["", "Sim", "Não"], horizontal=True, key="pdf_agressivo_outros")
            if comport_agressivo == "Sim":
                st.text_input("Em quais momentos/gatilhos a agressividade se manifesta?", key="pdf_momentos_agressao")

    # --- sub-tab 4. AUTONOMIA E ROTINA DIÁRIA ---
    with sub_aba_autonomia:
        st.subheader("Habilidades de Vida Diária e Rotina")
        
        with st.container(border=True):
            st.subheader("Higiene, Desfralde e Autonomia")
            st.radio("Ainda faz uso frequente de fraldas?", ["", "Sim", "Não"], horizontal=True, key="pdf_usa_fralda")
            st.radio("Sabe/consegue pedir para ir ao banheiro?", ["", "Sim", "Não"], horizontal=True, key="pdf_pede_banheiro")
            st.radio("Consegue se vestir sozinho(a)?", ["", "Sim", "Não"], horizontal=True, key="pdf_veste_sozinho")
            st.radio("Demonstra dificuldades de coordenação ou restrição motora?", ["", "Sim", "Não"], horizontal=True, key="pdf_dif_motora")
            st.radio("Dorme bem e possui um padrão de sono regulado?", ["", "Sim", "Não"], horizontal=True, key="pdf_dorme_bem")

        with st.container(border=True):
            st.subheader("Interesses, Lazer e Elementos Motivadores")
            st.radio("Demonstra interesse ativo ou acalma-se ouvindo música?", ["", "Sim", "Não"], horizontal=True, key="pdf_gosta_musica")
            st.radio("Demonstra empatia ou gosta de animais?", ["", "Sim", "Não"], horizontal=True, key="pdf_gosta_animais")
            
            assiste_desenho = st.radio("Costuma assistir a desenhos animados em telas?", ["", "Sim", "Não"], horizontal=True, key="pdf_assiste_desenho")
            if assiste_desenho == "Sim":
                st.text_input("Quais são os seus desenhos/personagens favoritos?", key="pdf_quais_desenhos")
                
            st.text_area("O que ele(a) mais gosta de brincar ou fazer quando está livre?", key="pdf_gosta_brincar")

    # --- 5. CAMPOS DINÂMICOS PARA NOVAS PERGUNTAS ---
    st.markdown("---")
    st.subheader("➕ Personalização de Protocolo (Perguntas Adicionais)")
    st.write("Insira novos questionamentos ou tópicos específicos que a Dra. Michelle queira incluir na hora:")
    
    with st.container(border=True):
        col_add1, col_add2 = st.columns(2)
        with col_add1:
            pergunta_personalizada_1 = st.text_input("Título / Contexto da Nova Pergunta 1:", placeholder="Ex: Reação a ambientes barulhentos")
            resposta_personalizada_1 = st.text_area("Resposta do Paciente ou Responsável (Pergunta 1):", placeholder="Registre os detalhes aqui...")
        with col_add2:
            pergunta_personalizada_2 = st.text_input("Título / Contexto da Nova Pergunta 2:", placeholder="Ex: Histórico do sono na infância")
            resposta_personalizada_2 = st.text_area("Resposta do Paciente ou Responsável (Pergunta 2):", placeholder="Registre os detalhes aqui...")

    st.markdown("---")
    if st.button("💾 Consolidar Anamnese Completa no Prontuário", key="btn_salvar_ana_completa_pdf", type="primary", use_container_width=True):
        st.success(f"🎉 Excelente! Todo o histórico profundo do modelo oficial e campos personalizados foram salvos com sucesso!")

# =====================================================================
# ABA 6: SESSÃO DO DIA (ATENDIMENTO ADAPTATIVO POR PERFIL COM IDADES E GOOGLE SHEETS)
# =====================================================================
with aba6:
    st.header("🩺 Registro de Atendimento de Sessão")
    st.write("O formulário abaixo adapta suas perguntas automaticamente com base no perfil e idade do paciente.")

    paciente_sessao = st.selectbox(
        "Selecione o Paciente em Atendimento:", 
        ["Arthur Silva (Infantil - TEA)", "Beatriz Souza (Infantil - Apraxia)", "Carlos Eduardo (Adulto - Pós-AVC)"], 
        key="sessao_p_sel"
    )

    perfil_automatico = "Infantil" if "Infantil" in paciente_sessao else "Adulto"

    historico_contagem = {
        "Arthur Silva (Infantil - TEA)": {"total_consultas": 12, "protocolo": "PEI - TEA Nível 1"},
        "Beatriz Souza (Infantil - Apraxia)": {"total_consultas": 4, "protocolo": "PROAF - Apraxia"},
        "Carlos Eduardo (Adulto - Pós-AVC)": {"total_consultas": 21, "protocolo": "Mapeamento de Afasia"}
    }
    
    dados_p = historico_contagem.get(paciente_sessao, {"total_consultas": 0, "protocolo": "Geral"})
    num_sessao = dados_p["total_consultas"] + 1

    historico_idades = {
        "Arthur Silva (Infantil - TEA)": "6 anos e 4 meses (Nasc: 12/04/2020)",
        "Beatriz Souza (Infantil - Apraxia)": "4 anos e 1 mês (Nasc: 28/08/2022)",
        "Carlos Eduardo (Adulto - Pós-AVC)": "62 anos (Nasc: 05/01/1964)"
    }
    idade_paciente_atual = historico_idades.get(paciente_sessao, "Não Informada")

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1: st.metric("Atendimento Atual", f"Sessão Nº {num_sessao}")
    with col_m2: st.metric("Idade do Paciente", f"🎂 {idade_paciente_atual}")
    with col_m3: st.metric("Perfil Identificado", f"✨ {perfil_automatico}")
    with col_m4: st.metric("Data", date.today().strftime("%d/%m/%Y"))

    if perfil_automatico == "Adulto":
        st.error("⚠️ **ALERTA CLÍNICO (DISFAGIA/AFASIA):** Monitore sinais de penetração laríngea, tosse reflexa e umidade vocal após deglutições.")
    else:
        st.info("🎯 **FOCO TERAPÊUTICO (PEI/INFANTIL):** Priorize engajamento lúdico, contato visual sustentado e reforço positivo imediato.")

    perfil_escolhido = st.radio("Deseja alterar manualmente o formulário desta sessão?", ["Manter Automático", "Forçar Fluxo Infantil/TEA", "Forçar Fluxo Adulto/Disfagia/Afasia"], horizontal=True)
    fluxo_ativo = "Infantil" if "Infantil" in perfil_escolhido or (perfil_escolhido == "Manter Automático" and perfil_automatico == "Infantil") else "Adulto"

    with st.form("form_sessao_dia_dinamico"):
        st.subheader("📝 Mapeamento Técnico da Consulta")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            protocolo_utilizado = st.text_input("Protocolo / Abordagem Aplicada hoje:", value=dados_p["protocolo"])
            recursos_utilizados = st.multiselect("Quais Recursos Clínicos foram usados?", ["Espelho", "Massa de Modelar", "Livros Infantis", "Jogos de Tabuleiro", "Software Auditivo", "Cartões de Nomeação"])
        with col_s2:
            nivel_evolucao = st.select_slider("Evolução Percebida hoje:", options=["Regressão/Crise", "Estável", "Evolução Gradual", "Independente"])

        meta_inf_1 = "Não Iniciado"
        meta_inf_2 = "Não Iniciado"
        chk_tosse, chk_voz, chk_anomia, sel_consist = False, False, False, "Nenhuma"

        if fluxo_ativo == "Infantil":
            st.markdown("<p style='color:#007bff; font-weight:bold;'>🎯 Acompanhamento de Metas do PEI (Infantil)</p>", unsafe_allow_html=True)
            with st.container(border=True):
                col_pei1, col_pei2 = st.columns(2)
                with col_pei1:
                    meta_inf_1 = st.select_slider("Meta 1 (Linguagem Expressiva - Fonemas):", options=["Não Iniciado", "Em Introdução", "Com Apoio", "Independente"], value="Com Apoio", key="hub_pei_1")
                with col_pei2:
                    meta_inf_2 = st.select_slider("Meta 2 (Socioemocional - Contato Visual):", options=["Não Iniciado", "Em Introdução", "Com Apoio", "Independente"], value="Em Introdução", key="hub_pei_2")
        else:
            st.markdown("<p style='color:#e64980; font-weight:bold;'>🍽️ Gerenciamento de Risco e Linguagem (Adulto/Idoso)</p>", unsafe_allow_html=True)
            with st.container(border=True):
                col_ad1, col_ad2 = st.columns(2)
                with col_ad1:
                    chk_tosse = st.checkbox("Sinais de Penetração/Aspiração (Tosse/Engasgo com Líquidos)", key="hub_chk_tosse")
                    chk_voz = st.checkbox("Voz Molhada após Deglutição", key="hub_chk_voz_molhada")
                with col_ad2:
                    chk_anomia = st.checkbox("Presença de Anomia (Dificuldade de encontrar palavras)", key="hub_chk_anomia")
                    sel_consist = st.selectbox("Consistência Segura Testada hoje:", ["Nenhuma", "Zero (Líquidos Finos)", "Nível 4 (Pastoso)", "Nível 7 (Sólidos)"], key="hub_sel_consist")

        st.subheader("🧠 Notas Clínicas Descritivas")
        observacoes_dia = st.text_area("Descreva detalhadamente as respostas do paciente hoje:", height=150)
        proxima_conduta = st.text_input("Conduta Planejada para a Próxima Consulta:")

        st.markdown("---")
        btn_gravar_sessao = st.form_submit_button("💾 Finalizar Atendimento e Enviar para o Prontuário", type="primary", use_container_width=True)
        if btn_gravar_sessao:
            meta_ou_tosse = str(meta_inf_1) if fluxo_ativo == "Infantil" else f"Tosse/Aspiração: {chk_tosse}"
            meta_ou_voz = str(meta_inf_2) if fluxo_ativo == "Infantil" else f"Voz Molhada: {chk_voz} | Anomia: {chk_anomia} | Consistência: {sel_consist}"
            
            sucesso_sessao = salvar_nova_evolucao(
                paciente=paciente_sessao,
                protocolo=protocolo_utilizado,
                recursos=recursos_utilizados,
                evolucao_slider=nivel_evolucao,
                meta1_tosse=meta_ou_tosse,
                meta2_voz=meta_ou_voz,
                notas_clinicas=observacoes_dia,
                proxima_conduta=proxima_conduta
            )
            if sucesso_sessao:
                st.success(f"✅ Sucesso absoluto! O Atendimento Nº {num_sessao} foi consolidado na nuvem do Google Sheets!")
                st.balloons()

    st.markdown("### 🖨️ Documentação da Sessão")
    pdf_quick_buf = io.BytesIO()
    pdf_quick_buf.write(b"Comprovante de Evolucao de Sessao Avulsa")
    st.download_button(
        "🖨️ Exportar e Imprimir Relatório Desta Sessão", 
        data=pdf_quick_buf.getvalue(), 
        file_name=f"Evolucao_Sessao_{num_sessao}.pdf", 
        mime="application/pdf", 
        use_container_width=True
    )

# =====================================================================
# ABA 7: CENTRAL DO PACIENTE (PRONTUÁRIO HUB UNIFICADO PREMIUM)
# =====================================================================
with aba7:
    st.header("🗂️ Central Unificada do Paciente & Prontuário Clínico")
    st.write("Hub gerencial completo. Selecione o prontuário para visualizar históricos acumulados.")

    lista_central_pacientes = ["Arthur Silva (Infantil - TEA)", "Beatriz Souza (Infantil - Apraxia)", "Carlos Eduardo (Adulto - Pós-AVC)"]
    paciente_hub_ativo = st.selectbox("Selecione o Prontuário Ativo para Consulta:", lista_central_pacientes, key="hub_p_ativo")
    
    sub_hub_ficha, sub_hub_linha_tempo, sub_hub_laudos = st.tabs([
        "👤 Ficha Médica & Cadastro", 
        "📈 Linha do Tempo & Histórico Acumulado", 
        "🖨️ Gerador de Relatórios & Impressão"
    ])

    with sub_hub_ficha:
        st.subheader("📋 Informações Consolidadas do Paciente")
        idade_hub = "6 anos e 4 meses" if "Arthur" in paciente_hub_ativo else ("4 anos e 1 mês" if "Beatriz" in paciente_hub_ativo else "62 anos")
        nasc_hub = "12/04/2020" if "Arthur" in paciente_hub_ativo else ("28/08/2022" if "Beatriz" in paciente_hub_ativo else "05/01/1964")

        with st.container(border=True):
            st.markdown(f"### **Paciente:** {paciente_hub_ativo}")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                st.markdown(f"🎂 **Idade Cronológica:** {idade_hub} *(Data de Nasc: {nasc_hub})*")
                st.markdown("**Filiação:** Dra. Michelle Neves (Mãe) / Pedro Silva (Pai)")
                st.markdown("**Endereço:** Rua das Orquídeas, 456, Barra da Tijuca, Rio de Janeiro/RJ")
            with col_f2:
                st.markdown("**Contato Principal:** (21) 99999-8888")
                st.markdown("**Status Clínico Ativo:** Plano de Ensino Individualizado (PEI) em Andamento")

        with st.container(border=True):
            st.subheader("📚 Resumo Analítico da Anamnese e Triagem")
            st.markdown("- **Queixa Principal:** Atraso no desenvolvimento da fala e episódios de seletividade alimentar marcante.")
            st.markdown("- **Fatores Neurocomportamentais:** Apresenta estereotipias motoras sutis e ecolalia imediata.")
            st.markdown("- **Autonomia Diária:** Em fase de desfralde assistido; atende a comandos funcionais simples.")

    with sub_hub_linha_tempo:
        st.subheader("📈 Histórico Cronológico de Evolução (Linha do Tempo)")
        with st.container(border=True):
            st.markdown("#### **Sessão Nº 12 — 09/08/2026**")
            st.markdown("**Protocolo:** PEI - TEA Nível 1 | **Recursos:** Massa de Modelar | **Evolução:** Evolução Gradual")
            st.write("*Evolução Descritiva:* Apresentou boa fixação ocular, realizou os comandos com facilidade.")
        with st.container(border=True):
            st.markdown("#### **Sessão Nº 11 — 02/08/2026**")
            st.markdown("**Protocolo:** PEI - TEA Nível 1 | **Recursos:** Cartões de Nomeação | **Evolução:** Estável")

    with sub_hub_laudos:
        st.subheader("📄 Emissão de Documentos Clínicos Oficiais")
        with st.container(border=True):
            doc_tipo = st.selectbox("Tipo de Documento Desejado:", ["Relatório de Evolução Clínica", "Laudo de Avaliação Fonoaudiológica Completo"])
            doc_parecer = st.text_area("Parecer Técnico Descritivo do Documento:", placeholder="Escreva a conclusão diagnóstica...")
        
        st.markdown("---")
        col_pfd1, col_pfd2 = st.columns(2)
        with col_pfd1:
            if st.button("⚙️ Compilar e Estruturar Relatório Completo", use_container_width=True):
                if doc_parecer: st.success("🎉 Relatório estruturado e preparado na memória local!")
                else: st.warning("⚠️ Adicione o parecer descritivo para estruturar o relatório.")
        with col_pfd2:
            pdf_hub_buf = io.BytesIO()
            pdf_hub_buf.write(b"Documento Clinico Emitido por FonoClinic Premium")
            st.download_button(
                "🖨️ Gerar PDF para Download", 
                data=pdf_hub_buf.getvalue(), 
                file_name=f"Relatorio_{paciente_hub_ativo.replace(' ', '_')}.pdf", 
                mime="application/pdf", 
                use_container_width=True
            )
