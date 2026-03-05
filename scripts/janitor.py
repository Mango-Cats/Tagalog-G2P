import pandas as pd


def rem_with_char(
    data: pd.DataFrame, char_set: set[str] = {"c", "f", "j", "Ã±", "q", "v", "x", "z"}
) -> pd.DataFrame:
    mask = data["word"].apply(lambda x: char_set.isdisjoint(set(str(x).lower())))
    return data[mask]


def rem_min_len(data: pd.DataFrame, min_len: int = 2) -> pd.DataFrame:
    return data[data["word"].str.len() >= min_len]


if __name__ == "__main__":
    file = "train.dict"
    df = pd.read_csv(
        file, sep=None, engine="python", header=None, names=["word", "pronunciation"]
    )

    df = rem_min_len(df)
    df = rem_with_char(df)

    df.to_csv("cleaned.dict", sep=" ", index=False, header=False, quoting=3)
