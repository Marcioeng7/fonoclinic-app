import streamlit as st
from datetime import date, datetime, timedelta
import io
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="FonoClinic v1.7", page_icon="🩺", layout="wide")

# =====================================================================
# MOTOR DE CONEXÃO PREMIUM COM GOOGLE SHEETS VIA SECRETS (CORRIGIDO)
# =====================================================================
@st.cache_resource
def conectar_google_sheets():
    try:
        escopos = ["https://googleapis.com", "https://googleapis.com"]
        credenciais_dict = dict(st.secrets["gspread_credentials"])
        pk = credenciais_dict["private_key"]
        if "\\n" in pk:
            pk = pk.replace("\\n", "\n")
        credenciais_dict["private_key"] = pk.strip().strip('"').strip("'")
        creds = Credentials.from_service_account_info(credenciais_dict, scopes=escopos)
        return gspread.authorize(creds).open("FonoClinic_Data")
    except Exception as e:
        st.error(f"❌ Erro de conexão com o Google Sheets: {e}")
        return None

db_google = conectar_google_sheets()

def salvar_novo_paciente(nome, nascimento, genero, cpf, mae, pai, responsavel, telefone, perfis, rua, numero, bairro, city):
    if not db_google: return False
    try:
        db_google.worksheet("Pacientes").append_row([
            date.today().strftime("%d/%m/%Y"), nome, 
            nascimento.strftime("%d/%m/%Y") if isinstance(nascimento, date) else str(nascimento),
            genero, cpf, mae, pai, responsavel, telefone, ", ".join(perfis), rua, numero, bairro, city
        ])
        return True
    except: return False

def salvar_nova_evolucao(paciente, protocolo, recursos, evolucao_slider, meta1, meta2, notas, conduta):
    if not db_google: return False
    try:
        db_google.worksheet("Evolucoes").append_row([
            date.today().strftime("%d/%m/%Y"), paciente, protocolo, ", ".join(recursos), evolucao_slider, meta1, meta2, notas, conduta
        ])
        return True
    except: return False

st.markdown("<style>.stTabs [data-baseweb='tab'] {font-weight: 600; padding: 10px 20px;}</style>", unsafe_allow_html=True)
st.title("🩺 FonoClinic v1.7 — Gestão Clínica")
if db_google: st.success("🟢 Banco de Dados Google Sheets Conectado e Ativo!")
else: st.error("🔴 Aguardando Conexão ativa com o Google Sheets.")

horarios_disponiveis = []
hora_atual = datetime.strptime("08:00", "%H:%M")
while hora_atual <= datetime.strptime("20:00", "%H:%M"):
    horarios_disponiveis.append(hora_atual.strftime("%H:%M"))
    hora_atual += timedelta(minutes=10)

def pergunta_sim_nao(label, key, info_adicional=False, label_adicional="Detalhes"):
    col1, col2 = st.columns(2)
    with col1: resp = st.radio(label, ["", "Sim", "Não"], index=0, key=key, horizontal=True)
    with col2: det = st.text_input(label_adicional, key=f"{key}_det") if info_adicional and resp == "Sim" else ""
    return resp, det

aba1, aba2, aba3, aba4, aba5, aba6, aba7 = st.tabs([
    "📋 Painel de Atendimento", "📅 Marcar Horário", "👤 Admitir Paciente", "📝 Triagem Rápida", "📚 Anamnese", "🩺 Sessão do Dia", "🗂️ Prontuário Hub"
])

with aba1:
    st.header("📋 Painel de Atendimento Diário")
    tipo_visao = st.radio("Escopo:", ["Ver por Dia", "Ver por Semana", "Ver por Mês"], horizontal=True)
    data_base = st.date_input("Data:", value=date.today())
    dados_agenda = [
        {"id": "1", "paciente": "Arthur Silva", "idade": "6 anos e 4 meses", "perfil": "👶 Infantil (TEA)", "hora": "09:00", "status": "Agendado"},
        {"id": "2", "paciente": "Beatriz Souza", "idade": "4 anos e 1 mês", "perfil": "👶 Infantil (Apraxia)", "hora": "10:30", "status": "Atendido"},
        {"id": "3", "paciente": "Carlos Eduardo", "idade": "62 anos", "perfil": "🧓 Adulto (Pós-AVC)", "hora": "14:00", "status": "Faltou"}
    ]
    for ag in dados_agenda:
        with st.container(border=True):
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                st.markdown(f"### ⏰ **{ag['hora']}** — {ag['paciente']} <small style='background-color:#e7f5ff; color:#228be6; padding:3px; border-radius:4px;'>{ag['perfil']}</small>", unsafe_allow_html=True)
                st.write(f"🎂 Idade: {ag['idade']}")
            with col_c2:
                if ag['status'] == "Agendado": st.warning(f"🔹 {ag['status']}")
                elif ag['status'] == "Atendido": st.success(f"✅ {ag['status']}")
                else: st.error(f"❌ {ag['status']}")
            with col_c3:
                if ag['status'] == "Agendado":
                    if st.button("✅ Concluir", key=f"c_{ag['id']}", use_container_width=True): st.success("Gravado!")

# =====================================================================
# CONTINUAÇÃO DA ABA 2 À ABA 7
# =====================================================================
with aba2:
    st.header("📅 Agendamento e Gestão de Vagas")
    with st.container(border=True):
        col_ag1, col_ag2 = st.columns(2)
        with col_ag1:
            p_nome = st.selectbox("Paciente:", ["Arthur Silva", "Beatriz Souza", "Carlos Eduardo"], key="agenda_p_sel")
            data_inicio = st.date_input("Data:", value=date.today(), key="agenda_data_ini")
            hora_agend = st.selectbox("Horário:", horarios_disponiveis, key="agenda_hora_sel")
        with col_ag2:
            tipo_consulta = st.selectbox("Modalidade:", ["Atendimento de Rotina", "Triagem", "Anamnese", "🚫 Bloqueio"])
            obs_consulta = st.text_input("Observação:", key="agenda_obs")
        if st.button("🗓️ Confirmar Agendamento", key="btn_fixar_agenda", type="primary", use_container_width=True):
            st.success(f"🎉 Compromisso agendado para {p_nome}!")

with aba3:
    st.header("👤 Admissão e Cadastro de Novo Paciente")
    with st.form("form_cadastro_paciente"):
        st.markdown("### 🧬 1. Dados Pessoais e Filiação")
        with st.container(border=True):
            col_cad1, col_cad2 = st.columns(2)
            with col_cad1:
                cad_nome = st.text_input("Nome Completo:", placeholder="Sem abreviações")
                cad_nasc = st.date_input("Data de Nascimento:", value=date(2015, 1, 1))
                cad_genero = st.selectbox("Gênero:", ["", "Masculino", "Feminino", "Outro"])
                cad_cpf = st.text_input("CPF:", placeholder="000.000.000-00")
            with col_cad2:
                cad_mae = st.text_input("Nome da Mãe:")
                cad_pai = st.text_input("Nome do Pai:")
                cad_resp = st.text_input("Responsável Legal:")
                cad_tel = st.text_input("Telefone (WhatsApp):", placeholder="(00) 00000-0000")
        
        cad_perfis = st.multiselect("🏷️ Categorias Clínicas:", ["👶 Infantil", "🧓 Adulto", "🧩 TEA", "🗣️ Apraxia", "🍽️ Disfagia", "🧠 Afasia"], default=["👶 Infantil", "🧩 TEA"])

        st.markdown("### 📍 2. Endereço e Complementos")
        with st.container(border=True):
            col_e1, col_e2, col_e3 = st.columns(3)
            with col_e1: cad_rua = st.text_input("Rua:")
            with col_e2: cad_num = st.text_input("Número:")
            with col_e3: cad_compl = st.text_input("Complemento:")
            col_e4, col_e5, col_e6 = st.columns(3)
            with col_e4: cad_bairro = st.text_input("Bairro:")
            with col_e5: cad_cidade = st.text_input("Cidade:")
            with col_e6: cad_uf = st.text_input("UF:", max_chars=2)

        if st.form_submit_button("💾 Salvar Registro de Admissão", type="primary", use_container_width=True):
            if cad_nome:
                if salvar_novo_paciente(cad_nome, cad_nasc, cad_genero, cad_cpf, cad_mae, cad_pai, cad_resp, cad_tel, cad_perfis, cad_rua, cad_num, cad_bairro, cad_cidade):
                    st.success(f"🎉 Registro de {cad_nome} gravado no Google Sheets!")
                    st.balloons()
                else: st.error("❌ Falha ao gravar dados. Verifique a conexão.")
            else: st.warning("⚠️ Nome do paciente é obrigatório.")

with aba4:
    st.header("📝 Questionário de Triagem Inicial Rápida")
    p_triagem = st.selectbox("Paciente para Triagem:", ["Arthur Silva", "Beatriz Souza", "Carlos Eduardo"], key="t_sel")
    with st.container(border=True):
        tri_queixa = st.text_area("Queixa Principal:")
        resp_fala, det_fala = pergunta_sim_nao("Apresenta atraso na fala?", "tri_fala", True, "Início das primeiras palavras:")
        resp_mast, det_mast = pergunta_sim_nao("Dificuldade na mastigação/deglutição?", "tri_mast", True, "Texturas recusadas:")
    if st.button("💾 Gravar Triagem", type="primary", use_container_width=True): st.success("Triagem salva no simulador local!")

with aba5:
    st.header("📚 Anamnese Clínica Completa")
    sub_geral, sub_cognitiva, sub_comportamento = st.tabs(["🩺 Saúde", "🧠 Cognição", "🧩 Comportamento"])
    with sub_geral:
        with st.container(border=True):
            st.radio("Frequenta Escola?", ["", "Sim", "Não"], horizontal=True, key="ana_escola")
            st.text_area("Já possui diagnóstico fechado? Se sim, qual?", key="ana_diag")
            st.radio("Toma medicação contínua?", ["", "Sim", "Não"], horizontal=True, key="ana_med")
    with sub_cognitiva:
        with st.container(border=True):
            st.radio("O paciente é verbal?", ["", "Sim", "Não"], horizontal=True, key="ana_verbal")
            st.radio("Atende a comandos simples?", ["", "Sim", "Não"], horizontal=True, key="ana_coman")
    with sub_comportamento:
        with st.container(border=True):
            st.checkbox("Agitado(a)", key="ana_agitado")
            st.checkbox("Tranquilo(a)", key="ana_tranquilo")
            st.radio("Apresenta seletividade alimentar?", ["", "Sim", "Não"], horizontal=True, key="ana_selet")
            st.radio("Apresenta ecolalia?", ["", "Sim", "Não"], horizontal=True, key="ana_ecol")
    if st.button("💾 Consolidar Anamnese Completa", type="primary", use_container_width=True): st.success("Anamnese consolidada localmente!")

with aba6:
    st.header("🩺 Registro de Atendimento de Sessão")
    p_sessao = st.selectbox("Paciente em Atendimento:", ["Arthur Silva (Infantil - TEA)", "Beatriz Souza (Infantil - Apraxia)", "Carlos Eduardo (Adulto - Pós-AVC)"], key="s_sel")
    fluxo_ativo = "Infantil" if "Infantil" in p_sessao else "Adulto"
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1: st.metric("Perfil Identificado", f"✨ {fluxo_ativo}")
    with col_m2: st.metric("Data", date.today().strftime("%d/%m/%Y"))
    with col_m3: st.metric("Status do Banco", "Conectado" if db_google else "Desconectado")

    with st.form("form_sessao_dia_dinamico"):
        protocolo = st.text_input("Protocolo Aplicado:", value="PEI - TEA Nível 1" if fluxo_ativo == "Infantil" else "Mapeamento de Afasia")
        recursos = st.multiselect("Recursos:", ["Espelho", "Massa de Modelar", "Livros", "Cartões", "Sondas"])
        evolucao_slider = st.select_slider("Evolução hoje:", options=["Regressão", "Estável", "Evolução Gradual", "Independente"])
        
        meta_inf_1, meta_inf_2 = "Não Iniciado", "Não Iniciado"
        chk_tosse, chk_voz = False, False

        if fluxo_ativo == "Infantil":
            st.markdown("**🎯 Metas do PEI**")
            meta_inf_1 = st.select_slider("Meta 1 (Linguagem):", options=["Não Iniciado", "Em Introdução", "Com Apoio", "Independente"])
            meta_inf_2 = st.select_slider("Meta 2 (Socioemocional):", options=["Não Iniciado", "Em Introdução", "Com Apoio", "Independente"])
        else:
            st.markdown("**🍽️ Gerenciamento de Risco**")
            chk_tosse = st.checkbox("Sinais de Penetração/Aspiração (Tosse/Engasgo)")
            chk_voz = st.checkbox("Voz Molhada após Deglutição")

        notas_clinicas = st.text_area("Notas Clínicas Descritivas:")
        proxima_conduta = st.text_input("Conduta Planejada:")

        if st.form_submit_button("💾 Finalizar Atendimento e Gravar", type="primary", use_container_width=True):
            m1 = str(meta_inf_1) if fluxo_ativo == "Infantil" else f"Tosse: {chk_tosse}"
            m2 = str(meta_inf_2) if fluxo_ativo == "Infantil" else f"Voz Molhada: {chk_voz}"
            if salvar_nova_evolucao(p_sessao, protocolo, recursos, evolucao_slider, m1, m2, notas_clinicas, proxima_conduta):
                st.success("✅ Atendimento consolidado com sucesso no Google Sheets!")
                st.balloons()
            else: st.error("❌ Erro ao salvar dados no Google Sheets.")

    pdf_buf = io.BytesIO()
    pdf_buf.write(b"Relatorio de Evolucao de Sessao FonoClinic")
    st.download_button("🖨️ Exportar PDF Desta Sessão", data=pdf_buf.getvalue(), file_name="Evolucao_Sessao.pdf", mime="application/pdf", use_container_width=True)

with aba7:
    st.header("🗂️ Central Unificada do Paciente")
    p_hub = st.selectbox("Selecione o Prontuário:", ["Arthur Silva", "Beatriz Souza", "Carlos Eduardo"], key="h_sel")
    sub_ficha, sub_tempo = st.tabs(["👤 Ficha Médica", "📈 Histórico Acumulado"])
    with sub_ficha:
        with st.container(border=True):
            st.markdown(f"### **Paciente:** {p_hub}")
            st.markdown("- **Status Clínico:** Plano de Ensino Individualizado (PEI) em Andamento")
            st.markdown("- **Queixa Principal:** Atraso no desenvolvimento da fala e episódios de seletividade alimentar.")
    with sub_tempo:
        with st.container(border=True):
            st.markdown("#### **Última Sessão Registrada (Simulação)**")
            st.write("Apresentou boa fixação ocular e realizou os comandos de pareamento com facilidade.")
