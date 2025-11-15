# **PokeVault**

PokeVault est une application permettant de gérer une collection de cartes Pokémon : ajout, suivi, organisation par set, et estimation de valeur.
Le projet est structuré en **monorepo** avec un backend FastAPI et un frontend Nuxt 3.

---

## **Structure**

```
/frontend   → Interface utilisateur (Nuxt 4, Tailwind)
/backend    → API (FastAPI, PostgreSQL)
```

---

## **Fonctionnalités prévues**

* Gestion de la collection (ajout, édition, suppression)
* Organisation par set / numéro / rareté
* Suivi d’informations : état, prix d’acquisition, date d’acquisition
* Import simplifié via photo (OCR du numéro + suggestions)
* Visualisation de cartes manquantes par set (mastersets)
* Suivi de la valeur de la collection (prix externes)
* Dashboard basique : valeur totale + évolution

---

## **Technologies**

**Frontend**

* Nuxt 4
* TailwindCSS
* @nuxt/ui

**Backend**

* FastAPI
* SQLAlchemy
* PostgreSQL
* OCR (pytesseract)

---

## **Installation**

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
make install
make run
```

---

## **Objectif du projet**

Fournir un outil simple pour gérer une collection Pokémon de manière propre, structurée et visuelle, sans dépendre d’un Excel ou d’applications limitées.