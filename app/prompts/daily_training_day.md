Génère ou adapte le planning à partir de la target_date fournie dans les données.
Base-toi sur les objectifs en cours, les milestones récemment atteintes, les séances récentes, les résultats de course et les feedbacks.

S'il existe un planning, retourne uniquement les journées et milestones nécessitant des changements. Sinon, propose un planning en fonction des objectifs. Ne modifie jamais de journée antérieure à target_date ni de séance déjà terminée.

Réponds uniquement avec un objet JSON contenant :
- updated_training_days : une liste d'objets avec training_day_date (YYYY-MM-DD) et trainings (liste).
- updated_milestones : une liste d'objets décrivant les modifications d'objectifs existants.

Chaque training contient :
- id_training : l'identifiant fourni dans le contexte pour modifier une séance existante ; null pour créer une séance. N'invente jamais d'identifiant.
- training_type : "running" ou "strength".
- title : titre non vide.
- training_duration : entier strictement positif, en minutes.
- training_distance : nombre strictement positif en km pour running ; null pour strength.
- description : description non vide de la séance.

Les entraînements et journées omis sont conservés. La liste trainings décrit uniquement les créations et modifications, pas un remplacement complet de la journée. Une liste vide crée un jour de repos si aucune séance n'existe pour cette date ; elle ne supprime jamais les séances déjà présentes. Pour modifier une séance, utilise son id_training plutôt que d'en recréer une. Il ne peut y avoir qu'une séance de chaque type par jour, en comptant les séances existantes conservées. Ne change pas l'identifiant, la date d'association, le statut de réalisation ni le feedback d'une séance.

Chaque milestone modifiée contient :
- id_milestone : identifiant d'un objectif en cours fourni dans le contexte.
- date_estimated : date estimée YYYY-MM-DD, à partir de target_date.
- milestone_type : "distance", "pace" ou "pace on distance".
- milestone_distance : distance positive en km pour distance et pace on distance, sinon null.
- milestone_speed : allure positive en minutes/km pour pace et pace on distance, sinon null.

Ne modifie pas les milestones atteintes et ne crée pas de milestone dans cette réponse. Retourne une liste vide pour chaque catégorie ne nécessitant aucun changement. Le schéma JSON joint précise les champs autorisés.
