import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import base64
import io
from datetime import datetime, timedelta
import random

# Page config with gaming theme
st.set_page_config(
    page_title="🎮 GC Skills Arena",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with animations and gaming elements
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    .game-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        font-family: 'Orbitron', monospace;
        position: relative;
        overflow: hidden;
        animation: glow 2s ease-in-out infinite alternate;
        margin-bottom: 2rem;
    }
    
    @keyframes glow {
        from { box-shadow: 0 0 20px rgba(102, 126, 234, 0.5); }
        to { box-shadow: 0 0 40px rgba(118, 75, 162, 0.8); }
    }
    
    .xp-bar {
        background: #2d3748;
        height: 30px;
        border-radius: 15px;
        position: relative;
        overflow: hidden;
        margin: 10px 0;
    }
    
    .xp-fill {
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        height: 100%;
        border-radius: 15px;
        transition: width 1s ease;
        position: relative;
    }
    
    .level-badge {
        display: inline-block;
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: #000;
        padding: 8px 16px;
        border-radius: 25px;
        font-weight: bold;
        font-family: 'Orbitron', monospace;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    .achievement-unlock {
        background: linear-gradient(135deg, #FF6B6B, #4ECDC4);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        animation: slideIn 0.5s ease-out;
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .power-meter {
        background: linear-gradient(45deg, #833ab4, #fd1d1d, #fcb045);
        height: 8px;
        border-radius: 4px;
        margin: 5px 0;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .leaderboard-card {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        transition: transform 0.3s ease;
        border-left: 5px solid #FFD700;
    }
    
    .leaderboard-card:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .quest-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .combo-multiplier {
        color: #FF6B35;
        font-size: 1.2em;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
</style>
""", unsafe_allow_html=True)

# Game mechanics functions
def calculate_level_and_xp(points):
    """Calculate player level and XP based on arcade points"""
    if points == 0:
        return 0, 0, 100
    
    level = int(points ** 0.5) + 1
    current_level_threshold = (level - 1) ** 2
    next_level_threshold = level ** 2
    current_xp = points - current_level_threshold
    xp_for_next = next_level_threshold - current_level_threshold
    
    return level, current_xp, xp_for_next

def get_player_rank(points, all_points):
    """Get player rank and tier"""
    sorted_points = sorted(all_points, reverse=True)
    rank = sorted_points.index(points) + 1
    total_players = len(all_points)
    
    percentile = (total_players - rank + 1) / total_players * 100
    
    if percentile >= 95:
        tier = "🏆 Grandmaster"
        color = "#FFD700"
    elif percentile >= 80:
        tier = "💎 Master"
        color = "#C0C0C0"
    elif percentile >= 60:
        tier = "⚔️ Champion"
        color = "#CD7F32"
    elif percentile >= 40:
        tier = "🛡️ Warrior"
        color = "#4285F4"
    elif percentile >= 20:
        tier = "⚡ Fighter"
        color = "#34A853"
    else:
        tier = "🎯 Rookie"
        color = "#EA4335"
    
    return rank, tier, color, percentile

def calculate_combo_multiplier(skill_badges, arcade_games, trivia_games):
    """Calculate combo multiplier for balanced progress"""
    min_activity = min(skill_badges//5, arcade_games, trivia_games)
    if min_activity >= 5:
        return "🔥 MEGA COMBO! x3"
    elif min_activity >= 3:
        return "⚡ COMBO! x2"
    elif min_activity >= 1:
        return "✨ Streak x1.5"
    else:
        return "💪 Keep Going!"

def get_achievements(skill_badges, arcade_games, trivia_games, total_points):
    """Generate dynamic achievements"""
    achievements = []
    
    if skill_badges >= 10:
        achievements.append("🎓 Scholar - 10+ Skill Badges")
    if arcade_games >= 5:
        achievements.append("🎮 Gamer - 5+ Arcade Games")
    if trivia_games >= 5:
        achievements.append("🧠 Quiz Master - 5+ Trivia Games")
    if total_points >= 50:
        achievements.append("⭐ Point Hunter - 50+ Points")
    if skill_badges > 0 and arcade_games > 0 and trivia_games > 0:
        achievements.append("🎯 All-Rounder - Active in All Areas")
    
    return achievements

@st.cache_data
def generate_enhanced_sample_data():
    """Generate enhanced sample data with gaming elements"""
    np.random.seed(42)
    n_participants = 150
    
    # Generate realistic data with gaming progression
    data = []
    for i in range(n_participants):
        # Simulate different player types
        player_type = random.choice(['casual', 'hardcore', 'balanced', 'new'])
        
        if player_type == 'hardcore':
            skill_badges = np.random.randint(20, 60)
            arcade_games = np.random.randint(6, 12)
            trivia_games = np.random.randint(5, 10)
        elif player_type == 'balanced':
            skill_badges = np.random.randint(10, 30)
            arcade_games = np.random.randint(4, 8)
            trivia_games = np.random.randint(3, 7)
        elif player_type == 'casual':
            skill_badges = np.random.randint(2, 15)
            arcade_games = np.random.randint(1, 5)
            trivia_games = np.random.randint(1, 4)
        else:  # new
            skill_badges = np.random.randint(0, 5)
            arcade_games = np.random.randint(0, 2)
            trivia_games = np.random.randint(0, 2)
        
        # Calculate points using original system
        base_points = skill_badges // 2 + arcade_games + trivia_games
        
        data.append({
            'Nama Peserta': f'Player_{i+1:03d}',
            'Player Type': player_type,
            'Skill Badges': skill_badges,
            'Arcade Games': arcade_games,
            'Trivia Games': trivia_games,
            'Total Points': base_points,
            'Status': random.choice(['Active', 'Inactive'], p=[0.8, 0.2]),
            'Join Date': datetime.now() - timedelta(days=random.randint(1, 30))
        })
    
    return pd.DataFrame(data)

def create_player_profile_card(player_data, all_points):
    """Create an enhanced player profile card"""
    points = player_data['Total Points']
    level, current_xp, xp_for_next = calculate_level_and_xp(points)
    rank, tier, color, percentile = get_player_rank(points, all_points)
    
    xp_percentage = (current_xp / xp_for_next) * 100 if xp_for_next > 0 else 100
    
    combo = calculate_combo_multiplier(
        player_data['Skill Badges'], 
        player_data['Arcade Games'], 
        player_data['Trivia Games']
    )
    
    achievements = get_achievements(
        player_data['Skill Badges'],
        player_data['Arcade Games'], 
        player_data['Trivia Games'],
        points
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="quest-card">
            <h2>⚡ {player_data['Nama Peserta']}</h2>
            <div class="level-badge">Level {level}</div>
            <p><strong>🏆 Rank:</strong> #{rank} ({percentile:.1f}% percentile)</p>
            <p><strong>🎖️ Tier:</strong> <span style="color: {color};">{tier}</span></p>
            <p><strong>💯 Total Points:</strong> {points}</p>
            <p class="combo-multiplier">{combo}</p>
            
            <div class="xp-bar">
                <div class="xp-fill" style="width: {xp_percentage}%"></div>
            </div>
            <small>XP: {current_xp}/{xp_for_next} (Level {level} → {level+1})</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if achievements:
            st.markdown("**🏅 Achievements Unlocked:**")
            for achievement in achievements:
                st.markdown(f'<div class="achievement-unlock">{achievement}</div>', unsafe_allow_html=True)

def create_live_leaderboard(df, limit=10):
    """Create an animated leaderboard"""
    st.markdown("### 🏆 Live Leaderboard Arena")
    
    top_players = df.nlargest(limit, 'Total Points')
    
    for idx, (_, player) in enumerate(top_players.iterrows()):
        rank_emoji = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
        level, _, _ = calculate_level_and_xp(player['Total Points'])
        
        # Power level indicator
        power_level = min(player['Total Points'] / 100 * 100, 100)
        
        st.markdown(f"""
        <div class="leaderboard-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{rank_emoji[idx]} #{idx+1} {player['Nama Peserta']}</strong>
                    <br>
                    <small>Level {level} • {player['Total Points']} points</small>
                </div>
                <div>
                    <div class="power-meter" style="width: {power_level}px;"></div>
                    <small>Power: {power_level:.0f}%</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_skill_radar_chart(df):
    """Create a radar chart for skill distribution"""
    # Calculate averages for different skill types
    avg_skills = df['Skill Badges'].mean()
    avg_arcade = df['Arcade Games'].mean()
    avg_trivia = df['Trivia Games'].mean()
    
    # Create radar chart
    categories = ['Skill Badges', 'Arcade Games', 'Trivia Games']
    values = [avg_skills, avg_arcade, avg_trivia]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # Close the polygon
        theta=categories + [categories[0]],
        fill='toself',
        name='Community Average',
        line_color='rgba(255, 99, 132, 1)',
        fillcolor='rgba(255, 99, 132, 0.2)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values) * 1.2]
            )),
        title="🎯 Community Skill Distribution",
        showlegend=True,
        height=400
    )
    
    return fig

def create_progress_dashboard(df):
    """Create main progress dashboard"""
    # Gaming header
    st.markdown("""
    <div class="game-header">
        <h1>🎮 GOOGLE CLOUD SKILLS ARENA</h1>
        <p>⚡ Level up your cloud skills • Compete with peers • Unlock achievements ⚡</p>
        <div style="margin-top: 1rem;">
            <span class="level-badge">🌟 Active Players: {}</span>
            <span class="level-badge">⚡ Total XP Generated: {}</span>
        </div>
    </div>
    """.format(len(df[df['Status'] == 'Active']), df['Total Points'].sum()), unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Active Players", len(df[df['Status'] == 'Active']), 
                 delta=f"+{len(df[df['Status'] == 'Active']) - len(df[df['Status'] == 'Inactive'])}")
    
    with col2:
        avg_level = np.mean([calculate_level_and_xp(p)[0] for p in df['Total Points']])
        st.metric("📊 Avg Level", f"{avg_level:.1f}", delta="↗️ Growing")
    
    with col3:
        total_achievements = sum(len(get_achievements(row['Skill Badges'], row['Arcade Games'], 
                                                   row['Trivia Games'], row['Total Points'])) 
                               for _, row in df.iterrows())
        st.metric("🏅 Total Achievements", total_achievements, delta="🔥 Hot!")
    
    with col4:
        combo_players = sum(1 for _, row in df.iterrows() 
                          if "COMBO" in calculate_combo_multiplier(row['Skill Badges'], 
                                                                 row['Arcade Games'], row['Trivia Games']))
        st.metric("⚡ Combo Players", combo_players, delta="💪 Strong")

def main():
    # Load data
    if 'game_data' not in st.session_state:
        st.session_state.game_data = generate_enhanced_sample_data()
    
    df = st.session_state.game_data
    
    # Sidebar - Player Selection and Filters
    st.sidebar.markdown("### 🎮 Player Control Panel")
    
    # Player search
    selected_player = st.sidebar.selectbox(
        "🔍 Select Your Character:",
        options=[''] + sorted(df['Nama Peserta'].tolist()),
        format_func=lambda x: "Choose your player..." if x == '' else x
    )
    
    # Game mode filter
    game_modes = st.sidebar.multiselect(
        "🎯 Filter by Player Type:",
        options=df['Player Type'].unique(),
        default=df['Player Type'].unique()
    )
    
    # Apply filters
    filtered_df = df[df['Player Type'].isin(game_modes)] if game_modes else df
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Arena", type="primary"):
        st.session_state.game_data = generate_enhanced_sample_data()
        st.rerun()
    
    # Main dashboard
    create_progress_dashboard(filtered_df)
    
    # Two column layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Individual player profile
        if selected_player:
            player_data = df[df['Nama Peserta'] == selected_player].iloc[0]
            create_player_profile_card(player_data, df['Total Points'].tolist())
        
        # Interactive charts
        tab1, tab2, tab3 = st.tabs(["📊 Power Levels", "🎯 Skill Radar", "📈 Progress Trends"])
        
        with tab1:
            # Points distribution with gaming theme
            fig_points = px.histogram(
                filtered_df, x='Total Points', nbins=20,
                title="⚡ Power Level Distribution",
                color_discrete_sequence=['#667eea']
            )
            fig_points.update_layout(
                xaxis_title="Power Points",
                yaxis_title="Number of Players",
                showlegend=False
            )
            st.plotly_chart(fig_points, use_container_width=True)
        
        with tab2:
            # Radar chart
            st.plotly_chart(create_skill_radar_chart(filtered_df), use_container_width=True)
        
        with tab3:
            # Player type distribution
            fig_types = px.pie(
                filtered_df, names='Player Type',
                title="🎮 Player Type Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_types, use_container_width=True)
    
    with col2:
        # Live leaderboard
        create_live_leaderboard(filtered_df)
        
        # Quick achievements panel
        st.markdown("### 🎊 Recent Achievements")
        for _, player in filtered_df.nlargest(5, 'Total Points').iterrows():
            achievements = get_achievements(
                player['Skill Badges'], player['Arcade Games'], 
                player['Trivia Games'], player['Total Points']
            )
            if achievements:
                with st.expander(f"⭐ {player['Nama Peserta']}"):
                    for achievement in achievements[:3]:  # Show top 3
                        st.write(f"• {achievement}")
    
    # Global stats footer
    st.markdown("---")
    st.markdown("### 🌍 Global Arena Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"🏆 **Highest Score:** {df['Total Points'].max()} points")
    
    with col2:
        top_player = df.loc[df['Total Points'].idxmax(), 'Nama Peserta']
        st.success(f"👑 **Arena Champion:** {top_player}")
    
    with col3:
        st.warning(f"⚡ **Average Power:** {df['Total Points'].mean():.1f} points")

if __name__ == "__main__":
    main()