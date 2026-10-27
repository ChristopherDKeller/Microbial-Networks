# Prüft, welche Spalten in den beiden Metadaten-Dateien vorhanden sind und welche nicht
# --> Alle Spalten die Redbiom enthält sind in Qiita enthalten, aber nicht alle Spalten die Qiita enthält sind in Redbiom enthalten
import pandas as pd

qiita = pd.read_csv("qiita_metadata.tsv", sep="\t", low_memory=False)
redbiom = pd.read_csv("redbiom_metadata.tsv", sep="\t", low_memory=False)

print("Qiita:", qiita.shape)
print("Redbiom:", redbiom.shape)

print("Qiita-Spalten:", qiita.columns[:10].tolist())
print("Redbiom-Spalten:", redbiom.columns[:10].tolist())


qiita_cols = set(qiita.columns)
redbiom_cols = set(redbiom.columns)

print("Nur Qiita:", len(qiita_cols - redbiom_cols))
print("Nur Redbiom:", len(redbiom_cols - qiita_cols))
print("Gemeinsam:", len(qiita_cols & redbiom_cols))

print("\nNur in Qiita:")
print(sorted(qiita_cols - redbiom_cols))

print("\nNur in Redbiom:")
print(sorted(redbiom_cols - qiita_cols))