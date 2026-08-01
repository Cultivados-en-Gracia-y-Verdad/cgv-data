PRAGMA foreign_keys = ON;

CREATE TABLE evidence_classes (
    evidence_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    definition TEXT NOT NULL,
    identity_allowed INTEGER NOT NULL DEFAULT 0,
    required_wording TEXT
);

CREATE TABLE topics (
    topic_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    research_definition TEXT NOT NULL,
    primary_references TEXT,
    boundary_note TEXT,
    status TEXT NOT NULL DEFAULT 'seeded'
);

CREATE TABLE passages (
    passage_id TEXT PRIMARY KEY,
    book TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    verses TEXT NOT NULL,
    reference TEXT NOT NULL UNIQUE,
    scope_purpose TEXT,
    literary_form TEXT,
    speaker_source TEXT,
    recipient_audience TEXT,
    historical_marker TEXT,
    exact_text TEXT,
    translation TEXT,
    observation TEXT,
    review_status TEXT NOT NULL DEFAULT 'seeded',
    notes TEXT
);

CREATE TABLE passage_topics (
    passage_id TEXT NOT NULL,
    topic_id TEXT NOT NULL,
    PRIMARY KEY (passage_id, topic_id),
    FOREIGN KEY (passage_id) REFERENCES passages(passage_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE
);

CREATE TABLE statements (
    statement_id TEXT PRIMARY KEY,
    passage_id TEXT NOT NULL,
    verse_reference TEXT NOT NULL,
    statement_type TEXT NOT NULL,
    subject_text TEXT,
    predicate_text TEXT,
    object_text TEXT,
    exact_wording TEXT,
    translation TEXT,
    certainty TEXT NOT NULL DEFAULT 'explicit',
    review_status TEXT NOT NULL DEFAULT 'seeded',
    FOREIGN KEY (passage_id) REFERENCES passages(passage_id) ON DELETE CASCADE
);

CREATE TABLE connections (
    connection_id TEXT PRIMARY KEY,
    source_reference TEXT NOT NULL,
    target_reference TEXT NOT NULL,
    evidence_code TEXT NOT NULL,
    shared_feature TEXT NOT NULL,
    connection_statement TEXT NOT NULL,
    identity_claim INTEGER NOT NULL DEFAULT 0,
    review_status TEXT NOT NULL DEFAULT 'seeded',
    caution_note TEXT,
    FOREIGN KEY (evidence_code) REFERENCES evidence_classes(evidence_code)
);

CREATE TABLE chronology (
    event_id TEXT PRIMARY KEY,
    reference TEXT NOT NULL,
    event_label TEXT NOT NULL,
    anchor_type TEXT NOT NULL,
    stated_marker TEXT NOT NULL,
    sequence_relation TEXT,
    related_event_id TEXT,
    duration_text TEXT,
    people_places TEXT,
    observation TEXT,
    review_status TEXT NOT NULL DEFAULT 'seeded',
    FOREIGN KEY (related_event_id) REFERENCES chronology(event_id)
);

CREATE TABLE output_plan (
    output_id TEXT PRIMARY KEY,
    output_type TEXT NOT NULL,
    title TEXT NOT NULL,
    section_order INTEGER NOT NULL,
    record_type TEXT NOT NULL,
    record_id TEXT NOT NULL,
    inclusion_note TEXT,
    status TEXT NOT NULL DEFAULT 'planned'
);

CREATE INDEX idx_passages_reference ON passages(reference);
CREATE INDEX idx_statements_passage ON statements(passage_id);
CREATE INDEX idx_connections_source ON connections(source_reference);
CREATE INDEX idx_connections_target ON connections(target_reference);
CREATE INDEX idx_chronology_reference ON chronology(reference);
