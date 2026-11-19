"""data.py - fixed lists that never change while the app runs.

Shared file: each member edits ONLY their own marked section.
"""

## ---------- [OWNER: Kong Fu Sheng] journal moods ----------
MOODS = [                                                     # mood 1 to 5
    {'value': 1, 'label': 'Rough', 'emoji': '😞', 'colour': '#E5484D'},
    {'value': 2, 'label': 'Meh',   'emoji': '😕', 'colour': '#F28C28'},
    {'value': 3, 'label': 'Okay',  'emoji': '🙂', 'colour': '#F5C542'},
    {'value': 4, 'label': 'Good',  'emoji': '😄', 'colour': '#7BC86C'},
    {'value': 5, 'label': 'Great', 'emoji': '🤩', 'colour': '#00C389'},
]
MOOD_BY_VALUE = {mood['value']: mood for mood in MOODS}      # 3 → the 'Okay' dict

# ---------- [OWNER: Tan Yu Zhe] MMU subjects ----------
# (code, name, lecturer, weight, colour). The Mini IT Project counts a bit more.
MMU_SUBJECTS = [
    ('CSP1123', 'Mini IT Project', 'Supervisor', 1.5, '#00FF9C'),
    ('CDS1114', 'Digital System', 'Lecturer', 1.0, '#4DA3FF'),
    ('CMT1134', 'Mathematics III', 'Lecturer', 1.0, '#FFB020'),
    ('CPP1113', 'Physics', 'Lecturer', 1.0, '#FF6B4A'),
    ('LAE1113', 'Academic English', 'Lecturer', 1.0, '#FF7EB6'),
    ('LCT1113', 'Critical Thinking', 'Lecturer', 1.0, '#B38BFF'),
    ('LCE1113', 'Communicative English', 'Lecturer', 1.0, '#F472B6'),
    ('GNB1114', 'Introduction to Business Management', 'Lecturer', 1.0, '#9BE15D'),
    ('CSP1114', 'Problem Solving and Program Design', 'Lecturer', 1.0, '#22D3EE'),
    ('CMT1114', 'Mathematics I', 'Lecturer', 1.0, '#FACC15'),
    ('CCT1114', 'Introduction to Computing Technology', 'Lecturer', 1.0, '#60A5FA'),
    ('CMF1114', 'Multimedia Fundamentals', 'Lecturer', 1.0, '#FB923C'),
    ('CMT1124', 'Mathematics II', 'Lecturer', 1.0, '#FDE047'),
    ('LEE1113', 'Essential English', 'Lecturer', 1.0, '#F9A8D4'),
]

DEFAULT_SUBJECTS = MMU_SUBJECTS     # every new account starts with all 14
