# libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import re
import streamlit as st
import datetime
import folium
from streamlit_folium import folium_static
import numpy as np

from PIL import Image # aqui importamos a biblioteca para colocar imagens no streamlit


st.set_page_config(page_title='Visão Restaurante', layout='wide')

# ---------------------------------------
# Funções
# ---------------------------------------
def time_for_deliver(df1):
                
    cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time' ]
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                      color='std_time', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time']))

    return fig

def time_for_city(df1):
                
    cols = ['City', 'Time_taken(min)']
    df_aux = df1.loc[:, cols].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time' ]
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))

    fig.update_layout(barmode='group')

    return fig

def time_mean_city(df1):
            
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
        
    # Use a notação de colchetes para acessar as colunas corretamente
    df1['distance'] = df1[cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                         (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

    avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()

    fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])

    return fig

def avg_st_time_delivery(df1, festival, op):
    """ 
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
            Imput:
                - df: dataframe com os dados necessários para o cálculo
                - op: tipo de operação que precisa ser calculado
                    'avg_time': calcula o tempo médio
                    'std_time': calcula o desvio padrão do tempo
            Output:
                - df: dataframe com 2 colunas e 1 linha.
    """
    #Tempo de entrga medio c/ festival
    cols = ['Time_taken(min)', 'Festival']
    df_aux = df1.loc[:, cols].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    
    df_aux = round(df_aux.loc[df_aux['Festival'] == festival, op], 2)
    
    return df_aux

def distance(df1):
    # Distancia Media
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    
    # Use a notação de colchetes para acessar as colunas corretamente
    df1['distance'] = df1[cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                         (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
    
    avg_distance = round(df1['distance'].mean(), 2)
    
    return avg_distance

def clean_code(df):
    """ Esta função tem a responsabilibsade de limpar o dataframe
    
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo de coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica)

        Imput: dataframe
        Output: dataframe
    """
    # Remover spaco da string
    df['ID'] = df['ID'].str.strip()
    df['Delivery_person_ID'] = df['Delivery_person_ID'].str.strip()
    
    # Excluir as linhas com a idade dos entregadores vazia
    # ( Conceitos de seleção condicional )
    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['Road_traffic_density'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['City'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['Festival'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    # Conversao de texto/categoria/string para numeros inteiros
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )
    
    # Conversao de texto/categoria/strings para numeros decimais
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )
    
    # Conversao de texto para data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )
    
    # Remove as linhas da culuna multiple_deliveries que tenham o
    # conteudo igual a 'NaN '
    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )
    
    # Comando para remover o texto de números
    df = df.reset_index( drop=True )
    
    # Retirando os numeros da coluna Time_taken(min)
    df['Time_taken(min)'] = df['Time_taken(min)'].str.extract(r'(\d+)').fillna('0').astype(int)
    
    # Retirando os espaços da coluna Festival
    df['Festival'] = df['Festival'].str.strip()

    return df
# -------------------------------- 
# Inicio da Estrutura 
# -------------------------------

# ---------------------------------------
# Lendo e copiando DataFrame
# ---------------------------------------

df_raw = pd. read_csv('dataset/train.csv')
df = df_raw.copy()

# --------------------------------------
# Limpando o dataframe
# --------------------------------------
df = clean_code(df)

# -------------------------------------
# Copia do df
# -------------------------------------

df1 = df.copy()

# -------------------------------------
# Barra Lateral
# -------------------------------------

st.header( "Market Place - Visão Restaurantes")

st.sidebar.markdown('# Cury Comapny')
st.sidebar.markdown('## Fastest delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime.datetime(2022, 4, 13),
    min_value=datetime.datetime(2022, 2, 11), #mudou o datetime, agora é necessário importar o datetime
    max_value=datetime.datetime(2022, 4, 6),
    format='DD-MM-YYYY')
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de Transito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown("""---""")

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Transito
#linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
#df1 = df1.loc[linhas_selecionadas, :]

# ----------------------------------------
# Layout no Streamlit
# ----------------------------------------

tab1, tab2, tab3 = st.tabs(['Visão geral', '', ''])

with tab1:

    with st.container():
        
    

        col1, col2, col3, col4, col5, col6 =  st.columns(6)

        with col1:
            # entregadores Unicos
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', delivery_unique)

        with col2:
            avg_distance = distance(df1)
            col2.metric('A distância média das entregas', avg_distance)
            

        with col3:
            df_aux = avg_st_time_delivery(df1, 'Yes', 'avg_time')
            col3.metric('Tempo médio de entrega', df_aux)
 

        with col4:
            df_aux = avg_st_time_delivery(df1, 'Yes', 'std_time')
            col4.metric('Tempo médio de entrega', df_aux)

        with col5:
            df_aux = avg_st_time_delivery(df1, 'No', 'avg_time')
            col5.metric('Tempo médio de entrega', df_aux)
            

        with col6:
            df_aux = avg_st_time_delivery(df1, 'No', 'std_time')
            col6.metric('Desvio Padrão', df_aux)
            


    with st.container():
        st.markdown("""___""")
        fig = time_mean_city(df1)
        st.title('Tempo Médio por Cidade (Pizza)')
        st.plotly_chart(fig)
        


    with st.container():
        st.markdown("""___""")
        col1, col2 = st.columns(2)

        with col1:
            fig = time_for_city(df1)
            st.title('Distribuição do tempo por cidade')
            st.plotly_chart(fig)
            
                
                
        with col2:
            fig = time_for_deliver(df1)
            st.title('Tempo Médio por tipo de entrega')
            st.plotly_chart(fig)
            
    
                


        with st.container():
            st.markdown("""___""")
            st.title('Tempo Médio por Cidade e tipo de tráfego')
            cols = ['City', 'Time_taken(min)', 'Type_of_order']
            df_aux = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time' ]
            df_aux = df_aux.reset_index()

            st.dataframe(df_aux)

        
    




















