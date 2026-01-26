# README

## Introduction

Dans les entrepôts logistiques, la préparation des commandes représente une part importante du temps et des coûts opérationnels. Les commandes reçues sont traitées via un Warehouse Management System (WMS), puis confiées à des préparateurs chargés de collecter les produits correspondants.

L’un des principaux leviers d’optimisation consiste à réduire les distances parcourues lors de ces collectes. Parmi les différentes approches possibles (picking, batching, slotting), ce projet se concentre uniquement sur le slotting, c’est-à-dire l’organisation des produits dans l’entrepôt.

L’objectif est de déterminer un emplacement adapté pour chaque produit, tout en respectant les contraintes du problème, afin de limiter les déplacements, rapprocher les produits souvent commandés ensemble et améliorer l’efficacité globale de la préparation des commandes.

Ce projet est réalisé dans un cadre pédagogique, en lien avec des problématiques industrielles réelles.

---

## 📁 Arborescence du projet

L’arborescence du projet est organisée comme suit :

```
/
├── build/
├── data/
├── lib/
├── python/
├── solutions/
├── src/
└── README.md
```

### `build/`

**Fichiers générés automatiquement** (binaires, résultats intermédiaires, logs, etc.).
Ce dossier peut être supprimé et régénéré sans perte d’information.
* Cmake
### `data/`

**Données d’entrée** du projet (instances, paramètres, jeux de tests).

### `lib/`

**Bibliothèques** du projet. 
On va utilser ces modules par le code principal situé dans `src/`.

### `python/`

Dossier dédié aux **scripts Python**.
Il peut inclure :

* des scripts d’analyse,
* des outils d’expérimentation,
* des visualisations de résultats,
* ou des automatisations diverses.

### `solutions/`

**Solutions produites par le projet**.
Cela peut inclure des fichiers de sortie, des résultats finaux ou des comparaisons de performances.

### `src/`

Le **cœur du code source**. L’implémentation principale du modèle, des algorithmes et de la logique métier.

---

## Classes et interactions

TODO

---

## Idées et autres...

### Conventions de nommage

* **Fonctions et méthodes** : `snake_case`

  * Exemple : `read_solution()`, `check_rack_capacity()`

* **Fichiers** = pareil que leur classe : `CamelCase`

  * Exemple : `DataLoader.cpp`, `DataLoader.py`
