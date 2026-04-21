import sqlite3

conn = sqlite3.connect('database/scouting.db')

doublons = conn.execute('''
    SELECT j.nom, e.nom as equipe, COUNT(*) as nb
    FROM stats_match s
    JOIN joueurs j ON s.joueur_id = j.id
    JOIN equipes e ON j.equipe_id = e.id
    WHERE e.nom = 'Nancy'
    GROUP BY s.joueur_id
    HAVING COUNT(*) > 1
''').fetchall()

print('Doublons Nancy: ' + str(len(doublons)))
for d in doublons:
    print(d)

conn.close()