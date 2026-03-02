dict_name = "wikipron.dict"

with open("wikipron_tgl.tsv", "r", encoding="utf-8") as fin, open(
    dict_name, "w", encoding="utf-8"
) as fout:

    for line in fin:
        parts = line.strip().split("\t")
        if len(parts) < 2:
            continue

        word = parts[0]
        phonemes = " ".join(parts[1:])
        fout.write(f"{word}\t{phonemes}\n")
