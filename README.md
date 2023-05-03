# ingest-procmon

This is a utility to quickly index Procmon exports into elasticsearch. It should be able to handle whatever columns you have selected, these are the ones that I use personally that work with this script:

![Procmon Column Settings](/media/columns.png)

Just edit the configuration YAML file as appropriate, rename it to `config.yml` and you should be good to go! The appropriate mappings have already been defined in `procmon-mapping.json`.

## Usage

```
python3 .\ingest-procmon.py --help
usage: ingest-procmon.py [-h] [--file FILE] [--index INDEX]

optional arguments:
  -h, --help     show this help message and exit
  --file FILE    The Procmon CSV logfile to index into elasticsearch
  --index INDEX  The index to index documents into. If not selected, the index
                 specified in configuration will be used.
```

### Example

```
python3 ./ingest-procmon.py --file sampledata.csv --index procmon-sample-data
```