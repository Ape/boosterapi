import os
import sys

import boostertutor.generator
import flask
import natsort


application = flask.Flask(__name__)

gen = boostertutor.generator.MtgPackGenerator(
    os.environ["DATA"],
    validate_data=False,
)


@application.route("/booster/<set_code>")
def booster(set_code):
    set_meta = gen.data.sets.get(set_code.upper())

    if not set_meta:
        return flask.jsonify({"error": f"Set '{set_code}' not found."}), 404

    if not set_meta.boosters:
        return flask.jsonify({"error": f"Set '{set_code}' has no boosters."}), 404

    booster_type = get_booster_type(set_meta)
    booster = gen.get_pack(
        set_code,
        booster_type=booster_type,
    )

    return flask.jsonify({
        "booster_type": booster_type,
        "cards": list(get_cards(booster)),
    }), 200


def get_booster_type(set_meta):
    for booster_type in ["draft", "play", "default"]:
        if booster_type in set_meta.boosters:
            return booster_type

    return next(iter(set_meta.boosters))


def get_cards(booster):
    for item in booster.cards:
        variations = [item.card] + item.card.variations
        card = natsort.natsorted(variations, key=lambda x: x.number)[0]

        yield {
            "name": card.name,
            "mana_cost": card.mana_cost,
            "supertypes": card.supertypes,
            "types": card.types,
            "rarity": card.rarity,
            "scryfall_id": card.identifiers.scryfall_id,
        }
