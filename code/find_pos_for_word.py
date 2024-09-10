#!/usr/bin/env python

import click
import pandas as pd


@click.command()
@click.option(
    "--pos-jsonl",
    type=click.Path(exists=True),
    help="Path to the TSV file containing the part-of-speech tags",
)
@click.argument("words", nargs=-1)
def main(pos_jsonl, words):
    df = pd.read_json(pos_jsonl, lines=True)
    df["token"] = df.token.str.lower()
    click.echo(
        df[df.token.isin(words)].to_json(
            orient="records", lines=True, force_ascii=False
        ), nl=False
    )


if __name__ == "__main__":
    main()
