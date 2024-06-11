#!/usr/bin/env bash

from collections import namedtuple
from pathlib import Path

import click
import duckdb
import spacy
from loguru import logger

DEFAULT_DB_NAME = "data/corpus.duckdb"


def output_as_jsonl(result):
    stdout = click.get_text_stream("stdout")
    result.to_json(stdout, orient="records", lines=True, force_ascii=False)


def output_as_tsv(result):
    stdout = click.get_text_stream("stdout")
    result.to_csv(stdout, sep="\t", index=False, encoding="utf-8")


def output_based_on_format(result, output_format):
    output_fn = {
        "jsonl": output_as_jsonl,
        "tsv": output_as_tsv,
    }.get(output_format, click.echo)

    output_fn(result)


def safely_grab_db(db):
    if not db:
        import os

        db = (
            os.environ["DUCKDB_DATABASE"]

            if "DUCKDB_DATABASE" in os.environ
            else DEFAULT_DB_NAME
        )

    return db
