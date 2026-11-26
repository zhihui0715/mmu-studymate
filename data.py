"""data.py - fixed lists that never change while the app runs.

Shared file: each member edits ONLY their own marked section.
"""

# ---------- [OWNER: Kong Fu Sheng] journal moods ----------
MOODS = ['Rough', 'Meh', 'Okay', 'Good', 'Great']           # mood 1 to 5
MOOD_FACES = ['😞', '😕', '🙂', '😄', '🤩']


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

DEFAULT_SUBJECTS = MMU_SUBJECTS     # every new account starts with all 14

# W3: the only values the task form accepts
TASK_TYPES = ['Assignment', 'Quiz', 'Test', 'Exam', 'Presentation', 'Project', 'Study task']
PRIORITIES = ['Low', 'Medium', 'High', 'Critical']

# Kanban columns in order (the tasks.status values) and the names shown. Used by the board from W4.
COLUMNS = ['todo', 'prog', 'done']
COLUMN_NAMES = {'todo': 'To do', 'prog': 'In progress', 'done': 'Completed'}