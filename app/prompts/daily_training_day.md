
S'il n'y a aucun training en base de données, génère l'ensemble du planning d'entrainement en fonction du context, si un planning d'entrainement existe (trainings en base), adapte le au besoin et modifie seulement les futurs trainings (a partir de la target_date) qui ont besoin d'être modifiés en fonction des données récentes et des objectifs en cours : 
- Base-toi sur l'historique actuel, les dernières séances, les objectifs en cours et les eventuels feedbacks envoyés par l'utilisateur : a toi de décider en tant que coach, si les prochains trainings doivent être adaptés ou si les données récentes montrent que le planning d'entrainement n'a pas besoin d'être modifié par rapport aux milestones en cours. 
- Si c'est un jour de repos, la liste des trainings sera vide
- Le programme d'entrainement doit suivre le format suivant : 
{
    "updated_training_days": [
        "training_day_date": date du jour de l'entrainement,
        "trainings": [
            {
            "id_training": id du training,
            "training_type": running ou strength,
            "title": titre de la session,
            "training_duration": durée en minutes,
            "training_distance": si training_type = running,
            "description": description de l'entrainement, en fonction de si running on strength
            },
            {
            "training_type": running ou strength,
            "title": titre de la session,
            "training_duration": durée en minutes,
            "training_distance": si training_type = running,
            "description": description de l'entrainement, en fonction de si running on strength
            }
        ]
    ],
    "updated_milestones": [
        "id_milestone": id de la milestone,
        "date_estimated": date estimée de complétion,
        "milestone_type": vitesse, distance ou les deux,
        "milestone_distance": distance à faire si milestone_type = distance,
        "milestone_speed": vitesse à atteindre si milestone_type = pace
    ]

}
- Il ne peut y avoir qu'un seul training de chaque type par jour maximum