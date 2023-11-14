import pandas as pd

K_FACTOR = 32
HOME_ADVANTAGE = 0
TOSS_ADVANTAGE = 0


def update_elo(
    elo_1,
    elo_2,
    result,
    toss_won_by_team1=False,
    K=K_FACTOR,
    home_advantage=HOME_ADVANTAGE,
    toss_advantage=TOSS_ADVANTAGE,
    return_expected=False,
):
    """
    Update the Elo ratings after a match. The K-factor is used to determine how much the Elo ratings should change.
    The home advantage is the Elo rating advantage for the home team. The toss advantage is the Elo rating advantage,

    Args:
        elo_1 (float): Elo rating for the first team before the match
        elo_2 (float): Elo rating for the second team before the match
        result (float): 1 if the first team won, 0 if the second team won
        toss_won_by_team1 (bool): True if the first team won the toss, False otherwise. Default: False
        K (float): The K-factor for Elo ratings
        home_advantage (float): The Elo rating advantage for the home team
        toss_advantage (float): The Elo rating advantage for the team that won the toss
        return_expected (bool): True if the expected score should be returned

    Returns:
        new_elo_1 (float): Updated Elo rating for the first team
        new_elo_2 (float): Updated Elo rating for the second team
        exp_1 (float): Expected score for the first team
        exp_2 (float): Expected score for the second team
    """
    elo_1_w_home_adv = elo_1 + home_advantage
    # Calculate the elos with toss advantage
    elo_1_w_advantages = elo_1_w_home_adv + toss_advantage * toss_won_by_team1
    elo_2_w_advantages = elo_2 + toss_advantage * (1 - toss_won_by_team1)

    # Calculate the expected score for each team
    exp_1 = 1 / (1 + 10 ** ((elo_2_w_advantages - elo_1_w_advantages) / 400))
    exp_2 = 1 / (1 + 10 ** ((elo_1_w_advantages - elo_2_w_advantages) / 400))

    # Update the Elo ratings
    new_elo_1 = elo_1 + K * (result - exp_1)
    new_elo_2 = elo_2 + K * (1 - result - exp_2)

    return (
        (new_elo_1, new_elo_2)
        if not return_expected
        else (new_elo_1, new_elo_2, exp_1, exp_2)
    )


def calculate_elo_ratings(
    matches, K=K_FACTOR, home_advantage=HOME_ADVANTAGE, toss_advantage=TOSS_ADVANTAGE
):
    """
    Calculate the Elo ratings after each match in the dataset

    Args:
        matches (pandas.DataFrame): DataFrame containing the match results
        K (float): The K-factor for Elo ratings
        home_advantage (float): The Elo rating advantage for the home team, default: 0
        toss_advantage (float): The Elo rating advantage for the team that won the toss, default: 0
    """
    # Initialize the Elo ratings for each team
    elo_ratings = {team: 1500 for team in matches["Team1"].unique()}
    games = []
    for season in matches["Season"].unique():
        season = matches.loc[matches["Season"] == season].to_dict("records")
        for match in season:
            # Get the Elo ratings before the match
            team1_elo_before = elo_ratings[match["Team1"]]
            team2_elo_before = elo_ratings[match["Team2"]]

            # Update the Elo ratings after the match
            result = 1 if match["WinningTeam"] == match["Team1"] else 0
            toss_won_by_team1 = match["TossWinner"] == match["Team1"]
            team1_elo_after, team2_elo_after, team1_exp, team2_exp = update_elo(
                elo_1=team1_elo_before,
                elo_2=team2_elo_before,
                result=result,
                toss_won_by_team1=toss_won_by_team1,
                K=K,
                home_advantage=home_advantage,
                toss_advantage=toss_advantage,
                return_expected=True,
            )

            # Update the Elo ratings dictionary
            elo_ratings[match["Team1"]] = team1_elo_after
            elo_ratings[match["Team2"]] = team2_elo_after

            # Save the updated Elo ratings for each match
            match["Team1_elo_before"] = team1_elo_before
            match["Team2_elo_before"] = team2_elo_before
            match["Team1_expected"] = team1_exp
            match["Team2_expected"] = team2_exp
            match["Result"] = result
            match["Team1_elo_after"] = team1_elo_after
            match["Team2_elo_after"] = team2_elo_after

            games.append(match)

        # At the end of the season, move the elo rating of each team closer to 1500
        # by 1/3rd of the difference between the current rating and 1500
        for team in elo_ratings:
            elo_ratings[team] += (1500 - elo_ratings[team]) / 3

    return pd.DataFrame(games)
