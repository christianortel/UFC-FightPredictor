"""
UFC Fight Predictor - Data Processor & Prediction Engine
Loads fighter data, engineers features, and predicts fight outcomes.
"""
import pandas as pd
import numpy as np
from src.db_manager import get_connection

def load_fighters():
    """Load fighter data from SQLite database."""
    conn = get_connection()
    
    query = """
    SELECT 
        f.name as Name,
        f.nickname as Nickname,
        f.height_cm as Height_cm,
        f.reach_cm as Reach_cm,
        f.stance as Stance,
        f.dob as DOB,
        f.weight_lbs as Weight_lbs,
        f.url as URL,
        s.wins as Wins,
        s.losses as Losses,
        s.draws as Draws,
        s.sapm as SApM,
        s.slpm as SLpM,
        s.str_acc as Str_Acc,
        s.str_def as Str_Def,
        s.td_avg as TD_Avg,
        s.td_acc as TD_Acc,
        s.td_def as TD_Def,
        s.sub_avg as Sub_Avg
    FROM fighters f
    JOIN fighter_stats s ON f.id = s.fighter_id
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Error loading from DB: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def clean_fighters(df):
    """Clean and prepare fighter data for analysis."""
    # Keep only fighters with enough data (at least 1 fight)
    df = df.copy()
    df = df[df['Wins'].notna() & df['Losses'].notna()]
    df['TotalFights'] = df['Wins'] + df['Losses'] + df['Draws'].fillna(0)
    df = df[df['TotalFights'] >= 1]
    
    # Fill missing numerical values with median
    numeric_cols = ['Height_cm', 'Reach_cm', 'SLpM', 'Str_Acc', 'SApM', 
                    'Str_Def', 'TD_Avg', 'TD_Acc', 'TD_Def', 'Sub_Avg']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    
    # Fill missing stance with 'Orthodox' (most common)
    df['Stance'] = df['Stance'].fillna('Orthodox')
    
    # Calculate win rate
    df['WinRate'] = df['Wins'] / df['TotalFights']
    
    # Calculate finish rate (proxy: wins by KO/Sub tend to correlate with higher SLpM and Sub_Avg)
    # We don't have exact finish data from roster page, but we can approximate
    df['FinishPotential'] = (df['SLpM'] * 0.5) + (df['Sub_Avg'] * 0.5)
    
    # Assign weight class based on Weight_lbs
    def assign_weight_class(weight):
        if pd.isna(weight):
            return 'Unknown'
        weight = int(weight)
        if weight <= 115:
            return 'Strawweight'
        elif weight <= 125:
            return 'Flyweight'
        elif weight <= 135:
            return 'Bantamweight'
        elif weight <= 145:
            return 'Featherweight'
        elif weight <= 155:
            return 'Lightweight'
        elif weight <= 170:
            return 'Welterweight'
        elif weight <= 185:
            return 'Middleweight'
        elif weight <= 205:
            return 'Light Heavyweight'
        else:
            return 'Heavyweight'
    
    df['WeightClass'] = df['Weight_lbs'].apply(assign_weight_class)
    
    return df

def predict_matchup(fighter_a_row, fighter_b_row):
    """
    Predict the outcome of a fight between Fighter A and Fighter B.
    
    Uses a weighted scoring system based on statistical advantages:
    - Striking Differential (40%)
    - Grappling Differential (30%)  
    - Physical Advantage (15%)
    - Experience & Win Rate (15%)
    
    Returns: dict with probabilities and breakdown
    """
    
    scores = {}
    breakdown = {}
    
    # --- 1. STRIKING (40% weight) ---
    # Higher SLpM = more offense, Lower SApM = better defense
    # Higher Str_Acc = more efficient, Higher Str_Def = harder to hit
    a_strike_offense = (fighter_a_row.get('SLpM', 0) or 0)
    b_strike_offense = (fighter_b_row.get('SLpM', 0) or 0)
    a_strike_defense = (fighter_a_row.get('Str_Def', 0.5) or 0.5)
    b_strike_defense = (fighter_b_row.get('Str_Def', 0.5) or 0.5)
    a_strike_acc = (fighter_a_row.get('Str_Acc', 0.5) or 0.5)
    b_strike_acc = (fighter_b_row.get('Str_Acc', 0.5) or 0.5)
    a_sapm = (fighter_a_row.get('SApM', 3.0) or 3.0)
    b_sapm = (fighter_b_row.get('SApM', 3.0) or 3.0)
    
    # Net striking: how much damage you deal vs absorb
    a_net_striking = (a_strike_offense * a_strike_acc) - (a_sapm * (1 - a_strike_defense))
    b_net_striking = (b_strike_offense * b_strike_acc) - (b_sapm * (1 - b_strike_defense))
    
    strike_diff = a_net_striking - b_net_striking
    breakdown['Striking'] = {
        'Fighter_A': round(a_net_striking, 2),
        'Fighter_B': round(b_net_striking, 2),
        'Advantage': 'A' if strike_diff > 0 else ('B' if strike_diff < 0 else 'Even')
    }
    
    # --- 2. GRAPPLING (30% weight) ---
    a_td = (fighter_a_row.get('TD_Avg', 0) or 0)
    b_td = (fighter_b_row.get('TD_Avg', 0) or 0)
    a_td_acc = (fighter_a_row.get('TD_Acc', 0) or 0)
    b_td_acc = (fighter_b_row.get('TD_Acc', 0) or 0)
    a_td_def = (fighter_a_row.get('TD_Def', 0.5) or 0.5)
    b_td_def = (fighter_b_row.get('TD_Def', 0.5) or 0.5)
    a_sub = (fighter_a_row.get('Sub_Avg', 0) or 0)
    b_sub = (fighter_b_row.get('Sub_Avg', 0) or 0)
    
    # Grappling score: ability to take down * accuracy + submission threat - opponent's TD defense effectiveness
    a_grapple = (a_td * a_td_acc) + (a_sub * 0.5) - (b_td * b_td_acc * (1 - a_td_def))
    b_grapple = (b_td * b_td_acc) + (b_sub * 0.5) - (a_td * a_td_acc * (1 - b_td_def))
    
    grapple_diff = a_grapple - b_grapple
    breakdown['Grappling'] = {
        'Fighter_A': round(a_grapple, 2),
        'Fighter_B': round(b_grapple, 2),
        'Advantage': 'A' if grapple_diff > 0 else ('B' if grapple_diff < 0 else 'Even')
    }
    
    # --- 3. PHYSICAL (15% weight) ---
    a_reach = (fighter_a_row.get('Reach_cm', 180) or 180)
    b_reach = (fighter_b_row.get('Reach_cm', 180) or 180)
    a_height = (fighter_a_row.get('Height_cm', 178) or 178)
    b_height = (fighter_b_row.get('Height_cm', 178) or 178)
    
    reach_diff = (a_reach - b_reach) / 10.0  # Normalize: 10cm = 1 point
    height_diff = (a_height - b_height) / 10.0
    physical_diff = (reach_diff * 0.7) + (height_diff * 0.3)
    
    breakdown['Physical'] = {
        'Fighter_A_Reach': a_reach,
        'Fighter_B_Reach': b_reach,
        'Reach_Diff_cm': round(a_reach - b_reach, 1),
        'Advantage': 'A' if physical_diff > 0 else ('B' if physical_diff < 0 else 'Even')
    }
    
    # --- 4. EXPERIENCE & WIN RATE (15% weight) ---
    a_winrate = (fighter_a_row.get('WinRate', 0.5) or 0.5)
    b_winrate = (fighter_b_row.get('WinRate', 0.5) or 0.5)
    a_fights = (fighter_a_row.get('TotalFights', 1) or 1)
    b_fights = (fighter_b_row.get('TotalFights', 1) or 1)
    
    # Adjustied win rate (weighted by experience - more fights = more reliable)
    exp_factor_a = min(a_fights / 15.0, 1.0)  # Cap at 15 fights
    exp_factor_b = min(b_fights / 15.0, 1.0)
    
    a_adj_winrate = a_winrate * exp_factor_a + 0.5 * (1 - exp_factor_a)
    b_adj_winrate = b_winrate * exp_factor_b + 0.5 * (1 - exp_factor_b)
    
    exp_diff = a_adj_winrate - b_adj_winrate
    breakdown['Experience'] = {
        'Fighter_A_WinRate': round(a_winrate, 3),
        'Fighter_B_WinRate': round(b_winrate, 3),
        'Fighter_A_Fights': int(a_fights),
        'Fighter_B_Fights': int(b_fights),
        'Advantage': 'A' if exp_diff > 0 else ('B' if exp_diff < 0 else 'Even')
    }
    
    # --- COMBINE SCORES ---
    # Normalize each differential to roughly [-1, 1] range
    def sigmoid(x, scale=1.0):
        return 1.0 / (1.0 + np.exp(-x * scale))
    
    striking_score = sigmoid(strike_diff, scale=0.8)  # 0.5 = even
    grappling_score = sigmoid(grapple_diff, scale=0.8)
    physical_score = sigmoid(physical_diff, scale=1.0)
    experience_score = sigmoid(exp_diff * 5, scale=1.0)
    
    # Weighted combination
    combined_score = (
        striking_score * 0.40 +
        grappling_score * 0.30 +
        physical_score * 0.15 +
        experience_score * 0.15
    )
    
    # Convert to probabilities
    prob_a = combined_score
    prob_b = 1 - combined_score
    
    return {
        'prob_a': round(prob_a, 4),
        'prob_b': round(prob_b, 4),
        'predicted_winner': fighter_a_row['Name'] if prob_a > prob_b else fighter_b_row['Name'],
        'confidence': round(abs(prob_a - 0.5) * 200, 1),  # 0-100% confidence
        'breakdown': breakdown
    }

if __name__ == "__main__":
    df = load_fighters()
    df = clean_fighters(df)
    print(f"Loaded {len(df)} fighters.")
    print(f"\nWeight Classes:\n{df['WeightClass'].value_counts()}")
    print(f"\nSample fighters:")
    print(df[['Name', 'Wins', 'Losses', 'WeightClass', 'SLpM', 'TD_Avg', 'WinRate']].head(10))
