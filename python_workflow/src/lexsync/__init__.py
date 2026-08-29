"""lexsync: lexical optimisation and hardware-timed experiment generation."""
from .corpora import fetch_corpus, list_corpora
from .counterbalancing import balance_lists, counterbalance, participant_table
from .datasheet import build_datasheet, methods_paragraph, write_datasheet
from .generation import build_lexdec_stimuli, generate_pseudowords, make_pseudoword
from .matching import match_stimuli, resample_stimuli, select_continuous_stimuli
from .paradigms import PARADIGMS, required_fields, resolve_events
from .querying import (
                       add_bigram_frequency,
                       add_neighbourhood,
                       add_pair_overlap,
                       build_pool,
                       count_syllables,
                       load_items,
                       load_lexicon,
                       load_pool,
                       merge_norms,
)
from .run_pipeline import run_all, run_pipeline
from .scripting import (
                       export_experiments,
                       export_jspsych,
                       export_opensesame,
                       export_psychopy,
                       resolve_trial_timing,
)
from .validation import (
                       balance_check,
                       cohens_d,
                       cohens_d_ci,
                       describe_stimuli,
                       match_report,
                       match_report_continuous,
                       tost_equiv,
                       variance_ratio,
)

__all__ = [
    "load_lexicon", "load_items", "load_pool", "add_neighbourhood", "add_bigram_frequency",
    "count_syllables", "merge_norms", "build_pool", "match_stimuli",
    "resample_stimuli", "select_continuous_stimuli", "make_pseudoword",
    "generate_pseudowords", "build_lexdec_stimuli",
    "PARADIGMS", "resolve_events", "required_fields",
    "counterbalance", "balance_lists", "participant_table", "describe_stimuli", "cohens_d",
    "cohens_d_ci", "tost_equiv", "variance_ratio", "balance_check", "match_report",
    "match_report_continuous", "export_experiments",
    "export_psychopy", "export_opensesame", "export_jspsych", "resolve_trial_timing",
    "add_pair_overlap",
    "list_corpora", "fetch_corpus",
    "build_datasheet", "methods_paragraph", "write_datasheet",
    "run_pipeline", "run_all",
]
__version__ = "0.1.0"
