"""
Builds ovelser_v2.xlsx = original ovelser.xlsx + new progressive workouts.
Run: py data/build_workouts.py
"""
import pandas as pd
import os

BASE = os.path.dirname(__file__)
EXCEL_IN  = os.path.join(BASE, "ovelser.xlsx")
EXCEL_OUT = os.path.join(BASE, "ovelser_v2.xlsx")

df = pd.read_excel(EXCEL_IN)

# ── helper ────────────────────────────────────────────────────────────────────
def rows(name, wtype, focus, groups):
    """
    groups = list of (group_label, sets, exercises)
    exercises = list of (name, duration, rest)
    """
    out = []
    for g, sets, exs in groups:
        for ex, dur, rest in exs:
            out.append({
                "Group": g,
                "Exercise": ex,
                "Duration": dur,
                "Rest": rest,
                "Sets": sets,
                "Type": focus,
                "Name": name,
                "Workout_type": wtype,
            })
    return out

def calc_duration(row_list):
    """Calculate total seconds from a list of row dicts."""
    total = 0
    for r in row_list:
        total += (r["Duration"] + r["Rest"]) * r["Sets"]
    return total

# ─────────────────────────────────────────────────────────────────────────────
# WARMUP / COOLDOWN BLOCKS
# ─────────────────────────────────────────────────────────────────────────────
# Short warmup ~2 min
WU_S_FULL = [("Wrist warm-up", 20, 3), ("Dynamic side bends", 20, 3),
             ("Standig hip rotations", 20, 3), ("Hip Flexor Strech", 20, 3)]
WU_S_CORE = [("Elbow rotations", 20, 3), ("Dynamic side bends", 20, 3),
             ("Roll down", 20, 3), ("Chest openers with rotation", 20, 3)]
WU_S_BUTT = [("Side bends", 20, 3), ("Side to side rotations", 20, 3),
             ("Hip rotations (left)", 20, 3), ("Hip rotations (right)", 20, 3),
             ("Hip Openers (left)", 20, 3), ("Hip Openers (right)", 20, 3)]

# Medium warmup ~3 min
WU_M_FULL = [("Wrist warm-up", 30, 5), ("Chest openers with rotation", 30, 5),
             ("Dynamic side bends", 30, 5), ("Standig hip rotations", 30, 5),
             ("Hip Flexor Strech", 30, 5)]
WU_M_BUTT = [("Side bends", 20, 3), ("Side to side rotations", 20, 3),
             ("Hip rotations (left)", 30, 3), ("Hip rotations (right)", 30, 3),
             ("Deep side to side lunge", 30, 3), ("Hip Openers (left)", 30, 3)]
WU_M_UPPER = [("Elbow rotations", 30, 5), ("Wrist warm-up", 30, 5),
              ("Dynamic side bends", 30, 5), ("Standig hip rotations", 30, 5),
              ("Deep side to side lunge", 30, 5)]

# Cooldowns
CD_S = [("Knees to chest strech", 30, 5), ("Cat to Cow Strech", 30, 5),
        ("Childs pose", 30, 5)]   # ~2.25 min
CD_S_BUTT = [("Figure 4 Strech  (right)", 30, 3), ("Figure 4 Strech  (left)", 30, 3),
             ("Crossed-legged chest to floor", 30, 3)]   # ~1.5 min
CD_M = [("Seated hamstring strech", 30, 5), ("Knees to chest strech", 30, 5),
        ("Cat to Cow Strech", 30, 5), ("Childs pose", 30, 5)]  # ~3 min
CD_M_BUTT = [("Seated hamstring strech", 30, 5),
             ("Figure 4 strech (left) rumpe", 30, 5),
             ("Figure 4 strech (right) rumpe", 30, 5),
             ("Pigeon pose (right) - toye rumpe", 30, 5),
             ("Pigeon pose (left) - toye rumpe", 30, 5)]  # ~3.75 min

# ═════════════════════════════════════════════════════════════════════════════
# FASE 1  (uke 1-4): 15-22 min
# Each block target: ~15-22 min = 900-1320 s
# ═════════════════════════════════════════════════════════════════════════════

new_rows = []

# ── 1. Mini Full Body Start, 16 min ──────────────────────────────────────────
# WU 4×(20+3)×1=92s, B 3×(30+7)×3=333s, C 2×(30+7)×3=222s, CD 3×(30+5)×1=105s = 752s ≈ 12.5 min
# Legg til mer: B 3 sett 35s, C 3 sett
new_rows += rows("Mini Full Body Start, 16 min", "Calisthenics", "Full Body", [
    ("A", 1, WU_S_FULL),                                        # 92 s
    ("B", 3, [("Push-ups", 30, 7), ("Prisoner squat", 30, 7),  # 3×(30+7)×3=333 s
              ("Mountain Climber", 30, 7)]),
    ("C", 3, [("Superman", 30, 7), ("Flutter kicks", 30, 7),   # 3×(30+7)×3=333 s
              ("Scissor Kicks", 30, 7)]),
    ("E", 1, CD_S),                                             # 105 s
    # Total ≈ 863 s ≈ 14.4 min → legg til en D-blokk
    ("D", 2, [("Burpee", 30, 10), ("Side lunges (left)", 30, 7),
              ("Side lunges (right)", 30, 7)]),                 # 3×(30+8)×2=228 s
    # 863+228 = 1091 s ≈ 18 min — litt for mye. Bruk 2 sett i B og C:
])
# Reset og bygg riktig:
new_rows = new_rows[:-len(rows("Mini Full Body Start, 16 min", "Calisthenics", "Full Body", [
    ("A", 1, WU_S_FULL), ("B", 3, [("Push-ups", 30, 7), ("Prisoner squat", 30, 7), ("Mountain Climber", 30, 7)]),
    ("C", 3, [("Superman", 30, 7), ("Flutter kicks", 30, 7), ("Scissor Kicks", 30, 7)]),
    ("E", 1, CD_S), ("D", 2, [("Burpee", 30, 10), ("Side lunges (left)", 30, 7), ("Side lunges (right)", 30, 7)]),
]))]

# Bygg alle øktene rent fra starten
new_rows = []

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FASE 1 — 15-22 min  (900-1320 s)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 1. Mini Full Body Start, 16 min  target ~960 s
# WU_S_FULL(92) + B 2sett×3øv×37(30+7)=222 + C 2sett×3øv×37=222 + D 2sett×2øv×37=148 + CD_S(105) = 789 → øk til 3 sett B
# WU(92) + B3×3×37=333 + C2×3×37=222 + CD(105) = 752  → legg til D
# WU(92)+B3×3×37=333+C2×3×37=222+D2×2×40(30+10)=160+CD(105)=912 ≈ 15.2 min ✓
new_rows += rows("Mini Full Body Start, 16 min", "Calisthenics", "Full Body", [
    ("A", 1, WU_S_FULL),
    ("B", 3, [("Push-ups", 30, 7), ("Prisoner squat", 30, 7), ("Mountain Climber", 30, 7)]),
    ("C", 2, [("Superman", 30, 7), ("Flutter kicks", 30, 7), ("Scissor Kicks", 30, 7)]),
    ("D", 2, [("Glute Bridges", 30, 10), ("Side lunges (left)", 30, 10), ("Side lunges (right)", 30, 10)]),
    ("E", 1, CD_S),
])
# 92 + 333 + 222 + 240 + 105 = 992 s ≈ 16.5 min ✓

# 2. Core Starter, 15 min  target ~900 s
# WU_S_CORE(92) + B3×3×35=315 + C2×3×35=210 + CD_S_no butt(105) = 722 → neste eksakt
# WU(92)+B3×3×(30+5)=315+C3×3×35=315+CD(105)=827 → bytt CD til M
# WU(92)+B3×3×35=315+C3×3×35=315+CD_M(210)=932 ≈ 15.5 min ✓
new_rows += rows("Core Starter, 15 min", "Calisthenics", "Core", [
    ("A", 1, WU_S_CORE),
    ("B", 3, [("Push ups", 30, 5), ("Mountain Climber", 30, 5), ("Scissor Kicks", 30, 5)]),
    ("C", 3, [("Commando plank", 30, 5), ("Flutter kicks", 30, 5), ("Heel taps", 30, 5)]),
    ("E", 1, CD_M),
])
# 92 + 315 + 315 + 210 = 932 s ≈ 15.5 min ✓

# 3. Butt Beginner, 17 min  target ~1020 s
# WU_S_BUTT(138)+B2×3×35=210+C2×4×35=280+D2×3×35=210+CD_S_BUTT(99)=937 → litt lite
# WU(138)+B3×3×35=315+C2×4×35=280+D2×3×35=210+CD_S_BUTT(99)=1042 ≈ 17.4 min ✓
new_rows += rows("Butt Beginner, 17 min", "Calisthenics", "Butt", [
    ("A", 1, WU_S_BUTT),
    ("B", 3, [("Glute Bridges", 30, 5), ("Donkey kicks (Right)", 30, 5), ("Donkey kicks (Left)", 30, 5)]),
    ("C", 2, [("Prone Leg raise (Right)", 30, 5), ("Prone Leg raise (Left)", 30, 5),
              ("Clamshell (Right)", 30, 5), ("Clamshell (Left)", 30, 5)]),
    ("D", 2, [("Fire Hydrant (Right)", 30, 5), ("Fire Hydrant (Left)", 30, 5),
              ("Wall sit", 30, 5)]),
    ("E", 1, CD_S_BUTT),
])
# 138 + 315 + 280 + 210 + 99 = 1042 s ≈ 17.4 min ✓

# 4. Upper Body Light, 17 min  target ~1020 s
# WU 5øv×(20+3)×1=115 + B2×3×35=210 + C2×3×35=210 + D1×6×35(mixed)=~210 + CD_S(105)= 850 → øk sett
# B3×3×35=315 + C2×3×35=210 + D(105)+CD(105) = 115+315+210+105+105=850 → legg til E
# Prøv: WU(115)+B3×3×35=315+C3×3×35=315+CD(105+99)=949 ✓
new_rows += rows("Upper Body Light, 17 min", "Calisthenics", "Chest, back", [
    ("A", 1, [("Side bends", 20, 3), ("Elbow rotations", 20, 3), ("Rotation Toe Touches", 20, 3),
              ("Walkouts", 20, 3), ("Hip openers", 20, 3)]),
    ("B", 3, [("Push-ups", 30, 5), ("Walkouts to forearm plank", 30, 5), ("Prone Leg Raise", 30, 5)]),
    ("C", 3, [("Backrise ", 30, 5), ("Mountain climbers", 30, 5), ("Robot arms", 30, 5)]),
    ("D", 1, [("Overhead lat strech (right)", 20, 5), ("Overhead lat strech (left)", 20, 5),
              ("Open Book (right)", 20, 5), ("Open Book (left)", 20, 5), ("Childs pose", 30, 5)]),
    ("E", 1, CD_S),
])
# 115+315+315+175+105 = 1025 s ≈ 17.1 min ✓

# 5. Legs & Butt Easy, 18 min  target ~1080 s
# WU_S_BUTT(138)+B2×3×35=210+C2×4×35=280+D2×3×35=210+CD_S_BUTT(99)=937
# Øk B til 3 sett: 138+315+280+210+99=1042 ≈ 17.4 ✓
new_rows += rows("Legs & Butt Easy, 18 min", "Calisthenics", "Butt, legs", [
    ("A", 1, WU_S_BUTT),
    ("B", 3, [("Prisoner squat", 30, 5), ("Half Squat walk", 30, 5), ("Glute Bridges", 30, 5)]),
    ("C", 2, [("Donkey kicks (Right)", 30, 5), ("Donkey kicks (Left)", 30, 5),
              ("Fire Hydrant (Right)", 30, 5), ("Fire Hydrant (Left)", 30, 5)]),
    ("D", 2, [("Side lunges (left)", 30, 5), ("Side lunges (right)", 30, 5),
              ("Glute bridges with abduction", 30, 5)]),
    ("E", 1, CD_S_BUTT + [("Knees to chest strech", 30, 5)]),
])
# 138+315+280+210+(99+35)=1077 ≈ 18 min ✓

# 6. Core & Back Easy, 18 min  target ~1080 s
# WU_S_CORE(92)+B3×3×37=333+C3×3×37=333+CD_M(210)=968 → legg 1 øv i B
# WU(92)+B3×4×37=444+C2×3×37=222+CD_M(210)=968 → legg D
# WU(92)+B3×3×37=333+C2×3×37=222+D2×2×37=148+CD_M(210)=1005 ≈ 16.7 min → øk C til 3sett
# WU(92)+B3×3×37=333+C3×3×37=333+CD_M(210)=968 ≈ 16 min → alt: 40s arbeid
# Med 40s: WU(92)+B3×3×(40+7)=423+C2×3×47=282+CD_M(210)=1007 ≈ 16.8 min
# WU(92)+B3×3×47=423+C3×3×47=423+CD(105)=1043 ≈ 17.4 min ✓
new_rows += rows("Core & Back Easy, 18 min", "Calisthenics", "Core, back", [
    ("A", 1, WU_S_CORE),
    ("B", 3, [("Wide Grip push-ups", 30, 7), ("Superman", 30, 7), ("Mountain Climber", 30, 7)]),
    ("C", 3, [("Back Bow with heel taps", 30, 7), ("Flutter kicks", 30, 7), ("Commando plank", 30, 7)]),
    ("D", 2, [("Glute bridges with abduction", 30, 7), ("Scissor Kicks", 30, 7)]),
    ("E", 1, CD_M),
])
# 92+333+333+148+210 = 1116 s ≈ 18.6 min ✓

# 7. Full Body Boost, 20 min  target ~1200 s
# WU_M_FULL(175)+B3×3×47=423+C3×3×47=423+CD_M(210)=1231 ≈ 20.5 min ✓
new_rows += rows("Full Body Boost, 20 min", "Calisthenics", "Full Body", [
    ("A", 1, WU_M_FULL),
    ("B", 3, [("Push-ups", 30, 7), ("Prisoner squat", 30, 7), ("Burpee", 30, 10)]),
    ("C", 3, [("Mountain Climber", 30, 7), ("Superman", 30, 7), ("Scissor Kicks", 30, 7)]),
    ("E", 1, CD_M),
])
# 175+423+333+210=1141 → B burpee 30+10=40, de andre 30+7=37: 3×(37+37+40)=342+3×(37+37+37)=333+175+210=1060
# La meg bare bruke 35s arbeid og 10s pause:
# 175 + 3×3×45=405 + 3×3×45=405 + 210 = 1195 ≈ 19.9 ✓

# Reset denne og legg på nytt
new_rows = new_rows[:-len(rows("Full Body Boost, 20 min", "Calisthenics", "Full Body", [
    ("A", 1, WU_M_FULL), ("B", 3, [("Push-ups", 30, 7), ("Prisoner squat", 30, 7), ("Burpee", 30, 10)]),
    ("C", 3, [("Mountain Climber", 30, 7), ("Superman", 30, 7), ("Scissor Kicks", 30, 7)]), ("E", 1, CD_M),
]))]
new_rows += rows("Full Body Boost, 20 min", "Calisthenics", "Full Body", [
    ("A", 1, WU_M_FULL),
    ("B", 3, [("Push-ups", 35, 10), ("Prisoner squat", 35, 10), ("Burpee", 35, 10)]),
    ("C", 3, [("Mountain Climber", 35, 10), ("Superman", 35, 10), ("Scissor Kicks", 35, 10)]),
    ("E", 1, CD_M),
])
# 175 + 3×3×45=405 + 3×3×45=405 + 210 = 1195 ≈ 19.9 min ✓

# 8. Butt & Thighs Intro, 21 min  target ~1260 s
# WU_M_BUTT(6øv×23×1=138+...): (20+3)×2+(20+3)×2+(30+3)×2+(30+3)×2+(30+3)×2+(30+3)×2
# = 46+46+66+66+66+66=356 → nei, det er WU_M_BUTT med sets=1 per øvelse
# WU_M_BUTT: 6 øvelser, (20+3)+(20+3)+(30+3)+(30+3)+(30+3)+(30+3)=46+46+66+66+66+66=356 s??? Nei:
# sets=1 => (20+3)*1 + (20+3)*1 + (30+3)*1 + (30+3)*1 + (30+3)*1 + (30+3)*1 = 196 s ≈ 3.3 min
# B3×3×45=405+C2×4×42=336+D2×2×45=180+CD_M_BUTT(5×35×1=175)=1292 ✓
new_rows += rows("Butt & Thighs Intro, 21 min", "Calisthenics", "Butt, legs", [
    ("A", 1, WU_M_BUTT),
    ("B", 3, [("Curtsey lunges (left)", 30, 10), ("Curtsey lunges (right)", 30, 10),
              ("Glute Bridges", 30, 10)]),
    ("C", 2, [("Donkey kicks (Right)", 30, 7), ("Donkey kicks (Left)", 30, 7),
              ("Fire Hydrant (Right)", 30, 7), ("Fire Hydrant (Left)", 30, 7)]),
    ("D", 2, [("Wall sit", 30, 10), ("Sumo squats", 30, 10)]),
    ("E", 1, CD_M_BUTT),
])
# WU:196 + B:3×3×40=360 + C:2×4×37=296 + D:2×2×40=160 + CD:5×35=175 = 1187 ≈ 19.8 min ✓

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FASE 2 — ~25 min  (1400-1560 s)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 9. Full Body Circuit, 25 min  target ~1500 s
# WU_M_FULL(175)+B3×3×47=423+C3×3×47=423+D3×3×47=423+CD_M(210)=1654 → litt for mye
# WU(175)+B3×3×47=423+C3×3×47=423+D2×3×47=282+CD(210)=1513 ≈ 25.2 min ✓
new_rows += rows("Full Body Circuit, 25 min", "Calisthenics", "Full Body", [
    ("A", 1, WU_M_FULL),
    ("B", 3, [("Push-ups", 35, 7), ("Burpee", 35, 10), ("Prisoner squat", 35, 7)]),
    ("C", 3, [("Mountain Climber", 35, 7), ("Superman", 35, 7), ("Scissor Kicks", 35, 7)]),
    ("D", 2, [("Glute bridges with abduction", 35, 7), ("Back Bow with heel taps", 35, 7),
              ("Flutter kicks", 35, 7)]),
    ("E", 1, CD_M),
])
# 175+423+333+222+210=1363 → øk D til 3sett: 175+423+333+333+210=1474 ≈ 24.6 min
# Legg på litt: endre cd til CD_M + CD_S_BUTT
# 175+423+333+333+210+99=1573 ≈ 26.2 → for mye. Bruk:

new_rows = new_rows[:-len(rows("Full Body Circuit, 25 min", "Calisthenics", "Full Body", [
    ("A", 1, WU_M_FULL), ("B", 3, [("Push-ups", 35, 7), ("Burpee", 35, 10), ("Prisoner squat", 35, 7)]),
    ("C", 3, [("Mountain Climber", 35, 7), ("Superman", 35, 7), ("Scissor Kicks", 35, 7)]),
    ("D", 2, [("Glute bridges with abduction", 35, 7), ("Back Bow with heel taps", 35, 7), ("Flutter kicks", 35, 7)]),
    ("E", 1, CD_M),
]))]
new_rows += rows("Full Body Circuit, 25 min", "Calisthenics", "Full Body", [
    ("A", 1, WU_M_FULL),
    ("B", 3, [("Push-ups", 35, 7), ("Burpee", 35, 10), ("Prisoner squat", 35, 7)]),
    ("C", 3, [("Mountain Climber", 35, 7), ("Superman", 35, 7), ("Scissor Kicks", 35, 7)]),
    ("D", 3, [("Glute bridges with abduction", 35, 7), ("Flutter kicks", 35, 7)]),
    ("E", 1, CD_M),
])
# 175 + 3×3×(35+avg7_10) → exakt:
# B: 3×((35+7)+(35+10)+(35+7))=3×(42+45+42)=387
# C: 3×((35+7)+(35+7)+(35+7))=3×42×3=378
# D: 3×((35+7)+(35+7))=3×84=252
# E: 4×35=140 (CD_M = 4 items × (30+5))
# Faktisk CD_M: 4×(30+5)=4×35=140
# Total: 175+387+378+252+140=1332 ≈ 22.2 → for lite
# Eksisterende "Full Body Blast, 24 mins" → 24 min. La meg bruke 40s:
new_rows = new_rows[:-len(rows("Full Body Circuit, 25 min", "Calisthenics", "Full Body", [
    ("A", 1, WU_M_FULL), ("B", 3, [("Push-ups", 35, 7), ("Burpee", 35, 10), ("Prisoner squat", 35, 7)]),
    ("C", 3, [("Mountain Climber", 35, 7), ("Superman", 35, 7), ("Scissor Kicks", 35, 7)]),
    ("D", 3, [("Glute bridges with abduction", 35, 7), ("Flutter kicks", 35, 7)]),
    ("E", 1, CD_M),
]))]
new_rows += rows("Full Body Circuit, 25 min", "Calisthenics", "Full Body", [
    ("A", 1, WU_M_FULL),
    ("B", 3, [("Push-ups", 40, 8), ("Burpee", 40, 10), ("Prisoner squat", 40, 8)]),
    ("C", 3, [("Mountain Climber", 40, 8), ("Superman", 40, 8), ("Scissor Kicks", 40, 8)]),
    ("D", 3, [("Glute bridges with abduction", 40, 8), ("Back Bow with heel taps", 40, 8),
              ("Flutter kicks", 40, 8)]),
    ("E", 1, CD_M),
])
# B: 3×(48+50+48)=438, C: 3×(48×3)=432, D: 3×(48×3)=432, WU:175, CD:140
# Total: 175+438+432+432+140=1617 ≈ 26.9 min → litt for mye
# Sett D til 2 sett: 175+438+432+288+140=1473 ≈ 24.6 min ✓ (innen 25)
new_rows = new_rows[:-len(rows("Full Body Circuit, 25 min", "Calisthenics", "Full Body", [
    ("A", 1, WU_M_FULL), ("B", 3, [("Push-ups", 40, 8), ("Burpee", 40, 10), ("Prisoner squat", 40, 8)]),
    ("C", 3, [("Mountain Climber", 40, 8), ("Superman", 40, 8), ("Scissor Kicks", 40, 8)]),
    ("D", 3, [("Glute bridges with abduction", 40, 8), ("Back Bow with heel taps", 40, 8), ("Flutter kicks", 40, 8)]),
    ("E", 1, CD_M),
]))]
new_rows += rows("Full Body Circuit, 25 min", "Calisthenics", "Full Body", [
    ("A", 1, WU_M_FULL),
    ("B", 3, [("Push-ups", 40, 8), ("Burpee", 40, 10), ("Prisoner squat", 40, 8)]),
    ("C", 3, [("Mountain Climber", 40, 8), ("Superman", 40, 8), ("Scissor Kicks", 40, 8)]),
    ("D", 2, [("Glute bridges with abduction", 40, 8), ("Back Bow with heel taps", 40, 8),
              ("Flutter kicks", 40, 8)]),
    ("E", 1, CD_M),
])
# 175+438+432+288+140=1473 ≈ 24.6 ✓

# 10. Glute Power, 25 min  target ~1500 s
# WU_M_BUTT(196)+B3×3×(35+7)=378+C3×4×(35+7)=504+D2×3×(35+7)=252+CD_M_BUTT(5×35=175)=1505 ≈ 25 ✓
new_rows += rows("Glute Power, 25 min", "Calisthenics", "Butt", [
    ("A", 1, WU_M_BUTT),
    ("B", 3, [("Glute bridges with abduction", 35, 7), ("Donkey kicks (Right)", 35, 7),
              ("Donkey kicks (Left)", 35, 7)]),
    ("C", 3, [("Clamshell (Right)", 35, 7), ("Clamshell (Left)", 35, 7),
              ("Fire Hydrant (Right)", 35, 7), ("Fire Hydrant (Left)", 35, 7)]),
    ("D", 2, [("Slick Floor Bridges Curls", 35, 7), ("Single Leg Glute Bridge (Right)", 35, 7),
              ("Single Leg Glute Bridge (Left)", 35, 7)]),
    ("E", 1, CD_M_BUTT),
])
# 196 + 3×3×42=378 + 3×4×42=504 + 2×3×42=252 + 175=1505 ≈ 25 min ✓

# 11. Core Strength, 25 min  target ~1500 s
# WU_S_CORE(92)+B3×3×(40+5)=405+C3×3×45=405+D2×3×45=270+CD_M(140)=1312 → legg mer
# WU_M(175)+B3×3×45=405+C3×3×45=405+CD_M(140)=1125 → trenger D+E
# WU_M(175)+B3×3×45=405+C3×3×45=405+D3×3×45=405+CD_S(105)=1495 ≈ 24.9 ✓
new_rows += rows("Core Strength, 25 min", "Calisthenics", "Core", [
    ("A", 1, WU_M_FULL),
    ("B", 3, [("Push ups", 40, 5), ("Mountain Climber", 40, 5), ("Scissor Kicks", 40, 5)]),
    ("C", 3, [("Spider + Cross Plank", 40, 5), ("Flutter kicks", 40, 5), ("Commando plank", 40, 5)]),
    ("D", 3, [("Heel taps", 40, 5), ("V Sit Bicycles", 40, 5), ("Wave Push-ups", 40, 5)]),
    ("E", 1, CD_S),
])
# 175+405+405+405+105=1495 ≈ 24.9 min ✓

# 12. Chest & Back Builder, 25 min  target ~1500 s
# WU(115)+B3×3×42=378+C3×3×42=378+D3×3×42=378+E_CD(175)=1424 → ok
new_rows += rows("Chest & Back Builder, 25 min", "Calisthenics", "Chest, back", [
    ("A", 1, [("Side bends", 20, 3), ("Elbow rotations", 20, 3), ("Rotation Toe Touches", 20, 3),
              ("Walkouts", 20, 3), ("Hip openers", 20, 3)]),
    ("B", 3, [("Walkouts to Push-ups", 35, 7), ("Mountain Climber - to push-ups", 35, 7),
              ("High Plank Walk out (ikke opp)", 35, 7)]),
    ("C", 3, [("Push-ups", 35, 7), ("Superman rows", 35, 7), ("Prone Leg Raise", 35, 7)]),
    ("D", 3, [("Backrise ", 35, 7), ("Plank Jack Shoulder taps", 35, 7), ("Robot arms", 35, 7)]),
    ("E", 1, [("Overhead lat strech (right)", 30, 5), ("Overhead lat strech (left)", 30, 5),
              ("Seated lower back strech (left)", 30, 5), ("Seated lower back strech (right)", 30, 5),
              ("Childs pose", 30, 5)]),
])
# 115+378+378+378+175=1424 ≈ 23.7 min ✓

# 13. Lower Body & Glutes, 25 min  target ~1500 s
# WU_M_BUTT(196)+B3×3×(35+10)=405+C3×4×(35+7)=504+D 0+CD_M_BUTT(175)=1280 → legg D
# +D2×3×(35+10)=270 → 1550 ≈ 25.8 ✓
new_rows += rows("Lower Body & Glutes, 25 min", "Calisthenics", "Butt, legs", [
    ("A", 1, WU_M_BUTT),
    ("B", 3, [("Curtsey lunges (left)", 35, 10), ("Curtsey lunges (right)", 35, 10),
              ("Squat jumps", 35, 10)]),
    ("C", 3, [("Side Step Squat", 35, 7), ("Glute bridges (hold)", 35, 7),
              ("Fire Hydrant (Right)", 35, 7), ("Fire Hydrant (Left)", 35, 7)]),
    ("D", 2, [("Backward Lunges (left)", 35, 10), ("Backward Lunges (Right", 35, 10),
              ("Sumo squats", 35, 10)]),
    ("E", 1, CD_M_BUTT),
])
# 196 + 3×3×45=405 + 3×4×42=504 + 2×3×45=270 + 175=1550 ≈ 25.8 ✓

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FASE 3 — 25-30 min  (1500-1800 s)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 14. Full Body Burn, 28 min  target ~1680 s
# WU_M_FULL(175)+B3×3×(40+7)=423+C3×3×47=423+D3×3×47=423+CD_M(140)=1584 → legg mer
# +D 3sett × (40+10)=450: WU+B+C+D+CD = 175+423+423+450+140=1611 ≈ 26.9 min
# Legg extra stretch: +CD_S_BUTT(99): 1710 ≈ 28.5 ✓
new_rows += rows("Full Body Burn, 28 min", "Calisthenics", "Full Body", [
    ("A", 1, WU_M_FULL),
    ("B", 3, [("Push-ups", 40, 7), ("Burpee", 40, 10), ("Prisoner squat", 40, 7)]),
    ("C", 3, [("Modified Diagonal mountain climbers", 40, 7), ("Narrow push-ups", 40, 7),
              ("Scissor Kicks", 40, 7)]),
    ("D", 3, [("Glute bridges with abduction", 40, 10), ("Back Bow with heel taps", 40, 7),
              ("Superman", 40, 7)]),
    ("E", 1, CD_M),
    ("F", 1, CD_S_BUTT),
])
# 175+423+423+450+140+99=1710 ≈ 28.5 min ✓

# 15. Glute & Core Power, 28 min  target ~1680 s
# WU_M_BUTT(196)+B3×3×47=423+C3×4×47=564+D3×3×47=423+CD_M_BUTT(175)=1781 → litt for mye
# Sett D til 2sett: 196+423+564+282+175=1640 ≈ 27.3 ✓
new_rows += rows("Glute & Core Power, 28 min", "Calisthenics", "Butt", [
    ("A", 1, WU_M_BUTT),
    ("B", 3, [("Glute bridges with abduction", 40, 7), ("Single Leg Glute Bridge (Right)", 40, 7),
              ("Single Leg Glute Bridge (Left)", 40, 7)]),
    ("C", 3, [("Donkey kicks (Right)", 40, 7), ("Donkey kicks (Left)", 40, 7),
              ("Clamshell (Right)", 40, 7), ("Clamshell (Left)", 40, 7)]),
    ("D", 2, [("Sumo squats", 40, 10), ("Curtsey lunges (left)", 40, 10),
              ("Curtsey lunges (right)", 40, 10)]),
    ("E", 1, CD_M_BUTT + [("Spinal Twist (left)", 30, 5), ("Spinal Twist (right)", 30, 5)]),
])
# 196+423+564+282+(175+70)=1710 ≈ 28.5 ✓

# 16. Core & Upper Advanced, 28 min  target ~1680 s
# WU_M_UPPER(175)+B3×3×47=423+C3×3×47=423+D3×3×47=423+CD_M(140)=1584 → legg D4 blokk
# +E 1×3×47=141: 175+423+423+423+141+140=1725 ≈ 28.8 ✓
new_rows += rows("Core & Upper Advanced, 28 min", "Calisthenics", "Arms, core", [
    ("A", 1, WU_M_UPPER),
    ("B", 3, [("Hindu push-ups", 40, 7), ("Flutter kicks", 40, 7), ("Commando plank", 40, 7)]),
    ("C", 3, [("Pseudo push-ups", 40, 7), ("Modified Diagonal mountain climbers", 40, 7),
              ("High Plank Walk out", 40, 7)]),
    ("D", 3, [("Heel taps", 40, 7), ("Spider + Cross Plank", 40, 7), ("Diamond push-ups", 40, 7)]),
    ("E", 1, [("L-Crunch (left)", 40, 7), ("L-Crunch (Right)", 40, 7), ("V Sit Bicycles", 40, 7)]),
    ("F", 1, CD_M),
])
# 175+423+423+423+141+140=1725 ≈ 28.8 ✓

# 17. Legs of Steel, 30 min  target ~1800 s
# WU 5øv×35×1=175+B3×3×55=495+C3×3×50=450+D3×3×50=450+CD5×35=175=1745 ≈ 29 ✓
new_rows += rows("Legs of Steel, 30 min", "Calisthenics", "Butt, legs", [
    ("A", 1, [("Elbow rotations", 30, 5), ("Hip Flexor Strech", 30, 5),
              ("Standing hip rotations (left)", 30, 5), ("Standing hip rotations (right)", 30, 5),
              ("Deep side to side lunge", 30, 5)]),
    ("B", 3, [("Burpee", 40, 15), ("Squat jumps", 40, 10), ("Glute bridges (hold)", 40, 10)]),
    ("C", 3, [("Backward Lunges (left)", 40, 10), ("Backward Lunges (Right", 40, 10),
              ("Sumo squats", 40, 10)]),
    ("D", 3, [("Glute bridges with abduction", 40, 10), ("Fire Hydrant (Right)", 40, 7),
              ("Fire Hydrant (Left)", 40, 7)]),
    ("E", 1, [("Seated hamstring strech", 30, 5), ("Plank to downward dog", 30, 5),
              ("Figure 4 strech (left) rumpe", 30, 5), ("Figure 4 strech (right) rumpe", 30, 5),
              ("Cat to Cow Strech", 30, 5)]),
])
# 175+3×(55+50+50)=465+3×(50+50+50)=450+3×(50+47+47)=432+175=1697 ≈ 28.3
# Eksakt: B=3×(55+50+50)=465, C=3×3×50=450, D=3×(50+47+47)=432, WU=175, CD=175
# =1697 ≈ 28.3 ✓ (innen 25-30)

# 18. Total Body Finisher, 30 min  target ~1800 s
# WU_M_FULL(175)+B3×3×45=405+C3×4×47=564+D3×3×45=405+CD_M_FULL+butt(140+99)=239=1788 ≈ 29.8 ✓
new_rows += rows("Total Body Finisher, 30 min", "Calisthenics", "Full Body", [
    ("A", 1, WU_M_FULL),
    ("B", 3, [("Superman", 40, 5), ("Push-ups", 40, 5), ("Squat to walkout", 40, 5)]),
    ("C", 3, [("Pivot lunge (left)", 40, 5), ("Pivot lunge (right)", 40, 5),
              ("Wood chops (left)", 40, 5), ("Wood Chops (right)", 40, 7)]),
    ("D", 3, [("Mountain Climber", 40, 5), ("Seated knee tucks", 40, 5),
              ("Burpee walk (jumps)", 40, 10)]),
    ("E", 1, [("Knees to chest strech", 30, 5), ("Overhead lat strech ", 30, 5),
              ("Plank to downward dog", 30, 5), ("Cobra", 30, 5), ("Childs pose", 30, 5)]),
])
# 175+405+3×(45+45+45+47)=546+3×(45+45+50)=420+175=1721 ≈ 28.7 ✓

# ─────────────────────────────────────────────────────────────────────────────
# Append and save
# ─────────────────────────────────────────────────────────────────────────────
new_df = pd.DataFrame(new_rows,
                      columns=["Group", "Exercise", "Duration", "Rest", "Sets",
                                "Type", "Name", "Workout_type"])
combined = pd.concat([df, new_df], ignore_index=True)
combined.to_excel(EXCEL_OUT, index=False)

# Verify durations
print("=== New workout durations ===")
for name in new_df["Name"].unique():
    sub = new_df[new_df["Name"] == name]
    total = 0
    for _, row in sub.iterrows():
        s = int(row["Sets"]) if not pd.isna(row["Sets"]) else 1
        d = row["Duration"] if not pd.isna(row["Duration"]) else 0
        r = row["Rest"] if not pd.isna(row["Rest"]) else 0
        total += (d + r) * s
    print(f"  {total//60:.0f} min  {name}")

print(f"\nTotal rows in Excel: {len(combined)}")
print("Done — saved to ovelser_v2.xlsx")
