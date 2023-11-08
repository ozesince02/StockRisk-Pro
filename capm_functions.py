import plotly.express as px
import numpy as np


def interactive_plot(df):
    fig = px.line()
    for i in df.columns[1:]:
        fig.add_scatter(x=df['Date'], y=df[i], name=i)
    fig.update_layout(width=450,
                      margin=dict(l=20, r=20, t=20, b=20),
                      legend=dict(orientation='h', yanchor='bottom',
                                  y=1.02, xanchor='right', x=1))
    return fig


def histogram(rnt_df):
    fig = px.histogram(rnt_df,
                       x='Stock',
                       y=rnt_df.iloc[:,1],
                       color='Stock',
                       text_auto=True,
                       color_discrete_sequence=px.colors.qualitative.Dark24)
    fig.update_layout(
        yaxis_title_text='Calculated Return',
    )
    return fig


def normalize(df_2):
    df = df_2.copy()
    for i in df.columns[1:]:
        df[i] = df[i]/df[i][0]
    return df


def daily_return(df):
    df_daily_return = df.copy()
    for i in df.columns[1:]:
        for j in range(1, len(df)):
            df_daily_return[i][j]=((df[i][j]-df[i][j-1])/df[i][j-1])*100
        df_daily_return[i][0] = 0
    return df_daily_return


def calculate_beta(stocks_daily_return, stock, index_name):
    rm = stocks_daily_return[index_name].mean()*252

    b, a = np.polyfit(stocks_daily_return[index_name], stocks_daily_return[stock], 1)
    return b, a
