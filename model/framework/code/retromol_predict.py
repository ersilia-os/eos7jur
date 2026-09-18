"""RetroMol biosynthetic fingerprint.

Parses a molecule into its biosynthetic building blocks with RetroMol's
retrobiosynthetic ruleset, then encodes the resulting monomers as a
452-dimensional count vector plus a coverage value.

Two points that are easy to get wrong and are load-bearing here:

1. Bin index is the token's alphabetical position in the vocabulary, because
   RetroMol's Fingerprinter only hashes when the vocabulary outgrows the bit
   width, which it does not at 452 tokens. Adding a single rule upstream would
   therefore renumber the vector silently. `vocabulary.txt` freezes the token
   order that `run_columns.csv` describes, and `_check_vocabulary_drift` refuses
   to run if the installed ruleset no longer matches it.

2. The paper reports a 1024-dimensional vector. That figure comes from the fixed
   width of the DuckDB array column in RetroMol's own retrieval database, not
   from the fingerprint: bins 452-1023 are unreachable and always zero. This
   model emits the 452 reachable bins, which is what `Fingerprinter(vocab)`
   returns by default.
"""

import os

# Read by retromol.utils.timeout at import time, so it must be set first.
os.environ.setdefault("TIMEOUT_RUN_RETROMOL", "60")

import numpy as np
from rdkit import Chem
from retromol.model.rules import RuleSet
from retromol.model.submission import Submission
from retromol.pipelines.parsing import run_retromol_with_timeout
from retromol_fingerprint.fingerprint import Fingerprinter, Vocabulary

ROOT = os.path.dirname(os.path.abspath(__file__))
VOCABULARY_FILE = os.path.join(ROOT, "vocabulary.txt")

N_TOKENS = 452
N_COLUMNS = N_TOKENS + 1  # the token bins plus coverage

_RULES = RuleSet.load_default()
_VOCABULARY = Vocabulary.from_file(VOCABULARY_FILE)
_FINGERPRINTER = Fingerprinter(_VOCABULARY)


def _check_vocabulary_drift():
    """Abort if the installed ruleset no longer matches the frozen vocabulary.

    A mismatch means the column meanings in run_columns.csv have shifted, which
    is silent and unrecoverable at the level of stored predictions. Failing at
    import is the only safe response.
    """
    installed = set()
    for rule in _RULES.matching_rules:
        installed.add(rule.name)
        installed.update(rule.pseudonyms or [])
    frozen = set(_VOCABULARY.tokens) - {"<UNK>"}
    if installed != frozen:
        added = sorted(installed - frozen)
        removed = sorted(frozen - installed)
        raise RuntimeError(
            "Installed RetroMol ruleset does not match vocabulary.txt, so "
            "fingerprint bins no longer mean what run_columns.csv says. "
            f"Added: {added[:10]}. Removed: {removed[:10]}. "
            "Pin retromol to the version this model was built against."
        )


_check_vocabulary_drift()

if _FINGERPRINTER.size != N_TOKENS:
    raise RuntimeError(
        f"Expected a {N_TOKENS}-bin fingerprint, got {_FINGERPRINTER.size}."
    )


def _monomer_tokens(result):
    """Collect the token set of every monomer across every readout path.

    All paths are pooled rather than only the longest one, so tailoring
    modifications that sit off the main backbone (glycosylation, methylation)
    still reach the fingerprint. An unidentified monomer contributes an empty
    token list, which Fingerprinter.encode routes to the <UNK> bin.
    """
    tokens = []
    for path in result.linear_readout.paths:
        for node in path:
            identity = node.identity
            rule = getattr(identity, "matched_rule", None) if identity else None
            if rule is None:
                tokens.append([])
            else:
                tokens.append([rule.name] + list(rule.pseudonyms or []))
    return tokens


def _featurize_one(smiles):
    """Return the 453 values for one SMILES, or None if it cannot be computed.

    None is reserved for molecules RetroMol could not process at all: an
    unparseable SMILES, a parser error, or a timeout. A molecule that parses
    successfully but yields no identified monomers is a real result, not a
    failure, and comes back as zeros with a coverage of 0.0.
    """
    # RDKit builds an atom-less molecule from an empty string rather than
    # failing, and RetroMol then reports it as parsed with zero coverage. Reject
    # anything that is not a real molecule up front, so an empty cell in a user
    # CSV yields a null row instead of a fabricated all-zero fingerprint.
    if not isinstance(smiles, str) or not smiles.strip():
        return None
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None or molecule.GetNumAtoms() == 0:
        return None

    try:
        result = run_retromol_with_timeout(Submission(smiles=smiles), _RULES)
        fingerprint = _FINGERPRINTER.encode(_monomer_tokens(result))
        coverage = result.calculate_coverage()
    except Exception:
        # Deliberately broad: a single malformed molecule must not abort the
        # batch. Covers RetroMol's readout ValueError on molecules whose root
        # node drops out of the synthesis graph (~0.7% of NPAtlas) and the
        # 60 s timeout. Unparseable input is already handled above.
        return None
    return np.concatenate([fingerprint, np.float32([coverage])])


def featurize(smiles_list):
    """Return an (N, 453) float32 array of fingerprints plus coverage.

    Rows for molecules that could not be processed are NaN, so the output keeps
    one row per input in the original order.
    """
    out = np.full((len(smiles_list), N_COLUMNS), np.nan, dtype=np.float32)
    for i, smiles in enumerate(smiles_list):
        values = _featurize_one(smiles)
        if values is not None:
            out[i] = values
    return out
