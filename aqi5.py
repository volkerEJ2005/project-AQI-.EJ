import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import numpy as np
import plotly.express as px
import time
from datetime import datetime

# Load your model (replace with your actual model path)
# with open('rdforest_mode4.pk', 'rb') as f:
#     model = pickle.load(f)

# Page config
st.set_page_config(
    page_title="AQI Vision | Real-time Air Quality Dashboard",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for animations and styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

# HTML for animated background
def particle_background():
    return """
    <canvas id="particle-canvas"></canvas>
    <script>
    const canvas = document.getElementById('particle-canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const particles = [];
    const particleCount = window.innerWidth < 600 ? 30 : 100;
    
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 3 + 1;
            this.speedX = Math.random() * 1 - 0.5;
            this.speedY = Math.random() * 1 - 0.5;
            this.color = `hsl(${Math.random() * 60 + 180}, 100%, 70%)`;
        }
        
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            
            if (this.x < 0 || this.x > canvas.width) this.speedX *= -1;
            if (this.y < 0 || this.y > canvas.height) this.speedY *= -1;
        }
        
        draw() {
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
            
            // Glow effect
            ctx.shadowBlur = 10;
            ctx.shadowColor = this.color;
        }
    }
    
    function init() {
        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();
        }
        
        requestAnimationFrame(animate);
    }
    
    init();
    animate();
    
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
    </script>
    """

# AQI Gauge Component
def aqi_gauge(value):
    aqi_levels = {
        "Good": (0, 50, "#00E400"),
        "Moderate": (51, 100, "#FFFF00"),
        "Unhealthy for Sensitive Groups": (101, 150, "#FF7E00"),
        "Unhealthy": (151, 200, "#FF0000"),
        "Very Unhealthy": (201, 300, "#8F3F97"),
        "Hazardous": (301, 500, "#7E0023")
    }
    
    for level, (min_val, max_val, color) in aqi_levels.items():
        if min_val <= value <= max_val:
            current_level = level
            current_color = color
            break
    
    return f"""
    <div class="gauge-container">
        <div class="gauge">
            <div class="gauge-body" style="--rotation:{value / 500 * 180}deg; --color:{current_color};">
                <div class="gauge-fill" style="background: conic-gradient(
                    #00E400 0% 10%,
                    #FFFF00 10% 20%,
                    #FF7E00 20% 30%,
                    #FF0000 30% 40%,
                    #8F3F97 40% 60%,
                    #7E0023 60% 100%
                );"></div>
                <div class="gauge-cover">{value}</div>
            </div>
            <div class="gauge-label" style="color: {current_color}">{current_level}</div>
        </div>
    </div>
    """

# Main App
def main():
    # Inject particle background
    html(particle_background(), height=0)
    
    # Header with animated text
    st.markdown("""
    <div class="header-container">
        <h1 class="glow">AQI <span class="pulse">Vision</span></h1>
        <p class="subtitle">Real-time Air Quality Intelligence Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🌍 Live Dashboard", "📈 Historical Trends", "🔮 Predictions"])
    
    with tab1:
        # Create columns for layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Current AQI display with animation
            st.markdown("""
            <div class="current-aqi">
                <div class="aqi-pulse" style="--aqi-color: #00E400;">
                    <h2>Current AQI</h2>
                    <div class="aqi-value">72</div>
                    <div class="aqi-status">Good</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Pollutant indicators
            st.markdown("### Pollutant Levels")
            pollutants = {
                "SO₂": {"value": 2.02, "trend": "↘️", "safe": 20},
                "CO": {"value": 0.06, "trend": "→", "safe": 4},
                "NO₂": {"value": 17.84, "trend": "↗️", "safe": 40},
                "O₃": {"value": 26.07, "trend": "↘️", "safe": 50}
            }
            
            # Define units for each pollutant
            pollutant_units = {
                "SO₂": "ppb",
                "CO": "ppm",
                "NO₂": "ppb",
                "O₃": "ppb"
            }
            for name, data in pollutants.items():
                safe_percent = min(100, (data["value"] / data["safe"]) * 100)
                color = "#00E400" if safe_percent < 50 else "#FF7E00" if safe_percent < 75 else "#FF0000"
                unit = pollutant_units.get(name, "ppb")
                
                st.markdown(f"""
                <div class="pollutant-bar">
                    <div class="pollutant-info">
                        <span class="pollutant-name">{name}</span>
                        <span class="pollutant-value">{data["value"]} {unit} {data["trend"]}</span>
                    </div>
                    <div class="pollutant-meter">
                        <div class="pollutant-fill" style="width: {safe_percent}%; background: {color};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Map visualization
            st.markdown("### Air Quality Map")
            
            # Generate some sample data
            map_data = pd.DataFrame({
                'lat': [37.76 + np.random.normal(0, 0.02) for _ in range(20)],
                'lon': [-122.4 + np.random.normal(0, 0.02) for _ in range(20)],
                'aqi': np.random.randint(30, 150, 20),
                'size': np.random.randint(5, 20, 20)
            })
            
            fig = px.scatter_mapbox(map_data, lat="lat", lon="lon", size="size",
                                  color="aqi", range_color=[0, 300],
                                  color_continuous_scale=["#00E400", "#FFFF00", "#FF7E00", "#FF0000", "#8F3F97", "#7E0023"],
                                  zoom=10, height=400)
            fig.update_layout(mapbox_style="carto-darkmatter")
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig, use_container_width=True)
            
            # Real-time charts
            st.markdown("### Real-time Monitoring")
            
            # Generate time series data
            time_data = pd.DataFrame({
                'Time': pd.date_range(start="2023-01-01", periods=24, freq="H"),
                'PM2.5': np.sin(np.linspace(0, 4*np.pi, 24)) * 10 + 30,
                'NO2': np.cos(np.linspace(0, 4*np.pi, 24)) * 5 + 15,
                'O3': np.sin(np.linspace(0, 2*np.pi, 24)) * 8 + 20
            })
            
            fig2 = px.line(time_data, x="Time", y=["PM2.5", "NO2", "O3"],
                          color_discrete_sequence=["#00E400", "#FF7E00", "#0088FF"],
                          height=300)
            fig2.update_layout({
                'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                'font': {'color': 'white'}
            })
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        st.markdown("### Historical AQI Trends")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start date", datetime(2023, 1, 1))
        with col2:
            end_date = st.date_input("End date", datetime(2023, 12, 31))
        
        # Generate historical data
        date_range = pd.date_range(start=start_date, end=end_date)
        historical_data = pd.DataFrame({
            'Date': date_range,
            'AQI': np.sin(np.linspace(0, 10*np.pi, len(date_range))) * 40 + 70,
            'Temperature': np.cos(np.linspace(0, 5*np.pi, len(date_range))) * 5 + 25,
            'Humidity': np.random.normal(60, 10, len(date_range))
        })
        
        # Historical chart
        fig3 = px.line(historical_data, x="Date", y="AQI",
                      title="AQI Over Time",
                      height=400)
        fig3.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
            'font': {'color': 'white'}
        })
        fig3.update_traces(line=dict(color='#00E400', width=3))
        st.plotly_chart(fig3, use_container_width=True)
        
        # Correlation heatmap
        st.markdown("### Pollutant Correlations")
        corr_data = historical_data.copy()
        corr_data['PM2.5'] = np.random.normal(25, 5, len(date_range))
        corr_data['NO2'] = np.random.normal(15, 3, len(date_range))
        corr_matrix = corr_data[['AQI', 'PM2.5', 'NO2', 'Temperature', 'Humidity']].corr()
        
        fig4 = px.imshow(corr_matrix,
                        text_auto=True,
                        color_continuous_scale='Viridis',
                        height=400)
        fig4.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
            'font': {'color': 'white'}
        })
        st.plotly_chart(fig4, use_container_width=True)
    
    with tab3:
        st.markdown("### AQI Prediction")
        
        # Prediction form
        with st.form("prediction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                so2 = st.slider("SO₂ (ppb)", 0.0, 50.0, 2.02)
                co = st.slider("CO (ppm)", 0.0, 10.0, 0.06)
                no = st.slider("NO (ppb)", 0.0, 50.0, 8.93)
                no2 = st.slider("NO₂ (ppb)", 0.0, 50.0, 17.84)
                
            with col2:
                o3 = st.slider("O₃ (ppb)", 0.0, 100.0, 26.07)
                temp = st.slider("Temperature (°C)", -10.0, 40.0, 28.7)
                humidity = st.slider("Humidity (%)", 0.0, 100.0, 80.27)
                wind_speed = st.slider("Wind Speed (m/s)", 0.0, 20.0, 0.33)
            
            submitted = st.form_submit_button("Predict AQI")
            
            if submitted:
                # Simulate prediction (replace with actual model prediction)
                # input_data = [[so2, co, no, no2, nox, nh3, o3, ws, wd, rh, sr, tc]]
                # prediction = model.predict(input_data)[0]
                
                # For demo purposes, we'll use a simple calculation
                prediction = min(500, max(0, 
                    (so2 * 2) + (co * 10) + (no * 0.5) + (no2 * 1.5) + 
                    (o3 * 0.8) + ((30 - temp) * 0.5) + (humidity * 0.1) + 
                    (wind_speed * -2) + np.random.normal(50, 10)
                ))
                
                # Show prediction with animation
                with st.spinner('Analyzing air quality...'):
                    time.sleep(1.5)
                    
                    st.markdown(f"""
                    <div class="prediction-result">
                        <h3>Predicted AQI: <span class="pulse">{int(prediction)}</span></h3>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(aqi_gauge(int(prediction)), unsafe_allow_html=True)
    # Footer
    st.markdown("""
    <div class="footer">
        <p>Data updates every 5 minutes | Last updated: {}</p>
        <p class="glow">🌍 Protect our air quality 🌫️</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()