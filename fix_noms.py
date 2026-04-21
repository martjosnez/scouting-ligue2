import sqlite3

conn = sqlite3.connect('database/scouting.db')

corrections = [
    ('Teddy Bouriaud', 'Teddy Bouriaud'),
    ('Yannis Nahounnou', 'Yannis Nahounou'),
    ('Yanisis Nahounnon', 'Yannis Nahounou'),
    ('Martin Experance', 'Martin Experience'),
    ('Martin Experence', 'Martin Experience'),
    ('Zakaria Zioui', 'Zakaria Ztouti'),
    ('Zakaria Zrouti', 'Zakaria Ztouti'),
    ('V. Mathieu Patric...', 'Patrick Ouotro'),
    ('Patrick Ouotao', 'Patrick Ouotro'),
    ('Chaik El Hansar', 'Chafik El Hansar'),
    ('Cazim Suljic', 'Cazim Suljic'),
    ('Victor Orakpo', 'Victor Orakpo'),
    ('Mathieu Gueridez', 'Mathieu Guendez'),
    ('Mattheo Guendez', 'Mathieu Guendez'),
    ('Nama Sissoko', 'Pape Sissoko'),
    ('Niama Sissoko', 'Pape Sissoko'),
    ('Walid Bouabdeli', 'Walid Bouabdelli'),
    ('Walid Boualddeli', 'Walid Bouabdelli'),
    ('Brandon Bakangu', 'Brandon Bokangu'),
    ('Elyjah Mendy', 'Elyjah Mendy'),
    ('Elydjah Mendy', 'Elyjah Mendy'),
    ('Adrien Juilloux', 'Adrien Julloux'),
    ('Adrien Juloux', 'Adrien Julloux'),
    ('Faitout Maouassa', 'Faitout Maouassa'),
    ('Fallout Maouassa', 'Faitout Maouassa'),
    ('Nicolas Saint-Ruf', 'Nicolas Saint-Ruf'),
    ('Oumar Sidibe', 'Oumar Sidibe'),
]

for ancien, nouveau in corrections:
    if ancien == nouveau:
        continue
    existant = conn.execute("SELECT id FROM joueurs WHERE nom = ?", (nouveau,)).fetchone()
    if existant:
        ancien_id = conn.execute("SELECT id FROM joueurs WHERE nom = ?", (ancien,)).fetchone()
        if ancien_id:
            conn.execute("DELETE FROM stats_match WHERE joueur_id = ?", (ancien_id[0],))
            conn.execute("DELETE FROM joueurs WHERE nom = ?", (ancien,))
            print('DOUBLON supprime: ' + ancien)
        else:
            print('DEJA OK: ' + nouveau)
    else:
        r = conn.execute("UPDATE joueurs SET nom = ? WHERE nom = ?", (nouveau, ancien))
        if r.rowcount > 0:
            print('OK: ' + ancien + ' -> ' + nouveau)
        else:
            print('NON TROUVE: ' + ancien)

conn.commit()
conn.close()
print('Termine !')