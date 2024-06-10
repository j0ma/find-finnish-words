import random

import click
import pandas as pd

## Built based on: https://jattekivaafinskaa.wordpress.com/suomen-kielen-erityispiirteet/

# Parts of speech
ADJECTIVE = "<ADJ>"
NOUN = "<N>"
VERB = "<V>"
ADVERB = "<ADV>"
PRONOUN = "<PRO>"

# Morphological categories for nouns
DERIVATION = "<DER>"
PLURAL = "<PLU>"
CASE = "<CASE>"
POSSESSIVE_SUFFIX = "<POSS>"
ENCLITIC = "<CLIT>"

# Morphological categories for nouns
MODUS_OR_TEMPORAL = "<MOD_TEMP>"
PERSON = "<PERS>"
ENCLITIC = "<CLIT>"

POSSIBLE_NOMINAL_MODIFIERS = [PLURAL, DERIVATION, CASE, POSSESSIVE_SUFFIX, ENCLITIC]
POSSIBLE_VERB_MODIFIERS = [DERIVATION, MODUS_OR_TEMPORAL, PERSON, ENCLITIC]

NOMINAL = "nominal"
VERB = "verb"


@click.command()
@click.option("--num-suffixes", "-n", type=int, required=True)
@click.option(
    "--part-of-speech", "-p", type=click.Choice([NOMINAL, VERB]), required=True
)
@click.argument("stem", default="<stem>")
def main(num_suffixes, part_of_speech, stem):
    # Given number of suffixes, sample a setting

    possible_modifiers = {
        "nominal": POSSIBLE_NOMINAL_MODIFIERS,
        "verb": POSSIBLE_VERB_MODIFIERS,
    }[part_of_speech]
    sampled_modifiers = random.sample(possible_modifiers, k=num_suffixes)
    sampled_modifiers = pd.Categorical(
        values=sampled_modifiers, categories=possible_modifiers, ordered=True
    ).sort_values()
    output = " ".join(sampled_modifiers)

    print(f"{stem} {output}")


if __name__ == "__main__":
    main()
