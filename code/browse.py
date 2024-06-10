from collections import namedtuple
from pathlib import Path

import click
import duckdb
import spacy
from loguru import logger

nlp = spacy.load("fi_core_news_lg")

TokenMatch = namedtuple(
    "TokenMatch", ["document_id", "sentence_id", "token_id", "token"]
)

DEFAULT_DB_NAME = "data/corpus.duckdb"


def safely_grab_db(db):
    if not db:
        import os

        db = (
            os.environ["DUCKDB_DATABASE"]

            if "DUCKDB_DATABASE" in os.environ
            else DEFAULT_DB_NAME
        )

    return db


@click.group()
def cli():
    pass


@cli.command("ingest")
@click.option("--db", type=click.Path(), required=False)
@click.option("--debug/--no-debug", default=False)
@click.argument("input_directory")
def ingest(db, debug, input_directory):

    db = safely_grab_db(db)

    """Ingest a directory of text files."""
    conn = duckdb.connect(database=db, read_only=False)
    conn.execute(
        """
    CREATE TABLE IF NOT EXISTS tokens (
        document_id INTEGER,
        sentence_id INTEGER,
        token_id INTEGER,
        document_file TEXT,
        token TEXT,
        lemma TEXT,
        pos TEXT,
        dep TEXT,
        morph TEXT
    )
    """
    )

    input_path = Path(input_directory)

    for document_idx, file in enumerate(input_path.glob("*.txt")):
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()

        doc = nlp(text)

        if debug:
            logger.debug(f"Processing file: {file.name}")

        for sent_idx, sent in enumerate(doc.sents):
            for token in sent:
                token = token
                lemma = token.lemma_
                pos = token.pos_
                dep = token.dep_
                morph = token.morph
                conn.execute(
                    """
INSERT INTO tokens (
    document_id,
    sentence_id,
    token_id,
    document_file,
    token,
    lemma,
    pos,
    dep,
    morph
)
VALUES (
    {document_idx},
    {sent_idx},
    {token_idx},
    '{file_name}',
    '{token}',
    '{lemma}',
    '{pos}',
    '{dep}',
    '{morph}'
)
""".format(
                        document_idx=document_idx,
                        sent_idx=sent_idx,
                        token_idx=token.i,
                        token=str(token),
                        lemma=lemma,
                        pos=pos,
                        dep=dep,
                        morph=morph,
                        file_name=file.name,
                    )
                )

    conn.close()


@cli.command("query")
@click.option("--db", type=click.Path(exists=True), required=False)
@click.option("--debug/--no-debug", default=False)
@click.argument("query", required=True)
def query(db, debug, query):
    """Query an existing collection saved to a.duckdb file."""

    db = safely_grab_db(db)

    with duckdb.connect(database=db, read_only=False) as conn:

        if debug:
            logger.debug(f"Querying for '{query}'")

        result = conn.execute(
            f"""
        SELECT document_id, sentence_id, token_id, token
        FROM tokens
        WHERE token = '{query}'
        """
        ).fetchall()

        for row in result:
            matched_token = TokenMatch(*row)
            click.echo(matched_token)


@cli.command("fetch-sentence")
@click.option("--db", type=click.Path(exists=True), required=False)
@click.option("--debug/--no-debug", default=False)
@click.argument("document_id", required=True)
@click.argument("sentence_id", required=True)
def fetch(db, debug, document_id, sentence_id):
    """Query an existing collection saved to a.duckdb file."""

    db = safely_grab_db(db)

    with duckdb.connect(database=db, read_only=False) as conn:

        if debug:
            logger.debug(f"Fetcing sentence {sentence_id} from document {document_id}")

        result = conn.execute(
            f"""
        SELECT token
        FROM tokens
        WHERE document_id = {document_id}
        AND sentence_id = {sentence_id}
        """
        ).fetchall()

        tokens = " ".join([tok[0] for tok in result]).strip()
        click.echo(tokens)


@cli.command("fetch-all")
@click.option("--db", type=click.Path(exists=True), required=False)
@click.option("--debug/--no-debug", default=False)
@click.argument("document_id", required=True)
@click.argument("sentence_id", required=True)
def fetch(db, debug, document_id, sentence_id):
    """Query an existing collection saved to a.duckdb file."""

    db = safely_grab_db(db)
    stdout = click.get_text_stream("stdout")

    with duckdb.connect(database=db, read_only=False) as conn:

        if debug:
            logger.debug(f"Fetcing sentence {sentence_id} from document {document_id}")

        result = conn.sql(
            f"""
        SELECT *
        FROM tokens
        WHERE document_id = {document_id}
        AND sentence_id = {sentence_id}
        """
        ).df()

        result.to_json(stdout, orient="records", lines=True)


if __name__ == "__main__":
    cli()
