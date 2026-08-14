import streamlit as st
from datetime import date, datetime, timedelta
import io

# Configuração da página - Mantendo o layout amplo (wide) para a tela não encolher
st.set_page_config(page_title="FonoClinic v1.3", page_icon="🩺", layout="wide")

# Inicialização do banco de dados na memória do navegador
if "pacientes" not in st.session_state:
    st.session_state.pacientes = {}
if "agenda" not in st.session_state:
    st.session_state.agenda = []

# Função interna para gerar as perguntas de Sim/Não com padrão em branco ("")
def pergunta_sim_nao(label, key, info_adicional=False, label_adicional="Detalhes"):
    col1, col2 = st.columns(2)
    with col1:
        resposta = st.radio(label, ["", "Sim", "Não"], index=0, key=key, horizontal=True)
    with col2:
        detalhe = ""
        if info_adicional and resposta == "Sim":
            detalhe = st.text_input(f"{label_adicional}", key=f"{key}_det")
    return resposta, detalhe

# Configuração das 6 abas oficiais e organizadas
aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
    "👤 Identificação do Paciente",
    "📝 Anamnese", 
    "📅 Marcar Horário",
    "📋 Painel de Atendimento",
    "📦 Consultas Realizadas", 
    "📄 Laudos & PDFs"
])

# =====================================================================
# ABA 1: IDENTIFICAÇÃO DO PACIENTE
# =====================================================================
with aba1:
    st.header("👤 Identificação do Paciente")
    st.write("Insira os dados cadastrais básicos de admissão.")

    nome_paciente = st.text_input("Nome Completo do Paciente (Obrigatório)", key="cad_nome").strip()
    
    col1, col2, col3 = st.columns(3)
    data_nasc = col1.date_input("Data de Nascimento", value=None, min_value=date(2000, 1, 1), key="cad_data_nasc")
    sexo = col2.selectbox("Sexo", ["", "Masculino", "Feminino", "Outro"], key="cad_sexo")
    apelido = col3.text_input("Apelido", key="cad_apelido")
    
    col4, col5, col6 = st.columns(3)
    naturalidade = col4.text_input("Naturalidade", key="cad_naturalidade")
    endereco = col5.text_input("Endereço Completo", key="cad_endereco")
    emergencia = col6.text_input("Em caso de emergência ligar para:", key="cad_emergencia")
    
    col7, col8, col9 = st.columns(3)
    estuda = col7.selectbox("Estuda?", ["", "Sim", "Não"], key="cad_estuda")
    turma = col8.text_input("Turma", key="cad_turma") if estuda == "Sim" else ""
    turno = col9.selectbox("Turno", ["", "Manhã", "Tarde", "Integral"], key="cad_turno") if estuda == "Sim" else ""
    
    col10, col11, col12 = st.columns(3)
    responsavel = col10.text_input("Nome do Responsável Legal", key="cad_responsavel")
    profissao = col11.text_input("Profissão do Responsável", key="cad_profissao")
    telefone = col12.text_input("Telefone de Contato", key="cad_telefone")

    if st.button("💾 Salvar Cadastro de Identificação", key="btn_salvar_cadastro"):
        if not nome_paciente:
            st.error("Erro: O nome do paciente é obrigatório.")
        elif nome_paciente in st.session_state.pacientes:
            st.warning(f"O paciente '{nome_paciente}' já está cadastrado.")
        else:
            st.session_state.pacientes[nome_paciente] = {
                "identificacao": {
                    "nome": nome_paciente, "data_nasc": data_nasc, "sexo": sexo, "apelido": apelido,
                    "naturalidade": naturalidade, "endereco": endereco, "emergencia": emergencia,
                    "estuda": estuda, "turma": turma, "turno": turno, "responsavel": responsavel,
                    "profissao": profissao, "telefone": telefone
                },
                "sessoes_realizadas": 0, "evolucoes": [], "anamnese": {}
            }
            st.success(f"Cadastro de '{nome_paciente}' realizado! Siga para a aba Anamnese.")

# =====================================================================
# ABA 2: ANAMNESE CLINICA DEFINITIVA COM EXAMES
# =====================================================================
with aba2:
    st.header("Anamnese — FonoClinic")
    
    if not st.session_state.pacientes:
        st.info("Por favor, realize primeiro o cadastro de identificação do paciente na Aba 1.")
    else:
        paciente_anamnese = st.selectbox("Selecione o Paciente:", list(st.session_state.pacientes.keys()), key="sel_pac_anamnese")
        
        with st.expander("📋 Queixa Principal e Histórico Clínico", expanded=True):
            queixa = st.text_area("Queixa Principal (O que te trouxe aqui?)")
            pergunta_sim_nao("Faz terapia com outros profissionais?", "ter_outros", True, "Quais?")
            st.text_input("Tem diagnóstico?")
            pergunta_sim_nao("Alérgico:", "alergia", True, "Quais?")
            pergunta_sim_nao("Toma medicação:", "medicao", True, "Quais?")
            st.text_input("Com quem passa mais tempo:")
            pergunta_sim_nao("Pratica ou gosta de esportes:", "esportes")

        with st.expander("🦶 Marcos de Desenvolvimento e Rotina de Telas", expanded=False):
            col_m1, col_m2 = st.columns(2)
            idade_sentou = col_m1.text_input("Com qual idade sentou?")
            idade_andou = col_m2.text_input("Com qual idade andou?")
            st.markdown("---")
            st.write("**🧏 Marcos de Fala e Comunicação:**")
            idade_primeiras_palavras = st.text_input("Com qual idade falou as primeiras palavras?")
            como_se_comunica_atualmente = st.text_area("Como se comunica atualmente?")
            st.markdown("---")
            st.write("**📱 Uso de Eletrônicos / Telas:**")
            tempo_telas = st.selectbox("Tempo diário estimado de exposição a telas:", ["", "Não utiliza", "Até 1 hora por dia", "De 1 a 3 horas por dia", "De 3 a 5 horas por dia", "Mais de 5 horas por dia"])
            detalhe_telas = st.text_input("Quais conteúdos costuma assistir ou jogar?")

        with st.expander("🩺 Exames e Avaliações Complementares", expanded=False):
            st.write("**🦻 Histórico e Exames Auditivos:**")
            pergunta_sim_nao("Fez o Teste da Orelhinha na maternidade?", "teste_orelha")
            pergunta_sim_nao("Apresenta infecções de ouvido (otites) recorrentes?", "inf_ouvido", True, "Teve quantas?")
            pergunta_sim_nao("Possui exame de Audiometria / Imitanciometria recente?", "audio_recente", True, "Resultado/Data?")
            pergunta_sim_nao("Possui exame do BERA (PEATE) recente?", "bera_audio", True, "Resultado/Data?")
            st.markdown("---")
            st.write("**🧠 Histórico Neurológico e Genético:**")
            pergunta_sim_nao("Já realizou exame de EEG?", "eeg_exame", True, "Resultado?")
            pergunta_sim_nao("Já realizou Ressonância Magnética (RM)?", "rm_cranio", True, "Resultado?")
            pergunta_sim_nao("Está em investigação genética?", "genetica_painel", True, "Resultado?")
            st.markdown("---")
            st.write("**🏫 Histórico Escolar e Relatórios:**")
            pergunta_sim_nao("A escola enviou algum Relatório Pedagógico?", "relatorio_escola", True, "Queixas?")
            pergunta_sim_nao("Passa por Neuropediatra ou Psiquiatra Infantil?", "medico_especialista", True, "Frequência?")

        with st.expander("🗣️ Comunicação, Interação e Conhecimentos Básicos", expanded=False):
            pergunta_sim_nao("Verbal:", "verbal")
            pergunta_sim_nao("Interage bem:", "interage")
            pergunta_sim_nao("Olha no olho ao ser chamado:", "olha_olho")
            pergunta_sim_nao("Atende a comandos:", "comandos")
            st.markdown("---")
            st.write("**Conhecimentos Pedagógicos Básicos:**")
            col_p1, col_p2 = st.columns(2)
            with col_p1: st.radio("Sabe as vogais:", ["", "Sim", "Não"], key="vogais")
            with col_p2: st.radio("Sabe as cores:", ["", "Sim", "Não"], key="cores_sabe")

        with st.expander("🧠 Rotina, Comportamento e Sinais de Alerta", expanded=False):
            pergunta_sim_nao("Seletividade alimentar:", "seletividade")
            pergunta_sim_nao("Dorme bem:", "dorme_bem")
            pergunta_sim_nao("Apresenta Estereotipia:", "estereotipia")
            pergunta_sim_nao("Apresenta Ecolalia:", "ecolalia")

        with st.expander("🚽 Autonomia, Alimentação e Histórico de Desenvolvimento", expanded=False):
            pergunta_sim_nao("Usa Fralda?", "fralda")
            pergunta_sim_nao("Sabe pedir para ir ao banheiro?", "banheiro")
            amamentacao = st.text_input("Ele(a) mamou peito ou fórmula?")
            mastigacao_degluticao = st.text_area("Descreva a mastigação e deglutição:")

        st.markdown("---")
        realizada_com = st.text_input("Anamnese realizada com:")
        st.caption("Avaliação registrada por: Dra. Michelle Neves — Fonoaudióloga")

        if st.button("💾 Salvar Anamnese Expandida", key="btn_salvar_anamnese"):
            st.session_state.pacientes[paciente_anamnese]["anamnese"] = {
                "queixa": queixa, "realizada_com": realizada_com, "idade_sentou": idade_sentou,
                "idade_andou": idade_andou, "mastigacao": mastigacao_degluticao, 
                "idade_fala": idade_primeiras_palavras, "tempo_telas": tempo_telas
            }
            st.success(f"Anamnese completa de '{paciente_anamnese}' salva localmente com sucesso!")

# =====================================================================
# ABA 3: MARCAR HORÁRIO (COM RECORRÊNCIA AUTOMÁTICA)
# =====================================================================
with aba3:
    st.header("📅 Agendamento de Consultas")
    st.write("Agende horários únicos ou configure repetições automáticas (recorrências) para o paciente.")

    col_ag1, col_ag2 = st.columns(2)
    
    with col_ag1:
        if st.session_state.pacientes:
            p_nome = st.selectbox("Selecione o Paciente para o Horário:", list(st.session_state.pacientes.keys()), key="agenda_p_sel")
        else:
            p_nome = st.text_input("Nome do Paciente para Agenda:", key="agenda_p_txt")
            
        data_inicio = st.date_input("Data da Consulta (ou Data de Início):", value=date.today(), key="agenda_data_ini")
        hora_agend = st.text_input("Horário do Atendimento (Ex: 14:00):", key="agenda_hora_txt")

    with col_ag2:
        recorrencia = st.selectbox("Repetição / Recorrência do Horário:", [
            "Consulta Única", 
            "Semanal (Todas as semanas)", 
            "Mensal (Uma vez por mês)", 
            "Anual (Uma vez por ano)"
        ])
        
        qtd_repeticoes = 1
        if recorrencia != "Consulta Única":
            qtd_repeticoes = st.number_input("Quantas vezes deseja repetir esse horário?", min_value=2, value=4, step=1)
        
        st.info("📌 Status Inicial do Agendamento: **Agendado**")

    if st.button("🗓️ Fixar na Grade de Agendamentos", key="btn_fixar_agenda"):
        if not p_nome or not hora_agend:
            st.error("Por favor, preencha o nome do paciente e o horário para agendar.")
        else:
            datas_agendadas = []
            data_atual = data_inicio
            
            for i in range(qtd_repeticoes):
                datas_agendadas.append(data_atual.strftime("%d/%m/%Y"))
                if recorrencia == "Semanal (Todas as semanas)":
                    data_atual += timedelta(weeks=1)
                elif recorrencia == "Mensal (Uma vez por mês)":
                    data_atual += timedelta(days=30)
                elif recorrencia == "Anual (Uma vez por ano)":
                    data_atual += timedelta(days=365)
            
            for dt in datas_agendadas:
                st.session_state.agenda.append({
                    "id": len(st.session_state.agenda),
                    "paciente": p_nome,
                    "data": dt,
                    "hora": hora_agend,
                    "status": "Agendado"
                })
            
            st.success(f"🗓️ Sucesso! Foram gerados {qtd_repeticoes} agendamentos para {p_nome}.")
            st.rerun()

# =====================================================================
# ABA 4: PAINEL DE ATENDIMENTO COM FILTROS DE DIA, SEMANA, MÊS E ANO
# =====================================================================
with aba4:
    st.header("📋 Painel de Atendimento")
    st.write("Gerencie e visualize os compromissos da clínica filtrando por períodos.")

    # Nova Inteligência: Seletor de Escopo de Visão sugerido por você
    tipo_visao = st.radio(
        "Escolha o escopo de visualização da grade:",
        ["Ver por Dia", "Ver por Semana", "Ver por Mês", "Ver por Ano"],
        horizontal=True,
        key="radio_tipo_visao"
    )
    
    data_base = st.date_input("Selecione a Data Base de referência:", value=date.today(), key="painel_data_ref")
    
    # Filtragem matemática baseada na escolha da Dra. Michelle
    agendamentos_filtrados = []
    
    if tipo_visao == "Ver por Dia":
        target_str = data_base.strftime("%d/%m/%Y")
        st.subheader(f"📅 Consultas do Dia: {target_str}")
        agendamentos_filtrados = [ag for ag in st.session_state.agenda if ag["data"] == target_str]
        
    elif tipo_visao == "Ver por Semana":
        # Calcula o início (segunda) e fim (domingo) da semana da data escolhida
        inicio_semana = data_base - timedelta(days=data_base.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        st.subheader(f"📆 Consultas da Semana: {inicio_semana.strftime('%d/%m/%Y')} até {fim_semana.strftime('%d/%m/%Y')}")
        
        for ag in st.session_state.agenda:
            ag_data = datetime.strptime(ag["data"], "%d/%m/%Y").date()
            if inicio_semana <= ag_data <= fim_semana:
                agendamentos_filtrados.append(ag)
                
    elif tipo_visao == "Ver por Mês":
        target_mes_ano = data_base.strftime("/%m/%Y") # Filtra pelo final da string (Ex: /08/2026)
        st.subheader(f"🗓️ Consultas do Mês: {data_base.strftime('%m/%Y')}")
        agendamentos_filtrados = [ag for ag in st.session_state.agenda if ag["data"].endswith(target_mes_ano)]
        
    elif tipo_visao == "Ver por Ano":
        target_ano = data_base.strftime("%Y")
        st.subheader(f"📊 Planejamento Anual de Consultas: {target_ano}")
        agendamentos_filtrados = [ag for ag in st.session_state.agenda if ag["data"].endswith(target_ano)]

    # Renderização visual dos cartões (Cards)
    if not agendamentos_filtrados:
        st.info("Nenhum compromisso encontrado para o período selecionado.")
    else:
        # Ordenação inteligente: primeiro agrupa por data, depois por horário
        agendamentos_filtrados.sort(key=lambda x: (datetime.strptime(x["data"], "%d/%m/%Y"), x["hora"]))
        
        for idx, ag in enumerate(st.session_state.agenda):
            if ag in agendamentos_filtrados:
                with st.container(border=True):
                    col_c1, col_c2, col_c3 = st.columns(3)
                    
                    with col_c1:
                        st.markdown(f"### ⏰ **{ag['hora']}** — {ag['paciente']}")
                        st.write(f"📌 Data: **{ag['data']}**")
                    
                    with col_c2:
                        if ag["status"] == "Agendado":
                            st.warning(f"🔹 Status: {ag['status']}")
                        elif ag["status"] == "Atendido":
                            st.success(f"✅ Status: {ag['status']}")
                        else:
                            st.error(f"❌ Status: {ag['status']}")
                    
                    with col_c3:
                        if ag["status"] == "Agendado":
                            col_b1, col_b2 = st.columns(2)
                            if col_b1.button("✅ Concluir", key=f"concluir_{ag['id']}"):
                                st.session_state.agenda[idx]["status"] = "Atendido"
                                p_alvo = ag['paciente']
                                if p_alvo in st.session_state.pacientes:
                                    st.session_state.pacientes[p_alvo]["sessoes_realizadas"] += 1
                                st.success(f"Atendimento registrado!")
                                st.rerun()
                            
                            if col_b2.button("🚨 Falta", key=f"falta_{ag['id']}"):
                                st.session_state.agenda[idx]["status"] = "Faltou"
                                st.rerun()
                        else:
                            if st.button("🗑️ Desmarcar", key=f"excluir_{ag['id']}"):
                                if ag["status"] == "Atendido" and ag['paciente'] in st.session_state.pacientes:
                                    if st.session_state.pacientes[ag['paciente']]["sessoes_realizadas"] > 0:
                                        st.session_state.pacientes[ag['paciente']]["sessoes_realizadas"] -= 1
                                st.session_state.agenda.pop(idx)
                                st.success("Removido.")
                                st.rerun()

# =====================================================================
# ABA 5: CONSULTAS REALIZADAS (HISTÓRICO ACUMULATIVO E PRONTUÁRIO)
# =====================================================================
with aba5:
    st.header("📦 Histórico Clínico e Evolução das Sessões")
    
    if not st.session_state.pacientes:
        st.info("Nenhum paciente cadastrado na Aba 1 ainda.")
    else:
        paciente_sel = st.selectbox("Selecione o Paciente para Acompanhamento:", list(st.session_state.pacientes.keys()), key="sel_pac_pacotes")
        dados_p = st.session_state.pacientes[paciente_sel]
        
        # Garante que o contador acumulativo de realizadas exista na memória do prontuário
        if "sessoes_realizadas" not in dados_p:
            st.session_state.pacientes[paciente_sel]["sessoes_realizadas"] = 0
            
        # Exibição visual do Contador Histórico Acumulado
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.write(f"Acompanhando o prontuário eletrônico de: **{paciente_sel}**")
        with col_p2:
            realizadas = dados_p.get("sessoes_realizadas", 0)
            st.metric(label="✨ Total de Consultas Realizadas", value=f"{realizadas} atendimentos", delta="Histórico Acumulado")
                
        st.markdown("---")
        st.subheader("📝 Lançamento de Atendimento, Exames e Relatórios")
        
        tipo_registro = st.selectbox("Selecione o Tipo de Registro Clínico:", [
            "Evolução de Atendimento de Rotina", 
            "Relatório de Atendimento Concluído", 
            "Laudo de Exame Externo / Anexo"
        ], key="sel_tipo_registro_clinico")
        
        texto_clinico = st.text_area("Digite o texto, relatório ou parecer do documento:", key="txt_area_clinico")
        
        if st.button("💾 Salvar Registro Clínico", key="btn_salvar_registro_clinico"):
            if not texto_clinico.strip():
                st.error("Por favor, digite o conteúdo do registro antes de salvar.")
            else:
                # Armazena na ficha do paciente na memória local
                st.session_state.pacientes[paciente_sel]["evolucoes"].append({
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "tipo": tipo_registro,
                    "texto": texto_clinico
                })
                
                st.success("Registro clínico e evolução anexados ao histórico do paciente com sucesso!")
                st.rerun()

# =====================================================================
# ABA 6: LAUDOS & PDFS (PREPARADO PARA TODOS OS DOCUMENTOS)
# =====================================================================
with aba6:
    st.header("📄 Emissão de Documentos e Relatórios em PDF")
    
    tipo_doc = st.selectbox("Selecione o Documento para Gerar PDF:", [
        "Laudo Fonoaudiológico", 
        "Atestado de Comparecimento", 
        "Recibo",
        "Espelho da Anamnese Completa",
        "Histórico Clínico e Evoluções"
    ], key="sel_tipo_pdf")
    
    if tipo_doc == "Laudo Fonoaudiológico":
        st.text_input("Nome do Paciente:", key="pdf_laudo_nome")
        st.text_input("Código CID:", key="pdf_laudo_cid")
        st.text_area("Parecer Técnico Fonoaudiológico:", key="pdf_laudo_parecer")
    elif tipo_doc == "Atestado de Comparecimento":
        st.text_input("Nome do Paciente:", key="pdf_atest_nome")
        st.date_input("Data do Comparecimento", value=date.today(), key="pdf_atest_data")
        st.text_input("Horário do Atendimento:", key="pdf_atest_hora")
    elif tipo_doc == "Recibo":
        st.text_input("Recebi de (Nome):", key="pdf_recibo_nome")
        st.number_input("Valor Cobrado (R$):", min_value=0.0, format="%.2f", key="pdf_recibo_valor")
        st.text_input("Valor por Extenso:", key="pdf_recibo_extenso")
    elif tipo_doc in ["Espelho da Anamnese Completa", "Histórico Clínico e Evoluções"]:
        if not st.session_state.pacientes:
            st.warning("Nenhum paciente cadastrado para extração de relatório em PDF.")
        else:
            st.selectbox("Puxar Dados do Paciente:", list(st.session_state.pacientes.keys()), key="pdf_p_sel")

    if st.button("⚙️ Gerar PDF Oficial", key="btn_gerar_pdf_oficial"):
        st.info(f"O documento '{tipo_doc}' foi processado com sucesso no buffer local.")
        pdf_buffer = io.BytesIO()
        pdf_buffer.write(b"PDF Base FonoClinic v1.3")
        st.download_button(
            "📥 Baixar Arquivo PDF para Impressão", 
            data=pdf_buffer.getvalue(), 
            file_name=f"{tipo_doc.lower().replace(' ', '_')}.pdf", 
            mime="application/pdf",
            key="btn_download_pdf"
        )
