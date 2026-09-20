"""Pattern tables for the AI-likeness audit.

Every table maps 1:1 onto a category of the audit in ``SKILL.md``. Keeping the
data here (and the logic in ``slopscore.py``) means a new tell is a one-line
change plus a test, not a rewrite of the scorer.

Language support is English only. The tables are keyed by language so an Italian
or Spanish pack can be added without touching the scoring code, but nothing but
``en`` is calibrated today.

## Provenance of the last four categories

``metaphor_saturation``, ``missing_anchors``, ``over_unified_argument`` and
``unrelieved_earnestness`` come from StoryScope (Russell et al., arXiv:2604.03136),
a study that induces 304 narrative features from ~61,600 parallel human/LLM
stories; those features (no raw text access) separate human from AI writing
at 93.2% macro-F1. The paper is about long-form fiction; these four are the
subset of its findings that plausibly transfer to expository prose, each
backed by a total variation distance (TVD) of 0.16-0.48 between the AI and
human value distributions for its underlying feature(s), independently
re-derived from the paper's own released feature data (its PDF was
unreachable when this was written) rather than trusted from a summary. See
the "Evidence" line under each category in SKILL.md for the percentages -
not every line states its TVD explicitly (a couple of the underlying
features are multi-select, where "TVD" admits more than one reasonable
definition, so the percentages are cited alone rather than picking one) -
and evals/README.md for how the re-derivation was checked.

All four are whole-document semantic judgments in the paper (does one conceit
structure the whole piece? is every example serving the same thesis?). The
regexes below are narrow lexical proxies for a small set of common surface
tells, calibrated against real generated text rather than reimplementing the
paper's LLM-judged features. Read that plainly: a text can exhibit the
underlying pattern strongly and trip none of these regexes, and a paraphrase
of one of SKILL.md's own worked examples frequently does exactly that. They
are validated as detector *mechanics* (tests/test_detectors.py) and as a
description of real slop this project observed, not as reliable measures of
how often the pattern occurs in the wild - see evals/README.md for what that
means for the eval numbers. Two things this project's re-derivation of the
paper's data explicitly found do NOT separate AI from human text are
deliberately absent from every table: raw em-dash/parenthetical frequency
(TVD 0.03) and sentence length (TVD 0.03-0.08, and sentence fragments
actually run more common in AI text, 85% vs 67%, the opposite of the folk
assumption). Do not add either as a detector without new evidence.
"""

from __future__ import annotations

# Category keys, in the order SKILL.md lists them in the audit.
CATEGORIES: dict[str, str] = {
    "significance_inflation": "Generic statements of importance",
    "automatic_interpretation": "Automatic interpretation after facts",
    "promotional_adjectives": "Promotional adjectives",
    "formulaic_contrast": "Formulaic contrasts",
    "rule_of_three": "Three-item lists",
    "synonym_cycling": "Forced synonym variation",
    "elevated_verbs": "Avoidance of simple verbs",
    "over_structuring": "Excessive headings or bullets",
    "vague_attribution": "Vague attribution",
    "template_conclusion": "Generic conclusion",
    "meta_chatbot": "Meta-chatbot phrasing",
    "artificial_completeness": "Artificially comprehensive coverage",
    # Added from StoryScope (arXiv:2604.03136), a narrative-feature study of
    # human vs. LLM fiction. These four are whole-document tendencies with only
    # loose lexical proxies here — see the module docstring and evals/README.md
    # for the paper findings that justify each one, and for what the paper
    # explicitly found does NOT distinguish AI text (raw em-dash frequency,
    # sentence length) which is deliberately not encoded anywhere below.
    "metaphor_saturation": "Metaphor saturation",
    "missing_anchors": "Missing real-world anchors",
    "over_unified_argument": "Over-unified argument",
    "unrelieved_earnestness": "Unrelieved earnestness",
}

# Categories scored by a structural pass rather than by the regex tables.
STRUCTURAL = frozenset({"over_structuring", "artificial_completeness", "synonym_cycling"})

EN_LEXICAL: dict[str, list[str]] = {
    "significance_inflation": [
        r"\bin\s+an?\s+(?:era|age|world|time|landscape)\s+(?:of|when|where|defined\s+by|increasingly)\b",
        r"\bit\'?s\s+worth\s+(?:revisiting|remembering|considering|noting|asking|pausing)\b",
        r"\bfew\s+\w+\s+(?:carry|have|are|command)\s+as\s+much\b",
        r"\ban?\s+(?:lasting|enduring|indelible|profound|outsized)\s+(?:mark|impact|impression|legacy|relevance|influence)\b",
        r"\bspeaks?\s+to\s+(?:a|an|the|how|why|something)\b",
        r"\ba\s+(?:reminder|testament|masterclass|case\s+study|window)\s+(?:that|to|in|into)\b",
        r"\bnow\s+more\s+than\s+ever\b",
        r"\bat\s+a\s+time\s+when\b",
        r"\bat\s+its\s+core\b",
        r"\bhas\s+become\s+(?:one\s+of|a\s+defining|synonymous|shorthand)\b",
        r"\b(?:remains?|stays?)\s+(?:as\s+)?(?:relevant|central|vital|essential|important|urgent)\b",
        r"\bthe\s+(?:real|deeper|bigger)\s+(?:question|answer|challenge|opportunity|point|lesson)\b",
        r"\b(?:highlight|underscor|underlin|emphasiz)\w*\s+the\s+(?:importance|significance|need|role|value)\b",
        r"\bplays?\s+(?:a|an)\s+(?:crucial|critical|vital|key|pivotal|central|significant|important)\s+role\b",
        r"\b(?:is|are|stands?|serves?)\s+(?:as\s+)?a\s+testament\s+to\b",
        r"\bcannot\s+be\s+overstated\b",
        r"\bever[- ](?:evolving|changing|expanding|growing)\b",
        r"\bin\s+today'?s\s+(?:fast[- ]paced|digital|modern|interconnected|competitive|complex)\b",
        r"\b(?:digital|technological|business|political|cultural|media|economic)\s+landscape\b",
        r"\bin\s+an?\s+(?:increasingly|rapidly)\s+\w+\s+world\b",
        r"\bhas\s+become\s+(?:increasingly\s+)?(?:essential|crucial|vital|indispensable)\b",
        r"\bat\s+the\s+forefront\s+of\b",
        r"\ba\s+(?:crucial|critical|vital|key|pivotal)\s+(?:step|milestone|moment|turning\s+point)\b",
    ],
    "automatic_interpretation": [
        r"[\u2014\u2013]\s*(?:it\'?s|it\s+was|and\s+that|a\s+reminder|a\s+testament|a\s+shift|a\s+sign|one\s+that|not\s+\w+,\s+but)\b",
        r",\s+a\s+(?:reminder|testament|sign|shift|reflection|signal|symptom)\s+(?:that|of|to)\b",
        r",\s+which\s+(?:in\s+turn|itself|is\s+why|says\s+something)\b",
        r"\bwhat\s+(?:this|that)\s+means\s+(?:is|for)\b",
        r"\bthat\s+\w+\s+itself\s+became\b",
        r"\bthe\s+(?:real\s+)?lesson\s+(?:here\s+)?is\b",
        # Participial commentary tacked onto the end of a factual clause.
        r",\s+(?:highlighting|underscoring|underlining|reflecting|showcasing|demonstrating|"
        r"emphasizing|signaling|signalling|illustrating|cementing|solidifying|reinforcing|"
        r"marking|paving|ushering|contributing\s+to|adding\s+to|further\s+\w+ing)\b",
        r"\bpaving\s+the\s+way\s+for\b",
        r"\bushering\s+in\s+(?:a|an|the)\b",
        r"\bwhich\s+(?:highlights|underscores|reflects|demonstrates|showcases|speaks\s+to)\b",
        r"\bthis\s+(?:development|shift|change|move|trend|milestone)\s+"
        r"(?:highlights|underscores|reflects|demonstrates|showcases|marks|signals)\b",
    ],
    "promotional_adjectives": [
        r"\bmeaningful(?:ly)?\b",
        r"\bcompelling\b",
        r"\bthoughtful(?:ly)?\b",
        r"\bholistic\b",
        r"\bnuanced\b",
        r"\belegant(?:ly)?\b",
        r"\bresilient\b",
        r"\bprofound(?:ly)?\b",
        r"\bcornerstone\b",
        r"\bmasterclass\b",
        r"\bempower(?:s|ed|ing|ment)?\b",
        r"\bunlock(?:s|ed|ing)?\s+(?:the|new|its|their)\b",
        r"\bforward[- ](?:thinking|looking)\b",
        r"\bever[- ]present\b",
        r"\bvibrant\b",
        r"\bgroundbreaking\b",
        r"\brenowned\b",
        r"\brich\s+tapestry\b",
        r"\bpivotal\b",
        r"\btransformative\b",
        r"\bremarkable\b",
        r"\bdiverse\s+array\b",
        r"\bcommitment\s+to\b",
        r"\bnestled\b",
        r"\btestament\b",
        r"\bcutting[- ]edge\b",
        r"\bstate[- ]of[- ]the[- ]art\b",
        r"\bseamless(?:ly)?\b",
        r"\bunparalleled\b",
        r"\bmeticulous(?:ly)?\b",
        r"\bmyriad\b",
        r"\bplethora\b",
        r"\binvaluable\b",
        r"\bunwavering\b",
        r"\brevolutionary\b",
        r"\bgame[- ]chang(?:er|ing)\b",
        r"\bbreathtaking\b",
        r"\bstunning\b",
        r"\bvisionary\b",
        r"\btrailblazing\b",
        r"\bworld[- ]class\b",
        r"\bpar\s+excellence\b",
        r"\bnothing\s+short\s+of\b",
        r"\bindelible\s+mark\b",
        r"\benduring\s+legacy\b",
        r"\bstoried\s+(?:career|history)\b",
    ],
    "formulaic_contrast": [
        r"\b(?:is|are|was|were)n\'?t\s+(?:just|only|merely)\b",
        r"\bit\'?s\s+about\s+\w+",
        r"\bwhere\s+some\b[^.!?\n]{0,50}\bothers\b",
        r"\b\w+ing\s+together\s+rather\s+than\b",
        r"\bnot\s+\w+ing,\s+but\s+\w+ing\b",
        r"\bboth\s+\w+\s+and\s+\w+,\s+",
        r"\bnot\s+only\b[^.!?\n]{0,80}?\bbut\s+also\b",
        r"\bnot\s+(?:just|merely|simply)\b[^.!?\n]{0,80}?\bbut\b",
        r"\bisn'?t\s+(?:just|only|merely|about)\b[^.!?\n]{0,80}?\b(?:it'?s|but)\b",
        r"\brather\s+than\b[^.!?\n]{0,60},",
        r"\bfrom\s+\w+(?:\s+\w+){0,2}\s+to\s+\w+(?:\s+\w+){0,2},",
        r"\bwhether\b[^.!?\n]{0,60}?\bor\b[^.!?\n]{0,40},",
        r"\bit'?s\s+not\s+(?:about|that)\b[^.!?\n]{0,60}?\bit'?s\b",
        r"\bmore\s+than\s+(?:just|simply)\b",
        r"\bless\s+(?:about|of)\b[^.!?\n]{0,60}?\bmore\s+(?:about|of)\b",
        # NOT included: a "where the old X did A, the new X does B" pattern
        # (a real construction - "where our old system asked users to adapt,
        # our new system adapts to the user" - one instance in this project's
        # eval draft corpus, plus one echo of it in a revision, two hits total
        # across ~100 real documents in testing). Removed after an
        # adversarial review pass found it false-positives just as readily on
        # a plain factual comparison ("where the old boiler burned oil, the
        # new boiler burns gas"), and this category has no floor, so a single
        # ordinary sentence like that would score it - not enough real value
        # to justify the risk.
    ],
    "rule_of_three": [
        # Three short comma-separated items, Oxford comma optional.
        r"\b\w+(?:\s+\w+){0,2},\s+\w+(?:\s+\w+){0,2},?\s+and\s+\w+(?:\s+\w+){0,2}\b",
    ],
    "elevated_verbs": [
        r"\bnavigat(?:e|es|ed|ing)\b",
        r"\bchampion(?:s|ed|ing)\b",
        r"\bdriv(?:e|es|ing)\s+(?:innovation|growth|change|results|value|impact)\b",
        r"\breshap(?:e|es|ing|ed)\b",
        r"\bredefin(?:e|es|ing|ed)\b",
        r"\busher(?:s|ed|ing)?\s+in\b",
        r"\butiliz(?:e|es|ed|ing|ation)\b",
        r"\bserves?\s+as\b",
        r"\bleverag(?:e|es|ed|ing)\b",
        r"\bfacilitat(?:e|es|ed|ing)\b",
        r"\barticulat(?:e|es|ed|ing)\b",
        r"\bunderwent\s+a\b",
        r"\bcommenc(?:e|es|ed|ing)\b",
        r"\bendeavou?r(?:s|ed|ing)?\b",
        r"\bdelv(?:e|es|ed|ing)\s+into\b",
        r"\bembark(?:s|ed|ing)?\s+(?:on|upon)\b",
        r"\bfoster(?:s|ed|ing)?\b",
        r"\bharness(?:es|ed|ing)?\b",
        r"\bspearhead(?:s|ed|ing)?\b",
        r"\bgarner(?:s|ed|ing)?\b",
        r"\bencompass(?:es|ed|ing)?\b",
        r"\bboasts?\b",
        r"\bnavigat(?:e|es|ed|ing)\s+the\s+(?:complexities|challenges|landscape)\b",
        r"\bauthored\b",
        r"\bsought\s+to\s+\w+",
    ],
    "vague_attribution": [
        r"\bby\s+(?:many|most|all)\s+accounts\b",
        r"\bfor\s+many,",
        r"\bis\s+often\s+(?:cited|described|seen|regarded|considered|called)\b",
        r"\bmany\s+(?:scholars|historians|researchers|leaders|teams|developers|companies|educators)\b",
        r"\bsome\s+(?:scholars|historians|researchers|would\s+say|might\s+argue)\b",
        r"\bin\s+many\s+cases\b",
        r"\bin\s+some\s+sense\b",
        r"\barguably\b",
        r"\bwidely\s+(?:cited|recognized|regarded|seen|accepted|considered|praised)\b",
        r"\breactions\b[^.!?\n]{0,40}\bvaried\b",
        r"\bexperts?\s+(?:say|believe|argue|note|agree|suggest|warn)\b",
        r"\bcritics?\s+(?:say|argue|note|contend|point\s+out)\b",
        r"\bobservers?\s+(?:say|note|argue)\b",
        r"\b(?:many|some|most)\s+(?:believe|argue|say|feel|contend|would\s+argue)\b",
        r"\bstudies\s+(?:suggest|show|indicate|have\s+shown)\b",
        r"\bresearch\s+(?:suggests|shows|indicates)\b",
        r"\bit\s+is\s+(?:widely|generally|often)\s+(?:believed|regarded|accepted|considered|held)\b",
        r"\banalysts?\s+(?:say|predict|expect|note)\b",
        r"\bhistorians?\s+(?:say|argue|note|generally\s+agree)\b",
        r"\bsupporters\s+(?:say|argue|point)\b",
        r"\bis\s+(?:widely|often)\s+(?:seen|viewed|regarded|considered)\s+as\b",
    ],
    "template_conclusion": [
        r"\bthe\s+(?:future|road\s+ahead)\s+(?:is|looks|belongs|will)\b",
        r"\bmoving\s+forward\b",
        r"\bthe\s+bottom\s+line\b",
        r"\bin\s+the\s+end\b",
        r"\bone\s+\w+\s+at\s+a\s+time\b",
        r"\bthat\'?s\s+(?:the|what)\s+\w+\s+is\s+about\b",
        r"(?mi)^\s*(?:#+\s*)?in\s+conclusion\b",
        r"\bin\s+conclusion\b",
        r"\bin\s+summary\b",
        r"\bto\s+sum\s+up\b",
        r"\ball\s+in\s+all\b",
        r"\bat\s+the\s+end\s+of\s+the\s+day\b",
        r"\blooking\s+ahead\b",
        r"\bdespite\s+these\s+(?:challenges|obstacles|difficulties|setbacks)\b",
        r"\bas\s+the\s+\w+\s+continues\s+to\s+evolve\b",
        r"\bonly\s+time\s+will\s+tell\b",
        r"\bone\s+thing\s+is\s+(?:clear|certain)\b",
        r"(?mi)^\s*ultimately,",
        r"\bwhat\s+(?:is|'s)\s+clear\s+is\s+that\b",
        r"\bremains?\s+to\s+be\s+seen\b",
        r"\bhis\s+legacy\s+(?:continues|remains|endures)\b",
    ],
    "meta_chatbot": [
        r"(?mi)^\s*(?:sure|certainly|absolutely|of\s+course|great\s+question)[!,.]",
        r"\bhere(?:'s|\s+is|\s+are)\s+(?:a|an|the)?\s*(?:detailed|comprehensive|brief|quick|short)?\s*"
        r"(?:overview|summary|breakdown|rundown|look|guide)\b",
        r"(?mi)^\s*below\s+(?:are|is)\b",
        r"\bit(?:'s|\s+is)\s+(?:important|worth)\s+(?:to\s+note|noting|mentioning)\b",
        r"\bas\s+requested\b",
        r"\bi\s+hope\s+this\s+helps\b",
        r"\blet\s+me\s+know\s+if\b",
        r"\bfeel\s+free\s+to\b",
        r"\bwould\s+you\s+like\s+me\s+to\b",
        r"\bi\s+can\s+also\s+\w+",
        r"\bin\s+this\s+(?:article|post|guide|piece),?\s+(?:we|i)(?:'ll|\s+will)\b",
    ],
    "metaphor_saturation": [
        # The extended-analogy opener: "if X was A, this is B". The paper's
        # single strongest style feature (figurative density, TVD 0.483) is a
        # whole-document judgment; this catches only its clearest syntactic
        # tell, deliberately narrow to avoid flagging one incidental idiom.
        r"\bif\s+(?:the\s+)?\w+(?:\s+\w+){0,4}\s+was\s+an?\s+\w+,\s+"
        r"(?:this|it|the\s+\w+)(?:\s+\w+)?\s+is\s+(?:the|an?)\b",
        # A three-step figurative escalation ("eroded, then cracked, then gave
        # way") — the gradual-collapse conceit the paper's examples lean on.
        r"\b\w+ed,\s+then\s+\w+ed,\s+then\s+(?:\w+\s+)?\w+\b",
        r"\bis\s+the\s+\w+\s+(?:you|we|they)\s+pay\s+(?:on|for)\b",
        r"\b(?:a|the)\s+(?:kind|sort)\s+of\s+\w+\s+that\s+(?:presses?|weighs?|sits?)\b",
        # NOT included, on purpose: a bare "is a kind of" or "think of X as Y".
        # Both are ordinary definitional/explanatory devices - "a raccoon is a
        # kind of procyonid", "think of the cache as a dictionary" - not a
        # reached-for figure. An adversarial review pass found both false-
        # positiving on legitimate taxonomic and explanatory prose; removed
        # rather than narrowed, since no simple qualifier reliably tells the
        # two apart. See evals/README.md's "How narrow, concretely" section.
    ],
    "missing_anchors": [
        # A generic placeholder standing in for a thing that has a real name.
        # Distinct from vague_attribution: this fires on entity-naming
        # avoidance in illustrations and asides that assert nothing, not on
        # unsourced claims.
        #
        # The four lookbehinds guard against the category's own worst failure
        # mode: "Kubernetes is a popular platform" names Kubernetes right
        # there, but without the guard the adjective+noun pattern fires on "a
        # popular platform" regardless of what precedes it. Excluding an
        # immediately preceding is/was/are/were rules out exactly the
        # "NAMED_THING is a popular X" predicate-nominal construction (the
        # common case where the sentence already did name something) while
        # still catching the phrase as a subject ("A popular streaming
        # service ran into trouble") or object ("we picked a popular
        # platform") - an adversarial review pass found the un-guarded
        # version scoring 2/2, the category's maximum, on a sentence that
        # named two real products.
        r"(?i)(?<!\bis\s)(?<!\bwas\s)(?<!\bare\s)(?<!\bwere\s)"
        r"\ba\s+(?:popular|leading|major|well[- ]known|certain|large|prominent|renowned)\s+"
        r"(?:streaming\s+service|company|provider|platform|framework|brand|book|author|"
        r"study|report|organization|firm|app|tool|publication)\b",
        r"(?i)(?<!\bis\s)(?<!\bwas\s)(?<!\bare\s)(?<!\bwere\s)"
        r"\bone\s+(?:leading|major|well[- ]known|popular)\s+"
        r"(?:company|provider|platform|framework|brand|tool|app)\b",
        r"\bsome\s+companies\s+have\s+(?:begun|started)\s+(?:to\s+)?experiment",
        r"\bstudies\s+in\s+recent\s+years\s+have\s+shown\b",
        # NOT included: a separate "a major provider had an outage" pattern -
        # it fully overlapped the adjective+noun pattern above on the common
        # case ("a major provider") and double-counted a single sentence as
        # two hits. The adjective+noun pattern above still catches that
        # exact case, but not every variant - "a major cloud provider had an
        # outage" no longer scores at all, since "cloud" breaks the
        # adjective+noun adjacency the surviving pattern requires. Recall was
        # already known to be narrow (see evals/README.md); this is one more
        # instance of it, not a new kind of gap.
    ],
    "over_unified_argument": [
        # Explicit cross-item unification language: every example, thread, or
        # detail is announced as pointing to the same one idea. Distinct from
        # template_conclusion (category 10), which is about generic sign-off
        # phrasing rather than forced thematic unity.
        r"\beach\s+of\s+these\s+(?:threads|examples|points|cases)\s+(?:points?|leads?|traces?)\s+back\s+to\b",
        r"\ball\s+of\s+(?:this|these)\s+points?\s+to\s+(?:the\s+)?same\b",
        r"\bthe\s+same\s+underlying\s+(?:question|idea|theme|pattern|truth)\b",
        r"\bjust\s+as\s+\w+(?:\s+\w+){0,4},\s+so\s+(?:too\s+)?\w+\b",
        r"\btaken\s+together,\s+(?:the|these)\b",
        r"\bwhat\s+(?:all\s+of\s+)?this\s+(?:comes\s+down\s+to|boils\s+down\s+to)\s+is\b",
        r"\bevery\s+(?:thread|example|detail)\s+(?:here\s+)?(?:points?|leads?|traces?)\s+back\s+to\b",
        r"\bif\s+(?:this|that|\w+)\s+\w+(?:\s+\w+){0,3}\s+taught\s+(?:us|me)\s+anything,\s+it'?s\s+that\b",
        r"\bthose\s+aren'?t\s+(?:contradictions|opposites|trade-?offs),\s+they'?re\b",
        r"\bisn'?t\s+the\s+enemy\s+of\b",
    ],
    "unrelieved_earnestness": [
        # Stock phrases from the solemn "corporate journey" register: nothing
        # dry, wry, or deflating anywhere. A lexical proxy for a genuinely
        # document-level absence (no irony anywhere), so it only catches the
        # most common boilerplate, not the underlying tonal monotony itself.
        r"\bthis\s+journey\s+has\s+been\b",
        r"\bevery\s+(?:obstacle|challenge|setback)\s+(?:became|was)\s+an?\s+opportunity\b",
        r"\b(?:challenging|difficult)\s+(?:but|yet)\s+(?:ultimately\s+)?rewarding\b",
        r"\bembrac(?:e|ed|ing)\s+(?:the\s+)?complexity\s+rather\s+than\s+shy",
        r"\bthe\s+(?:results|numbers|outcome)\s+speak\s+for\s+themselves\b",
        r"\bwas\s+not\s+without\s+its\s+(?:challenges|difficulties)\b",
        r"\ba\s+labor\s+of\s+love\b",
        r"\ba\s+deep\s+sense\s+of\s+gratitude\b",
        r"\bfew\s+experiences\s+teach\s+you\s+(?:more\s+)?about\b",
        r"\bthat\s+(?:tension|struggle|friction),?\s+i'?ve\s+come\s+to\s+believe,?\s+is\s+where\b",
        # NOT included, on purpose: a bare "required (great) patience/
        # perseverance/resilience/dedication". That phrase is satisfied by
        # ordinary factual difficulty reports ("required great patience
        # because the clips are brittle") as often as by performed
        # solemnity, and contributed zero real hits across the eval corpus
        # when it was tried - removed rather than kept as dead weight.
    ],
}

# Category 6 in SKILL.md: the same referent renamed to avoid repetition. Detected
# by counting how many distinct members of one cluster appear in a single text.
# Three or more distinct members of a cluster is the signal.
EN_SYNONYM_CLUSTERS: dict[str, list[str]] = {
    "generic-referent": [
        r"\bthe\s+technology\b",
        r"\bthe\s+platform\b",
        r"\bthe\s+solution\b",
        r"\bthe\s+tool\b",
        r"\bthe\s+system\b",
        r"\bthese\s+innovations\b",
        r"\bthe\s+offering\b",
        r"\bthe\s+space\b",
    ],
    "processor": [
        r"\bthe\s+processor\b",
        r"\bthe\s+chip\b",
        r"\bthe\s+silicon\b",
        r"\bthe\s+computing\s+unit\b",
        r"\bthe\s+die\b",
        r"\bthe\s+package\b",
    ],
    "company": [
        r"\bthe\s+company\b",
        r"\bthe\s+firm\b",
        r"\bthe\s+organization\b",
        r"\bthe\s+business\b",
        r"\bthe\s+corporation\b",
        r"\bthe\s+enterprise\b",
        r"\bthe\s+outfit\b",
    ],
    "person-leader": [
        r"\bthe\s+president\b",
        r"\bthe\s+leader\b",
        r"\bthe\s+statesman\b",
        r"\bthe\s+politician\b",
        r"\bthe\s+commander[- ]in[- ]chief\b",
        r"\bthe\s+former\s+senator\b",
        r"\bthe\s+lawmaker\b",
    ],
    "study": [
        r"\bthe\s+study\b",
        r"\bthe\s+research\b",
        r"\bthe\s+paper\b",
        r"\bthe\s+findings\b",
        r"\bthe\s+analysis\b",
        r"\bthe\s+investigation\b",
    ],
    "book": [
        r"\bthe\s+book\b",
        r"\bthe\s+volume\b",
        r"\bthe\s+work\b",
        r"\bthe\s+text\b",
        r"\bthe\s+tome\b",
        r"\bthe\s+publication\b",
    ],
}

# Category 12: the canned essay skeleton. Counted as headings, not as prose.
EN_COMPLETENESS_SECTIONS: list[str] = [
    r"^introduction$",
    r"^overview$",
    r"^background$",
    r"^benefits?$",
    r"^advantages?$",
    r"^pros$",
    r"^drawbacks?$",
    r"^disadvantages?$",
    r"^cons$",
    r"^limitations?$",
    r"^challenges?$",
    r"^criticism$",
    r"^controversies$",
    r"^implications?$",
    r"^impact$",
    r"^significance$",
    r"^legacy$",
    r"^(?:the\s+)?future(?:\s+outlook)?$",
    r"^looking\s+ahead$",
    r"^what'?s\s+next$",
    r"^conclusion$",
    r"^final\s+thoughts$",
    r"^key\s+takeaways?$",
    r"^summary$",
    r"^tips$",
    r"^best\s+practices$",
]

LEXICAL: dict[str, dict[str, list[str]]] = {"en": EN_LEXICAL}
SYNONYM_CLUSTERS: dict[str, dict[str, list[str]]] = {"en": EN_SYNONYM_CLUSTERS}
COMPLETENESS_SECTIONS: dict[str, list[str]] = {"en": EN_COMPLETENESS_SECTIONS}

SUPPORTED_LANGUAGES = tuple(sorted(LEXICAL))
