"""ASA 25/261 — PREMIUM GROUNDING · RUN 001 adjudication input.

One entry per active atomic proposition (26). Each entry carries:
  * the frozen exact proposition wording (Freeze section 48) — never rewritten;
  * the Agent Arena claim-forensics analysis (frozen 4-label taxonomy, evidence
    tiers, roles, failure modes) consumed by agent_arena.forensic_report;
  * the Phase-7B representation fields (allowed_summary_strength, client
    strength, bounded-negative-search basis) consumed by
    agent_arena.artifact_binding;
  * the section-24 proposition verdict record fields.

No replacement claim language is produced anywhere (recommended_revision stays
empty by design). Evidence-preparation states are quoted from the freeze as
INPUT, never used to derive a verdict mechanically.
"""

# Bounded negative-search route records (Freeze sections 18/19/66/67/73).
# Only the five propositions that received documented proposition-specific
# negative-search work appear here. M-01b deliberately does NOT.
SEARCH_SCOPES = {
    "P-02": dict(
        search_scope_id="SS-P-02",
        resources=["PubMed title/abstract", "Europe PMC title/abstract",
                   "Europe PMC body/full text", "OpenAlex",
                   "bounded broad scholarly/web screen"],
        query_terms=["grounding", "earthing", "barefoot", "bare feet",
                     "barefoot walking", "soil contact", "direct Earth contact",
                     "conductive Earth contact", "arthritis", "arthritic"],
        date_cutoff="2026-08-22",
        search_completeness="structured",
        counts="PubMed 140 found/25 screened; Europe PMC t/a 140/25; "
               "Europe PMC full text 479/25; OpenAlex 62 deduplicated",
        result="A — NEGATIVE SEARCH STATE CONFIRMED",
    ),
    "P-05": dict(
        search_scope_id="SS-P-05",
        resources=["PubMed title/abstract", "Europe PMC title/abstract",
                   "Europe PMC body/full text", "OpenAlex",
                   "bounded broad scholarly/web screen"],
        query_terms=["grounding", "earthing", "barefoot", "soil contact",
                     "direct Earth contact", "conductive Earth contact",
                     "headache", "headaches", "migraine", "migraines"],
        date_cutoff="2026-08-22",
        search_completeness="structured",
        counts="PubMed 5/5; Europe PMC t/a 6/6; Europe PMC full text 40/25; "
               "OpenAlex 46 deduplicated",
        result="A — NEGATIVE SEARCH STATE CONFIRMED",
    ),
    "V-01": dict(
        search_scope_id="SS-V-01",
        resources=["PubMed title/abstract", "Europe PMC title/abstract",
                   "Europe PMC body/full text", "OpenAlex",
                   "bounded broad scholarly/web screen"],
        query_terms=["grounding", "earthing", "barefoot", "soil contact",
                     "direct Earth contact", "conductive Earth contact",
                     "varicose veins", "varicosis", "venous insufficiency"],
        date_cutoff="2026-08-22",
        search_completeness="structured",
        counts="PubMed 1/1; Europe PMC t/a 1/1; Europe PMC full text 6/6; "
               "OpenAlex 34 deduplicated",
        result="A — NEGATIVE SEARCH STATE CONFIRMED",
    ),
    "E-02": dict(
        search_scope_id="SS-E-02",
        resources=["PubMed title/abstract", "Europe PMC title/abstract",
                   "Europe PMC body/full text", "OpenAlex",
                   "bounded broad scholarly/web screen"],
        query_terms=["grounding", "earthing", "barefoot", "soil contact",
                     "direct Earth contact", "conductive Earth contact",
                     "brain fog", "cognitive fog"],
        date_cutoff="2026-08-22",
        search_completeness="structured",
        counts="PubMed 0/0; Europe PMC t/a 0/0; Europe PMC full text 0/0; "
               "OpenAlex 40 deduplicated",
        result="A — NEGATIVE SEARCH STATE CONFIRMED",
    ),
    "I-02": dict(
        search_scope_id="SS-I-02",
        resources=["PubMed title/abstract", "Europe PMC title/abstract",
                   "Europe PMC body/full text", "OpenAlex",
                   "bounded broad scholarly/web screen"],
        query_terms=["grounding", "earthing", "barefoot", "soil contact",
                     "direct Earth contact", "conductive Earth contact",
                     "immune function", "immune response", "immunocompetence"],
        date_cutoff="2026-08-22",
        search_completeness="structured",
        counts="PubMed 6/6; Europe PMC t/a 6/6; Europe PMC full text 67/25; "
               "OpenAlex 54 deduplicated",
        result="A — NEGATIVE SEARCH STATE CONFIRMED",
    ),
}


# ---------------------------------------------------------------------------
# Active proposition adjudications (26). Order = Freeze section 88.
# ---------------------------------------------------------------------------
PROPOSITIONS = [

# ===================== MECHANISM =====================
dict(
    pid="M-01a",
    proposition="A conductive grounding path can alter measurable electrical "
                "potential, voltage, or current associated with the human body.",
    origin="F06, repaired",
    ptype="EXPLICIT; PHYSICAL/ELECTRICAL; MECHANISTIC; PRODUCT-SPECIFIC",
    prep_state="SOME DIRECT EVIDENCE LOCATED",
    mechanism_state="DIRECTLY DEMONSTRATED IN HUMANS",
    qualifiers=["PRODUCT EQUIVALENCE UNCERTAIN"],
    routing="STANDARD BIOMEDICAL ADJUDICATION",
    label="solid",
    alt_label=None,
    alt_rationale="No competing frozen label applies: the wording asserts a "
                  "physical/electrical effect and the evidence is human "
                  "physical/electrical measurement at the same tier.",
    confidence=0.88,
    strength="limited_support",
    overlay="QUALIFIED",
    claim_strength="MODEST — a capability claim ('can alter') at the physical "
                   "measurement layer; no clinical or molecular assertion.",
    verdict_summary="Configured conductive Earth contact demonstrably changes "
                    "measurable human electrical potential, voltage or current. "
                    "The wording stays at the tier the evidence reaches; the only "
                    "material bound is that the advertised 2025 device's own "
                    "electrical equivalence is unverified.",
    evidence_tier="limited_human",
    conclusion_tier="same as evidence",
    bridge_supported=True,
    items=[
        dict(text="Sokal & Sokal 2012: under Faraday-cage conditions, measured "
                  "potentials at tongue, teeth and nails and venous blood values "
                  "changed with grounding.",
             source_reference="H09", tier="limited_human", role="supporting",
             why_it_matters="Direct human demonstration that a conductive path "
                            "alters measurable electrical state."),
        dict(text="Chevalier & Brown 2016: human body voltage and current "
                  "quantified under configured grounding.",
             source_reference="H18", tier="limited_human", role="supporting",
             why_it_matters="Independent quantification of the same physical "
                            "endpoint in a different configuration."),
        dict(text="Passi et al. 2017: preterm-infant skin voltage fell from "
                  "415.3 plus/minus 277.5 to 19.1 plus/minus 16.8 mV, a decrease "
                  "of 95.6 plus/minus 1.1 percent SE, p<.001, n=26.",
             source_reference="H19", tier="limited_human", role="supporting",
             why_it_matters="Third independent group; large, precisely reported "
                            "effect on the physical endpoint itself."),
        dict(text="Exact conductor percentage, dimensions, cable configuration, "
                  "safety resistor, ground-continuity verification and exposure "
                  "protocol of the advertised 2025 product are unverified; no "
                  "evidence line receives DIRECT PRODUCT MATCH.",
             source_reference="Freeze section 39", tier="not_applicable",
             role="missing_expected",
             why_it_matters="The measured configurations are class analogues; "
                            "the advertised device's electrical equivalence is "
                            "not established."),
    ],
    supporting=["H09 — human potentials altered under configured grounding",
                "H18 — body voltage/current quantified",
                "H19 — 95.6 percent skin-voltage reduction, p<.001"],
    contra=["Exact 2025 product electrical equivalence unverified "
            "(PRODUCT EQUIVALENCE UNCERTAIN)",
            "Configurations differ across studies; instrumentation establishes "
            "electrical change only and nothing above it"],
    missing_comparison_group=False,
    missing_causal_chain=False,
    missing_human_evidence=False,
    sufficiency="sufficient",
    sufficiency_rationale="Three independent human measurement lines address the "
                          "exact endpoint the proposition names. Sufficiency is "
                          "asserted for the physical proposition only.",
    failure_modes=[],
    risk="low",
    risk_rationale="A correct physical statement carries little reader-decision "
                   "risk on its own. Risk arises only if a reader treats it as "
                   "proof of the higher-layer health claims, which M-01b blocks.",
    reader_misunderstanding="That a measurable voltage change is itself evidence "
                            "of a health benefit.",
    affected_decision="Purchase of a wellness device.",
    directness="DIRECT — human measurement of the exact named endpoint.",
    endpoint_fidelity="HIGH — voltage/current/potential measured directly; no "
                      "clinical endpoint implied by the wording.",
    population_fidelity="PARTIAL — configured convenience and neonatal samples; "
                        "not the advertised customer population, though the "
                        "physical claim is population-insensitive.",
    timeframe_fidelity="ADEQUATE — immediate/acute measurement matches an "
                       "immediate physical capability claim.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — class analogue only.",
    causality_boundary="Configured connection causes measurable electrical "
                       "change. No higher mechanism or benefit follows.",
    replication="Multiple independent groups and configurations; exact "
                "configuration and product not replicated.",
    steelman="Strongest legitimate reading: this is the one advertised "
             "mechanistic assertion that is directly demonstrated in humans by "
             "at least three independent groups, with a large and precisely "
             "reported effect (H19). Read as a generic physical statement it is "
             "straightforwardly correct and should not be diluted.",
    steelman_result="SURVIVES — the proposition holds at the physical layer.",
    adversarial="The registry types M-01a as PRODUCT-SPECIFIC, and no evidence "
                "line achieves DIRECT PRODUCT MATCH. A reader takes 'electrons "
                "flow from the Earth into our bodies' as a claim about the "
                "purchased device, whose conductor, resistance and ground "
                "continuity are unverified.",
    adversarial_result="PARTIALLY SUSTAINED — bounds the verdict to QUALIFIED "
                       "rather than SOLID; does not defeat the proposition.",
    divergence="MATERIAL — Steelman argued SOLID on the generic physical "
               "reading; the adversarial layer's product-specificity objection "
               "was accepted, resolving to QUALIFIED.",
    residual_uncertainty="Electrical equivalence of the exact 2025 device and "
                         "configuration.",
    rationale="The wording claims a capability at the physical measurement "
              "layer and the evidence is direct human measurement at that same "
              "layer, so there is no tier gap and no rhetorical inflation: the "
              "frozen label is solid. It is nevertheless not delivered as SOLID "
              "in the reporting family because the proposition is registered as "
              "product-specific while the advertised device's own electrical "
              "behaviour is unverified — a documented bound, not a doubt about "
              "the physics.",
),

dict(
    pid="M-01b",
    proposition="During grounding, electrons originating from Earth flow into "
                "the human body in the direction, quantity, and biological "
                "distribution implied by the advertisement.",
    origin="F06, repaired",
    ptype="EXPLICIT; MOLECULAR-PROVENANCE; MECHANISTIC; PRODUCT-SPECIFIC",
    prep_state="NO MATERIAL DIRECT EVIDENCE LOCATED",
    mechanism_state="NOT ESTABLISHED",
    qualifiers=["PRODUCT EQUIVALENCE UNCERTAIN",
                "MOLECULAR PROVENANCE NOT ESTABLISHED"],
    routing="REQUIRED DIRECT ENDPOINT NOT DEMONSTRATED — this state follows from "
            "the absence of the required direct molecular provenance/direction/"
            "dose/distribution demonstration in the assembled mechanism "
            "evidence. M-01b did NOT receive the proposition-specific bounded "
            "negative-search protocol applied to P-02, P-05, V-01, E-02 and I-02.",
    label="overclaim",
    alt_label="mechanism_vs_evidence",
    alt_rationale="A mechanism_vs_evidence reading was considered and rejected "
                  "as primary under the frozen precedence rule: no animal or "
                  "preclinical pathway is being extrapolated to human clinical "
                  "benefit here. The advertisement asserts a molecular event in "
                  "humans as accomplished fact when the measurement that would "
                  "establish it was never performed — rhetorical inflation, "
                  "which the taxonomy routes to the generic label.",
    confidence=0.86,
    strength="not_directly_established",
    overlay="UNSUPPORTED",
    claim_strength="STRONG AND SPECIFIC — asserts molecular provenance, "
                   "direction, quantity and biological distribution as "
                   "established fact.",
    verdict_summary="The advertisement states that electrons originating from "
                    "Earth flow into the body. No located human study traces "
                    "electron provenance or establishes direction, biologically "
                    "relevant quantity or tissue distribution. Measured "
                    "electrical change (M-01a) is compatible with charge "
                    "movement but cannot substitute for that demonstration.",
    evidence_tier="limited_human",
    conclusion_tier="human_therapeutic",
    bridge_supported=False,
    items=[
        dict(text="Configured human voltage and current observations are "
                  "compatible with charge movement across a conductive path.",
             source_reference="H09/H18/H19", tier="limited_human",
             role="supporting",
             why_it_matters="The nearest supporting observation; it constrains "
                            "the physics but does not identify the source, "
                            "direction, dose or destination of any charge."),
        dict(text="No tracer, isotope-labelling, biologically relevant dose, "
                  "direction or tissue-distribution study was located in the "
                  "assembled mechanism evidence.",
             source_reference="Freeze sections 26/41/52", tier="not_applicable",
             role="missing_expected",
             why_it_matters="The endpoint that would establish the proposition "
                            "was never measured in any located human study."),
        dict(text="Evidence for M-01a must not be counted automatically as "
                  "evidence for M-01b; the historical conflated M-01 is "
                  "superseded precisely because it merged the two.",
             source_reference="Freeze sections 15/41", tier="not_applicable",
             role="weakening",
             why_it_matters="Blocks the substitution that would otherwise make "
                            "the proposition look supported."),
    ],
    supporting=["Electrical measurements compatible with charge movement "
                "(H09/H18/H19) — insufficient for provenance"],
    contra=["No tracer / dose / direction / tissue-distribution study located",
            "M-01a cannot substitute (frozen separation, Freeze section 15)",
            "Mechanism state frozen as NOT ESTABLISHED (Freeze sections 41/91)"],
    missing_comparison_group=False,
    missing_causal_chain=True,
    missing_human_evidence=True,
    sufficiency="insufficient",
    sufficiency_rationale="The required direct endpoint (molecular provenance "
                          "with direction, quantity and distribution) is absent "
                          "from every located human study.",
    failure_modes=[
        dict(mode="conclusion_exceeds_results",
             rationale="A molecular-provenance event is asserted as fact on the "
                       "strength of macroscopic electrical measurements that "
                       "cannot identify electron origin, direction or dose.",
             evidence_refs=["H09/H18/H19", "Freeze sections 26/41/52"]),
        dict(mode="missing_causal_chain",
             rationale="The link from measured potential change to Earth-origin "
                       "electron delivery is asserted, not demonstrated; the "
                       "chain is frozen as NOT ESTABLISHED.",
             evidence_refs=["Freeze sections 41/91"]),
        dict(mode="missing_human_evidence",
             rationale="No human study measured the provenance, direction, "
                       "quantity or tissue distribution the claim specifies.",
             evidence_refs=["Freeze sections 26/52"]),
    ],
    risk="moderate",
    risk_rationale="The mechanism sentence is what makes the downstream health "
                   "list feel physically grounded to a lay reader; accepting it "
                   "makes every later claim seem pre-justified.",
    reader_misunderstanding="That a well-understood physical process has been "
                            "shown to deliver Earth electrons into body tissue.",
    affected_decision="Purchase of a wellness device on mechanistic grounds.",
    directness="ABSENT — no direct human evidence for the named endpoint.",
    endpoint_fidelity="ENDPOINT ABSENT — provenance, dose and distribution were "
                      "not measured.",
    population_fidelity="NOT APPLICABLE — no human population carries the "
                        "required provenance or dose mapping.",
    timeframe_fidelity="NOT APPLICABLE — no relevant timeframe was measured.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — an exact device could not "
                     "close the molecular provenance gap in any case.",
    causality_boundary="M-01a cannot establish molecular source, direction, "
                       "dose or distribution.",
    replication="No direct human demonstration exists, therefore no replication.",
    steelman="Strongest legitimate reading: a conductive path to Earth does "
             "equalise potential, and charge movement is the physically "
             "expected accompaniment; the claim is not physically absurd and "
             "the direction of electron flow toward a positively charged body "
             "is a coherent hypothesis consistent with H09/H18/H19.",
    steelman_result="DOES NOT REACH THE WORDING — plausibility is not "
                    "demonstration; the advertisement asserts quantity and "
                    "biological distribution, which no located study measured.",
    adversarial="The claim imports a specific molecular narrative onto a "
                "macroscopic measurement. Neither the number of electrons, the "
                "net direction under real-world conditions, nor delivery to any "
                "tissue compartment has been shown.",
    adversarial_result="SUSTAINED.",
    divergence="NONE MATERIAL — both layers agree the required endpoint is "
               "missing; they differ only on how plausible the hypothesis is.",
    residual_uncertainty="Direct charge tracing, direction, quantity and tissue "
                         "distribution in vivo remain unmeasured.",
    rationale="The verdict rests on the absence of the specific measurement the "
              "claim presupposes, not on a proposition-specific literature "
              "sweep: M-01b was never subjected to the bounded negative-search "
              "protocol. UNSUPPORTED here means the required direct endpoint "
              "was not demonstrated in the assembled evidence — it is not a "
              "finding that no such study could exist.",
),
]

PROPOSITIONS += [

dict(
    pid="M-02",
    proposition="That electron flow neutralises free radicals in humans.",
    origin="F07",
    ptype="EXPLICIT; BIOCHEMICAL-MECHANISTIC; PRODUCT-SPECIFIC",
    prep_state="INDIRECT / MECHANISTIC ONLY",
    mechanism_state="SPECULATIVE",
    qualifiers=["PRODUCT EQUIVALENCE UNCERTAIN", "HUMAN DIRECT ASSAY ABSENT"],
    routing="STANDARD BIOMEDICAL ADJUDICATION",
    label="mechanism_vs_evidence",
    alt_label="overclaim",
    alt_rationale="An overclaim reading is defensible because the advertisement "
                  "presents the process under 'has been shown to'. "
                  "mechanism_vs_evidence is taken as primary because the "
                  "definitional trigger is squarely present: a described "
                  "biochemical pathway evidenced only ex vivo and in narrative "
                  "theory is used to assert an event in living humans.",
    confidence=0.84,
    strength="not_directly_established",
    overlay="UNSUPPORTED",
    claim_strength="STRONG — asserts an accomplished biochemical event in "
                   "humans, presented under 'has been shown to'.",
    verdict_summary="Free-radical neutralisation by grounding-delivered "
                    "electrons is a theoretical proposal supported ex vivo in "
                    "non-human tissue. No validated in-vivo human radical assay "
                    "under sham control was located, and the proposition also "
                    "inherits the unestablished provenance step (M-01b).",
    evidence_tier="cell",
    conclusion_tier="human_therapeutic",
    bridge_supported=False,
    items=[
        dict(text="Oschman 2007 and Oschman, Chevalier & Brown 2015 propose "
                  "electron-donation antioxidant action as a mechanism.",
             source_reference="R02/R03", tier="not_applicable", role="supporting",
             why_it_matters="Theoretical basis only; narrative reviews by the "
                            "core author network, not independent synthesis."),
        dict(text="Giulivi & Kotz 2025: ex-vivo mouse-liver mitochondria showed "
                  "ATP approximately +5 to 11 percent and H2O2/ROS "
                  "approximately -22 to 33 percent under reported conditions.",
             source_reference="Giulivi & Kotz 2025", tier="cell",
             role="supporting",
             why_it_matters="The strongest concrete antioxidant signal located; "
                            "it is ex vivo, non-human and cannot demonstrate "
                            "in-vivo human radical neutralisation."),
        dict(text="No direct in-vivo human free-radical assay under sham "
                  "control was located.",
             source_reference="Freeze sections 51/52/55", tier="not_applicable",
             role="missing_expected",
             why_it_matters="The endpoint the claim names has never been "
                            "measured in living humans."),
        dict(text="Lin et al. 2022 reported that the proposed electrochemical "
                  "signal was non-supportive.",
             source_reference="H26", tier="limited_human", role="weakening",
             why_it_matters="The one human study that probed a proposed "
                            "electrochemical intermediate did not support it."),
    ],
    supporting=["R02/R03 electron-donation theory",
                "Giulivi & Kotz 2025 ex-vivo mouse-liver ROS/H2O2 reduction"],
    contra=["No direct in-vivo human radical assay located",
            "H26 proposed electrochemical signal non-supportive",
            "Inherits M-01b: the electron delivery the claim presupposes is "
            "itself NOT ESTABLISHED"],
    missing_comparison_group=False,
    missing_causal_chain=True,
    missing_human_evidence=True,
    sufficiency="insufficient",
    sufficiency_rationale="Evidence sits two tiers below the claim: ex-vivo "
                          "non-human tissue and narrative theory against an "
                          "asserted in-vivo human event.",
    failure_modes=[
        dict(mode="mechanism_to_human_benefit_leap",
             rationale="An ex-vivo mouse-liver mitochondrial ROS signal and a "
                       "narrative electron-donation theory are used to assert "
                       "radical neutralisation in living humans.",
             evidence_refs=["Giulivi & Kotz 2025", "R02/R03"]),
        dict(mode="evidence_tier_mismatch",
             rationale="Evidence tier is cell/ex-vivo non-human; the conclusion "
                       "tier is an accomplished human biochemical effect.",
             evidence_refs=["Giulivi & Kotz 2025"]),
        dict(mode="missing_human_evidence",
             rationale="No validated in-vivo human radical assay under sham "
                       "control exists in the located evidence.",
             evidence_refs=["Freeze sections 51/52"]),
    ],
    risk="moderate",
    risk_rationale="Oxidative-stress language lends scientific authority to the "
                   "downstream therapeutic list without any human demonstration.",
    reader_misunderstanding="That free-radical neutralisation by grounding is an "
                            "established human physiological fact.",
    affected_decision="Purchase of a wellness device on antioxidant grounds.",
    directness="INDIRECT / MECHANISTIC ONLY — no direct human evidence.",
    endpoint_fidelity="ENDPOINT ABSENT in living humans.",
    population_fidelity="NO DIRECT HUMAN POPULATION.",
    timeframe_fidelity="NO HUMAN TIMEFRAME MEASURED.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — the exact product was "
                     "never tested on this endpoint.",
    causality_boundary="Theoretical and non-human evidence cannot establish "
                       "human radical neutralisation.",
    replication="No direct human demonstration, therefore no replication.",
    steelman="Strongest legitimate reading: electron donation is a chemically "
             "coherent antioxidant mechanism, and Giulivi & Kotz 2025 supplies "
             "a real measured reduction in H2O2/ROS with a concurrent ATP rise "
             "in mitochondria — a non-trivial, directionally consistent signal "
             "rather than pure speculation.",
    steelman_result="DOES NOT REACH THE WORDING — an ex-vivo non-human signal "
                    "cannot support an asserted in-vivo human event, and the "
                    "delivery step it presupposes is unestablished.",
    adversarial="The claim chains two unestablished steps: Earth-electron "
                "delivery (M-01b, NOT ESTABLISHED) and in-vivo neutralisation. "
                "The only human probe of a proposed electrochemical "
                "intermediate (H26) was non-supportive.",
    adversarial_result="SUSTAINED.",
    divergence="NONE MATERIAL — the layers agree on the tier gap and differ "
               "only on how much credit the ex-vivo signal deserves.",
    residual_uncertainty="A validated in-vivo human radical assay under sham "
                         "control has not been performed.",
    rationale="The claim asserts a human biochemical event on evidence drawn "
              "from non-human ex-vivo tissue and narrative theory, with the "
              "delivery step it depends on frozen as NOT ESTABLISHED. This is a "
              "mechanism-to-human leap, not a bounded search failure: the "
              "verdict reflects a tier gap, and a real ex-vivo signal is "
              "preserved rather than dismissed.",
),

dict(
    pid="M-03",
    proposition="That process reduces oxidative stress in humans.",
    origin="F07",
    ptype="EXPLICIT; BIOCHEMICAL/PHYSIOLOGICAL; PRODUCT-SPECIFIC",
    prep_state="INDIRECT / MECHANISTIC ONLY",
    mechanism_state="INDIRECTLY SUPPORTED",
    qualifiers=["PRODUCT EQUIVALENCE UNCERTAIN", "SURROGATE ENDPOINT ONLY"],
    routing="STANDARD BIOMEDICAL ADJUDICATION",
    label="mechanism_vs_evidence",
    alt_label="overclaim",
    alt_rationale="overclaim is a genuine competing reading and is recorded as "
                  "the documented alternative. mechanism_vs_evidence is primary "
                  "because the operative error is the attribution of scattered "
                  "human marker movement to a specific unestablished "
                  "preclinical pathway.",
    confidence=0.79,
    strength="not_directly_established",
    overlay="UNSUPPORTED",
    claim_strength="MODERATE-STRONG — asserts that the specific claimed process "
                   "reduces human oxidative stress.",
    verdict_summary="Some human oxidative and inflammatory markers have moved "
                    "in grounding studies, and the mechanism layer is frozen as "
                    "INDIRECTLY SUPPORTED. The proposition as worded, however, "
                    "attributes that reduction to 'that process' — the electron "
                    "delivery and radical neutralisation of M-01b and M-02, "
                    "which are NOT ESTABLISHED and SPECULATIVE. No study "
                    "mediates from electrical exposure to oxidative-stress "
                    "change.",
    evidence_tier="biomarker",
    conclusion_tier="human_therapeutic",
    bridge_supported=False,
    items=[
        dict(text="Chevalier et al. 2018: selected oxidative and inflammatory "
                  "markers changed in a 16-participant massage-therapist "
                  "stepped-wedge design.",
             source_reference="H21", tier="biomarker", role="supporting",
             why_it_matters="The nearest human oxidative-marker evidence; small, "
                            "many markers, no continuous parallel control, and "
                            "one dataset with H22."),
        dict(text="Non-human and ex-vivo oxidative signals, including the "
                  "Giulivi & Kotz 2025 mitochondrial ROS reduction.",
             source_reference="Giulivi & Kotz 2025", tier="cell",
             role="supporting",
             why_it_matters="Directionally consistent but not human and not "
                            "in vivo."),
        dict(text="No prespecified human oxidative-stress endpoint with "
                  "mediation from electrical exposure was located; the causal "
                  "electron mediation is absent.",
             source_reference="Freeze sections 53/58/63", tier="not_applicable",
             role="missing_expected",
             why_it_matters="Marker movement without mediation cannot establish "
                            "that the claimed process is the cause."),
        dict(text="Lin et al. 2022 reported the proposed electrochemical signal "
                  "as non-supportive.",
             source_reference="H26", tier="limited_human", role="weakening",
             why_it_matters="Weakens the specific proposed intermediate."),
    ],
    supporting=["H21 selected human oxidative/inflammatory markers",
                "Non-human and ex-vivo oxidative signals"],
    contra=["Markers scattered and multiply tested; no prespecification",
            "No mediation from electrical exposure to oxidative change",
            "H26 electrochemical signal non-supportive",
            "Depends on M-01b (NOT ESTABLISHED) and M-02 (SPECULATIVE)"],
    missing_comparison_group=False,
    missing_causal_chain=True,
    missing_human_evidence=False,
    sufficiency="insufficient",
    sufficiency_rationale="Human marker evidence exists but is small, multiply "
                          "tested and unmediated; it cannot attribute change to "
                          "the specific claimed process.",
    failure_modes=[
        dict(mode="mechanism_to_human_benefit_leap",
             rationale="A preclinical antioxidant pathway is credited with "
                       "human oxidative-stress reduction that scattered marker "
                       "movement does not causally establish.",
             evidence_refs=["H21", "Giulivi & Kotz 2025"]),
        dict(mode="missing_causal_chain",
             rationale="No study mediates from electrical exposure through "
                       "electron delivery and radical neutralisation to a human "
                       "oxidative-stress endpoint.",
             evidence_refs=["Freeze sections 41/53/58"]),
    ],
    risk="moderate",
    risk_rationale="Oxidative-stress reduction is the pivot from mechanism to "
                   "the advertised therapeutic list.",
    reader_misunderstanding="That the advertised electron mechanism has been "
                            "shown to lower oxidative stress in people.",
    affected_decision="Purchase of a wellness device on antioxidant grounds.",
    directness="INDIRECT / MECHANISTIC ONLY.",
    endpoint_fidelity="PARTIAL — related oxidative and inflammatory markers "
                      "exist, but not a causal-pathway endpoint.",
    population_fidelity="Biomarker and non-human samples; not general clinical "
                        "populations.",
    timeframe_fidelity="Acute and short marker windows; durable oxidative "
                       "change not measured.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — mixed devices and markers.",
    causality_boundary="No mediation from electrical exposure to human "
                       "oxidative-stress change.",
    replication="Related markers from more than one group; no exact causal "
                "replication.",
    steelman="Strongest legitimate reading: the mechanism layer is frozen as "
             "INDIRECTLY SUPPORTED, not speculative. Real human oxidative and "
             "inflammatory markers have moved in more than one group, and the "
             "non-human ex-vivo work points the same way. A differently worded, "
             "weaker association claim about grounding and some human oxidative "
             "markers would carry genuine indirect support.",
    steelman_result="PARTIALLY SURVIVES — supports an association at the marker "
                    "layer, but not the process-specific causal wording.",
    adversarial="'That process' names the M-01b/M-02 chain. With delivery NOT "
                "ESTABLISHED and neutralisation SPECULATIVE, the wording "
                "attributes marker movement to a mechanism that has not been "
                "shown to occur.",
    adversarial_result="SUSTAINED for the wording as frozen.",
    divergence="MATERIAL — Steelman established genuine indirect marker "
               "support; the adversarial layer showed the process-specific "
               "attribution fails. Resolved by verdicting the exact wording "
               "while recording the surviving marker-level support.",
    residual_uncertainty="Prespecified human oxidative-stress endpoints with "
                         "electrical-exposure mediation have not been studied.",
    rationale="The evidence-preparation state is INDIRECT / MECHANISTIC ONLY "
              "and the mechanism state is INDIRECTLY SUPPORTED, but neither is "
              "read mechanically. What defeats the exact wording is the "
              "referent of 'that process': the claim credits an unestablished "
              "delivery-and-neutralisation chain with an effect that only "
              "unmediated marker movement supports. The genuine indirect "
              "marker-level support is preserved and reported rather than "
              "suppressed.",
),
]

PROPOSITIONS += [

dict(
    pid="I-01",
    proposition="Premium Grounding reduces inflammation.",
    origin="F01/F08",
    ptype="EXPLICIT; PHYSIOLOGICAL; THERAPEUTIC; PRODUCT-SPECIFIC",
    prep_state="VERY LIMITED DIRECT EVIDENCE",
    mechanism_state=None,
    qualifiers=["SURROGATE ENDPOINT ONLY", "PRODUCT EQUIVALENCE UNCERTAIN",
                "REPLICATION ABSENT for clinical disease"],
    routing="STANDARD BIOMEDICAL ADJUDICATION",
    label="overclaim",
    alt_label="mechanism_vs_evidence",
    alt_rationale="Rejected as primary under the frozen precedence rule: the "
                  "taxonomy explicitly excludes the biomarker/surrogate-to-"
                  "clinical gap from mechanism_vs_evidence and routes surrogate "
                  "endpoints framed as clinical outcomes to overclaim.",
    confidence=0.87,
    strength="not_directly_established",
    overlay="OVERCLAIM",
    claim_strength="STRONG — an unqualified therapeutic assertion presented "
                   "alongside eleven named conditions and under 'has been shown "
                   "to'.",
    verdict_summary="Human evidence for this claim is entirely surrogate: "
                    "cytokines, CK, CRP, thermography and one uncontrolled "
                    "wound series. No clinical inflammatory-disease trial "
                    "exists, and the newest biomarker line (H34 CRP) rests on "
                    "paired within-group and post hoc subgroup tests without a "
                    "direct group contrast.",
    evidence_tier="biomarker",
    conclusion_tier="human_therapeutic",
    bridge_supported=False,
    items=[
        dict(text="Brown, Chevalier & Hill 2015 and Chevalier et al. 2018 "
                  "report selected inflammatory and CK-related marker "
                  "differences across many outcomes and timepoints.",
             source_reference="H16/H21", tier="biomarker", role="supporting",
             why_it_matters="Direct human biomarker signals, but multiply "
                            "tested and sponsor/network associated."),
        dict(text="Sokal et al. 2025: CRP 15.34 to 24.42 versus 24.54 to 57.42 "
                  "mg/L, p=.000033, with sign, mean, median and unit conflicts "
                  "preserved.",
             source_reference="H31", tier="biomarker", role="supporting",
             why_it_matters="A large nominal p-value on a surrogate marker in a "
                            "one-night postoperative setting, with unresolved "
                            "reporting conflicts."),
        dict(text="Kim JS et al. 2024: full-sample salivary CRP sneaker "
                  "98.74 to 129.11 to 185.15 pg/mL, pre to final p=.046; "
                  "barefoot 144.80 to 196.94 to 123.67, p=.608. Baseline-CRP at "
                  "or above 100 post hoc subset: sneaker n=9 p=.963; barefoot "
                  "n=14 282.13 to 254.26 to 113.11, p=.010.",
             source_reference="H34", tier="biomarker", role="supporting",
             why_it_matters="Earth-contact eligible human CRP line, but these "
                            "are paired within-group and post hoc subgroup "
                            "tests; the source table supplies no direct "
                            "group-by-time or between-group contrast."),
        dict(text="No clinical inflammatory-disease trial and no validated "
                  "clinical inflammation endpoint were located.",
             source_reference="Freeze sections 27/51/63", tier="not_applicable",
             role="missing_expected",
             why_it_matters="The claim names a therapeutic effect for which no "
                            "clinical outcome study exists."),
        dict(text="Estiningtyas et al. 2024 reported wound-score improvement in "
                  "21 patients with no comparator and incomplete methods.",
             source_reference="H29", tier="limited_human", role="weakening",
             why_it_matters="Uncontrolled; natural course and wound care cannot "
                            "be separated from the intervention."),
    ],
    supporting=["H16/H21 selected inflammatory and CK markers",
                "H31 CRP p=.000033 (surrogate, reporting-sensitive)",
                "H34 Earth-contact salivary CRP subgroup signal",
                "H29 uncontrolled wound-score observation"],
    contra=["No clinical inflammatory-disease trial located",
            "H34 CRP rests on paired/subgroup analyses without a direct group "
            "interaction test",
            "H31 CRP carries sign/mean/median/unit conflicts",
            "H16 multiplicity across many outcomes and timepoints",
            "H21/H22 are one dataset, not two replications"],
    missing_comparison_group=False,
    missing_causal_chain=True,
    missing_human_evidence=False,
    sufficiency="insufficient",
    sufficiency_rationale="All human evidence is surrogate; the claim is "
                          "therapeutic. No clinical inflammation endpoint was "
                          "measured anywhere in the located evidence.",
    failure_modes=[
        dict(mode="evidence_tier_mismatch",
             rationale="Biomarker-tier evidence (CRP, cytokines, CK, "
                       "thermography) supports a therapeutic-tier claim about "
                       "reducing inflammation.",
             evidence_refs=["H16/H21", "H31", "H34"]),
        dict(mode="conclusion_exceeds_results",
             rationale="Marker movement in small, multiply tested studies is "
                       "presented as an established anti-inflammatory effect of "
                       "the product.",
             evidence_refs=["H34", "Freeze sections 27/51"]),
    ],
    risk="high",
    risk_rationale="Readers with inflammatory conditions may substitute the "
                   "device for treatment; the advertisement pairs the claim "
                   "with arthritis and other named conditions.",
    reader_misunderstanding="That the product has been shown to reduce clinical "
                            "inflammation, rather than to move some markers in "
                            "small studies.",
    affected_decision="Management of an inflammatory condition.",
    directness="VERY LIMITED DIRECT — human, but surrogate endpoints only.",
    endpoint_fidelity="LOW — CRP, cytokines, CK, thermography and wound scores "
                      "are surrogates; no inflammatory-disease outcome.",
    population_fidelity="Mostly healthy, active, occupational, surgical or "
                        "wound samples; no inflammatory-disease programme.",
    timeframe_fidelity="Acute to five-week biomarker windows and one "
                       "postoperative night; durable clinical inflammation "
                       "absent.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — partial analogues and "
                     "barefoot exposure; no exact-product disease endpoint.",
    causality_boundary="Biomarker movement and multiplicity cannot establish "
                       "clinical anti-inflammatory efficacy.",
    replication="Multiple biomarker contexts, no common prespecified clinical "
                "inflammation endpoint; H21/H22 collapse to one dataset.",
    steelman="Strongest legitimate reading: several independent human contexts "
             "show inflammatory-marker movement in a consistent direction, "
             "including a randomised sham-controlled postoperative CRP "
             "difference (H31) and an Earth-contact CRP decline in the "
             "high-baseline barefoot subgroup (H34). This is a real, repeated "
             "biological signal and should not be dismissed as noise.",
    steelman_result="PARTIALLY SURVIVES at the biomarker layer — does not reach "
                    "the therapeutic wording.",
    adversarial="Every supporting result is a surrogate. H34's decisive-looking "
                "numbers are paired within-group and post hoc subgroup tests "
                "with no group-by-time contrast; H31's CRP reporting is "
                "internally conflicted; H16 tested many outcomes. No study "
                "measured clinical inflammation at all.",
    adversarial_result="SUSTAINED.",
    divergence="MATERIAL — Steelman defended a genuine repeated biomarker "
               "signal; the adversarial layer showed none of it reaches a "
               "clinical endpoint. Resolved as OVERCLAIM with the biomarker "
               "signal explicitly preserved.",
    residual_uncertainty="An adequately powered inflammatory-disease or "
                         "validated-inflammation-endpoint RCT has not been done.",
    rationale="The evidence-preparation state VERY LIMITED DIRECT EVIDENCE is "
              "not read as a verdict. The decisive facts are that every human "
              "result is a surrogate marker, that the strongest new line (H34) "
              "supplies no between-group contrast, and that the advertised "
              "wording asserts a therapeutic effect under 'has been shown to'. "
              "The distance between marker movement and the advertised clinical "
              "claim is what makes this an overclaim.",
),

dict(
    pid="I-02",
    proposition="Premium Grounding boosts immune function.",
    origin="F12",
    ptype="EXPLICIT; PHYSIOLOGICAL; THERAPEUTIC; PRODUCT-SPECIFIC",
    prep_state="NO MATERIAL DIRECT EVIDENCE LOCATED",
    mechanism_state=None,
    qualifiers=["SURROGATE ENDPOINT ONLY", "PRODUCT EQUIVALENCE UNCERTAIN",
                "BOUNDED NEGATIVE SEARCH"],
    routing="BOUNDED NEGATIVE SEARCH — proposition-specific negative-search work "
            "documented and confirmed at class A after expanded terminology.",
    label="overclaim",
    alt_label=None,
    alt_rationale="No specific frozen label fits: no preclinical pathway is "
                  "extrapolated and no causal inference from correlation is "
                  "drawn. The error is asserting a functional benefit on "
                  "immune-related markers that do not measure function.",
    confidence=0.89,
    strength="not_supported",
    overlay="UNSUPPORTED",
    claim_strength="STRONG — asserts an enhancement of immune function as "
                   "demonstrated.",
    verdict_summary="No study measuring immune competence, infection "
                    "incidence, pathogen clearance, vaccine response or durable "
                    "protection was located, after a documented "
                    "proposition-specific search extended with barefoot and "
                    "Earth-contact terminology. The only Earth-contact "
                    "immune-related line (H34 IFN-gamma) is discordant and "
                    "supplies no grounding-specific signal.",
    evidence_tier="biomarker",
    conclusion_tier="human_therapeutic",
    bridge_supported=False,
    items=[
        dict(text="Brown, Chevalier & Hill 2015 and Chevalier et al. 2018 "
                  "report immune-cell and cytokine markers.",
             source_reference="H16/H21", tier="biomarker", role="supporting",
             why_it_matters="Immune-related markers only; none measures immune "
                            "competence or clinical protection."),
        dict(text="Kim JS et al. 2024 salivary IFN-gamma: sneaker pre to "
                  "session 10 p=.004, barefoot p=.115; sneaker pre to session "
                  "20 p=.082, barefoot p=.167.",
             source_reference="H34", tier="biomarker", role="contradictory",
             why_it_matters="Discordant and non-supportive for a "
                            "grounding-specific signal. The nominally "
                            "significant change occurred in the SNEAKER group. "
                            "A difference in significance between two "
                            "within-group tests is not a significant "
                            "between-group difference."),
        dict(text="No immune competence, infection, pathogen-clearance or "
                  "vaccine-response endpoint was measured in any located study.",
             source_reference="Freeze sections 27/34/51", tier="not_applicable",
             role="missing_expected",
             why_it_matters="The functional endpoint the claim names does not "
                            "exist in the evidence base."),
        dict(text="Documented proposition-specific search across PubMed "
                  "(6 found/6 screened), Europe PMC title/abstract (6/6) and "
                  "full text (67/25) and OpenAlex (54 deduplicated) with "
                  "grounding, earthing, barefoot, soil-contact and Earth-contact "
                  "terminology to the 22 August 2026 cut-off: class A, negative "
                  "search state confirmed.",
             source_reference="Freeze sections 19/70/73", tier="not_applicable",
             role="missing_expected",
             why_it_matters="Establishes that the absence is a documented "
                            "bounded retrieval finding within named routes — "
                            "not proof that no such study exists anywhere."),
    ],
    supporting=["H16/H21 immune-related markers (non-functional)"],
    contra=["H34 IFN-gamma discordant / non-supportive",
            "No functional immune endpoint measured anywhere",
            "Bounded negative search class A confirmed after expanded "
            "terminology"],
    missing_comparison_group=False,
    missing_causal_chain=True,
    missing_human_evidence=True,
    sufficiency="insufficient",
    sufficiency_rationale="The functional endpoint is absent from the entire "
                          "located evidence base and a documented "
                          "proposition-specific search did not recover one.",
    failure_modes=[
        dict(mode="evidence_tier_mismatch",
             rationale="Immune-related biomarkers are offered for a claim about "
                       "immune function.",
             evidence_refs=["H16/H21", "H34"]),
        dict(mode="conclusion_exceeds_results",
             rationale="A functional immune benefit is asserted where no "
                       "functional endpoint was measured and the one "
                       "Earth-contact marker line is discordant.",
             evidence_refs=["H34"]),
        dict(mode="missing_human_evidence",
             rationale="No human study measured immune competence, infection, "
                       "pathogen clearance or vaccine response.",
             evidence_refs=["Freeze sections 27/34"]),
    ],
    risk="high",
    risk_rationale="Immune claims can lead readers to substitute a device for "
                   "vaccination, treatment or medical advice.",
    reader_misunderstanding="That the product strengthens resistance to "
                            "infection.",
    affected_decision="Infection prevention and immune health decisions.",
    directness="ABSENT for the functional endpoint.",
    endpoint_fidelity="ENDPOINT ABSENT — immune-related markers only.",
    population_fidelity="Healthy biomarker samples; no immune-compromised, "
                        "infection or vaccine population.",
    timeframe_fidelity="Acute and short biomarker windows; durable functional "
                       "immunity absent.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — no exact-product "
                     "functional immune endpoint.",
    causality_boundary="Marker movement cannot establish functional immune "
                       "benefit.",
    replication="No direct functional immune evidence, therefore no replication.",
    steelman="Strongest legitimate reading: immune-related markers including "
             "cytokines and IFN-gamma have been measured in grounded humans, "
             "and H34 is a genuine Earth-contact intervention study that "
             "entered the inventory on merit. Immunological plausibility via "
             "inflammation modulation is not absurd.",
    steelman_result="FAILS — the one Earth-contact immune line runs the wrong "
                    "way for the claim, and no functional endpoint exists.",
    adversarial="H34's only nominally significant IFN-gamma change is in the "
                "sneaker comparator group, not the barefoot group. Reading a "
                "between-group effect from that pattern would be the "
                "difference-in-significance fallacy the freeze explicitly "
                "forbids. Nothing else measures immune function at all.",
    adversarial_result="SUSTAINED.",
    divergence="NONE MATERIAL — both layers agree the functional endpoint is "
               "absent and the marker evidence is discordant.",
    residual_uncertainty="A prespecified immune competence, infection or "
                         "vaccine-response RCT has not been performed. Absence "
                         "remains a bounded search finding within the named "
                         "routes and terminology.",
    rationale="Two independent grounds converge: the functional endpoint the "
              "claim names was never measured, and the single Earth-contact "
              "immune-marker study is discordant with the claim's direction. "
              "The negative state is reported at the breadth its documented "
              "basis supports — a structured multi-route search to the "
              "cut-off — and is not represented as proof that no such study "
              "exists.",
),
]

PROPOSITIONS += [

dict(
    pid="S-01",
    proposition="Premium Grounding improves sleep quality.",
    origin="F01/F04/F09",
    ptype="EXPLICIT; SUBJECTIVE/CLINICAL; THERAPEUTIC; PRODUCT-SPECIFIC",
    prep_state="MIXED / CONFLICTING",
    mechanism_state=None,
    qualifiers=["REPORTING-SENSITIVE", "PRODUCT EQUIVALENCE UNCERTAIN"],
    routing="STANDARD BIOMEDICAL ADJUDICATION",
    label="overclaim",
    alt_label="solid",
    alt_rationale="A solid reading was considered: several controlled studies "
                  "do report sleep benefit and the underlying evidence really "
                  "is mixed rather than empty. It is rejected because the "
                  "advertised wording reports the effect as established for a "
                  "general audience while the largest set of prespecified "
                  "between-group questionnaire comparisons was null.",
    confidence=0.82,
    strength="mixed",
    overlay="OVERCLAIM",
    claim_strength="STRONG — an unqualified effect claim placed first in the "
                   "advertised benefit list.",
    verdict_summary="Sleep is the best-studied advertised outcome and the "
                    "evidence genuinely points both ways. A 12-week pilot found "
                    "a large pointwise PSQI difference but its model group "
                    "coefficient was p=.053 with 31.8 percent attrition; a "
                    "one-month double-blind trial found no day-31 difference on "
                    "ISI, PSQI, ESS or perceived stress. Neither the advertised "
                    "certainty nor a general-audience effect is established.",
    evidence_tier="limited_human",
    conclusion_tier="general_public",
    bridge_supported=False,
    items=[
        dict(text="Lin et al. 2022: week-12 PSQI grounded 0.3 plus/minus 0.7 "
                  "(n=8) versus control 3.0 plus/minus 1.9 (n=7), Mann-Whitney "
                  "p=.006.",
             source_reference="H26", tier="limited_human", role="supporting",
             why_it_matters="The strongest controlled sleep signal located; a "
                            "pointwise comparison in 15 completers."),
        dict(text="Park et al. 2025: actigraphy signal reported, but the prose "
                  "points to day 31 while a parenthetical says 'Day 38: p<.01, "
                  "t=3.5'; absolute values are absent.",
             source_reference="H30", tier="limited_human", role="supporting",
             why_it_matters="A positive objective signal whose measurement "
                            "timepoint is internally contradictory and is left "
                            "unresolved; it cannot be assigned by inference."),
        dict(text="Ghaly & Teplitz 2004 (uncontrolled n=12), Chevalier et al. "
                  "2019 (16 massage therapists) and Kim 2020 (observational mat "
                  "users) report subjective sleep improvement; H33 reports a "
                  "secondary sleep time-by-group F=7.53, p=.008.",
             source_reference="H02/H22/H24/H33", tier="limited_human",
             role="supporting",
             why_it_matters="Additional narrow signals, each uncontrolled, "
                            "self-selected, one dataset, or confounded by a "
                            "combined barefoot walking programme."),
        dict(text="Park et al. 2025 day-31 between-group results: ISI p=.275, "
                  "PSQI p=.562, ESS p=.962, BEPSI p=.756.",
             source_reference="H30", tier="limited_human", role="contradictory",
             why_it_matters="The most complete set of prespecified "
                            "between-group sleep comparisons in the substrate "
                            "is uniformly null."),
        dict(text="Lin et al. 2022 GEE group coefficient B=-1.407, SE=.7278, "
                  "95 percent Wald CI -2.834 to .019, p=.053; attrition 7/22 "
                  "(31.8 percent); registration posted February 2022 for a "
                  "trial completed July 2020.",
             source_reference="H26", tier="limited_human", role="weakening",
             why_it_matters="The model-based estimate does not reach "
                            "significance and is not a group-by-time "
                            "interaction; retrospective registration cannot "
                            "secure prespecification."),
        dict(text="Park et al. 2025 participant-flow conflicts: 60 stated, "
                  "three exclusions stated, 56 analysed, text 26/30 versus "
                  "Table 3 30/28; baseline ISI 7.6 plus/minus .7 versus 12 "
                  "plus/minus 1.2, p<.001.",
             source_reference="H30", tier="limited_human", role="weakening",
             why_it_matters="Denominator contradictions and a large baseline "
                            "imbalance prevent a stable effect estimate."),
    ],
    supporting=["H26 week-12 pointwise PSQI p=.006",
                "H30 selected actigraphy signal (timepoint unresolved)",
                "H02/H22/H24 subjective sleep signals",
                "H33 secondary sleep time-by-group F=7.53, p=.008"],
    contra=["H30 day-31 ISI p=.275, PSQI p=.562, ESS p=.962, BEPSI p=.756",
            "H26 GEE group coefficient p=.053 with 31.8 percent attrition",
            "H30 denominator and baseline conflicts; actigraphy timepoint "
            "contradiction unresolved",
            "H33 sleep signal arises inside an inseparable combined programme",
            "No exact-product protocol replication"],
    missing_comparison_group=False,
    missing_causal_chain=False,
    missing_human_evidence=False,
    sufficiency="insufficient",
    sufficiency_rationale="Evidence exists on both sides and no stable decisive "
                          "effect estimate survives the reporting conflicts.",
    failure_modes=[
        dict(mode="conclusion_exceeds_results",
             rationale="An established general effect is advertised while the "
                       "most complete prespecified between-group comparisons "
                       "were null and the strongest positive model estimate did "
                       "not reach significance.",
             evidence_refs=["H30", "H26"]),
        dict(mode="inappropriate_generalization",
             rationale="Signals from mild Alzheimer patients, 12 uncontrolled "
                       "participants, 16 massage therapists and self-selected "
                       "mat users are generalised to a general customer "
                       "audience.",
             evidence_refs=["H26", "H02", "H22", "H24"]),
    ],
    risk="moderate",
    risk_rationale="Sleep is the headline benefit and the most likely purchase "
                   "driver; readers are unlikely to see the null results.",
    reader_misunderstanding="That sleep improvement is an established, "
                            "reliable effect of the product.",
    affected_decision="Purchase; possible deferral of insomnia care.",
    directness="DIRECT but MIXED — several controlled human sleep trials with "
               "conflicting results.",
    endpoint_fidelity="MODERATE — PSQI, ISI and actigraphy are relevant "
                      "instruments, but results are inconsistent, "
                      "population-specific and reporting-sensitive.",
    population_fidelity="LOW for the advertised audience — mild Alzheimer "
                        "patients, sleep-complaint samples, occupational "
                        "cohorts and a menopause programme.",
    timeframe_fidelity="Minutes to 12 weeks; persistence generally unreported.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — sleep systems are class "
                     "analogues, not verified matches.",
    causality_boundary="Attrition, baseline imbalance, reporting conflicts and "
                       "cointerventions weaken causal sleep attribution.",
    replication="Several independent studies; no consistent exact protocol or "
                "effect replication; mixed.",
    steelman="Strongest legitimate reading: this is the one advertised outcome "
             "with multiple independent controlled trials, a large pointwise "
             "12-week PSQI difference (p=.006), an objective actigraphy signal "
             "and consistent subjective reports across four further contexts. "
             "The direction of effect is repeatedly positive and the H26 "
             "confidence interval (-2.834 to .019) excludes almost all harm.",
    steelman_result="PARTIALLY SURVIVES — supports a genuine mixed state with a "
                    "positive lean, not the advertised certainty.",
    adversarial="The single most complete set of prespecified between-group "
                "comparisons (H30 day 31) is null across all four instruments. "
                "H26's model estimate is p=.053 with a third of participants "
                "lost and retrospective registration. H30's positive actigraphy "
                "result cannot even be assigned to a timepoint.",
    adversarial_result="SUSTAINED against the advertised wording.",
    divergence="MATERIAL — Steelman defended a real positive lean; the "
               "adversarial layer showed the prespecified comparisons are null. "
               "Resolved by verdicting the advertised certainty as overclaim "
               "while recording the evidence state as genuinely mixed rather "
               "than empty.",
    residual_uncertainty="H30's actigraphy timepoint (day 31 versus day 38) is "
                         "irreducibly contradictory in the source and is left "
                         "unresolved; a registered, powered exact-product sleep "
                         "RCT with co-primary endpoints does not exist.",
    rationale="MIXED / CONFLICTING is not read as UNCERTAIN. The evidence is "
              "genuinely two-sided and is reported that way, but the "
              "adjudicated object is the advertised wording, which presents "
              "sleep improvement as an established general-audience effect. "
              "Against a null prespecified questionnaire set, a "
              "non-significant model estimate, unresolved reporting conflicts "
              "and no exact-product replication, that wording asserts more than "
              "the evidence carries.",
),

dict(
    pid="S-02",
    proposition="Premium Grounding is relevant to/alleviates insomnia.",
    origin="F02 in context",
    ptype="IMPLIED; THERAPEUTIC; CONDITION-SPECIFIC; PRODUCT-SPECIFIC",
    prep_state="VERY LIMITED DIRECT EVIDENCE",
    mechanism_state=None,
    qualifiers=["CONDITION MISMATCH", "PRODUCT EQUIVALENCE UNCERTAIN"],
    routing="STANDARD BIOMEDICAL ADJUDICATION",
    label="overclaim",
    alt_label=None,
    alt_rationale="No specific frozen label applies; the error is condition "
                  "drift from general sleep scores to a named clinical "
                  "disorder.",
    confidence=0.85,
    strength="not_directly_established",
    overlay="OVERCLAIM",
    claim_strength="STRONG BY PLACEMENT — 'Insomnia' heads the 'Do you suffer "
                   "from any of these?' list immediately before the product "
                   "benefit sentence.",
    verdict_summary="No adequately powered, registered trial in a diagnosed "
                    "insomnia population was located. The available samples are "
                    "sleep-complaint convenience groups, and the one trial that "
                    "used the standard insomnia instrument found no day-31 "
                    "between-group difference on it.",
    evidence_tier="limited_human",
    conclusion_tier="human_therapeutic",
    bridge_supported=False,
    items=[
        dict(text="Ghaly & Teplitz 2004 (n=12 with sleep dysfunction) and Park "
                  "et al. 2025 enrolled participants with sleep complaints.",
             source_reference="H02/H30", tier="limited_human", role="supporting",
             why_it_matters="Condition-adjacent samples; neither establishes a "
                            "diagnosed-insomnia population or a "
                            "response/remission endpoint."),
        dict(text="Park et al. 2025 day-31 Insomnia Severity Index "
                  "between-group p=.275.",
             source_reference="H30", tier="limited_human", role="contradictory",
             why_it_matters="The ISI is the standard insomnia instrument and it "
                            "showed no between-group difference."),
        dict(text="No diagnosed-insomnia trial with response or remission "
                  "endpoints, harms ascertainment or durable follow-up was "
                  "located.",
             source_reference="Freeze sections 51/55/63", tier="not_applicable",
             role="missing_expected",
             why_it_matters="The clinical endpoint the implied claim needs does "
                            "not exist."),
    ],
    supporting=["H02/H30 sleep-complaint samples (condition-adjacent only)"],
    contra=["H30 day-31 ISI p=.275",
            "No diagnosed-insomnia efficacy population or endpoint located",
            "General sleep-score change does not equal insomnia treatment"],
    missing_comparison_group=False,
    missing_causal_chain=False,
    missing_human_evidence=False,
    sufficiency="insufficient",
    sufficiency_rationale="No diagnosed population and no prespecified "
                          "response/remission endpoint exist in the evidence.",
    failure_modes=[
        dict(mode="inappropriate_generalization",
             rationale="General sleep-quality scores in convenience samples are "
                       "extended to a named clinical sleep disorder.",
             evidence_refs=["H02/H30"]),
        dict(mode="conclusion_exceeds_results",
             rationale="Clinical relevance to insomnia is implied while the "
                       "standard insomnia instrument showed no between-group "
                       "difference.",
             evidence_refs=["H30"]),
    ],
    risk="high",
    risk_rationale="Insomnia is a diagnosable disorder with effective "
                   "treatments; implied relevance may delay care.",
    reader_misunderstanding="That the product is a recognised option for "
                            "insomnia.",
    affected_decision="Whether to seek clinical treatment for insomnia.",
    directness="VERY LIMITED — no diagnosed-population evidence.",
    endpoint_fidelity="LOW — general sleep outcomes do not equal "
                      "diagnosed-insomnia response or remission.",
    population_fidelity="ABSENT — no confirmed diagnosed-insomnia efficacy "
                        "population.",
    timeframe_fidelity="No durable insomnia response or remission follow-up.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN plus condition mismatch.",
    causality_boundary="General sleep change cannot establish insomnia "
                       "treatment.",
    replication="No diagnosed-insomnia replication.",
    steelman="Strongest legitimate reading: participants in H02 and H30 did "
             "have sleep dysfunction rather than being healthy volunteers, and "
             "H26 showed a large 12-week PSQI difference. If grounding improves "
             "sleep quality at all, some benefit for insomnia sufferers is a "
             "reasonable expectation.",
    steelman_result="FAILS — the expectation is not evidence, and the one "
                    "insomnia-specific instrument tested was null.",
    adversarial="The claim borrows credibility from general sleep research to "
                "address a named disorder that was never studied, in a context "
                "that invites self-treatment.",
    adversarial_result="SUSTAINED.",
    divergence="NONE MATERIAL.",
    residual_uncertainty="A diagnosed-insomnia RCT with response/remission, "
                         "harms and durable follow-up has not been performed.",
    rationale="VERY LIMITED DIRECT EVIDENCE is not read as a verdict. What "
              "decides this proposition is the condition mismatch: the "
              "advertisement names a clinical disorder, the evidence contains "
              "no diagnosed population and no response or remission endpoint, "
              "and the single trial that administered the standard insomnia "
              "instrument found no between-group difference on it.",
),
]

PROPOSITIONS += [

dict(
    pid="S-03",
    proposition="Premium Grounding lowers stress levels.",
    origin="F10",
    ptype="EXPLICIT; SUBJECTIVE; THERAPEUTIC; PRODUCT-SPECIFIC",
    prep_state="MIXED / CONFLICTING",
    mechanism_state=None,
    qualifiers=["HIGH CONFOUNDING", "PRODUCT EQUIVALENCE UNCERTAIN"],
    routing="STANDARD BIOMEDICAL ADJUDICATION",
    label="overclaim",
    alt_label=None,
    alt_rationale="No specific frozen label applies; the operative error is "
                  "asserting a durable effect from acute and confounded signals "
                  "against null prespecified comparisons.",
    confidence=0.83,
    strength="mixed",
    overlay="OVERCLAIM",
    claim_strength="STRONG — 'Lower stress levels' is listed under 'has been "
                   "shown to'.",
    verdict_summary="Positive stress signals are acute, self-reported, small or "
                    "confounded by a combined walking programme, and they sit "
                    "beside two null prespecified comparisons. No durable "
                    "stress-reduction endpoint under sham control was located.",
    evidence_tier="limited_human",
    conclusion_tier="general_public",
    bridge_supported=False,
    items=[
        dict(text="Chevalier & Sinatra 2011 (n=27) reported acute heart-rate "
                  "variability changes interpreted as reduced stress.",
             source_reference="H07", tier="biomarker", role="supporting",
             why_it_matters="Acute autonomic surrogate; no durable stress "
                            "endpoint."),
        dict(text="Ghaly & Teplitz 2004 and Chevalier et al. 2019 report "
                  "subjective stress improvement.",
             source_reference="H02/H22", tier="limited_human", role="supporting",
             why_it_matters="Uncontrolled n=12 and a 16-participant "
                            "stepped-wedge dataset; self-report only."),
        dict(text="Kim M-H & Lee E-Y 2025 reported stress z=-3.58, p<.001.",
             source_reference="H33", tier="limited_human", role="supporting",
             why_it_matters="Statistically strong but arises inside a "
                            "12-week combined barefoot forest-walking programme "
                            "in which exercise, nature, social and researcher "
                            "contact cannot be separated."),
        dict(text="Park et al. 2025 day-31 perceived stress (BEPSI) "
                  "between-group p=.756.",
             source_reference="H30", tier="limited_human", role="contradictory",
             why_it_matters="A prespecified between-group stress comparison "
                            "that was null."),
        dict(text="Lin et al. 2022 reported no between-group anxiety or "
                  "depression effect.",
             source_reference="H26", tier="limited_human", role="contradictory",
             why_it_matters="Adjacent affective endpoints were null in the "
                            "best-controlled 12-week trial."),
    ],
    supporting=["H07 acute HRV", "H02/H22 subjective stress",
                "H33 stress z=-3.58, p<.001 (confounded programme)"],
    contra=["H30 day-31 BEPSI p=.756", "H26 anxiety/depression null",
            "Acute autonomic and subjective change is not durable relief",
            "H33 grounding component not isolable"],
    missing_comparison_group=False,
    missing_causal_chain=False,
    missing_human_evidence=False,
    sufficiency="insufficient",
    sufficiency_rationale="Positive signals are acute or confounded; the "
                          "prespecified controlled comparisons were null.",
    failure_modes=[
        dict(mode="conclusion_exceeds_results",
             rationale="Durable stress reduction is asserted from acute "
                       "autonomic surrogates and self-report while prespecified "
                       "between-group stress and affective comparisons were "
                       "null.",
             evidence_refs=["H07", "H30", "H26"]),
        dict(mode="inappropriate_generalization",
             rationale="A confounded 12-week menopause walking programme and a "
                       "16-participant occupational cohort are generalised to a "
                       "general audience.",
             evidence_refs=["H33", "H22"]),
    ],
    risk="moderate",
    risk_rationale="Stress claims are broadly appealing and rarely checked; the "
                   "risk is misplaced reliance rather than acute harm.",
    reader_misunderstanding="That stress reduction is a demonstrated, lasting "
                            "product effect.",
    affected_decision="Purchase; possible substitution for stress management.",
    directness="DIRECT but MIXED and confounded.",
    endpoint_fidelity="MODERATE — subjective stress and HRV are relevant but "
                      "acute or confounded; several null comparisons.",
    population_fidelity="Convenience, occupational and menopause samples; no "
                        "stress-disorder programme.",
    timeframe_fidelity="Acute to 12 weeks; durability not established.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — sheets, patches and "
                     "combined programmes differ.",
    causality_boundary="Acute autonomic and subjective change cannot establish "
                       "durable stress reduction.",
    replication="Several small lines; inconsistent endpoints and nulls; no "
                "robust replication.",
    steelman="Strongest legitimate reading: three independent contexts report "
             "reduced stress, including a large effect size in H33, and an "
             "autonomic mechanism (HRV) points the same way. Subjective stress "
             "relief is a legitimate outcome to measure by self-report.",
    steelman_result="PARTIALLY SURVIVES — a real mixed state with positive "
                    "signals, not the advertised established effect.",
    adversarial="The largest effect (H33) cannot be attributed to grounding at "
                "all, and the two prespecified between-group tests of stress "
                "and affect were null. What remains is acute HRV and "
                "self-report in tiny samples.",
    adversarial_result="SUSTAINED against the advertised wording.",
    divergence="MATERIAL — Steelman credited repeated positive signals; the "
               "adversarial layer showed the strongest one is not attributable "
               "and the controlled ones were null.",
    residual_uncertainty="No independent validated stress trial with sham or "
                         "active control and durability follow-up exists.",
    rationale="The evidence is genuinely two-sided and is reported as mixed. "
              "The advertised wording nevertheless presents stress reduction as "
              "demonstrated, when the only large effect comes from an "
              "inseparable combined programme and both prespecified "
              "between-group comparisons were null.",
),

dict(
    pid="S-04",
    proposition="Premium Grounding lowers cortisol production.",
    origin="F10",
    ptype="EXPLICIT; PHYSIOLOGICAL/BIOMARKER; PRODUCT-SPECIFIC",
    prep_state="VERY LIMITED DIRECT EVIDENCE",
    mechanism_state=None,
    qualifiers=["REPLICATION ABSENT", "PRODUCT EQUIVALENCE UNCERTAIN"],
    routing="STANDARD BIOMEDICAL ADJUDICATION",
    label="overclaim",
    alt_label=None,
    alt_rationale="No specific frozen label applies; the error is asserting a "
                  "production-rate change from a single uncontrolled "
                  "time-profile observation.",
    confidence=0.88,
    strength="not_directly_established",
    overlay="OVERCLAIM",
    claim_strength="STRONG AND PHYSIOLOGICALLY SPECIFIC — names cortisol "
                   "production rather than a subjective state.",
    verdict_summary="The entire evidence base for this claim is one "
                    "uncontrolled 12-participant study reporting a night-time "
                    "salivary cortisol pattern change. A time-specific salivary "
                    "profile is not a measure of cortisol production, and no "
                    "controlled independent replication exists.",
    evidence_tier="biomarker",
    conclusion_tier="human_therapeutic",
    bridge_supported=False,
    items=[
        dict(text="Ghaly & Teplitz 2004: uncontrolled n=12 with sleep "
                  "dysfunction, pain and stress; night cortisol pattern and "
                  "subjective measures reportedly improved over 8 weeks.",
             source_reference="H02", tier="biomarker", role="supporting",
             why_it_matters="The only direct evidence for this proposition; no "
                            "control group, no blinding and no validated "
                            "endpoint."),
        dict(text="A time-specific salivary cortisol profile is not equivalent "
                  "to general cortisol production; the prohibited transition is "
                  "pattern to general production lowering.",
             source_reference="Freeze sections 36/54/58", tier="not_applicable",
             role="missing_expected",
             why_it_matters="The endpoint the wording names was not measured."),
        dict(text="No controlled independent replication of the H02 cortisol "
                  "observation was located.",
             source_reference="Freeze sections 51/60", tier="not_applicable",
             role="missing_expected",
             why_it_matters="A single uncontrolled result carries no "
                            "replication support."),
    ],
    supporting=["H02 night-time salivary cortisol pattern change (uncontrolled, "
                "n=12)"],
    contra=["No control group; time, regression and expectancy confounding",
            "Salivary time profile is not cortisol production rate",
            "No controlled independent replication"],
    missing_comparison_group=True,
    missing_causal_chain=False,
    missing_human_evidence=False,
    sufficiency="insufficient",
    sufficiency_rationale="One uncontrolled 12-participant observation cannot "
                          "support a physiological production claim.",
    failure_modes=[
        dict(mode="missing_comparison_group",
             rationale="The sole supporting study has no control arm; observed "
                       "change cannot be separated from time, regression or "
                       "expectancy.",
             evidence_refs=["H02"]),
        dict(mode="conclusion_exceeds_results",
             rationale="A change in a night-time salivary profile is presented "
                       "as lowered cortisol production.",
             evidence_refs=["H02", "Freeze sections 54/58"]),
        dict(mode="evidence_tier_mismatch",
             rationale="An uncontrolled biomarker observation is offered for a "
                       "specific physiological production claim.",
             evidence_refs=["H02"]),
    ],
    risk="moderate",
    risk_rationale="Cortisol language carries clinical authority disproportionate "
                   "to a single uncontrolled observation.",
    reader_misunderstanding="That the product measurably lowers a stress "
                            "hormone.",
    affected_decision="Purchase on physiological grounds.",
    directness="VERY LIMITED — one uncontrolled human observation.",
    endpoint_fidelity="LOW — salivary cortisol profile, not production rate.",
    population_fidelity="A single n=12 sleep, pain and stress sample.",
    timeframe_fidelity="One 8-week uncontrolled profile; no durable "
                       "replication.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — H02 pad equivalence not "
                     "established.",
    causality_boundary="An uncontrolled time-profile change cannot establish "
                       "general production lowering.",
    replication="No controlled independent replication of H02.",
    steelman="Strongest legitimate reading: H02 measured an objective "
             "biomarker rather than only self-report, over eight weeks, in a "
             "symptomatic population, and reported a coherent change in the "
             "expected direction alongside subjective improvement.",
    steelman_result="FAILS — an uncontrolled single study cannot support a "
                    "specific physiological production claim.",
    adversarial="The claim rests on one arm of twelve people with no "
                "comparator, and it misnames the endpoint: a night-time "
                "salivary pattern is not production.",
    adversarial_result="SUSTAINED.",
    divergence="NONE MATERIAL.",
    residual_uncertainty="A controlled circadian-cortisol replication with "
                         "curve analysis and a clinical link has not been done.",
    rationale="Two independent defects decide this: the sole supporting study "
              "has no comparison group, and the measured quantity is not the "
              "quantity the wording names. VERY LIMITED DIRECT EVIDENCE is the "
              "input state, not the verdict; the verdict follows from the "
              "endpoint mismatch and the absence of any controlled evidence.",
),
]

PROPOSITIONS += [

dict(
    pid="P-01",
    proposition="Premium Grounding reduces aches and pain.",
    origin="F02/F04",
    ptype="EXPLICIT; SUBJECTIVE; THERAPEUTIC; PRODUCT-SPECIFIC",
    prep_state="SOME DIRECT EVIDENCE LOCATED",
    mechanism_state=None,
    qualifiers=["CONDITION/TIMEFRAME MISMATCH", "PRODUCT EQUIVALENCE UNCERTAIN"],
    routing="STANDARD BIOMEDICAL ADJUDICATION",
    label="overclaim",
    alt_label="solid",
    alt_rationale="A solid reading was seriously considered and is recorded as "
                  "the documented alternative: H31 is the strongest direct "
                  "efficacy signal in the substrate. It is rejected as primary "
                  "because the advertised wording is unqualified and sits "
                  "beside a list of chronic conditions none of the evidence "
                  "addresses.",
    confidence=0.78,
    strength="limited_support",
    overlay="QUALIFIED",
    claim_strength="STRONG AND BROAD as advertised — 'reducing pain' placed "
                   "beside arthritis, back pain, neck aches and headaches.",
    verdict_summary="This is the advertised outcome with the strongest direct "
                    "human evidence: a randomised sham-controlled trial in 84 "
                    "post-lumbar-surgery patients found a VAS mean change of "
                    "2.50 versus 1.5952, exact p=.010511. That supports a "
                    "bounded conclusion in acute induced, occupational and "
                    "postoperative contexts only. It does not support the broad "
                    "chronic-pain framing the advertisement uses, and the trial "
                    "reports no confidence interval and no formal minimal "
                    "clinically important difference.",
    evidence_tier="limited_human",
    conclusion_tier="human_therapeutic",
    bridge_supported=False,
    items=[
        dict(text="Sokal et al. 2025: randomised, 42 active versus 42 sham "
                  "ankle pads for one postoperative night with paracetamol for "
                  "all. VAS mean change 2.50 versus 1.5952, exact p=.010511. "
                  "Table 2 medians 2.5 versus 1; narrative and abstract give "
                  "2.0 versus 1.",
             source_reference="H31", tier="limited_human", role="supporting",
             why_it_matters="The strongest direct human efficacy signal "
                            "located. The exact p-value is .010511 — "
                            "significant at the .05 level, NOT at .01. Summary "
                            "statistics conflict across the paper."),
        dict(text="Brown, Chevalier & Hill 2015 (randomised double-blind, 16 "
                  "active/16 sham) and Chevalier et al. 2019 (16 massage "
                  "therapists) report pain and soreness signals.",
             source_reference="H16/H22", tier="limited_human", role="supporting",
             why_it_matters="Induced-soreness and occupational contexts; H22 "
                            "shares its cohort with H21."),
        dict(text="Brown, Chevalier & Hill 2015 reported pain occurring in both "
                  "groups, with isolated biomarker differences among many "
                  "outcomes and timepoints.",
             source_reference="H16", tier="limited_human", role="contradictory",
             why_it_matters="The induced-soreness line does not show a clean "
                            "pain benefit."),
        dict(text="Sokal et al. 2025 CK mean change 54.619 versus 40.5 U/L, "
                  "p=.534106 — not significantly different between groups.",
             source_reference="H31", tier="biomarker", role="weakening",
             why_it_matters="The muscle-damage biomarker in the same trial "
                            "showed no group difference, so a coherent "
                            "mechanistic story is not established."),
        dict(text="No condition-specific chronic-pain RCT with a minimal "
                  "clinically important difference, medication use and "
                  "follow-up was located; no registration was located for H31.",
             source_reference="Freeze sections 32/55/63", tier="not_applicable",
             role="missing_expected",
             why_it_matters="The advertised chronic-pain framing has no "
                            "supporting trial, and the strongest study lacks "
                            "prespecification."),
    ],
    supporting=["H31 postoperative VAS, exact p=.010511 (randomised, sham, n=84)",
                "H16 induced-soreness signals", "H22 occupational pain signals"],
    contra=["H16 pain occurred in both groups; extreme multiplicity",
            "H31 CK p=.534106; no CI, no MCID, no registration located",
            "No chronic or condition-specific pain trial",
            "Acute induced, occupational and postoperative models do not "
            "transfer to arthritis, back, neck or headache pain"],
    missing_comparison_group=False,
    missing_causal_chain=False,
    missing_human_evidence=False,
    sufficiency="insufficient",
    sufficiency_rationale="Sufficient for a bounded acute-context statement; "
                          "insufficient for the advertised general and chronic "
                          "pain claim.",
    failure_modes=[
        dict(mode="inappropriate_generalization",
             rationale="Evidence from one postoperative night, induced muscle "
                       "soreness in healthy young men and 16 massage therapists "
                       "is extended to general and chronic pain across four "
                       "named conditions.",
             evidence_refs=["H31", "H16", "H22"]),
        dict(mode="conclusion_exceeds_results",
             rationale="An unqualified pain-reduction benefit is advertised "
                       "from a single significant acute result that reports no "
                       "confidence interval and no clinical-relevance "
                       "threshold.",
             evidence_refs=["H31"]),
    ],
    risk="high",
    risk_rationale="Pain is the second advertised benefit and is paired with "
                   "chronic conditions; readers may defer treatment.",
    reader_misunderstanding="That a demonstrated acute postoperative effect "
                            "means the product treats their chronic pain.",
    affected_decision="Chronic pain management and care seeking.",
    directness="DIRECT within narrow acute contexts.",
    endpoint_fidelity="MODERATE — VAS and DOMS pain are relevant in the "
                      "contexts studied; not broad chronic pain.",
    population_fidelity="LOW for the advertised audience — healthy DOMS "
                        "participants, bodyworkers and postoperative patients.",
    timeframe_fidelity="LOW — hours to four days and occupational weeks; "
                       "chronic durability absent.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — patch, sheet and mat "
                     "analogues across narrow pain models.",
    causality_boundary="Narrow contexts and cointerventions block broad pain "
                       "causality.",
    replication="Several pain contexts and groups; no same-condition or "
                "same-protocol replication.",
    steelman="Strongest legitimate reading: H31 is a randomised, sham-"
             "controlled trial with 84 participants, an adequate active "
             "comparator design and a statistically significant result on the "
             "primary pain measure. It is genuine direct human efficacy "
             "evidence and dismissing it would be over-scepticism. Within "
             "acute postoperative and induced-soreness contexts, a bounded "
             "pain effect has real support.",
    steelman_result="SURVIVES IN BOUNDED FORM — this is the basis for the "
                    "QUALIFIED verdict rather than an unsupported one.",
    adversarial="The significant result carries no confidence interval and no "
                "MCID, so clinical relevance is unknown; the same trial's "
                "muscle-damage biomarker was null; the paper's own summary "
                "statistics conflict; no registration was located; and none of "
                "the evidence touches the chronic conditions the advertisement "
                "names.",
    adversarial_result="SUSTAINED against the advertised breadth; does not "
                       "defeat the bounded acute finding.",
    divergence="MATERIAL AND DECISIVE — the Steelman layer established genuine "
               "bounded efficacy evidence while the adversarial layer "
               "established that the advertised framing is far broader than "
               "that evidence. Resolved as QUALIFIED: supported within "
               "documented acute bounds, not supported as advertised.",
    residual_uncertainty="Clinical relevance of the H31 effect is unknown "
                         "without a CI or MCID; no chronic-pain trial exists.",
    rationale="This is the one proposition where a randomised sham-controlled "
              "human trial reports a significant effect on the endpoint the "
              "claim names, so the evidence is neither absent nor purely "
              "surrogate. The exact p-value is preserved as .010511 rather than "
              "the historical p<.01. The verdict is QUALIFIED because support "
              "exists strictly within acute postoperative, induced-soreness and "
              "occupational bounds, while the advertised wording is "
              "unqualified and appears beside chronic conditions for which no "
              "evidence was located.",
),

dict(
    pid="P-02",
    proposition="Premium Grounding is relevant to/alleviates arthritis.",
    origin="F02 in context",
    ptype="IMPLIED; THERAPEUTIC; CONDITION-SPECIFIC; PRODUCT-SPECIFIC",
    prep_state="NO MATERIAL DIRECT EVIDENCE LOCATED",
    mechanism_state=None,
    qualifiers=["BOUNDED NEGATIVE SEARCH", "PRODUCT EQUIVALENCE UNCERTAIN"],
    routing="BOUNDED NEGATIVE SEARCH — proposition-specific negative-search work "
            "documented and confirmed at class A after expanded terminology.",
    label="overclaim",
    alt_label=None,
    alt_rationale="No specific frozen label applies; the error is implying "
                  "relevance to a named disease with no qualifying study.",
    confidence=0.90,
    strength="not_supported",
    overlay="UNSUPPORTED",
    claim_strength="STRONG BY PLACEMENT — a named rheumatological disease in "
                   "the 'Do you suffer from any of these?' list.",
    verdict_summary="No human Earth-contact or grounding intervention study "
                    "with an arthritis-relevant clinical or functional endpoint "
                    "was located, after the most extensive proposition-specific "
                    "search in the case. Candidate barefoot-gait records were "
                    "excluded because they involve no conductive Earth contact.",
    evidence_tier="not_applicable",
    conclusion_tier="human_therapeutic",
    bridge_supported=False,
    items=[
        dict(text="Only nonspecific pain and inflammatory surrogates exist; no "
                  "arthritis-specific trial was located.",
             source_reference="Freeze sections 50/52", tier="biomarker",
             role="supporting",
             why_it_matters="The nearest available material is generic and "
                            "does not address arthritis disease activity, "
                            "function or progression."),
        dict(text="Shakoor & Block 2006 barefoot knee-osteoarthritis gait, "
                  "Neogi et al. 2021 barefoot exposure and unstable-footwear "
                  "studies were screened and excluded: ordinary gait, footwear "
                  "or observational exposure with no conductive Earth or "
                  "earthing intervention.",
             source_reference="Freeze section 71", tier="not_applicable",
             role="weakening",
             why_it_matters="Documents that the closest candidate records were "
                            "inspected and are ineligible, rather than "
                            "overlooked."),
        dict(text="Documented proposition-specific search across PubMed "
                  "(140 found/25 screened), Europe PMC title/abstract (140/25) "
                  "and full text (479/25) and OpenAlex (62 deduplicated), with "
                  "grounding, earthing, barefoot, soil-contact and Earth-contact "
                  "terminology to the 22 August 2026 cut-off: class A, negative "
                  "search state confirmed.",
             source_reference="Freeze sections 19/70/73", tier="not_applicable",
             role="missing_expected",
             why_it_matters="Establishes the breadth of the documented basis "
                            "for the negative statement."),
        dict(text="Arthritis disease-activity, function and progression "
                  "endpoints are absent from the entire evidence base.",
             source_reference="Freeze sections 54/55", tier="not_applicable",
             role="missing_expected",
             why_it_matters="No endpoint capable of supporting the claim was "
                            "ever measured."),
    ],
    supporting=["Nonspecific pain and inflammatory surrogates only"],
    contra=["No arthritis Earth-contact or grounding trial located",
            "Closest candidates excluded for absence of conductive Earth contact",
            "Arthritis endpoints absent from the whole evidence base"],
    missing_comparison_group=False,
    missing_causal_chain=False,
    missing_human_evidence=True,
    sufficiency="insufficient",
    sufficiency_rationale="No qualifying study exists within the documented "
                          "search routes and terminology.",
    failure_modes=[
        dict(mode="inappropriate_generalization",
             rationale="Generic pain and inflammation material is extended to a "
                       "named rheumatological disease that was never studied.",
             evidence_refs=["Freeze sections 50/52"]),
        dict(mode="missing_human_evidence",
             rationale="No human Earth-contact intervention study with an "
                       "arthritis-relevant endpoint was located.",
             evidence_refs=["Freeze sections 19/70/73"]),
    ],
    risk="high",
    risk_rationale="Arthritis is a progressive disease with effective "
                   "treatments; implied relevance may delay rheumatological "
                   "care.",
    reader_misunderstanding="That grounding is an evidence-based option for "
                            "arthritis.",
    affected_decision="Whether to seek or continue arthritis treatment.",
    directness="ABSENT — no direct eligible trial.",
    endpoint_fidelity="ENDPOINT ABSENT — no arthritis activity, function or "
                      "progression measure.",
    population_fidelity="ABSENT — arthritis types, severity and treatments "
                        "unrepresented.",
    timeframe_fidelity="NOT APPLICABLE — no direct timeframe.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — no product or condition "
                     "match.",
    causality_boundary="No direct causal contrast exists.",
    replication="None.",
    steelman="Strongest legitimate reading: arthritis is an inflammatory "
             "condition, some grounding studies report inflammatory-marker "
             "movement, and H31 showed a real acute pain effect. A "
             "mechanistically motivated expectation of benefit is not "
             "unreasonable.",
    steelman_result="FAILS — a mechanistic expectation is not condition "
                    "evidence, and the inflammation line is itself surrogate "
                    "only (see I-01).",
    adversarial="The most thorough search in the entire case, extended with "
                "barefoot and Earth-contact terminology specifically to guard "
                "against the indexing failure that had hidden H33, still found "
                "nothing eligible.",
    adversarial_result="SUSTAINED.",
    divergence="NONE MATERIAL.",
    residual_uncertainty="An arthritis RCT measuring disease activity, pain, "
                         "function and harms has not been performed. The "
                         "absence is a bounded retrieval finding within the "
                         "documented routes and terminology, not proof that no "
                         "relevant study exists.",
    rationale="NO MATERIAL DIRECT EVIDENCE LOCATED is not read as an automatic "
              "UNSUPPORTED. The verdict is reached because this proposition "
              "received documented, proposition-specific negative-search work "
              "that was deliberately hardened against terminology drift and "
              "still confirmed the negative state at class A, because the "
              "closest candidate records were inspected and are ineligible, "
              "and because no arthritis endpoint exists anywhere in the "
              "substrate. The negative statement is reported at the breadth of "
              "its documented basis only.",
),
]

PROPOSITIONS += [

dict(
    pid="P-03",
    proposition="Premium Grounding reduces muscle stiffness.",
    origin="F02 in context",
    ptype="IMPLIED; THERAPEUTIC; CONDITION-SPECIFIC; PRODUCT-SPECIFIC",
    prep_state="VERY LIMITED DIRECT EVIDENCE",
    mechanism_state=None,
    qualifiers=["REPORTING-SENSITIVE", "REPLICATION ABSENT",
                "PRODUCT EQUIVALENCE UNCERTAIN"],
    routing="STANDARD BIOMEDICAL ADJUDICATION",
    label="overclaim",
    alt_label=None,
    alt_rationale="No specific frozen label applies; the error is asserting an "
                  "effect on the strength of a grey report with internal "
                  "denominator conflicts and no validated endpoint.",
    confidence=0.85,
    strength="not_directly_established",
    overlay="OVERCLAIM",
    claim_strength="MODERATE-STRONG — a named symptom in the condition list.",
    verdict_summary="The only direct support is a grey trade-journal report "
                    "whose recruitment total (60) conflicts with its own "
                    "outcome-table total (50), which used no validated "
                    "stiffness instrument and has never been replicated.",
    evidence_tier="limited_human",
    conclusion_tier="human_therapeutic",
    bridge_supported=False,
    items=[
        dict(text="Ober 2000, ESD Journal grey report: grounded conductive "
                  "sleep pad versus ungrounded/sham over one month, with large "
                  "subjective sleep, stiffness and pain percentages. 60 said "
                  "recruited but outcome-table totals reach 50.",
             source_reference="H01", tier="limited_human", role="supporting",
             why_it_matters="The only direct stiffness observation; a grey "
                            "report with a denominator conflict and no reported "
                            "allocation or validated-scale detail."),
        dict(text="Delayed-onset-muscle-soreness work provides indirect "
                  "mechanism context only.",
             source_reference="H06/H16", tier="limited_human", role="supporting",
             why_it_matters="Induced soreness in healthy young men is not the "
                            "advertised muscle-stiffness complaint."),
        dict(text="No validated stiffness endpoint in a defined population, and "
                  "no replication of H01, were located.",
             source_reference="Freeze sections 54/55/60", tier="not_applicable",
             role="missing_expected",
             why_it_matters="Neither a measurement instrument nor an "
                            "independent confirmation exists."),
    ],
    supporting=["H01 grey subjective stiffness report",
                "H06/H16 induced-soreness work (indirect)"],
    contra=["H01 denominator conflict (60 recruited versus 50 in the table)",
            "No validated stiffness outcome instrument",
            "No replication beyond the grey report"],
    missing_comparison_group=False,
    missing_causal_chain=False,
    missing_human_evidence=False,
    sufficiency="insufficient",
    sufficiency_rationale="A single grey report with unresolved internal "
                          "arithmetic and no validated endpoint cannot support "
                          "a therapeutic claim.",
    failure_modes=[
        dict(mode="conclusion_exceeds_results",
             rationale="A symptom benefit is asserted from a grey report whose "
                       "own participant totals conflict and which used no "
                       "validated stiffness measure.",
             evidence_refs=["H01"]),
        dict(mode="inappropriate_generalization",
             rationale="Induced muscle soreness in healthy young men is "
                       "extended to general muscle stiffness in the advertised "
                       "audience.",
             evidence_refs=["H06/H16"]),
    ],
    risk="moderate",
    risk_rationale="Muscle stiffness is usually benign; the main risk is "
                   "misplaced purchase reliance.",
    reader_misunderstanding="That a measured, reliable stiffness benefit exists.",
    affected_decision="Purchase for musculoskeletal complaints.",
    directness="VERY LIMITED — one grey subjective report.",
    endpoint_fidelity="LOW — no validated stiffness endpoint.",
    population_fidelity="Undefined stiffness population.",
    timeframe_fidelity="One grey one-month report only.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — grey pad specification "
                     "absent.",
    causality_boundary="Grey, uncontrolled and unclear methods.",
    replication="None beyond the grey report.",
    steelman="Strongest legitimate reading: H01 did use an ungrounded sham "
             "comparator and reported large subjective improvements, and "
             "delayed-onset-soreness work supplies a plausible mechanism for "
             "reduced stiffness after exertion.",
    steelman_result="FAILS — the sham design cannot rescue a report whose own "
                    "participant totals do not reconcile and which used no "
                    "validated instrument.",
    adversarial="The evidence is a trade-journal report that cannot account for "
                "ten of its own participants, with no validated scale and no "
                "independent confirmation in 26 years.",
    adversarial_result="SUSTAINED.",
    divergence="NONE MATERIAL.",
    residual_uncertainty="A validated stiffness endpoint in a defined "
                         "population has never been measured.",
    rationale="The proposition fails on evidence quality rather than absence: "
              "direct material exists but is a grey report with unreconciled "
              "denominators, no validated instrument and no replication, "
              "against which an unqualified symptom benefit is advertised.",
),

dict(
    pid="P-04",
    proposition="Premium Grounding reduces back and neck pain.",
    origin="F02 in context",
    ptype="IMPLIED; THERAPEUTIC; CONDITION-SPECIFIC; PRODUCT-SPECIFIC",
    prep_state="VERY LIMITED DIRECT EVIDENCE",
    mechanism_state=None,
    qualifiers=["HIGH CONFOUNDING", "CONDITION MISMATCH",
                "PRODUCT EQUIVALENCE UNCERTAIN"],
    routing="STANDARD BIOMEDICAL ADJUDICATION",
    label="overclaim",
    alt_label=None,
    alt_rationale="No specific frozen label applies; the error combines "
                  "cointervention confounding with condition drift.",
    confidence=0.87,
    strength="not_directly_established",
    overlay="OVERCLAIM",
    claim_strength="MODERATE-STRONG — two distinct named conditions ('back "
                   "pain', 'Neck aches') in the condition list.",
    verdict_summary="Back pain is addressed only by a 12-participant grey "
                    "report in which both arms received massage, and by an "
                    "acute postoperative lumbar context that is not chronic "
                    "back pain. No neck-pain study of any kind was located.",
    evidence_tier="limited_human",
    conclusion_tier="human_therapeutic",
    bridge_supported=False,
    items=[
        dict(text="2021 Jing massage-plus-earthing grey report, n=12 with "
                  "chronic low-back pain: massage in both arms plus grounded "
                  "versus sham sleep; pain reduction 38 percent versus 17 "
                  "percent reported.",
             source_reference="H25", tier="limited_human", role="supporting",
             why_it_matters="Tiny, grey, with an active cointervention in both "
                            "arms and uncertain publication and method status; "
                            "retained as context only."),
        dict(text="Sokal et al. 2025 concerns post-lumbar-surgery recovery, an "
                  "acute surgical context rather than chronic back pain.",
             source_reference="H31", tier="limited_human", role="supporting",
             why_it_matters="Anatomically adjacent but a different clinical "
                            "condition and timeframe."),
        dict(text="No separate neck-pain trial was located.",
             source_reference="Freeze sections 51/52", tier="not_applicable",
             role="missing_expected",
             why_it_matters="One of the two advertised conditions has no "
                            "evidence at all."),
        dict(text="No back or neck trial without confounded cointerventions "
                  "was located.",
             source_reference="Freeze section 63", tier="not_applicable",
             role="missing_expected",
             why_it_matters="The one back-pain observation cannot separate "
                            "grounding from massage."),
    ],
    supporting=["H25 grey low-back report with massage in both arms",
                "H31 postoperative lumbar context (indirect)"],
    contra=["H25 massage cointervention and uncertain method status",
            "No separate neck-pain trial exists",
            "Postoperative acute pain is not chronic back or neck pain"],
    missing_comparison_group=False,
    missing_causal_chain=False,
    missing_human_evidence=False,
    sufficiency="insufficient",
    sufficiency_rationale="One confounded grey observation for back pain and no "
                          "evidence at all for neck pain.",
    failure_modes=[
        dict(mode="conclusion_exceeds_results",
             rationale="A benefit for two named chronic conditions is implied "
                       "from a 12-participant grey report with an active "
                       "cointervention and an acute postoperative trial.",
             evidence_refs=["H25", "H31"]),
        dict(mode="inappropriate_generalization",
             rationale="Acute postoperative lumbar pain is extended to chronic "
                       "back pain and to neck pain, for which nothing was "
                       "located.",
             evidence_refs=["H31"]),
    ],
    risk="high",
    risk_rationale="Chronic back and neck pain are common reasons to seek "
                   "care; implied relevance may delay assessment.",
    reader_misunderstanding="That the product is an evidence-based option for "
                            "back or neck pain.",
    affected_decision="Chronic spinal pain management.",
    directness="VERY LIMITED for back pain; ABSENT for neck pain.",
    endpoint_fidelity="LOW — low-back and postoperative pain do not cover "
                      "separate chronic back and neck conditions.",
    population_fidelity="Low-back and postoperative groups only.",
    timeframe_fidelity="Six massage sessions or one postoperative night; "
                       "chronic timeframe mismatch.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — cointervention and "
                     "postoperative patch are not the advertised product.",
    causality_boundary="Massage and surgical cointerventions plus condition "
                       "drift block causal attribution.",
    replication="No independent same-condition or same-protocol replication.",
    steelman="Strongest legitimate reading: H25 reported more than double the "
             "pain reduction in the grounded arm (38 versus 17 percent) with "
             "massage held constant across arms, which is the correct design "
             "logic for isolating the added component, and H31 shows grounding "
             "can affect pain in a spinal-surgery population.",
    steelman_result="FAILS — the design logic is sound but the sample is twelve "
                    "people in an incompletely reported grey document, and neck "
                    "pain remains entirely unstudied.",
    adversarial="The advertisement names two conditions. One rests on a "
                "12-participant grey report of uncertain publication status; "
                "the other rests on nothing.",
    adversarial_result="SUSTAINED.",
    divergence="NONE MATERIAL.",
    residual_uncertainty="Separate back and neck trials without confounded "
                         "cointerventions have not been performed.",
    rationale="The proposition bundles two named conditions. For back pain the "
              "only direct material is a tiny grey report with an active "
              "cointervention in both arms and uncertain methods; for neck pain "
              "there is no evidence whatever. The advertised implication of "
              "relevance to both exceeds this substantially.",
),

dict(
    pid="P-05",
    proposition="Premium Grounding is relevant to/alleviates headaches.",
    origin="F02 in context",
    ptype="IMPLIED; THERAPEUTIC; CONDITION-SPECIFIC; PRODUCT-SPECIFIC",
    prep_state="NO MATERIAL DIRECT EVIDENCE LOCATED",
    mechanism_state=None,
    qualifiers=["BOUNDED NEGATIVE SEARCH", "PRODUCT EQUIVALENCE UNCERTAIN"],
    routing="BOUNDED NEGATIVE SEARCH — proposition-specific negative-search work "
            "documented and confirmed at class A after expanded terminology.",
    label="overclaim",
    alt_label=None,
    alt_rationale="No specific frozen label applies; the error is implying "
                  "relevance to a named condition with no qualifying study.",
    confidence=0.90,
    strength="not_supported",
    overlay="UNSUPPORTED",
    claim_strength="MODERATE-STRONG — a named condition in the 'Do you suffer "
                   "from any of these?' list.",
    verdict_summary="No headache-specific human grounding or Earth-contact "
                    "intervention study was located. Screened candidates were "
                    "natural-environment exercise, aerobic walking and "
                    "foot-reflexology migraine studies, none of which involves "
                    "conductive Earth contact with a qualifying endpoint.",
    evidence_tier="not_applicable",
    conclusion_tier="human_therapeutic",
    bridge_supported=False,
    items=[
        dict(text="No headache-specific human grounding study was located.",
             source_reference="Freeze section 50", tier="not_applicable",
             role="missing_expected",
             why_it_matters="There is no supporting evidence line at all for "
                            "this proposition."),
        dict(text="Screened and excluded: natural-environment exercise, aerobic "
                  "walking and foot-reflexology migraine studies, plus "
                  "incidental earthing records — no barefoot Earth-contact "
                  "migraine intervention or qualifying endpoint combination.",
             source_reference="Freeze section 71", tier="not_applicable",
             role="weakening",
             why_it_matters="Documents that near-miss candidates were inspected "
                            "and are ineligible."),
        dict(text="Documented proposition-specific search across PubMed "
                  "(5 found/5 screened), Europe PMC title/abstract (6/6) and "
                  "full text (40/25) and OpenAlex (46 deduplicated) with "
                  "grounding, earthing, barefoot, soil-contact and Earth-contact "
                  "terminology to the 22 August 2026 cut-off: class A, negative "
                  "search state confirmed.",
             source_reference="Freeze sections 19/70/73", tier="not_applicable",
             role="missing_expected",
             why_it_matters="Establishes the breadth of the documented basis "
                            "for the negative statement."),
        dict(text="Headache frequency, intensity, disability and medication "
                  "endpoints are absent from the entire evidence base.",
             source_reference="Freeze section 54", tier="not_applicable",
             role="missing_expected",
             why_it_matters="No endpoint capable of supporting the claim was "
                            "ever measured."),
    ],
    supporting=[],
    contra=["No headache-specific human grounding study located",
            "Near-miss candidates excluded for absence of Earth contact",
            "Headache endpoints absent from the whole evidence base"],
    missing_comparison_group=False,
    missing_causal_chain=False,
    missing_human_evidence=True,
    sufficiency="insufficient",
    sufficiency_rationale="No qualifying study exists within the documented "
                          "search routes and terminology.",
    failure_modes=[
        dict(mode="missing_human_evidence",
             rationale="No human Earth-contact intervention study with a "
                       "headache-relevant endpoint was located.",
             evidence_refs=["Freeze sections 19/70/73"]),
        dict(mode="conclusion_exceeds_results",
             rationale="Relevance to a named condition is implied where no "
                       "supporting evidence line exists at all.",
             evidence_refs=["Freeze section 50"]),
    ],
    risk="high",
    risk_rationale="Headache and migraine have effective treatments and can "
                   "signal serious disease; implied relevance may delay care.",
    reader_misunderstanding="That grounding is a recognised option for "
                            "headaches or migraine.",
    affected_decision="Whether to seek assessment or treatment for headaches.",
    directness="ABSENT — no direct eligible trial.",
    endpoint_fidelity="ENDPOINT ABSENT — no frequency, intensity, disability or "
                      "medication measure.",
    population_fidelity="ABSENT — headache types and aetiologies unrepresented.",
    timeframe_fidelity="NOT APPLICABLE — no direct timeframe.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — no study or product "
                     "match.",
    causality_boundary="No direct causal contrast exists.",
    replication="None.",
    steelman="Strongest legitimate reading: headache can be stress- and "
             "sleep-related, and grounding studies report changes in both "
             "domains, so an indirect pathway to headache relief is not "
             "incoherent.",
    steelman_result="FAILS — an indirect pathway argument is not condition "
                    "evidence, and the stress and sleep lines it depends on are "
                    "themselves mixed (S-01, S-03).",
    adversarial="A documented multi-route search hardened with barefoot and "
                "Earth-contact terminology returned nothing eligible, and no "
                "headache endpoint exists anywhere in the substrate.",
    adversarial_result="SUSTAINED.",
    divergence="NONE MATERIAL.",
    residual_uncertainty="A headache-type trial with frequency, intensity and "
                         "disability endpoints has not been performed. The "
                         "absence is a bounded retrieval finding within the "
                         "documented routes and terminology, not proof that no "
                         "relevant study exists.",
    rationale="The verdict rests on documented, proposition-specific "
              "negative-search work confirmed at class A after deliberate "
              "terminology hardening, on the inspection and exclusion of "
              "near-miss candidates, and on the complete absence of any "
              "headache endpoint in the substrate — not on a mechanical "
              "reading of the preparation state.",
),
]

PROPOSITIONS += [

dict(
    pid="V-01",
    proposition="Premium Grounding is relevant to/alleviates varicose veins.",
    origin="F02 in context",
    ptype="IMPLIED; THERAPEUTIC; CONDITION-SPECIFIC; PRODUCT-SPECIFIC",
    prep_state="NO MATERIAL DIRECT EVIDENCE LOCATED",
    mechanism_state=None,
    qualifiers=["BOUNDED NEGATIVE SEARCH", "PRODUCT EQUIVALENCE UNCERTAIN"],
    routing="BOUNDED NEGATIVE SEARCH — proposition-specific negative-search work "
            "documented and confirmed at class A after expanded terminology.",
    label="overclaim",
    alt_label=None,
    alt_rationale="No specific frozen label applies; the error is implying "
                  "relevance to a structural vascular disease using perfusion "
                  "and viscosity surrogates.",
    confidence=0.91,
    strength="not_supported",
    overlay="UNSUPPORTED",
    claim_strength="MODERATE-STRONG — a named vascular disease in the condition "
                   "list.",
    verdict_summary="No varicose-vein or venous-insufficiency grounding trial "
                    "was located. The available perfusion, viscosity and "
                    "plantar-pump material is indirect and cannot speak to "
                    "venous valve anatomy, reflux or disease progression.",
    evidence_tier="biomarker",
    conclusion_tier="human_therapeutic",
    bridge_supported=False,
    items=[
        dict(text="Perfusion, blood-viscosity, zeta-potential and plantar-pump "
                  "material is indirect only.",
             source_reference="H10/H13/H17", tier="biomarker", role="supporting",
             why_it_matters="Acute haemodynamic surrogates that do not address "
                            "venous valve anatomy, reflux or symptoms."),
        dict(text="Tsimba et al. 2023 barefoot treadmill plantar venous-pump "
                  "study was screened and excluded: healthy volunteers, "
                  "treadmill surface, no Earth contact and no venous-disease "
                  "treatment endpoint.",
             source_reference="Freeze section 71", tier="not_applicable",
             role="weakening",
             why_it_matters="The single closest candidate was inspected and is "
                            "ineligible on both intervention and endpoint."),
        dict(text="Documented proposition-specific search across PubMed "
                  "(1 found/1 screened), Europe PMC title/abstract (1/1) and "
                  "full text (6/6) and OpenAlex (34 deduplicated) with "
                  "grounding, earthing, barefoot, soil-contact and Earth-contact "
                  "terminology to the 22 August 2026 cut-off: class A, negative "
                  "search state confirmed.",
             source_reference="Freeze sections 19/70/73", tier="not_applicable",
             role="missing_expected",
             why_it_matters="Establishes the breadth of the documented basis "
                            "for the negative statement."),
        dict(text="Varicose symptoms, duplex anatomy, reflux and progression "
                  "endpoints are absent from the entire evidence base.",
             source_reference="Freeze section 54", tier="not_applicable",
             role="missing_expected",
             why_it_matters="No endpoint capable of supporting the claim was "
                            "ever measured."),
    ],
    supporting=["Perfusion, viscosity and plantar-pump surrogates (indirect)"],
    contra=["No varicose-vein or venous-insufficiency grounding trial located",
            "Tsimba 2023 excluded: no Earth contact, no venous-disease endpoint",
            "Surrogates cannot show anatomy, reflux or symptom change"],
    missing_comparison_group=False,
    missing_causal_chain=False,
    missing_human_evidence=True,
    sufficiency="insufficient",
    sufficiency_rationale="No qualifying study exists within the documented "
                          "search routes and terminology, and surrogates cannot "
                          "substitute for a structural vascular endpoint.",
    failure_modes=[
        dict(mode="evidence_tier_mismatch",
             rationale="Acute haemodynamic surrogates are offered for a "
                       "structural venous disease claim.",
             evidence_refs=["H10/H13/H17"]),
        dict(mode="missing_human_evidence",
             rationale="No human Earth-contact intervention study with a "
                       "venous-disease endpoint was located.",
             evidence_refs=["Freeze sections 19/70/73"]),
    ],
    risk="high",
    risk_rationale="Varicose veins and venous insufficiency are progressive "
                   "vascular conditions requiring assessment; implied relevance "
                   "may delay care.",
    reader_misunderstanding="That grounding addresses varicose veins.",
    affected_decision="Whether to seek vascular assessment.",
    directness="ABSENT — no direct eligible trial.",
    endpoint_fidelity="ENDPOINT ABSENT — no symptom, duplex, reflux or "
                      "progression measure.",
    population_fidelity="ABSENT — venous-disease population unrepresented.",
    timeframe_fidelity="NOT APPLICABLE — no direct timeframe.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — no study or product "
                     "match.",
    causality_boundary="No direct causal contrast; surrogates do not establish "
                       "venous-disease change.",
    replication="None.",
    steelman="Strongest legitimate reading: grounding studies do report changes "
             "in blood viscosity and peripheral perfusion, and venous return is "
             "a haemodynamic process, so a mechanistic story connecting the two "
             "can be told.",
    steelman_result="FAILS — varicose veins are a structural valve disorder; "
                    "acute rheological change in healthy volunteers cannot "
                    "address it, and no study tried.",
    adversarial="The one candidate record involved a treadmill rather than "
                "Earth contact and healthy volunteers rather than patients. "
                "The claim reaches a structural vascular disease from acute "
                "blood-property surrogates.",
    adversarial_result="SUSTAINED.",
    divergence="NONE MATERIAL.",
    residual_uncertainty="A venous-disease trial with duplex, anatomical and "
                         "symptom outcomes has not been performed. The absence "
                         "is a bounded retrieval finding within the documented "
                         "routes and terminology, not proof that no relevant "
                         "study exists.",
    rationale="Two grounds converge: documented proposition-specific "
              "negative-search work confirmed at class A with the single "
              "closest candidate inspected and excluded, and a tier mismatch in "
              "which acute haemodynamic surrogates are offered for a structural "
              "venous disease whose endpoints were never measured.",
),

dict(
    pid="E-01",
    proposition="Premium Grounding boosts energy/alleviates lack of energy.",
    origin="F02/F04",
    ptype="EXPLICIT; SUBJECTIVE/GENERAL-WELLNESS; PRODUCT-SPECIFIC",
    prep_state="MIXED / CONFLICTING",
    mechanism_state=None,
    qualifiers=["CONDITION/ENDPOINT MISMATCH", "PRODUCT EQUIVALENCE UNCERTAIN"],
    routing="STANDARD BIOMEDICAL ADJUDICATION",
    label="overclaim",
    alt_label=None,
    alt_rationale="No specific frozen label applies; the error is asserting an "
                  "effect on an undefined construct against a direct objective "
                  "null.",
    confidence=0.84,
    strength="mixed",
    overlay="OVERCLAIM",
    claim_strength="STRONG — 'boosting energy' appears in the main benefit "
                   "sentence and 'Lack of energy' in the condition list.",
    verdict_summary="'Energy' has no consistent operational definition in the "
                    "evidence. The one small positive line is self-report in 16 "
                    "massage therapists; the one direct objective test found no "
                    "difference in fatigue, oxygen uptake, heart rate, lactate "
                    "or running economy.",
    evidence_tier="limited_human",
    conclusion_tier="general_public",
    bridge_supported=False,
    items=[
        dict(text="Chevalier et al. 2019: small energy and fatigue self-report "
                  "improvements in 16 massage therapists.",
             source_reference="H22", tier="limited_human", role="supporting",
             why_it_matters="Self-report in a 16-participant stepped wedge that "
                            "shares its cohort with H21; many outcomes."),
        dict(text="Muniz-Pardos et al. 2022: randomised crossover in 10 elite "
                  "male runners found no difference in oxygen uptake, heart "
                  "rate, lactate, fatigue or running economy (51.1 plus/minus "
                  "4.2 versus 50.9 plus/minus 5.1).",
             source_reference="H27", tier="limited_human", role="contradictory",
             why_it_matters="A direct, objective, materially null test of "
                            "fatigue and functional capacity. Its product is "
                            "grounded footwear, so the null must not be "
                            "generalised to all grounding settings."),
        dict(text="The energy and fatigue construct is inconsistently defined "
                  "across the evidence; no validated fatigue or energy scale "
                  "with objective function in a representative population was "
                  "located.",
             source_reference="Freeze sections 54/63", tier="not_applicable",
             role="missing_expected",
             why_it_matters="Without a defined metric the claim cannot be "
                            "reliably tested or verified."),
    ],
    supporting=["H22 small self-reported energy and fatigue improvement"],
    contra=["H27 direct acute null across fatigue, oxygen uptake, heart rate, "
            "lactate and running economy",
            "'Energy' lacks a defined metric",
            "H22 is 16 participants with many outcomes and one shared cohort"],
    missing_comparison_group=False,
    missing_causal_chain=False,
    missing_human_evidence=False,
    sufficiency="insufficient",
    sufficiency_rationale="One small self-report line against a direct "
                          "objective null, on an undefined construct.",
    failure_modes=[
        dict(mode="conclusion_exceeds_results",
             rationale="An energy benefit is advertised while the only direct "
                       "objective test of fatigue and functional capacity was "
                       "null.",
             evidence_refs=["H27", "H22"]),
        dict(mode="inappropriate_generalization",
             rationale="Self-report from 16 occupational participants is "
                       "extended to the general audience.",
             evidence_refs=["H22"]),
    ],
    risk="low",
    risk_rationale="Low-energy complaints are usually benign; the main risk is "
                   "misplaced purchase reliance rather than clinical harm.",
    reader_misunderstanding="That an energy increase is a demonstrated product "
                            "effect.",
    affected_decision="Purchase for fatigue complaints.",
    directness="DIRECT but MIXED, including a direct objective null.",
    endpoint_fidelity="LOW — the energy construct is inconsistently defined; "
                      "objective function is mixed to null.",
    population_fidelity="No representative general-audience fatigue population.",
    timeframe_fidelity="Acute or short occupational and exercise windows.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — workplace mats and shoes; "
                     "the null used grounded footwear.",
    causality_boundary="A vague construct plus mixed positive and null lines "
                       "prevents causal attribution.",
    replication="Small positive self-report plus an independent acute null; not "
                "an exact replication either way.",
    steelman="Strongest legitimate reading: H27 tested 20-minute running "
             "economy in elite athletes wearing grounded shoes, which is a "
             "narrow and product-mismatched proxy for everyday energy; the "
             "freeze itself prohibits generalising that null to all grounding "
             "settings. H22's self-reported improvement in energy is the more "
             "on-point measure for the advertised construct.",
    steelman_result="PARTIALLY SURVIVES — it correctly limits the weight of the "
                    "null, but leaves the claim resting on 16 self-reports "
                    "against an undefined endpoint.",
    adversarial="No definition of 'energy' is offered anywhere; the only "
                "objective measurement attempt found nothing; and the "
                "supporting line is self-report from a cohort already counted "
                "once elsewhere.",
    adversarial_result="SUSTAINED.",
    divergence="MATERIAL — the Steelman layer correctly discounted the null for "
               "product mismatch, but this did not rescue the claim: the "
               "remaining support is one small self-report line on an "
               "unoperationalised construct.",
    residual_uncertainty="A validated fatigue or energy scale plus objective "
                         "function in representative users has not been "
                         "studied.",
    rationale="The evidence is genuinely mixed and is reported as such, and the "
              "direct null is explicitly not generalised beyond its "
              "product-mismatched acute setting. The claim nonetheless fails "
              "because the advertised effect is asserted on an undefined "
              "construct with a single small self-report line as its only "
              "support.",
),
]

PROPOSITIONS += [

dict(
    pid="E-02",
    proposition="Premium Grounding is relevant to/alleviates brain fog.",
    origin="F02 in context",
    ptype="IMPLIED; THERAPEUTIC; CONDITION-SPECIFIC; PRODUCT-SPECIFIC",
    prep_state="NO MATERIAL DIRECT EVIDENCE LOCATED",
    mechanism_state=None,
    qualifiers=["BOUNDED NEGATIVE SEARCH", "CONDITION MISMATCH",
                "PRODUCT EQUIVALENCE UNCERTAIN"],
    routing="BOUNDED NEGATIVE SEARCH — proposition-specific negative-search work "
            "documented and confirmed at class A after expanded terminology.",
    label="overclaim",
    alt_label=None,
    alt_rationale="No specific frozen label applies; the error is implying "
                  "relevance to a complaint that no located study measured and "
                  "that the evidence never operationalised.",
    confidence=0.90,
    strength="not_supported",
    overlay="UNSUPPORTED",
    claim_strength="MODERATE-STRONG — a named complaint in the condition list.",
    verdict_summary="No grounding or Earth-contact study operationalising brain "
                    "fog or cognitive fog was located; the structured routes "
                    "returned zero records in PubMed and Europe PMC. The one "
                    "superficially similar record, an ordinary playground "
                    "barefoot exercise and cognition study, tested neither "
                    "conductivity nor brain fog and is screening-ineligible.",
    evidence_tier="not_applicable",
    conclusion_tier="human_therapeutic",
    bridge_supported=False,
    items=[
        dict(text="No brain-fog-specific human grounding study exists in the "
                  "located evidence.",
             source_reference="Freeze section 50", tier="not_applicable",
             role="missing_expected",
             why_it_matters="There is no supporting evidence line at all for "
                            "this proposition."),
        dict(text="Kim T et al. 2024 (PMID 38926837) is an ordinary "
                  "barefoot-versus-sneaker playground exercise and cognition "
                  "study; conductivity, electrical Earth connection and brain "
                  "fog were not tested. It receives no H identifier and is "
                  "distinct from H34 (Kim JS et al. 2024).",
             source_reference="Freeze sections 34/71", tier="not_applicable",
             role="weakening",
             why_it_matters="Blocks the most likely misattribution in this "
                            "case: two 2024 barefoot studies by authors named "
                            "Kim, only one of which is eligible, and neither of "
                            "which addresses brain fog."),
        dict(text="Documented proposition-specific search across PubMed "
                  "(0 found/0 screened), Europe PMC title/abstract (0/0) and "
                  "full text (0/0) and OpenAlex (40 deduplicated) with "
                  "grounding, earthing, barefoot, soil-contact and Earth-contact "
                  "terminology to the 22 August 2026 cut-off: class A, negative "
                  "search state confirmed.",
             source_reference="Freeze sections 19/70/73", tier="not_applicable",
             role="missing_expected",
             why_it_matters="Establishes the breadth of the documented basis "
                            "for the negative statement."),
        dict(text="Brain fog and cognitive fog were never operationalised as "
                  "endpoints; no validated cognition or cognitive-fatigue "
                  "measure appears in the substrate.",
             source_reference="Freeze sections 54/63", tier="not_applicable",
             role="missing_expected",
             why_it_matters="Even a well-designed study could not have "
                            "supported the claim without a defined measure."),
    ],
    supporting=[],
    contra=["No brain-fog grounding study located; zero structured-route hits",
            "Kim T et al. 2024 screening-ineligible and does not address brain "
            "fog",
            "Brain fog never operationalised as an endpoint"],
    missing_comparison_group=False,
    missing_causal_chain=False,
    missing_human_evidence=True,
    sufficiency="insufficient",
    sufficiency_rationale="No qualifying study and no operational endpoint "
                          "exist within the documented routes and terminology.",
    failure_modes=[
        dict(mode="missing_human_evidence",
             rationale="No human Earth-contact intervention study with a "
                       "brain-fog or cognitive endpoint was located.",
             evidence_refs=["Freeze sections 19/70/73"]),
        dict(mode="conclusion_exceeds_results",
             rationale="Relevance to a named complaint is implied where no "
                       "supporting evidence line and no defined endpoint exist.",
             evidence_refs=["Freeze sections 50/54"]),
    ],
    risk="moderate",
    risk_rationale="Persistent cognitive complaints can indicate treatable "
                   "conditions; implied relevance may delay assessment.",
    reader_misunderstanding="That grounding has been shown to clear cognitive "
                            "fog.",
    affected_decision="Whether to seek assessment for cognitive symptoms.",
    directness="ABSENT — no direct eligible study.",
    endpoint_fidelity="ENDPOINT ABSENT — brain fog not operationalised.",
    population_fidelity="ABSENT — brain-fog populations and causes "
                        "unrepresented.",
    timeframe_fidelity="NOT APPLICABLE — no direct timeframe.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — no study or product "
                     "match.",
    causality_boundary="No grounding or brain-fog causal contrast exists.",
    replication="None.",
    steelman="Strongest legitimate reading: brain fog is commonly attributed to "
             "poor sleep and stress, both of which grounding studies address, "
             "so an indirect pathway is conceivable; and a 2024 barefoot study "
             "did report cognitive outcomes.",
    steelman_result="FAILS — the 2024 cognition study is screening-ineligible "
                    "and did not measure brain fog, and the sleep and stress "
                    "lines it would depend on are themselves mixed.",
    adversarial="Structured database routes returned literally zero records, "
                "the complaint was never operationalised, and the one record "
                "that could be mistaken for evidence tested neither grounding "
                "nor brain fog.",
    adversarial_result="SUSTAINED.",
    divergence="NONE MATERIAL.",
    residual_uncertainty="An operational brain-fog definition with validated "
                         "cognition or fatigue endpoints has never been "
                         "studied. The absence is a bounded retrieval finding "
                         "within the documented routes and terminology, not "
                         "proof that no relevant study exists.",
    rationale="Documented proposition-specific negative-search work confirmed "
              "the negative state at class A with zero structured-route hits, "
              "the nearest candidate is explicitly screening-ineligible, and "
              "the complaint has no operational definition anywhere in the "
              "substrate. The verdict follows from those three facts rather "
              "than from the preparation state label.",
),

dict(
    pid="E-03",
    proposition="Premium Grounding is relevant to/alleviates menopause "
                "symptoms.",
    origin="F02 in context",
    ptype="IMPLIED; THERAPEUTIC; CONDITION-SPECIFIC; PRODUCT-SPECIFIC",
    prep_state="VERY LIMITED DIRECT EVIDENCE — GROUNDING COMPONENT NOT ISOLABLE",
    mechanism_state=None,
    qualifiers=["GROUNDING COMPONENT NOT ISOLABLE", "HIGH CONFOUNDING",
                "PRODUCT MISMATCH", "PRODUCT EQUIVALENCE UNCERTAIN",
                "REPLICATION ABSENT"],
    routing="STANDARD BIOMEDICAL ADJUDICATION — note that the historical "
            "negative-search state for menopause was INVALIDATED by H33 and "
            "must not be reinstated.",
    label="overclaim",
    alt_label=None,
    alt_rationale="No specific frozen label applies. A mechanism_vs_evidence "
                  "reading was rejected: no preclinical pathway is extrapolated "
                  "— the defect is that a real human condition study cannot "
                  "attribute its effect to grounding.",
    confidence=0.83,
    strength="not_directly_established",
    overlay="OVERCLAIM",
    claim_strength="MODERATE-STRONG — a named life-stage condition in the "
                   "condition list.",
    verdict_summary="This is the only advertised condition with a "
                    "condition-relevant human Earth-contact study, and its "
                    "reported effects are large. But allocation was nonrandom, "
                    "the comparator equalised nothing, no product was involved, "
                    "and exercise, walking, forest exposure, social contact, "
                    "researcher attention, sensory stimulation and soil contact "
                    "cannot be separated. Nothing in it is attributable to "
                    "grounding.",
    evidence_tier="limited_human",
    conclusion_tier="human_therapeutic",
    bridge_supported=False,
    items=[
        dict(text="Kim M-H & Lee E-Y 2025: quasi-experimental nonequivalent "
                  "control, 73 enrolled and 60 analysed (29 intervention, 31 "
                  "control), women with Menopause Rating Scale at or above 8; "
                  "60 minutes, three times weekly for 12 weeks on a maintained "
                  "2.7 km soil forest trail with barefoot soil contact. "
                  "Menopausal symptoms z=-5.59, p<.001; stress z=-3.58, p<.001; "
                  "quality of life z=-3.47, p=.001; sleep time-by-group F=7.53, "
                  "p=.008.",
             source_reference="H33", tier="limited_human", role="supporting",
             why_it_matters="Genuine condition-relevant direct exposure in a "
                            "symptomatic population with large reported effects "
                            "on a condition-specific instrument."),
        dict(text="Allocation was nonrandom, collection partly nonconcurrent, "
                  "some prior controls were later re-enrolled, outcomes were "
                  "self-reported, attrition was differential (10 of 39 "
                  "intervention dropouts versus 3 of 34 controls), and there "
                  "was no preregistration.",
             source_reference="H33", tier="limited_human", role="weakening",
             why_it_matters="Design and reporting features that individually "
                            "and jointly undermine causal attribution."),
        dict(text="There was no equal-exercise, shod-walking or sham-grounding "
                  "control; exercise, walking, forest and nature exposure, "
                  "social and group contact, researcher support, sensory "
                  "stimulation and soil contact are inseparable.",
             source_reference="H33", tier="limited_human", role="contradictory",
             why_it_matters="The comparator equalised none of the "
                            "cointerventions, so the grounding component cannot "
                            "be isolated from the programme as a whole."),
        dict(text="No Premium Grounding product was used; the intervention was "
                  "barefoot walking on a soil forest trail. Replication is "
                  "absent.",
             source_reference="H33", tier="not_applicable",
             role="missing_expected",
             why_it_matters="Product mismatch and a single unreplicated "
                            "programme."),
    ],
    supporting=["H33 menopause z=-5.59, p<.001; stress z=-3.58; QoL z=-3.47; "
                "sleep time-by-group F=7.53, p=.008"],
    contra=["Nonrandom allocation, partly nonconcurrent collection, "
            "re-enrolment, differential attrition, self-report, no "
            "preregistration",
            "No equal-exercise, shod-walking or sham-grounding control",
            "Exercise, nature, social, researcher, sensory and soil components "
            "inseparable",
            "PRODUCT MISMATCH; REPLICATION ABSENT"],
    missing_comparison_group=False,
    missing_causal_chain=True,
    missing_human_evidence=False,
    sufficiency="insufficient",
    sufficiency_rationale="A real condition-relevant exposure exists, but its "
                          "design cannot attribute any part of the effect to "
                          "grounding, and no product was tested.",
    failure_modes=[
        dict(mode="missing_causal_chain",
             rationale="The design cannot separate grounding from exercise, "
                       "nature exposure, social contact and researcher "
                       "attention, so no causal link to grounding is "
                       "established.",
             evidence_refs=["H33"]),
        dict(mode="conclusion_exceeds_results",
             rationale="A product benefit for menopause symptoms is implied "
                       "from a barefoot forest-walking programme that used no "
                       "product and isolated no component.",
             evidence_refs=["H33"]),
    ],
    risk="high",
    risk_rationale="Menopause symptom management has effective options; "
                   "implied product relevance may displace them.",
    reader_misunderstanding="That the product has been shown to relieve "
                            "menopause symptoms.",
    affected_decision="Menopause symptom management.",
    directness="VERY LIMITED DIRECT — condition-relevant exposure, "
               "GROUNDING COMPONENT NOT ISOLABLE.",
    endpoint_fidelity="MODERATE — the Menopause Rating Scale is "
                      "condition-relevant, but self-report within a combined "
                      "programme prevents grounding specificity.",
    population_fidelity="GOOD for the condition — symptomatic middle-aged women "
                        "— but represented only in one nonrandom programme.",
    timeframe_fidelity="Twelve-week programme; post-intervention durability not "
                       "established.",
    product_transfer="PRODUCT MISMATCH and PRODUCT EQUIVALENCE UNCERTAIN — "
                     "barefoot soil walking, not the advertised product.",
    causality_boundary="Exercise, walking, forest and nature, social, "
                       "researcher, sensory and soil-contact effects are "
                       "inseparable.",
    replication="REPLICATION ABSENT — a single combined-exposure programme.",
    steelman="Strongest legitimate reading: H33 is a real, condition-specific, "
             "adequately sized human study in exactly the advertised "
             "population, using a validated condition instrument, with a very "
             "large effect (z=-5.59, p<.001) reproduced across four outcome "
             "domains including an objective sleep interaction. It was found "
             "only because the search was deliberately hardened against "
             "terminology drift, and it forced a genuine upgrade of this "
             "proposition's evidence state. It must not be dismissed and must "
             "never be reverted to a no-evidence state.",
    steelman_result="SURVIVES AS CONDITION-RELEVANT EXPOSURE — but supports no "
                    "grounding-specific or product-specific conclusion.",
    adversarial="The control group received no new structured activity at all. "
                "Twelve weeks of thrice-weekly supervised forest walking with "
                "group and researcher contact would be expected to improve "
                "self-reported symptoms, stress, quality of life and sleep "
                "whether or not the participants were barefoot. Nothing "
                "isolates the conductive component, and no product was used.",
    adversarial_result="SUSTAINED.",
    divergence="MATERIAL — the Steelman layer established a genuine, "
               "condition-relevant and statistically strong human study; the "
               "adversarial layer established that none of its effect is "
               "attributable to grounding. Resolved as OVERCLAIM with the "
               "mandatory qualifier GROUNDING COMPONENT NOT ISOLABLE carried on "
               "the verdict, and the positive study explicitly preserved.",
    residual_uncertainty="A randomised barefoot or Earth-contact versus shod or "
                         "sham trial equalising exercise, environment, social "
                         "and researcher exposure and measurement schedule has "
                         "not been performed.",
    rationale="The frozen state VERY LIMITED DIRECT EVIDENCE — GROUNDING "
              "COMPONENT NOT ISOLABLE is preserved exactly and is never "
              "reverted to NO MATERIAL DIRECT EVIDENCE LOCATED. The "
              "adjudicated object is the advertised implication that the "
              "product relieves menopause symptoms. The single supporting "
              "study used no product and cannot attribute its effect to the "
              "conductive component, so the implication is not supported, while "
              "the study itself is preserved as a real condition-relevant "
              "signal for a barefoot soil-walking programme.",
),
]

PROPOSITIONS += [

dict(
    pid="C-01",
    proposition="Premium Grounding enhances cardiovascular health.",
    origin="F11",
    ptype="EXPLICIT; PHYSIOLOGICAL/THERAPEUTIC; PRODUCT-SPECIFIC",
    prep_state="VERY LIMITED DIRECT EVIDENCE",
    mechanism_state=None,
    qualifiers=["SURROGATE ENDPOINT ONLY", "PRODUCT EQUIVALENCE UNCERTAIN"],
    routing="STANDARD BIOMEDICAL ADJUDICATION",
    label="overclaim",
    alt_label="mechanism_vs_evidence",
    alt_rationale="Rejected as primary under the frozen precedence rule: the "
                  "taxonomy routes surrogate endpoints framed as clinical "
                  "outcomes to overclaim and explicitly excludes the "
                  "surrogate-to-clinical gap from mechanism_vs_evidence.",
    confidence=0.88,
    strength="not_directly_established",
    overlay="OVERCLAIM",
    claim_strength="STRONG AND BROAD — 'Enhance cardiovascular health' asserts "
                   "a clinical benefit in the most consequential domain in the "
                   "advertisement.",
    verdict_summary="All supporting evidence is acute surrogate measurement — "
                    "zeta potential, facial perfusion, blood viscosity — or "
                    "blood-pressure change in mostly uncontrolled one-group "
                    "designs. No cardiovascular event, function or durable "
                    "risk-modification outcome was studied.",
    evidence_tier="biomarker",
    conclusion_tier="human_therapeutic",
    bridge_supported=False,
    items=[
        dict(text="Chevalier et al. 2013: red-cell zeta potential -5.28 to "
                  "-14.3 mV, a 2.70-fold ratio of magnitude, individual ratios "
                  "1.27 to 5.63, paired p=3.57 x 10 to the -4, uncontrolled "
                  "n=10.",
             source_reference="H10", tier="biomarker", role="supporting",
             why_it_matters="The 2.70 figure is a zeta-potential magnitude "
                            "ratio, NOT a 270 percent health improvement and "
                            "not a cardiovascular efficacy result. The study is "
                            "uncontrolled with ten participants."),
        dict(text="Chevalier 2014 laser-speckle facial perfusion changes and "
                  "Brown & Chevalier 2015 blood-viscosity differences during "
                  "yoga, p=.03, n=28 women.",
             source_reference="H13/H17", tier="biomarker", role="supporting",
             why_it_matters="Acute cardiovascular surrogates; H13 shares its "
                            "cohort with H14 and H15 and is Earth FX funded."),
        dict(text="Teli et al. 2015, Elkin & Winter 2018/2019, Estiningtyas et "
                  "al. 2023 and Wedri et al. 2025 report blood-pressure "
                  "reductions in weak or uncontrolled designs.",
             source_reference="H12/H20/H28/H32", tier="limited_human",
             role="supporting",
             why_it_matters="Clinical measurement, but three of the four are "
                            "one-group pre/post with medication, natural "
                            "course, regression and behaviour confounding."),
        dict(text="No cardiovascular event or function trial, and no durable "
                  "risk-modification outcome, were located.",
             source_reference="Freeze sections 27/51/63", tier="not_applicable",
             role="missing_expected",
             why_it_matters="The clinical endpoint the claim names has never "
                            "been studied."),
        dict(text="Blood-property and imaging surrogates are of uncertain "
                  "clinical meaning; the prohibited transition is blood "
                  "property or image to cardiovascular clinical outcome.",
             source_reference="Freeze sections 36/40", tier="not_applicable",
             role="weakening",
             why_it_matters="Blocks the inference the advertisement invites."),
    ],
    supporting=["H10 zeta potential", "H13 perfusion", "H17 viscosity p=.03",
                "H12/H20/H28/H32 weak blood-pressure signals"],
    contra=["No cardiovascular event, function or durable outcome trial",
            "H20/H28/H32 uncontrolled one-group designs",
            "Surrogates of uncertain clinical meaning",
            "H13/H14/H15 collapse to one dataset"],
    missing_comparison_group=True,
    missing_causal_chain=True,
    missing_human_evidence=False,
    sufficiency="insufficient",
    sufficiency_rationale="Acute surrogates and uncontrolled blood-pressure "
                          "observations cannot establish enhanced "
                          "cardiovascular health.",
    failure_modes=[
        dict(mode="evidence_tier_mismatch",
             rationale="Zeta potential, perfusion imaging and viscosity are "
                       "biomarker-tier surrogates offered for a clinical "
                       "cardiovascular claim.",
             evidence_refs=["H10", "H13/H17"]),
        dict(mode="missing_comparison_group",
             rationale="Three of the four blood-pressure lines and the zeta "
                       "potential study are uncontrolled one-group designs.",
             evidence_refs=["H10", "H20", "H28", "H32"]),
        dict(mode="conclusion_exceeds_results",
             rationale="Enhanced cardiovascular health is asserted where no "
                       "cardiovascular event, function or durable outcome was "
                       "ever measured.",
             evidence_refs=["Freeze sections 27/51"]),
    ],
    risk="high",
    risk_rationale="Cardiovascular claims can lead readers to alter or stop "
                   "antihypertensive or other cardiac treatment.",
    reader_misunderstanding="That the product improves heart health or lowers "
                            "cardiovascular risk.",
    affected_decision="Cardiovascular treatment adherence and risk management.",
    directness="VERY LIMITED — surrogates and weak blood-pressure designs.",
    endpoint_fidelity="LOW — blood properties and imaging are not "
                      "cardiovascular health, events or durable risk "
                      "modification.",
    population_fidelity="Prehypertensive, hypertensive and healthy surrogate "
                        "samples; no cardiovascular-outcome population.",
    timeframe_fidelity="Mostly acute or short, or uncontrolled months; no "
                       "durable event or risk outcome.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — barefoot, patches and "
                     "mats; no exact-product clinical trial.",
    causality_boundary="Surrogates and uncontrolled blood-pressure change "
                       "cannot establish cardiovascular causality.",
    replication="Multiple heterogeneous surrogate and blood-pressure lines; no "
                "clinical outcome replication.",
    steelman="Strongest legitimate reading: blood pressure is a genuine "
             "clinical measurement, four separate groups reported reductions, "
             "and the zeta-potential and viscosity findings offer a coherent "
             "rheological mechanism by which those reductions might occur. The "
             "convergence across mechanism and measurement is not trivial.",
    steelman_result="PARTIALLY SURVIVES at the surrogate layer — does not reach "
                    "cardiovascular health.",
    adversarial="Three of the four blood-pressure studies have no comparator at "
                "all, so regression to the mean, medication changes and "
                "seasonal or behavioural effects are unexcluded. The "
                "rheological findings are acute, small and partly from one "
                "collapsed dataset. Not one study measured a cardiovascular "
                "outcome.",
    adversarial_result="SUSTAINED.",
    divergence="MATERIAL — the Steelman layer identified genuine mechanistic "
               "convergence; the adversarial layer showed the clinical "
               "endpoint is entirely absent and the blood-pressure evidence is "
               "largely uncontrolled.",
    residual_uncertainty="Controlled long-term vascular function and clinical "
                         "cardiovascular outcome trials have not been "
                         "performed.",
    rationale="The claim names the clinical construct 'cardiovascular health' "
              "while every supporting result is either an acute surrogate or an "
              "uncontrolled blood-pressure observation. The H10 2.70 figure is "
              "preserved as a zeta-potential magnitude ratio and is not "
              "permitted to read as a health improvement. The distance between "
              "the measured surrogates and the advertised clinical benefit is "
              "what makes this an overclaim.",
),

dict(
    pid="R-01",
    proposition="Premium Grounding accelerates recovery from exercise.",
    origin="F13",
    ptype="EXPLICIT; PHYSIOLOGICAL/FUNCTIONAL; PRODUCT-SPECIFIC",
    prep_state="MIXED / CONFLICTING",
    mechanism_state=None,
    qualifiers=["PRODUCT MISMATCH", "PRODUCT EQUIVALENCE UNCERTAIN",
                "mixed replication"],
    routing="STANDARD BIOMEDICAL ADJUDICATION",
    label="overclaim",
    alt_label="solid",
    alt_rationale="A solid reading was considered on the strength of H23, an "
                  "independent randomised triple-blind trial. It is rejected as "
                  "primary because the advertised wording is unqualified for a "
                  "general audience while the evidence is small, heterogeneous "
                  "and includes a direct objective null.",
    confidence=0.75,
    strength="mixed",
    overlay="QUALIFIED",
    claim_strength="STRONG — 'Accelerate recovery from exercise' is listed "
                   "under 'has been shown to'.",
    verdict_summary="An independent randomised triple-blind trial reported a "
                    "smaller performance decline and a smaller creatine-kinase "
                    "rise over ten nights after eccentric exercise, supported "
                    "by biomarker signals from other groups. A separate "
                    "randomised crossover found no acute effect, but it tested "
                    "grounded footwear and running economy rather than "
                    "recovery. Bounded support exists in eccentric-exercise "
                    "recovery protocols; the advertised general claim does not "
                    "follow.",
    evidence_tier="limited_human",
    conclusion_tier="general_public",
    bridge_supported=False,
    items=[
        dict(text="Müller et al. 2019: randomised triple-blind, 22 sport and "
                  "physiotherapy students (12 grounded, 10 sham), grounded "
                  "versus sham sleep for 10 nights after downhill treadmill "
                  "running; smaller decline in selected performance measures "
                  "and a smaller creatine-kinase rise.",
             source_reference="H23", tier="limited_human", role="supporting",
             why_it_matters="The strongest recovery evidence and the only "
                            "clearly independent positive group, outside the "
                            "core author network. Blood biomarker subset n=4."),
        dict(text="Brown, Chevalier & Hill 2015 DOMS biomarkers (creatine "
                  "kinase day 2 p=.04, neutrophils p=.05) and Sokal et al. 2013 "
                  "lower urea at sampled timepoints.",
             source_reference="H16/H11", tier="biomarker", role="supporting",
             why_it_matters="Directionally consistent biomarker signals, but "
                            "selected from many outcomes and timepoints."),
        dict(text="Muniz-Pardos et al. 2022: randomised crossover in 10 elite "
                  "male runners, grounded versus non-grounded shoes over a "
                  "20-minute run; no difference in oxygen uptake, heart rate, "
                  "lactate, fatigue or running economy.",
             source_reference="H27", tier="limited_human", role="contradictory",
             why_it_matters="A direct objective null, but on acute performance "
                            "rather than recovery and with a mismatched "
                            "product. The freeze prohibits generalising a "
                            "grounded-shoe null to all grounding settings."),
        dict(text="Brown, Chevalier & Hill 2010: randomised double-blind pilot "
                  "in 8 healthy young men with selected differences among 48 "
                  "outcomes under a nonstandard threshold of at least 10 "
                  "percent.",
             source_reference="H06", tier="limited_human", role="weakening",
             why_it_matters="Extreme multiplicity and imprecision; a "
                            "feasibility signal only."),
        dict(text="No registered, powered recovery trial with multiplicity "
                  "control and the exact product was located.",
             source_reference="Freeze section 63", tier="not_applicable",
             role="missing_expected",
             why_it_matters="No study addresses the advertised product or the "
                            "general audience."),
    ],
    supporting=["H23 independent randomised triple-blind recovery signal",
                "H16 DOMS biomarkers", "H11 urea and creatinine surrogates"],
    contra=["H27 direct acute null (product mismatch, different construct)",
            "H06 48 outcomes with a nonstandard threshold",
            "H16 pain occurred in both groups",
            "H23 n=22 with a biomarker subset of 4",
            "No registered, powered, exact-product recovery trial"],
    missing_comparison_group=False,
    missing_causal_chain=False,
    missing_human_evidence=False,
    sufficiency="insufficient",
    sufficiency_rationale="Sufficient for a bounded statement about eccentric-"
                          "exercise recovery protocols; insufficient for the "
                          "advertised general claim.",
    failure_modes=[
        dict(mode="inappropriate_generalization",
             rationale="A 22-participant eccentric-exercise protocol in sport "
                       "students is extended to recovery for the general "
                       "advertised audience.",
             evidence_refs=["H23"]),
        dict(mode="conclusion_exceeds_results",
             rationale="An established recovery benefit is advertised while the "
                       "supporting trials are small and multiply tested and a "
                       "direct objective test found nothing.",
             evidence_refs=["H23", "H06", "H27"]),
    ],
    risk="moderate",
    risk_rationale="Exercise recovery claims carry limited clinical risk; the "
                   "main exposure is misplaced purchase reliance.",
    reader_misunderstanding="That faster recovery is an established, "
                            "generalisable product effect.",
    affected_decision="Purchase for training and recovery support.",
    directness="DIRECT within eccentric-exercise recovery protocols; MIXED "
               "overall.",
    endpoint_fidelity="MODERATE — DOMS, creatine kinase and performance "
                      "measures are relevant but heterogeneous; a direct acute "
                      "null survives on a different construct.",
    population_fidelity="LOW for the advertised audience — healthy young men, "
                        "sport students and elite runners.",
    timeframe_fidelity="Acute to ten nights and four days; long-term recovery "
                       "adaptation untested.",
    product_transfer="PRODUCT MISMATCH and PRODUCT EQUIVALENCE UNCERTAIN — "
                     "patches, sheets and shoes; no exact product.",
    causality_boundary="Positive and null lines differ in product, exercise "
                       "model and endpoint; no common causal replication.",
    replication="Independent positive and null groups with heterogeneous "
                "protocols; mixed.",
    steelman="Strongest legitimate reading: H23 is randomised, triple-blind and "
             "independent of the commercial author network, and it reports "
             "coherent effects across two different endpoint types — "
             "performance decline and creatine-kinase rise — over a realistic "
             "ten-night protocol. Two further groups report biomarker changes "
             "in the same direction. The apparent counterevidence tested a "
             "different construct with a different product and does not "
             "transfer.",
    steelman_result="SURVIVES IN BOUNDED FORM — this is the basis for the "
                    "QUALIFIED verdict.",
    adversarial="H23 has 22 participants and a four-person biomarker subset. "
                "H06 tested 48 outcomes under an invented threshold. H16 found "
                "pain in both arms. Nothing is registered, powered or "
                "product-matched, and the one attempt at an objective "
                "functional measurement found nothing.",
    adversarial_result="PARTIALLY SUSTAINED — defeats the advertised breadth, "
                       "not the bounded eccentric-exercise finding.",
    divergence="MATERIAL AND DECISIVE — the Steelman layer established a "
               "genuine independent positive trial and correctly limited the "
               "null's reach on product-mismatch grounds; the adversarial layer "
               "established that the trials are small, multiply tested and "
               "unregistered. Resolved as QUALIFIED, with the evidence state "
               "recorded as mixed.",
    residual_uncertainty="A registered, powered recovery trial with "
                         "multiplicity control and the exact product has not "
                         "been performed.",
    rationale="The evidence is genuinely two-sided and is reported as mixed "
              "rather than converted into UNCERTAIN. Support is real but "
              "bounded: one independent randomised triple-blind trial in an "
              "eccentric-exercise protocol, with consistent biomarker signals "
              "elsewhere. The direct null is weighed at its true relevance — a "
              "different construct with a mismatched product — and is not "
              "generalised. The advertised unqualified general claim exceeds "
              "those bounds, so the verdict is QUALIFIED rather than SOLID.",
),
]

PROPOSITIONS += [

dict(
    pid="W-01",
    proposition="Premium Grounding restores the body's natural balance.",
    origin="F01/F03",
    ptype="EXPLICIT; GENERAL-WELLNESS; PRODUCT-SPECIFIC",
    prep_state="NO MATERIAL DIRECT EVIDENCE LOCATED",
    mechanism_state=None,
    qualifiers=["ENDPOINT NOT OPERATIONALISED", "PRODUCT EQUIVALENCE UNCERTAIN"],
    routing="NOT OPERATIONALISABLE AS WORDED — 'natural balance' has no defined "
            "scientific endpoint. This is a defect in the claim, not an "
            "epistemic gap in the evidence.",
    label="overclaim",
    alt_label=None,
    alt_rationale="No specific frozen label applies. The claim asserts a "
                  "definite physiological restoration with no testable "
                  "referent, which is rhetorical inflation and routes to the "
                  "generic residual label.",
    confidence=0.86,
    strength="not_directly_established",
    overlay="UNSUPPORTED",
    claim_strength="STRONG BUT UNFALSIFIABLE — asserts an accomplished "
                   "restoration of a physiological state that is never "
                   "defined.",
    verdict_summary="'Natural balance' names no measurable physiological "
                    "variable. No homeostatic endpoint was defined or measured "
                    "in any located study, so the claim cannot be tested as "
                    "worded and therefore cannot be substantiated.",
    evidence_tier="not_applicable",
    conclusion_tier="general_public",
    bridge_supported=False,
    items=[
        dict(text="Chevalier et al. 2019 reports improvement across several "
                  "well-being symptoms in 16 massage therapists.",
             source_reference="H22", tier="limited_human", role="supporting",
             why_it_matters="The nearest available material; scattered symptom "
                            "self-reports cannot validate a global balance "
                            "claim and the cohort is shared with H21."),
        dict(text="No operationalised 'natural balance' endpoint exists; no "
                  "defined homeostatic variable was identified, so the "
                  "mechanism cannot be tested as worded.",
             source_reference="Freeze sections 53/54/63", tier="not_applicable",
             role="missing_expected",
             why_it_matters="Without a prespecified testable definition the "
                            "claim admits no evidence for or against it."),
        dict(text="The undefined construct also prevents a population, "
                  "timeframe or causal contrast from being specified.",
             source_reference="Freeze sections 56/57/58", tier="not_applicable",
             role="weakening",
             why_it_matters="Every fidelity dimension fails for the same "
                            "reason: there is nothing to measure."),
    ],
    supporting=["H22 scattered well-being symptom self-reports (not a balance "
                "endpoint)"],
    contra=["No defined homeostatic variable; the claim is untestable as worded",
            "Scattered symptom reports cannot validate a global balance claim"],
    missing_comparison_group=False,
    missing_causal_chain=True,
    missing_human_evidence=True,
    sufficiency="insufficient",
    sufficiency_rationale="No endpoint exists against which sufficiency could "
                          "be assessed; the claim is not operationalisable.",
    failure_modes=[
        dict(mode="conclusion_exceeds_results",
             rationale="A definite physiological restoration is asserted with "
                       "no defined variable, no measurement and no study.",
             evidence_refs=["Freeze sections 53/54"]),
        dict(mode="missing_human_evidence",
             rationale="No human study measured any operationalised 'natural "
                       "balance' endpoint.",
             evidence_refs=["Freeze section 63"]),
    ],
    risk="moderate",
    risk_rationale="Unfalsifiable wellness language is persuasive precisely "
                   "because it cannot be checked, and it frames the specific "
                   "condition list that follows it.",
    reader_misunderstanding="That a measurable physiological normalisation has "
                            "been demonstrated.",
    affected_decision="Purchase on general health grounds.",
    directness="NOT ASSESSABLE — no endpoint exists.",
    endpoint_fidelity="NO OPERATIONAL ENDPOINT.",
    population_fidelity="Undefined construct prevents population definition.",
    timeframe_fidelity="Timeframe undefined.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — no endpoint and no exact "
                     "match.",
    causality_boundary="An undefined construct prevents any causal test.",
    replication="None, because the outcome is undefined.",
    steelman="Strongest legitimate reading: 'restores natural balance' could be "
             "read as ordinary consumer shorthand for general well-being rather "
             "than a specific physiological assertion, and H22 does report "
             "broad symptom improvement across several domains.",
    steelman_result="FAILS — the wording appears in a therapeutic health "
                    "advertisement immediately before eleven named medical "
                    "conditions, where it reads as a physiological claim; and "
                    "even the charitable reading has only shared-cohort "
                    "self-report behind it.",
    adversarial="The claim is constructed so that no observation could ever "
                "contradict it. That is not a gap in current knowledge but a "
                "property of the wording, and the substantiation burden rests "
                "with the advertiser.",
    adversarial_result="SUSTAINED.",
    divergence="NONE MATERIAL.",
    residual_uncertainty="A prespecified testable definition does not exist; "
                         "without one, resolution is impossible in principle.",
    rationale="This proposition is routed as NOT OPERATIONALISABLE AS WORDED "
              "and is deliberately NOT recorded as UNCERTAIN. UNCERTAIN would "
              "assert that the state of the world is unknown; here the state of "
              "the world is not at issue, because the claim specifies no "
              "measurable quantity. A health claim that admits no possible "
              "evidence cannot be substantiated, so it is recorded as "
              "UNSUPPORTED with the routing qualifier carried on the verdict.",
),

dict(
    pid="X-01",
    proposition="Premium Grounding produces the advertised benefits across the "
                "general audience and listed conditions.",
    origin="F01-F13",
    ptype="IMPLIED; BROAD THERAPEUTIC GENERALISATION; PRODUCT-SPECIFIC",
    prep_state="NO MATERIAL DIRECT EVIDENCE LOCATED",
    mechanism_state=None,
    qualifiers=["PRODUCT EQUIVALENCE UNCERTAIN", "CONDITION/TIMEFRAME DRIFT",
                "REPLICATION ABSENT"],
    routing="BUNDLE / GENERALISATION CLAIM — COMPONENT ADJUDICATION REQUIRED. "
            "Adjudicated by aggregating the component verdicts across benefits, "
            "populations, conditions, timeframes and products; NOT dismissed as "
            "untestable.",
    label="overclaim",
    alt_label=None,
    alt_rationale="No specific frozen label applies; the error is "
                  "generalisation across dimensions none of the component "
                  "evidence supports.",
    confidence=0.92,
    strength="not_supported",
    overlay="UNSUPPORTED",
    claim_strength="MAXIMALLY BROAD — asserts the full advertised benefit set "
                   "for a general audience across eleven named conditions.",
    verdict_summary="Adjudicated by component rather than dismissed as "
                    "untestable. Across the twenty-one biomedical component "
                    "propositions, none reaches SOLID; three are QUALIFIED "
                    "within narrow bounds; sleep, stress, energy and recovery "
                    "are mixed; five named conditions have no material direct "
                    "evidence after documented negative search; immune function "
                    "is unsupported and its one Earth-contact marker line is "
                    "discordant; the mechanism chain is broken at the "
                    "provenance step; no proposition has an exact-product "
                    "match; and no study tested the bundle, a general audience "
                    "or durable outcomes.",
    evidence_tier="limited_human",
    conclusion_tier="general_public",
    bridge_supported=False,
    items=[
        dict(text="Component benefits: no component proposition reaches SOLID. "
                  "M-01a, P-01 and R-01 are QUALIFIED within narrow bounds; "
                  "S-01, S-03, E-01 and R-01 are mixed; I-01, C-01, S-02, S-04, "
                  "P-03, P-04 and E-03 are overclaims on surrogate, single, "
                  "grey or non-isolable evidence.",
             source_reference="Component adjudication, this run",
             tier="limited_human", role="supporting",
             why_it_matters="Isolated positive outcomes exist, which is why the "
                            "bundle is adjudicated rather than dismissed; but "
                            "no component supports an unqualified benefit."),
        dict(text="Component conditions: arthritis, headache, varicose veins, "
                  "brain fog and immune function retain NO MATERIAL DIRECT "
                  "EVIDENCE LOCATED after documented proposition-specific "
                  "negative search confirmed at class A.",
             source_reference="Freeze sections 70/73", tier="not_applicable",
             role="contradictory",
             why_it_matters="Five of the advertised conditions have no "
                            "qualifying study within the documented routes."),
        dict(text="Component populations: healthy young men, elite runners, "
                  "massage therapists, sport students, mild Alzheimer patients, "
                  "preterm infants, postoperative and hypertensive patients and "
                  "symptomatic middle-aged women. No representative "
                  "multi-condition or general-audience cohort was studied.",
             source_reference="Freeze section 37", tier="not_applicable",
             role="contradictory",
             why_it_matters="The advertised audience is not represented "
                            "anywhere in the evidence."),
        dict(text="Component timeframes run from 20 minutes to 12 weeks, with "
                  "durability largely unreported; the advertisement carries no "
                  "duration qualifier and its present-tense wording cannot "
                  "inherit durability that studies did not measure.",
             source_reference="Freeze section 38", tier="not_applicable",
             role="contradictory",
             why_it_matters="No durable multi-condition programme exists."),
        dict(text="Component products: no evidence line receives DIRECT PRODUCT "
                  "MATCH; every proposition carries PRODUCT EQUIVALENCE "
                  "UNCERTAIN. No proposition has a confirmed exact-product "
                  "replication.",
             source_reference="Freeze sections 39/43", tier="not_applicable",
             role="contradictory",
             why_it_matters="Generalisation to the advertised product is "
                            "unsupported at every component."),
        dict(text="No study of the full proposition exists; no single "
                  "demonstrated mechanism spans all named conditions, and the "
                  "chain link 'outcomes generalise to the exact product and all "
                  "conditions' is frozen as NOT ESTABLISHED.",
             source_reference="Freeze sections 41/50/91", tier="not_applicable",
             role="missing_expected",
             why_it_matters="The bundle itself was never tested."),
    ],
    supporting=["Isolated positive outcomes in several narrow studies"],
    contra=["No component proposition reaches SOLID",
            "Five named conditions unsupported after documented negative search",
            "Immune function unsupported with a discordant marker line",
            "Mechanism chain broken at the provenance step (M-01b NOT "
            "ESTABLISHED)",
            "Sleep, stress, energy and recovery genuinely mixed",
            "No exact-product match or replication anywhere",
            "No general-audience, multi-condition or durable programme"],
    missing_comparison_group=False,
    missing_causal_chain=True,
    missing_human_evidence=True,
    sufficiency="insufficient",
    sufficiency_rationale="Every generalisation dimension — benefits, "
                          "populations, conditions, timeframes and products — "
                          "fails independently on the component evidence.",
    failure_modes=[
        dict(mode="inappropriate_generalization",
             rationale="Isolated narrow findings in unrepresentative "
                       "populations are generalised to a general audience "
                       "across eleven named conditions and an untested "
                       "product.",
             evidence_refs=["Freeze sections 37/38/39/43"]),
        dict(mode="conclusion_exceeds_results",
             rationale="The advertised bundle asserts a benefit set that no "
                       "study tested and that the component adjudication does "
                       "not support at any component.",
             evidence_refs=["Component adjudication, this run"]),
        dict(mode="evidence_tier_mismatch",
             rationale="Biomarker and acute surrogate evidence underpins a "
                       "broad durable therapeutic generalisation.",
             evidence_refs=["Freeze section 40"]),
    ],
    risk="critical",
    risk_rationale="This is the aggregate takeaway a reader forms from the "
                   "advertisement as a whole, spanning eleven named conditions "
                   "including progressive and treatable diseases.",
    reader_misunderstanding="That the product reliably delivers all the "
                            "advertised benefits for people like them.",
    affected_decision="Purchase, and management of up to eleven named health "
                      "conditions.",
    directness="ABSENT — no study of the full proposition.",
    endpoint_fidelity="NO OMNIBUS ENDPOINT OR BUNDLE was measured.",
    population_fidelity="ABSENT — no representative multi-condition or "
                        "general-audience cohort.",
    timeframe_fidelity="ABSENT — no durable multi-condition programme.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — all underlying transfers "
                     "unresolved.",
    causality_boundary="No evidence supports causal generalisation across all "
                       "conditions.",
    replication="No full-bundle replication.",
    steelman="Strongest legitimate reading: the advertisement lists benefits "
             "that are individually studied rather than invented. Sleep, pain "
             "and recovery each have randomised sham-controlled trials, "
             "inflammation and cardiovascular function each have human "
             "biomarker signals, and menopause has a condition-specific study "
             "with large effects. Read charitably as 'these are the areas where "
             "grounding has been investigated', the list is not fabricated.",
    steelman_result="FAILS AS A GENERALISATION — investigation is not "
                    "demonstration. Even taking every component at its "
                    "strongest, no component supports an unqualified benefit "
                    "for this audience with this product, and five conditions "
                    "have nothing at all.",
    adversarial="The bundle multiplies its component weaknesses. It requires "
                "simultaneously that an unestablished mechanism operates, that "
                "surrogate markers translate into clinical benefit, that narrow "
                "unrepresentative samples generalise, that acute effects "
                "persist, that five unstudied conditions respond, and that all "
                "of it transfers to a product no study used.",
    adversarial_result="SUSTAINED.",
    divergence="NONE MATERIAL on the verdict — the layers agree. They differ "
               "only on how much credit the underlying research programme "
               "deserves, which is recorded but does not change the "
               "generalisation finding.",
    residual_uncertainty="A representative multi-condition programme with "
                         "exact-product data has not been performed. The five "
                         "condition-level absences remain bounded retrieval "
                         "findings, not proof of nonexistence.",
    rationale="X-01 is adjudicated by component as required, not dismissed as "
              "untestable. Each generalisation dimension is tested separately "
              "and each fails on its own: benefits (no component reaches "
              "SOLID), conditions (five unsupported after documented search), "
              "populations (the advertised audience is unrepresented), "
              "timeframes (durability unmeasured) and products (no exact "
              "match anywhere). The verdict does not silently assume immune "
              "benefit, uniform sleep efficacy, or the unestablished M-01b "
              "provenance step; each of those is carried at its own adjudicated "
              "strength.",
),
]

PROPOSITIONS += [

dict(
    pid="X-02",
    proposition="Premium Grounding is the most powerful natural health upgrade "
                "available for purchase.",
    origin="F05",
    ptype="EXPLICIT; SUPERIORITY/GENERAL-WELLNESS; PRODUCT-SPECIFIC",
    prep_state="NO MATERIAL DIRECT EVIDENCE LOCATED",
    mechanism_state=None,
    qualifiers=["COMPARATOR UNDEFINED", "PRODUCT EQUIVALENCE UNCERTAIN",
                "REPLICATION ABSENT"],
    routing="SUPERIORITY CLAIM — COMPARATOR / METRIC UNDEFINED.",
    label="overclaim",
    alt_label=None,
    alt_rationale="No specific frozen label applies; unsupported_superiority is "
                  "a frozen failure mode within the generic residual label.",
    confidence=0.93,
    strength="not_supported",
    overlay="UNSUPPORTED",
    claim_strength="SUPERLATIVE — asserts first rank among all purchasable "
                   "natural health interventions.",
    verdict_summary="A superlative comparative claim requires a defined "
                    "comparator universe, a ranking metric and head-to-head "
                    "evidence. None of the three exists. No superiority trial "
                    "of any kind was located, and the product's own absolute "
                    "effects are unestablished at every component.",
    evidence_tier="not_applicable",
    conclusion_tier="general_public",
    bridge_supported=False,
    items=[
        dict(text="No defined head-to-head superiority evidence was located.",
             source_reference="Freeze section 50", tier="not_applicable",
             role="missing_expected",
             why_it_matters="A comparative claim has no comparative evidence "
                            "behind it."),
        dict(text="The comparator universe and the ranking metric are both "
                  "undefined; no superiority margin is specified.",
             source_reference="Freeze sections 51/54/63", tier="not_applicable",
             role="missing_expected",
             why_it_matters="Even with data, the claim could not be evaluated "
                            "without a defined comparison set and metric."),
        dict(text="No mechanism can establish comparative superiority, and the "
                  "comparator market population is undefined.",
             source_reference="Freeze sections 53/56", tier="not_applicable",
             role="weakening",
             why_it_matters="No indirect route to the claim exists either."),
        dict(text="The product's absolute effects are themselves unestablished: "
                  "no component proposition reaches SOLID and no evidence line "
                  "achieves DIRECT PRODUCT MATCH.",
             source_reference="Component adjudication, this run",
             tier="not_applicable", role="contradictory",
             why_it_matters="A first-rank claim presupposes a demonstrated "
                            "absolute effect, which does not exist here."),
    ],
    supporting=[],
    contra=["No head-to-head superiority evidence located",
            "Comparator universe, ranking metric and margin all undefined",
            "Absolute product effects unestablished at every component"],
    missing_comparison_group=True,
    missing_causal_chain=False,
    missing_human_evidence=True,
    sufficiency="insufficient",
    sufficiency_rationale="No comparative evidence, no comparator definition "
                          "and no ranking metric exist.",
    failure_modes=[
        dict(mode="unsupported_superiority_claim",
             rationale="First rank among all purchasable natural health "
                       "interventions is asserted with no head-to-head "
                       "evidence, no defined comparator universe and no "
                       "ranking metric.",
             evidence_refs=["Freeze sections 50/51/63"]),
        dict(mode="missing_comparison_group",
             rationale="A comparative claim is made where no comparator was "
                       "ever specified or studied.",
             evidence_refs=["Freeze section 54"]),
        dict(mode="conclusion_exceeds_results",
             rationale="A superlative is asserted while the product's absolute "
                       "effects are unestablished at every component.",
             evidence_refs=["Component adjudication, this run"]),
    ],
    risk="high",
    risk_rationale="A superlative invites readers to prefer this product over "
                   "interventions that do have evidence.",
    reader_misunderstanding="That the product outperforms other natural health "
                            "options.",
    affected_decision="Choosing this product instead of an evidenced "
                      "alternative.",
    directness="ABSENT — no superiority trial.",
    endpoint_fidelity="NO DEFINED COMPARATIVE METRIC.",
    population_fidelity="Comparator market population undefined.",
    timeframe_fidelity="No comparative timeframe.",
    product_transfer="PRODUCT EQUIVALENCE UNCERTAIN — product and comparator "
                     "performance not reported.",
    causality_boundary="No causal comparative superiority design exists.",
    replication="No superiority study, therefore no replication.",
    steelman="Strongest legitimate reading: superlatives in consumer "
             "advertising are sometimes read as non-literal enthusiasm rather "
             "than a testable comparative assertion.",
    steelman_result="FAILS — the superlative appears in a therapeutic health "
                    "advertisement immediately after specific medical claims, "
                    "where it functions as a comparative health assertion; and "
                    "no comparative evidence exists on any reading.",
    adversarial="The claim is comparative and superlative, yet neither the set "
                "being compared nor the dimension of comparison is stated, and "
                "no comparison was ever performed.",
    adversarial_result="SUSTAINED.",
    divergence="NONE MATERIAL.",
    residual_uncertainty="A defined comparator universe, superiority margin and "
                         "head-to-head trials do not exist.",
    rationale="This is routed as a superiority claim with an undefined "
              "comparator and metric, not treated as an ordinary efficacy "
              "proposition. It fails on three independent grounds: no "
              "head-to-head evidence, no definable comparison, and no "
              "established absolute effect to rank in the first place.",
),

dict(
    pid="Q-01",
    proposition="Thousands trust the product for the stated benefits.",
    origin="F01",
    ptype="EXPLICIT; COMMERCIAL/POPULARITY; PRODUCT-SPECIFIC",
    prep_state="NO MATERIAL DIRECT EVIDENCE LOCATED",
    mechanism_state=None,
    qualifiers=["COMMERCIAL SUBSTANTIATION REQUIRED"],
    routing="OUTSIDE BIOMEDICAL EVIDENCE SCOPE — COMMERCIAL SUBSTANTIATION "
            "REQUIRED. Absence of biomedical literature is NOT evidence against "
            "a customer-count proposition.",
    label=None,
    analysis_status="insufficient_input",
    alt_label=None,
    alt_rationale="No frozen biomedical label is assigned. Forcing one would "
                  "misrepresent a commercial fact as a scientific finding. The "
                  "framework's own insufficient_input state is used instead, "
                  "which permits a null label under the frozen contract.",
    confidence=None,
    strength="not_assessed",
    overlay="OUTSIDE BIOMEDICAL EVIDENCE SCOPE — COMMERCIAL SUBSTANTIATION "
            "REQUIRED",
    claim_strength="FACTUAL COMMERCIAL ASSERTION — a customer count coupled to "
                   "a benefit attribution.",
    verdict_summary="This is a commercial fact about customer numbers and "
                    "trust, not a biomedical proposition. The frozen substrate "
                    "contains no customer records, sampling frame, trust "
                    "definition or dates, and biomedical studies are incapable "
                    "of establishing or refuting it. The required input class "
                    "is absent, so no biomedical verdict is issued.",
    evidence_tier="not_applicable",
    conclusion_tier="general_public",
    bridge_supported=None,
    items=[
        dict(text="The official record supplies no denominator, survey or trust "
                  "measure, and no customer or sales substantiation was "
                  "reported.",
             source_reference="Freeze sections 50/51/82", tier="not_applicable",
             role="missing_expected",
             why_it_matters="The evidence class the claim requires is absent "
                            "from the substrate, and the adjudication receives "
                            "this as an explicit gap."),
        dict(text="Scientific numbers cannot verify commercial claims; "
                  "scientific participants do not represent customers and "
                  "scientific causality is inapplicable to a commercial trust "
                  "fact.",
             source_reference="Freeze sections 46/56/58", tier="not_applicable",
             role="weakening",
             why_it_matters="Establishes that the biomedical evidence base is "
                            "not merely silent but categorically inapplicable, "
                            "so its silence carries no adverse inference."),
    ],
    supporting=[],
    contra=["No customer count, sampling frame, trust definition or dates "
            "reported — an evidential gap, not counterevidence"],
    missing_comparison_group=False,
    missing_causal_chain=False,
    missing_human_evidence=False,
    sufficiency="unknown",
    sufficiency_rationale="Sufficiency cannot be assessed: the required "
                          "evidence class is commercial and lies outside the "
                          "biomedical substrate entirely.",
    failure_modes=[],
    risk="unknown",
    risk_rationale="Reader-impact risk cannot be characterised without knowing "
                   "whether the underlying commercial fact is accurate. "
                   "Recorded as an explicit insufficient state rather than "
                   "guessed.",
    reader_misunderstanding="That a stated customer count is itself evidence "
                            "that the stated benefits occur.",
    affected_decision="Purchase influenced by social proof.",
    directness="NOT APPLICABLE — not a biomedical endpoint.",
    endpoint_fidelity="Requires an auditable commercial or customer endpoint, "
                      "not science.",
    population_fidelity="Scientific participants do not represent customers.",
    timeframe_fidelity="Trust count date and duration not reported.",
    product_transfer="Not applicable scientifically; exact-product customer "
                     "records required.",
    causality_boundary="Scientific causality is inapplicable to a commercial "
                       "trust fact.",
    replication="Scientific replication not applicable; commercial verification "
                "absent.",
    steelman="Strongest legitimate reading: a customer-count statement may well "
             "be accurate and is routinely verifiable from sales and CRM "
             "records. Nothing in the scientific substrate contradicts it.",
    steelman_result="ACCEPTED AS FAR AS IT GOES — the claim is not scientific "
                    "and is not adjudicated adversely here.",
    adversarial="The claim couples a count to a benefit attribution ('trusted "
                "... for better sleep, less inflammation, and restored "
                "balance'), which invites readers to treat popularity as "
                "efficacy evidence. That inferential step is addressed under "
                "S-01, I-01 and W-01, and is not resolved by the count itself.",
    adversarial_result="NOTED AND ROUTED — the popularity-to-efficacy inference "
                       "is adjudicated at the benefit propositions, not here.",
    divergence="NONE MATERIAL.",
    residual_uncertainty="Auditable customer counts, sampling frame, trust "
                         "definition, dates and benefit-specific responses are "
                         "not reported and were never in scope for this "
                         "substrate.",
    rationale="Routed out of biomedical adjudication rather than dropped. The "
              "frozen preparation state NO MATERIAL DIRECT EVIDENCE LOCATED is "
              "explicitly NOT read as UNSUPPORTED here: absent biomedical "
              "literature is not evidence against a customer-count "
              "proposition. The framework's insufficient_input state is used, "
              "which carries a null label and a not_assessed strength ceiling, "
              "so no client statement may assert any evidential conclusion "
              "about it.",
),

dict(
    pid="Q-02",
    proposition="The advertised 40% sale was ending soon.",
    origin="F14",
    ptype="EXPLICIT; COMMERCIAL/URGENCY; PRODUCT-SPECIFIC",
    prep_state="NO MATERIAL DIRECT EVIDENCE LOCATED",
    mechanism_state=None,
    qualifiers=["COMMERCIAL SUBSTANTIATION REQUIRED"],
    routing="OUTSIDE BIOMEDICAL EVIDENCE SCOPE — COMMERCIAL SUBSTANTIATION "
            "REQUIRED. Absence of biomedical literature is NOT evidence against "
            "a pricing or promotion-history proposition.",
    label=None,
    analysis_status="insufficient_input",
    alt_label=None,
    alt_rationale="No frozen biomedical label is assigned; a pricing and "
                  "promotion-history fact is categorically outside the "
                  "claim-forensics taxonomy.",
    confidence=None,
    strength="not_assessed",
    overlay="OUTSIDE BIOMEDICAL EVIDENCE SCOPE — COMMERCIAL SUBSTANTIATION "
            "REQUIRED",
    claim_strength="FACTUAL COMMERCIAL ASSERTION — a discount level plus an "
                   "urgency assertion about its end date.",
    verdict_summary="This is a pricing and promotion-history fact. The frozen "
                    "substrate contains no reference price, no sale start or "
                    "end date and no promotion history, and biomedical evidence "
                    "is categorically inapplicable. The required input class is "
                    "absent, so no biomedical verdict is issued.",
    evidence_tier="not_applicable",
    conclusion_tier="general_public",
    bridge_supported=None,
    items=[
        dict(text="No contemporaneous reference price, sale start or end date, "
                  "or promotion history was reported in the official record.",
             source_reference="Freeze sections 50/51/63", tier="not_applicable",
             role="missing_expected",
             why_it_matters="The evidence class the claim requires is absent "
                            "from the substrate, and the adjudication receives "
                            "this as an explicit gap."),
        dict(text="Commercial claims require customer and promotion records; "
                  "scientific numbers cannot verify them and scientific "
                  "causality is inapplicable to a promotion-history fact.",
             source_reference="Freeze sections 46/58", tier="not_applicable",
             role="weakening",
             why_it_matters="Establishes categorical inapplicability, so "
                            "biomedical silence carries no adverse inference."),
    ],
    supporting=[],
    contra=["No reference price, end date or promotion history reported — an "
            "evidential gap, not counterevidence"],
    missing_comparison_group=False,
    missing_causal_chain=False,
    missing_human_evidence=False,
    sufficiency="unknown",
    sufficiency_rationale="Sufficiency cannot be assessed: the required "
                          "evidence class is commercial and lies outside the "
                          "biomedical substrate entirely.",
    failure_modes=[],
    risk="unknown",
    risk_rationale="Reader-impact risk cannot be characterised without the "
                   "promotion record. Recorded as an explicit insufficient "
                   "state rather than guessed.",
    reader_misunderstanding="That a genuine limited-time discount applies.",
    affected_decision="Timing and urgency of purchase.",
    directness="NOT APPLICABLE — not a biomedical endpoint.",
    endpoint_fidelity="Requires a contemporaneous pricing and promotion "
                      "endpoint, not science.",
    population_fidelity="Population not applicable.",
    timeframe_fidelity="Sale start and end history not reported.",
    product_transfer="Not applicable scientifically; exact promotion records "
                     "required.",
    causality_boundary="Scientific causality is inapplicable to a "
                       "promotion-history fact.",
    replication="Scientific replication not applicable; commercial "
                "verification absent.",
    steelman="Strongest legitimate reading: a time-limited discount is an "
             "ordinary retail practice, verifiable from the advertiser's own "
             "pricing records, and nothing in the scientific substrate "
             "contradicts it.",
    steelman_result="ACCEPTED AS FAR AS IT GOES — the claim is not scientific "
                    "and is not adjudicated adversely here.",
    adversarial="Urgency framing can pressure a purchase decision, but whether "
                "the stated end date was genuine is a pricing-record question "
                "that this substrate cannot address in either direction.",
    adversarial_result="NOT ADJUDICABLE ON THIS SUBSTRATE.",
    divergence="NONE MATERIAL.",
    residual_uncertainty="A contemporaneous reference price, sale start and end "
                         "dates and promotion history are not reported and were "
                         "never in scope for this substrate.",
    rationale="Routed out of biomedical adjudication rather than dropped. The "
              "frozen preparation state is explicitly NOT read as UNSUPPORTED: "
              "the absence of biomedical literature about a discount period is "
              "not evidence about the discount. The framework's "
              "insufficient_input state carries a null label and a "
              "not_assessed strength ceiling.",
),
]

assert len(PROPOSITIONS) == 26, f"expected 26 propositions, got {len(PROPOSITIONS)}"
