import sqlite3

conn = sqlite3.connect('database/scouting.db')

doublons = conn.execute('''
    SELECT j.nom, e.nom as equipe, COUNT(*) as nb
    FROM joueurs j
    JOIN equipes e ON j.equipe_id = e.id
    GROUP BY j.nom, j.equipe_id
    HAVING COUNT(*) > 1
''').fetchall()

print('Doublons trouves: ' + str(len(doublons)))
for d in doublons:
    print(d)

conn.close()