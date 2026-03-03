from typing import Dict, Any
import gzip
import os

def summarize_vcf(vcf_path: str, max_records: int = 20000) -> Dict[str, Any]:
    """
    Summarize VCF quickly without heavy computation.
    - counts samples from header
    - estimates variant count by scanning up to max_records
    """
    facts: Dict[str, Any] = {"vcf_path": vcf_path, "vcf_basename": os.path.basename(vcf_path)}
    opener = gzip.open if vcf_path.endswith(".gz") else open

    sample_count = None
    variant_count = 0
    chroms = set()

    with opener(vcf_path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("##"):
                continue
            if line.startswith("#CHROM"):
                parts = line.strip().split("\t")
                # VCF columns: CHROM POS ID REF ALT QUAL FILTER INFO FORMAT samples...
                if len(parts) > 9:
                    sample_count = len(parts) - 9
                    facts["samples_preview"] = parts[9: min(9+10, len(parts))]
                else:
                    sample_count = 0
                continue
            if line.startswith("#"):
                continue
            # data line
            variant_count += 1
            parts = line.split("\t")
            if parts:
                chroms.add(parts[0])
            if variant_count >= max_records:
                break

    facts["sample_count"] = sample_count
    facts["variant_count_scanned"] = variant_count
    facts["chroms_scanned"] = sorted(list(chroms))[:20]
    facts["note"] = "Variant count is a scan-based estimate; full count may be larger."
    return facts
