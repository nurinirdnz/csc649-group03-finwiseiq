# FinWiseIQ Knowledge Dataset

This folder holds the custom question–answer dataset that FinWiseIQ retrieves from before generating an answer.

## Files

| File                    | What it is                     |
| ----------------------- | ------------------------------ |
| `finwiseiq_dataset.csv` | 50 Q&A pairs (10 per category) |

## Columns

| Column           | Meaning                                                               |
| ---------------- | --------------------------------------------------------------------- |
| `id`             | Category prefix + number, e.g. `KYC-001`                              |
| `category`       | One of the five categories below, spelled exactly the same every time |
| `question`       | The question as a user would ask it                                   |
| `answer`         | A short answer written based on the cited source                      |
| `source`         | Title of the source document                                          |
| `source_section` | Paragraph, section or part used                                       |
| `last_reviewed`  | Date the row was last checked against the source (YYYY-MM-DD)         |

## Categories

| Prefix | Category                                 | Pairs |
| ------ | ---------------------------------------- | ----- |
| IFF    | Islamic Finance Fundamentals             | 10    |
| IFC    | Islamic Financing Contracts              | 10    |
| AML    | AML/CFT                                  | 10    |
| KYC    | KYC/CDD                                  | 10    |
| REG    | Malaysian Financial Regulatory Framework | 10    |

## Where the data came from

Answers are paraphrased summaries of official publications from Bank Negara Malaysia (BNM), the Islamic Financial Services Board (IFSB), the Financial Action Task Force (FATF), the Securities Commission Malaysia, and Malaysian legislation. No text is copied at length. The full list of sources, with links, is in [`docs/source_registry.md`](../docs/source_registry.md).

## Data rules followed

- No personal data (no names of private individuals, IC numbers, phone numbers or account details).
- Every row records its source and section so it can be checked.
- Each row is checked against its source before it is merged, and `last_reviewed` records that date.

## Disclaimer

This dataset is for educational purposes only. It is not legal, financial, regulatory or Shariah advice.
