# Pipeline d'import & d'analyse d'images

Cette section décrit le flux complet côté backend pour l'import de photos (FilePond) et l'analyse OCR/CV aboutissant à la création d'une carte dans la collection d'un utilisateur.

---

## Vue d'ensemble

1. **Upload** : le frontend envoie une ou plusieurs images via `POST /imports/batches` en précisant `subject_type` (`cards` ou `sealed`).
2. **Stockage temporaire** : les octets sont stockés dans Redis (TTL configurable) et les métadonnées sont persistées dans `analysis_images`.
3. **Analyse** : `ImageAnalyzer` (OpenCV multi-rotations + EasyOCR/pytesseract) détecte les cartes présentes, découpe les différentes zones (haut, bas, texte) et extrait des features (nom, PV, numéro, set, illustrateur, année…).
4. **Matching** : `CardMatchingService` interroge la base complète `cards` + `sets` et retourne des candidats scorés.
5. **Validation UX** : le frontend affiche les candidats classés, l'utilisateur valide ou choisit un autre candidat.
6. **Création collection** : `POST /imports/drafts/{draft_id}/select` crée un `UserCard`, marque le draft comme validé et met à jour la progression `user_master_set`.

---

## Modules clés

| Module | Rôle |
| --- | --- |
| `app/services/image_store.py` | Lecture/écriture des octets d'image dans Redis (`IMAGE_TTL_SECONDS`). |
| `app/models/analysis_image.py` | Métadonnées d'une image (filename, mimetype, TTL, statut). |
| `app/services/image_analysis.py` | Détection multi-cartes (classeurs, rotations) + OCR contextuel (zones nom/HP/bas de carte). |
| `app/services/card_text.py` | Wrapper EasyOCR/pytesseract pour extraire les champs structurés (FR par défaut). |
| `app/services/card_matching.py` | Ranking combinant nom/numéro/HP/types/illustrateur + similarité visuelle ORB (optionnelle). |
| `app/services/card_similarity.py` | Compare un crop et l'artwork officiel via ORB (activé si `ANALYSIS_VISUAL_MATCHING=1`). |
| `app/models/card_draft.py` | Résultat d'analyse d'une carte détectée (candidats, statut, `subject_type`). |
| `app/models/user_card.py` | Carte effectivement possédée par l'utilisateur (créée après validation). |
| `app/models/user_master_set.py` | Suivi de la progression utilisateur sur un set précis. |
| `app/services/reporting.py` | Génère un JSON d'audit horodaté dans `ANALYSIS_OUTPUT_DIR`. |

---

## API Import/Analyse

> Tous les endpoints nécessitent un JWT d'accès (`Authorization: Bearer <token>`).

### 1. POST `/imports/batches`

Upload multipart (`files[]`) → retourne `batch_id` et la liste des drafts créés.

```bash
curl -H "Authorization: Bearer $TOKEN" \
  -F "subject_type=cards" \
  -F "files=@/tmp/carte-1.jpg" -F "files=@/tmp/carte-2.jpg" \
  http://localhost:8000/imports/batches
```

Réponse:

```json
{
  "batch_id": "b16e6dc1-16d9-41d8-8d2d-a109354b4ae1",
  "drafts": [
    {
      "id": "1918c5d7-67aa-42b6-bacd-3b7a29ea0df7",
      "image_id": "b288c722-815e-4f2d-9c8b-8c02ec0789c6",
      "status": "awaiting_validation",
      "image_url": "/imports/images/b288c722-815e-4f2d-9c8b-8c02ec0789c6",
      "subject_type": "cards",
      "candidates": [{ "card_id": "sv3-51", "name": "Noadkoko", "score": 0.91, "...": "..." }],
      "detected_metadata": {
        "probable_name": "NOADKOKO",
        "local_number": "051",
        "raw_text": "..."
      }
    }
  ]
}
```

### 2. GET `/imports/images/{image_id}`

Stream de l'image stockée dans Redis (réservé au propriétaire). Chaque lecture rafraîchit le TTL.

### 3. GET `/imports/batches/{batch_id}`

Récupère les drafts d'un batch pour rafraîchir l'UI ou suivre un traitement asynchrone.

### 4. GET `/imports/drafts/{draft_id}`

Retourne un draft individuel.

### 5. POST `/imports/drafts/{draft_id}/select`

Payload:

```json
{
  "card_id": "sv3-51",
  "quantity": 1,
  "condition": "near_mint",
  "price_paid": 12.5,
  "acquired_at": "2024-10-31",
  "notes": "Pull perso"
}
```

Réponse:

```json
{
  "draft": { "...": "Draft mis à jour (status=validated)", "subject_type": "cards" },
  "user_card": {
    "id": "d566ba9a-78cf-4c1a-94f0-1c8c9498acdb",
    "card_id": "sv3-51",
    "quantity": 1,
    "condition": "near_mint"
  },
  "master_set": {
    "set_id": "sv3",
    "owned_card_count": 52,
    "tracked_card_count": 221,
    "completion_rate": 0.235
  }
}
```

---

## Modèles SQL ajoutés

| Table | Description | Champs clés |
| --- | --- | --- |
| `analysis_images` | Métadonnées d'une image temp stockée (Redis key, TTL, content type). | `redis_key`, `expires_at`, `status`. |
| `card_drafts` | Résultat d'analyse d'une carte détectée (candidats JSON, statut, image_id, type). | `batch_id`, `top_candidate_id`, `detected_metadata`, `subject_type`. |
| `user_cards` | Inventaire utilisateur (quantité, état, prix, lien vers draft source). | `condition`, `price_paid`, `draft_id`. |
| `user_master_set` | Progression completiste sur un set. | `tracked_card_count`, `owned_card_count`, `completion_rate`. |

Les migrations Alembic associées se trouvent dans `backend/migrations/versions/2025010601_image_pipeline.py`.

---

## Déploiement & variables d'environnement

| Variable | Rôle | Valeur par défaut |
| --- | --- | --- |
| `DATABASE_URL` | Connexion PostgreSQL | – |
| `REDIS_URL` | Cache pour les images | `redis://localhost:6379/0` |
| `IMAGE_TTL_SECONDS` | TTL des images temporaires | `900` |
| `ANALYSIS_MAX_CANDIDATES` | Nb max de candidats retournés par carte | `5` |
| `ANALYSIS_CONFIDENCE_THRESHOLD` | Seuil (hint UX) pour mettre en avant le top 1 | `0.82` |
| `ANALYSIS_OUTPUT_DIR` | Dossier où sont stockés les rapports JSON horodatés | `output` |
| `ANALYSIS_LANGUAGES` | Langues passées à EasyOCR/pytesseract | `fr,en` |
| `ANALYSIS_VISUAL_MATCHING` | Active la comparaison visuelle ORB | `1` |
| `CARD_ASSET_BASE_URL` | URL fallback pour récupérer un artwork officiel | – |

> Exemple docker-compose local (PostgreSQL + Redis) :

```yaml
services:
  postgres:
    image: postgres:16
    ports: ["5432:5432"]
    environment:
      POSTGRES_PASSWORD: postgres
  redis:
    image: redis:7
    ports: ["6379:6379"]
```

Lancez ensuite:

```bash
cd backend
alembic upgrade head
uvicorn app.main:app --reload
```

---

## Flux complet (frontend -> backend)

1. **Sélection FilePond** (Nuxt) → bouton "Analyser" → `useImports.uploadBatch(FormData)` (avec `subject_type`) → `POST /imports/batches`.
2. **FastAPI** stocke chaque image dans Redis, crée `analysis_images`, lance `ImageAnalyzer`, crée `card_drafts` et produit un rapport JSON dans `output/`.
3. **Réponse** : `batch_id` + `drafts`. L'UI affiche le top 1 + bouton "Valider" + "Plus d'options".
4. **Validation** : `selectDraft(draftId, payload)` → `POST /imports/drafts/{id}/select`.
5. **Backend** : crée `user_cards`, marque le draft validé, recalcul `user_master_set`.
6. **UI** : met à jour la carte comme validée, affiche badge + message succès.

---

## Aller plus loin

- Support des items scellés : l'API accepte déjà `subject_type=sealed` (pas d'analyse, rapport archivé) – brancher un matcher dédié ultérieurement.
- Analyse asynchrone : déplacer l'analyse dans une tâche Celery/RQ, `status=pending` jusqu'à completion.
- Historique : stocker le JSON complet de détection pour audit/ML.
