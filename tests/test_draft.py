from app.models import DraftProspect
from app.recommendations.draft import build_draft_board, positional_needs


def test_positional_needs_accounts_for_already_drafted_players():
    needs = positional_needs({"RB": 2, "WR": 1})

    assert needs["RB"] == 2   # target 4, have 2
    assert needs["WR"] == 3   # target 4, have 1
    assert needs["QB"] == 1   # target 1, have 0


def test_positional_needs_never_goes_negative():
    needs = positional_needs({"QB": 5})

    assert needs["QB"] == 0


def test_drafted_players_excluded_from_board():
    prospects = [
        DraftProspect("d1", "Player A", "RB", "SEA", 5, 1, 200.0, 1.0),
        DraftProspect("d2", "Player B", "WR", "DAL", 7, 2, 190.0, 2.0),
    ]

    board = build_draft_board(prospects, drafted_ids={"d1"}, drafted_players_by_position={})

    names = [p["name"] for p in board]
    assert "Player A" not in names
    assert "Player B" in names


def test_higher_team_need_boosts_rank_for_similar_players():
    prospects = [
        DraftProspect("d1", "Needed Position Player", "TE", "KC", 10, 5, 200.0, 5.0),
        DraftProspect("d2", "Filled Position Player", "RB", "SEA", 5, 4, 201.0, 4.0),
    ]
    # Team already has plenty of RBs (need = 0) but no TE (need = 1).
    # Projected points are nearly identical, so the need bonus should decide the order.
    board = build_draft_board(prospects, drafted_ids=set(), drafted_players_by_position={"RB": 10})

    ranked_names = [p["name"] for p in board]
    assert ranked_names[0] == "Needed Position Player"


def test_recommended_rank_is_sequential_starting_at_one():
    prospects = [
        DraftProspect("d1", "A", "RB", "SEA", 5, 1, 300.0, 1.0),
        DraftProspect("d2", "B", "WR", "DAL", 7, 2, 250.0, 2.0),
        DraftProspect("d3", "C", "TE", "KC", 10, 3, 200.0, 3.0),
    ]

    board = build_draft_board(prospects, drafted_ids=set(), drafted_players_by_position={})

    ranks = [p["recommended_rank"] for p in board]
    assert ranks == [1, 2, 3]
