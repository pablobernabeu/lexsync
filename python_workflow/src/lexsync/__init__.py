# -*- coding: utf-8 -*-
"""lexsync: multidimensional lexical optimisation and hardware-timed experiment generation."""
from .corpora import fetch_corpus, list_corpora
from .counterbalancing import counterbalance, participant_table
from .generation import build_lexdec_stimuli, generate_pseudowords, make_pseudoword
from .matching import match_stimuli
from .paradigms import PARADIGMS, required_fields, resolve_events
from .querying import add_neighbourhood, build_pool, load_items, load_lexicon
from .run_pipeline import run_all, run_pipeline
from .scripting import (export_experiments, export_jspsych, export_opensesame,
                        export_psychopy)
from .validation import (balance_check, cohens_d, cohens_d_ci, describe_stimuli,
                         match_report, tost_equiv)

__all__ = [
    "load_lexicon", "load_items", "add_neighbourhood", "build_pool", "match_stimuli",
    "make_pseudoword", "generate_pseudowords", "build_lexdec_stimuli",
    "PARADIGMS", "resolve_events", "required_fields",
    "counterbalance", "participant_table", "describe_stimuli", "cohens_d",
    "cohens_d_ci", "tost_equiv", "balance_check", "match_report", "export_experiments",
    "export_psychopy", "export_opensesame", "export_jspsych", "list_corpora", "fetch_corpus",
    "run_pipeline", "run_all",
]
__version__ = "0.1.0"
