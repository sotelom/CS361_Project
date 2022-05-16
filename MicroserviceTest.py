import requests

ENDPOINT = f"https://showboat-rest-api.herokuapp.com/report-generator"

reports = [
           {"sim_number": "1",
            "num_trials": "10000",
            "num_opponents": "3",
            "user_cards": [12, 52],
            "opponent_cards": [[38, 52], [52, 52], [11, 0]],
            "community_cards": [25, 52, 52, 52, 52],
            "win_pct": "70.5",
            "loss_pct": "25.5",
            "tie_pct": "4.0"
           },
           {"sim_number": "2",
            "num_trials": "8000",
            "num_opponents": "2",
            "user_cards": [51, 52],
            "opponent_cards": [[38, 52], [11, 0]],
            "community_cards": [25, 52, 52, 52, 52],
            "win_pct": "73.5",
            "loss_pct": "24.5",
            "tie_pct": "2.0"
           }
]

# reports = [
#            {"sim_number": "1",
#             "num_trials": "10000",
#             "num_opponents": "3",
#             "user_cards": ["A of S", "?"],
#             "opponent_cards": [["A of H", "?"], ["?", "?"], ["K of C", "2 of C"]],
#             "community_cards": ["A of D", "?", "?", "?", "?"],
#             "win_pct": "70.5",
#             "loss_pct": "25.5",
#             "tie_pct": "4.0"
#            },
#            {"sim_number": "2",
#             "num_trials": "8000",
#             "num_opponents": "2",
#             "user_cards": ["A of S", "?"],
#             "opponent_cards": [["A of H", "?"], ["K of C", "2 of C"]],
#             "community_cards": ["A of D", "?", "?", "?", "?"],
#             "win_pct": "73.5",
#             "loss_pct": "24.5",
#             "tie_pct": "2.0"
#            }
# ]

headers = {"Content-Type": "application/json"}
res = requests.post(ENDPOINT, json=reports, headers=headers)
print(res.text)