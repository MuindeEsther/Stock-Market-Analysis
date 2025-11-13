import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def plot_price_chart(data, ticker_name):
    # Plot candlestick chart with moving avergaes and Bollinger Band
    if data is None or data.empty:
        logger.warning(f"No data available to plot for {ticker_name}")
        return go.Figure()
    fig = go.Figure()
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=f'{ticker_name}Price'
    ))
    
    # Moving Averages
    if 'MA_20' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['MA_20'],
            mode='lines',
            name='MA_20',
            line=dict(color='orange', width=1)
        ))
        
    if 'MA_50' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['MA_50'],
            mode='lines',
            name='MA_50',
            line=dict(color='blue', width=1)
        ))
        
    if 'MA_200' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['MA_200'],
            mode='lines',
            name='MA_200',
            line=dict(color='green', width=1)
        ))
        
    # Bollinger Bands
    if 'BB_Upper' in data.columns and 'BB_Lower' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['BB_Upper'],
            mode='lines',
            name='Bollinger Upper',
            line=dict(color='lightgrey', width=1),
            fill=None
        ))
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['BB_Lower'],
            mode='lines',
            name='Bollinger Lower',
            line=dict(color='lightgrey', width=1),
            fill='tonexty', fillcolor='rgba(211,211,211,0.2'
        ))
        
    fig.update_layout(
        title=f'{ticker_name} - Price with Technical Indicators',
        xaxis_title='Date',
        yaxis_title='Price (USD / KES)',
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_volume_chart(data, ticker_name):
    # Plot volume chart
    if data is None or data.empty:
        logger.warning(f"No data available to plot for {ticker_name}")
        return go.Figure()
    fig = px.bar(
        data,
        x=data.index,
        y='Volume',
        title=f'{ticker_name} - Daily Trading Volume',
        labels={'Volume': 'Volume', 'Date': 'Date'},
        template='plotly_white'
    )
    fig.update_layout(
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_cumulative_returns(data_dict):
    # Plot cumulative returns comparison between multiple tickers
    fig = go.Figure()
    
    for name, df in data_dict.items():
        if 'Cumulative_Return' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['Cumulative_Return'],
                mode='lines',
                name=name
            ))
    
    fig.update_layout(
        title="Cumulative Returns Comparison (Kenya vs Global)",
        yaxis_title='Cumulative Return (%)',
        xaxis_title='Date',
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_correlation_heatmap(corr_matrix):
    # Plot correlation heatmap
    if corr_matrix is None or corr_matrix.empty:
        logger.warning("No correlation data available to plot")
        return go.Figure()
    fig = px.imshow(
        corr_matrix,
        text_auto=".2f",
        color_continuous_scale='RdBu',
        title='Correlation Heatmap of Selected Tickers',
        labels={'color': 'Correlation Coefficient'},
        zmin=-1,
        zmax=1
    )
    fig.update_layout(
        template='plotly_white',
        hovermode='closest'
    )
    return fig

        