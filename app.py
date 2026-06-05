
import streamlit as st
import pandas as pd
from supabase import create_client, client

#Configuração da Página
st.set_page_config(page_title="Mansão App")
st.title("Mansão das Figurinhas")

#Conecta supabase
url = "https://pbgqppburbsifxikmgjy.supabase.co"
key = "sb_publishable_3wX2yAg-4iPKxnujUa_TYA_fqk0SdCN"
supabase: client = create_client(url, key)

#Popula df com dados do supabase
get = supabase.table('Figurinhas').select("*").execute()
df = pd.DataFrame(get.data)

if not df.empty:
    distinct_grupos = df['Grupo'].unique()

    #Sanfona1
    for grupo in distinct_grupos:
        with st.expander(f'📅 Grupo {grupo}'):
            selecoes_grupo = df[df['Grupo'] == grupo]['Selecao'].unique()

            for selecao in selecoes_grupo:
                with st.expander(f'👕 {selecao}'):
                    figurinhas_selecao = df[(df['Grupo'] == grupo) & (df['Selecao'] == selecao)]
                    figurinhas_selecao = figurinhas_selecao.sort_values(by='IdFigurinha')

                    colunas = st.columns(4)

                    for index, linha in figurinhas_selecao.iterrows():
                        id_fig = linha['IdFigurinha']
                        num_fig = linha['Num_Figurinha']
                        status = linha['Obtido']
                        figurinha = linha['Cod_Figurinha']

                        cor = 'primary' if status else 'secondary'
                        icone = '❌' if status else '✅'
                        
                        col_atual = (id_fig-1) % 4

                        with colunas[col_atual]:

                            clicou = st.button(
                                label=f"{figurinha}",
                                key=f"btn_{id_fig}",
                                type=cor,
                                use_container_width=True
                            )

                            if clicou:
                                novo_status = not status

                                supabase.table('Figurinhas').update({'Obtido': novo_status}).eq('IdFigurinha', id_fig).execute()

                                st.rerun()

else:
    st.info("deu ruim fml!")