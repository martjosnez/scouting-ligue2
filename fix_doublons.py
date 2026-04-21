import sqlite3

conn = sqlite3.connect('database/scouting.db')

deleted = conn.execute('''
    DELETE FROM stats_match
    WHERE id NOT IN (
        SELECT MIN(id)
        FROM stats_match
        GROUP BY joueur_id
    )
''')

conn.commit()
print('Doublons supprimes: ' + str(deleted.rowcount))

total = conn.execute('SELECT COUNT(*) FROM stats_match').fetchone()[0]
print('Total stats_match apres nettoyage: ' + str(total))

conn.close()