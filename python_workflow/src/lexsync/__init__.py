# -*- coding: utf-8 -*-
"""lexsync: multidimensional lexical optimisation and hardware-timed experiment generation."""
from .corpora import fetch_corpus, list_corpora
from .counterbalancing import counterbalance, participant_table
from .matching import match_stimuli
from .querying import add_neighbourhood, build_pool, load_lexicon
from .run_pipeline import run_all, run_pipeline
from .scripting import export_experiments, export_opensesame, export_psychopy
from .validation import (balance_check, cohens_d, describe_stimuli, match_report,
                         tost_equiv)

__all__ = [
    "load_lexicon", "add_neighbourhood", "build_pool", "match_stimuli",
    "counterbalance", "participant_table", "describe_stimuli", "cohens_d",
    "tost_equiv", "balance_check", "match_report", "export_experiments",
    "export_psychopy", "export_opensesame", "list_corpora", "fetch_corpus",
    "run_pipeline", "run_all",
]
__version__ = "0.1.0"
