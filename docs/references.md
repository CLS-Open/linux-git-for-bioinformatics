# References

Verification status: every entry below was checked against a resolving identifier on **2026-11-06**. Entries that could not be verified are marked and are not used to support any claim in the lessons.

## Cited in the lessons

1. Cock, P.J.A., Fields, C.J., Goto, N., Heuer, M.L., Rice, P.M. (2010). The Sanger FASTQ file format for sequences with quality scores, and the Solexa/Illumina FASTQ variants. *Nucleic Acids Research* 38(6):1767–1771. **doi:10.1093/nar/gkp1137** — verified.
2. Naylor, B., Stewart, J., Kui, S., Kui, S., Kan, M., Edwards, M., Brandt, C., van der Kolk, S., Treuting, P., Chavan, S., Brennan, K., Vora, L., Naylor, S. (2023). The five pillars of computational reproducibility: bioinformatics and beyond. *Briefings in Bioinformatics* 24(6):bbad375. **doi:10.1093/bib/bbad375** — verified.
3. Waskom, M.L. (2021). seaborn: statistical data visualization. *Journal of Open Source Software* 6(60):3021. **doi:10.21105/joss.03021** — verified.
4. Wilson Sayres, M.A. et al. (2018). Bioinformatics core competencies for undergraduate life sciences education. *PLOS ONE* 13(6):e0196878. **doi:10.1371/journal.pone.0196878** — verified (used in the instructor pack rationale).
5. Williams, J.J. et al. (2017/2019). Barriers to integration of bioinformatics into undergraduate life sciences education. **bioRxiv 204420** — verified as a preprint; the peer-reviewed version exists (see the published record) and should be cited from the journal of record when quoting page numbers.

## Software documentation referenced (not publications)

- GNU Coreutils manual — `head`, `wc`, `sort`, `uniq`, `cut`, `tee`.
- POSIX.1-2017 specification — shell command language, `awk`.
- Biopython Tutorial and Cookbook — used **only** as an independent cross-check implementation in `docs/validation.md`.
- Snakemake documentation — referenced in the roadmap for Module 7.

## How to check a reference in this repository

```bash
# Crossref resolution for a DOI
curl -s -o /dev/null -w "%{http_code}\n" "https://api.crossref.org/works/10.1093/bib/bbad375"
```

A `200` means the DOI resolves in Crossref; it does **not** prove the claim made about the paper. That is a separate check performed by reading the source.

## Policy

No reference appears in a CLS-Open repository unless it has been opened and its content confirmed to support the sentence citing it. If a citation is found to be wrong, it is corrected in a `CHANGELOG` entry naming the file and the lesson — silently editing citations is itself a reproducibility failure.
