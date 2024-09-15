import json
import random
from collections import Counter, defaultdict

import click
from loguru import logger
from tqdm import tqdm
from uralicNLP import uralicApi

DISAMBIGUATION_METHODS = {"first", "last", "random", "longest", "shortest"}


def disambiguate(candidates, disambiguation_method):
    if disambiguation_method == "first":
        return candidates[0]
    elif disambiguation_method == "last":
        return candidates[-1]
    elif disambiguation_method == "random":
        return random.choice(candidates)
    elif disambiguation_method == "longest":
        return max(candidates, key=len)
    elif disambiguation_method == "shortest":
        return min(candidates, key=len)
    else:
        raise ValueError(f"Unknown disambiguation method: {disambiguation_method}")


@click.command()
@click.option("--input-file", help="Input file to segment", type=click.File("r"))
@click.option("--language", help="Language of the input file", type=str, default="fin")
@click.option(
    "--disambiguation-method",
    help="Disambiguation method to use",
    type=click.Choice(DISAMBIGUATION_METHODS),
    default="longest",
    show_default=True,
)
@click.option("--with-stats", help="Print statistics", is_flag=True)
@click.option("--debug", help="Enable debug logging", is_flag=True)
def main(input_file, language, disambiguation_method, with_stats, debug):
    word_to_n_morphemes = Counter()
    n_morphemes_to_words = defaultdict(list)
    n_morpheme_histogram = Counter()
    n_skipped_empty = 0
    n_skipped_no_segm = 0
    n_words_accepted = 0
    n_words_considered = 0

    for word in tqdm(input_file, desc="Reading inputs..."):
        n_words_considered += 1
        output_row = {}
        word = word.strip()

        if not word:
            if debug:
                logger.debug(f'Skipping word "{word}" it is empty.')
            n_skipped_empty += 1

            continue

        segmentations = uralicApi.segment(word, language=language)

        if not segmentations:
            if debug:
                logger.debug(f'Skipping word "{word}" it has no segmentations.')
            n_skipped_no_segm += 1

            continue

        for segmentation in segmentations:
            n_morphemes = len(segmentation)
            word_to_n_morphemes[word] += n_morphemes
            n_morphemes_to_words[n_morphemes].append(word)
            n_morpheme_histogram[n_morphemes] += 1

        chosen_segmentation = disambiguate(
            candidates=segmentations, disambiguation_method=disambiguation_method
        )
        output_row["word"] = word
        output_row["segmentation"] = chosen_segmentation
        output_row["n_morphemes"] = len(chosen_segmentation)
        output_row["n_candidate_segmentations"] = len(segmentations)

        output_json = json.dumps(output_row, ensure_ascii=False, indent=None)
        click.echo(output_json)

        n_words_accepted += 1

    if with_stats:
        logger.info("Overall statistics:")
        logger.info(
            f"Number of words processed: {n_words_considered:-,}",
        )
        logger.info(
            f"Number of words accepted: {n_words_accepted:-,}",
        )
        logger.info(
            f"Number of skipped words with no segmentations: {n_skipped_no_segm:-,}"
        )
        logger.info(
            f"Number of skipped empty words: {n_skipped_empty:-,}",
        )

        logger.info(f"Accept rate: {n_words_accepted / n_words_considered:.2%}")
        logger.info(
            f"Rejection rate: {(n_skipped_no_segm + n_skipped_empty) / n_words_considered:.2%}"
        )

        click.echo("Histogram of number of morphemes per word:")

        for n_morphemes, n_words in sorted(
            n_morpheme_histogram.items(), key=lambda x: x[0]
        ):
            logger.info(f"{n_morphemes} {n_words:-,}", err=True)


if __name__ == "__main__":
    main()
