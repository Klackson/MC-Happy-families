# MonteCarlo Happy Families

A Monte-Carlo planning framework for playing **Happy Families** (*Jeu des 7 familles*) under imperfect information, with four AI agents of increasing sophistication benchmarked against each other.

## The problem

Happy Families is an information-asymmetric card game: players ask opponents for specific cards, collect complete families to score points, and keep their hands hidden. The challenge is deciding *who to ask* and *for which card* when you can't see anyone else's hand. Every ask leaks information to opponents, and every failed ask hands them your turn.

## How it works

The game engine (`game.py`) tracks each player's hand, a draw pile, scored families, and a **belief matrix** — a `(nb_players × nb_families × nb_cards)` array that is updated after every ask: the asked card's probability goes to 0 for the asked player if they don't have it, and other unseen cards in that family get redistributed. Beliefs also gently converge toward the mean each turn to avoid overconfidence.

When an AI needs to pick a move, it first **samples a plausible world**: it knows its own hand exactly, then fills in the other players' unknown cards by sampling from the belief-weighted distribution (`assume_game_state_v2`). It then simulates many games from that world and picks the move with the highest average score.

## The four agents

**SimpleAI** — samples 100 random worlds, tries each possible ask in each, runs a random playout to the end, and picks the highest expected score.

**PIMC** (Perfect Information Monte Carlo) — same world sampling, but instead of a random playout, plays each simulated world to completion with both agents acting greedily on full information.

**NestedAI** — two-level planning: samples 6 worlds, and for each world evaluates moves using an inner Monte Carlo loop. If the move succeeds (lucky), it recursively finds the best next move for itself; if it fails, it finds the best move the *opponent* would make (minimax-style).

**SmarterAI** — same as NestedAI but uses the belief-weighted world sampling (v2) at both levels instead of uniform random, and applies a softmax temperature on scores to soften argmax decisions.

Results of head-to-head matchups are logged in the `.txt` files in the repo.
