# import mysql.connector
#
# # def get_db_connection():
# #     conn = mysql.connector.connect(
# #         host="localhost",
# #         port=5222,
# #         user="root",
# #         password="",
# #         database="amazon_scraper"
# #     )
# #     return conn
#
# # Création de la table
# conn = get_db_connection()
# cursor = conn.cursor()
#
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS produits (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     marque VARCHAR(255) NOT NULL,
#     processeur VARCHAR(255),
#     taille_ecran VARCHAR(100),
#     disque_dur VARCHAR(255),
#     prix VARCHAR(100),
#     note DECIMAL(3,1),
#     avis INT
# )
# """)
#
# conn.commit()
# cursor.close()
# conn.close()
#
# print("✅ Table 'produits' créée avec succès.")
