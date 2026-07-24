import streamlit as st

import ai_client
import db
import exporter
import extractors
import theme

st.set_page_config(page_title="Resumidor de Conteúdo IA", layout="wide")

theme.apply_theme()
db.init_db()

# --------------------------------------------------------------------------
# Sidebar: gerenciamento de pastas / assuntos
# --------------------------------------------------------------------------
theme.theme_toggle_button()
st.sidebar.title("Pastas / Assuntos")

folders = db.list_folders()
folder_names = {f["id"]: f["name"] for f in folders}

with st.sidebar.expander("Nova pasta"):
    new_folder_name = st.text_input("Nome da nova pasta", key="new_folder_name")
    if st.button("Criar pasta", key="create_folder_btn"):
        if new_folder_name.strip():
            try:
                db.create_folder(new_folder_name.strip())
                st.success(f"Pasta '{new_folder_name}' criada.")
                st.rerun()
            except Exception as exc:
                st.error(f"Erro ao criar pasta: {exc}")
        else:
            st.warning("Informe um nome válido.")

selected_folder_id = None
if folders:
    selected_folder_id = st.sidebar.selectbox(
        "Pasta ativa",
        options=[f["id"] for f in folders],
        format_func=lambda fid: folder_names.get(fid, "?"),
        key="active_folder",
    )

    with st.sidebar.expander("Renomear / Excluir pasta"):
        rename_value = st.text_input(
            "Novo nome", value=folder_names.get(selected_folder_id, ""), key="rename_folder_input"
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Renomear", key="rename_folder_btn"):
                try:
                    db.rename_folder(selected_folder_id, rename_value.strip())
                    st.success("Pasta renomeada.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Erro ao renomear: {exc}")
        with col2:
            if st.button("Excluir", key="delete_folder_btn"):
                db.delete_folder(selected_folder_id)
                st.warning("Pasta excluída (resumos associados também foram removidos).")
                st.rerun()
else:
    st.sidebar.info("Nenhuma pasta ainda. Crie uma acima.")

st.sidebar.divider()
if not ai_client.get_secret("OPENAI_API_KEY"):
    st.sidebar.text_input(
        "Chave da API (OpenAI)",
        type="password",
        key="manual_api_key",
        help="Necessária apenas se st.secrets não estiver configurado (uso local).",
    )

st.title("Resumidor de Conteúdo com IA")

tab_new, tab_library = st.tabs(["Novo Resumo", "Meus Resumos"])

# --------------------------------------------------------------------------
# Aba: Novo Resumo
# --------------------------------------------------------------------------
with tab_new:
    source_kind = st.radio("Tipo de fonte", ["Vídeo do YouTube", "Arquivo"], horizontal=True)

    source_ref = None
    default_title = ""
    uploaded_file = None
    yt_url = ""

    if source_kind == "Vídeo do YouTube":
        yt_url = st.text_input("URL do vídeo do YouTube")
        if yt_url:
            source_ref = yt_url
            default_title = yt_url
    else:
        uploaded_file = st.file_uploader(
            "Envie um documento",
            type=["pdf", "docx", "txt", "md", "xlsx", "csv"],
        )
        if uploaded_file is not None:
            source_ref = uploaded_file.name
            default_title = uploaded_file.name

    mode = st.radio("Modo de resumo", ["Automático", "Customizado"], horizontal=True)
    custom_instructions = ""
    if mode == "Customizado":
        custom_instructions = st.text_area(
            "Instruções específicas",
            placeholder="Ex: foque em dados financeiros e use linguagem simples.",
        )

    title_input = st.text_input("Título do resumo", value=default_title)
    target_folder = None
    if folders:
        target_folder = st.selectbox(
            "Salvar na pasta",
            options=[f["id"] for f in folders],
            format_func=lambda fid: folder_names.get(fid, "?"),
            key="target_folder_new",
        )

    generate = st.button("Gerar Resumo", type="primary", disabled=not source_ref)

    if generate:
        try:
            with st.spinner("Extraindo conteúdo..."):
                if source_kind == "Vídeo do YouTube":
                    content_text = extractors.extract_content("youtube", yt_url)
                    detected_source_type = "youtube"
                else:
                    content_text = extractors.extract_content("arquivo", (uploaded_file.name, uploaded_file))
                    detected_source_type = "arquivo"

            if not content_text or not content_text.strip():
                st.error("Não foi possível extrair texto desta fonte.")
            else:
                if len(content_text) > ai_client.MAX_CONTENT_CHARS:
                    st.warning(
                        "Conteúdo muito longo: apenas os primeiros "
                        f"{ai_client.MAX_CONTENT_CHARS:,} caracteres serão considerados."
                    )

                with st.spinner("Gerando resumo com IA..."):
                    summary_md = ai_client.summarize(
                        content_text,
                        mode="auto" if mode == "Automático" else "custom",
                        custom_instructions=custom_instructions,
                    )

                st.session_state["last_summary"] = {
                    "title": title_input or default_title,
                    "content_md": summary_md,
                    "source_type": detected_source_type,
                    "source_ref": source_ref,
                    "folder_id": target_folder,
                }
        except ValueError as exc:
            st.error(f"Entrada inválida: {exc}")
        except RuntimeError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Ocorreu um erro inesperado ao processar a fonte: {exc}")

    if "last_summary" in st.session_state:
        result = st.session_state["last_summary"]
        st.markdown("---")
        st.subheader(result["title"])
        st.markdown(result["content_md"])

        col_save, col_export = st.columns(2)
        with col_save:
            if st.button("Salvar na pasta selecionada", disabled=not folders):
                db.save_summary(
                    result["folder_id"],
                    result["title"],
                    result["source_type"],
                    result["source_ref"],
                    result["content_md"],
                )
                st.success("Resumo salvo com sucesso.")
                del st.session_state["last_summary"]
                st.rerun()
        with col_export:
            html_export = exporter.export_single(
                result["title"],
                f"Fonte: {result['source_type']} • {result['source_ref']}",
                result["content_md"],
            )
            st.download_button(
                "Exportar como HTML",
                data=html_export,
                file_name=f"{(result['title'] or 'resumo')[:50]}.html",
                mime="text/html",
            )

# --------------------------------------------------------------------------
# Aba: Meus Resumos
# --------------------------------------------------------------------------
with tab_library:
    filter_folder = st.selectbox(
        "Filtrar por pasta",
        options=[None] + [f["id"] for f in folders],
        format_func=lambda fid: "Todas as pastas" if fid is None else folder_names.get(fid, "?"),
        key="library_filter",
    )

    summaries = db.list_summaries(filter_folder)

    if not summaries:
        st.info("Nenhum resumo encontrado.")
    else:
        selected_ids = []
        for s in summaries:
            with st.expander(f"{s['title']} — {s['folder_name'] or 'Sem pasta'} ({s['created_at']})"):
                st.markdown(s["content_md"])
                cols = st.columns([1, 1, 2])
                with cols[0]:
                    if st.checkbox("Selecionar", key=f"select_{s['id']}"):
                        selected_ids.append(s["id"])
                with cols[1]:
                    if st.button("Excluir", key=f"delete_{s['id']}"):
                        db.delete_summary(s["id"])
                        st.rerun()
                with cols[2]:
                    single_html = exporter.export_single(
                        s["title"],
                        f"Pasta: {s['folder_name']} • Fonte: {s['source_type']} • {s['created_at']}",
                        s["content_md"],
                    )
                    st.download_button(
                        "Exportar HTML",
                        data=single_html,
                        file_name=f"{s['title'][:50]}.html",
                        mime="text/html",
                        key=f"export_{s['id']}",
                    )

        if selected_ids:
            selected_summaries = [s for s in summaries if s["id"] in selected_ids]
            batch_html = exporter.export_batch(selected_summaries)
            st.download_button(
                f"Exportar {len(selected_ids)} resumo(s) selecionado(s) (HTML)",
                data=batch_html,
                file_name="resumos_exportados.html",
                mime="text/html",
            )
