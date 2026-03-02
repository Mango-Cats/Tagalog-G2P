docker build -t phonetisaurus .
docker run --rm -it -v "${PWD}:/work" phonetisaurus bash
