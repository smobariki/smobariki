def should_process_accession(accession: str, known_accessions: set[str]) -> bool:
    return accession not in known_accessions
