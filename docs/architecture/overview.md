# Architecture Overview

## 1. Candidate pipeline

Resume -> text extraction -> section detection -> skill/entity extraction -> normalized candidate profile.

The extracted profile is editable by the user before recommendations are generated.

## 2. Job pipeline

Source adapter -> raw job -> normalization -> skill extraction -> deduplication -> persistence -> embedding.

Each adapter has one responsibility: turn an external source into the internal job schema.

## 3. Recommendation pipeline

Candidate profile + job -> feature extraction -> baseline lexical score -> semantic score -> weighted hybrid score -> explanation.

The system should retain score components so users can understand recommendations.

## 4. Skill-gap pipeline

Required skills - candidate skills -> normalized missing skills -> priority calculation -> learning resources.

## 5. Alert pipeline

New/updated job -> candidate eligibility -> recommendation score -> threshold -> notification.

## Non-functional requirements

- deterministic normalization where possible
- graceful failure for individual job sources
- idempotent ingestion
- observable background jobs
- secure secret handling
- testable ML components
