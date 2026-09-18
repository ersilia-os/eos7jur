# RetroMol Biosynthetic Fingerprint

Decomposes a natural product into the biosynthetic building blocks its assembly line would have used, returning a 452-dimensional count vector over monomer tokens spanning polyketide extender units, amino acids and tailoring modifications. RetroMol was built to give natural products and their biosynthetic gene clusters a shared encoding, and applies curated retrobiosynthetic rules rather than a trained model, so output is fully deterministic. A coverage value reports how much of the molecule was parsed; compounds outside modular polyketide and nonribosomal peptide chemistry parse poorly.

This model was incorporated on 2026-09-18.


## Information
### Identifiers
- **Ersilia Identifier:** `eos7jur`
- **Slug:** `retromol-fingerprint`

### Domain
- **Task:** `Representation`
- **Subtask:** `Featurization`
- **Biomedical Area:** `Any`
- **Target Organism:** `Any`
- **Tags:** `Fingerprint`, `Natural product`, `Descriptor`

### Input
- **Input:** `Compound`
- **Input Dimension:** `1`

### Output
- **Output Dimension:** `453`
- **Output Consistency:** `Fixed`
- **Interpretation:** Weights of 451 biosynthetic building-block tokens plus an unidentified-monomer bin and a coverage fraction.

Below are the **Output Columns** of the model:
| Name | Type | Direction | Description |
|------|------|-----------|-------------|
| feat_000 | float | high | Accumulated weight of monomers that no matching rule could identify |
| feat_001 | float | high | Accumulated weight of the 1-(1-1-dimethylallyl)-tryptophan biosynthetic building block token |
| feat_002 | float | high | Accumulated weight of the 1-aminocyclopropane-1-carboxylic acid biosynthetic building block token |
| feat_003 | float | high | Accumulated weight of the 1-pyrroline-5-carboxylic acid biosynthetic building block token |
| feat_004 | float | high | Accumulated weight of the 10-14-dimethyloctadecanoic acid biosynthetic building block token |
| feat_005 | float | high | Accumulated weight of the 2-2-dimethylpropanoic acid biosynthetic building block token |
| feat_006 | float | high | Accumulated weight of the 2-3-diaminobutyric acid biosynthetic building block token |
| feat_007 | float | high | Accumulated weight of the 2-3-diaminopropionate biosynthetic building block token |
| feat_008 | float | high | Accumulated weight of the 2-3-dihydroxy-para-aminobenzoic acid biosynthetic building block token |
| feat_009 | float | high | Accumulated weight of the 2-3-dihydroxybenzoic acid biosynthetic building block token |

_10 of 453 columns are shown_
### Source and Deployment
- **Source:** `Local`
- **Source Type:** `External`
- **S3 Storage**: [https://ersilia-models-zipped.s3.eu-central-1.amazonaws.com/eos7jur.zip](https://ersilia-models-zipped.s3.eu-central-1.amazonaws.com/eos7jur.zip)

### Resource Consumption
- **Model Size (Mb):** `1`
- **Environment Size (Mb):** `931`


### References
- **Source Code**: [https://github.com/moltools/retromol](https://github.com/moltools/retromol)
- **Publication**: [https://doi.org/10.64898/2026.06.12.731935](https://doi.org/10.64898/2026.06.12.731935)
- **Publication Type:** `Preprint`
- **Publication Year:** `2026`
- **Ersilia Contributor:** [TiagoJanela](https://github.com/TiagoJanela)

### License
This package is licensed under a [GPL-3.0](https://github.com/ersilia-os/ersilia/blob/master/LICENSE) license. The model contained within this package is licensed under a [MIT](LICENSE) license.

**Notice**: Ersilia grants access to models _as is_, directly from the original authors, please refer to the original code repository and/or publication if you use the model in your research.


## Use
To use this model locally, you need to have the [Ersilia CLI](https://github.com/ersilia-os/ersilia) installed.
The model can be **fetched** using the following command:
```bash
# fetch model from the Ersilia Model Hub
ersilia fetch eos7jur
```
Then, you can **serve**, **run** and **close** the model as follows:
```bash
# serve the model
ersilia serve eos7jur
# generate an example file
ersilia example -n 3 -f my_input.csv
# run the model
ersilia run -i my_input.csv -o my_output.csv
# close the model
ersilia close
```

## About Ersilia
The [Ersilia Open Source Initiative](https://ersilia.io) is a tech non-profit organization fueling sustainable research in the Global South.
Please [cite](https://github.com/ersilia-os/ersilia/blob/master/CITATION.cff) the Ersilia Model Hub if you've found this model to be useful. Always [let us know](https://github.com/ersilia-os/ersilia/issues) if you experience any issues while trying to run it.
If you want to contribute to our mission, consider [donating](https://www.ersilia.io/donate) to Ersilia!
