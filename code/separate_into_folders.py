import json
import random
import tempfile as tmp
from collections import Counter, defaultdict
from pathlib import Path

import click
import yaml
from loguru import logger
from tqdm import tqdm
from uralicNLP import uralicApi


def format_output(data, output_format):
    if output_format == "jsonl":
        return json.dumps(data)
    elif output_format == "yaml":
        return yaml.dump(data)


@click.command()
@click.option("--input-file", help="Input file to segment", type=click.File("r"))
@click.option(
    "--output-folder",
    help="Output folder.",
    type=click.Path(path_type=Path),
    default=None,
)
@click.option("--filename-field", help="Field to use as filename", required=True)
@click.option("--stratify-field", help="Field to stratify the data by", required=True)
@click.option("--output-format", type=click.Choice(["jsonl", "yaml"]))
@click.option("--debug", help="Enable debug logging", is_flag=True)
def main(
    input_file, output_folder, filename_field, stratify_field, output_format, debug
):
    if output_folder is None:
        output_folder = Path(tmp.mkdtemp())

    if not output_folder.exists():
        output_folder.mkdir(parents=True)

    for json_line in tqdm(input_file, desc="Reading json_lines..."):
        data = json.loads(json_line)
        stratify_value = data[stratify_field]
        inner_output_folder = output_folder / str(stratify_value)

        if not inner_output_folder.exists():
            inner_output_folder.mkdir(parents=True)

        output_file = inner_output_folder / f"{data[filename_field]}.{output_format}"
        with output_file.open("a") as f:
            click.echo(format_output(data, output_format), file=f)


if __name__ == "__main__":
    main()
