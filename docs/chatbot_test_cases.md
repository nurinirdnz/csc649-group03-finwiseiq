# Chatbot Test Cases (Week 9)

**Project:** FinWiseIQ — CSC649 Group 03
**Status:** all test cases run, 28 November 2026. Only the UX ratings (Section 6) are still pending.

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
- **Live run** means the case was typed into the running app with the real OpenAI API, and the reply was captured in a screenshot. Screenshots are in [screenshots/chatbot_test_evidence/](screenshots/chatbot_test_evidence/), named by test ID.
- **Routing check (25 Nov)** means the case was run through `process_question()` with real retrieval, but with OpenAI replaced by a stub. It shows which path the chatbot takes (answer, follow-up, small talk or fallback) and which dataset row is found, **not** the wording of the final answer.
- **Auto test** means an automated test in `tests/`.

**Scores (0–2)** are used for context retention and sentiment handling:

| Score | Meaning |
|---|---|
| 2 | Handled fully as expected |
| 1 | Handled partly: a polite, safe reply, but it misses part of the expected behaviour |
| 0 | Not handled: wrong topic, lost context, or an unsuitable reply |

**Owners (proposed):**

| Test type | Owner |
|---|---|
| Intent recognition | Siti Nasyitah |
| Response relevance | Syafiqah Wahidah |
| Context retention | Nurin Irdina |
| Sentiment handling | Nurisha Adilla |
| Task completion | Syafiqah Wahidah |
| UX peer review | One student from another group plus all four members (collected by Siti Nasyitah) |

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
| I7 | Apa beza murabahah dgn ijarah eh? *(Malay slang and short forms)* | Comparison question → compares the two contracts | Answered in Malay: murabahah is a sale at cost plus profit, ijarah is a lease where the bank keeps ownership; also explained IMBT, with sources | ✅ | Live run: [I7](screenshots/chatbot_test_evidence/I7.png) |

## 2. Response relevance

Is the retrieved information, and the answer built from it, relevant to the question?

| ID | Input | Expected | Actual | Result | Evidence |
|---|---|---|---|---|---|
| R1 | What is customer due diligence? | CDD row at rank 1; answer explains CDD | Rank 1; correct, faithful answer | ✅ | T09, E2E (24 Nov) |
| R2 | Is a court bound by the SAC's ruling? | REG-004; mentions the 2019 Federal Court ruling | Rank 1 (0.888); includes the binding-referral rule and the 2019 ruling | ✅ | T13, E2E (24 Nov) |
| R3 | Wht is murabaha finacing *(typos)* | Still finds the Murabahah financing row | IFC-001 "What is Murabahah financing?" at rank 1 (0.696) | ✅ | Routing check (25 Nov) |
| R4 | Apa itu murabahah? *(Malay)* | Murabahah row at rank 1 | Rank 1 was IFC-010 Mudarabah; Murabahah rows were 2nd and 3rd | ⚠️ | Routing check (25 Nov) |
| R5 | explain kyc & aml requirments for islamic bnk acc *(abbreviations and typos)* | Lists the basic KYC/AML requirements (CDD, identity verification, monitoring) | The intent was understood despite the typos, but the answer only defined e-KYC and said the verified information did not cover the full requirements | ⚠️ | Live run: [R5](screenshots/chatbot_test_evidence/R5.png) |
| R6 | Recommend me the best nasi lemak in Shah Alam. | Out of scope → fallback | Standard out-of-scope fallback | ✅ | Live run: [R6](screenshots/chatbot_test_evidence/R6.png) |
| R7 | What are the main principles of Mudarabah according to BNM policy? | Accurate principles with BNM references | Two parties (rabbul mal and mudarib), agreed profit-sharing ratio, capital provider bears losses unless caused by misconduct or negligence; cites paras 10.1, 16.4, 17.1–17.2 | ✅ | Live run: [R7](screenshots/chatbot_test_evidence/R7.png) |

## 3. Context retention

Does the chatbot keep the topic across a conversation? Each case is a **sequence** of messages.

| ID | Sequence | Expected | Actual | Result | Evidence |
|---|---|---|---|---|---|
| S1 | "What is murabahah?" → "Tell me more" | 2nd reply stays on murabahah and adds detail | Added that the bank buys the asset first, both cost and profit are disclosed, ownership passes to the customer, and how this differs from ijarah | ✅ | Live run: [S1a](screenshots/chatbot_test_evidence/S1a.png), [S1b](screenshots/chatbot_test_evidence/S1b.png); C8 |
| S2 | "What is murabahah?" → "oh ok" → "tell me more" | "oh ok" gets a friendly reply; "tell me more" still about murabahah | "oh ok" → "Glad that helps! 😊 Is there anything else I can help you with? Or say "tell me more"…"; "tell me more" → "Murabahah is a sale, not a lease…". **Before the fix (KAN-47, PR #28)** "oh ok" replaced the topic | ✅ (was ❌) | Live run: [S2a](screenshots/chatbot_test_evidence/S2a.png), [S2b](screenshots/chatbot_test_evidence/S2b.png), [S2c](screenshots/chatbot_test_evidence/S2c.png); C9; auto test `test_chit_chat_does_not_replace_the_topic` |
| S3 | "Apa itu ijarah?" → "hmm" → "terangkan lagi" | "hmm" gets a Malay reply; "terangkan lagi" continues ijarah | Ijarah explained in Malay; "hmm" → "Tak apa, ambil masa anda! 😊 …"; "terangkan lagi" gave more on ijarah in Malay, the difference from murabahah and IMBT | ✅ | Live run: [S3a](screenshots/chatbot_test_evidence/S3a.png), [S3b](screenshots/chatbot_test_evidence/S3b.png), [S3c](screenshots/chatbot_test_evidence/S3c.png); C4, C10 |
| S4 | "What is murabahah?" → "How is it different from ijarah?" | Comparison uses the earlier topic | Compared murabahah (a sale, ownership passes to the customer) with ijarah (a lease, the bank keeps ownership and its risks) | ✅ | Live run: [S4a](screenshots/chatbot_test_evidence/S4a.png), [S4b](screenshots/chatbot_test_evidence/S4b.png); C11 |
| S5 | Any question → **Clear** → "Tell me more" | No memory after Clear | No earlier history reaches the backend after Clear | ✅ | Auto test `test_welcome_and_clear_leave_no_backend_history` |
| S6 | "What is Ijarah?" → "How does it differ from Murabahah?" | Comparison uses the earlier ijarah topic | Compared both contracts correctly and mentioned IMBT | ✅ | Live run: [S6a](screenshots/chatbot_test_evidence/S6a.png), [S6b](screenshots/chatbot_test_evidence/S6b.png) |

## 4. Sentiment handling

FinWiseIQ has **no sentiment detection**. These cases check how it copes when users show emotion: frustrated or confused messages should still get a helpful answer, and positive or hesitant messages should get a friendly reply.

| ID | Input | Expected | Actual | Result | Evidence |
|---|---|---|---|---|---|
| SE1 | I'm so confused, what even is murabahah?? | Calm, simple answer about murabahah | Calm 3-sentence answer: a sale, not a lease, at cost plus an agreed profit, usually paid in instalments, with BNM sources | ✅ | Live run: [SE1](screenshots/chatbot_test_evidence/SE1.png) |
| SE2 | Ugh, I still don't get customer due diligence. Explain it simply please | Simple CDD explanation | Simple explanation: identify and verify the customer, check who acts for them and who owns them, and understand the purpose; ended with a one-line plain summary. Same result in a second run | ✅ | Live run, twice: [SE2a](screenshots/chatbot_test_evidence/SE2a.png), [SE2b](screenshots/chatbot_test_evidence/SE2b.png) |
| SE3 | This bot is useless | Acknowledge the frustration and offer help | Standard out-of-scope fallback ("Sorry, I can only answer questions about…"); the frustration is not acknowledged | ❌ | Routing check (25 Nov) |
| SE4 | thanks | Warm reply | "You're welcome! 😊 …" | ✅ | Routing check (25 Nov) |
| SE5 | hmm *(after a question)* | Reassuring reply that keeps the topic | "No worries, take your time! 😊 If something wasn't clear, say "tell me more"…" | ✅ | C3; auto tests |
| SE6 | Wow this is really helpful!! *(happy / excited user)* | Warm, positive reply; offers further help | Standard out-of-scope fallback ("Sorry, I can only answer questions about…"); the praise is not acknowledged. Same result in a second run | ❌ | Live run, twice: [SE6a](screenshots/chatbot_test_evidence/SE6a.png), [SE6b](screenshots/chatbot_test_evidence/SE6b.png) |

## 5. Task completion

Can a user complete a realistic goal with the chatbot?

| ID | User goal | Input | Expected | Actual | Result | Evidence |
|---|---|---|---|---|---|---|
| TC1 | Find out whether a cash deposit is reported | If I deposit RM30,000 cash, is it reported? | Applies the RM25,000 cash-threshold rule to RM30,000 | Applied the threshold to the user's amount, with sources | ✅ | T08, E2E (24 Nov) |
| TC2 | Learn how long KYC records are kept | How long do banks keep KYC records? | Correct retention period with source | Correct answer, rank 1 | ✅ | T11, E2E (24 Nov) |
| TC3 | Learn how to save money in a Shariah-compliant way, asking in Malay | mcm mana nak simpan duit dlm shariah-compliant way? | Relevant answer, or a clear next step | Nothing passed the threshold, so the Malay fallback appeared. It suggests asking in English. The English question "How to save money in a Shariah-compliant way?" finds IFF-001 (0.649) | ❌ | Routing check (25 Nov) |
| TC4 | Start a new conversation | Several messages → **Clear** | Chat cleared, welcome shown, no crash | Chat reset to the welcome message | ✅ | U09 (24 Nov) |
| TC5 | Get a structured list | List 3 key Shariah requirements for a valid Murabahah contract according to BNM. | Three requirements with sources | Gave only one point (how the price is set) and said it could not reliably list three; did not invent the rest | ❌ | Live run: [TC5](screenshots/chatbot_test_evidence/TC5.png) |

## 6. User experience

### UX scenario

| ID | Input | Expected | Actual | Result | Evidence |
|---|---|---|---|---|---|
| UX1 | I am new to Islamic banking. Explain Murabahah in simple words without heavy jargon. | Beginner-friendly answer without jargon | Plain 3-sentence explanation: the bank buys the item, sells it to you at cost plus an agreed profit, tells you both amounts, and you pay in instalments | ✅ | Live run: [UX1](screenshots/chatbot_test_evidence/UX1.png) |

### UX peer review

Each reviewer uses the running app for about 5 minutes, asking their own questions (including a follow-up and an off-topic question), then **rates it 1–5** (1 = very poor, 5 = excellent). Rate honestly and add a short comment for any score of 3 or below.

The **outside tester** is a student from another CSC649 group, so at least one rating comes from someone who did not build the chatbot.

| Criterion | Outside tester | Nurin | Wahidah | Nasyitah | Nurisha | Average |
|---|---|---|---|---|---|---|
| Ease of use | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | |
| Clarity of answers | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | |
| Tone and friendliness | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | |
| Empathy (feels understood and supported) | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | |
| Engagement | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | |
| Flow smoothness (natural conversation, follow-ups) | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | |
| User comfort | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | |
| Response speed | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | |
| Trust (sources shown, honest refusals) | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | |
| **Overall satisfaction** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | |
| **Reviewer average** | | | | | | **UX average: ⏳** |

**How to calculate:** *Average* (last column) is the mean of each row. *Reviewer average* is the mean of each column. The **UX average** is the mean of all filled-in scores, out of 5.

**Comments:**

- Outside tester (name and group): ⏳
- Nurin: ⏳
- Wahidah: ⏳
- Nasyitah: ⏳
- Nurisha: ⏳

**Limitation:** four of the five reviewers are the developers, so their scores may be biased. The outside tester's scores are reported separately in the table so they can be compared.

---

## Summary

| Test type | Minimum required | Cases | ✅ Pass | ⚠️ Partial | ❌ Fail | ⏳ Pending |
|---|---|---|---|---|---|---|
| Intent recognition | 2 | 7 | 6 | 0 | 1 | 0 |
| Response relevance | 2 | 7 | 5 | 2 | 0 | 0 |
| Context retention | 2 sequences | 6 sequences | 6 | 0 | 0 | 0 |
| Sentiment handling | 2 | 6 | 4 | 0 | 2 | 0 |
| Task completion | 2 | 5 | 3 | 0 | 2 | 0 |
| User experience | 1 | 1 scenario + rating review | 1 | 0 | 0 | rating review |
| **Total** | | **32 cases + 1 rating review** | **25** | **2** | **5** | **rating review** |

### Metrics

| Metric | Formula | Result |
|---|---|---|
| Intent accuracy | Correct intents ÷ intent cases × 100 | 6 / 7 = **85.7%** (I6 failed) |
| Response relevance | Fully relevant ÷ relevance cases × 100 | 5 / 7 = **71.4%** fully relevant. R4 and R5 are partial: R4 found the right rows at ranks 2 and 3; R5 understood the question but the answer was incomplete. No answer was off-topic |
| Context retention score | Sum of 0–2 scores ÷ (2 × flows) | S1 2, S2 2, S3 2, S4 2, S5 2, S6 2 → **12 / 12** |
| Sentiment handling score | Sum of 0–2 scores ÷ (2 × cases) | SE1 2, SE2 2, SE3 1, SE4 2, SE5 2, SE6 1 → **10 / 12**. SE3 and SE6 score 1 because the fallback is polite but ignores the user's emotion |
| Task completion rate | Tasks completed ÷ tasks attempted × 100 | 3 / 5 = **60.0%** (TC3 and TC5 failed) |
| UX average (1–5) | Mean of all UX scores | **⏳** pending |
| Overall pass rate | Passed ÷ cases × 100 | 25 / 32 = **78.1%** (partial counted as not passed) |

### Overall chatbot score summary

| Area | Score | Comment |
|---|---|---|
| Intent accuracy | 85.7% | English, typos, slang and Malay with shared terms routed correctly; Malay-only wording can match the wrong row |
| Response relevance | 71.4% fully relevant | No off-topic answers; two answers were incomplete or ranked lower |
| Context retention | 12 / 12 | Topic kept across follow-ups, small talk and Malay after the KAN-47 fix |
| Sentiment handling | 10 / 12 | Confused and frustrated *questions* get calm, simple answers; emotional messages with no question get the fallback |
| Task completion | 60.0% | Single-fact tasks completed; a Malay task and a structured-list task did not |
| UX | Scenario passed; rating ⏳ | Beginner-friendly answer without jargon |
| **Overall** | **25 / 32 = 78.1%** | Failures fall into three patterns: Malay-only wording (F2), emotional messages with no question (F3) and gaps in the knowledge base (F4) |

Off-topic messages (I2, I5, R6) were refused without calling OpenAI. When information was missing (R5, TC5), the chatbot said so instead of inventing an answer.

These figures cover only the 32 cases in this document. Answer accuracy across the full test set is in [end_to_end_evaluation.md](end_to_end_evaluation.md): correctness 13 / 15, faithfulness 17 / 17, refusal 5 / 5, usefulness 20 / 20.

**Update when the UX ratings are in:** fill in the UX average in both tables above.

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

### F3. Emotional messages with no question get the fallback (SE3, SE6): open

- **What happened:**
  - "This bot is useless" got the standard out-of-scope fallback, which reads as cold to an annoyed user.
  - "Wow this is really helpful!!" got the same fallback, telling a happy user to rephrase.
- **Cause:** the chatbot has no sentiment detection. Small talk is matched against a fixed list of short phrases: "thanks" is on the list (SE4 passed), but longer praise or complaints are not. These messages have no finance content, so nothing passes the threshold.
- **Possible fix:** add common praise and frustration phrases (for example "helpful", "great", "useless") to the small-talk handling, with replies such as "Glad it helped! 😊 Anything else you'd like to know?" and "Sorry this hasn't been helpful. Could you tell me which Islamic finance or compliance topic you're looking for?"
- **Status:** open; not planned before submission.

### F4. Gaps in the knowledge base give incomplete answers (TC5, R5): open

- **What happened:**
  - "List 3 key Shariah requirements for a valid Murabahah contract according to BNM." got only one point (how the price is set).
  - "explain kyc & aml requirments for islamic bnk acc" got only the definition of e-KYC.
- **Cause:** the 55-row dataset holds short Q&A pairs, not the full policy documents. There is no row listing the Murabahah contract requirements or the full KYC/AML requirements, so retrieval returns the closest rows and the model correctly refuses to fill the gap.
- **Good behaviour:** in both cases the chatbot said the information was not available instead of inventing it, as the system prompt requires.
- **Possible fix:** add Q&A rows for common "list the requirements" questions (Murabahah contract requirements, KYC/CDD steps), with sources from the BNM policy documents.
- **Status:** open; not planned before submission.
