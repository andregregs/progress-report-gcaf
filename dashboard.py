import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Google Cloud Skills Boost Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #4285f4, #34a853);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .milestone-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .achievement-badge {
        background: #34a853;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.2rem;
    }
    .status-good { color: #34a853; }
    .status-warning { color: #fbbc04; }
    .status-error { color: #ea4335; }
</style>
""", unsafe_allow_html=True)

def calculate_arcade_points(skill_badges, game_arcade, game_trivia, special_games=0):
    """Calculate total arcade points based on the new scoring system"""
    # Base points
    skill_points = skill_badges // 2  # 1 point per 2 skill badges
    game_points = game_arcade  # 1 point per game
    trivia_points = game_trivia  # 1 point per trivia
    special_points = special_games  # Additional points for special games
    
    base_total = skill_points + game_points + trivia_points + special_points
    
    # Check milestones (only highest milestone bonus applies)
    milestone_bonus = 0
    milestone_achieved = "None"
    
    # Ultimate Milestone: 10 Arcade + 8 Trivia + 44 Skill Badges = 65 points
    if game_arcade >= 10 and game_trivia >= 8 and skill_badges >= 44:
        milestone_bonus = 25
        milestone_achieved = "Ultimate"
    # Milestone 3: 8 Arcade + 7 Trivia + 30 Skill Badges = 45 points
    elif game_arcade >= 8 and game_trivia >= 7 and skill_badges >= 30:
        milestone_bonus = 15
        milestone_achieved = "Milestone 3"
    # Milestone 2: 6 Arcade + 6 Trivia + 20 Skill Badges = 32 points
    elif game_arcade >= 6 and game_trivia >= 6 and skill_badges >= 20:
        milestone_bonus = 10
        milestone_achieved = "Milestone 2"
    # Milestone 1: 4 Arcade + 4 Trivia + 10 Skill Badges = 18 points
    elif game_arcade >= 4 and game_trivia >= 4 and skill_badges >= 10:
        milestone_bonus = 5
        milestone_achieved = "Milestone 1"
    
    total_points = base_total + milestone_bonus
    
    return {
        'base_points': base_total,
        'milestone_bonus': milestone_bonus,
        'total_points': total_points,
        'milestone_achieved': milestone_achieved,
        'breakdown': {
            'skill_points': skill_points,
            'game_points': game_points,
            'trivia_points': trivia_points,
            'special_points': special_points
        }
    }

@st.cache_data
def load_data():
    """Load and process the CSV data"""
    try:
        # Replace with actual path
        df = pd.read_csv('GCAF25-ID-WQ9-NCL.csv')
        
        # Remove sensitive columns
        sensitive_cols = ['Email Peserta', 'Nomor HP Peserta']
        df_safe = df.drop(columns=[col for col in sensitive_cols if col in df.columns])
        
        # Calculate arcade points for each participant
        arcade_data = []
        for _, row in df_safe.iterrows():
            skill_badges = row['# Jumlah Skill Badge yang Diselesaikan'] or 0
            game_arcade = row['# Jumlah Game Arcade yang Diselesaikan'] or 0
            game_trivia = row['# Jumlah Game Trivia yang Diselesaikan'] or 0
            
            points_data = calculate_arcade_points(skill_badges, game_arcade, game_trivia)
            arcade_data.append(points_data)
        
        # Add arcade points data to dataframe
        df_safe['Arcade Points'] = [data['total_points'] for data in arcade_data]
        df_safe['Milestone Achieved'] = [data['milestone_achieved'] for data in arcade_data]
        df_safe['Milestone Bonus'] = [data['milestone_bonus'] for data in arcade_data]
        
        return df_safe, arcade_data
    except FileNotFoundError:
        # Sample data for demo
        return generate_sample_data()

def generate_sample_data():
    """Generate sample data for demonstration"""
    np.random.seed(42)
    n_participants = 100
    
    data = {
        'Nama Peserta': [f'Peserta {i+1}' for i in range(n_participants)],
        'Status URL Profil': np.random.choice(['All Good', 'Issues'], n_participants, p=[0.8, 0.2]),
        'Status Redeem Kode Akses': np.random.choice(['Yes', 'No'], n_participants, p=[0.7, 0.3]),
        'Milestone yang Diselesaikan': np.random.choice(['None', 'Milestone 1', 'Milestone 2'], n_participants),
        '# Jumlah Skill Badge yang Diselesaikan': np.random.randint(0, 50, n_participants),
        '# Jumlah Game Arcade yang Diselesaikan': np.random.randint(0, 12, n_participants),
        '# Jumlah Game Trivia yang Diselesaikan': np.random.randint(0, 10, n_participants),
    }
    
    df = pd.DataFrame(data)
    
    # Calculate arcade points
    arcade_data = []
    for _, row in df.iterrows():
        skill_badges = row['# Jumlah Skill Badge yang Diselesaikan']
        game_arcade = row['# Jumlah Game Arcade yang Diselesaikan']
        game_trivia = row['# Jumlah Game Trivia yang Diselesaikan']
        
        points_data = calculate_arcade_points(skill_badges, game_arcade, game_trivia)
        arcade_data.append(points_data)
    
    df['Arcade Points'] = [data['total_points'] for data in arcade_data]
    df['Milestone Achieved'] = [data['milestone_achieved'] for data in arcade_data]
    df['Milestone Bonus'] = [data['milestone_bonus'] for data in arcade_data]
    
    return df, arcade_data

def create_overview_metrics(df):
    """Create overview metrics"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Peserta",
            value=len(df),
            delta=f"Active: {len(df[df['Arcade Points'] > 0])}"
        )
    
    with col2:
        total_badges = df['# Jumlah Skill Badge yang Diselesaikan'].sum()
        st.metric(
            label="Total Skill Badges",
            value=int(total_badges),
            delta=f"Avg: {total_badges/len(df):.1f}"
        )
    
    with col3:
        total_arcade = df['# Jumlah Game Arcade yang Diselesaikan'].sum()
        st.metric(
            label="Total Game Arcade",
            value=int(total_arcade),
            delta=f"Avg: {total_arcade/len(df):.1f}"
        )
    
    with col4:
        total_trivia = df['# Jumlah Game Trivia yang Diselesaikan'].sum()
        st.metric(
            label="Total Game Trivia",
            value=int(total_trivia),
            delta=f"Avg: {total_trivia/len(df):.1f}"
        )
    
    with col5:
        redeemed = len(df[df['Status Redeem Kode Akses'] == 'Yes'])
        st.metric(
            label="Akses Diredeeem",
            value=redeemed,
            delta=f"{redeemed/len(df)*100:.1f}%"
        )

def create_milestone_report(df):
    """Create milestone achievement report"""
    st.subheader("🏆 Laporan Milestone")
    
    # Count milestone achievements
    milestone_counts = df['Milestone Achieved'].value_counts()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Milestone summary
        st.write("**Ringkasan Pencapaian:**")
        for milestone in ['Ultimate', 'Milestone 3', 'Milestone 2', 'Milestone 1', 'None']:
            count = milestone_counts.get(milestone, 0)
            percentage = (count / len(df)) * 100
            
            if milestone == 'Ultimate':
                emoji = "👑"
                color = "gold"
            elif milestone.startswith('Milestone'):
                emoji = "🏆"
                color = "silver"
            else:
                emoji = "⭕"
                color = "gray"
                
            st.write(f"{emoji} **{milestone}**: {count} peserta ({percentage:.1f}%)")
    
    with col2:
        # Milestone distribution chart
        fig_milestone = px.pie(
            values=milestone_counts.values,
            names=milestone_counts.index,
            title="Distribusi Pencapaian Milestone",
            color_discrete_sequence=['#FFD700', '#C0C0C0', '#CD7F32', '#4285f4', '#ea4335']
        )
        fig_milestone.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_milestone, use_container_width=True)

def create_progress_charts(df):
    """Create progress visualization charts"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Simplified Skill Badge Distribution
        # Group badges into ranges for easier understanding
        def badge_category(count):
            if count == 0:
                return "0 Badges (Belum Mulai)"
            elif count <= 5:
                return "1-5 Badges (Pemula)"
            elif count <= 15:
                return "6-15 Badges (Berkembang)"
            elif count <= 30:
                return "16-30 Badges (Mahir)"
            else:
                return "30+ Badges (Expert)"
        
        df['Badge Category'] = df['# Jumlah Skill Badge yang Diselesaikan'].apply(badge_category)
        badge_counts = df['Badge Category'].value_counts()
        
        # Reorder categories
        category_order = [
            "0 Badges (Belum Mulai)",
            "1-5 Badges (Pemula)", 
            "6-15 Badges (Berkembang)",
            "16-30 Badges (Mahir)",
            "30+ Badges (Expert)"
        ]
        badge_counts = badge_counts.reindex(category_order, fill_value=0)
        
        fig_badges = px.bar(
            x=badge_counts.index, 
            y=badge_counts.values,
            title="Level Kemampuan Peserta (Berdasarkan Skill Badges)",
            labels={'x': 'Level Kemampuan', 'y': 'Jumlah Peserta'},
            color=badge_counts.values,
            color_continuous_scale='Blues'
        )
        fig_badges.update_layout(
            showlegend=False,
            xaxis_tickangle=-45,
            height=400
        )
        st.plotly_chart(fig_badges, use_container_width=True)
    
    with col2:
        # Arcade Points Distribution
        fig_points = px.histogram(
            df,
            x='Arcade Points',
            nbins=20,
            title="Distribusi Poin Arcade",
            color_discrete_sequence=['#34a853']
        )
        fig_points.add_vline(
            x=df['Arcade Points'].mean(),
            line_dash="dash",
            line_color="red",
            annotation_text=f"Rata-rata: {df['Arcade Points'].mean():.1f}"
        )
        fig_points.update_layout(height=400)
        st.plotly_chart(fig_points, use_container_width=True)

def create_leaderboard(df):
    """Create leaderboard"""
    st.subheader("🏆 Top Performers")
    
    # Sort by arcade points
    top_performers = df.nlargest(15, 'Arcade Points')
    
    # Create leaderboard table
    leaderboard_data = []
    for idx, (_, row) in enumerate(top_performers.iterrows()):
        # Medal emoji for top 3
        if idx == 0:
            rank_display = "🥇 #1"
        elif idx == 1:
            rank_display = "🥈 #2"
        elif idx == 2:
            rank_display = "🥉 #3"
        else:
            rank_display = f"#{idx + 1}"
            
        leaderboard_data.append({
            'Rank': rank_display,
            'Nama': row['Nama Peserta'],
            'Skill Badges': int(row['# Jumlah Skill Badge yang Diselesaikan']),
            'Game Arcade': int(row['# Jumlah Game Arcade yang Diselesaikan']),
            'Game Trivia': int(row['# Jumlah Game Trivia yang Diselesaikan']),
            'Milestone': row['Milestone Achieved'],
            'Poin Arcade': int(row['Arcade Points']),
            'Status': row['Status Redeem Kode Akses']
        })
    
    leaderboard_df = pd.DataFrame(leaderboard_data)
    
    # Display as table
    st.dataframe(
        leaderboard_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.TextColumn("Peringkat", width="small"),
            "Nama": st.column_config.TextColumn("Nama Peserta", width="medium"),
            "Poin Arcade": st.column_config.NumberColumn("Poin Arcade", width="small"),
            "Milestone": st.column_config.TextColumn("Milestone", width="medium")
        }
    )

def create_individual_analysis(df):
    """Create individual participant analysis"""
    st.subheader("🔍 Analisis Individual")
    
    # Search participant
    search_name = st.selectbox(
        "Pilih atau cari peserta:",
        options=[''] + sorted(df['Nama Peserta'].tolist()),
        format_func=lambda x: "Pilih peserta..." if x == '' else x
    )
    
    if search_name:
        participant = df[df['Nama Peserta'] == search_name].iloc[0]
        
        # Calculate detailed points breakdown
        skill_badges = int(participant['# Jumlah Skill Badge yang Diselesaikan'])
        game_arcade = int(participant['# Jumlah Game Arcade yang Diselesaikan'])
        game_trivia = int(participant['# Jumlah Game Trivia yang Diselesaikan'])
        
        points_data = calculate_arcade_points(skill_badges, game_arcade, game_trivia)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"""
            <div class="milestone-card">
                <h3>📊 {participant['Nama Peserta']}</h3>
                <p><strong>🎯 Total Poin Arcade:</strong> {points_data['total_points']} poin</p>
                <p><strong>🏆 Milestone:</strong> {points_data['milestone_achieved']}</p>
                <p><strong>🎁 Bonus Milestone:</strong> {points_data['milestone_bonus']} poin</p>
                <p><strong>📱 Status Redeem:</strong> {participant['Status Redeem Kode Akses']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Points breakdown
            st.write("**Breakdown Poin:**")
            st.write(f"• Skill Badges: {skill_badges} badges → {points_data['breakdown']['skill_points']} poin")
            st.write(f"• Game Arcade: {game_arcade} games → {points_data['breakdown']['game_points']} poin")
            st.write(f"• Game Trivia: {game_trivia} trivia → {points_data['breakdown']['trivia_points']} poin")
            st.write(f"• **Bonus Milestone: +{points_data['milestone_bonus']} poin**")
        
        with col2:
            # Progress toward next milestone
            st.write("**Progress ke Milestone Berikutnya:**")
            
            current_milestone = points_data['milestone_achieved']
            
            if current_milestone == "None":
                target = "Milestone 1"
                target_req = "4 Arcade + 4 Trivia + 10 Skill Badges"
                progress_arcade = min(game_arcade / 4 * 100, 100)
                progress_trivia = min(game_trivia / 4 * 100, 100)
                progress_skill = min(skill_badges / 10 * 100, 100)
            elif current_milestone == "Milestone 1":
                target = "Milestone 2"
                target_req = "6 Arcade + 6 Trivia + 20 Skill Badges"
                progress_arcade = min(game_arcade / 6 * 100, 100)
                progress_trivia = min(game_trivia / 6 * 100, 100)
                progress_skill = min(skill_badges / 20 * 100, 100)
            elif current_milestone == "Milestone 2":
                target = "Milestone 3"
                target_req = "8 Arcade + 7 Trivia + 30 Skill Badges"
                progress_arcade = min(game_arcade / 8 * 100, 100)
                progress_trivia = min(game_trivia / 7 * 100, 100)
                progress_skill = min(skill_badges / 30 * 100, 100)
            elif current_milestone == "Milestone 3":
                target = "Ultimate Milestone"
                target_req = "10 Arcade + 8 Trivia + 44 Skill Badges"
                progress_arcade = min(game_arcade / 10 * 100, 100)
                progress_trivia = min(game_trivia / 8 * 100, 100)
                progress_skill = min(skill_badges / 44 * 100, 100)
            else:
                target = "🎉 Sudah mencapai Ultimate!"
                target_req = "Selamat! Anda sudah menyelesaikan semua milestone!"
                progress_arcade = 100
                progress_trivia = 100
                progress_skill = 100
            
            st.write(f"**Target: {target}**")
            st.write(f"Requirement: {target_req}")
            
            if target != "🎉 Sudah mencapai Ultimate!":
                # Progress bars
                st.write(f"Game Arcade: {progress_arcade:.0f}%")
                st.progress(progress_arcade / 100)
                
                st.write(f"Game Trivia: {progress_trivia:.0f}%")
                st.progress(progress_trivia / 100)
                
                st.write(f"Skill Badges: {progress_skill:.0f}%")
                st.progress(progress_skill / 100)

# Main app
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Laporan Harian Peserta</h1>
        <p>Fasilitator - Andre Gregori Sangari</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df, arcade_data = load_data()
    
    # Sidebar filters
    st.sidebar.header("🎛️ Filter Data")
    
    # Status filter - handle empty selection
    status_options = df['Status Redeem Kode Akses'].unique().tolist()
    status_filter = st.sidebar.multiselect(
        "Filter Status Redeem:",
        options=status_options,
        default=status_options  # Default to all options
    )
    
    # If no status selected, show all data
    if not status_filter:
        filtered_df = df
        st.sidebar.warning("Tidak ada status yang dipilih. Menampilkan semua data.")
    else:
        filtered_df = df[df['Status Redeem Kode Akses'].isin(status_filter)]
    
    # Show filtered data info
    st.sidebar.info(f"Menampilkan {len(filtered_df)} dari {len(df)} peserta")
    
    # Main content
    create_overview_metrics(filtered_df)
    
    st.markdown("---")
    
    create_milestone_report(filtered_df)
    
    st.markdown("---")
    
    create_progress_charts(filtered_df)
    
    st.markdown("---")
    
    create_leaderboard(filtered_df)
    
    st.markdown("---")
    
    create_individual_analysis(filtered_df)
    
    # Download filtered data
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Download Data")
    
    # Prepare download data (remove sensitive info if any)
    download_df = filtered_df.drop(columns=['Email Peserta', 'Nomor HP Peserta'], errors='ignore')
    csv = download_df.to_csv(index=False)
    st.sidebar.download_button(
        label="Download Data CSV",
        data=csv,
        file_name=f"gc_skills_progress_{len(filtered_df)}_participants.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()