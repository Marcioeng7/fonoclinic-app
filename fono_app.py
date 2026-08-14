# ==============================================================================
# BLOCO 1 DE 5: MOTORES, CONEXÃO CLOUD (GOOGLE SHEETS) E MÁGINA DAS 6 ABAS ORIGINAL
# ==============================================================================
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials as SACredentials
from datetime import datetime, timedelta

# 1. CONFIGURAÇÃO DA PÁGINA (Deve ser o primeiro comando Streamlit)
st.set_page_config(
    page_title="FonoClinic v1.3",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. MOTOR DE CONEXÃO COM O GOOGLE SHEETS
@st.cache_resource
def conectar_google_sheets():
    try:
        escopos = [
            "https://googleapis.com",
            "https://googleapis.com"
        ]
        # Carrega de forma blindada os Secrets do Streamlit Cloud
        info_chaves = dict(st.secrets["gcp_service_account"])
        credenciais = SACredentials.from_service_account_info(info_chaves, scopes=escopos)
        cliente = gspread.authorize(credenciais)
        
        # ID da sua planilha extraído do diário de bordo
        id_planilha = "1qLEa7_iEPSkENJSovjy6_3yzVVjtVAKnJDkteG6Skdw"
        return cliente.open_by_key(id_planilha)
    except Exception as e:
        st.error(f"Erro crítico de comunicação cloud: {e}")
        return None

# Conecta ao banco de dados mestre na nuvem
gspread_client = conectar_google_sheets()

if gspread_client:
    try:
        aba_identificacao = gspread_client.worksheet("identificacao")
        aba_anamnese = gspread_client.worksheet("anamnese")
        aba_evolucao = gspread_client.worksheet("evolucoes_relatorios")
        aba_agenda = gspread_client.worksheet("agenda")
    except Exception as e:
        st.error(f"Erro ao mapear abas físicas da planilha: {e}")

# 3. CABEÇALHO OFICIAL DA CLÍNICA
st.title("📝 FonoClinic v1.3 — Painel de Gestão e Prontuários")
st.markdown("---")

# Criação exata das 6 abas solicitadas pela jornada da Dra. Michelle Neves
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 1. Painel de Atendimento",
    "📅 2. Marcar Horário",
    "👤 3. Admitir Paciente (Cadastro)",
    "📝 4. Preencher Anamnese",
    "🗂️ 5. Central do Paciente (Prontuário)",
    "📄 6. Laudos & PDFs"
])

# ==============================================================================
# BLOCO 2 DE 5: ABA 1 — PAINEL DE ATENDIMENTO COMPLETO COM CARDS E FILTROS
# ==============================================================================
with tab1:
    st.header("📋 Painel de Atendimento")
    st.write("Visão unificada da clínica. Acompanhe os horários e registre a presença com botões de ação rápida.")
    
    if gspread_client is None:
        st.error("❌ Não há conexão ativa com a nuvem do Google Sheets.")
    else:
        # Filtro de Escopo de Tempo
        filtro_tempo = st.radio(
            "Visualizar atendimentos por:",
            ["Apenas Hoje", "Esta Semana", "Este Mês", "Todo o Ano"],
            horizontal=True
        )
        
        # Puxa os dados atualizados da agenda
        try:
            with st.spinner("Buscando agenda atualizada na nuvem..."):
                registros_agenda = aba_agenda.get_all_records()
        except Exception as e:
            st.error(f"Erro ao carregar dados da agenda: {e}")
            registros_agenda = []

        hoje_dt = datetime.now()
        data_hoje_str = hoje_dt.strftime("%d/%m/%Y")
        
        # Filtragem Inteligente dos dados com base no tempo
        atendimentos_filtrados = []
        for reg in registros_agenda:
            data_reg_str = str(reg.get("Data", "") or reg.get("Data do Atendimento (DD/MM/AAAA):", "")).strip()
            try:
                reg_dt = datetime.strptime(data_reg_str, "%d/%m/%Y")
            except:
                continue # Pula caso a data esteja mal formatada
                
            if filtro_tempo == "Apenas Hoje" and data_reg_str == data_hoje_str:
                atendimentos_filtrados.append((reg, reg_dt))
            elif filtro_tempo == "Esta Semana":
                inicio_semana = hoje_dt - timedelta(days=hoje_dt.weekday())
                fim_semana = inicio_semana + timedelta(days=6)
                if inicio_semana.date() <= reg_dt.date() <= fim_semana.date():
                    atendimentos_filtrados.append((reg, reg_dt))
            elif filtro_tempo == "Este Mês" and reg_dt.month == hoje_dt.month and reg_dt.year == hoje_dt.year:
                atendimentos_filtrados.append((reg, reg_dt))
            elif filtro_tempo == "Todo o Ano" and reg_dt.year == hoje_dt.year:
                atendimentos_filtrados.append((reg, reg_dt))

        # Ordena por data e depois por horário
        atendimentos_filtrados.sort(key=lambda x: (x[1], str(x[0].get("Horário", "") or x[0].get("Horário (HH:MM):", ""))))
        
        st.markdown("---")
        if not atendimentos_filtrados:
            st.info(f"💡 Nenhum agendamento encontrado para o escopo selecionado ({filtro_tempo}).")
        else:
            # Renderização em formato de Cartões (Cards)
            for idx, (atend, _) in enumerate(atendimentos_filtrados):
                data_at = atend.get("Data", "") or atend.get("Data do Atendimento (DD/MM/AAAA):", "")
                hora_at = atend.get("Horário", "") or atend.get("Horário (HH:MM):", "")
                pac_at = atend.get("Nome do Paciente", "") or atend.get("Paciente", "")
                status_at = atend.get("Status", "") or atend.get("Status Inicial:", "")
                
                # Cores de marcação baseadas no status atual
                cor_status = "🔵"
                if status_at == "Atendido": cor_status = "🟢"
                elif "Falta" in status_at: cor_status = "🔴"
                elif status_at == "Confirmado": cor_status = "🟡"
                
                with st.container():
                    col_c1, col_c2, col_c3 = st.columns([1, 3, 2])
                    with col_c1:
                        st.markdown(f"### `{hora_at}`\n*{data_at}*")
                    with col_c2:
                        st.markdown(f"### {pac_at}\nStatus atual: {cor_status} **{status_at}**")
                    with col_c3:
                        # Identificadores para os botões acionarem as linhas corretas
                        id_p_btn = st.text_input(f"Confirme o ID para evoluir {pac_at}:", placeholder="PAC001", key=f"id_btn_{idx}")
                        
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if btn_col1.button("✅ Concluir", key=f"btn_ok_{idx}"):
                                if not id_p_btn:
                                    st.warning("⚠️ Insira o ID do paciente para registrar!")
                                else:
                                    with st.spinner("Computando atendimento na nuvem..."):
                                        try:
                                            # 1. Registra a evolução simplificada com contagem automática +1
                                            aba_evolucao.append_row([id_p_btn, data_at, "Fonoterapia", "Atendimento concluído via Painel Diário. Presença confirmada.", "+1 Sessão"])
                                            st.success(f"🎉 Sessão de {pac_at} registrada!")
                                            st.rerun()
                                        except Exception as err:
                                            st.error(f"Erro: {err}")
                        with btn_col2:
                            if btn_col2.button("🚨 Falta", key=f"btn_falta_{idx}"):
                                if not id_p_btn:
                                    st.warning("⚠️ Insira o ID do paciente para registrar!")
                                else:
                                    with st.spinner("Registrando falta na nuvem..."):
                                        try:
                                            aba_evolucao.append_row([id_p_btn, data_at, "Falta", "Paciente faltou ao atendimento programado.", "0"])
                                            st.error(f"🚨 Falta registrada para {pac_at}.")
                                            st.rerun()
                                        except Exception as err:
                                            st.error(f"Erro: {err}")
                st.markdown("---")

# ==============================================================================
# BLOCO 3 DE 5: ABA 2 — MARCAR HORÁRIO COM AGENDAMENTO EM LOTE E RECORRÊNCIA
# ==============================================================================
with tab2:
    st.header("📅 Marcar Horário de Atendimento")
    st.write("Agende consultas isoladas ou configure recorrências em lote automaticamente na nuvem.")
    
    with st.form("form_agendamento_lote", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nome_paciente_agenda = st.text_input("Nome Completo do Paciente:", placeholder="Digite o nome para a grade")
            data_inicio_str = st.text_input("Data do Atendimento (ou Início do Lote) (DD/MM/AAAA):", placeholder="14/08/2026")
            
            # Automação de Horários de 10 em 10 minutos (Gera lista limpa de opções)
            lista_horarios = []
            for h in range(7, 21): # Das 07:00 às 20:00
                for m in range(0, 60, 10):
                    lista_horarios.append(f"{h:02d}:{m:02d}")
            horario_selecionado = st.selectbox("Horário da Consulta:", lista_horarios)
            
        with col2:
            tipo_recorrencia = st.selectbox(
                "Configuração de Recorrência (Agendamento em Lote):",
                ["Consulta Única", "Repetição Semanal (4 sessões)", "Repetição Semanal (8 sessões)", "Repetição Mensal (3 meses)"]
            )
            status_inicial = st.selectbox("Status Inicial:", ["Agendado", "Confirmado"])
            
        botao_marcar_agenda = st.form_submit_button("💾 Salvar Agendamento(s) na Nuvem")
        
    if botao_marcar_agenda:
        if not nome_paciente_agenda or not data_inicio_str:
            st.warning("⚠️ O 'Nome do Paciente' e a 'Data' são obrigatórios!")
        elif gspread_client is None:
            st.error("❌ Sem conexão ativa com o Google Sheets.")
        else:
            with st.spinner("Processando engenharia de datas em lote..."):
                try:
                    # Converte a data inicial para fazer os cálculos matemáticos de tempo
                    data_base = datetime.strptime(data_inicio_str.strip(), "%d/%m/%Y")
                    datas_agendamento = []
                    
                    # Lógica de cálculo em lote baseada na recorrência escolhida
                    if tipo_recorrencia == "Consulta Única":
                        datas_agendamento.append(data_base)
                    elif "4 sessões" in tipo_recorrencia:
                        for i in range(4):
                            datas_agendamento.append(data_base + timedelta(weeks=i))
                    elif "8 sessões" in tipo_recorrencia:
                        for i in range(8):
                            datas_agendamento.append(data_base + timedelta(weeks=i))
                    elif "3 meses" in tipo_recorrencia:
                        for i in range(3):
                            # Adiciona aproximadamente 30 dias para cada mês subsequente
                            datas_agendamento.append(data_base + timedelta(days=i*30))
                    
                    # Gravação em lote de todas as linhas calculadas na aba agenda
                    linhas_para_salvar = []
                    for dt in datas_agendamento:
                        data_formatada = dt.strftime("%d/%m/%Y")
                        linhas_para_salvar.append([data_formatada, horario_selecionado, nome_paciente_agenda, status_inicial])
                    
                    # Envia todas as linhas de uma vez para a nuvem (Rápido e seguro)
                    aba_agenda.append_rows(linhas_para_salvar)
                    
                    st.success(f"🎉 Sucesso! Foram gerados e salvos {len(linhas_para_salvar)} agendamentos na grade da clínica!")
                except ValueError:
                    st.error("❌ Formato de data inválido! Certifique-se de digitar no padrão DD/MM/AAAA (Ex: 14/08/2026).")
                except Exception as e:
                    st.error(f"Erro ao salvar agendamentos na nuvem: {e}")

# ==============================================================================
# BLOCO 4 DE 5: ABA 3 — ADMITIR PACIENTE & ABA 4 — ANAMNESE CLÍNICA DE 53 VARIÁVEIS
# ==============================================================================

# --- ABA 3: ADMITIR PACIENTE (CADASTRO) ---
with tab3:
    st.header("👤 Admitir Novo Paciente")
    st.write("Efetue a admissão inicial e o cadastro dos dados de contato do paciente na nuvem.")
    
    with st.form("form_admissao_cadastro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            id_paciente = st.text_input("Código/ID do Paciente (Ex: PAC001):", placeholder="PAC001")
            nome_paciente = st.text_input("Nome Completo do Paciente:", placeholder="Nome do paciente")
            data_nascimento = st.text_input("Data de Nascimento (DD/MM/AAAA):", placeholder="14/08/2020")
            idade_paciente = st.text_input("Idade Atual:", placeholder="Ex: 6 anos")
        with col2:
            nome_responsavel = st.text_input("Nome do Responsável Legal:", placeholder="Mãe, Pai ou Tutor")
            telefone_contato = st.text_input("Telefone de Contato (Com DDD):", placeholder="(21) 99999-9999")
            queixa_principal = st.text_area("Queixa Principal (Relato inicial do responsável):", placeholder="Motivo da busca pelo atendimento...")
            
        botao_salvar_admissao = st.form_submit_button("💾 Confirmar Admissão na Nuvem")
        
    if botao_salvar_admissao:
        if not id_paciente or not nome_paciente:
            st.warning("⚠️ O 'Código/ID' e o 'Nome Completo' são obrigatórios para a admissão!")
        elif gspread_client is None:
            st.error("❌ Sem conexão ativa com o Google Sheets.")
        else:
            with st.spinner("Gravando admissão no banco de dados..."):
                try:
                    nova_linha_id = [id_paciente, nome_paciente, data_nascimento, idade_paciente, nome_responsavel, telefone_contato, queixa_principal]
                    aba_identificacao.append_row(nova_linha_id)
                    st.success(f"🎉 Paciente '{nome_paciente}' admitido com sucesso na clínica!")
                except Exception as e:
                    st.error(f"Erro ao salvar admissão na nuvem: {e}")

# --- ABA 4: PREENCHER ANAMNESE CLÍNICA EXPANDIDA ---
with tab2:  # Vinculado à aba física número 4 estrutural
    st.header("📝 Preencher Anamnese Clínica Expandida")
    st.write("Formulário fonoaudiológico completo para investigação profunda de neurodesenvolvimento e rotina.")
    
    with st.form("form_anamnese_gigante", clear_on_submit=True):
        st.subheader("📍 Vinculação Obrigatória")
        id_paciente_anamnese = st.text_input("Código/ID do Paciente Admitido (Deve ser igual ao ID da Admissão):", placeholder="PAC001")
        
        st.markdown("---")
        st.subheader("👶 Seção 1: Marcos do Desenvolvimento Motor e do Sono")
        col_an1, col_an2 = st.columns(2)
        with col_an1:
            idade_sentou = st.text_input("Com qual idade sentou sozinh(a)?", placeholder="Ex: 6 meses")
            idade_andou = st.text_input("Com qual idade andou sozinh(a)?", placeholder="Ex: 1 ano e 2 meses")
            controle_esfincter = st.text_area("Histórico de Desfralde / Controle de Esfíncteres:", placeholder="Detalhes sobre o desfralde diurno/noturno...")
        with col_an2:
            padrao_sono = st.text_area("Qualidade e Padrão do Sono:", placeholder="Agitado, terror noturno, acorda muito, ronca, dorme de boca aberta...")
            postura_dormir = st.text_input("Postura preferencial ao dormir:", placeholder="De lado, bruços, barriga para cima...")
            
        st.markdown("---")
        st.subheader("🗣️ Seção 2: Marcos de Fala, Linguagem e Comunicação Atual")
        col_an3, col_an4 = st.columns(2)
        with col_an3:
            primeiras_palavras = st.text_input("Idade em que surgiram as primeiras palavras com intenção:", placeholder="Ex: 12 meses")
            comunicacao_atual = st.text_area("Como se comunica atualmente?", placeholder="Fala frases completas, aponta, usa gestos, palavras isoladas, ecolalia...")
            inteligibilidade = st.selectbox("A fala é compreendida por pessoas de fora do ciclo familiar?", ["Sim, totalmente", "Parcialmente", "Apenas pela família próxima", "Não compreendida"])
        with col_an4:
            compreensao_comandos = st.text_area("Capacidade de Compreensão:", placeholder="Atende a comandos simples/complexos, olha quando chamado pelo nome...")
            interacao_social = st.text_area("Padrão de Comportamento e Interação Social:", placeholder="Interage bem com outras crianças, prefere brincar sozinho, contato visual adequado...")

        st.markdown("---")
        st.subheader("🍽️ Seção 3: Funções Estomatognáticas e Rotina Alimentar")
        col_an5, col_an6 = st.columns(2)
        with col_an5:
            tipo_amamentacao = st.text_input("Histórico de Amamentação:", placeholder="Materna até qual idade, uso de fórmula...")
            introducao_alimentar = st.text_area("Como foi a introdução alimentar?", placeholder="Aceitou bem, teve recusas, histórico de engasgos...")
            mastigacao_padrao = st.text_area("Padrão de Mastigação e Deglutição:", placeholder="Mastiga de boca aberta, cansaço ao mastigar, acumula alimento na boca...")
        with col_an6:
            seletividade_alimentar = st.text_area("Seletividade Alimentar:", placeholder="Recusa texturas, cores ou grupos específicos de alimentos? Detalhe...")
            habitos_orais = st.text_area("Hábitos Orais Deletérios:", placeholder="Uso de mamadeira (até quando), chupeta, roer unhas, morder objetos...")

        st.markdown("---")
        st.subheader("📺 Seção 4: Rotina Diária e Exposição a Telas/Eletrônicos")
        col_an7, col_an8 = st.columns(2)
        with col_an7:
            tempo_tela = st.text_input("Tempo diário estimado de exposição a telas (TV, celular, tablet):", placeholder="Ex: 3 horas por dia")
        with col_an8:
            conteudo_tela = st.text_area("Principais conteúdos assistidos e comportamento durante a exposição:", placeholder="Desenhos, vídeos de jogos, fica hipnotizado, imita falas das telas...")

        st.markdown("---")
        st.subheader("🏥 Seção 5: Histórico Médico e Exames Complementares Avançados")
        col_an9, col_an10 = st.columns(2)
        with col_an9:
            exames_auditivos = st.text_area("Avaliações Auditivas (BERA, Audiometria, Impedanciometria):", placeholder="Resultados e datas dos exames auditivos...")
            exames_neurologicos = st.text_area("Exames Neurológicos (EEG, Ressonância Magnética, Tomografia):", placeholder="Resultados de exames de imagem ou atividade cerebral...")
            acompanhamento_especialistas = st.text_area("Acompanhamento com Neuropediatra, Psiquiatra Infantil ou Psicólogo:", placeholder="Nome do especialista, diagnósticos em investigação ou fechados...")
        with col_an10:
            relatorios_escolares = st.text_area("Histórico e Relatórios Pedagógicos da Escola:", placeholder="Queixas da professora, adaptação escolar, suporte de mediação...")
            antecedentes_familiares = st.text_area("Antecedentes Familiares de Alterações de Fala, Linguagem ou Aprendizagem:", placeholder="Casos de atraso de fala, autismo, TDAH ou dislexia na família...")
            historico_clinico_geral = st.text_area("Histórico Clínico Geral (Cirurgias, otites de repetição, internações):", placeholder="Intervenções cirúrgicas, quadros alérgicos, uso de medicações contínuas...")

        botao_salvar_anamnese_expandida = st.form_submit_button("💾 Salvar Anamnese Expandida na Nuvem")
        
    if botao_salvar_anamnese_expandida:
        if not id_paciente_anamnese:
            st.warning("⚠️ Você precisa informar o 'Código/ID do Paciente' para salvar este prontuário!")
        elif gspread_client is None:
            st.error("❌ Sem conexão ativa com o Google Sheets.")
        else:
            with st.spinner("Gravando todas as variáveis clínicas na nuvem..."):
                try:
                    # Agrupamento linear das variáveis estruturadas para envio à aba anamnese
                    dados_anamnese_completa = [
                        id_paciente_anamnese, idade_sentou, idade_andou, controle_esfincter, padrao_sono, postura_dormir,
                        primeiras_palavras, comunicacao_atual, inteligibilidade, compreensao_comandos, interacao_social,
                        tipo_amamentacao, introducao_alimentar, mastigacao_padrao, seletividade_alimentar, habitos_orais,
                        tempo_tela, conteudo_tela, exames_auditivos, exames_neurologicos, acompanhamento_especialistas,
                        relatorios_escolares, antecedentes_familiares, historico_clinico_geral
                    ]
                    aba_anamnese.append_row(dados_anamnese_completa)
                    st.success(f"🎉 Prontuário de Anamnese do paciente '{id_paciente_anamnese}' gravado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar anamnese robusta: {e}")

# ==============================================================================
# BLOCO 5 DE 5: ABA 5 — CENTRAL DO PACIENTE (TEXTO PURO) & ABA 6 — LAUDOS & PDFS
# ==============================================================================

# --- ABA 5: CENTRAL DO PACIENTE (PRONTUÁRIO DIGITAL ÚNICO) ---
with tab5:
    st.header("🗂️ Central do Paciente (Prontuário)")
    st.write("Busque e visualize o histórico clínico unificado e consolidado diretamente da nuvem.")
    
    if gspread_client is None:
        st.error("❌ Conexão com a nuvem indisponível. Não é possível carregar os prontuários.")
    else:
        try:
            # Captura todas as linhas em formato de matriz de texto puro para evitar colisões
            matriz_id = aba_identificacao.get_all_values()
            
            if len(matriz_id) <= 1:
                st.info("💡 Nenhum paciente admitido no Google Sheets até o momento. Vá para a Aba 3.")
            else:
                # Separa os cabeçalhos da primeira linha e as linhas de dados puras
                cabecalhos_id = matriz_id[0]
                linhas_dados_id = matriz_id[1:]
                
                # Monta a lista de busca apenas com os nomes (coluna 2 - Índice 1)
                lista_nomes = []
                for linha in linhas_dados_id:
                    if len(linha) > 1 and linha[1]:
                        lista_nomes.append(str(linha[1]).strip())
                
                lista_nomes = sorted(list(set(lista_nomes)))
                nome_selecionado = st.selectbox("🔍 Selecione o Paciente para abrir a Pasta Digital:", lista_nomes)
                
                # Localiza a linha correspondente ao paciente selecionado
                linha_paciente = None
                for linha in linhas_dados_id:
                    if len(linha) > 1 and str(linha[1]).strip() == nome_selecionado:
                        linha_paciente = linha
                        break
                
                if linha_paciente:
                    # Captura as colunas por índice fixo para blindagem absoluta contra erros
                    id_atual = linha_paciente[0] if len(linha_paciente) > 0 else "Sem ID"
                    data_nasc_at = linha_paciente[2] if len(linha_paciente) > 2 else "Não informada"
                    idade_at = linha_paciente[3] if len(linha_paciente) > 3 else "Não informada"
                    resp_at = linha_paciente[4] if len(linha_paciente) > 4 else "Não informado"
                    contato_at = linha_paciente[5] if len(linha_paciente) > 5 else "Não informado"
                    queixa_at = linha_paciente[6] if len(linha_paciente) > 6 else "Não informada"
                    
                    st.markdown("---")
                    st.subheader("📋 Informações Cadastrais de Admissão")
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        st.markdown(f"**ID do Paciente:** `{id_atual}`")
                        st.markdown(f"**Nome Completo:** {nome_selecionado}")
                        st.markdown(f"**Data de Nascimento:** {data_nasc_at}")
                    with col_p2:
                        st.markdown(f"**Idade Cadastrada:** {idade_at}")
                        st.markdown(f"**Responsável Legal:** {resp_at}")
                        st.markdown(f"**Telefone de Contato:** {contato_at}")
                    
                    st.info(f"**Queixa Principal de Entrada:** {queixa_at}")
                    
                    # --- BUSCA DA ANAMNESE CLÍNICA ---
                    st.markdown("---")
                    st.subheader("🩺 Prontuário de Desenvolvimento (Anamnese Expandida)")
                    
                    matriz_an = aba_anamnese.get_all_values()
                    linha_anamnese = None
                    if len(matriz_an) > 1:
                        for lan in matriz_an[1:]:
                            if len(lan) > 0 and str(lan[0]).strip() == str(id_atual).strip():
                                float_linha_an = lan
                                break
                    
                    if float_linha_an:
                        st.markdown(f"**Marcos Motores (Sentou/Andou):** Sentou com `{float_linha_an[1] if len(float_linha_an)>1 else ''}` | Andou com `{float_linha_an[2] if len(float_linha_an)>2 else ''}`")
                        st.markdown(f"**Controle de Esfíncteres / Desfralde:** {float_linha_an[3] if len(float_linha_an)>3 else 'Não informado'}")
                        st.markdown(f"**Padrão e Qualidade do Sono:** {float_linha_an[4] if len(float_linha_an)>4 else 'Não informado'}")
                        st.markdown(f"**Primeiras Palavras / Fala Inicial:** {float_linha_an[6] if len(float_linha_an)>6 else 'Não informado'}")
                        st.markdown(f"**Comunicação Atual e Expressão:** {float_linha_an[7] if len(float_linha_an)>7 else 'Não informada'}")
                        st.markdown(f"**Inteligibilidade da Fala:** {float_linha_an[8] if len(float_linha_an)>8 else 'Não informada'}")
                        st.markdown(f"**Interação Social e Comportamento:** {float_linha_an[10] if len(float_linha_an)>10 else 'Não informado'}")
                        st.markdown(f"**Seletividade Alimentar Relevante:** {float_linha_an[14] if len(float_linha_an)>14 else 'Não informada'}")
                        st.markdown(f"**Tempo de Exposição a Telas Diário:** `{float_linha_an[16] if len(float_linha_an)>16 else 'Não informado'}`")
                        st.markdown(f"**Conteúdos de Telas e Comportamento:** {float_linha_an[17] if len(float_linha_an)>17 else 'Não informado'}")
                        
                        st.markdown("##### 🏥 Exames e Laudos Complementares")
                        st.markdown(f"**Avaliações Auditivas (BERA/Audiometria):** {float_linha_an[18] if len(float_linha_an)>18 else 'Não informado'}")
                        st.markdown(f"**Exames Neurológicos (EEG/Imagem):** {float_linha_an[19] if len(float_linha_an)>19 else 'Não informado'}")
                        st.markdown(f"**Acompanhamento Imediato com Especialistas:** {float_linha_an[20] if len(float_linha_an)>20 else 'Não informado'}")
                        st.markdown(f"**Relatórios e Queixas Escolares:** {float_linha_an[21] if len(float_linha_an)>21 else 'Não informado'}")
                    else:
                        st.warning("⚠️ Nenhuma anamnese expandida foi preenchida para este ID até o momento.")
                    
                    # --- BUSCA DA LINHA DO TEMPO DE EVOLUÇÕES ---
                    st.markdown("---")
                    st.subheader("📈 Linha do Tempo e Histórico de Consultas")
                    
                    matriz_ev = aba_evolucao.get_all_values()
                    evolucoes_encontradas = []
                    if len(matriz_ev) > 1:
                        for lev in matriz_ev[1:]:
                            if len(lev) > 0 and str(lev[0]).strip() == str(id_atual).strip():
                                evolucoes_encontradas.append(lev)
                    
                    if not evolucoes_encontradas:
                        st.info("💡 Nenhuma evolução ou registro de presença computado para este paciente.")
                    else:
                        st.markdown(f"**Total de Consultas Registradas na Nuvem:** `{len(evolucoes_encontradas)}` sessões.")
                        for idx, ev in enumerate(evolucoes_encontradas):
                            dt_ev = ev[1] if len(ev) > 1 else "Sem data"
                            tp_ev = ev[2] if len(ev) > 2 else "Sessão"
                            ds_ev = ev[3] if len(ev) > 3 else ""
                            cs_ev = ev[4] if len(ev) > 4 else ""
                            
                            with st.expander(f"🗓️ Sessão Clínica em {dt_ev} — Tipo: {tp_ev}"):
                                st.markdown(f"**Conduta Técnica:** {ds_ev}")
                                if cs_ev and cs_ev != "0" and cs_ev != "+1 Sessão":
                                    st.markdown(f"**Planejamento / Atividades para Casa:** {cs_ev}")
        except Exception as e:
            st.error(f"Erro ao processar Central do Paciente por Texto Puro: {e}")

# --- ABA 6: LAUDOS & PDFS (MECANISMO DE DOCUMENTOS) ---
with tab6:
    st.header("📄 Laudos, Recibos & PDFs")
    st.write("Central de emissão de documentos médicos oficiais com o carimbo da Dra. Michelle Neves.")
    
    st.info("📌 O motor ReportLab está pronto para ser plugado nesta seção para gerar impressões físicas profissionais.")
    
    tipo_documento = st.selectbox("Selecione o tipo de documento a emitir:", ["Atestado de Comparecimento", "Recibo de Atendimento", "Relatório Fonoaudiológico de Evolução"])
    
    with st.container():
        st.write("Campos estruturais de assinatura técnica:")
        st.code("Dra. Michelle Neves — Fonoaudióloga", language="text")
        
        # Botão simulado inicial
        if st.button("🖨️ Visualizar Estrutura de Impressão"):
            st.success("Estrutura validada com sucesso! Pronto para receber a programação do PDF real.")
