# ==============================================================================
# BLOCO 1 DE 5: IMPORTAÇÕES, SEGURANÇA E CONEXÃO COM O GOOGLE SHEETS
# ==============================================================================
import streamlit as st
import gspread
from google.auth.credentials import Credentials
from google.oauth2.service_account import Credentials as SACredentials
import hmac

# 1. CONFIGURAÇÃO DA PÁGINA (Deve ser o primeiro comando Streamlit)
st.set_page_config(
    page_title="FonoClinic v1.3",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. MOTOR DE CONEXÃO COM O GOOGLE SHEETS (NUVEM)
@st.cache_resource
def conectar_google_sheets():
    try:
        # Escopos necessários para leitura e gravação no Drive/Sheets
        escopos = [
            "https://googleapis.com",
            "https://googleapis.com"
        ]
        
        # Carrega as credenciais seguras dos Secrets do Streamlit Cloud
        info_chaves = dict(st.secrets["gcp_service_account"])
        credenciais = SACredentials.from_service_account_info(info_chaves, scopes=escopos)
        
        # Autentica o cliente do gspread
        cliente = gspread.authorize(credenciais)
        
        # Abre a planilha oficial pelo ID exato fornecido
        id_planilha = "1qLEa7_iEPSkENJSovjy6_3yzVVjtVAKnJDkteG6Skdw"
        planilha_mestre = cliente.open_by_key(id_planilha)
        return planilha_mestre
    except Exception as e:
        st.error(f"Erro crítico de comunicação com o Google Sheets: {e}")
        st.info("Verifique se o e-mail do robô foi compartilhado na Planilha como Editor.")
        return None

# Inicializa as tabelas na nuvem
gspread_client = conectar_google_sheets()

if gspread_client:
    try:
        aba_identificacao = gspread_client.worksheet("identificacao")
        aba_anamnese = gspread_client.worksheet("anamnese")
        aba_evolucao = gspread_client.worksheet("evolucoes_relatorios")
        aba_agenda = gspread_client.worksheet("agenda")
    except Exception as e:
        st.error(f"Erro ao carregar as abas da planilha: {e}")
        st.warning("Verifique se os nomes das abas no Sheets estão exatamente como: identificacao, anamnese, evolucoes_relatorios e agenda")

# 3. INTERFACE PRINCIPAL E CRIAÇÃO DAS ABAS
st.title("📝 FonoClinic v1.3 — Prontuário Digital Integrado")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👥 1. Identificação do Paciente", 
    "🩺 2. Anamnese Clínica", 
    "📈 3. Evoluções e Relatórios", 
    "📅 4. Agenda Integrada",
    "📂 5. Central do Paciente"
])

# ==============================================================================
# BLOCO 2 DE 5: ABA 1 — IDENTIFICAÇÃO E CADASTRO DO PACIENTE
# ==============================================================================
with tab1:
    st.header("👥 Cadastro e Identificação do Paciente")
    st.write("Insira os dados cadastrais do paciente para registrar ou atualizar na nuvem.")
    
    with st.form("form_identificacao", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            id_paciente = st.text_input("Código/ID do Paciente (Ex: PAC001):", placeholder="PAC001")
            nome_paciente = st.text_input("Nome Completo:", placeholder="Nome do paciente")
            data_nascimento = st.text_input("Data de Nascimento (DD/MM/AAAA):", placeholder="14/08/2020")
            idade_paciente = st.text_input("Idade:", placeholder="Ex: 6 anos")
        
        with col2:
            nome_responsavel = st.text_input("Nome do Responsável (Se menor):", placeholder="Mãe ou Pai")
            telefone_contato = st.text_input("Telefone de Contato (Com DDD):", placeholder="(21) 99999-9999")
            queixa_principal = st.text_area("Queixa Principal (Breve resumo):", placeholder="Motivo da busca pelo atendimento")
            
        botao_salvar_id = st.form_submit_button("💾 Salvar Identificação na Nuvem")
        
    if botao_salvar_id:
        if not id_paciente or not nome_paciente:
            st.warning("⚠️ Os campos 'Código/ID' e 'Nome Completo' são obrigatórios!")
        elif gspread_client is None:
            st.error("❌ Não há conexão ativa com o Google Sheets. Verifique o Bloco 1.")
        else:
            with st.spinner("Gravando dados no Google Sheets..."):
                try:
                    # Prepara a linha para inserção
                    nova_linha = [
                        id_paciente, 
                        nome_paciente, 
                        data_nascimento, 
                        idade_paciente, 
                        nome_responsavel, 
                        telefone_contato, 
                        queixa_principal
                    ]
                    # Adiciona a linha na aba identificacao
                    aba_identificacao.append_row(nova_linha)
                    st.success(f"🎉 Paciente '{nome_paciente}' cadastrado com sucesso no banco de dados!")
                except Exception as e:
                    st.error(f"Erro ao salvar dados na nuvem: {e}")

# ==============================================================================
# BLOCO 3 DE 5: ABA 2 — ANAMNESE CLÍNICA DETALHADA
# ==============================================================================
with tab2:
    st.header("🩺 Anamnese Clínica")
    st.write("Preencha o histórico de desenvolvimento e saúde do paciente.")
    
    with st.form("form_anamnese", clear_on_submit=True):
        st.subheader("📍 Identificação de Vínculo")
        id_paciente_anamnese = st.text_input("Código/ID do Paciente Cadastrado (Deve ser igual ao da Aba 1):", placeholder="PAC001")
        
        st.markdown("---")
        st.subheader("👶 Desenvolvimento Motor e Linguagem")
        col1, col2 = st.columns(2)
        with col1:
            desenv_motor = st.text_area("Marcos de Desenvolvimento Motor (Sentou, andou no tempo esperado?):", placeholder="Detalhes sobre o desenvolvimento motor...")
            desenv_linguagem = st.text_area("Desenvolvimento da Linguagem (Primeiras palavras, balbucios?):", placeholder="Detalhes sobre o início da fala...")
        with col2:
            compreensao = st.text_area("Compreensão (Atende a comandos, atende quando chamado?):", placeholder="Como é a compreensão do paciente...")
            comportamento = st.text_area("Comportamento e Interação Social:", placeholder="Agitado, tímido, interage bem com outras crianças...")
            
        st.markdown("---")
        st.subheader("🍽️ Funções Estomatognáticas (Alimentação e Respiração)")
        col3, col4 = st.columns(2)
        with col3:
            alimentacao = st.text_area("Histórico de Alimentação (Mastigação, seletividade alimentar, engasgos?):", placeholder="Dificuldades ou padrões alimentares...")
        with col4:
            respiracao_sono = st.text_area("Respiração e Sono (Respora pela boca, ronca, sono agitado?):", placeholder="Padrão respiratório e de sono...")
            
        st.markdown("---")
        st.subheader("🏥 Histórico Médico e Familiar")
        historico_medico = st.text_area("Histórico Médico, Exames e Antecedentes Familiares relevante:", placeholder="Cirurgias, otites frequentes, casos semelhantes na família...")
        
        botao_salvar_anamnese = st.form_submit_button("💾 Salvar Anamnese na Nuvem")
        
    if botao_salvar_anamnese:
        if not id_paciente_anamnese:
            st.warning("⚠️ Você precisa informar o 'Código/ID do Paciente' para vincular a anamnese!")
        elif gspread_client is None:
            st.error("❌ Não há conexão ativa com o Google Sheets. Verifique o Bloco 1.")
        else:
            with st.spinner("Gravando anamnese no Google Sheets..."):
                try:
                    nova_anamnese = [
                        id_paciente_anamnese,
                        desenv_motor,
                        desenv_linguagem,
                        compreensao,
                        comportamento,
                        alimentacao,
                        respiracao_sono,
                        historico_medico
                    ]
                    aba_anamnese.append_row(nova_anamnese)
                    st.success(f"🎉 Anamnese do paciente '{id_paciente_anamnese}' salva com sucesso no banco de dados!")
                except Exception as e:
                    st.error(f"Erro ao salvar anamnese na nuvem: {e}")

# ==============================================================================
# BLOCO 4 DE 5: ABA 3 — EVOLUÇÕES/RELATÓRIOS & ABA 4 — AGENDA INTEGRADA
# ==============================================================================
with tab3:
    st.header("📈 Evoluções Clínicas e Relatórios")
    st.write("Registre o progresso diário do paciente e o planejamento das sessões.")
    
    with st.form("form_evolucao", clear_on_submit=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            id_paciente_evolucao = st.text_input("Código/ID do Paciente:", placeholder="PAC001")
            data_sessao = st.text_input("Data da Sessão (DD/MM/AAAA):", placeholder="14/08/2026")
            tipo_sessao = st.selectbox("Tipo de Atendimento:", ["Fonoterapia", "Avaliação", "Retorno", "Supervisão"])
        with col2:
            descricao_evolucao = st.text_area("Evolução Clínica (Conduta, desempenho e respostas aos estímulos):", placeholder="Descreva como foi a sessão...")
            orientacoes_casa = st.text_area("Orientações para Casa / Planejamento Próxima Sessão:", placeholder="Tarefas ou estratégias passadas aos responsáveis...")
            
        botao_salvar_evolucao = st.form_submit_button("💾 Salvar Evolução na Nuvem")
        
    if botao_salvar_evolucao:
        if not id_paciente_evolucao or not descricao_evolucao:
            st.warning("⚠️ Os campos 'Código/ID' e 'Evolução Clínica' são obrigatórios!")
        elif gspread_client is None:
            st.error("❌ Não há conexão ativa com o Google Sheets.")
        else:
            with st.spinner("Gravando evolução no Google Sheets..."):
                try:
                    nova_evolucao = [
                        id_paciente_evolucao,
                        data_sessao,
                        tipo_sessao,
                        descricao_evolucao,
                        orientacoes_casa
                    ]
                    aba_evolucao.append_row(nova_evolucao)
                    st.success(f"🎉 Evolução do paciente '{id_paciente_evolucao}' gravada com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar evolução na nuvem: {e}")

with tab4:
    st.header("📅 Agenda de Atendimentos")
    st.write("Controle de horários e agendamentos da clínica sincronizado com a nuvem.")
    
    with st.form("form_agenda", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            data_agenda = st.text_input("Data do Atendimento (DD/MM/AAAA):", placeholder="17/08/2026")
            horario_agenda = st.text_input("Horário (HH:MM):", placeholder="14:00")
        with col2:
            paciente_agenda = st.text_input("Nome do Paciente:", placeholder="Nome completo do paciente")
            status_agenda = st.selectbox("Status Inicial:", ["Agendado", "Confirmado", "Cancelado", "Atendido"])
            
        botao_salvar_agenda = st.form_submit_button("💾 Confirmar Agendamento na Nuvem")
        
    if botao_salvar_agenda:
        if not data_agenda or not paciente_agenda:
            st.warning("⚠️ Os campos 'Data' e 'Nome do Paciente' são obrigatórios!")
        elif gspread_client is None:
            st.error("❌ Não há conexão ativa com o Google Sheets.")
        else:
            with st.spinner("Gravando agendamento no Google Sheets..."):
                try:
                    novo_agendamento = [
                        data_agenda,
                        horario_agenda,
                        paciente_agenda,
                        status_agenda
                    ]
                    aba_agenda.append_row(novo_agendamento)
                    st.success(f"🎉 Compromisso com '{paciente_agenda}' agendado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar agendamento na nuvem: {e}")

# ==============================================================================
# BLOCO 5 DE 5: ABA 5 — CENTRAL DO PACIENTE (PRONTUÁRIO DIGITAL ÚNICO)
# ==============================================================================
with tab5:
    st.header("📂 Central do Paciente — Prontuário Digital Único")
    st.write("Busque e visualize o histórico completo e consolidado de qualquer paciente direto da nuvem.")
    
    if gspread_client is None:
        st.error("❌ Conexão com a nuvem indisponível. Não é possível carregar os prontuários.")
    else:
        try:
            # Puxa todas as linhas da aba de identificação para listar os pacientes
            registros_id = aba_identificacao.get_all_records()
            
            # Filtra e monta a lista apenas com os nomes dos pacientes para o selectbox
            lista_nomes_pacientes = [p.get("Nome Completo", "") for p in registros_id if p.get("Nome Completo", "")]
            lista_nomes_pacientes = sorted(list(set(lista_nomes_pacientes)))  # Remove duplicados e ordena
            
            if not lista_nomes_pacientes:
                st.info("💡 Nenhum paciente cadastrado no Google Sheets até o momento. Vá para a Aba 1.")
            else:
                paciente_selecionado = st.selectbox("🔍 Selecione o Paciente para abrir a Pasta Digital:", lista_nomes_pacientes)
                
                # Encontra a linha de dados cadastrais do paciente selecionado
                dados_cadastrais = next((p for p in registros_id if p.get("Nome Completo", "") == paciente_selecionado), None)
                
                if dados_cadastrais:
                    id_atual = dados_cadastrais.get("Código/ID do Paciente (Ex: PAC001):", "") or dados_cadastrais.get("ID", "")
                    # Tenta pegar por índice caso a chave mude ligeiramente
                    if not id_atual and len(dados_cadastrais.values()) > 0:
                        id_atual = list(dados_cadastrais.values())[0]
                        
                    st.markdown("---")
                    
                    # Painel 1: Dados Cadastrais Básicos
                    st.subheader("📋 Informações Cadastrais")
                    col_id1, col_id2 = st.columns(2)
                    with col_id1:
                        st.markdown(f"**ID do Paciente:** {id_atual}")
                        st.markdown(f"**Nome Completo:** {dados_cadastrais.get('Nome Completo:', '') or dados_cadastrais.get('Nome Completo', '')}")
                        st.markdown(f"**Data de Nascimento:** {dados_cadastrais.get('Data de Nascimento (DD/MM/AAAA):', '') or dados_cadastrais.get('Data de Nascimento', '')}")
                    with col_id2:
                        st.markdown(f"**Idade:** {dados_cadastrais.get('Idade:', '') or dados_cadastrais.get('Idade', '')}")
                        st.markdown(f"**Responsável:** {dados_cadastrais.get('Nome do Responsável (Se menor):', '') or dados_cadastrais.get('Nome do Responsável', '')}")
                        st.markdown(f"**Contato:** {dados_cadastrais.get('Telefone de Contato (Com DDD):', '') or dados_cadastrais.get('Telefone de Contato', '')}")
                    
                    st.info(f"**Queixa Principal:** {dados_cadastrais.get('Queixa Principal (Breve resumo):', '') or dados_cadastrais.get('Queixa Principal', '')}")
                    
                    # Painel 2: Histórico de Anamnese Relacionado
                    st.markdown("---")
                    st.subheader("🩺 Histórico Clínico (Anamnese)")
                    try:
                        registros_anamnese = aba_anamnese.get_all_records()
                        # Procura a anamnese que bate com o ID do paciente
                        anamnese_paciente = next((a for a in registros_anamnese if str(list(a.values())[0]) == str(id_atual)), None)
                        
                        if anamnese_paciente:
                            chaves_an = list(anamnese_paciente.keys())
                            st.markdown(f"**Marcos de Desenvolvimento Motor:** {anamnese_paciente.get(chaves_an[1], 'Não informado') if len(chaves_an) > 1 else ''}")
                            st.markdown(f"**Desenvolvimento de Linguagem:** {anamnese_paciente.get(chaves_an[2], 'Não informado') if len(chaves_an) > 2 else ''}")
                            st.markdown(f"**Compreensão:** {anamnese_paciente.get(chaves_an[3], 'Não informado') if len(chaves_an) > 3 else ''}")
                            st.markdown(f"**Comportamento:** {anamnese_paciente.get(chaves_an[4], 'Não informado') if len(chaves_an) > 4 else ''}")
                            st.markdown(f"**Alimentação (Funções Estomatognáticas):** {anamnese_paciente.get(chaves_an[5], 'Não informado') if len(chaves_an) > 5 else ''}")
                            st.markdown(f"**Respiração e Sono:** {anamnese_paciente.get(chaves_an[6], 'Não informado') if len(chaves_an) > 6 else ''}")
                            st.markdown(f"**Histórico Médico/Familiar:** {anamnese_paciente.get(chaves_an[7], 'Não informado') if len(chaves_an) > 7 else ''}")
                        else:
                            st.warning("⚠️ Nenhuma anamnese clínica foi preenchida para este paciente ainda.")
                    except Exception as e_an:
                        st.caption(f"Não foi possível processar os campos de anamnese: {e_an}")
                        
                    # Painel 3: Histórico de Evoluções das Sessões
                    st.markdown("---")
                    st.subheader("📈 Linha do Tempo de Atendimentos (Evoluções)")
                    try:
                        registros_evolucoes = aba_evolucao.get_all_records()
                        evolucoes_paciente = [e for e in registros_evolucoes if str(list(e.values())[0]) == str(id_atual)]
                        
                        if not evolucoes_paciente:
                            st.info("💡 Nenhuma sessão evolutiva registrada para este paciente.")
                        else:
                            for idx, ev in enumerate(evolucoes_paciente):
                                chaves_ev = list(ev.keys())
                                data_ev = ev.get(chaves_ev[1], 'Sem Data') if len(chaves_ev) > 1 else 'Sem Data'
                                tipo_ev = ev.get(chaves_ev[2], 'Sessão') if len(chaves_ev) > 2 else 'Sessão'
                                desc_ev = ev.get(chaves_ev[3], '') if len(chaves_ev) > 3 else ''
                                orient_ev = ev.get(chaves_ev[4], '') if len(chaves_ev) > 4 else ''
                                
                                with st.expander(f"🗓️ Sessão em {data_ev} — Tipo: {tipo_ev}"):
                                    st.markdown(f"**Conduta e Evolução:** {desc_ev}")
                                    if orient_ev:
                                        st.markdown(f"**Orientações enviadas para casa:** {orient_ev}")
                    except Exception as e_ev:
                        st.caption(f"Não foi possível processar a linha de evoluções: {e_ev}")
        except Exception as e:
            st.error(f"Erro ao carregar Central do Paciente: {e}")
            st.info("Certifique-se de que a planilha do Google Sheets possui dados válidos e cabeçalhos na primeira linha.")
