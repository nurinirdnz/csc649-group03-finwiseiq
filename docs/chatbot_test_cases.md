# Chatbot Test Cases (Week 9)

**Project:** FinWiseIQ — CSC649 Group 03
**Status:** DRAFT, 25 November 2026. Cases marked ⏳ still need to be run by their owner.

This document tests FinWiseIQ as a chatbot, using the six test types from the Week 9 brief: intent recognition, response relevance, context retention, sentiment handling, task completion and user-experience (UX) peer review. It builds on the earlier evaluations instead of repeating them:

- [retrieval_evaluation.md](retrieval_evaluation.md) and [end_to_end_evaluation.md](end_to_end_evaluation.md): the 20 test questions T01–T20
- [KAN-39_Gradio_Usability_Test_Report.md](KAN-39_Gradio_Usability_Test_Report.md): usability scenarios U01–U12
- [pipeline_test_results.md](pipeline_test_results.md): KAN-47 conversation-memory cases C1–C15

## How to read the results

| Mark | Meaning |
|---|---|
| ✅ Pass | Behaved as expected |
| ⚠️ Partial | Partly correct (for example, the right row was found but not at rank 1) |
| ❌ Fail | Did not behave as expected |
| ⏳ Pending | Not run yet; the owner runs it in the app and fills in *Actual* and *Result* |

**Evidence** says where each result comes from:

- **E2E / U / C** refer to earlier documented runs (with the real OpenAI API for E2E and U).
- **Routing check (25 Nov)** means the case was run through `process_question()` with real retrieval, but with OpenAI replaced by a stub. It shows which path the chatbot takes (answer, follow-up, small talk or fallback) and which dataset row is found, **not** the wording of the final answer.
- **Auto test** means an automated test in `tests/`.

**Owners (proposed):**

| Test type | Owner |
|---|---|
| Intent recognition | Siti Nasyitah |
| Response relevance | Syafiqah Wahidah |
| Context retention | Nurin Irdina |
| Sentiment handling | Nurisha Adilla |
| Task completion | Syafiqah Wahidah |
| UX peer review | All four members (collected by Siti Nasyitah) |

---

## 1. Intent recognition

Does the chatbot recognise what kind of message it received (finance question, greeting, small talk, out-of-scope request) and route it correctly?

| ID | Input | Expected intent → behaviour | Actual | Result | Evidence |
|---|---|---|---|---|---|
| I1 | What is Murabahah financing? | Finance question → answer with sources | Answer about Murabahah with BNM sources | ✅ | U02 (24 Nov) |
| I2 | What's the weather today? | Out of scope → fallback, OpenAI not called | Fallback message; nothing passed the 0.45 threshold | ✅ | T16, U07; routing check (25 Nov) |
| I3 | hi | Greeting → friendly local reply | "Hello! How can I help you with Islamic finance or Malaysian financial compliance?" | ✅ | Auto test `test_standalone_greetings_reply_locally` |
| I4 | thanks | Small talk → friendly reply, no search | "You're welcome! 😊 Feel free to ask if you have any other questions." | ✅ | Routing check (25 Nov) |
| I5 | Which stock should I buy today? | Personal investment advice → refuse | Polite refusal explaining the chatbot's scope | ✅ | U06 (24 Nov) |
| I6 | Apa itu usaha wajar pelanggan? *(Malay: "What is customer due diligence?")* | Finance question (CDD) → CDD answer | Retrieved IFC-007 "What is Ijarah?" (0.472), the wrong topic | ❌ | Routing check (25 Nov) |

## 2. Response relevance

Is the retrieved information, and the answer built from it, relevant to the question?

| ID | Input | Expected | Actual | Result | Evidence |
|---|---|---|---|---|---|
| R1 | What is customer due diligence? | CDD row at rank 1; answer explains CDD | Rank 1; correct, faithful answer | ✅ | T09, E2E (24 Nov) |
| R2 | Is a court bound by the SAC's ruling? | REG-004; mentions the 2019 Federal Court ruling | Rank 1 (0.888); includes the binding-referral rule and the 2019 ruling | ✅ | T13, E2E (24 Nov) |
| R3 | Wht is murabaha finacing *(typos)* | Still finds the Murabahah financing row | IFC-001 "What is Murabahah financing?" at rank 1 (0.696) | ✅ | Routing check (25 Nov) |
| R4 | Apa itu murabahah? *(Malay)* | Murabahah row at rank 1 | Rank 1 was IFC-010 Mudarabah; Murabahah rows were 2nd and 3rd | ⚠️ | Routing check (25 Nov) |

## 3. Context retention

Does the chatbot keep the topic across a conversation? Each case is a **sequence** of messages.

| ID | Sequence | Expected | Actual | Result | Evidence |
|---|---|---|---|---|---|
| S1 | "What is murabahah?" → "Tell me more" | 2nd message searched together with the murabahah topic; history sent | Searched "What is murabahah? Tell me more"; history sent | ✅* | C8, routing check (25 Nov) |
| S2 | "What is murabahah?" → "oh ok" → "tell me more" | "oh ok" gets a friendly reply; "tell me more" still about murabahah | **Before the fix:** "oh ok" became the topic and "tell me more" lost murabahah. **After the fix (KAN-47, PR #28):** topic kept | ✅* (was ❌) | C9; auto test `test_chit_chat_does_not_replace_the_topic` |
| S3 | "Apa itu ijarah?" → "hmm" → "terangkan lagi" | "hmm" gets a Malay reply; "terangkan lagi" continues ijarah | Malay reply "Tak apa, ambil masa anda! 😊 …"; follow-up used the ijarah topic | ✅* | C4, C10 |
| S4 | "What is murabahah?" → "How is it different from ijarah?" | Comparison uses the earlier topic | Searched with both; history sent | ✅* | C11 |
| S5 | Any question → **Clear** → "Tell me more" | No memory after Clear | No earlier history reaches the backend after Clear | ✅ | Auto test `test_welcome_and_clear_leave_no_backend_history` |

\* Checked with OpenAI stubbed: the topic and history handling are verified, but the final answer text was not recorded. **To do (Nurin):** run S1–S4 in the app and paste a one-line summary of each live answer into *Actual*.

## 4. Sentiment handling

FinWiseIQ has **no sentiment detection**. These cases check how it copes when users show emotion: frustrated or confused messages should still get a helpful answer, and positive or hesitant messages should get a friendly reply.

| ID | Input | Expected | Actual | Result | Evidence |
|---|---|---|---|---|---|
| SE1 | I'm so confused, what even is murabahah?? | Calm, simple answer about murabahah | Retrieval found the murabahah rows (0.751), so OpenAI is called. Live answer tone: **⏳** | ⏳ | Routing check (25 Nov) |
| SE2 | Ugh, I still don't get customer due diligence. Explain it simply please | Simple CDD explanation | Retrieval found KYC-001 "What is CDD?" (0.687). Live answer: **⏳** | ⏳ | Routing check (25 Nov) |
| SE3 | This bot is useless | Acknowledge the frustration and offer help | Standard out-of-scope fallback ("Sorry, I can only answer questions about…"); the frustration is not acknowledged | ❌ | Routing check (25 Nov) |
| SE4 | thanks | Warm reply | "You're welcome! 😊 …" | ✅ | Routing check (25 Nov) |
| SE5 | hmm *(after a question)* | Reassuring reply that keeps the topic | "No worries, take your time! 😊 If something wasn't clear, say "tell me more"…" | ✅ | C3; auto tests |

**To do (Nurisha):** run SE1 and SE2 in the app and record whether the answer stays calm, simple and correct.

## 5. Task completion

Can a user complete a realistic goal with the chatbot?

| ID | User goal | Input | Expected | Actual | Result | Evidence |
|---|---|---|---|---|---|---|
| TC1 | Find out whether a cash deposit is reported | If I deposit RM30,000 cash, is it reported? | Applies the RM25,000 cash-threshold rule to RM30,000 | Applied the threshold to the user's amount, with sources | ✅ | T08, E2E (24 Nov) |
| TC2 | Learn how long KYC records are kept | How long do banks keep KYC records? | Correct retention period with source | Correct answer, rank 1 | ✅ | T11, E2E (24 Nov) |
| TC3 | Learn how to save money in a Shariah-compliant way, asking in Malay | mcm mana nak simpan duit dlm shariah-compliant way? | Relevant answer, or a clear next step | Nothing passed the threshold, so the Malay fallback appeared. It suggests asking in English. The English question "How to save money in a Shariah-compliant way?" finds IFF-001 (0.649) | ❌ | Routing check (25 Nov) |
| TC4 | Start a new conversation | Several messages → **Clear** | Chat cleared, welcome shown, no crash | Chat reset to the welcome message | ✅ | U09 (24 Nov) |

## 6. UX peer review

Each member uses the running app for about 5 minutes and **rates it 1–5** (1 = very poor, 5 = excellent). Rate honestly and add a short comment for any score of 3 or below.

| Criterion | Nurin | Wahidah | Nasyitah | Nurisha | Average |
|---|---|---|---|---|---|
| Ease of use | ⏳ | ⏳ | ⏳ | ⏳ | |
| Clarity of answers | ⏳ | ⏳ | ⏳ | ⏳ | |
| Response speed | ⏳ | ⏳ | ⏳ | ⏳ | |
| Visual design | ⏳ | ⏳ | ⏳ | ⏳ | |
| Trust (sources shown, honest refusals) | ⏳ | ⏳ | ⏳ | ⏳ | |
| **Overall** | ⏳ | ⏳ | ⏳ | ⏳ | |

**Comments:**

- Nurin: ⏳
- Wahidah: ⏳
- Nasyitah: ⏳
- Nurisha: ⏳

**Limitation:** the reviewers are the developers, so the scores may be biased. A review by students outside the team would be stronger.

---

## Summary

| Test type | Minimum required | Cases | ✅ Pass | ⚠️ Partial | ❌ Fail | ⏳ Pending |
|---|---|---|---|---|---|---|
| Intent recognition | 2 | 6 | 5 | 0 | 1 | 0 |
| Response relevance | 2 | 4 | 3 | 1 | 0 | 0 |
| Context retention | 2 sequences | 5 sequences | 5 | 0 | 0 | 0 |
| Sentiment handling | 2 | 5 | 2 | 0 | 1 | 2 |
| Task completion | 2 | 4 | 3 | 0 | 1 | 0 |
| UX peer review | 1 | 1 review (4 raters) | – | – | – | 1 |
| **Total** | | **24 cases + 1 review** | **18** | **1** | **3** | **2 + review** |

**Metrics (from the 22 completed cases):**

- **Pass rate:** 18 / 22 = **81.8%** (partial counted as not passed)
- **Context retention:** 5 / 5 sequences keep the topic (4 of them checked with OpenAI stubbed; live answers still to be recorded)
- **Out-of-scope handling:** off-topic messages (I2, I5) were refused without calling OpenAI
- **Language:** every failure (I6, TC3) and the partial (R4) involve Malay-only wording

These figures cover only the 24 cases in this document. Answer accuracy across the full test set is in [end_to_end_evaluation.md](end_to_end_evaluation.md): correctness 13 / 15, faithfulness 17 / 17, refusal 5 / 5, usefulness 20 / 20.

**Update when the pending cases are done:** recount the table and the pass rate.

---

## Failed cases

### F1. Small talk replaced the conversation topic (S2): fixed

- **What happened:** in live testing on 25 Nov, the user asked "What is murabahah?", then typed "oh ok", then "tell me more". "oh ok" got the fallback and was treated as the new topic, so "tell me more" lost the murabahah context.
- **Cause:** `last_topic_question()` took the last user message that was not a follow-up, even if it never got a real answer.
- **Fix (KAN-47, PR #28):**
  - Only a message whose reply contained sources counts as the topic.
  - Small talk such as "oh ok", "hmm" or "thanks" now gets a friendly reply instead of the fallback.
- **Status:** ✅ fixed and covered by automated tests.

### F2. Malay questions in Malay wording fail retrieval (I6, TC3, partly R4): open

- **What happened:**
  - "Apa itu usaha wajar pelanggan?" (customer due diligence) matched the Ijarah row.
  - "mcm mana nak simpan duit dlm shariah-compliant way?" found nothing.
  - "Apa itu murabahah?" ranked Mudarabah first.
- **Cause:** the dataset is in English and `all-MiniLM-L6-v2` is an English model. Malay questions only match when the key term is the same in both languages ("Apa itu takaful?").
- **Mitigation so far:** when a Malay question finds nothing, the chatbot shows the out-of-scope message in Malay and suggests asking in English.
- **Not fixed:** a Malay question that matches the *wrong* row (I6) still reaches OpenAI with the wrong context.
- **Possible fix (future work):** a multilingual embedding model, or Malay versions of the dataset questions, followed by re-calibrating the threshold.

### F3. Frustration is not acknowledged (SE3): open

- **What happened:** "This bot is useless" got the standard out-of-scope fallback, which reads as cold to an annoyed user.
- **Cause:** the chatbot has no sentiment detection. The message has no finance content, so nothing passes the threshold.
- **Possible fix:** add common frustration phrases to the small-talk lists with an empathetic reply. For example: "Sorry this hasn't been helpful. Could you tell me which Islamic finance or compliance topic you're looking for?"
- **Status:** open; not planned before submission.
