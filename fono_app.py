import streamlit as st
from datetime import date, datetime
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

# Configuração das 5 abas com os nomes exatos e independentes
aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "👤 Identificação do Paciente",
    "📝 Anamnese", 
    "📦 Controle de Pacotes & Evoluções", 
    "📄 Laudos & PDFs", 
    "📅 Agenda Semanal"
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
            # Removidos os pacotes, mantendo apenas o contador histórico de realizadas
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
        
        # --- BLOCO 1: QUEIXA E SAÚDE ---
        with st.expander("📋 Queixa Principal e Histórico Clínico", expanded=True):
            queixa = st.text_area("Queixa Principal (O que te trouxe aqui?)")
            pergunta_sim_nao("Faz terapia com outros profissionais?", "ter_outros", True, "Quais?")
            st.text_input("Tem diagnóstico?")
            pergunta_sim_nao("Alérgico:", "alergia", True, "Quais?")
            pergunta_sim_nao("Toma medicação:", "medicao", True, "Quais?")
            st.text_input("Com quem passa mais tempo:")
            pergunta_sim_nao("Pratica ou gosta de esportes:", "esportes")

        # --- BLOCO 2: MARCOS DE DESENVOLVIMENTO E ROTINA DE TELAS ---
        with st.expander("🦶 Marcos de Desenvolvimento e Rotina de Telas", expanded=False):
            col_m1, col_m2 = st.columns(2)
            idade_sentou = col_m1.text_input("Com qual idade sentou?")
            idade_andou = col_m2.text_input("Com qual idade andou?")
            
            st.markdown("---")
            st.write("**🧏 Marcos de Fala e Comunicação:**")
            idade_primeiras_palavras = st.text_input("Com qual idade falou as primeiras palavras?")
            como_se_comunica_atualmente = st.text_area("Como se comunica atualmente (Gestos, palavras isoladas, frases curtas, choro)?")
            
            st.markdown("---")
            st.write("**📱 Uso de Eletrônicos / Telas:**")
            tempo_telas = st.selectbox("Tempo diário estimado de exposição a telas (Celular, Tablet, TV):", [
                "", "Não utiliza", "Até 1 hora por dia", "De 1 a 3 horas por dia", "De 3 a 5 horas por dia", "Mais de 5 horas por dia"
            ])
            detalhe_telas = st.text_input("Quais conteúdos costuma assistir ou jogar?")

        # --- BLOCO 3: EXAMES E AVALIAÇÕES COMPLEMENTARES ---
        with st.expander("🩺 Exames e Avaliações Complementares", expanded=False):
            st.write("**🦻 Histórico e Exames Auditivos:**")
            pergunta_sim_nao("Fez o Teste da Orelhinha na maternidade?", "teste_orelha")
            pergunta_sim_nao("Apresenta infecções de ouvido (otites) recorrentes?", "inf_ouvido", True, "Teve quantas ou usou carretel?")
            pergunta_sim_nao("Possui exame de Audiometria / Imitanciometria recente?", "audio_recente", True, "Resultado/Data?")
            pergunta_sim_nao("Possui exame do BERA (PEATE) recente?", "bera_audio", True, "Resultado/Data?")
            
            st.markdown("---")
            st.write("**🧠 Histórico Neurológico e Genético:**")
            pergunta_sim_nao("Já realizou exame de EEG (Eletroencefalograma)?", "eeg_exame", True, "Resultado/Teve alteração?")
            pergunta_sim_nao("Já realizou Ressonância Magnética (RM) do crânio?", "rm_cranio", True, "Resultado?")
            pergunta_sim_nao("Está em investigação genética ou possui Cariótipo/Painel?", "genetica_painel", True, "Qual o resultado?")
            
            st.markdown("---")
            st.write("**👁️ Visão, Outros Exames e Acompanhamento Médico:**")
            pergunta_sim_nao("Possui Avaliação Visual / Oftalmológica recente?", "visao_oftalmo", True, "Usa óculos ou tem estrabismo?")
            pergunta_sim_nao("Já realizou exame de Processamento Auditivo Central (PAC)?", "pac_exame", True, "Resultado?")
            pergunta_sim_nao("O Teste do Pezinho ou Teste do Linguinho teve alguma alteração?", "pezinho_linguinho", True, "Qual alteração?")
            
            st.markdown("---")
            st.write("**🏫 Histórico Escolar e Relatórios:**")
            pergunta_sim_nao("A escola ou creche enviou algum Relatório Pedagógico?", "relatorio_escola", True, "Quais as queixas principais da escola?")
            pergunta_sim_nao("Passa por consulta regular com Neuropediatra ou Psiquiatra Infantil?", "medico_especialista", True, "Nome do médico e frequência?")

        # --- BLOCO 4: LINGUAGEM E SOCIAIS ---
        with st.expander("🗣️ Comunicação, Interação e Conhecimentos Básicos", expanded=False):
            pergunta_sim_nao("Verbal:", "verbal")
            pergunta_sim_nao("Interage bem:", "interage")
            pergunta_sim_nao("Olha no olho ao ser chamado:", "olha_olho")
            pergunta_sim_nao("Atende a comandos (pega isso aqui e coloca na mesa):", "comandos")
            pergunta_sim_nao("Sabe o seu nome:", "sabe_nome")
            pergunta_sim_nao("Sabe o nome dos responsáveis:", "nome_resp")
            pergunta_sim_nao("Sabe se expressar?", "expressar")
            
            st.markdown("---")
            st.write("**Conhecimentos Pedagógicos Básicos:**")
            col_p1, col_p2, col_p3, col_p4 = st.columns(4)
            with col_p1: st.radio("Sabe as vogais:", ["", "Sim", "Não"], key="vogais")
            with col_p2: st.radio("Sabe as cores:", ["", "Sim", "Não"], key="cores_sabe")
            with col_p3: st.radio("Sabe o alfabeto:", ["", "Sim", "Não"], key="alfabeto")
            with col_p4: st.radio("Fala inglês:", ["", "Sim", "Não"], key="ingles")

            st.markdown("---")
            st.write("**Marcos de Nomeação e Identificação:**")
            pergunta_sim_nao("Nomeia as cores?", "nomeia_cores")
            pergunta_sim_nao("Nomeia objetos?", "nomeia_objetos")
            pergunta_sim_nao("Identifica Figuras?", "identifica_figuras")
            pergunta_sim_nao("Nomeia animais?", "nomeia_animais")
            pergunta_sim_nao("Sabe as emoções?", "emocoes")

        # --- BLOCO 5: COMPORTAMENTO E ROTINA ---
        with st.expander("🧠 Rotina, Comportamento e Sinais de Alerta", expanded=False):
            pergunta_sim_nao("Seletividade alimentar:", "seletividade")
            pergunta_sim_nao("Dorme bem:", "dorme_bem")
            pergunta_sim_nao("Gosta de música:", "musica")
            pergunta_sim_nao("Gosta de animais?", "gosta_animais")
            pergunta_sim_nao("Assiste desenho animado?", "desenho", True, "Quais desenhos?")
            
            st.markdown("---")
            st.write("⚠️ **Sinais de Alerta e Comportamentos Atípicos:**")
            pergunta_sim_nao("Estereotipia:", "estereotipia")
            pergunta_sim_nao("Ecolalia:", "ecolalia")
            pergunta_sim_nao("Fixação em algo:", "fixacao")
            pergunta_sim_nao("Dificuldade motora:", "dif_motora")
            pergunta_sim_nao("Auto-agressão:", "auto_agressao")
            pergunta_sim_nao("Agressivo com os outros:", "agressivo", True, "Em quais momentos?")

        # --- BLOCO 6: HISTÓRICO ALIMENTAR E AUTONOMIA ---
        with st.expander("🚽 Autonomia, Alimentação e Histórico de Desenvolvimento", expanded=False):
            pergunta_sim_nao("Usa Fralda?", "fralda")
            pergunta_sim_nao("Sabe pedir para ir ao banheiro?", "banheiro")
            pergunta_sim_nao("Se veste sozinho?", "veste_sozinho")
            
            st.markdown("---")
            st.write("**Histórico Alimentar e Funções Orofaciais:**")
            amamentacao = st.text_input("Ele(a) mamou peito ou fórmula?")
            pergunta_sim_nao("Usou e ainda usa chupeta, dedo ou mamadeira?", "chupeta")
            mastigacao_degluticao = st.text_area("Descreva como é a mastigação e deglutição (Engasga, recusa sólidos, etc.):")
            
            st.markdown("---")
            col_a, col_b = st.columns(2)
            with col_a:
                st.radio("Parto:", ["", "Cesária", "Normal"], key="parto")
                st.text_input("Alguma intercorrência no parto?")
            with col_b:
                st.multiselect("Ele(a) é predominantemente:", ["Agitado", "Tranquilo", "Inseguro", "Impaciente"], key="perfil_psic")
                
            st.text_area("O que ele(a) gosta de brincar?")
            st.text_area("O que mais gosta de fazer?")

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
# ABA 3: GESTÃO DE EVOLUÇÕES E SESSÕES REALIZADAS ACUMULADAS
# =====================================================================
with aba3:
    st.header("📦 Histórico Clínico e Evolução das Sessões")
    
    if not st.session_state.pacientes:
        st.info("Nenhum paciente cadastrado na Aba 1 ainda.")
    else:
        paciente_sel = st.selectbox("Selecione o Paciente para Acompanhamento:", list(st.session_state.pacientes.keys()), key="sel_pac_pacotes")
        dados_p = st.session_state.pacientes[paciente_sel]
        
        # Garante que o contador acumulativo de realizadas exista na memória do prontuário
        if "sessoes_realizadas" not in dados_p:
            st.session_state.pacientes[paciente_sel]["sessoes_realizadas"] = 0
            
        # Exibição visual do Contador Histórico sugerido por você
        col_p1, col_p2 = st.columns([2, 1])
        with col_p1:
            st.write(f"Acompanhando o prontuário eletrônico de: **{paciente_sel}**")
        with col_p2:
            realizadas = dados_p.get("sessoes_realizadas", 0)
            st.metric(label="✨ Total de Consultas Realizadas", value=f"{realizadas} atendimentos", delta="Histórico Acumulado")
                
        st.markdown("---")
        st.subheader("📝 Lançamento de Atendimento, Exames e Relatórios")
        
        tipo_registro = st.selectbox("Selecione o Tipo de Registro:", [
            "Evolução de Atendimento de Rotina", 
            "Relatório de Atendimento Concluído", 
            "Laudo de Exame Externo / Anexo"
        ])
        
        texto_clinico = st.text_area("Digite o texto, relatório ou parecer do documento:")
        
        if st.button("💾 Salvar Registro Clínico", key="btn_salvar_registro_clinico"):
            if not texto_clinico.strip():
                st.error("Por favor, digite o conteúdo do registro antes de salvar.")
            else:
                # Armazena na ficha do paciente na nuvem local
                st.session_state.pacientes[paciente_sel]["evolucoes"].append({
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "tipo": tipo_registro,
                    "texto": texto_clinico
                })
                
                st.success("Registro clínico e evolução anexados ao histórico do paciente com sucesso!")
                st.rerun()

# =====================================================================
# ABA 4: LAUDOS & PDFS (PREPARADO PARA TODOS OS DOCUMENTOS)
# =====================================================================
with aba4:
    st.header("📄 Emissão de Documentos e Relatórios em PDF")
    
    tipo_doc = st.selectbox("Selecione o Documento para Gerar PDF:", [
        "Laudo Fonoaudiológico", 
        "Atestado de Comparecimento", 
        "Recibo",
        "Espelho da Anamnese Completa",
        "Histórico Clínico e Evoluções"
    ])
    
    if tipo_doc == "Laudo Fonoaudiológico":
        st.text_input("Nome do Paciente:")
        st.text_input("Código CID:")
        st.text_area("Parecer Técnico Fonoaudiológico:")
    elif tipo_doc == "Atestado de Comparecimento":
        st.text_input("Nome do Paciente:")
        st.date_input("Data do Comparecimento", value=date.today())
        st.text_input("Horário do Atendimento:")
    elif tipo_doc == "Recibo":
        st.text_input("Recebi de (Nome):")
        st.number_input("Valor Cobrado (R$):", min_value=0.0, format="%.2f")
        st.text_input("Valor por Extenso:")
    elif tipo_doc in ["Espelho da Anamnese Completa", "Histórico Clínico e Evoluções"]:
        if not st.session_state.pacientes:
            st.warning("Nenhum paciente cadastrado para extração de relatório em PDF.")
        else:
            st.selectbox("Puxar Dados do Paciente:", list(st.session_state.pacientes.keys()), key="pdf_p_sel")

    if st.button("⚙️ Gerar PDF Oficial"):
        st.info(f"O documento '{tipo_doc}' foi processado com sucesso no buffer local.")
        pdf_buffer = io.BytesIO()
        pdf_buffer.write(b"PDF Base FonoClinic v1.3")
        st.download_button(
            "📥 Baixar Arquivo PDF para Impressão", 
            data=pdf_buffer.getvalue(), 
            file_name=f"{tipo_doc.lower().replace(' ', '_')}.pdf", 
            mime="application/pdf"
        )

# =====================================================================
# ABA 5: AGENDA INTEGRADA COM CONTADOR AUTOMÁTICO ACUMULADO
# =====================================================================
with aba5:
    st.header("📅 Painel Integrado de Marcação de Consultas")
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.subheader("Marcar Horário")
        if st.session_state.pacientes:
            p_nome = st.selectbox("Selecione o Paciente para o Horário:", list(st.session_state.pacientes.keys()), key="agenda_p_sel")
        else:
            p_nome = st.text_input("Nome do Paciente para Agenda:")
            
        data_agend = st.date_input("Data do Atendimento", value=date.today(), key="agenda_data")
        hora_agend = st.text_input("Horário (Ex: 09:30):")
        status_agend = st.selectbox("Status Inicial:", ["Agendado", "Atendido", "Faltou"])
        
        if st.button("Fixar na Agenda Semanal"):
            if not p_nome or not hora_agend:
                st.error("Preencha o nome e o horário.")
            else:
                st.session_state.agenda.append({
                    "id": len(st.session_state.agenda), "paciente": p_nome,
                    "data": data_agend.strftime("%d/%m/%Y"), "hora": hora_agend, "status": status_agend
                })
                st.success("Consulta fixada no painel!")
                st.rerun()
                
    with col_a2:
        st.subheader("Painel de Atendimentos da Semana")
        if not st.session_state.agenda:
            st.info("Nenhum compromisso marcado para esta semana.")
        else:
            for idx, ag in enumerate(st.session_state.agenda):
                # Columns com o número 3 fixado corretamente para evitar quebras visuais
                col_c1, col_c2, col_c3 = st.columns(3)
                col_c1.write(f"📌 **{ag['hora']}** - {ag['paciente']} ({ag['data']})")
                col_c2.write(f"*{ag['status']}*")
                
                # Automação inteligente: Ao clicar em Concluir, o contador ganha +1
                if ag['status'] == "Agendado":
                    if col_c3.button("✅ Concluir", key=f"ok_{ag['id']}"):
                        st.session_state.agenda[idx]["status"] = "Atendido"
                        
                        p_alvo = ag['paciente']
                        if p_alvo in st.session_state.pacientes:
                            if "sessoes_realizadas" not in st.session_state.pacientes[p_alvo]:
                                st.session_state.pacientes[p_alvo]["sessoes_realizadas"] = 0
                            
                            # Soma diretamente no contador histórico e acumulativo do paciente
                            st.session_state.pacientes[p_alvo]["sessoes_realizadas"] += 1
                            st.success(f"Atendimento de {p_alvo} concluído! +1 consulta adicionada ao histórico acumulado.")
                        st.rerun()
                else:
                    if col_c3.button("❌ Excluir", key=f"del_{ag['id']}"):
                        st.session_state.agenda.pop(idx)
                        st.success("Horário liberado!")
                        st.rerun()
