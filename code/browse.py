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


def output_as_jsonl(result):
    stdout = click.get_text_stream("stdout")
    result.to_json(stdout, orient="records", lines=True)


def output_as_tsv(result):
    stdout = click.get_text_stream("stdout")
    result.to_csv(stdout, sep="\t", index=False)


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


@cli.command("ingest", help="Ingest a directory of text files.")
@click.option("--db", type=click.Path(), required=False)
@click.option("--debug/--no-debug", default=False)
@click.argument("input_directory")
def ingest(db, debug, input_directory):

    db = safely_grab_db(db)

    """Ingest a directory of text files."""
    with duckdb.connect(database=db, read_only=False) as conn:
        conn.execute(
            """
        CREATE TABLE IF NOT EXISTS tokens (
            document_id INTEGER,
            sentence_id INTEGER,
            token_id INTEGER,
            document_file TEXT,
            token TEXT,
            lemma TEXT,
            suffix TEXT,
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
                    suffix = token.suffix_
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
        suffix,
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
        '{suffix}',
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
                            suffix=suffix,
                            pos=pos,
                            dep=dep,
                            morph=morph,
                            file_name=file.name,
                        )
                    )


def output_based_on_format(result, output_format):
    output_fn = {
        "jsonl": output_as_jsonl,
        "tsv": output_as_tsv,
    }.get(output_format, click.echo)

    output_fn(result)


@cli.command("query", help="Query an existing collection for a given token.")
@click.option("--db", type=click.Path(exists=True), required=False)
@click.option(
    "--output-format", "-f", type=click.Choice(["jsonl", "tsv"]), default="tsv"
)
@click.option("--debug/--no-debug", default=False)
@click.argument("query", required=True)
def query(db, output_format, debug, query):
    """Query an existing collection saved to a.duckdb file."""

    db = safely_grab_db(db)

    with duckdb.connect(database=db, read_only=False) as conn:

        if debug:
            logger.debug(f"Querying for '{query}'")

        result = conn.sql(
            f"""
        SELECT document_id, sentence_id, token_id, token
        FROM tokens
        WHERE token = '{query}'
        """
        ).df()

        output_based_on_format(result, output_format)


def fetch_sentence(db, document_id, sentence_id, debug=False):
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

        sentence = " ".join([tok[0] for tok in result]).strip()
        return sentence


@cli.command("fetch-sent-str", help="Fetch a sentence from a document.")
@click.option("--db", type=click.Path(exists=True), required=False)
@click.option(
    "--output-format", "-f", type=click.Choice(["jsonl", "tsv"]), default="jsonl"
)
@click.option("--debug/--no-debug", default=False)
@click.argument("document_id", required=True)
@click.argument("sentence_id", required=True)
def fetch_sent_str(db, output_format, debug, document_id, sentence_id):
    """Query an existing collection saved to a.duckdb file."""

    db = safely_grab_db(db)

    sentence = fetch_sentence(db, document_id, sentence_id, debug)
    click.echo(sentence)


def fetch_sentence_plus_metadata(db, document_id, sentence_id, debug=False):
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

        return result


@cli.command("fetch-sent-all", help="Fetch sentence with per-token metadata")
@click.option("--db", type=click.Path(exists=True), required=False)
@click.option(
    "--output-format", "-f", type=click.Choice(["jsonl", "tsv"]), default="tsv"
)
@click.option("--debug/--no-debug", default=False)
@click.argument("document_id", required=True)
@click.argument("sentence_id", required=True)
def fetch_sent_all(db, output_format, debug, document_id, sentence_id):
    """Query an existing collection saved to a.duckdb file."""

    db = safely_grab_db(db)

    result = fetch_sentence_plus_metadata(db, document_id, sentence_id, debug)
    output_based_on_format(result, output_format)


if __name__ == "__main__":
    cli()
