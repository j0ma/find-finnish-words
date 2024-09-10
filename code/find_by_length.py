import click
import pandas as pd


@click.command()
@click.option("-n", help="num suffixes", type=int, required=True)
@click.argument("tsv_file")
def main(n, tsv_file):
    df = pd.read_csv(
        tsv_file, sep="\t", names=["lemma", "inflected_word", "msd", "segments"]
    )
    df["num_segm"] = df["segments"].str.split("|").apply(len)
    filtered = df[df["num_segm"] == n]

    stdout = click.get_text_stream("stdout")
    filtered.to_csv(stdout, sep="\t", header=False, index=False)


if __name__ == "__main__":
    main()
